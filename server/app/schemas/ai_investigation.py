from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime


class RootCauseStatus(str, Enum):
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


class EvidenceSupport(str, Enum):
    DIRECT = "direct"
    INFERRED = "inferred"
    UNSUPPORTED = "unsupported"


class EvidenceAssessment(BaseModel):
    claim: str
    support: str
    supports_root_cause: bool
    support_level: EvidenceSupport


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
                "summary": (
                    "A database connection timeout was recorded. "
                    "The supplied evidence does not establish the root cause."
                ),
                "likely_root_cause": ("Insufficient evidence to determine root cause."),
                "root_cause_status": "unknown",
                "evidence": ["ERROR database connection timeout after 30 seconds"],
                "evidence_assessment": [
                    {
                        "claim": "A database connection timeout occurred.",
                        "support": (
                            "The manual log explicitly contains "
                            "the database timeout error."
                        ),
                        "supports_root_cause": False,
                        "support_level": "direct",
                    },
                    {
                        "claim": (
                            "The GitHub commit was successfully "
                            "deployed to Production."
                        ),
                        "support": (
                            "The commit and deployment share the same "
                            "SHA and repository, and the deployment "
                            "status is successful."
                        ),
                        "supports_root_cause": False,
                        "support_level": "direct",
                    },
                    {
                        "claim": (
                            "The production deployment caused " "the database timeout."
                        ),
                        "support": (
                            "The supplied evidence does not establish "
                            "a causal relationship."
                        ),
                        "supports_root_cause": False,
                        "support_level": "unsupported",
                    },
                ],
                "impact": (
                    "The supplied evidence does not establish "
                    "the actual impact of the timeout."
                ),
                "recommended_actions": [
                    "Review application logs around the incident.",
                    "Review database connection and infrastructure metrics.",
                    "Review deployment logs for the affected repository.",
                ],
                "unknowns": [
                    "The supplied evidence does not establish the root cause.",
                    "The supplied evidence does not establish whether "
                    "the deployment contributed to the incident.",
                ],
                "confidence": 0.35,
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
