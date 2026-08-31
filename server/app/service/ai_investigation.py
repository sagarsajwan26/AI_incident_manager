import json
from app.schemas.ai_investigation import InvestigationResult, AIInvestigationOutput
from app.schemas.investigation import InvestigationContext
from app.ai.base import LLMProvider
from app.ai.prompt_builder import InvestigationPromptBuilder
from pydantic import ValidationError
from app.ai.investigation_validator import InvestigationValidator


class AIInvestigatorService:

    def __init__(self, provider: LLMProvider):

        self.provider = provider
        self.prompt_builder = InvestigationPromptBuilder()
        self.validator = InvestigationValidator()

    async def investigate(
        self,
        context: InvestigationContext,
    ) -> InvestigationResult:

        prompt = self.prompt_builder.build(context)
        raw_response = await self.provider.generate(prompt)

        try:
            data = json.loads(raw_response)

        except json.JSONDecodeError as exc:
            raise RuntimeError("LLM returned invalid JSON") from exc
        # Conservative fallback when the model omits the
        # root cause classification.
        if "root_cause_status" not in data:
            data["root_cause_status"] = "unknown"

        if "unknowns" not in data:
            data["unknowns"] = ["The model did not provide explicit unknowns."]

        try:
            result = InvestigationResult.model_validate(data)
        except ValidationError as exc:
            raise RuntimeError(
                f"LLM response does not match InvestigationResult scheme:{exc}"
            ) from exc
        return self.validator.validate(result)
