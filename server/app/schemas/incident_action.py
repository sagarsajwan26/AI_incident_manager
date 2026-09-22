from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models.incident_action import IncidentActionPhase


class IncidentActionCreate(BaseModel):
    phase: IncidentActionPhase
    action_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    outcome: str | None = None


class IncidentActionResponse(BaseModel):
    id: int
    incident_id: int
    tenant_id: int
    performed_by: int
    phase: IncidentActionPhase
    action_type: str
    description: str
    outcome: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
