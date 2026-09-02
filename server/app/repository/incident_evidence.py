from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident_evidence import IncidentEvidence


class IncidentEvidenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        incident_id: int,
        tenant_id: int,
        added_by: int,
        source: str,
        external_id: str | None,
        evidence_type: str,
        content: str,
    ) -> IncidentEvidence:
        evidence = IncidentEvidence(
            incident_id=incident_id,
            tenant_id=tenant_id,
            added_by=added_by,
            evidence_type=evidence_type,
            content=content,
            source=source,
            external_id=external_id,
        )
        self.db.add(evidence)
        await self.db.flush()
        await self.db.refresh(evidence)
        return evidence

    async def get_by_incident(
        self,
        incident_id: int,
        tenant_id: int,
    ) -> list[IncidentEvidence]:
        result = await self.db.execute(
            select(IncidentEvidence)
            .where(
                IncidentEvidence.incident_id == incident_id,
                IncidentEvidence.tenant_id == tenant_id,
            )
            .order_by(IncidentEvidence.created_at.asc())
        )

        return list(result.scalars().all())

    async def get_by_external_id(
        self,
        incident_id: int,
        tenant_id: int,
        source: str,
        external_id: str,
    ) -> IncidentEvidence | None:
        result = await self.db.execute(
            select(IncidentEvidence).where(
                IncidentEvidence.incident_id == incident_id,
                IncidentEvidence.tenant_id == tenant_id,
                IncidentEvidence.source == source,
                IncidentEvidence.external_id == external_id,
            )
        )

        return result.scalar_one_or_none()
