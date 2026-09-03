import httpx


class GithubClient:
    BASE_URL = "https://api.github.com"
    API_VERSION = "2026-03-10"

    def __init__(self, token: str):
        self.token = token

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
                raise RuntimeError("github returned an unexpected response")

            return data
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Github request failed: {exc}") from exc

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
                raise RuntimeError("github returned an unexpected commit response")

            return data
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Github commit request failed: {exc}") from exc

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
                    raise RuntimeError(
                        "github returned an unexpected deployments response"
                    )
                return data
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Github deployment request failed : {exc}") from exc

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
                raise RuntimeError(
                    "github returned an unexpected deployment status response"
                )
            return data
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Github deployment status request failed: {exc}"
            ) from exc
