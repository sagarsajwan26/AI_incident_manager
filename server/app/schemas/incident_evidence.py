from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


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
    source: str
    external_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GithubEvidenceRequest(BaseModel):
    per_page: int = Field(default=10, ge=1, le=100)
