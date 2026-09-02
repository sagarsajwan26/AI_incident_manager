from app.schemas.investigation import InvestigationContext


class InvestigationPromptBuilder:
    def build(self, context: InvestigationContext) -> str:
        incident = context.incident

        comments = (
            "\n".join(f"- {comment.content}" for comment in context.comments)
            or "No comments available"
        )

        evidence = (
            "\n".join(
                f"- [{item.evidence_type}] {item.content}" for item in context.evidence
            )
            or "No evidence available"
        )

        audit_history = (
            "\n".join(
                f"- {audit.action}: {audit.old_value} -> {audit.new_value}"
                for audit in context.audit_history
            )
            or "No audit history available"
        )

        return f"""
```

You are an experienced production incident investigator.

Analyze the incident using ONLY the information provided below.

Do not invent facts.
Do not assume information that is not present.
Clearly distinguish evidence from hypotheses.

## INCIDENT

Title: {incident.title}
Description: {incident.description}
Severity: {incident.severity.value}
Status: {incident.status.value}
Assigned To: {incident.assigned_to}

## COMMENTS

{comments}

## EVIDENCE

{evidence}

## AUDIT HISTORY

{audit_history}

Return ONLY valid JSON.

The response MUST contain exactly these fields:

{{
"summary": "string",
"likely_root_cause": "string",
"root_cause_status": "confirmed",
"evidence": [
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

IMPORTANT:

"root_cause_status" MUST ALWAYS be exactly one of:

* "confirmed"
* "probable"
* "unknown"

If the supplied evidence is insufficient to determine the root cause:

"likely_root_cause" MUST be:
"Insufficient evidence to determine root cause."

and

"root_cause_status" MUST be:
"unknown"

STRICT INVESTIGATION RULES:

1. Every root-cause claim must be supported by supplied evidence.
2. Do not treat correlation as causation.
3. If evidence is insufficient, do not guess.
4. Separate confirmed facts from hypotheses and unknowns.
5. Never invent system behavior, users, infrastructure, deployments, logs, or causes.
6. Do not infer causation unless the supplied evidence establishes it.
7. Every required JSON field must be present.
8. Return JSON only. Do not include markdown.
   """
