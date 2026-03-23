from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn
import threading
import asyncio
import logging
from typing import Dict, Any

from .circuit_breaker import BreakerRegistry
from .dlq import DeadLetterQueue

app = FastAPI(title="FinRobot Health & Metrics")
dlq = DeadLetterQueue()
log = logging.getLogger(__name__)

async def _check_redis() -> Dict[str, Any]:
    try:
        from redis.asyncio import Redis
        r = Redis.from_url('redis://localhost:6379')
        if await r.ping():
            return {"ok": True, "details": "Redis connected"}
        return {"ok": False, "details": "Redis ping failed"}
    except Exception as e:
        return {"ok": False, "details": str(e)}

async def _check_ollama() -> Dict[str, Any]:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get('http://localhost:11434/api/tags')
            if resp.status_code == 200:
                return {"ok": True, "details": "Ollama responding"}
            return {"ok": False, "details": f"Ollama HTTP {resp.status_code}"}
    except Exception as e:
        return {"ok": False, "details": str(e)}

def _check_breakers() -> Dict[str, Any]:
    breakers = BreakerRegistry.all()
    status = {name: b.state.value for name, b in breakers.items()}
    all_closed = all(s == 'closed' for s in status.values())
    return {"ok": all_closed, "details": status}

@app.get("/health")
async def health_check():
    checks = {
        "redis": await _check_redis(),
        "ollama": await _check_ollama(),
        "breakers": _check_breakers(),
    }
    all_ok = all(c["ok"] for c in checks.values())
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={
            "status": "healthy" if all_ok else "degraded",
            "checks": checks
        }
    )

@app.get("/ready")
async def ready_check():
    # In a real app, this would check if initialization is complete
    return {"status": "ready"}

@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    lines = []
    # Circuit Breaker Metrics
    for name, breaker in BreakerRegistry.all().items():
        lines.append(f'circuit_breaker_failures_total{{name="{name}"}} {breaker._failure_count}')
        # state: 0=closed, 1=open, 2=half_open
        state_val = 0 if breaker.state == "closed" else 1 if breaker.state == "open" else 2
        lines.append(f'circuit_breaker_state{{name="{name}"}} {state_val}')
    
    # DLQ Metrics
    try:
        stats = await dlq.get_stats()
        lines.append(f'dlq_pending_items {stats["pending_count"]}')
    except:
        pass
        
    return "\n".join(lines) + "\n"

@app.get("/circuit-breakers")
async def get_breakers():
    return {name: {"state": b.state.value, "failures": b._failure_count} 
            for name, b in BreakerRegistry.all().items()}

def start_health_server(port: int = 8765):
    """Launches the health server in a separate thread."""
    def _run():
        log.info(f"Starting Health Server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
    
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
