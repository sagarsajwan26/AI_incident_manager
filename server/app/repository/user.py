from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(
        self,
        tenant_id: int,
        email: str,
        passwordHash: str,
        name: str,
        role: UserRole,
    ) -> User:

        user = User(
            tenant_id=tenant_id,
            email=email,
            passwordHash=passwordHash,
            name=name,
            role=role,
        )

        self.db.add(user)

        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def get_by_email(
        self,
        email: str,
        tenant_id: int | None = None,
    ) -> User | None:

        query = select(User).where(User.email == email)

        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:

        result = await self.db.execute(
            select(User)
        )

        return list(result.scalars().all())

    async def get_by_id_and_tenant(
        self,
        user_id: int,
        tenant_id: int,
    ) -> User | None:

        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.tenant_id == tenant_id,
            )
        )

        return result.scalar_one_or_none()
