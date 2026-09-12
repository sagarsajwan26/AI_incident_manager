# Exception hierarchy for AI investigation failures

class AIInvestigationError(Exception):
    """Base exception for AI investigation failures.

    Attributes:
        provider (str): Name of the AI provider involved in the investigation.
        cause (Exception | None): Original exception that triggered the failure.
    """

    def __init__(self, provider: str, cause: Exception | None = None):
        self.provider = provider
        self.cause = cause
        if cause:
            super().__init__(f"{provider} investigation error: {cause}")
        else:
            super().__init__(f"{provider} investigation error")


class AIProviderError(AIInvestigationError):
    """Base class for AI provider errors."""
    pass


class AIProviderTimeoutError(AIProviderError):
    """Raised when the AI provider request times out."""
    pass


class AIProviderUnavailableError(AIProviderError):
    """Raised when the AI provider is unavailable or returns upstream errors."""
    pass


class AIInvalidResponseError(AIInvestigationError):
    """Raised when the AI provider returns malformed or invalid output."""
    pass


class AIConfigurationError(AIInvestigationError):
    """Raised when AI configuration is missing or invalid."""
    pass
