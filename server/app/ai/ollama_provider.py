import httpx
from app.ai.base import LLMProvider
from app.core.config import settings


class OllamaProvider(LLMProvider):
    async def generate(self, prompt: str) -> str:
        url = f"{settings.ollama_base_url}/api/generate"
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
                response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response")

            if not response_text:
                raise RuntimeError("ollama returend an empty response ")

            return response_text
        except httpx.HTTPError as exc:
            raise RuntimeError(f"ollama request failed:{exc}") from exc
