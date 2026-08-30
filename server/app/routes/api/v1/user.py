from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.authorization import require_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import CreateUserRequest, UserResponse
from app.service.user import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    data: CreateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.create_user(
        tenant_id=current_user.tenant_id,
        email=data.email,
        password=data.password,
        name=data.name,
        role=data.role,
    )
    return user
