from datetime import datetime
from pydantic import BaseModel, Field
from app.models.incident import IncidentSeverity, IncidentStatus


class CreateIncidentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    severity: IncidentSeverity


class IncidentResponse(BaseModel):
    tenant_id: int
    id: int
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    reported_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssignIncidentRequest(BaseModel):
    investigator_id: int
