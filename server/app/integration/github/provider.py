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

    async def collect_deployments(
        self, owner: str, repo: str, per_page: int = 10
    ) -> list[dict]:
        deployments = await self.client.list_deployments(
            owner=owner, repo=repo, per_page=per_page
        )

        results = []

        for deployment in deployments:
            deployment_id = deployment.get("id")

            if not deployment_id:
                continue

            statuses = await self.client.get_deployment_status(
                owner=owner,
                repo=repo,
                deployment_id=deployment_id,
            )

            latest_status = statuses[0] if statuses else None

            results.append(
                {
                    "deployment_id": deployment_id,
                    "repository": f"{owner}/{repo}",
                    "sha": deployment.get("sha"),
                    "ref": deployment.get("ref"),
                    "environment": deployment.get("environment"),
                    "description": deployment.get("description"),
                    "created_at": deployment.get("created_at"),
                    "updated_at": deployment.get("updated_at"),
                    "url": deployment.get("url"),
                    "status": (latest_status.get("state") if latest_status else None),
                    "status_description": (
                        latest_status.get("description") if latest_status else None
                    ),
                    "status_created_at": (
                        latest_status.get("created_at") if latest_status else None
                    ),
                }
            )
        return results
