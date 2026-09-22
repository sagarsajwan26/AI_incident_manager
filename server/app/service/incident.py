import json
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.exceptions import AIInvestigationError, AIConfigurationError
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
from app.service.ai_investigation import AIInvestigatorService
from app.integration.github.client import GithubClient
from app.integration.github.provider import GithubProvider
from app.integration.github.exceptions import GithubIntegrationError
from app.exception.integration import IntegrationConnectionError
from app.ai.evidence_relationship_analyzer import EvidenceRelationshipAnalyzer
from app.service.integration import IntegrationService
from app.models.incident_resource import IncidentResource
from app.schemas.incident import IncidentResourceCreate
from app.repository.Incident_resource import IncidentResourceRepository
from app.repository.incident_action import IncidentActionRepository
from app.models.incident_action import IncidentAction, IncidentActionPhase

ALLOWED_STATUS_TRANSITIONS = {
    IncidentStatus.OPEN: {
        IncidentStatus.INVESTIGATING,
        IncidentStatus.RESOLVED,
    },
    IncidentStatus.INVESTIGATING: {
        IncidentStatus.CONTAINED,
        IncidentStatus.RESOLVED,
    },
    IncidentStatus.CONTAINED: {
        IncidentStatus.INVESTIGATING,
        IncidentStatus.RESOLVED,
    },
    IncidentStatus.RESOLVED: {
        IncidentStatus.INVESTIGATING,
        IncidentStatus.CLOSED,
    },
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
        self.integration_service = IntegrationService(db)
        self.incident_resource_repository = IncidentResourceRepository(db)
        self.incident_action_repository = IncidentActionRepository(db)

    def get_available_transitions(
        self,
        incident: Incident,
        current_user: User,
    ) -> list[IncidentStatus]:
        transitions = ALLOWED_STATUS_TRANSITIONS[incident.status]

        if current_user.role == UserRole.INVESTIGATOR:
            transitions = {
                status for status in transitions if status != IncidentStatus.CLOSED
            }

        return list(transitions)

    async def create_incident(
        self,
        tenant_id: int,
        reported_by: int,
        title: str,
        description: str,
        severity: IncidentSeverity,
        resource: IncidentResourceCreate | None = None,
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

        if resource is not None:
            incident_resource = IncidentResource(
                incident_id=incident.id,
                tenant_id=tenant_id,
                provider=resource.provider,
                resource_type=resource.resource_type,
                identifier=resource.identifier,
            )
            await self.incident_resource_repository.create(incident_resource)
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
        print("INVESTIGATION EVIDENCE:")
        for item in evidence:
            print(item.evidence_type, item.external_id, item.content)
        audit_history = await self.audit_repository.get_by_incident(
            incident_id=incident.id, tenant_id=current_user.tenant_id
        )
        relationship_analyzer = EvidenceRelationshipAnalyzer()
        evidence_relationships = relationship_analyzer.analyze(evidence)
        print("EVIDENCE RELATIONSHIPS:")

        for relationship in evidence_relationships:
            print(relationship.model_dump())
        return InvestigationContext(
            incident=incident,
            comments=comments,
            evidence=evidence,
            audit_history=audit_history,
            evidence_relationships=evidence_relationships,
        )

    async def run_incident_investigation(
        self, incident_id: int, current_user: User, per_page: int = 10
    ) -> InvestigationResult:

        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )

        if current_user.role not in (UserRole.ADMIN, UserRole.INVESTIGATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you dont have permission to investigate this incident",
            )

        github_resource = next(
            (
                resource
                for resource in incident.resources
                if resource.provider == "github"
                and resource.resource_type == "repository"
            ),
            None,
        )
        if github_resource is not None:
            await self.collect_github_evidence(
                incident_id=incident_id, per_page=per_page, current_user=current_user
            )
            await self.collect_github_deployment_evidence(
                incident_id=incident_id, per_page=per_page, current_user=current_user
            )
        return await self.investigate_incident(
            incident_id=incident_id, current_user=current_user
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
            raise AIConfigurationError(
                provider="ai",
                cause=RuntimeError("AI investigation service is not configured"),
            )

        try:
            output = await self.ai_service.investigate(context)
        except AIInvestigationError as exc:
            # Propagate typed AI investigation errors; API layer will map them
            raise
        except Exception as exc:
            # Unexpected errors become integration errors
            from app.exception.integration import IntegrationConnectionError

            raise IntegrationConnectionError(provider="ai", cause=exc) from exc

        await self.investigation_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident_id,
            triggered_by=current_user.id,
            provider=self.ai_service.provider_name,
            model=self.ai_service.model_name,
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

    async def get_investigation(
        self,
        incident_id: int,
        investigation_id: int,
        current_user: User,
    ) -> InvestigationResponse:
        incident = await self.get_incident(
            incident_id=incident_id,
            current_user=current_user,
        )

        investigation = await self.investigation_repository.get_by_id_and_incident(
            investigation_id=investigation_id,
            incident_id=incident.id,
            tenant_id=current_user.tenant_id,
        )

        if investigation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found",
            )

        return InvestigationResponse.model_validate(investigation)

    async def collect_github_evidence(
        self, incident_id: int, per_page: int, current_user: User
    ) -> list[IncidentEvidence]:
        incident = await self.get_incident(
            incident_id=incident_id, current_user=current_user
        )
        if current_user.role not in (UserRole.ADMIN, UserRole.INVESTIGATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you dont have permission to collect evidence",
            )

        github_resource = next(
            (
                resource
                for resource in incident.resources
                if resource.provider == "github"
                and resource.resource_type == "repository"
            ),
            None,
        )
        if github_resource is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No GitHub repository is configured for this incident",
            )

        try:
            owner, repo = github_resource.identifier.split("/", 1)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitHub repository identifier. Expected owner/repo",
            )

        integration = await self.integration_service.get_integration_by_provider(
            provider="github",
            tenant_id=current_user.tenant_id,
        )

        if integration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub integration is not configured",
            )

        if not integration.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub integration is inactive",
            )

        token = integration.credentials.get("token")

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub integration credentials are invalid",
            )

        client = GithubClient(token)
        provider = GithubProvider(client)

        try:
            commits = await provider.collect_commits(
                owner=owner, repo=repo, per_page=per_page
            )
        except GithubIntegrationError as exc:
            raise IntegrationConnectionError(
                provider="github",
                cause=exc,
            ) from exc

        created_evidence = []

        for commit in commits:
            existing = await self.evidence_repository.get_by_external_id(
                incident_id=incident.id,
                tenant_id=current_user.tenant_id,
                source="github",
                external_id=commit["sha"],
            )
            if existing:
                continue
            evidence = await self.evidence_repository.create(
                incident_id=incident.id,
                tenant_id=current_user.tenant_id,
                added_by=current_user.id,
                source="github",
                external_id=commit["sha"],
                evidence_type="commit",
                content=json.dumps(
                    {
                        "source": "github",
                        "type": "commit",
                        "repository": commit["repository"],
                        "sha": commit["sha"],
                        "message": commit["message"],
                        "author": commit["author"],
                        "timestamp": commit["timestamp"],
                        "url": commit["url"],
                        "stats": commit["stats"],
                        "changed_files": commit["changed_files"],
                    },
                    indent=2,
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

    async def collect_github_deployment_evidence(
        self, incident_id: int, per_page: int, current_user: User
    ) -> list[IncidentEvidence]:
        incident = await self.get_incident(
            incident_id=incident_id,
            current_user=current_user,
        )
        if current_user.role not in (UserRole.ADMIN, UserRole.INVESTIGATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you dont have permission to collect evidence",
            )

        github_resource = next(
            (
                resource
                for resource in incident.resources
                if resource.provider == "github"
                and resource.resource_type == "repository"
            ),
            None,
        )
        if github_resource is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No GitHub repository is configured for this incident",
            )

        try:
            owner, repo = github_resource.identifier.split("/", 1)

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitHub repository identifier. Expected owner/repo",
            )
        integration = await self.integration_service.get_integration_by_provider(
            provider="github", tenant_id=current_user.tenant_id
        )

        if integration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="github integration is not configured",
            )

        if not integration.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub integration is inactive",
            )
        token = integration.credentials.get("token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub integration credentials are invalid",
            )

        client = GithubClient(token)
        provider = GithubProvider(client)
        deployments = await provider.collect_deployments(
            owner=owner, repo=repo, per_page=per_page
        )

        created_evidence = []

        for deployment in deployments:
            external_id = f"deployment:{deployment['deployment_id']}"

            existing = await self.evidence_repository.get_by_external_id(
                incident_id=incident.id,
                tenant_id=current_user.tenant_id,
                source="github",
                external_id=external_id,
            )
            if existing:
                continue

            evidence = await self.evidence_repository.create(
                incident_id=incident.id,
                tenant_id=current_user.tenant_id,
                added_by=current_user.id,
                source="github",
                external_id=external_id,
                evidence_type="deployment",
                content=json.dumps(
                    {
                        "source": "github",
                        "type": "deployment",
                        "deployment_id": deployment["deployment_id"],
                        "sha": deployment["sha"],
                        "repository": deployment["repository"],
                        "ref": deployment["ref"],
                        "environment": deployment["environment"],
                        "description": deployment["description"],
                        "created_at": deployment["created_at"],
                        "updated_at": deployment["updated_at"],
                        "url": deployment["url"],
                        "status": deployment["status"],
                        "status_description": deployment["status_description"],
                        "status_created_at": deployment["status_created_at"],
                    },
                    indent=2,
                ),
            )

            created_evidence.append(evidence)

            await self.audit_repository.create(
                tenant_id=current_user.tenant_id,
                incident_id=incident.id,
                performed_by=current_user.id,
                action="EVIDENCE_ADDED",
                old_value=None,
                new_value=f"github deployment {deployment['deployment_id']}",
            )

        await self.db.commit()
        return created_evidence

    async def create_incident_action(
        self,
        incident_id: int,
        current_user: User,
        phase: IncidentActionPhase,
        action_type: str,
        description: str,
        outcome: str | None = None,
    ) -> IncidentAction:
        incident = await self.get_incident(incident_id, current_user)
        
        if phase == IncidentActionPhase.CLOSURE:
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only admins can create closure actions"
                )
            if incident.status != IncidentStatus.RESOLVED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Closure actions can only be created for resolved incidents"
                )
                
        action = IncidentAction(
            incident_id=incident.id,
            tenant_id=current_user.tenant_id,
            performed_by=current_user.id,
            phase=phase,
            action_type=action_type,
            description=description,
            outcome=outcome,
        )
        action = await self.incident_action_repository.create(action)
        
        await self.audit_repository.create(
            tenant_id=current_user.tenant_id,
            incident_id=incident.id,
            performed_by=current_user.id,
            action="ACTION_ADDED",
            old_value=None,
            new_value=f"{phase.value}: {action_type}",
        )
        await self.db.commit()
        return action

    async def get_incident_actions(
        self,
        incident_id: int,
        current_user: User,
    ) -> list[IncidentAction]:
        incident = await self.get_incident(incident_id, current_user)
        return await self.incident_action_repository.get_by_incident(
            incident_id=incident.id,
            tenant_id=current_user.tenant_id
        )
