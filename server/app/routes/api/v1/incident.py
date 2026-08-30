from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.incident_comment import (
    IncidentCommentResponse,
    CreateIncidentCommentRequest,
)
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.service.incident import IncidentService
from app.schemas.incident import (
    CreateIncidentRequest,
    IncidentResponse,
    AssignIncidentRequest,
    UpdateIncidentStatusRequest,
    IncidentAuditResponse,
)
from app.core.authorization import require_role

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
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)

    return await service.assign_incident(
        incident_id=incident_id,
        investigator_id=data.investigator_id,
        tenant_id=current_user.tenant_id,
    )


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: int,
    data: UpdateIncidentStatusRequest,
    current_user: User = Depends(require_role("admin", "investigator")),
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
    current_user: User = Depends(require_role("admin", "investigator")),
    db: AsyncSession = Depends(get_db),
):
    service = IncidentService(db)
    return await service.create_comment(
        incident_id=incident_id, content=data.content, current_user=current_user
    )
