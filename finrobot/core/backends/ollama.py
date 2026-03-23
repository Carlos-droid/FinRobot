import json
import logging
import httpx
from typing import Optional
from ..llm import BaseLLMBackend, LLMRequest, LLMResponse, TaskComplexity

logger = logging.getLogger(__name__)

class OllamaBackend(BaseLLMBackend):
    def __init__(self, base_url: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def complete(self, req: LLMRequest) -> LLMResponse:
        if req.temperature != 0.0:
            logger.warning(f"OllamaBackend usually requires temperature=0.0 for determinism. Got {req.temperature}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "model": self.model,
                    "prompt": req.prompt,
                    "system": req.system or "",
                    "stream": False,
                    "options": {
                        "temperature": req.temperature,
                        "num_predict": req.max_tokens,
                        "stop": req.stop_sequences if req.stop_sequences else None,
                        "seed": 42
                    }
                }
                
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                
                return LLMResponse(
                    content=data["response"],
                    usage={
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    },
                    model_name=self.model,
                    backend="ollama"
                )
            except Exception as e:
                logger.error(f"Ollama request failed: {str(e)}")
                raise

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Check if Ollama is running
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                
                # Check if our specific model is available
                models = [m["name"] for m in resp.json().get("models", [])]
                return any(self.model in m for m in models)
        except Exception:
            return False
