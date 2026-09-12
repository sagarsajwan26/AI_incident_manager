from fastapi import APIRouter, Depends, HTTPException, status
from app.ai.exceptions import AIInvestigationError
from app.exception.integration import IntegrationConnectionError
from app.integration.github.exceptions import (
    GithubAuthenticationError,
    GithubPermissionError,
    GithubNotFoundError,
    GithubRateLimitError,
    GithubUpstreamError,
    GithubTimeoutError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.incident_comment import (
    IncidentCommentResponse,
    CreateIncidentCommentRequest,
    UpdateIncidentCommentRequest,
)
from app.schemas.investigation import InvestigationContext
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.service.incident import IncidentService
from app.schemas.incident import (
    CreateIncidentRequest,
    IncidentResponse,
    AssignIncidentRequest,
    UpdateIncidentStatusRequest,
    IncidentAuditResponse,
)
from app.schemas.incident_evidence import (
    CreateIncidentEvidenceRequest,
    IncidentEvidenceResponse,
)
from app.core.authorization import require_role
from app.schemas.ai_investigation import InvestigationResult, InvestigationResponse
from app.service.ai_investigation import AIInvestigatorService
from app.ai.ollama_provider import OllamaProvider
from app.core.config import settings
from app.schemas.incident_evidence import GithubEvidenceRequest

router = APIRouter()


@router.post(
    "/",
    response_model=IncidentResponse,
)
async def create_incident(
    data: CreateIncidentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = IncidentService(db)
    return await service.create_incident(
        tenant_id=current_user.tenant_id,
        reported_by=current_user.id,
        title=data.title,
        description=data.description,
        severity=data.severity,
    )


@router.get("/", response_model=list[IncidentResponse])
async def get_incident(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    service = IncidentService(db)
    return await service.get_all_incident(current_user=current_user)


@router.get("/{incident_id}/audit", response_model=list[IncidentAuditResponse])
async def get_incident_audit(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    return await service.get_audit_history(
        incident_id=incident_id, current_user=current_user
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = IncidentService(db)
    return await service.get_incident(
        incident_id=incident_id, current_user=current_user
    )


@router.patch("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: int,
    data: AssignIncidentRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)

    return await service.assign_incident(
        incident_id=incident_id,
        investigator_id=data.investigator_id,
        tenant_id=current_user.tenant_id,
        current_user=current_user,
    )


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: int,
    data: UpdateIncidentStatusRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    return await service.update_status(
        incident_id=incident_id,
        new_status=data.status,
        tenant_id=current_user.tenant_id,
        current_user=current_user,
    )


@router.get("/{incident_id}/comments", response_model=list[IncidentCommentResponse])
async def get_incident_comments(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)

    return await service.get_comments(
        incident_id=incident_id, current_user=current_user
    )


@router.post(
    "/{incident_id}/comments",
    response_model=IncidentCommentResponse,
)
async def create_incident_comment(
    incident_id: int,
    data: CreateIncidentCommentRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    return await service.create_comment(
        incident_id=incident_id, content=data.content, current_user=current_user
    )


@router.patch(
    "/{incident_id}/comments/{comment_id}", response_model=IncidentCommentResponse
)
async def update_incident_comment(
    incident_id: int,
    comment_id: int,
    data: UpdateIncidentCommentRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    return await service.update_comment(
        incident_id=incident_id,
        comment_id=comment_id,
        content=data.content,
        current_user=current_user,
    )


@router.delete("/{incident_id}/comments/{comment_id}", status_code=204)
async def delete_incident_comment(
    incident_id: int,
    comment_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    await service.delete_comment(
        incident_id=incident_id, comment_id=comment_id, current_user=current_user
    )

    return None


@router.post(
    "/{incident_id}/evidence",
    response_model=IncidentEvidenceResponse,
)
async def create_incident_evidence(
    incident_id: int,
    data: CreateIncidentEvidenceRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)

    return await service.create_evidence(
        incident_id=incident_id,
        evidence_type=data.evidence_type,
        content=data.content,
        current_user=current_user,
    )


@router.get(
    "/{incident_id}/evidence",
    response_model=list[IncidentEvidenceResponse],
)
async def get_incident_evidence(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    return await service.get_evidence(
        incident_id=incident_id, current_user=current_user
    )


@router.get(
    "/{incident_id}/investigation-context",
    response_model=InvestigationContext,
)
async def get_investigation_context(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)

    return await service.get_investigation_context(
        incident_id=incident_id, current_user=current_user
    )


@router.post("/{incident_id}/investigate", response_model=InvestigationResult)
async def investigate_incident(
    incident_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR)),
    db: AsyncSession = Depends(get_db),
):

    provider = OllamaProvider()
    ai_service = AIInvestigatorService(
        provider=provider, provider_name="ollama", model_name=settings.ollama_model
    )
    incident_service = IncidentService(db=db, ai_service=ai_service)

    try:
        return await incident_service.investigate_incident(
            incident_id=incident_id, current_user=current_user
        )
    except AIInvestigationError as exc:
        # AI provider related errors
        from app.ai.exceptions import (
            AIProviderTimeoutError,
            AIProviderUnavailableError,
            AIInvalidResponseError,
            AIConfigurationError,
        )
        if isinstance(exc, AIProviderTimeoutError):
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI provider timeout",
            ) from exc
        if isinstance(exc, AIProviderUnavailableError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI provider unavailable",
            ) from exc
        if isinstance(exc, AIInvalidResponseError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI provider returned invalid response",
            ) from exc
        if isinstance(exc, AIConfigurationError):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI configuration error",
            ) from exc
        # Fallback for unexpected AI errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI investigation failed",
        ) from exc
    except IntegrationConnectionError as exc:
        # Fallback for other integration errors
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI investigation failed",
        ) from exc

@router.get(
    "/{incident_id}/investigations",
    response_model=list[InvestigationResponse],
)
async def get_investigation_history(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident_service = IncidentService(db)

    return await incident_service.get_investigation_history(
        incident_id=incident_id, current_user=current_user
    )


@router.get(
    "/{incident_id}/investigations/{investigation_id}",
    response_model=InvestigationResponse,
)
async def get_investigation(
    incident_id: int,
    investigation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    incident_service = IncidentService(db)

    return await incident_service.get_investigation(
        incident_id=incident_id, 
        investigation_id=investigation_id, 
        current_user=current_user
    )


@router.post(
    "/{incident_id}/evidence/github", response_model=list[IncidentEvidenceResponse]
)
async def collect_github_evidence(
    incident_id: int,
    request: GithubEvidenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    try:
        return await service.collect_github_evidence(
            incident_id=incident_id,
            owner=request.owner,
            repo=request.repo,
            per_page=request.per_page,
            current_user=current_user,
        )
    except IntegrationConnectionError as exc:
        cause = exc.cause

        if isinstance(cause, GithubAuthenticationError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="GitHub authentication failed",
            ) from exc

        if isinstance(cause, GithubPermissionError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="GitHub denied access to the requested resource",
            ) from exc

        if isinstance(cause, GithubNotFoundError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub repository or resource was not found",
            ) from exc

        if isinstance(cause, GithubRateLimitError):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="GitHub API rate limit exceeded",
            ) from exc

        if isinstance(cause, GithubTimeoutError):
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="GitHub API request timed out",
            ) from exc

        if isinstance(cause, GithubUpstreamError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="GitHub API is currently unavailable",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="GitHub integration request failed",
        ) from exc


@router.post(
    "/{incident_id}/evidence/github/deployments",
    response_model=list[IncidentEvidenceResponse],
)
async def collect_github_deployment_evidence(
    incident_id: int,
    request: GithubEvidenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)

    return await service.collect_github_deployment_evidence(
        incident_id=incident_id,
        owner=request.owner,
        repo=request.repo,
        per_page=request.per_page,
        current_user=current_user,
    )
