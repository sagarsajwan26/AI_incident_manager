from openai import AsyncOpenAI

from app.ai.base import LLMProvider
from app.core.config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.responses.create(
                model=settings.openai_model, input=prompt
            )
            response_text = response.output_text

            if not response_text:
                raise AIInvalidResponseError(provider="openai", cause=Exception("empty response"))
            return response_text
        except Exception as exc:
            raise AIProviderError(provider="openai", cause=exc) from exc
