import logging
import httpx
import os
from ..llm import BaseLLMBackend, LLMRequest, LLMResponse, TaskComplexity

logger = logging.getLogger(__name__)

class AnthropicBackend(BaseLLMBackend):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    async def complete(self, req: LLMRequest) -> LLMResponse:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_prompt = req.system or ""
        messages = [{"role": "user", "content": req.prompt}]
        
        payload = {
            "model": self.model,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "system": system_prompt,
            "messages": messages,
            "stop_sequences": req.stop_sequences if req.stop_sequences else None
        }

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                response = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                return LLMResponse(
                    content=data["content"][0]["text"],
                    usage={
                        "prompt_tokens": data["usage"]["input_tokens"],
                        "completion_tokens": data["usage"]["output_tokens"],
                        "total_tokens": data["usage"]["input_tokens"] + data["usage"]["output_tokens"]
                    },
                    model_name=self.model,
                    backend="anthropic"
                )
            except Exception as e:
                logger.error(f"Anthropic request failed: {str(e)}")
                raise

    async def health_check(self) -> bool:
        # Simple check: can we connect to the API?
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(self.base_url)
                # Anthropic usually returns 404 or similar on base URL, but we just want to see if it responds
                return resp.status_code in [200, 404, 401]
        except Exception:
            return False
