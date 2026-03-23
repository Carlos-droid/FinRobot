import time
import asyncio
import functools
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any, Dict, Optional
import redis.asyncio as aioredis
from .exceptions import CircuitOpenError

log = logging.getLogger(__name__)

class BreakerState(str, Enum):
    CLOSED    = 'closed'
    OPEN      = 'open'
    HALF_OPEN = 'half_open'

@dataclass
class CircuitBreaker:
    name:             str
    threshold:        int   = 5
    recovery_timeout: int   = 60   # seconds
    _failure_count:   int   = field(default=0, init=False)
    _state:           BreakerState = field(default=BreakerState.CLOSED, init=False)
    _opened_at:       Optional[float] = field(default=None, init=False)
    _redis:          Optional[aioredis.Redis] = field(default=None, init=False)

    def set_redis(self, redis: aioredis.Redis):
        self._redis = redis

    @property
    def state(self) -> BreakerState:
        if self._state == BreakerState.OPEN:
            if self._opened_at and time.time() - self._opened_at >= self.recovery_timeout:
                self._state = BreakerState.HALF_OPEN
        return self._state

    async def _sync_from_redis(self):
        if not self._redis: return
        try:
            val = await self._redis.get(f"breaker:{self.name}:state")
            if val:
                self._state = BreakerState(val.decode())
            val = await self._redis.get(f"breaker:{self.name}:failures")
            if val:
                self._failure_count = int(val.decode())
            val = await self._redis.get(f"breaker:{self.name}:opened_at")
            if val:
                self._opened_at = float(val.decode())
        except Exception as e:
            log.warning(f"Failed to sync breaker {self.name} from Redis: {e}")

    async def _sync_to_redis(self):
        if not self._redis: return
        try:
            await self._redis.set(f"breaker:{self.name}:state", self._state.value)
            await self._redis.set(f"breaker:{self.name}:failures", self._failure_count)
            if self._opened_at:
                await self._redis.set(f"breaker:{self.name}:opened_at", self._opened_at)
        except Exception as e:
            log.warning(f"Failed to sync breaker {self.name} to Redis: {e}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        await self._sync_from_redis()
        
        if self.state == BreakerState.OPEN:
            raise CircuitOpenError(f'Circuit {self.name} is OPEN')
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e

    async def _on_success(self):
        self._failure_count = 0
        self._state = BreakerState.CLOSED
        await self._sync_to_redis()

    async def _on_failure(self):
        self._failure_count += 1
        if self._failure_count >= self.threshold or self._state == BreakerState.HALF_OPEN:
            self._state = BreakerState.OPEN
            self._opened_at = time.time()
        await self._sync_to_redis()

class BreakerRegistry:
    _breakers: Dict[str, CircuitBreaker] = {}
    _redis: Optional[aioredis.Redis] = None

    @classmethod
    def set_redis(cls, redis_url: str = 'redis://localhost:6379'):
        cls._redis = aioredis.from_url(redis_url)
        for breaker in cls._breakers.values():
            breaker.set_redis(cls._redis)

    @classmethod
    def get_or_create(cls, name: str, threshold: int = 5, recovery_timeout: int = 60) -> CircuitBreaker:
        if name not in cls._breakers:
            breaker = CircuitBreaker(name, threshold, recovery_timeout)
            if cls._redis:
                breaker.set_redis(cls._redis)
            cls._breakers[name] = breaker
        return cls._breakers[name]

    @classmethod
    def all(cls) -> Dict[str, CircuitBreaker]:
        return cls._breakers

def circuit_breaker(name: str, threshold: int = 5, recovery_timeout: int = 60):
    """Decorator to apply a circuit breaker to an async function."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            breaker = BreakerRegistry.get_or_create(name, threshold, recovery_timeout)
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
