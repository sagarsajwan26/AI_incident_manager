from fastapi import APIRouter, Depends, status, HTTPException
from app.dependencies.auth import get_current_user
from app.core.authorization import require_role
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
)
from app.service.integration import IntegrationService
from app.exception.integration import DuplicateIntegrationError

router = APIRouter()


@router.post(
    "", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED
)
async def create_integration(
    data: IntegrationCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = IntegrationService(db)

    try:
        integration = await service.create_integration(
            tenant_id=current_user.tenant_id,
            provider=data.provider,
            credentials=data.credentials,
            webhook_secret=data.webhook_secret,
            is_active=data.is_active,
        )
    except DuplicateIntegrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
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


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    data: IntegrationUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = IntegrationService(db)

    integration = await service.update_integration(
        integration_id=integration_id,
        tenant_id=current_user.tenant_id,
        credentials=data.credentials,
        is_active=data.is_active,
    )
    if integration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="missing the integration"
        )

    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = IntegrationService(db)

    success = await service.delete_integration(
        integration_id=integration_id, tenant_id=current_user.tenant_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="missing the integration"
        )


@router.post("/{integration_id}/test", status_code=status.HTTP_200_OK)
async def test_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = IntegrationService(db)

    try:
        integration = await service.test_integration(
            integration_id=integration_id, tenant_id=current_user.tenant_id
        )
        if integration is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="missing the integration"
            )

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {
        "status": "success",
        "message": f"Integration {integration.provider} connection successfull",
    }
