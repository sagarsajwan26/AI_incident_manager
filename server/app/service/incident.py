from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.repository.incident import IncidentRepository
from app.repository.user import UserRepository
from app.models.user import UserRole, User
from app.repository.incident_audit import IncidentAuditRepository
from app.models.incident_audit import IncidentAuditLog
from app.repository.incident_comment import IncidentCommentRepository
from app.models.incident_comment import IncidentComment
from app.models.incident_evidence import IncidentEvidence
from app.repository.incident_evidence import IncidentEvidenceRepository
from app.schemas.investigation import InvestigationContext
from app.models.investigation import Investigation
from app.repository.investigation import InvestigationRepository
from app.schemas.ai_investigation import InvestigationResult, InvestigationResponse
from app.core.config import settings
from app.service.ai_investigation import AIInvestigatorService
from app.integration.github.client import GithubClient
from app.integration.github.provider import GithubProvider

ALLOWED_STATUS_TRANSITIONS = {
    IncidentStatus.OPEN: {
        IncidentStatus.INVESTIGATING,
    },
    IncidentStatus.INVESTIGATING: {
        IncidentStatus.CONTAINED,
    },
    IncidentStatus.CONTAINED: {IncidentStatus.RESOLVED},
    IncidentStatus.RESOLVED: {IncidentStatus.CLOSED},
    IncidentStatus.CLOSED: set(),
}


class IncidentService:
    def __init__(
        self, db: AsyncSession, ai_service: AIInvestigatorService | None = None
    ):
        self.db = db
        self.ai_service = ai_service
        self.incident_repository = IncidentRepository(db)
        self.user_repository = UserRepository(db)
        self.audit_repository = IncidentAuditRepository(db)
        self.comment_repository = IncidentCommentRepository(db)
        self.evidence_repository = IncidentEvidenceRepository(db)
        self.investigation_repository = InvestigationRepository(db)

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
        incident = await self.incident_repository.create(incident)
        await self.audit_repository.create(
            tenant_id=tenant_id,
            incident_id=incident.id,
            performed_by=reported_by,
            action="CREATED",
            old_value=None,
            new_value=None,
        )
        await self.db.commit()
        return incident

    async def get_incident(self, incident_id: int, current_user: User) -> Incident:
        if current_user.role == UserRole.INVESTIGATOR:
            incident = await self.incident_repository.get_by_id_and_assignee(
                incident_id=incident_id,
                tenant_id=current_user.tenant_id,
                assigned_to=current_user.id,
            )
        else:
            incident = await self.incident_repository.get_by_id_and_tenant(
                incident_id=incident_id, tenant_id=current_user.tenant_id
            )

        if incident is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )
        return incident

    async def get_all_incident(
        self,
        current_user: User,
    ) -> list[Incident]:

        if current_user.role == UserRole.INVESTIGATOR:
            return await self.incident_repository.get_all_by_assignee(
                tenant_id=current_user.tenant_id, assigned_to=current_user.id
            )
        return await self.incident_repository.get_all(tenant_id=current_user.tenant_id)

    async def assign_incident(
        self, incident_id: int, investigator_id: int, tenant_id: int, current_user: User
    ) -> Incident:
        incident = await self.incident_repository.get_by_id_and_tenant(
            incident_id=incident_id, tenant_id=tenant_id
        )
        if incident is None:
            raise HTTPException(status_code=404, detail="incident not found")

        investigator = await self.user_repository.get_by_id_and_tenant(
            user_id=investigator_id, tenant_id=tenant_id
        )
        if investigator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="investigator not found"
            )
        if investigator.role != UserRole.INVESTIGATOR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not an investigator",
            )
        if incident.assigned_to == investigator.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incident is already assigned to this investigator",
            )
        old_assigned_to = incident.assigned_to
        incident.assigned_to = investigator.id
        await self.incident_repository.save(incident)
        await self.audit_repository.create(
            tenant_id=tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="ASSIGNED",
            old_value=(str(old_assigned_to) if old_assigned_to is not None else None),
            new_value=str(investigator.id),
        )
        await self.db.commit()
        return incident

    async def update_status(
        self,
        incident_id: int,
        new_status: IncidentStatus,
        tenant_id: int,
        current_user: User,
    ) -> Incident:
        incident = await self.incident_repository.get_by_id_and_tenant(
            incident_id=incident_id, tenant_id=tenant_id
        )

        if incident is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="incident not found"
            )
        if current_user.role == UserRole.INVESTIGATOR:

            if incident.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="you can only update incidents assigned to you",
                )
            if new_status == IncidentStatus.CLOSED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="only admin can close incidents",
                )

        allowed_statuses = ALLOWED_STATUS_TRANSITIONS[incident.status]
        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid status transition: "
                    f"{incident.status.value} -> {new_status.value}"
                ),
            )

        old_status = incident.status
        incident.status = new_status

        await self.incident_repository.save(incident)
        await self.audit_repository.create(
            tenant_id=tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="STATUS_CHANGED",
            old_value=old_status.value,
            new_value=new_status.value,
        )

        await self.db.commit()

        return incident

    async def get_audit_history(
        self,
        incident_id: int,
        current_user: User,
    ) -> list[IncidentAuditLog]:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        return await self.audit_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )

    async def create_comment(
        self,
        incident_id: int,
        content: str,
        current_user: User,
    ) -> IncidentComment:
        incident = await self.get_incident(
            incident_id=incident_id,
            current_user=current_user,
        )
        if current_user.role not in (UserRole.ADMIN, UserRole.INVESTIGATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you dont have permission to create comments",
            )
        comment = await self.comment_repository.create(
            incident_id=incident.id,
            tenant_id=current_user.tenant_id,
            author_id=current_user.id,
            content=content,
        )

        await self.audit_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="COMMENT_ADDED",
            old_value=None,
            new_value=content,
        )

        await self.db.commit()
        return comment

    async def get_comments(
        self,
        incident_id: int,
        current_user: User,
    ) -> list[IncidentComment]:
        incident = await self.get_incident(
            incident_id=incident_id,
            current_user=current_user,
        )
        return await self.comment_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )

    async def update_comment(
        self, incident_id: int, comment_id: int, content: str, current_user: User
    ) -> IncidentComment:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        comment = await self.comment_repository.get_by_id(
            comment_id=comment_id,
            incident_id=incident.id,
            tenant_id=current_user.tenant_id,
        )

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
            )
        if current_user.role == UserRole.INVESTIGATOR:
            if comment.author_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only edit your own comment",
                )
        old_content = comment.content

        comment.content = content
        await self.audit_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="COMMENT_UPDATED",
            old_value=old_content,
            new_value=content,
        )

        await self.db.commit()

        return comment

    async def delete_comment(
        self, incident_id: int, comment_id: int, current_user: User
    ) -> None:
        incident = await self.get_incident(
            incident_id=incident_id,
            current_user=current_user,
        )
        comment = await self.comment_repository.get_by_id(
            comment_id=comment_id,
            incident_id=incident.id,
            tenant_id=current_user.tenant_id,
        )

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        if current_user.role == UserRole.INVESTIGATOR:
            if comment.author_id != current_user.id:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="you can only delete your own comments",
                )
        deleted_content = comment.content

        await self.db.delete(comment)

        await self.audit_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="COMMENT_DELETED",
            old_value=deleted_content,
            new_value=None,
        )
        await self.db.commit()

    async def create_evidence(
        self,
        incident_id: int,
        evidence_type: str,
        content: str,
        current_user: User,
    ) -> IncidentEvidence:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )

        if current_user.role not in (UserRole.ADMIN, UserRole.INVESTIGATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you dont have permission to add evidence",
            )
        evidence = await self.evidence_repository.create(
            incident_id=incident.id,
            tenant_id=current_user.tenant_id,
            added_by=current_user.id,
            evidence_type=evidence_type,
            content=content,
            source="manual",
            external_id=None,
        )

        await self.audit_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="EVIDENCE_ADDED",
            old_value=None,
            new_value=evidence_type,
        )

        await self.db.commit()

        return evidence

    async def get_evidence(
        self, incident_id: int, current_user: User
    ) -> list[IncidentEvidence]:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        return await self.evidence_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )

    async def get_investigation_context(
        self,
        incident_id: int,
        current_user: User,
    ) -> InvestigationContext:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        comments = await self.comment_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )
        evidence = await self.evidence_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )
        audit_history = await self.audit_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )

        return InvestigationContext(
            incident=incident,
            comments=comments,
            evidence=evidence,
            audit_history=audit_history,
        )

    async def investigate_incident(
        self,
        incident_id: int,
        current_user: User,
    ) -> InvestigationResult:

        context = await self.get_investigation_context(
            incident_id=incident_id,
            current_user=current_user,
        )

        if self.ai_service is None:
            raise RuntimeError("Ai investigation service is not configured")

        output = await self.ai_service.investigate(context)

        await self.investigation_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident_id,
            triggered_by=current_user.id,
            provider="ollama",
            model=settings.ollama_model,
            prompt=output.prompt,
            result=output.result.model_dump(mode="json"),
            confidence=output.result.confidence,
        )

        await self.db.commit()

        return output.result

    async def get_investigation_history(
        self, incident_id: int, current_user: User
    ) -> list[InvestigationResponse]:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        return await self.investigation_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )

    async def collect_github_evidence(
        self, incident_id: int, owner: str, repo: str, per_page: int, current_user: User
    ) -> list[IncidentEvidence]:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        if current_user.role not in (UserRole.ADMIN, UserRole.INVESTIGATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you dont have permission to collect evidence",
            )
        if not settings.github_token:
            raise RuntimeError("github token is not configured")

        client = GithubClient(settings.github_token)
        provider = GithubProvider(client)

        commits = await provider.collect_commits(owner=owner, repo=repo)

        created_evidence = []

        for commit in commits:
            existing = await self.evidence_repository.get_by_external_id(
                incident_id=incident.id,
                tenant_id=current_user.tenant_id,
                source="github",
                external_id=commit["sha"],
                evidence_typ="commit",
                content=...,
            )
            if existing:
                continue
            evidence = await self.evidence_repository.create(
                incident_id=incident.id,
                tenant_id=current_user.tenant_id,
                added_by=current_user.id,
                source="github",
                external_id=commit["sha"],
                content=(
                    f"commit :{commit['message']}\n"
                    f"Author :{commit['author']}\n"
                    f"URL: {commit['url']}"
                ),
            )
            created_evidence.append(evidence)

            await self.audit_repository.create(
                tenant_id=current_user.tenant_id,
                incident_id=incident.id,
                performed_by=current_user.id,
                action="EVIDENCE_ADDED",
                old_value=None,
                new_value=f"github commit {commit['sha']}",
            )

        await self.db.commit()
        return created_evidence
