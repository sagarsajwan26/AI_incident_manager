from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import Integration


class IntegrationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id,
        provider,
        credentials,
        is_active,
    ) -> Integration:
        integration = Integration(
            tenant_id=tenant_id,
            provider=provider,
            credentials=credentials,
            is_active=is_active,
        )

        self.db.add(integration)
        
        try:
            await self.db.commit()
            await self.db.refresh(integration)
        except IntegrityError:
            await self.db.rollback()
            raise

        return integration

    async def get_by_id_and_tenant(
        self, integration_id: int, tenant_id: int
    ) -> Integration | None:

        result = await self.db.execute(
            select(Integration).where(
                Integration.tenant_id == tenant_id,
                Integration.id == integration_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_provider_and_tenant(
        self,
        provider: str,
        tenant_id: int,
    ) -> Integration | None:

        result = await self.db.execute(
            select(Integration).where(
                Integration.provider == provider, Integration.tenant_id == tenant_id
            )
        )

        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: int,
    ) -> list[Integration]:
        result = await self.db.execute(
            select(Integration).where(Integration.tenant_id == tenant_id)
        )

        return list(result.scalars().all())

    async def update(
        self,
        integration_id: int,
        tenant_id: int,
        credentials: dict | None = None,
        is_active: bool | None = None,
    ) -> Integration | None:

        integration = await self.get_by_id_and_tenant(
            integration_id=integration_id, tenant_id=tenant_id
        )

        if integration is None:
            return None

        if credentials is not None:
            integration.credentials = credentials

        if is_active is not None:
            integration.is_active = is_active

        await self.db.commit()
        await self.db.refresh(integration)

        return integration

    async def delete(
        self,
        integration_id: int,
        tenant_id: int,
    ) -> bool:

        integration = await self.get_by_id_and_tenant(
            integration_id=integration_id, tenant_id=tenant_id
        )

        if integration is None:
            return False

        await self.db.delete(integration)
        await self.db.commit()

        return True
