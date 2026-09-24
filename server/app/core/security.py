import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from datetime import datetime, timezone, timedelta


def hash_password(password: str):
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(10))
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str):
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: str, role: str):
    payload = {
        "user_id": user_id,
        "role": role,
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.access_token_expire_minutes),
    }
    encoded = jwt.encode(payload, settings.access_token, algorithm="HS256")
    return encoded


def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.access_token, algorithms=["HS256"])

        if payload.get("type") != "access":
            return None
        user_id = payload.get("user_id")
        if user_id is None:
            return None

        return int(user_id)

    except InvalidTokenError as e:

        return None


def create_refresh_token(user_id: str):
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days),
    }
    encoded = jwt.encode(payload, settings.refresh_token, algorithm="HS256")
    return encoded


def verify_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.refresh_token, algorithms=["HS256"])

        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return payload

    except InvalidTokenError:
        return None
