import pytest
from unittest.mock import AsyncMock, MagicMock
from app.integration.github.provider import GithubProvider

@pytest.mark.asyncio
async def test_collect_commits_normalization():
    mock_client = MagicMock()
    mock_client.list_commits = AsyncMock(return_value=[
        {"sha": "abc1234"},
        {"sha": "def5678"}
    ])
    
    async def mock_get_commit(owner, repo, sha):
        return {
            "commit": {
                "message": f"Message for {sha}",
                "author": {"name": f"Author {sha}", "date": f"2023-10-01T12:00:00Z"}
            },
            "html_url": f"https://github.com/owner/repo/commit/{sha}",
            "stats": {"total": 5},
            "files": [{"filename": "app.py"}]
        }
    
    mock_client.get_commit = mock_get_commit
    
    provider = GithubProvider(mock_client)
    commits = await provider.collect_commits("owner", "repo")
    
    assert len(commits) == 2
    
    assert commits[0]["sha"] == "abc1234"
    assert commits[0]["repository"] == "owner/repo"
    assert commits[0]["message"] == "Message for abc1234"
    assert commits[0]["author"] == "Author abc1234"
    assert commits[0]["timestamp"] == "2023-10-01T12:00:00Z"
    assert commits[0]["url"] == "https://github.com/owner/repo/commit/abc1234"
    assert commits[0]["stats"] == {"additions": 0, "deletions": 0, "total": 5}
    assert commits[0]["changed_files"] == [{
        "filename": "app.py",
        "status": None,
        "additions": 0,
        "deletions": 0,
        "changes": 0
    }]

@pytest.mark.asyncio
async def test_collect_commits_missing_sha():
    mock_client = MagicMock()
    mock_client.list_commits = AsyncMock(return_value=[
        {"sha": "abc"},
        {"message": "broken commit"},
        {"sha": "xyz"}
    ])
    
    mock_client.get_commit = AsyncMock(return_value={
        "commit": {"message": "valid", "author": {"name": "valid", "date": "2023-10-01T12:00:00Z"}},
        "html_url": "url",
        "stats": {},
        "files": []
    })
    
    provider = GithubProvider(mock_client)
    commits = await provider.collect_commits("owner", "repo")
    
    assert len(commits) == 2
    assert commits[0]["sha"] == "abc"
    assert commits[1]["sha"] == "xyz"
    assert mock_client.get_commit.call_count == 2

@pytest.mark.asyncio
async def test_collect_deployments_normalization():
    mock_client = MagicMock()
    mock_client.list_deployments = AsyncMock(return_value=[
        {
            "id": 12345,
            "sha": "def5678",
            "ref": "main",
            "environment": "production",
            "description": "Deploying to prod",
            "created_at": "2023-10-01T12:00:00Z",
            "updated_at": "2023-10-01T12:05:00Z",
            "url": "https://api.github.com/repos/owner/repo/deployments/12345"
        }
    ])
    
    mock_client.get_deployment_status = AsyncMock(return_value=[
        {
            "state": "success",
            "description": "Deployed successfully",
            "created_at": "2023-10-01T12:10:00Z"
        },
        {
            "state": "pending",
            "description": "Deploying",
            "created_at": "2023-10-01T12:06:00Z"
        }
    ])
    
    provider = GithubProvider(mock_client)
    deployments = await provider.collect_deployments("owner", "repo")
    
    assert len(deployments) == 1
    d = deployments[0]
    
    assert d["deployment_id"] == 12345
    assert d["repository"] == "owner/repo"
    assert d["sha"] == "def5678"
    assert d["ref"] == "main"
    assert d["environment"] == "production"
    assert d["description"] == "Deploying to prod"
    assert d["created_at"] == "2023-10-01T12:00:00Z"
    assert d["updated_at"] == "2023-10-01T12:05:00Z"
    assert d["url"] == "https://api.github.com/repos/owner/repo/deployments/12345"
    assert d["status"] == "success"
    assert d["status_description"] == "Deployed successfully"
    assert d["status_created_at"] == "2023-10-01T12:10:00Z"

@pytest.mark.asyncio
async def test_collect_deployments_no_statuses():
    mock_client = MagicMock()
    mock_client.list_deployments = AsyncMock(return_value=[
        {
            "id": 12345,
            "sha": "def5678",
            "ref": "main",
            "environment": "production",
            "description": "Deploying to prod",
            "created_at": "2023-10-01T12:00:00Z",
            "updated_at": "2023-10-01T12:05:00Z",
            "url": "https://api.github.com/repos/owner/repo/deployments/12345"
        }
    ])
    
    mock_client.get_deployment_status = AsyncMock(return_value=[])
    
    provider = GithubProvider(mock_client)
    deployments = await provider.collect_deployments("owner", "repo")
    
    assert len(deployments) == 1
    d = deployments[0]
    
    assert d["status"] is None
    assert d["status_description"] is None
    assert d["status_created_at"] is None
