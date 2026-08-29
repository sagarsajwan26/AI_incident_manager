from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentSeverity
from app.repository.incident import IncidentRepository


class IncidentService:
    def __init__(self, db: AsyncSession):
        self.repository = IncidentRepository(db)

    async def create_incident(
        self,
        tenant_id: int,
        reported_by: int,
        title: str,
        description: str,
        severity: IncidentSeverity,
    ) -> Incident:
        incident = Incident(
            tenant_id=tenant_id,
            reported_by=reported_by,
            title=title,
            description=description,
            severity=severity,
        )

        return await self.repository.create(incident)

    async def get_incident(self, incident_id: int, tenant_id: int) -> Incident:
        incident = await self.repository.get_by_id(
            incident_id=incident_id, tenant_id=tenant_id
        )

        if incident is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )
        return incident

    async def get_all_incident(
        self,
        tenant_id: int,
    ) -> list[Incident]:
        return await self.repository.get_all(tenant_id=tenant_id)
