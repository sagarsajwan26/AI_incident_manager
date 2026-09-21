from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_resource import IncidentResource


class IncidentResourceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, resource: IncidentResource) -> IncidentResource:
        self.db.add(resource)
        await self.db.flush()
        await self.db.refresh(resource)
        return resource

    async def get_by_incident(
        self,
        incident_id: int,
        tenant_id: int,
    ) -> list[IncidentResource]:
        result = await self.db.execute(
            select(IncidentResource)
            .where(
                IncidentResource.incident_id == incident_id,
                IncidentResource.tenant_id == tenant_id,
            )
            .order_by(IncidentResource.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(
        self,
        resource_id: int,
        incident_id: int,
        tenant_id: int,
    ) -> IncidentResource | None:
        result = await self.db.execute(
            select(IncidentResource).where(
                IncidentResource.id == resource_id,
                IncidentResource.incident_id == incident_id,
                IncidentResource.tenant_id == tenant_id,
            )
        )

        return result.scalar_one_or_none()
