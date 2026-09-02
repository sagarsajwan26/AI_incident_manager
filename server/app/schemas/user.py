from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole


class UserResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    email: EmailStr
    role: UserRole
    model_config = ConfigDict(from_attributes=True)
