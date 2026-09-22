import json
import string
import random

import pytest
from unittest.mock import patch
from app.ai.base import LLMProvider

class FakeLLMProvider(LLMProvider):
    def __init__(self, response: str):
        self.response = response

    async def generate(self, prompt: str) -> str:
        if self.response == "error":
            raise RuntimeError("AI provider unavailable")
        return self.response

def valid_ai_response():
    return {
        "summary": "API Test summary.",
        "likely_root_cause": "API Test root cause.",
        "root_cause_status": "unknown",
        "evidence": ["Some evidence"],
        "evidence_assessment": [
            {
                "claim": "Some claim",
                "support": "Some support",
                "support_level": "direct",
                "supports_root_cause": False
            }
        ],
        "impact": "API Test impact.",
        "recommended_actions": ["API Test action."],
        "unknowns": ["API Test unknown."],
        "confidence": 0.5,
    }

def random_letters(n=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))



@pytest.fixture(scope="module")
def auth_setup(client):
    suffix = random_letters(6)
    email = f"user_{suffix}@example.com".lower()
    password = "Password123!"
    
    # Register
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "name": "TestUser",
        "tenant_name": f"Tenant{suffix}"
    })
    assert res.status_code == 200, res.text
    
    # Login to set cookie
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert res.status_code == 200, res.text
    return {"email": email, "password": password}


@pytest.fixture
def test_incident_id(client, auth_setup):
    response = client.post(
        "/incidents/",
        json={
            "title": "API Test Incident",
            "description": "Created for API tests",
            "severity": "high"
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_valid_authenticated_investigation(client, test_incident_id):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
        response = client.post(f"/incidents/{test_incident_id}/investigate")
        
    assert response.status_code == 200, response.text
    data = response.json()
    assert "summary" in data
    assert "likely_root_cause" in data
    assert data["root_cause_status"] == "unknown"


def test_unauthenticated_request(client, test_incident_id, auth_setup):
    # Temporarily remove cookies
    cookies_backup = dict(client.cookies)
    client.cookies.clear()
    
    response = client.post(f"/incidents/{test_incident_id}/investigate")
    assert response.status_code == 401
    
    # Restore cookies
    client.cookies.update(cookies_backup)


def test_nonexistent_incident(client, auth_setup):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
        response = client.post("/incidents/999999/investigate")
        
    assert response.status_code == 404


def test_wrong_tenant(client, test_incident_id, auth_setup):
    # Register/login a different user in a different tenant using the SAME client
    suffix = random_letters(6)
    email = f"wrong_{suffix}@example.com".lower()
    password = "Password123!"
    
    client.post("/auth/register", json={
        "email": email,
        "password": password,
        "name": "WrongUser",
        "tenant_name": f"WrongTenant{suffix}"
    })
    
    client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
        response = client.post(f"/incidents/{test_incident_id}/investigate")
        
    assert response.status_code in (403, 404), response.text
    
    # Restore the original user
    client.post("/auth/login", json={
        "email": auth_setup["email"],
        "password": auth_setup["password"]
    })


def test_ai_provider_failure(client, test_incident_id):
    fake_provider = FakeLLMProvider("error")
    with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
        response = client.post(f"/incidents/{test_incident_id}/investigate")
        
    # We expect 502
    assert response.status_code == 502


def test_investigation_is_persisted(client, test_incident_id):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
        res = client.post(f"/incidents/{test_incident_id}/investigate")
        assert res.status_code == 200, res.text
        
        history_resp = client.get(f"/incidents/{test_incident_id}/investigations")
        
    assert history_resp.status_code == 200, history_resp.text
    history = history_resp.json()
    assert len(history) > 0
    investigation = history[-1]
    
    assert "tenant_id" in investigation
    assert "incident_id" in investigation
    assert "triggered_by" in investigation
    assert "provider" in investigation
    assert "model" in investigation
    assert "result" in investigation
    assert "confidence" in investigation
    assert "created_at" in investigation

# ---------- ORCHESTRATION TESTS ----------

from app.service.incident import IncidentService
original_get_incident = IncidentService.get_incident
from unittest.mock import AsyncMock

def test_orchestration_github_resource_exists(client, test_incident_id):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    
    async def mock_get_incident(self, incident_id, current_user):
        incident = await original_get_incident(self, incident_id, current_user)
        from app.models.incident_resource import IncidentResource
        if not any(r.provider == "github" for r in incident.resources):
            incident.resources.append(IncidentResource(provider="github", resource_type="repository", identifier="owner/repo", tenant_id=current_user.tenant_id, incident_id=incident.id))
        return incident

    with patch("app.service.incident.IncidentService.get_incident", autospec=True, side_effect=mock_get_incident):
        with patch("app.service.incident.IncidentService.collect_github_evidence", new_callable=AsyncMock) as mock_commits:
            with patch("app.service.incident.IncidentService.collect_github_deployment_evidence", new_callable=AsyncMock) as mock_deploy:
                with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
                    response = client.post(f"/incidents/{test_incident_id}/investigate")
                    
    assert response.status_code == 200, response.text
    mock_commits.assert_awaited_once()
    mock_deploy.assert_awaited_once()


def test_orchestration_no_github_resource(client, test_incident_id):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    
    with patch("app.service.incident.IncidentService.collect_github_evidence", new_callable=AsyncMock) as mock_commits:
        with patch("app.service.incident.IncidentService.collect_github_deployment_evidence", new_callable=AsyncMock) as mock_deploy:
            with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
                response = client.post(f"/incidents/{test_incident_id}/investigate")
                    
    assert response.status_code == 200, response.text
    mock_commits.assert_not_called()
    mock_deploy.assert_not_called()


def test_orchestration_github_collection_fails(client, test_incident_id):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    
    async def mock_get_incident(self, incident_id, current_user):
        incident = await original_get_incident(self, incident_id, current_user)
        from app.models.incident_resource import IncidentResource
        if not any(r.provider == "github" for r in incident.resources):
            incident.resources.append(IncidentResource(provider="github", resource_type="repository", identifier="owner/repo", tenant_id=current_user.tenant_id, incident_id=incident.id))
        return incident

    from app.exception.integration import IntegrationConnectionError
    
    with patch("app.service.incident.IncidentService.get_incident", autospec=True, side_effect=mock_get_incident):
        with patch("app.service.incident.IncidentService.collect_github_evidence", new_callable=AsyncMock, side_effect=IntegrationConnectionError(provider="github", cause=Exception("failed"))):
            with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider) as mock_ai:
                response = client.post(f"/incidents/{test_incident_id}/investigate")
                    
    assert response.status_code == 502, response.text


def test_orchestration_permission_unauthorized(client, test_incident_id):
    fake_provider = FakeLLMProvider(json.dumps(valid_ai_response()))
    
    async def mock_get_incident(self, incident_id, current_user):
        from app.models.user import UserRole
        current_user.role = UserRole.MEMBER
        return await original_get_incident(self, incident_id, current_user)

    with patch("app.service.incident.IncidentService.get_incident", autospec=True, side_effect=mock_get_incident):
        with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
            response = client.post(f"/incidents/{test_incident_id}/investigate")
            
    assert response.status_code == 403, response.text
