from datetime import datetime, timezone

from app.ai.prompt_builder import InvestigationPromptBuilder
from app.schemas.investigation import (
    InvestigationContext,
    EvidenceRelationship,
)
from app.schemas.incident import IncidentResponse
from app.schemas.incident_evidence import IncidentEvidenceResponse


CREATED_AT = datetime(
    2026,
    2,
    27,
    11,
    9,
    43,
    tzinfo=timezone.utc,
)


def create_incident() -> IncidentResponse:
    return IncidentResponse(
        id=4,
        tenant_id=8,
        title="Database connection timeout",
        description="Production database connections are timing out.",
        status="open",
        severity="high",
        reported_by=1,
        assigned_to=None,
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )


def create_commit_evidence() -> IncidentEvidenceResponse:
    return IncidentEvidenceResponse(
        id=2,
        incident_id=4,
        tenant_id=8,
        added_by=1,
        evidence_type="commit",
        content=(
            "commit :first commit\n"
            "Author :sagarsajwan26\n"
            "URL: https://github.com/"
            "sagarsajwan79/darkx/commit/"
            "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92"
        ),
        source="github",
        external_id="4bf1e97f5005d06c12b1ea6ba89bf8643140bc92",
        created_at=CREATED_AT,
    )


def create_deployment_evidence() -> IncidentEvidenceResponse:
    return IncidentEvidenceResponse(
        id=4,
        incident_id=4,
        tenant_id=8,
        added_by=1,
        evidence_type="deployment",
        content="""{
            "source": "github",
            "type": "deployment",
            "deployment_id": 3939625728,
            "sha": "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92",
            "repository": "sagarsajwan79/darkx",
            "environment": "Production",
            "status": "success"
        }""",
        source="github",
        external_id="deployment:3939625728",
        created_at=CREATED_AT,
    )


def create_context(
    evidence=None,
    evidence_relationships=None,
) -> InvestigationContext:

    return InvestigationContext(
        incident=create_incident(),
        comments=[],
        evidence=evidence or [],
        audit_history=[],
        evidence_relationships=evidence_relationships or [],
    )


def test_prompt_contains_incident_information():

    builder = InvestigationPromptBuilder()

    context = create_context()

    prompt = builder.build(context)

    assert "Database connection timeout" in prompt
    assert "Production database connections are timing out." in prompt


def test_prompt_contains_evidence_information():

    builder = InvestigationPromptBuilder()

    commit = create_commit_evidence()

    context = create_context(
        evidence=[commit],
    )

    prompt = builder.build(context)

    assert "commit :first commit" in prompt
    assert "sagarsajwan26" in prompt
    assert "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92" in prompt
    assert "sagarsajwan79/darkx" in prompt


def test_prompt_contains_deterministic_evidence_relationship():

    builder = InvestigationPromptBuilder()

    commit = create_commit_evidence()
    deployment = create_deployment_evidence()

    relationship = EvidenceRelationship(
        source_evidence_id=2,
        target_evidence_id=4,
        relationship_type="commit_deployed",
        reason=(
            "GitHub commit "
            "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92 "
            "is associated with deployment 3939625728 because "
            "both records reference the same SHA in repository "
            "sagarsajwan79/darkx."
        ),
    )

    context = create_context(
        evidence=[commit, deployment],
        evidence_relationships=[relationship],
    )

    prompt = builder.build(context)

    assert "commit_deployed" in prompt
    assert "Evidence 2" in prompt
    assert "Evidence 4" in prompt
    assert "3939625728" in prompt
    assert "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92" in prompt


def test_prompt_contains_temporal_and_causality_rules():

    builder = InvestigationPromptBuilder()

    context = create_context()

    prompt = builder.build(context)

    assert "TEMPORAL AND CAUSALITY RULES" in prompt
    assert "matching commit SHA does NOT establish causality" in prompt
    assert "Do NOT infer temporal ordering" in prompt
    assert "If timestamps are not available" in prompt


def test_prompt_distinguishes_relationship_from_causality():

    builder = InvestigationPromptBuilder()

    commit = create_commit_evidence()
    deployment = create_deployment_evidence()

    relationship = EvidenceRelationship(
        source_evidence_id=2,
        target_evidence_id=4,
        relationship_type="commit_deployed",
        reason=(
            "GitHub commit "
            "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92 "
            "is associated with deployment 3939625728 because "
            "both records reference the same SHA in repository "
            "sagarsajwan79/darkx."
        ),
    )

    context = create_context(
        evidence=[commit, deployment],
        evidence_relationships=[relationship],
    )

    prompt = builder.build(context)

    assert "commit_deployed" in prompt
    assert "does NOT establish causality" in prompt
    assert "matching commit SHA does NOT establish causality" in prompt


def test_prompt_contains_no_unsupported_negative_claims_rule():

    builder = InvestigationPromptBuilder()

    context = create_context()

    prompt = builder.build(context)

    assert "NO UNSUPPORTED NEGATIVE CLAIMS" in prompt
    assert "Absence of evidence is NOT evidence" in prompt
    assert "state UNKNOWN" in prompt


def test_prompt_contains_evidence_assessment_rules():

    builder = InvestigationPromptBuilder()

    context = create_context()

    prompt = builder.build(context)

    assert "EVIDENCE ASSESSMENT" in prompt
    assert "claim" in prompt
    assert "support" in prompt
    assert "supports_root_cause" in prompt
    assert "support_level" in prompt
    
    prompt_lower = prompt.lower()
    
    assert "direct" in prompt_lower
    assert "inferred" in prompt_lower
    assert "unsupported" in prompt_lower


def test_prompt_contains_unknown_root_cause_rules():

    builder = InvestigationPromptBuilder()

    context = create_context()

    prompt = builder.build(context)

    assert "unknown" in prompt.lower()
    assert "root cause" in prompt.lower()
    assert "insufficient evidence" in prompt.lower()


def test_prompt_contains_recommendation_evidence_discipline():

    builder = InvestigationPromptBuilder()

    context = create_context()

    prompt = builder.build(context)

    assert "RECOMMENDED ACTIONS" in prompt
    
    prompt_lower = prompt.lower()
    assert "must be based on information gaps" in prompt_lower
    assert "do not introduce an event" in prompt_lower
    assert "must not assume" in prompt_lower
