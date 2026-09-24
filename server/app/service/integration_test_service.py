import httpx


class IntegrationTestservice:
    async def test_github(self, token: str) -> None:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user", headers=headers, timeout=10.0
            )
        if response.status_code != 200:
            raise ValueError("Invalid GitHub access token.")

    async def test_slack(self, token: str) -> None:

        headers = {
            "Authorization": f"Bearer {token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://slack.com/api/auth.test", headers=headers, timeout=10.0
            )

        if response.status_code != 200:
            raise ValueError("Invalid Slack access token.")

        data = response.json()
        if not data.get("ok"):
            raise ValueError(data.get("error", "Invalid Slack access token."))

    async def test(self, provider: str, token: str) -> None:
        if provider == "github":
            await self.test_github(token)

        elif provider == "slack":
            await self.test_slack(token)

        else:
            raise ValueError(f"Unsupported integration provider: {provider}")
