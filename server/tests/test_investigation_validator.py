import pytest
from app.ai.investigation_validator import InvestigationValidator
from app.schemas.ai_investigation import (
    InvestigationResult,
    RootCauseStatus,
    EvidenceSupport,
    EvidenceAssessment,
)


@pytest.fixture
def validator():
    return InvestigationValidator()


def create_base_result(status: RootCauseStatus, evidence_assessment: list[EvidenceAssessment], confidence: float = 0.9):
    return InvestigationResult(
        summary="Test summary",
        likely_root_cause="Test root cause",
        root_cause_status=status,
        evidence=["test evidence"],
        evidence_assessment=evidence_assessment,
        impact="Test impact",
        recommended_actions=["test action"],
        unknowns=[],
        confidence=confidence
    )


# 1. confirmed + direct      → confirmed
def test_confirmed_with_direct_support(validator):
    assessment = [
        EvidenceAssessment(
            claim="Deployment caused the incident.",
            support="Logs explicitly show it.",
            supports_root_cause=True,
            support_level=EvidenceSupport.DIRECT,
        )
    ]
    result = create_base_result(RootCauseStatus.CONFIRMED, assessment, confidence=0.7)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.CONFIRMED
    assert validated.confidence >= 0.85


# 2. confirmed + inferred    → probable
def test_confirmed_with_inferred_support(validator):
    assessment = [
        EvidenceAssessment(
            claim="Deployment caused the incident.",
            support="Traffic dropped right after.",
            supports_root_cause=True,
            support_level=EvidenceSupport.INFERRED,
        )
    ]
    result = create_base_result(RootCauseStatus.CONFIRMED, assessment, confidence=0.9)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.PROBABLE
    assert validated.confidence <= 0.84


# 3. confirmed + unsupported → unknown
def test_confirmed_with_unsupported_evidence(validator):
    assessment = [
        EvidenceAssessment(
            claim="Deployment caused the incident.",
            support="No evidence found.",
            supports_root_cause=False,
            support_level=EvidenceSupport.UNSUPPORTED,
        )
    ]
    result = create_base_result(RootCauseStatus.CONFIRMED, assessment, confidence=0.9)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.UNKNOWN
    assert validated.confidence <= 0.49


# 4. probable + direct       → probable
def test_probable_with_direct_support(validator):
    assessment = [
        EvidenceAssessment(
            claim="Deployment likely caused the incident.",
            support="Logs explicitly show it.",
            supports_root_cause=True,
            support_level=EvidenceSupport.DIRECT,
        )
    ]
    result = create_base_result(RootCauseStatus.PROBABLE, assessment, confidence=0.9)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.PROBABLE
    assert validated.confidence <= 0.84


# 5. probable + inferred     → probable
def test_probable_with_inferred_support(validator):
    assessment = [
        EvidenceAssessment(
            claim="Deployment likely caused the incident.",
            support="Traffic dropped.",
            supports_root_cause=True,
            support_level=EvidenceSupport.INFERRED,
        )
    ]
    result = create_base_result(RootCauseStatus.PROBABLE, assessment, confidence=0.9)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.PROBABLE
    assert validated.confidence <= 0.84


# 6. probable + unsupported  → unknown
def test_probable_with_unsupported_evidence(validator):
    assessment = [
        EvidenceAssessment(
            claim="Deployment likely caused the incident.",
            support="No evidence.",
            supports_root_cause=False,
            support_level=EvidenceSupport.UNSUPPORTED,
        )
    ]
    result = create_base_result(RootCauseStatus.PROBABLE, assessment, confidence=0.7)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.UNKNOWN
    assert validated.confidence <= 0.49


# 7. unknown                 → unknown
def test_unknown_stays_unknown(validator):
    assessment = [
        EvidenceAssessment(
            claim="Not sure what happened.",
            support="Logs are missing.",
            supports_root_cause=False,
            support_level=EvidenceSupport.UNSUPPORTED,
        )
    ]
    result = create_base_result(RootCauseStatus.UNKNOWN, assessment, confidence=0.95)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.UNKNOWN
    assert validated.confidence <= 0.49
    assert validated.likely_root_cause == "insufficient evidence to determine root cause"


# 8. empty assessment        → unknown
def test_empty_assessment_becomes_unknown(validator):
    result = create_base_result(RootCauseStatus.CONFIRMED, [], confidence=0.9)
    validated = validator.validate(result)
    
    assert validated.root_cause_status == RootCauseStatus.UNKNOWN
    assert validated.confidence <= 0.49
