from datetime import datetime

from pydantic import BaseModel, Field


class CreateIncidentEvidenceRequest(BaseModel):
    evidence_type: str = Field(
        min_length=2,
        max_length=50,
    )
    content: str = Field(min_length=1, max_length=20000)


class IncidentEvidenceResponse(BaseModel):
    id: int
    incident_id: int
    tenant_id: int
    added_by: int
    evidence_type: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
