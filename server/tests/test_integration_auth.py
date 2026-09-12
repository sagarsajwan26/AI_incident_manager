import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
import random
import string

def random_letters(n):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

def setup_user_with_role(client: TestClient, role: UserRole):
    suffix = random_letters(6)
    # Register user to ensure tenant exists in DB
    res = client.post("/auth/register", json={
        "email": f"test_{suffix}@example.com",
        "password": "Password123!",
        "name": "Auth Test",
        "tenant_name": f"Tenant_{suffix}"
    })
    user_data = res.json()
    
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
    return user_data

# POST /integration tests

def test_admin_post_integration(client: TestClient):
    setup_user_with_role(client, UserRole.ADMIN)
    res = client.post("/integration", json={"provider": "github", "credentials": {"token": "test"}, "is_active": True})
    assert res.status_code in (201, 200) # Integration is created
    app.dependency_overrides.pop(get_current_user, None)

def test_investigator_post_integration(client: TestClient):
    setup_user_with_role(client, UserRole.INVESTIGATOR)
    res = client.post("/integration", json={"provider": "github", "credentials": {"token": "test"}, "is_active": True})
    assert res.status_code == 403
    assert res.json()["detail"] == "You don't have permission to perform this action"
    app.dependency_overrides.pop(get_current_user, None)

def test_member_post_integration(client: TestClient):
    setup_user_with_role(client, UserRole.MEMBER)
    res = client.post("/integration", json={"provider": "github", "credentials": {"token": "test"}, "is_active": True})
    assert res.status_code == 403
    assert res.json()["detail"] == "You don't have permission to perform this action"
    app.dependency_overrides.pop(get_current_user, None)

def test_unauth_post_integration(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    client.cookies.clear()
    res = client.post("/integration", json={"provider": "github", "credentials": {"token": "test"}, "is_active": True})
    assert res.status_code == 401

# PATCH /integration/{id} tests

def test_admin_patch_integration(client: TestClient):
    setup_user_with_role(client, UserRole.ADMIN)
    res = client.post("/integration", json={"provider": "github", "credentials": {"token": "test"}, "is_active": True})
    assert res.status_code in (201, 200)
    integration_id = res.json()["id"]
    
    patch_res = client.patch(f"/integration/{integration_id}", json={"credentials": {"token": "patched"}, "is_active": False})
    assert patch_res.status_code == 200
    app.dependency_overrides.pop(get_current_user, None)

def test_investigator_patch_integration(client: TestClient):
    setup_user_with_role(client, UserRole.INVESTIGATOR)
    res = client.patch("/integration/1", json={"credentials": {"token": "patched"}, "is_active": False})
    assert res.status_code == 403
    assert res.json()["detail"] == "You don't have permission to perform this action"
    app.dependency_overrides.pop(get_current_user, None)

def test_member_patch_integration(client: TestClient):
    setup_user_with_role(client, UserRole.MEMBER)
    res = client.patch("/integration/1", json={"credentials": {"token": "patched"}, "is_active": False})
    assert res.status_code == 403
    assert res.json()["detail"] == "You don't have permission to perform this action"
    app.dependency_overrides.pop(get_current_user, None)

def test_unauth_patch_integration(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    client.cookies.clear()
    res = client.patch("/integration/1", json={"credentials": {"token": "patched"}, "is_active": False})
    assert res.status_code == 401

# DELETE /integration/{id} tests

def test_admin_delete_integration(client: TestClient):
    setup_user_with_role(client, UserRole.ADMIN)
    res = client.post("/integration", json={"provider": "github", "credentials": {"token": "test"}, "is_active": True})
    assert res.status_code in (201, 200)
    integration_id = res.json()["id"]

    del_res = client.delete(f"/integration/{integration_id}")
    assert del_res.status_code == 204
    app.dependency_overrides.pop(get_current_user, None)

def test_investigator_delete_integration(client: TestClient):
    setup_user_with_role(client, UserRole.INVESTIGATOR)
    res = client.delete("/integration/1")
    assert res.status_code == 403
    assert res.json()["detail"] == "You don't have permission to perform this action"
    app.dependency_overrides.pop(get_current_user, None)

def test_member_delete_integration(client: TestClient):
    setup_user_with_role(client, UserRole.MEMBER)
    res = client.delete("/integration/1")
    assert res.status_code == 403
    assert res.json()["detail"] == "You don't have permission to perform this action"
    app.dependency_overrides.pop(get_current_user, None)

def test_unauth_delete_integration(client: TestClient):
    app.dependency_overrides.pop(get_current_user, None)
    client.cookies.clear()
    res = client.delete("/integration/1")
    assert res.status_code == 401
