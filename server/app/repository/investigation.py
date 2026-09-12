from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investigation import Investigation
from app.models.user import User


class InvestigationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: int,
        incident_id: int,
        triggered_by: int,
        provider: str,
        model: str,
        prompt: str,
        result: dict,
        confidence: float,
    ) -> Investigation:

        investigation = Investigation(
            tenant_id=tenant_id,
            incident_id=incident_id,
            triggered_by=triggered_by,
            provider=provider,
            model=model,
            prompt=prompt,
            result=result,
            confidence=confidence,
        )
        self.db.add(investigation)
        await self.db.flush()
        await self.db.refresh(investigation)
        return investigation

    async def get_by_incident(
        self,
        incident_id: int,
        tenant_id: int,
    ) -> list[Investigation]:

        result = await self.db.execute(
            select(Investigation)
            .where(
                Investigation.incident_id == incident_id,
                Investigation.tenant_id == tenant_id,
            )
            .order_by(Investigation.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_id_and_incident(
        self,
        investigation_id: int,
        incident_id: int,
        tenant_id: int,
    ) -> Investigation | None:

        result = await self.db.execute(
            select(Investigation).where(
                Investigation.id == investigation_id,
                Investigation.incident_id == incident_id,
                Investigation.tenant_id == tenant_id,
            )
        )
        return result.scalars().first()
