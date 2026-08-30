from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.incident_audit import IncidentAuditLog
from app.database.session import get_db
from fastapi import Depends


class IncidentAuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: int,
        incident_id: int,
        performed_by: int,
        action: str,
        old_value: str | None,
        new_value: str | None,
    ) -> IncidentAuditLog:
        audit_log = IncidentAuditLog(
            tenant_id=tenant_id,
            incident_id=incident_id,
            performed_by=performed_by,
            action=action,
            old_value=old_value,
            new_value=new_value,
        )
        self.db.add(audit_log)
        await self.db.flush()
        await self.db.refresh(audit_log)
        return audit_log

    async def get_by_incident(
        self,
        incident_id: int,
        tenant_id: int,
    ) -> list[IncidentAuditLog]:
        result = await self.db.execute(
            select(IncidentAuditLog)
            .where(
                IncidentAuditLog.incident_id == incident_id,
                IncidentAuditLog.tenant_id == tenant_id,
            )
            .order_by(IncidentAuditLog.created_at.asc())
        )
        return list(result.scalars().all())
