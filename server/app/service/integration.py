from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.integration_repository import IntegrationRepository
from app.models.integration import Integration
from app.exception.integration import DuplicateIntegrationError
from app.service.integration_test_service import IntegrationTestservice


class IntegrationService:
    def __init__(self, db: AsyncSession):
        self.repository = IntegrationRepository(db)

    async def create_integration(
        self, tenant_id: int, provider: str, credentials: dict, is_active: bool = True
    ) -> Integration:
        existing = await self.repository.get_by_provider_and_tenant(
            provider=provider, tenant_id=tenant_id
        )

        if existing is not None:
            raise DuplicateIntegrationError(
                f"Integration for provider '{provider}' already exists."
            )

        token = credentials.get("token")

        if not token:
            raise ValueError("Integration token is required")

        tester = IntegrationTestservice()

        await tester.test(provider=provider, token=token)

        return await self.repository.create(
            tenant_id=tenant_id,
            provider=provider,
            credentials=credentials,
            is_active=is_active,
        )

    async def get_integration(
        self,
        integration_id: int,
        tenant_id: int,
    ) -> Integration | None:
        return await self.repository.get_by_id_and_tenant(
            integration_id=integration_id, tenant_id=tenant_id
        )

    async def list_integrations(
        self,
        tenant_id: int,
    ) -> list[Integration]:
        return await self.repository.list_by_tenant(tenant_id=tenant_id)

    async def update_integration(
        self,
        integration_id: int,
        tenant_id: int,
        credentials: dict | None = None,
        is_active: bool | None = None,
    ) -> Integration | None:
        return await self.repository.update(
            integration_id=integration_id,
            tenant_id=tenant_id,
            credentials=credentials,
            is_active=is_active,
        )

    async def delete_integration(
        self,
        integration_id: int,
        tenant_id: int,
    ) -> bool:
        return await self.repository.delete(
            integration_id=integration_id, tenant_id=tenant_id
        )

    async def get_integration_by_provider(
        self,
        provider: str,
        tenant_id: int,
    ) -> Integration | None:
        return await self.repository.get_by_provider_and_tenant(
            provider=provider, tenant_id=tenant_id
        )

    async def test_integration(
        self, integration_id: int, tenant_id: int
    ) -> Integration:
        integration = await self.repository.get_by_id_and_tenant(
            integration_id=integration_id, tenant_id=tenant_id
        )

        if integration is None:
            raise ValueError("Integration is inactive")

        token = integration.credentials.get("token")
        if not token:
            raise ValueError("integration is missing")

        tester = IntegrationTestservice()
        await tester.test(
            provider=integration.provider,
            token=token,
        )

        return integration
