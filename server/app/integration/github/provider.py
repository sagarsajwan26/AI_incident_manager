from app.integration.github.client import GithubClient


class GithubProvider:
    def __init__(self, client: GithubClient):
        self.client = client

    async def collect_commits(
        self, owner: str, repo: str, per_page: int = 10
    ) -> list[dict]:
        commits = await self.client.list_commits(
            owner=owner, repo=repo, per_page=per_page
        )

        results = []

        for commit in commits:
            sha = commit.get("sha")
            if not sha:
                continue

            details = await self.client.get_commit(owner=owner, repo=repo, sha=sha)
            commit_data = details.get("commit", {})
            author_data = commit_data.get("author") or {}
            github_author = details.get("author") or {}

            changed_files = []
            for file in details.get("files", []):
                changed_files.append(
                    {
                        "filename": file.get("filename"),
                        "status": file.get("status"),
                        "additions": file.get("additions", 0),
                        "deletions": file.get("deletions", 0),
                        "changes": file.get("changes", 0),
                    }
                )
            results.append(
                {
                    "sha": sha,
                    "repository": f"{owner}/{repo}",
                    "message": commit_data.get("message"),
                    "author": (github_author.get("login") or author_data.get("name")),
                    "timestamp": author_data.get("date"),
                    "url": details.get("html_url"),
                    "stats": {
                        "additions": details.get("stats", {}).get("additions", 0),
                        "deletions": details.get("stats", {}).get("deletions", 0),
                        "total": details.get("stats", {}).get("total", 0),
                    },
                    "changed_files": changed_files,
                }
            )
        return results
