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


class OllamaProvider(LLMProvider):

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama",
        )

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=settings.ollama_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if not content:
                raise AIInvalidResponseError(
                    provider="ollama",
                    cause=ValueError("Ollama returned an empty response"),
                )

            return content

        except AIInvestigationError:
            raise

        except APITimeoutError as exc:
            raise AIProviderTimeoutError(
                provider="ollama",
                cause=exc,
            ) from exc

        except (InternalServerError, APIConnectionError) as exc:
            raise AIProviderUnavailableError(
                provider="ollama",
                cause=exc,
            ) from exc
