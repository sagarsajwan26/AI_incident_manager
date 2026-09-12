# Exception hierarchy for AI provider errors

class AIProviderError(Exception):
    """Base class for AI provider errors.

    Attributes:
        provider (str): Name of the AI provider (e.g., "ollama", "openai").
        cause (Exception): Original exception that triggered this error.
    """

    def __init__(self, provider: str, cause: Exception):
        self.provider = provider
        self.cause = cause
        super().__init__(f"{provider} provider error: {cause}")


class AIProviderTimeoutError(AIProviderError):
    """Raised when the AI provider request times out."""
    pass


class AIProviderUnavailableError(AIProviderError):
    """Raised when the AI provider is unavailable or returns upstream errors."""
    pass


class AIInvestigationError(AIProviderError):
    """Base class for any error occurring during the AI investigation workflow."""
    pass

class AIInvalidResponseError(AIProviderError):
    """Raised when the AI provider returns malformed or empty JSON response."""
    pass

class AIConfigurationError(AIProviderError):
    """Raised when configuration for the AI provider is missing or invalid."""
    pass
