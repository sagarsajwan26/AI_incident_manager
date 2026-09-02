from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("tenant_name")
    @classmethod
    def validate_tenant_name(cls, value: str) -> str:
        value = value.strip()

        if any(char.isdigit() for char in value):
            raise ValueError("Tenant name cannot contain numbers")

        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if any(char.isdigit() for char in value):
            raise ValueError("Name cannot contain numbers")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter")

        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> EmailStr:
        return str(value).lower().strip()


class RegisterResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
