from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import asyncio

from app.core.logger import get_logger
from app.models.incident_automation_job import IncidentAutomationJob
from app.repository.incident_automation_job import IncidentAutomationRepository
from app.service.incident import IncidentService
from app.repository.incident_audit import IncidentAuditRepository
from app.repository.integration_repository import IntegrationRepository
from app.models.user import User

logger = get_logger(__name__)


class IncidentAutomationService:
    def __init__(
        self,
        db: AsyncSession,
        incident_service: IncidentService,
    ):
        self.db = db
        self.repository = IncidentAutomationRepository(db)
        self.incident_service = incident_service
        self.audit_repository = IncidentAuditRepository(db)
        self.integration_repository = IntegrationRepository(db)

    async def start_incident_automation(
        self, tenant_id: int, incident_id: int, current_user: User, background_tasks
    ) -> IncidentAutomationJob:
        active_job = await self.repository.get_active_job_for_incident(
            tenant_id, incident_id
        )
        if active_job:
            return active_job

        job = await self.repository.create(tenant_id, incident_id)

        await self.audit_repository.create(
            tenant_id=tenant_id,
            incident_id=incident_id,
            performed_by=current_user.id,
            action="AUTOMATION_STARTED",
            old_value=None,
            new_value=str(job.id),
        )
        await self.db.commit()

        # Enqueue the actual background run
        # Note: in a real celery/redis worker we would pass just IDs.
        # Here we pass the IDs and rely on the background task to get a new DB session.
        background_tasks.add_task(
            self._background_runner, job.id, tenant_id, incident_id, current_user.id
        )

        return job

    async def _background_runner(
        self, job_id: int, tenant_id: int, incident_id: int, user_id: int
    ):
        from app.database.session import async_sessionmaker_factory
        from app.repository.incident_automation_job import IncidentAutomationRepository
        from app.repository.incident import IncidentRepository

        # We need a new session for the background task
        async with async_sessionmaker_factory() as session:
            try:
                pass
            except Exception as e:
                logger.error(f"Automation failed for job {job_id}: {str(e)}")
