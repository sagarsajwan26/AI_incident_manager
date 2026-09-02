import asyncio
from datetime import datetime, timezone

from app.ai.ollama_provider import OllamaProvider
from app.service.ai_investigation import AIInvestigatorService
from app.schemas.investigation import InvestigationContext

from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.incident_comment import IncidentComment
from app.models.incident_evidence import IncidentEvidence
from app.models.incident_audit import IncidentAuditLog


async def main():

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 1. Fake incident
    # ---------------------------------------------------------

    incident = Incident(
        id=1,
        tenant_id=1,
        reported_by=1,
        title="API returning 500 errors",
        description=(
            "Users are receiving HTTP 500 errors when accessing " "the payment API."
        ),
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.INVESTIGATING,
        assigned_to=2,
        created_at=now,
        updated_at=now,
    )

    # ---------------------------------------------------------
    # 2. Fake evidence
    # ---------------------------------------------------------

    evidence = [
        IncidentEvidence(
            id=1,
            incident_id=1,
            tenant_id=1,
            added_by=2,
            evidence_type="log",
            content=(
                "Application logs show repeated database connection "
                "timeout errors immediately before the 500 responses."
            ),
            source="manual",
            external_id=None,
            created_at=now,
        )
    ]

    # ---------------------------------------------------------
    # 3. Fake comments
    # ---------------------------------------------------------

    comments = [
        IncidentComment(
            id=1,
            incident_id=1,
            tenant_id=1,
            author_id=1,
            content="Application started returning 500 errors.",
            created_at=datetime.now(timezone.utc),
        )
    ]

    # ---------------------------------------------------------
    # 4. Fake audit history
    # ---------------------------------------------------------

    audit_history = [
        IncidentAuditLog(
            id=1,
            tenant_id=1,
            incident_id=1,
            performed_by=1,
            action="CREATED",
            old_value=None,
            new_value=None,
            created_at=now,
        ),
        IncidentAuditLog(
            id=2,
            tenant_id=1,
            incident_id=1,
            performed_by=1,
            action="STATUS_CHANGED",
            old_value="open",
            new_value="investigating",
            created_at=now,
        ),
    ]

    # ---------------------------------------------------------
    # 5. Build investigation context
    # ---------------------------------------------------------

    context = InvestigationContext(
        incident=incident,
        comments=comments,
        evidence=evidence,
        audit_history=audit_history,
    )

    # ---------------------------------------------------------
    # 6. Create Ollama provider
    # ---------------------------------------------------------

    provider = OllamaProvider()

    # ---------------------------------------------------------
    # 7. Create AI investigator service
    # ---------------------------------------------------------

    ai_service = AIInvestigatorService(
        provider=provider,
        provider_name="ollama",
        model_name="qwen2.5:3b",
    )

    # ---------------------------------------------------------
    # 8. Run investigation
    # ---------------------------------------------------------

    result = await ai_service.investigate(context)

    # ---------------------------------------------------------
    # 9. Print result
    # ---------------------------------------------------------

    print("\n==============================")
    print("AI INVESTIGATION RESULT")
    print("==============================")

    print(result.result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
