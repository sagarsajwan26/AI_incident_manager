from app.repository.auth import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User, UserRole
from app.repository.tenant import TenantRepository


from app.core.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.tenant_repository = TenantRepository(db)

    async def register(
        self, email: str, password: str, name: str, tenant_name: str
    ) -> User:
        slug = tenant_name.lower().strip().replace(" ", "-")
        existing_tenant = await self.tenant_repository.get_by_slug(slug)
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tenant already exists",
            )
        tenant = await self.tenant_repository.create(name=tenant_name, slug=slug)
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="email already exist"
            )
        passwordHash = hash_password(password)
        user = await self.user_repository.create_user(
            email=email,
            passwordHash=passwordHash,
            name=name,
            role=UserRole.ADMIN,
            tenant_id=tenant.id,
        )

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login(self, email, password):
        user = await self.user_repository.get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid email or password",
            )

        isPasswordValid = verify_password(
            password=password, hashed_password=user.passwordHash
        )

        if not isPasswordValid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid email or password",
            )

        access_token = create_access_token(user_id=user.id, role=user.role)

        refresh_token = create_refresh_token(user.id)

        return {"access_token": access_token}
