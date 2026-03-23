import os
import logging
from typing import Dict, Any, Optional
from .llm import BaseLLMBackend, LLMRequest, LLMResponse, TaskComplexity
from .backends import OllamaBackend, AnthropicBackend, DeepSeekBackend

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        self.backends: Dict[str, BaseLLMBackend] = {}
        self._setup_backends()

    def _setup_backends(self):
        # 1. Local Ollama
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        ollama_model = os.environ.get("OLLAMA_MODEL", "qwen3.5:9b")
        self.backends["ollama"] = OllamaBackend(ollama_url, ollama_model)

        # 2. Anthropic (Claude)
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_key and "xxxxxxxx" not in anthropic_key:
            self.backends["anthropic"] = AnthropicBackend(anthropic_key)
        else:
            logger.warning("ANTHROPIC_API_KEY not configured or placeholder detected.")

        # 3. DeepSeek Chat
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        deepseek_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        if deepseek_key and "xxxxxxxx" not in deepseek_key:
            self.backends["deepseek_chat"] = DeepSeekBackend(
                deepseek_key, 
                model=os.environ.get("DEEPSEEK_CHAT_MODEL", "deepseek-chat"),
                base_url=deepseek_url
            )
            # 4. DeepSeek Reasoner
            self.backends["deepseek_reasoner"] = DeepSeekBackend(
                deepseek_key, 
                model=os.environ.get("DEEPSEEK_REASONER_MODEL", "deepseek-reasoner"),
                base_url=deepseek_url
            )
        else:
            logger.warning("DEEPSEEK_API_KEY not configured or placeholder detected.")

    async def route(self, req: LLMRequest) -> LLMResponse:
        """Route request to the most appropriate healthy backend."""
        
        target_backend_chain = self._get_backend_chain(req.complexity)
        
        last_error = None
        for backend_name in target_backend_chain:
            backend = self.backends.get(backend_name)
            if not backend:
                continue
                
            # Check health (optional, could be reactive)
            if await backend.health_check():
                try:
                    logger.info(f"Routing task {req.task_id} ({req.complexity}) to {backend_name}")
                    return await backend.complete(req)
                except Exception as e:
                    logger.error(f"Backend {backend_name} failed for task {req.task_id}: {str(e)}")
                    last_error = e
                    continue # Try next in chain
            else:
                logger.warning(f"Backend {backend_name} failed health check. Falling back...")

        if last_error:
            raise last_error
        raise RuntimeError(f"No healthy backends available for complexity {req.complexity}")

    def _get_backend_chain(self, complexity: TaskComplexity) -> list[str]:
        """Define the hierarchy of backends for each complexity level."""
        if complexity == TaskComplexity.DETERMINISTIC:
            return ["ollama", "deepseek_chat", "anthropic"]
        elif complexity == TaskComplexity.ANALYTICAL:
            return ["deepseek_chat", "anthropic", "ollama"]
        elif complexity == TaskComplexity.ADVERSARIAL:
            return ["deepseek_reasoner", "anthropic"]
        elif complexity == TaskComplexity.SYNTHESIS:
            return ["anthropic", "deepseek_reasoner"]
        return ["deepseek_chat", "ollama"]
