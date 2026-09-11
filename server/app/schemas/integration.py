from pydantic import BaseModel
from datetime import datetime


class IntegrationCreate(BaseModel):
    provider: str
    credentials: dict
    is_active: bool = True


class IntegrationResponse(BaseModel):
    id: int
    provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class IntegrationUpdate(BaseModel):
    credentials: dict | None = None
    is_active: bool | None = None
