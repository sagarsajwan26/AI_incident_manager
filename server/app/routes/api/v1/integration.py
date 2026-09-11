from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from app.dependencies.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User
from app.schemas.integration import IntegrationCreate, IntegrationResponse
from app.service.integration import IntegrationService

router = APIRouter()


@router.post(
    "", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED
)
async def create_integration(
    data: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IntegrationService(db)

    integration = await service.create_integration(
        tenant_id=current_user.tenant_id,
        provider=data.provider,
        credentials=data.credentials,
        is_active=data.is_active,
    )

    return integration


@router.get(
    "",
    response_model=list[IntegrationResponse],
)
async def get_integrations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    service = IntegrationService(db)

    integrations = await service.list_integrations(tenant_id=current_user.tenant_id)

    return integrations


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IntegrationService(db)

    integration = await service.get_integration(
        integration_id=integration_id, tenant_id=current_user.tenant_id
    )
    if integration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="missing the integration"
        )

    return integration
