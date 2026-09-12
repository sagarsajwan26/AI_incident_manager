class GithubIntegrationError(Exception):
    pass

class GithubAuthenticationError(GithubIntegrationError):
    pass

class GithubPermissionError(GithubIntegrationError):
    pass

class GithubNotFoundError(GithubIntegrationError):
    pass

class GithubRateLimitError(GithubIntegrationError):
    pass

class GithubUpstreamError(GithubIntegrationError):
    pass

class GithubTimeoutError(GithubIntegrationError):
    pass
