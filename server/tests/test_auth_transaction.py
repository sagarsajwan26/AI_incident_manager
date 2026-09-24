import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.models.tenant import Tenant
import uuid
import random
import string

@pytest.mark.asyncio
async def test_registration_transaction_rollback_on_user_failure(client: TestClient):
    """
    Test that if user creation fails during registration, the entire transaction is rolled back,
    and no orphaned tenant is left in the database.
    """
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.core.config import settings
    
    engine = create_async_engine(settings.database_url, echo=False)
    Session = async_sessionmaker(bind=engine)
    
    # Generate unique test data
    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    tenant_name = f"RollbackTenant-{suffix}"
    slug = tenant_name.lower().strip().replace(" ", "-")
    email = f"rollback_{suffix}@example.com"
    
    # Mock create_user to raise an Exception
    with patch("app.repository.user.UserRepository.create_user") as mock_create_user:
        mock_create_user.side_effect = Exception("Simulated user creation failure")
        
        # Try to register
        res = client.post("/auth/register", json={
            "email": email,
            "password": "Password123!",
            "name": "Rollback Test User",
            "tenant_name": tenant_name
        })
        
        # Ensure it failed (500 internal server error due to unhandled Exception, 
        # or it could be caught by FastAPI exception handlers)
        assert res.status_code == 500
        
    # Now verify the tenant does NOT exist in the database
    async with Session() as db_session:
        result = await db_session.execute(sa.select(Tenant).where(Tenant.slug == slug))
        tenant = result.scalar_one_or_none()
    
    assert tenant is None, "Tenant was not rolled back after user creation failure!"
