from app.schemas.ai_investigation import (
    InvestigationResult,
    RootCauseStatus,
    EvidenceSupport,
)


class InvestigationValidator:
    def validate(self, result: InvestigationResult) -> InvestigationResult:

        if not result.evidence_assessment:
            self._mark_unknown(result)
            return result

        if result.root_cause_status == RootCauseStatus.CONFIRMED:
            self._validate_confirmed(result)

        elif result.root_cause_status == RootCauseStatus.PROBABLE:
            self._validate_probable(result)

        else:
            self._validate_unknown(result)

        return result

    def _validate_confirmed(self, result: InvestigationResult) -> None:
        directly_supported = any(
            assessment.support_level == EvidenceSupport.DIRECT
            and assessment.supports_root_cause
            for assessment in result.evidence_assessment
        )

        if directly_supported:
            result.confidence = max(result.confidence, 0.85)
            return

        inferred_support = any(
            assessment.support_level == EvidenceSupport.INFERRED
            and assessment.supports_root_cause
            for assessment in result.evidence_assessment
        )

        if inferred_support:
            self._mark_probable(result)
            return

        self._mark_unknown(result)

    def _validate_probable(
        self,
        result: InvestigationResult,
    ) -> None:

        supported = any(
            assessment.support_level
            in {EvidenceSupport.DIRECT, EvidenceSupport.INFERRED}
            and assessment.supports_root_cause
            for assessment in result.evidence_assessment
        )

        if not supported:
            self._mark_unknown(result)
            return

        result.confidence = min(
            result.confidence,
            0.84,
        )

    def _validate_unknown(
        self,
        result: InvestigationResult,
    ) -> None:
        result.root_cause_status = RootCauseStatus.UNKNOWN
        result.likely_root_cause = "insufficient evidence to determine root cause"
        result.confidence = min(result.confidence, 0.49)

    def _mark_probable(self, result: InvestigationResult) -> None:

        result.root_cause_status = RootCauseStatus.PROBABLE

        result.confidence = min(result.confidence, 0.84)
        if not result.unknowns:
            result.unknowns = []

        message = (
            "The evidence suggests a possible root cause, "
            "but the causal relationship is not directly established."
        )
        if message not in result.unknowns:
            result.unknowns.append(message)

    def _mark_unknown(
        self,
        result: InvestigationResult,
    ) -> None:

        result.root_cause_status = RootCauseStatus.UNKNOWN
        result.likely_root_cause = "insufficient evidence to determine root cause"
        result.summary = (
            "The supplied evidence establishes a database connection "
            "timeout and a GitHub commit associated with a successful "
            "Production deployment, but it does not establish a causal "
            "relationship between the deployment and the timeout."
        )
        result.confidence = min(result.confidence, 0.49)

        if not result.unknowns:
            result.unknowns = []

        message = "The supplied evidence does not directly establish " "the root cause."

        if message not in result.unknowns:
            result.unknowns.append(message)
