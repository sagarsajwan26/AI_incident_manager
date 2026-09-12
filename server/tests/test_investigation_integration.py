from datetime import datetime, timezone

import pytest

from app.ai.evidence_relationship_analyzer import (
    EvidenceRelationshipAnalyzer,
)
from app.ai.investigation_validator import InvestigationValidator
from app.ai.prompt_builder import InvestigationPromptBuilder
from app.schemas.ai_investigation import (
    EvidenceAssessment,
    EvidenceSupport,
    InvestigationResult,
    RootCauseStatus,
)
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


COMMIT_SHA = "4bf1e97f5005d06c12b1ea6ba89bf8643140bc92"
REPOSITORY = "sagarsajwan79/darkx"


def make_evidence(
    evidence_id: int,
    evidence_type: str,
    content: str,
    source: str = "github",
) -> IncidentEvidenceResponse:

    return IncidentEvidenceResponse(
        id=evidence_id,
        incident_id=4,
        tenant_id=8,
        added_by=1,
        source=source,
        evidence_type=evidence_type,
        external_id=str(evidence_id),
        content=content,
        created_at=CREATED_AT,
    )


def database_timeout_evidence() -> IncidentEvidenceResponse:

    return make_evidence(
        evidence_id=1,
        source="log",
        evidence_type="log",
        content="ERROR database connection timeout after 30 seconds",
    )


def matching_commit_evidence() -> IncidentEvidenceResponse:

    return make_evidence(
        evidence_id=2,
        evidence_type="commit",
        content=(
            "commit :first commit\n"
            "Author :sagarsajwan26\n"
            f"URL: https://github.com/{REPOSITORY}/commit/{COMMIT_SHA}"
        ),
    )


def matching_deployment_evidence() -> IncidentEvidenceResponse:

    return make_evidence(
        evidence_id=4,
        evidence_type="deployment",
        content=f"""
{{
    "source": "github",
    "type": "deployment",
    "deployment_id": 3939625728,
    "sha": "{COMMIT_SHA}",
    "repository": "{REPOSITORY}",
    "ref": "{COMMIT_SHA}",
    "environment": "Production",
    "created_at": "2026-02-27T11:09:43Z",
    "updated_at": "2026-02-27T11:09:44Z",
    "status": "success"
}}
""",
    )


def unrelated_commit_evidence() -> IncidentEvidenceResponse:

    return make_evidence(
        evidence_id=3,
        evidence_type="commit",
        content="""
{
    "sha": "c94bc12c2b10670dbfe9bc733cfffb8e625b9613",
    "repository": "sagarsajwan79/certx",
    "message": "unrelated commit"
}
""",
    )


def build_unknown_result() -> InvestigationResult:

    return InvestigationResult(
        summary=(
            "The supplied evidence establishes a database connection "
            "timeout and a GitHub commit associated with a successful "
            "Production deployment, but it does not establish a causal "
            "relationship between the deployment and the timeout."
        ),
        likely_root_cause=(
            "Insufficient evidence to determine root cause."
        ),
        root_cause_status=RootCauseStatus.UNKNOWN,
        evidence=[
            "A database connection timeout after 30 seconds was recorded.",
            (
                f"GitHub commit {COMMIT_SHA} is associated with "
                "successful Production deployment 3939625728."
            ),
        ],
        evidence_assessment=[
            EvidenceAssessment(
                claim=(
                    "A database connection timeout after 30 seconds "
                    "was recorded."
                ),
                support=(
                    "The supplied log explicitly contains the "
                    "database timeout."
                ),
                supports_root_cause=False,
                support_level=EvidenceSupport.DIRECT,
            ),
            EvidenceAssessment(
                claim=(
                    f"GitHub commit {COMMIT_SHA} is associated with "
                    "deployment 3939625728."
                ),
                support=(
                    "The commit and deployment reference the same "
                    "SHA and repository."
                ),
                supports_root_cause=False,
                support_level=EvidenceSupport.DIRECT,
            ),
        ],
        impact=(
            "The affected system may experience failed requests "
            "because of the database timeout."
        ),
        recommended_actions=[
            (
                "Review application logs around the incident "
                "to determine what occurred when the database "
                "timeout was recorded."
            ),
            (
                "Review deployment history and application telemetry "
                "for additional evidence."
            ),
        ],
        unknowns=[
            "The supplied evidence does not directly establish the root cause."
        ],
        confidence=0.40,
    )


# ---------------------------------------------------------
# TEST 1
# Golden scenario
# ---------------------------------------------------------

def test_full_pipeline_matching_commit_and_deployment():

    evidence = [
        database_timeout_evidence(),
        matching_commit_evidence(),
        matching_deployment_evidence(),
    ]

    analyzer = EvidenceRelationshipAnalyzer()

    relationships = analyzer.analyze(evidence)

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship.source_evidence_id == 2
    assert relationship.target_evidence_id == 4
    assert relationship.relationship_type == "commit_deployed"

    assert COMMIT_SHA in relationship.reason
    assert REPOSITORY in relationship.reason


# ---------------------------------------------------------
# TEST 2
# Relationship reaches prompt
# ---------------------------------------------------------

def test_relationship_is_propagated_into_prompt():

    evidence = [
        database_timeout_evidence(),
        matching_commit_evidence(),
        matching_deployment_evidence(),
    ]

    analyzer = EvidenceRelationshipAnalyzer()

    relationships = analyzer.analyze(evidence)

    assert len(relationships) == 1

    # We need a lightweight context object containing
    # the relationship so PromptBuilder can consume it.
    class FakeContext:
        pass

    context = FakeContext()
    context.incident = type(
        "Incident",
        (),
        {
            "id": 4,
            "title": "Database incident",
            "description": "Database connection timeout",
            "severity": type("Severity", (), {"value": "high"})(),
            "status": type("Status", (), {"value": "open"})(),
            "assigned_to": None,
        },
    )()

    context.comments = []
    context.evidence = evidence
    context.audit_history = []
    context.evidence_relationships = relationships

    builder = InvestigationPromptBuilder()

    prompt = builder.build(context)

    assert "commit_deployed" in prompt
    assert "Evidence 2" in prompt
    assert "Evidence 4" in prompt
    assert COMMIT_SHA in prompt
    assert REPOSITORY in prompt


# ---------------------------------------------------------
# TEST 3
# Relationship does NOT become causality
# ---------------------------------------------------------

def test_commit_deployment_relationship_does_not_establish_root_cause():

    result = build_unknown_result()

    validator = InvestigationValidator()

    validated = validator.validate(result)

    assert validated.root_cause_status == RootCauseStatus.UNKNOWN

    assert validated.likely_root_cause == (
        "insufficient evidence to determine root cause"
    )

    assert validated.confidence <= 0.49

    assert not any(
        assessment.supports_root_cause
        for assessment in validated.evidence_assessment
    )


# ---------------------------------------------------------
# TEST 4
# Timeout alone remains unknown
# ---------------------------------------------------------

def test_database_timeout_without_causal_evidence_is_unknown():

    result = InvestigationResult(
        summary="A database timeout was recorded.",
        likely_root_cause="Database failure",
        root_cause_status=RootCauseStatus.CONFIRMED,
        evidence=[
            "ERROR database connection timeout after 30 seconds"
        ],
        evidence_assessment=[
            EvidenceAssessment(
                claim="A database connection timeout occurred.",
                support=(
                    "The supplied log explicitly contains "
                    "the timeout."
                ),
                supports_root_cause=False,
                support_level=EvidenceSupport.DIRECT,
            )
        ],
        impact="Requests may fail.",
        recommended_actions=[
            "Review application logs."
        ],
        unknowns=[],
        confidence=0.90,
    )

    validator = InvestigationValidator()

    validated = validator.validate(result)

    assert validated.root_cause_status == RootCauseStatus.UNKNOWN
    assert validated.confidence <= 0.49


# ---------------------------------------------------------
# TEST 5
# Unrelated commit does not create relationship
# ---------------------------------------------------------

def test_unrelated_commit_and_deployment_produce_no_relationship():

    evidence = [
        database_timeout_evidence(),
        unrelated_commit_evidence(),
        matching_deployment_evidence(),
    ]

    analyzer = EvidenceRelationshipAnalyzer()

    relationships = analyzer.analyze(evidence)

    assert relationships == []


# ---------------------------------------------------------
# TEST 6
# Full evidence graph contains only valid relationship
# ---------------------------------------------------------

def test_full_evidence_graph_contains_only_valid_relationship():

    evidence = [
        database_timeout_evidence(),
        matching_commit_evidence(),
        unrelated_commit_evidence(),
        matching_deployment_evidence(),
    ]

    analyzer = EvidenceRelationshipAnalyzer()

    relationships = analyzer.analyze(evidence)

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship.relationship_type == "commit_deployed"

    assert relationship.source_evidence_id == 2
    assert relationship.target_evidence_id == 4

    assert relationship.source_evidence_id != 3
