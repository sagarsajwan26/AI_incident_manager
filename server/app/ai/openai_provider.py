from openai import (
    AsyncOpenAI,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)

from app.ai.base import LLMProvider
from app.ai.exceptions import (
    AIInvestigationError,
    AIInvalidResponseError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.core.config import settings


class OpenAIProvider(LLMProvider):

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.responses.create(
                model=settings.openai_model,
                input=prompt,
            )

            response_text = response.output_text

            if not response_text:
                raise AIInvalidResponseError(
                    provider="openai",
                    cause=ValueError("OpenAI returned an empty response"),
                )

            return response_text

        except AIInvestigationError:
            raise

        except APITimeoutError as exc:
            raise AIProviderTimeoutError(
                provider="openai",
                cause=exc,
            ) from exc

        except (APIConnectionError, InternalServerError) as exc:
            raise AIProviderUnavailableError(
                provider="openai",
                cause=exc,
            ) from exc
