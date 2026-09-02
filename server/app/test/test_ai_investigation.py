import pytest

from app.service.ai_investigation import AIInvestigatorService
from app.schemas.ai_investigation import RootCauseStatus


class FakeLLMProvider:

    async def generate(self, prompt: str) -> str:
        return """
        {
            "summary": "The database timeout caused the testing deletion.",
            "likely_root_cause": "Database timeout caused testing deletion.",
            "root_cause_status": "confirmed",
            "evidence": [
                "ERROR database connection timeout after 30 seconds"
            ],
            "evidence_assessment": [
                {
                    "claim": "The database timeout caused the testing deletion.",
                    "support": "The timeout occurred before the deletion.",
                    "is_direct": false,
                    "supports_root_cause": true
                }
            ],
            "impact": "Testing may have been deleted.",
            "recommended_actions": [
                "Review database logs."
            ],
            "unknowns": [],
            "confidence": 0.95
        }
        """


class FakePromptBuilder:

    def build(self, context):
        return "test prompt"


class FakeContext:
    pass


@pytest.mark.asyncio
async def test_service_downgrades_unsupported_confirmed_root_cause():
    provider = FakeLLMProvider()

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="test-model",
    )

    service.prompt_builder = FakePromptBuilder()

    result = await service.investigate(FakeContext())

    assert result.result.root_cause_status == RootCauseStatus.PROBABLE
    assert result.result.confidence <= 0.84
