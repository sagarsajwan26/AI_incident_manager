from app.schemas.ai_investigation import InvestigationResult, RootCauseStatus


class InvestigationValidator:
    def validate(self, result: InvestigationResult) -> InvestigationResult:

        if (
            result.root_cause_status == RootCauseStatus.CONFIRMED
            and not result.evidence
        ):
            result.root_cause_status = "unknown"
            result.likely_root_cause = "Insufficient evidence to determine root cause."

            result.confidence = min(result.confidence, 0.3)
        if result.root_cause_status == RootCauseStatus.UNKNOWN:
            result.confidence = min(result.confidence, 0.4)

        if result.root_cause_status == RootCauseStatus.PROBABLE:
            result.confidence = min(result.confidence, 0.8)

        return result
