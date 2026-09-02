import json
from app.schemas.ai_investigation import InvestigationResult, AIInvestigationOutput
from app.schemas.investigation import InvestigationContext
from app.ai.base import LLMProvider
from app.ai.prompt_builder import InvestigationPromptBuilder
from pydantic import ValidationError
from app.ai.investigation_validator import InvestigationValidator


class AIInvestigatorService:

    def __init__(self, provider: LLMProvider, provider_name: str, model_name: str):

        self.provider = provider
        self.prompt_builder = InvestigationPromptBuilder()
        self.provider_name = provider_name
        self.model_name = model_name
        self.validator = InvestigationValidator()

    async def investigate(
        self,
        context: InvestigationContext,
    ) -> AIInvestigationOutput:

        prompt = self.prompt_builder.build(context)
        raw_response = await self.provider.generate(prompt)

        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise RuntimeError("AI provider returned invalid json") from exc

        try:
            result = InvestigationResult.model_validate(data)

        except ValidationError as exc:
            raise RuntimeError(f"AI response failed schema validation:{exc }") from exc

        result = self.validator.validate(result)

        return AIInvestigationOutput(prompt=prompt, result=result)
        # return InvestigationResult(
        #     summary=(
        #         f"Incident '{context.incident.title}' "
        #         f"is currently {context.incident.status.value}."
        #     ),
        #     likely_root_cause=(
        #         "Insufficient evidence for a reliable root-cause determination."
        #     ),
        #     evidence=[item.content for item in context.evidence],
        #     impact=context.incident.description,
        #     recommended_actions=[
        #         "Review available evidence.",
        #         "Inspect related application and infrastructure logs.",
        #         "Review recent changes before the incident.",
        #     ],
        #     confidence=0.2,
        # )
