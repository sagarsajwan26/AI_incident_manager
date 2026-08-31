from app.schemas.ai_investigation import InvestigationResult


class InvestigationValidator:
    def validate(self, result: InvestigationResult) -> InvestigationResult:

        if result.root_cause_status == "confirmed" and not result.evidence:
            result.root_cause_status = "unknown"
            result.likely_root_cause = "insufficient evidence to determine root cause"
            result.confidence = min(result.confidence, 0.3)
        return result
