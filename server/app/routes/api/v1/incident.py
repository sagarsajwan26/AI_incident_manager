from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.incident import CreateIncidentRequest, IncidentResponse
from app.service.incident import IncidentService

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
    incident = await service.create_incident(
        tenant_id=current_user.tenant_id,
        reported_by=current_user.id,
        title=data.title,
        description=data.description,
        severity=data.severity,
    )

    await db.commit()
    await db.refresh(incident)
    return incident


@router.get("/", response_model=list[IncidentResponse])
async def get_incident(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    service = IncidentService(db)
    return await service.get_all_incident(tenant_id=current_user.tenant_id)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = IncidentService(db)
    return await service.get_incident(
        tenant_id=current_user.tenant_id, incident_id=incident_id
    )
