from app.models.user import User
from app.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_access_token
from fastapi import HTTPException, Cookie, status, Depends
from app.repository.user import UserRepository


async def get_current_user(
    access_token: str | None = Cookie(default=None, include_in_schema=False),
    db: AsyncSession = Depends(get_db),
) -> User:
    print(access_token)
    user_repository = UserRepository(db)
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not foun")
    user_id = verify_access_token(access_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )
    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )

    return user


from app.core.logger import get_logger

logger = get_logger(__name__)
