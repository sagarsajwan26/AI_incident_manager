from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime


class RootCauseStatus(str, Enum):
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


class EvidenceAssessment(BaseModel):
    claim: str
    support: str
    is_direct: bool
    supports_root_cause: bool


class InvestigationResult(BaseModel):
    summary: str
    likely_root_cause: str
    root_cause_status: RootCauseStatus
    evidence: list[str]
    evidence_assessment: list[EvidenceAssessment]
    impact: str
    recommended_actions: list[str]
    unknowns: list[str]
    confidence: float = Field(ge=0.0, le=1.0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": "The incident includes a database timeout, but the supplied evidence does not establish the root cause.",
                "likely_root_cause": "Insufficient evidence to determine root cause.",
                "root_cause_status": "unknown",
                "evidence": ["ERROR database connection timeout after 30 seconds"],
                "evidence_assessment": [
                    {
                        "fact": "A database connection timeout occurred.",
                        "support": "The supplied evidence explicitly contains the timeout error.",
                        "is_direct": True,
                        "supports_root_cause": False,
                    }
                ],
                "impact": "The affected system may experience failed requests.",
                "recommended_actions": [
                    "Review application logs and deployment history."
                ],
                "unknowns": ["No evidence directly establishes the root cause."],
                "confidence": 0.4,
            }
        }
    )


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

    model_config = ConfigDict(from_attributes=True)


class AIInvestigationOutput(BaseModel):
    result: InvestigationResult
    prompt: str
