import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

class TaskComplexity(str, Enum):
    DETERMINISTIC = "deterministic"   # Local 7B-9B models (parsing, cleaning)
    ANALYTICAL    = "analytical"      # Cloud 70B+ (agent logic, sector analysis)
    ADVERSARIAL   = "adversarial"     # Cloud Thinking (CRO role)
    SYNTHESIS     = "synthesis"       # Cloud Thinking/High-End (CIO role)

class LLMRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    task_id: str
    complexity: TaskComplexity
    prompt: str
    system: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.0
    stop_sequences: List[str] = []
    metadata: Dict[str, Any] = {}

class LLMResponse(BaseModel):
    content: str
    usage: Dict[str, int] = {}
    model_name: str
    backend: str
    finish_reason: Optional[str] = None

class BaseLLMBackend(ABC):
    """Abstract base class for all LLM backends (Ollama, Anthropic, DeepSeek, etc.)"""
    
    @abstractmethod
    async def complete(self, req: LLMRequest) -> LLMResponse:
        """Execute a completion request."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy and available."""
        pass
