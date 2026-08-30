from datetime import datetime
from pydantic import BaseModel, Field


class CreateIncidentCommentRequest(BaseModel):
    content: str = Field(
        min_length=2,
        max_length=5000,
    )


class IncidentCommentResponse(BaseModel):
    id: int
    incident_id: int
    tenant_id: int
    author_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateIncidentCommentRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
