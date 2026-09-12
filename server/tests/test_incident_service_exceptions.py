import pytest
from unittest.mock import AsyncMock, patch
from app.service.incident import IncidentService
from app.integration.github.exceptions import GithubRateLimitError
from app.exception.integration import IntegrationConnectionError
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_collect_github_evidence_integration_error_translation():
    mock_db = AsyncMock()
    service = IncidentService(mock_db)
    
    current_user = User(id=1, email="test@test.com", passwordHash="hash", tenant_id=1, role=UserRole.ADMIN)
    
    # Mock get_incident
    mock_incident = AsyncMock()
    mock_incident.id = 1
    service.get_incident = AsyncMock(return_value=mock_incident)
    
    # Mock integration service
    mock_integration = AsyncMock()
    mock_integration.is_active = True
    mock_integration.credentials = {"token": "test_token"}
    service.integration_service.get_integration_by_provider = AsyncMock(return_value=mock_integration)
    
    # Mock GithubProvider to raise GithubRateLimitError
    with patch("app.service.incident.GithubProvider") as mock_provider_class:
        mock_provider_instance = AsyncMock()
        mock_provider_instance.collect_commits.side_effect = GithubRateLimitError("Rate limit exceeded")
        mock_provider_class.return_value = mock_provider_instance
        
        with pytest.raises(IntegrationConnectionError) as exc_info:
            await service.collect_github_evidence(
                incident_id=1,
                owner="owner",
                repo="repo",
                per_page=10,
                current_user=current_user
            )
            
        # Verify the exception type and its underlying cause
        assert exc_info.value.provider == "github"
        assert isinstance(exc_info.value.cause, GithubRateLimitError)
