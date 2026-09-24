from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.incident_automation_job import (
    IncidentAutomationJob,
    AutomationJobStatus,
)


class IncidentAutomationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant_id: int, incident_id: int) -> IncidentAutomationJob:
        job = IncidentAutomationJob(
            tenant_id=tenant_id,
            incident_id=incident_id,
            status=AutomationJobStatus.PENDING,
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_by_incident(
        self, tenant_id: int, incident_id: int
    ) -> IncidentAutomationJob | None:
        result = await self.db.execute(
            select(IncidentAutomationJob)
            .where(
                IncidentAutomationJob.tenant_id == tenant_id,
                IncidentAutomationJob.incident_id == incident_id,
            )
            .order_by(IncidentAutomationJob.created_at.desc())
        )
        return result.scalars().first()

    async def get_active_job_for_incident(
        self, tenant_id: int, incident_id: int
    ) -> IncidentAutomationJob | None:
        result = await self.db.execute(
            select(IncidentAutomationJob).where(
                IncidentAutomationJob.tenant_id == tenant_id,
                IncidentAutomationJob.incident_id == incident_id,
                IncidentAutomationJob.status.in_(
                    [AutomationJobStatus.PENDING, AutomationJobStatus.RUNNING]
                ),
            )
        )
        return result.scalars().first()

    async def save(self, job: IncidentAutomationJob) -> None:
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)

    async def update(
        self,
        job: IncidentAutomationJob,
        status: AutomationJobStatus,
        error_message: str | None = None,
    ) -> IncidentAutomationJob:
        job.status = status
        job.error_message = error_message
        self.db.add(job)

        await self.db.flush()
        await self.db.refresh(job)
        return job
