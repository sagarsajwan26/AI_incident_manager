import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.incident import IncidentStatus
from app.models.incident_action import IncidentActionPhase
from app.models.user import User, UserRole
import random
import string

def random_letters(n):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

def register_user(client: TestClient, role: UserRole, email: str, tenant_name: str):
    res = client.post("/auth/register", json={
        "email": email,
        "password": "Password123!",
        "name": "Auth Test",
        "tenant_name": tenant_name
    })
    return res.json()

def override_auth(user_data: dict, role: UserRole):
    def _override():
        return User(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"],
            passwordHash="hash",
            role=role,
            tenant_id=user_data["tenant_id"],
        )
    app.dependency_overrides[get_current_user] = _override

@pytest.fixture
def test_incident(client):
    suffix = random_letters(6)
    # We will register one admin for tenant 1, one admin for tenant 2.
    admin1_data = register_user(client, UserRole.ADMIN, f"admin_{suffix}@example.com", f"Tenant_{suffix}")
    admin2_data = register_user(client, UserRole.ADMIN, f"other_admin_{suffix}@example.com", f"Other_{suffix}")

    # Set up auth for admin1
    override_auth(admin1_data, UserRole.ADMIN)

    # Create investigators inside tenant 1 using admin
    res = client.post("/users/", json={
        "email": f"inv_{suffix}@example.com",
        "password": "Password123!",
        "name": "Investigator",
        "role": "investigator"
    })
    assert res.status_code == 200, res.text
    inv_data = res.json()

    res = client.post("/users/", json={
        "email": f"other_inv_{suffix}@example.com",
        "password": "Password123!",
        "name": "Other Investigator",
        "role": "investigator"
    })
    assert res.status_code == 200, res.text
    other_inv_data = res.json()

    # Create incident as admin
    res = client.post("/incidents/", json={
        "title": "Action Test Incident",
        "description": "Testing actions",
        "severity": "high"
    })
    assert res.status_code == 200, res.text
    incident = res.json()
    
    # Assign incident to inv
    res = client.patch(f"/incidents/{incident['id']}/assign", json={"investigator_id": inv_data["id"]})
    assert res.status_code == 200, res.text
    
    app.dependency_overrides.pop(get_current_user, None)
    return {
        "incident": incident,
        "admin": admin1_data,
        "inv": inv_data,
        "other_inv": other_inv_data,
        "other_admin": admin2_data
    }

def test_post_action_admin_can_create(client, test_incident):
    override_auth(test_incident["admin"], UserRole.ADMIN)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CONTAINMENT.value,
        "action_type": "Blocked IP",
        "description": "Blocked malicious IP address",
        "outcome": "Traffic stopped"
    })
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["action_type"] == "Blocked IP"
    app.dependency_overrides.pop(get_current_user, None)

def test_post_action_assigned_investigator_can_create(client, test_incident):
    override_auth(test_incident["inv"], UserRole.INVESTIGATOR)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.RESOLUTION.value,
        "action_type": "Restarted Service",
        "description": "Restarted the core service"
    })
    assert res.status_code == 200, res.text
    app.dependency_overrides.pop(get_current_user, None)

def test_post_action_unassigned_investigator_forbidden(client, test_incident):
    override_auth(test_incident["other_inv"], UserRole.INVESTIGATOR)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CONTAINMENT.value,
        "action_type": "Blocked IP",
        "description": "Should fail"
    })
    # Investigators can only see incidents assigned to them.
    # get_incident will raise 404.
    assert res.status_code == 404
    app.dependency_overrides.pop(get_current_user, None)

def test_post_action_cross_tenant_not_found(client, test_incident):
    override_auth(test_incident["other_admin"], UserRole.ADMIN)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CONTAINMENT.value,
        "action_type": "Blocked IP",
        "description": "Should fail"
    })
    assert res.status_code == 404
    app.dependency_overrides.pop(get_current_user, None)

def test_get_actions_admin_and_investigator(client, test_incident):
    # inv creates
    override_auth(test_incident["inv"], UserRole.INVESTIGATOR)
    client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CONTAINMENT.value,
        "action_type": "Action 1",
        "description": "Action 1"
    })

    # admin checks
    override_auth(test_incident["admin"], UserRole.ADMIN)
    res = client.get(f"/incidents/{test_incident['incident']['id']}/actions")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # assigned inv checks
    override_auth(test_incident["inv"], UserRole.INVESTIGATOR)
    res = client.get(f"/incidents/{test_incident['incident']['id']}/actions")
    assert res.status_code == 200

    # unassigned inv checks -> 404
    override_auth(test_incident["other_inv"], UserRole.INVESTIGATOR)
    res = client.get(f"/incidents/{test_incident['incident']['id']}/actions")
    assert res.status_code == 404

    # other admin checks -> 404
    override_auth(test_incident["other_admin"], UserRole.ADMIN)
    res = client.get(f"/incidents/{test_incident['incident']['id']}/actions")
    assert res.status_code == 404
    app.dependency_overrides.pop(get_current_user, None)

def test_closure_action_lifecycle(client, test_incident):
    # unresolved incident + admin -> 400
    override_auth(test_incident["admin"], UserRole.ADMIN)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CLOSURE.value,
        "action_type": "Final Review",
        "description": "Attempting closure"
    })
    assert res.status_code == 400

    # resolve incident
    client.patch(f"/incidents/{test_incident['incident']['id']}/status", json={"status": "resolved"})

    # resolved incident + investigator -> 403
    override_auth(test_incident["inv"], UserRole.INVESTIGATOR)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CLOSURE.value,
        "action_type": "Final Review",
        "description": "Attempting closure"
    })
    assert res.status_code == 403

    # resolved incident + admin -> allowed
    override_auth(test_incident["admin"], UserRole.ADMIN)
    res = client.post(f"/incidents/{test_incident['incident']['id']}/actions", json={
        "phase": IncidentActionPhase.CLOSURE.value,
        "action_type": "Final Review",
        "description": "Closure approved"
    })
    assert res.status_code == 200
    app.dependency_overrides.pop(get_current_user, None)
