from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident_evidence import IncidentEvidence
from app.models.user import User, UserRole
from app.repository.incident import IncidentRepository
from app.repository.incident_audit import IncidentAuditRepository
from app.repository.incident_evidence import IncidentEvidenceRepository


class EvidenceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.incident_repository = IncidentRepository(db)
        self.evidence_repository = IncidentEvidenceRepository(db)
        self.audit_repository = IncidentAuditRepository(db)

    async def create_evidence(
        self,
        incident_id: int,
        tenant_id: int,
        added_by: int,
        source: str,
        external_id: str | None,
        evidence_type: str,
        content: str,
    ) -> IncidentEvidence:
        incident = await self.incident_repository.get_by_id_and_tenant(
            incident_id=incident_id, tenant_id=tenant_id
        )

        if incident is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="incident not found"
            )
        if external_id is not None:
            existing = await self.evidence_repository.get_by_external_id(
                incident_id=incident_id,
                tenant_id=tenant_id,
                source=source,
                external_id=external_id,
            )
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="evidence already exists",
                )
        evidence = await self.evidence_repository.create(
            incident_id=incident_id,
            tenant_id=tenant_id,
            added_by=added_by,
            source=source,
            external_id=external_id,
            evidence_type=evidence_type,
            content=content,
        )

        await self.audit_repository.create(
            tenant_id=tenant_id,
            incident_id=incident_id,
            performed_by=added_by,
            action="EVIDENCE_ADDED",
            old_value=None,
            new_value=evidence_type,
        )
        await self.db.commit()
        return evidence
