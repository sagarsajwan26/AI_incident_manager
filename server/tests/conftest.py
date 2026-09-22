import asyncio
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.database.session import get_db
from app.core.config import settings


if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )


@pytest.fixture(scope="session")
def client():
    """
    Shared TestClient for the entire test session.

    Tests use a dedicated database engine/session factory so the
    production database engine is not reused by the test lifecycle.
    """

    test_engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )

    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    from unittest.mock import patch
    with patch("app.service.integration.IntegrationTestservice.test") as mock_test:
        mock_test.return_value = None
        with TestClient(
            app,
            base_url="http://testserver/api/v1",
            raise_server_exceptions=False,
        ) as test_client:
            yield test_client

    app.dependency_overrides.clear()
