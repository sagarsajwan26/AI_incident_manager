import httpx

from app.integration.github.exceptions import (
    GithubIntegrationError,
    GithubAuthenticationError,
    GithubPermissionError,
    GithubNotFoundError,
    GithubRateLimitError,
    GithubUpstreamError,
    GithubTimeoutError,
)

class GithubClient:
    BASE_URL = "https://api.github.com"
    API_VERSION = "2026-03-10"

    def __init__(self, token: str):
        self.token = token

    def _handle_request_error(self, exc: Exception):
        if isinstance(exc, httpx.HTTPStatusError):
            status = exc.response.status_code
            if status == 401:
                raise GithubAuthenticationError(f"GitHub authentication failed: {exc}") from exc
            elif status == 403:
                raise GithubPermissionError(f"GitHub permission denied: {exc}") from exc
            elif status == 404:
                raise GithubNotFoundError(f"GitHub resource not found: {exc}") from exc
            elif status == 429:
                raise GithubRateLimitError(f"GitHub rate limit exceeded: {exc}") from exc
            elif status >= 500:
                raise GithubUpstreamError(f"GitHub upstream error: {exc}") from exc
            else:
                raise GithubIntegrationError(f"GitHub API error {status}: {exc}") from exc
        elif isinstance(exc, httpx.TimeoutException):
            raise GithubTimeoutError(f"GitHub request timed out: {exc}") from exc
        elif isinstance(exc, httpx.HTTPError):
            raise GithubIntegrationError(f"GitHub network error: {exc}") from exc
        raise exc

    async def list_commits(
        self, owner: str, repo: str, per_page: int = 10
    ) -> list[dict]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": self.API_VERSION,
        }

        params = {"per_page": per_page}
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list):
                raise GithubIntegrationError("github returned an unexpected response")

            return data
        except httpx.HTTPError as exc:
            self._handle_request_error(exc)

    async def get_commit(
        self,
        owner: str,
        repo: str,
        sha: str,
    ) -> dict:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": self.API_VERSION,
        }
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits/{sha}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise GithubIntegrationError("github returned an unexpected commit response")

            return data
        except httpx.HTTPError as exc:
            self._handle_request_error(exc)

    async def list_deployments(
        self, owner: str, repo: str, per_page: int = 10
    ) -> list[dict]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": self.API_VERSION,
        }
        params = {
            "per_page": per_page,
        }
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/deployments"
        try:

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, list):
                    raise GithubIntegrationError(
                        "github returned an unexpected deployments response"
                    )
                return data
        except httpx.HTTPError as exc:
            self._handle_request_error(exc)

    async def get_deployment_status(
        self,
        owner: str,
        repo: str,
        deployment_id: int,
    ) -> list[dict]:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": self.API_VERSION,
        }
        url = (
            f"{self.BASE_URL}/repos/{owner}/{repo}/deployments/{deployment_id}/statuses"
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise GithubIntegrationError(
                    "github returned an unexpected deployment status response"
                )
            return data
        except httpx.HTTPError as exc:
            self._handle_request_error(exc)
