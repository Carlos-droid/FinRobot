import logging
import httpx
from typing import Optional
from ..llm import BaseLLMBackend, LLMRequest, LLMResponse, TaskComplexity

logger = logging.getLogger(__name__)

class DeepSeekBackend(BaseLLMBackend):
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def complete(self, req: LLMRequest) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if req.system:
            messages.append({"role": "system", "content": req.system})
        messages.append({"role": "user", "content": req.prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "stream": False,
            "stop": req.stop_sequences if req.stop_sequences else None
        }
        
        # Reasoner/Thinking mode specific handling could go here if needed via specialized prompts
        # or if the model name is 'deepseek-reasoner'.

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                choice = data["choices"][0]
                return LLMResponse(
                    content=choice["message"]["content"],
                    usage={
                        "prompt_tokens": data["usage"]["prompt_tokens"],
                        "completion_tokens": data["usage"]["completion_tokens"],
                        "total_tokens": data["usage"]["total_tokens"]
                    },
                    model_name=self.model,
                    backend="deepseek",
                    finish_reason=choice.get("finish_reason")
                )
            except Exception as e:
                logger.error(f"DeepSeek request failed: {str(e)}")
                raise

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                # Check models endpoint
                resp = await client.get(f"{self.base_url}/models", headers=headers)
                return resp.status_code == 200
        except Exception:
            return False
