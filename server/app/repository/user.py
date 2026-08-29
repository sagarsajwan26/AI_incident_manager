from app.models.user import User, UserRole
from app.database.session import get_db


async def create_user(
    self, tenant_id: int, email: str, passwordHash: str, name: str, role: UserRole
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
