from app.repository.user import UserRepository
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
        from sqlalchemy.exc import IntegrityError
        
        slug = tenant_name.lower().strip().replace(" ", "-")
        try:
            # Wrap tenant and user creation in a nested transaction
            # so we can roll back cleanly on conflict
            async with self.db.begin_nested():
                existing_tenant = await self.tenant_repository.get_by_slug(slug)
                if existing_tenant:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Tenant already exists. Please use a different tenant name.",
                    )
                tenant = await self.tenant_repository.create(name=tenant_name, slug=slug)
                
                existing_user = await self.user_repository.get_by_email(email)
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="A user with this email already exists",
                    )
                
                passwordHash = hash_password(password)
                user = await self.user_repository.create_user(
                    email=email,
                    passwordHash=passwordHash,
                    name=name,
                    role=UserRole.ADMIN,
                    tenant_id=tenant.id,
                )
        except IntegrityError as e:
            error_msg = str(e).lower()
            if "tenant" in error_msg or "slug" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tenant already exists. Please use a different tenant name.",
                )
            if "user" in error_msg or "email" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration failed due to a conflict.",
            )

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login(self, tenant_name: str, email: str, password: str):
        slug = tenant_name.lower().strip().replace(" ", "-")

        tenant = await self.tenant_repository.get_by_slug(slug)

        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid tenant, email or password",
            )

        user = await self.user_repository.get_by_email(email=email, tenant_id=tenant.id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid tenant, email or password",
            )

        isPasswordValid = verify_password(
            password=password, hashed_password=user.passwordHash
        )

        if not isPasswordValid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid tenant, email or password",
            )

        access_token = create_access_token(user_id=user.id, role=user.role)

        refresh_token = create_refresh_token(user.id)

        return {"access_token": access_token}
