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
        return self.response

def valid_ai_response(confidence=0.5):
    return {
        "summary": "API Test summary.",
        "likely_root_cause": "API Test root cause.",
        "root_cause_status": "probable",
        "evidence": ["Some evidence"],
        "evidence_assessment": [
            {
                "claim": "Some claim",
                "support": "Some support",
                "support_level": "inferred",
                "supports_root_cause": True
            }
        ],
        "impact": "API Test impact.",
        "recommended_actions": ["API Test action."],
        "unknowns": ["API Test unknown."],
        "confidence": confidence,
    }

def random_letters(n=8):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))



@pytest.fixture(scope="module")
def auth_setup(client):
    suffix = random_letters(6)
    email = f"hist_{suffix}@example.com".lower()
    password = "Password123!"
    
    # Register
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "name": "History User",
        "tenant_name": f"HistTenant{suffix}"
    })
    assert res.status_code == 200, res.text
    
    # Login to set cookie
    res = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert res.status_code == 200, res.text
    return {"email": email, "password": password}

@pytest.fixture(scope="module")
def test_incident_id(client, auth_setup):
    response = client.post(
        "/incidents/",
        json={
            "title": "History Test Incident",
            "description": "Created for history tests",
            "severity": "high"
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]

def test_multiple_investigations_are_persisted(client, test_incident_id):
    # Trigger 3 investigations with different fake responses to simulate history
    confidences = [0.40, 0.49, 0.72]
    
    for conf in confidences:
        fake_provider = FakeLLMProvider(json.dumps(valid_ai_response(confidence=conf)))
        with patch("app.routes.api.v1.incident.OllamaProvider", return_value=fake_provider):
            res = client.post(f"/incidents/{test_incident_id}/investigate")
            assert res.status_code == 200
            
    # Fetch history
    history_resp = client.get(f"/incidents/{test_incident_id}/investigations")
    assert history_resp.status_code == 200
    
    history = history_resp.json()
    
    # Verify the timeline order (the query returns them ordered by created_at DESC)
    # The last executed (0.72) should be first, then 0.49, then 0.40
    assert len(history) == 3
    assert history[0]["result"]["confidence"] == 0.72
    assert history[1]["result"]["confidence"] == 0.49
    assert history[2]["result"]["confidence"] == 0.40


def test_get_specific_investigation(client, test_incident_id):
    history_resp = client.get(f"/incidents/{test_incident_id}/investigations")
    assert history_resp.status_code == 200
    history = history_resp.json()
    
    assert len(history) > 0
    target_inv = history[0]
    inv_id = target_inv["id"]
    
    # Fetch specifically
    specific_resp = client.get(f"/incidents/{test_incident_id}/investigations/{inv_id}")
    assert specific_resp.status_code == 200
    
    specific_inv = specific_resp.json()
    assert specific_inv["id"] == inv_id
    assert specific_inv["confidence"] == target_inv["confidence"]
    assert specific_inv["result"] == target_inv["result"]

def test_get_nonexistent_investigation(client, test_incident_id):
    res = client.get(f"/incidents/{test_incident_id}/investigations/999999")
    assert res.status_code == 404
