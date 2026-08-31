from datetime import datetime
from pydantic import BaseModel

from app.schemas.incident import IncidentResponse
from app.schemas.incident_evidence import IncidentEvidenceResponse
from app.schemas.incident_comment import IncidentCommentResponse
from app.schemas.incident import IncidentAuditResponse


class InvestigationContext(BaseModel):
    incident: IncidentResponse
    comments: list[IncidentCommentResponse]
    evidence: list[IncidentEvidenceResponse]
    audit_history: list[IncidentAuditResponse]
