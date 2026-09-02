from app.integration.github.client import GithubClient


class GithubProvider:
    def __init__(self, client: GithubClient):
        self.client = client

    async def collect_commits(
        self,
        owner: str,
        repo: str,
    ) -> list[dict]:
        commits = await self.client.list_commits(owner=owner, repo=repo)

        return [
            {
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": (
                    commit["author"]["login"]
                    if commit.get("author")
                    else commit["commit"]["author"]["name"]
                ),
                "url": commit["html_url"],
            }
            for commit in commits
        ]
