import asyncio

from app.core.config import settings
from app.integration.github.client import GithubClient


async def main():
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN is not configured")

    client = GithubClient(settings.github_token)

    commits = await client.list_commits(
        owner="sagarsajwan79",
        repo="certx",
    )

    for commit in commits:
        print(commit["sha"])
        print(commit["commit"]["message"])
        print("-" * 50)


asyncio.run(main())
