from datetime import datetime, timezone

from app.ai.evidence_relationship_analyzer import EvidenceRelationshipAnalyzer
from app.schemas.incident_evidence import IncidentEvidenceResponse


def test_matching_commit_and_deployment_create_relationship():

    analyzer = EvidenceRelationshipAnalyzer()

    created_at = datetime(
        2026,
        2,
        27,
        11,
        9,
        43,
        tzinfo=timezone.utc,
    )

    commit = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    deployment = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    relationships = analyzer.analyze(
        [commit, deployment]
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship.source_evidence_id == 2
    assert relationship.target_evidence_id == 4
    assert relationship.relationship_type == "commit_deployed"


def test_different_sha_does_not_create_relationship():

    analyzer = EvidenceRelationshipAnalyzer()

    created_at = datetime(
        2026,
        2,
        27,
        11,
        9,
        43,
        tzinfo=timezone.utc,
    )

    commit = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    deployment = IncidentEvidenceResponse(
        id=4,
        incident_id=4,
        tenant_id=8,
        added_by=1,
        evidence_type="deployment",
        content="""{
            "source": "github",
            "type": "deployment",
            "deployment_id": 3939625728,
            "sha": "different-sha",
            "repository": "sagarsajwan79/darkx",
            "environment": "Production",
            "status": "success"
        }""",
        source="github",
        external_id="deployment:3939625728",
        created_at=created_at,
    )

    relationships = analyzer.analyze(
        [commit, deployment]
    )

    assert relationships == []


def test_same_sha_different_repository_does_not_create_relationship():

    analyzer = EvidenceRelationshipAnalyzer()

    created_at = datetime(
        2026,
        2,
        27,
        11,
        9,
        43,
        tzinfo=timezone.utc,
    )

    commit = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    deployment = IncidentEvidenceResponse(
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
            "repository": "another-owner/another-repository",
            "environment": "Production",
            "status": "success"
        }""",
        source="github",
        external_id="deployment:3939625728",
        created_at=created_at,
    )

    relationships = analyzer.analyze(
        [commit, deployment]
    )

    assert relationships == []


def test_reverse_evidence_ordering_creates_relationship():

    analyzer = EvidenceRelationshipAnalyzer()

    created_at = datetime(
        2026,
        2,
        27,
        11,
        9,
        43,
        tzinfo=timezone.utc,
    )

    commit = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    deployment = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    relationships = analyzer.analyze(
        [deployment, commit]
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship.source_evidence_id == 2
    assert relationship.target_evidence_id == 4
    assert relationship.relationship_type == "commit_deployed"


def test_non_github_evidence_does_not_create_relationship():

    analyzer = EvidenceRelationshipAnalyzer()

    created_at = datetime(
        2026,
        2,
        27,
        11,
        9,
        43,
        tzinfo=timezone.utc,
    )

    commit = IncidentEvidenceResponse(
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
        created_at=created_at,
    )

    deployment = IncidentEvidenceResponse(
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
        source="manual",
        external_id="deployment:3939625728",
        created_at=created_at,
    )

    relationships = analyzer.analyze(
        [commit, deployment]
    )

    assert relationships == []


def test_malformed_evidence_content_does_not_create_relationship():

    analyzer = EvidenceRelationshipAnalyzer()

    created_at = datetime(
        2026,
        2,
        27,
        11,
        9,
        43,
        tzinfo=timezone.utc,
    )

    commit = IncidentEvidenceResponse(
        id=2,
        incident_id=4,
        tenant_id=8,
        added_by=1,
        evidence_type="commit",
        content="this is malformed commit evidence",
        source="github",
        external_id="malformed-commit",
        created_at=created_at,
    )

    deployment = IncidentEvidenceResponse(
        id=4,
        incident_id=4,
        tenant_id=8,
        added_by=1,
        evidence_type="deployment",
        content="this is malformed deployment evidence",
        source="github",
        external_id="malformed-deployment",
        created_at=created_at,
    )

    relationships = analyzer.analyze(
        [commit, deployment]
    )

    assert relationships == []
