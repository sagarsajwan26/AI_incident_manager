import asyncio
import os
import sys

from app.integration.github.client import GithubClient


async def main():
    token = os.environ.get("GITHUB_TOKEN")
    if len(sys.argv) > 1:
        token = sys.argv[1]
        
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured. Provide it as an argument or env var.")

    client = GithubClient(token)

    commits = await client.list_commits(
        owner="sagarsajwan79",
        repo="certx",
    )

    for commit in commits:
        print(commit["sha"])
        print(commit["commit"]["message"])
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
