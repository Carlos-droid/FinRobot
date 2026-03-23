from .llm_config import get_ollama_config, get_nim_config, get_auto_config

# Lazy imports — solo se cargan cuando se acceden
def __getattr__(name):
    if name == "SingleAssistant":
        from .agents.workflow import SingleAssistant
        return SingleAssistant
    elif name == "MultiAssistant":
        from .agents.workflow import MultiAssistant
        return MultiAssistant
    raise AttributeError(f"module 'finrobot' has no attribute {name!r}")
