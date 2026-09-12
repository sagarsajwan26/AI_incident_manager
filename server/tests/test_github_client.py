import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.integration.github.client import GithubClient
from app.integration.github.exceptions import (
    GithubIntegrationError,
    GithubAuthenticationError,
    GithubPermissionError,
    GithubNotFoundError,
    GithubRateLimitError,
    GithubUpstreamError,
    GithubTimeoutError,
)

@pytest.mark.asyncio
async def test_list_commits_success():
    client = GithubClient("token_A")
    
    mock_response = MagicMock()
    mock_response.json.return_value = [{"sha": "abc123"}]
    mock_response.raise_for_status = MagicMock()
    
    mock_get = AsyncMock(return_value=mock_response)
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        result = await client.list_commits("owner", "repo")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["sha"] == "abc123"
        
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/owner/repo/commits",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": "Bearer token_A",
                "X-GitHub-Api-Version": "2026-03-10"
            },
            params={"per_page": 10}
        )

@pytest.mark.asyncio
@pytest.mark.parametrize("status_code, expected_exception", [
    (401, GithubAuthenticationError),
    (403, GithubPermissionError),
    (404, GithubNotFoundError),
    (429, GithubRateLimitError),
    (500, GithubUpstreamError),
    (502, GithubUpstreamError),
    (418, GithubIntegrationError), # Unmapped status codes fallback to base error
])
async def test_github_http_status_mapping(status_code, expected_exception):
    client = GithubClient("token_A")
    
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
    
    mock_get = AsyncMock(return_value=mock_response)
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        with pytest.raises(expected_exception):
            await client.list_commits("owner", "repo")

@pytest.mark.asyncio
async def test_github_timeout_mapping():
    client = GithubClient("token_A")
    
    mock_get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        with pytest.raises(GithubTimeoutError):
            await client.list_commits("owner", "repo")

@pytest.mark.asyncio
async def test_list_commits_malformed_response():
    client = GithubClient("token_A")
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "something unexpected"}
    
    mock_get = AsyncMock(return_value=mock_response)
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        with pytest.raises(GithubIntegrationError) as exc_info:
            await client.list_commits("owner", "repo")
        assert "unexpected response" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_commit_success():
    client = GithubClient("token_A")
    mock_response = MagicMock()
    mock_response.json.return_value = {"commit": {"message": "hello"}}
    mock_get = AsyncMock(return_value=mock_response)
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        res = await client.get_commit("owner", "repo", "sha123")
        assert isinstance(res, dict)
        assert res["commit"]["message"] == "hello"

@pytest.mark.asyncio
async def test_list_deployments_success():
    client = GithubClient("token_A")
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1}]
    mock_get = AsyncMock(return_value=mock_response)
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        res = await client.list_deployments("owner", "repo")
        assert isinstance(res, list)
        assert len(res) == 1
        assert res[0]["id"] == 1

@pytest.mark.asyncio
async def test_get_deployment_status_success():
    client = GithubClient("token_A")
    mock_response = MagicMock()
    mock_response.json.return_value = [{"state": "success"}]
    mock_get = AsyncMock(return_value=mock_response)
    
    mock_client_instance = MagicMock()
    mock_client_instance.get = mock_get
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client_instance
    mock_ctx.__aexit__.return_value = None
    
    with patch("app.integration.github.client.httpx.AsyncClient", return_value=mock_ctx):
        res = await client.get_deployment_status("owner", "repo", 1)
        assert isinstance(res, list)
        assert len(res) == 1
        assert res[0]["state"] == "success"
