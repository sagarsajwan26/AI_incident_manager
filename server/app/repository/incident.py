from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident import Incident


class IncidentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, incident: Incident) -> Incident:
        self.db.add(incident)

        await self.db.flush()
        await self.db.refresh(incident)
        return incident

    async def get_by_id(
        self,
        incident_id: int,
        tenant_id: int,
    ) -> Incident | None:
        result = await self.db.execute(
            select(Incident).where(
                Incident.id == incident_id, Incident.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        tenant_id: int,
    ) -> list[Incident]:
        result = await self.db.execute(
            select(Incident)
            .where(Incident.tenant_id == tenant_id)
            .order_by(Incident.created_at.desc())
        )
        return list(result.scalars().all())
