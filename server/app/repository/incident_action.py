from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident_action import IncidentAction


class IncidentActionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        action: IncidentAction,
    ) -> IncidentAction:
        self.db.add(action)
        await self.db.flush()
        await self.db.refresh(action)
        return action

    async def get_by_incident(
        self, incident_id: int, tenant_id: int
    ) -> list[IncidentAction]:
        result = await self.db.execute(
            select(IncidentAction)
            .where(
                IncidentAction.incident_id == incident_id,
                IncidentAction.tenant_id == tenant_id,
            )
            .order_by(IncidentAction.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(
        self,
        action_id: int,
        tenant_id: int,
        incident_id: int,
    ) -> IncidentAction | None:
        result = await self.db.execute(
            select(IncidentAction).where(
                IncidentAction.id == action_id,
                IncidentAction.incident_id == incident_id,
                IncidentAction.tenant_id == tenant_id,
            )
        )

        return result.scalar_one_or_none()
