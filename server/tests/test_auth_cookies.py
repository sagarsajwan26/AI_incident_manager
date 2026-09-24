import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def test_login_cookie_attributes_development(client: TestClient):
    settings.environment = "development"
    
    # Register a user
    import random, string
    suffix = "".join(random.choices(string.ascii_lowercase, k=6))
    email = f"user_{suffix}@example.com"
    password = "Password123!"
    tenant_name = f"Tenant{suffix}"
    
    res = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "name": "Cookie Dev User",
        "tenant_name": tenant_name
    })
    assert res.status_code == 200
    
    # Login
    res = client.post("/auth/login", json={
        "tenant_name": tenant_name,
        "email": email,
        "password": password
    })
    assert res.status_code == 200
    
    # Check cookie headers directly to verify attributes
    set_cookie_headers = res.headers.get_list("set-cookie")
    assert len(set_cookie_headers) > 0
    cookie_str = set_cookie_headers[0].lower()
    
    assert "access_token=" in cookie_str
    assert "httponly" in cookie_str
    assert "samesite=lax" in cookie_str
    assert "secure" not in cookie_str.split(";")  # It might be part of another word, but separated by ;

def test_login_cookie_attributes_production(client: TestClient):
    settings.environment = "production"
    try:
        # Register a user
        import random, string
        suffix = "".join(random.choices(string.ascii_lowercase, k=6))
        email = f"user_{suffix}@example.com"
        password = "Password123!"
        tenant_name = f"Tenant{suffix}"
        
        res = client.post("/auth/register", json={
            "email": email,
            "password": password,
            "name": "Cookie Prod User",
            "tenant_name": tenant_name
        })
        assert res.status_code == 200
        
        # Login
        res = client.post("/auth/login", json={
            "tenant_name": tenant_name,
            "email": email,
            "password": password
        })
        assert res.status_code == 200
        
        # Check cookie headers directly to verify attributes
        set_cookie_headers = res.headers.get_list("set-cookie")
        assert len(set_cookie_headers) > 0
        cookie_parts = [p.strip().lower() for p in set_cookie_headers[0].split(";")]
        
        assert "httponly" in cookie_parts
        assert any("samesite=lax" in p for p in cookie_parts)
        assert "secure" in cookie_parts
    finally:
        # Clean up state just in case
        settings.environment = "development"
