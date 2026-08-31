from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class RootCauseStatus(str, Enum):
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


class InvestigationResult(BaseModel):
    summary: str
    likely_root_cause: str
    root_cause_status: RootCauseStatus
    evidence: list[str]
    impact: str
    recommended_actions: list[str]
    unknowns: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class InvestigationResponse(BaseModel):
    id: int
    tenant_id: int
    incident_id: int
    triggered_by: int
    provider: str
    model: str
    result: InvestigationResult
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AIInvestigationOutput(BaseModel):
    result: InvestigationResult
    prompt: str
