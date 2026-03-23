class PipelineError(Exception):
    """Base exception for the FinRobot pipeline."""
    pass

class StateTransitionError(PipelineError):
    """Raised when an invalid state transition is attempted."""
    pass

class AgentError(PipelineError):
    """Raised when an agent fails to execute or returns invalid output."""
    pass

class CircuitOpenError(PipelineError):
    """Raised when a circuit breaker is open."""
    pass

class DLQError(PipelineError):
    """Raised when an error occurs while interacting with the Dead Letter Queue."""
    pass

class APIKeyMissingError(PipelineError):
    """Raised when a required API key is missing."""
    pass
