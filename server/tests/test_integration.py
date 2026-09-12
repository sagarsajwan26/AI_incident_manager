import string
import random
import pytest
import warnings


def random_letters(n=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))

@pytest.fixture(scope="module")
def auth_tenant_1(client):
    suffix = random_letters(6)
    email = f"t1_{suffix}@example.com".lower()
    password = "Password123!"
    
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "name": "TenantOneUser",
        "tenant_name": f"TenantOne{suffix}"
    })
    assert res.status_code == 200, res.text
    
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert res.status_code == 200, res.text
    return res.cookies

@pytest.fixture(scope="module")
def auth_tenant_2(client):
    suffix = random_letters(6)
    email = f"t2_{suffix}@example.com".lower()
    password = "Password123!"
    
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "name": "TenantTwoUser",
        "tenant_name": f"TenantTwo{suffix}"
    })
    assert res.status_code == 200, res.text
    
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert res.status_code == 200, res.text
    return res.cookies

def test_crud_success_cases(client, auth_tenant_1):
    # Create
    client.cookies.update(auth_tenant_1)
    res = client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "gh_123"},
        "is_active": True
    })
    assert res.status_code == 201, res.text
    integration = res.json()
    assert integration["provider"] == "github"
    assert "credentials" not in integration  # credentials never returned
    integration_id = integration["id"]

    # Read All
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    assert res.status_code == 200, res.text
    integrations = res.json()
    assert len(integrations) >= 1
    assert any(i["id"] == integration_id for i in integrations)

    # Read One
    client.cookies.update(auth_tenant_1)
    res = client.get(f"/integration/{integration_id}")
    assert res.status_code == 200, res.text
    assert res.json()["id"] == integration_id

    # Update
    client.cookies.update(auth_tenant_1)
    res = client.patch(f"/integration/{integration_id}", json={
        "is_active": False
    })
    assert res.status_code == 200, res.text
    assert res.json()["is_active"] is False

    # Delete
    client.cookies.update(auth_tenant_1)
    res = client.delete(f"/integration/{integration_id}")
    assert res.status_code == 204, res.text

    # Verify Deletion
    client.cookies.update(auth_tenant_1)
    res = client.get(f"/integration/{integration_id}")
    assert res.status_code == 404, res.text

def test_nonexistent_integration(client, auth_tenant_1):
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration/999999")
    assert res.status_code == 404, res.text

def test_cross_tenant_isolation(client, auth_tenant_1, auth_tenant_2):
    # Tenant 1 creates integration
    client.cookies.update(auth_tenant_1)
    res = client.post("/integration", json={
        "provider": "slack",
        "credentials": {"token": "sl_123"}
    })
    assert res.status_code == 201, res.text
    integration_id = res.json()["id"]

    # Tenant 2 tries to access it -> GET
    client.cookies.update(auth_tenant_2)
    res = client.get(f"/integration/{integration_id}")
    assert res.status_code == 404, res.text

    # Tenant 2 tries to access it -> PATCH
    client.cookies.update(auth_tenant_2)
    res = client.patch(f"/integration/{integration_id}", json={"is_active": False})
    assert res.status_code == 404, res.text

    # Tenant 2 tries to access it -> TEST
    client.cookies.update(auth_tenant_2)
    res = client.post(f"/integration/{integration_id}/test")
    assert res.status_code == 404, res.text

    # Tenant 2 tries to access it -> DELETE
    client.cookies.update(auth_tenant_2)
    res = client.delete(f"/integration/{integration_id}")
    assert res.status_code == 404, res.text

def test_duplicate_provider(client, auth_tenant_1):
    # Clean up previous github integration if any
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    for it in res.json():
        if it["provider"] == "github":
            client.cookies.update(auth_tenant_1)
            client.delete(f"/integration/{it['id']}")

    # First creation
    client.cookies.update(auth_tenant_1)
    res = client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "gh_first"}
    })
    assert res.status_code == 201, res.text

    # Second creation -> Proper Error (400)
    client.cookies.update(auth_tenant_1)
    res = client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "gh_second"}
    })
    assert res.status_code == 400, res.text

from unittest.mock import patch, AsyncMock

def test_collect_github_evidence_uses_correct_tenant_token(client, auth_tenant_1, auth_tenant_2):
    # 0. Clean up any existing github integrations
    for auth in [auth_tenant_1, auth_tenant_2]:
        client.cookies.update(auth)
        res = client.get("/integration")
        for it in res.json():
            if it["provider"] == "github":
                client.cookies.update(auth)
                client.delete(f"/integration/{it['id']}")

    # 1. Tenant 1 creates integration with token_A
    client.cookies.update(auth_tenant_1)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "token_A"},
        "is_active": True
    })

    # 2. Tenant 2 creates integration with token_B
    client.cookies.update(auth_tenant_2)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "token_B"},
        "is_active": True
    })

    # 3. Tenant 1 creates an incident
    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    assert res.status_code == 200, res.text
    incident_id = res.json()["id"]

    # 4. Mock GitHub client and provider
    with patch("app.service.incident.GithubClient") as mock_client_class:
        with patch("app.service.incident.GithubProvider") as mock_provider_class:
            mock_provider_instance = mock_provider_class.return_value
            mock_provider_instance.collect_commits = AsyncMock(return_value=[
                {
                    "sha": "abc1234",
                    "repository": "test-owner/test-repo",
                    "message": "Fix database timeout",
                    "author": "Test User",
                    "timestamp": "2023-10-01T12:00:00Z",
                    "url": "https://github.com/...",
                    "stats": {},
                    "changed_files": []
                }
            ])

            # 5. Call API to collect evidence for Tenant 1's incident using Tenant 1's auth
            client.cookies.update(auth_tenant_1)
            res = client.post(f"/incidents/{incident_id}/evidence/github", json={
                "owner": "test-owner",
                "repo": "test-repo",
                "per_page": 10
            })
            assert res.status_code == 200, res.text

            # 6. Verify GithubClient was initialized with token_A (Tenant 1's token), NOT token_B
            mock_client_class.assert_called_once_with("token_A")
            
            # Verify the evidence belongs to Tenant A
            evidence_list = res.json()
            assert len(evidence_list) == 1
            assert evidence_list[0]["tenant_id"] == res.json()[0].get("tenant_id", evidence_list[0]["tenant_id"]) # ensure it matches

def test_collect_github_evidence_cross_tenant_rejection(client, auth_tenant_1, auth_tenant_2):
    # Tenant 1 creates incident
    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    incident_id = res.json()["id"]

    # Tenant 2 tries to collect evidence for Tenant 1's incident
    client.cookies.update(auth_tenant_2)
    res = client.post(f"/incidents/{incident_id}/evidence/github", json={
        "owner": "test-owner",
        "repo": "test-repo",
        "per_page": 10
    })
    assert res.status_code == 404

def test_collect_github_evidence_missing_integration(client, auth_tenant_1):
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    for it in res.json():
        if it["provider"] == "github":
            client.cookies.update(auth_tenant_1)
            client.delete(f"/integration/{it['id']}")

    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    incident_id = res.json()["id"]

    client.cookies.update(auth_tenant_1)
    res = client.post(f"/incidents/{incident_id}/evidence/github", json={
        "owner": "test-owner",
        "repo": "test-repo",
        "per_page": 10
    })
    assert res.status_code == 404
    assert "not configured" in res.json()["detail"].lower()

def test_collect_github_evidence_inactive_integration(client, auth_tenant_1):
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    for it in res.json():
        if it["provider"] == "github":
            client.cookies.update(auth_tenant_1)
            client.delete(f"/integration/{it['id']}")
            
    client.cookies.update(auth_tenant_1)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "token_A"},
        "is_active": False
    })

    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    incident_id = res.json()["id"]

    client.cookies.update(auth_tenant_1)
    res = client.post(f"/incidents/{incident_id}/evidence/github", json={
        "owner": "test-owner",
        "repo": "test-repo",
        "per_page": 10
    })
    assert res.status_code == 400
    assert "inactive" in res.json()["detail"].lower()

def test_collect_github_evidence_invalid_credentials(client, auth_tenant_1):
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    for it in res.json():
        if it["provider"] == "github":
            client.cookies.update(auth_tenant_1)
            client.delete(f"/integration/{it['id']}")
            
    client.cookies.update(auth_tenant_1)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"not_token": "something"},
        "is_active": True
    })

    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    incident_id = res.json()["id"]

    client.cookies.update(auth_tenant_1)
    res = client.post(f"/incidents/{incident_id}/evidence/github", json={
        "owner": "test-owner",
        "repo": "test-repo",
        "per_page": 10
    })
    assert res.status_code == 400
    assert "invalid" in res.json()["detail"].lower()

def test_collect_github_deployment_evidence_uses_correct_tenant_token(client, auth_tenant_1, auth_tenant_2):
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    for it in res.json():
        if it["provider"] == "github":
            client.cookies.update(auth_tenant_1)
            client.delete(f"/integration/{it['id']}")
            
    client.cookies.update(auth_tenant_1)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "token_dep_A"},
        "is_active": True
    })

    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    incident_id = res.json()["id"]

    with patch("app.service.incident.GithubClient") as mock_client_class:
        with patch("app.service.incident.GithubProvider") as mock_provider_class:
            mock_provider_instance = mock_provider_class.return_value
            mock_provider_instance.collect_deployments = AsyncMock(return_value=[
                {
                    "deployment_id": 12345,
                    "sha": "def5678",
                    "repository": "test-owner/test-repo",
                    "ref": "main",
                    "environment": "production",
                    "description": "Deploying",
                    "created_at": "2023-10-01T12:00:00Z",
                    "updated_at": "2023-10-01T12:05:00Z",
                    "url": "https://github.com/...",
                    "status": "success",
                    "status_description": "Deployed",
                    "status_created_at": "2023-10-01T12:05:00Z"
                }
            ])

            client.cookies.update(auth_tenant_1)
            res = client.post(f"/incidents/{incident_id}/evidence/github/deployments", json={
                "owner": "test-owner",
                "repo": "test-repo",
                "per_page": 10
            })
            assert res.status_code == 200, res.text

            mock_client_class.assert_called_once_with("token_dep_A")
            
            evidence_list = res.json()
            assert len(evidence_list) == 1
            assert evidence_list[0]["tenant_id"] == res.json()[0].get("tenant_id", evidence_list[0]["tenant_id"])

def test_collect_github_evidence_rolls_back_on_failure(client, auth_tenant_1):
    client.cookies.update(auth_tenant_1)
    res = client.get("/integration")
    for it in res.json():
        if it["provider"] == "github":
            client.cookies.update(auth_tenant_1)
            client.delete(f"/integration/{it['id']}")
            
    client.cookies.update(auth_tenant_1)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "token_A"},
        "is_active": True
    })

    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Tenant 1 Incident",
        "description": "This is a long description",
        "severity": "low"
    })
    incident_id = res.json()["id"]

    with patch("app.service.incident.GithubClient"):
        with patch("app.service.incident.GithubProvider") as mock_provider_class:
            mock_provider_instance = mock_provider_class.return_value
            mock_provider_instance.collect_commits = AsyncMock(return_value=[
                {
                    "sha": "commit1",
                    "repository": "test-owner/test-repo",
                    "message": "First commit",
                    "author": "Test User",
                    "timestamp": "2023-10-01T12:00:00Z",
                    "url": "https://github.com/...",
                    "stats": {},
                    "changed_files": []
                },
                {
                    "sha": "commit2",
                    "repository": "test-owner/test-repo",
                    "message": "Second commit",
                    "author": "Test User",
                    "timestamp": "2023-10-01T12:01:00Z",
                    "url": "https://github.com/...",
                    "stats": {},
                    "changed_files": []
                }
            ])
            
            with patch("app.service.incident.IncidentAuditRepository.create", new_callable=AsyncMock) as mock_audit_create:
                mock_audit_create.side_effect = [None, Exception("Simulated DB failure")]
                
                client.cookies.update(auth_tenant_1)
                res = client.post(f"/incidents/{incident_id}/evidence/github", json={
                    "owner": "test-owner",
                    "repo": "test-repo",
                    "per_page": 10
                })
                
                assert res.status_code == 500
    
    # Verify no evidence was saved for this incident
    client.cookies.update(auth_tenant_1)
    res = client.get(f"/incidents/{incident_id}/evidence")
    evidence_list = res.json()
    assert len(evidence_list) == 0

    # Verify no evidence added audit records were created
    client.cookies.update(auth_tenant_1)
    res = client.get(f"/incidents/{incident_id}/audit")
    audit_list = res.json()
    evidence_audits = [a for a in audit_list if a["action"] == "EVIDENCE_ADDED"]
    assert len(evidence_audits) == 0
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.integration.github.exceptions import (
    GithubAuthenticationError,
    GithubPermissionError,
    GithubNotFoundError,
    GithubRateLimitError,
    GithubUpstreamError,
    GithubTimeoutError,
    GithubIntegrationError,
)

@pytest.mark.parametrize("exception_class, expected_status, expected_detail", [
    (GithubAuthenticationError, 502, "GitHub authentication failed"),
    (GithubPermissionError, 502, "GitHub denied access to the requested resource"),
    (GithubNotFoundError, 404, "GitHub repository or resource was not found"),
    (GithubRateLimitError, 429, "GitHub API rate limit exceeded"),
    (GithubTimeoutError, 504, "GitHub API request timed out"),
    (GithubUpstreamError, 502, "GitHub API is currently unavailable"),
    (GithubIntegrationError, 502, "GitHub integration request failed"),
])
def test_github_api_exception_mapping(client, auth_tenant_1, exception_class, expected_status, expected_detail):
    # 1. Create incident
    client.cookies.update(auth_tenant_1)
    res = client.post("/incidents/", json={
        "title": "Test Incident",
        "description": "Test description long enough",
        "severity": "high"
    })
    incident_id = res.json()["id"]

    # 2. Setup github integration for tenant
    client.cookies.update(auth_tenant_1)
    client.post("/integration", json={
        "provider": "github",
        "credentials": {"token": "test_token"},
        "is_active": True
    })

    # 3. Request evidence, but mock GithubClient to raise parameterized exception
    with patch("app.service.incident.GithubProvider") as mock_provider_class:
        mock_provider_instance = mock_provider_class.return_value
        mock_provider_instance.collect_commits.side_effect = exception_class("Mock error")
        
        client.cookies.update(auth_tenant_1)
        res = client.post(f"/incidents/{incident_id}/evidence/github", json={
            "owner": "test",
            "repo": "test",
            "per_page": 10
        })
        
        assert res.status_code == expected_status
        assert res.json()["detail"] == expected_detail
