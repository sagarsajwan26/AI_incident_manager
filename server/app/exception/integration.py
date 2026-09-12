class DuplicateIntegrationError(Exception):
    """Raised when a tenant already has an integration for a provider."""

class IntegrationConnectionError(Exception):
    def __init__(self, provider: str, cause: Exception):
        self.provider = provider
        self.cause = cause

        super().__init__(
            f"{provider} integration request failed: {cause}"
        )