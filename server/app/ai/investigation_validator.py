from app.schemas.ai_investigation import InvestigationResult, RootCauseStatus


class InvestigationValidator:
    def validate(self, result: InvestigationResult) -> InvestigationResult:

        if (
            result.root_cause_status == RootCauseStatus.CONFIRMED
            and not result.evidence
        ):
            self._mark_unknown(result)
            return result

        if result.root_cause_status == RootCauseStatus.UNKNOWN:
            self._validate_unknown(result)
        elif result.root_cause_status == RootCauseStatus.PROBABLE:
            self._validate_probable(result)
        elif result.root_cause_status == RootCauseStatus.CONFIRMED:
            self._validate_confirmed(result)

        return result

    def _validate_confirmed(
        self,
        result: InvestigationResult,
    ) -> None:

        directly_supported = any(
            assessment.is_direct and assessment.supports_root_cause
            for assessment in result.evidence_assessment
        )
        if directly_supported:
            result.confidence = max(result.confidence, 0.85)
            return

        indirectly_supported = any(
            assessment.supports_root_cause for assessment in result.evidence_assessment
        )
        if indirectly_supported:
            self._mark_probable(result)
            return

        self._mark_unknown(result)

    def _validate_probable(
        self,
        result: InvestigationResult,
    ) -> None:
        supported = any(
            assessment.supports_root_cause for assessment in result.evidence_assessment
        )

        if not supported:
            self._mark_unknown(result)
            return
        result.confidence = min(result.confidence, 0.84)

    def _validate_unknown(
        self,
        result: InvestigationResult,
    ) -> None:
        result.confidence = min(result.confidence, 0.49)

        result.likely_root_cause = "insufficient evidence to determine root cause"

    def _mark_probable(self, result: InvestigationResult) -> None:
        result.root_cause_status = RootCauseStatus.PROBABLE
        result.confidence = min(result.confidence, 0.84)
        if not result.unknowns:
            result.unknowns = []

        result.unknowns.append(
            "The evidence suggests the root cause."
            "but the casual relationship is not directly established"
        )

    def _mark_unknown(
        self,
        result: InvestigationResult,
    ) -> None:

        result.root_cause_status = RootCauseStatus.UNKNOWN
        result.likely_root_cause = "insufficient evidence to determine root cause"
        result.confidence = min(result.confidence, 0.49)

        result.unknowns.append(
            "the supplied evidence does not directly establish" "the root cause"
        )
