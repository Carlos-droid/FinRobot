import json
import time
from dataclasses import dataclass
from typing import Optional, List, Dict
import redis.asyncio as aioredis

DLQ_KEY    = 'finrobot:dlq'
DLQ_INDEX  = 'finrobot:dlq:index'
DLQ_TTL    = 86400   # 24 hours
MAX_RETRY  = 3

@dataclass
class DLQEntry:
    task_id:     str
    payload:     dict
    error_msg:   str
    retry_count: int
    failed_at:   float

class DeadLetterQueue:
    def __init__(self, redis_url: str = 'redis://localhost:6379'):
        self._redis = aioredis.from_url(redis_url)

    async def push(self, task_id: str, payload: dict, error_msg: str, 
                   retry_count: int = 0) -> None:
        """Pushes a failed task to the DLQ index and stores its payload."""
        entry = DLQEntry(task_id, payload, error_msg, retry_count, time.time())
        key = f'{DLQ_KEY}:{task_id}'
        # Store entry as JSON with TTL
        await self._redis.setex(key, DLQ_TTL, json.dumps(entry.__dict__))
        # Add task_id to sorted set index by failure time for easy retrieval of oldest first
        await self._redis.zadd(DLQ_INDEX, {task_id: entry.failed_at})

    async def pop_next_retry(self) -> Optional[DLQEntry]:
        """Retrieves the oldest task in the DLQ that hasn't exceeded MAX_RETRY."""
        # Get oldest task_ids from index
        task_ids = await self._redis.zrange(DLQ_INDEX, 0, 19)
        for tid_bytes in task_ids:
            tid = tid_bytes.decode()
            raw = await self._redis.get(f'{DLQ_KEY}:{tid}')
            if not raw:
                # Clean up stale index if data is gone
                await self._redis.zrem(DLQ_INDEX, tid)
                continue
            
            entry_dict = json.loads(raw)
            entry = DLQEntry(**entry_dict)
            if entry.retry_count < MAX_RETRY:
                # To avoid multiple workers picking same task, we could use a lock or a transfer list
                # For simplicity here, we increment retry_count and save
                entry.retry_count += 1
                await self._redis.setex(f'{DLQ_KEY}:{tid}', DLQ_TTL, json.dumps(entry.__dict__))
                return entry
            else:
                # Task exceeded retries, it stays in DLQ for manual inspection but not for auto-retry
                pass
        return None

    async def remove(self, task_id: str) -> None:
        """Removes a task from DLQ once it is successfully re-processed or abandoned."""
        await self._redis.delete(f'{DLQ_KEY}:{task_id}')
        await self._redis.zrem(DLQ_INDEX, task_id)

    async def get_stats(self) -> dict:
        """Returns statistics for the DLQ."""
        count = await self._redis.zcard(DLQ_INDEX)
        return {
            'pending_count': count,
            'max_retry': MAX_RETRY,
            'ttl_hours': DLQ_TTL // 3600
        }

    async def list_all(self, limit: int = 100) -> List[DLQEntry]:
        """Lists latest items in the DLQ."""
        task_ids = await self._redis.zrange(DLQ_INDEX, 0, limit - 1)
        entries = []
        for tid_bytes in task_ids:
            raw = await self._redis.get(f'{DLQ_KEY}:{tid_bytes.decode()}')
            if raw:
                entries.append(DLQEntry(**json.loads(raw)))
        return entries
