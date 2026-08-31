from app.schemas.investigation import InvestigationContext


class InvestigationPromptBuilder:
    def build(self, context: InvestigationContext) -> str:
        incident = context.incident

        comments = (
            "\n".join(f"-{comment.content}" for comment in context.comments)
            or "No comments available"
        )

        evidence = (
            "\n".join(
                f"-[{item.evidence_type}] {item.content}" for item in context.evidence
            )
            or "No evidence available"
        )

        audit_history = (
            "\n".join(
                (f"-{audit.action}: " f"{audit.old_value} -> {audit.new_value}")
                for audit in context.audit_history
            )
            or "No audit history available"
        )
        return f"""
You are an experienced production incident investigator.

Analyze the incident using ONLY the information provided below.

Do not invent facts.
Do not assume information that is not present.
Clearly distinguish evidence from hypotheses.

INCIDENT
--------
Title: {incident.title}
Description: {incident.description}
Severity: {incident.severity.value}
Status: {incident.status.value}
Assigned To: {incident.assigned_to}

COMMENTS
--------
{comments}

EVIDENCE
--------
{evidence}

AUDIT HISTORY
-------------
{audit_history}

Return ONLY valid JSON.

The response MUST contain exactly these fields:

{{
  "summary": "string",
  "likely_root_cause": "string",
  "root_cause_status": "confirmed | probable | unknown",  "evidence": [
    "string"
  ],
  "impact": "string",
  "recommended_actions": [
    "string"
  ],
  "unknowns": [
    "string"
  ],
  "confidence": 0.0
}}

STRICT INVESTIGATION RULES:

1. Every root-cause claim must be supported by supplied evidence.
2. Do not treat correlation as causation.
3. If the evidence is insufficient to establish a root cause,
   explicitly say "Insufficient evidence to determine root cause."
4. Separate:
   - confirmed facts
   - likely hypotheses
   - unknowns
5. Never invent system behavior, users, infrastructure,
   deployments, logs, or causes that are not present.
6. Do not infer that one event caused another unless the
   supplied evidence establishes that relationship.
"""
