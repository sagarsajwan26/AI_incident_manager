import pytest
from app.schemas.ai_investigation import (
    InvestigationResult,
    RootCauseStatus,
    EvidenceSupport,
    EvidenceAssessment,
)
from app.ai.investigation_validator import InvestigationValidator


@pytest.fixture
def base_result():
    return InvestigationResult(
        summary="Test summary",
        likely_root_cause="Test root cause",
        root_cause_status=RootCauseStatus.CONFIRMED,
        evidence=[],
        evidence_assessment=[],
        impact="Test impact",
        recommended_actions=[],
        unknowns=[],
        confidence=0.96, # Starting with a high confidence to test clamping
    )

def test_confirmed_direct_support(base_result):
    validator = InvestigationValidator()
    base_result.root_cause_status = RootCauseStatus.CONFIRMED
    base_result.confidence = 0.50 # Low confidence to test it being bumped
    base_result.evidence_assessment = [
        EvidenceAssessment(
            claim="Claim",
            support="Support",
            supports_root_cause=True,
            support_level=EvidenceSupport.DIRECT
        )
    ]
    
    result = validator.validate(base_result)
    
    assert result.root_cause_status == RootCauseStatus.CONFIRMED
    assert result.confidence >= 0.85

def test_confirmed_inferred_support(base_result):
    validator = InvestigationValidator()
    base_result.root_cause_status = RootCauseStatus.CONFIRMED
    base_result.evidence_assessment = [
        EvidenceAssessment(
            claim="Claim",
            support="Support",
            supports_root_cause=True,
            support_level=EvidenceSupport.INFERRED
        )
    ]
    
    result = validator.validate(base_result)
    
    assert result.root_cause_status == RootCauseStatus.PROBABLE
    assert result.confidence <= 0.84

def test_confirmed_no_support(base_result):
    validator = InvestigationValidator()
    base_result.root_cause_status = RootCauseStatus.CONFIRMED
    base_result.evidence_assessment = [
        EvidenceAssessment(
            claim="Claim",
            support="Support",
            supports_root_cause=False,
            support_level=EvidenceSupport.DIRECT
        ),
        EvidenceAssessment(
            claim="Claim 2",
            support="Support 2",
            supports_root_cause=True,
            support_level=EvidenceSupport.UNSUPPORTED
        )
    ]
    
    result = validator.validate(base_result)
    
    assert result.root_cause_status == RootCauseStatus.UNKNOWN
    assert result.confidence <= 0.49
    assert result.likely_root_cause == "Insufficient evidence to determine root cause."

def test_probable_direct_or_inferred_support(base_result):
    validator = InvestigationValidator()
    base_result.root_cause_status = RootCauseStatus.PROBABLE
    base_result.confidence = 0.96
    base_result.evidence_assessment = [
        EvidenceAssessment(
            claim="Claim",
            support="Support",
            supports_root_cause=True,
            support_level=EvidenceSupport.INFERRED
        )
    ]
    
    result = validator.validate(base_result)
    
    assert result.root_cause_status == RootCauseStatus.PROBABLE
    assert result.confidence <= 0.84

def test_probable_no_support(base_result):
    validator = InvestigationValidator()
    base_result.root_cause_status = RootCauseStatus.PROBABLE
    base_result.evidence_assessment = [
        EvidenceAssessment(
            claim="Claim",
            support="Support",
            supports_root_cause=False,
            support_level=EvidenceSupport.INFERRED
        )
    ]
    
    result = validator.validate(base_result)
    
    assert result.root_cause_status == RootCauseStatus.UNKNOWN
    assert result.confidence <= 0.49
    assert result.likely_root_cause == "Insufficient evidence to determine root cause."

def test_unknown(base_result):
    validator = InvestigationValidator()
    base_result.root_cause_status = RootCauseStatus.UNKNOWN
    base_result.evidence_assessment = [
        EvidenceAssessment(
            claim="Claim",
            support="Support",
            supports_root_cause=False,
            support_level=EvidenceSupport.UNSUPPORTED
        )
    ]
    
    result = validator.validate(base_result)
    
    assert result.root_cause_status == RootCauseStatus.UNKNOWN
    assert result.confidence <= 0.49
    assert result.likely_root_cause == "Insufficient evidence to determine root cause."
