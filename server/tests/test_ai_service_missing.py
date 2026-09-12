import pytest

@pytest.fixture
def auth_setup(client):
    """Register and login a test user, returning auth info."""
    suffix = "auth"  # simple static suffix
    email = f"user_{suffix}@example.com".lower()
    password = "Password123!"
    # Register
    res = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "TestUser",
            "tenant_name": f"Tenant{suffix}",
        },
    )
    assert res.status_code == 200, res.text
    # Login to set cookie
    res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, res.text
    return {"email": email, "password": password}

@pytest.fixture
def test_incident_id(client, auth_setup):
    """Create an incident and return its ID for tests needing one."""
    response = client.post(
        "/incidents/",
        json={
            "title": "Test Incident",
            "description": "Created for AI service missing test",
            "severity": "low",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]

def test_ai_service_missing_configuration(client, test_incident_id, auth_setup, monkeypatch):
    """When IncidentService is instantiated without an AI service, the endpoint should raise
    AIConfigurationError -> HTTP 500 and no investigation is persisted."""
    # Patch IncidentService used in the route to force ai_service=None
    from app.service.incident import IncidentService as RealIncidentService

    class MockIncidentService(RealIncidentService):
        def __init__(self, db):
            super().__init__(db, ai_service=None)

    # Apply the monkeypatch to the route module
    monkeypatch.setattr('app.routes.api.v1.incident.IncidentService', MockIncidentService)

    response = client.post(f"/incidents/{test_incident_id}/investigate")
    assert response.status_code == 500, response.text

    # Verify no investigation record was created
    history_resp = client.get(f"/incidents/{test_incident_id}/investigations")
    assert history_resp.status_code == 200, history_resp.text
    history = history_resp.json()
    assert len(history) == 0

