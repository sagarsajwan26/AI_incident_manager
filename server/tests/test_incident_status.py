import pytest
from app.models.incident import IncidentStatus
import random
import string

def random_letters(n):
    return ''.join(random.choices(string.ascii_letters, k=n))

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
def test_incident(client, auth_setup):
    res = client.post(
        "/incidents/",
        json={
            "title": "Status transition test incident",
            "description": "testing status",
            "severity": "low"
        }
    )
    return res.json()

def test_valid_status_transitions(client, auth_setup, test_incident):
    incident_id = test_incident["id"]
    
    valid_transitions = [
        (IncidentStatus.OPEN, IncidentStatus.INVESTIGATING),
        (IncidentStatus.OPEN, IncidentStatus.RESOLVED),
        (IncidentStatus.INVESTIGATING, IncidentStatus.CONTAINED),
        (IncidentStatus.INVESTIGATING, IncidentStatus.RESOLVED),
        (IncidentStatus.CONTAINED, IncidentStatus.INVESTIGATING),
        (IncidentStatus.CONTAINED, IncidentStatus.RESOLVED),
        (IncidentStatus.RESOLVED, IncidentStatus.INVESTIGATING),
        (IncidentStatus.RESOLVED, IncidentStatus.CLOSED),
    ]
    
    for from_status, to_status in valid_transitions:
        # Reset to from_status first (we do this by bypassing the API if needed, 
        # or we just use a new incident each time, but since it's a test, let's just 
        # create a new incident for each transition to be safe, or just use the DB).
        # Actually, let's just use the API to create a new incident for each test
        res = client.post("/incidents/", json={"title": "Test", "description": "testing status", "severity": "low"})
        inc_id = res.json()["id"]
        
        # We need a way to set the from_status without rules applying.
        # But wait, we can just transition it legally to `from_status`!
        if from_status == IncidentStatus.INVESTIGATING:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.INVESTIGATING})
        elif from_status == IncidentStatus.CONTAINED:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.INVESTIGATING})
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.CONTAINED})
        elif from_status == IncidentStatus.RESOLVED:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.RESOLVED})
        elif from_status == IncidentStatus.CLOSED:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.RESOLVED})
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.CLOSED})
            
        res = client.patch(f"/incidents/{inc_id}/status", json={"status": to_status})
        assert res.status_code == 200, f"Failed valid transition {from_status} -> {to_status}: {res.text}"


def test_invalid_status_transitions(client, auth_setup):
    invalid_transitions = [
        (IncidentStatus.OPEN, IncidentStatus.CONTAINED),
        (IncidentStatus.OPEN, IncidentStatus.CLOSED),
        (IncidentStatus.INVESTIGATING, IncidentStatus.OPEN),
        (IncidentStatus.INVESTIGATING, IncidentStatus.CLOSED),
        (IncidentStatus.CONTAINED, IncidentStatus.OPEN),
        (IncidentStatus.CONTAINED, IncidentStatus.CLOSED),
        (IncidentStatus.RESOLVED, IncidentStatus.CONTAINED),
        (IncidentStatus.CLOSED, IncidentStatus.OPEN),
        (IncidentStatus.CLOSED, IncidentStatus.INVESTIGATING),
        (IncidentStatus.CLOSED, IncidentStatus.CONTAINED),
        (IncidentStatus.CLOSED, IncidentStatus.RESOLVED),
    ]
    
    for from_status, to_status in invalid_transitions:
        res = client.post("/incidents/", json={"title": "Test", "description": "testing status", "severity": "low"})
        inc_id = res.json()["id"]
        
        if from_status == IncidentStatus.INVESTIGATING:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.INVESTIGATING})
        elif from_status == IncidentStatus.CONTAINED:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.INVESTIGATING})
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.CONTAINED})
        elif from_status == IncidentStatus.RESOLVED:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.RESOLVED})
        elif from_status == IncidentStatus.CLOSED:
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.RESOLVED})
            client.patch(f"/incidents/{inc_id}/status", json={"status": IncidentStatus.CLOSED})
            
        res = client.patch(f"/incidents/{inc_id}/status", json={"status": to_status})
        assert res.status_code == 400, f"Expected 400 for invalid transition {from_status} -> {to_status}, got {res.status_code}"

def test_available_transitions(client, auth_setup):
    res = client.post("/incidents/", json={"title": "Test Transitions", "description": "testing available_transitions", "severity": "low"})
    incident = res.json()
    assert "available_transitions" in incident
    # An open incident should have investigating and resolved available
    assert set(incident["available_transitions"]) == {"investigating", "resolved"}

    inc_id = incident["id"]
    client.patch(f"/incidents/{inc_id}/status", json={"status": "investigating"})
    res = client.get(f"/incidents/{inc_id}")
    incident = res.json()
    assert set(incident["available_transitions"]) == {"contained", "resolved"}

