from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repository.user import UserRepository


class UserService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def create_user(
        self,
        tenant_id: int,
        email: str,
        password: str,
        name: str,
        role: UserRole,
    ) -> User:

        if role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create another admin",
            )

        existing_user = await self.user_repository.get_by_email(
            email=email,
            tenant_id=tenant_id,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        password_hash = hash_password(password)

        user = await self.user_repository.create_user(
            tenant_id=tenant_id,
            email=email,
            passwordHash=password_hash,
            name=name,
            role=role,
        )

        await self.db.commit()

        return user
