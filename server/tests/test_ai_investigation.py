from app.core.config import settings
import json
from datetime import datetime, timezone

import pytest

from app.service.ai_investigation import AIInvestigatorService
from app.ai.base import LLMProvider
from app.schemas.investigation import InvestigationContext
from app.schemas.incident import IncidentResponse


CREATED_AT = datetime(
    2026,
    2,
    27,
    11,
    9,
    43,
    tzinfo=timezone.utc,
)


def create_context() -> InvestigationContext:

    incident = IncidentResponse(
        id=4,
        tenant_id=8,
        title="Database connection timeout",
        description="Production database connections are timing out.",
        status="open",
        severity="high",
        reported_by=1,
        assigned_to=None,
        created_at=CREATED_AT,
        updated_at=CREATED_AT,
    )

    return InvestigationContext(
        incident=incident,
        comments=[],
        evidence=[],
        audit_history=[],
        evidence_relationships=[],
    )


class FakeLLMProvider(LLMProvider):

    def __init__(self, response: str):
        self.response = response
        self.received_prompt = None

    async def generate(self, prompt: str) -> str:
        self.received_prompt = prompt
        return self.response


def valid_ai_response():

    return {
        "summary": "A database connection timeout was recorded.",
        "likely_root_cause": "Insufficient evidence to determine root cause.",
        "root_cause_status": "unknown",
        "evidence": [
            "A database connection timeout after 30 seconds was recorded."
        ],
        "evidence_assessment": [
            {
                "claim": "A database connection timeout occurred.",
                "support": "The incident evidence explicitly records the timeout.",
                "supports_root_cause": False,
                "support_level": "direct",
            }
        ],
        "impact": "The affected system may experience failed requests.",
        "recommended_actions": [
            "Review application logs around the incident."
        ],
        "unknowns": [
            "The supplied evidence does not establish the root cause."
        ],
        "confidence": 0.4,
    }


@pytest.mark.asyncio
async def test_valid_ai_response_returns_investigation_output():

    provider = FakeLLMProvider(
        json.dumps(valid_ai_response())
    )

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="fake-model",
    )

    result = await service.investigate(
        create_context()
    )

    assert result.result.root_cause_status.value == "unknown"
    assert result.result.confidence <= 0.49
    assert result.prompt
    assert provider.received_prompt == result.prompt


@pytest.mark.asyncio
async def test_invalid_json_raises_runtime_error():

    provider = FakeLLMProvider(
        "this is not valid json"
    )

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="fake-model",
    )

    from app.ai.exceptions import AIInvalidResponseError
    with pytest.raises(AIInvalidResponseError):
        await service.investigate(
            create_context()
        )


@pytest.mark.asyncio
async def test_invalid_schema_raises_runtime_error():

    invalid_response = {
        "summary": "Something happened.",
        "root_cause_status": "unknown",
    }

    provider = FakeLLMProvider(
        json.dumps(invalid_response)
    )

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="fake-model",
    )

    from app.ai.exceptions import AIInvalidResponseError
    with pytest.raises(AIInvalidResponseError):
        await service.investigate(
            create_context()
        )


@pytest.mark.asyncio
async def test_validator_is_invoked():

    response = valid_ai_response()

    response["root_cause_status"] = "confirmed"

    response["likely_root_cause"] = (
        "Database connection timeout was caused by an unknown change."
    )

    response["evidence_assessment"] = [
        {
            "claim": "The deployment caused the timeout.",
            "support": "The available evidence suggests a possible relationship.",
            "supports_root_cause": True,
            "support_level": "inferred",
        }
    ]

    provider = FakeLLMProvider(
        json.dumps(response)
    )

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="fake-model",
    )

    result = await service.investigate(
        create_context()
    )

    assert result.result.root_cause_status.value == "probable"
    assert result.result.confidence <= 0.84


@pytest.mark.asyncio
async def test_prompt_builder_output_is_sent_to_provider():

    provider = FakeLLMProvider(
        json.dumps(valid_ai_response())
    )

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="fake-model",
    )

    result = await service.investigate(
        create_context()
    )

    assert provider.received_prompt is not None
    assert provider.received_prompt == result.prompt
    assert "Database connection timeout" in provider.received_prompt


@pytest.mark.asyncio
async def test_provider_failure_propagates():

    class FailingProvider(LLMProvider):

        async def generate(self, prompt: str) -> str:
            raise RuntimeError("LLM provider unavailable")

    provider = FailingProvider()

    service = AIInvestigatorService(
        provider=provider,
        provider_name="fake",
        model_name="fake-model",
    )

    with pytest.raises(
        RuntimeError,
        match="LLM provider unavailable",
    ):
        await service.investigate(
            create_context()
        )


from unittest.mock import AsyncMock
import httpx

from openai import APITimeoutError, APIConnectionError, InternalServerError

from app.ai.exceptions import (
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.ai.ollama_provider import OllamaProvider
from app.ai.openai_provider import OpenAIProvider


def create_mock_response():
    request = httpx.Request("POST", "http://test")
    return httpx.Response(status_code=500, request=request)


@pytest.mark.asyncio
async def test_ollama_provider_maps_timeout_to_ai_timeout():
    provider = OllamaProvider()
    provider.client.chat.completions.create = AsyncMock(
        side_effect=APITimeoutError(request=None)
    )

    with pytest.raises(AIProviderTimeoutError):
        await provider.generate("test prompt")


@pytest.mark.asyncio
async def test_ollama_provider_maps_connection_error_to_ai_unavailable():
    provider = OllamaProvider()
    provider.client.chat.completions.create = AsyncMock(
        side_effect=APIConnectionError(request=None)
    )

    with pytest.raises(AIProviderUnavailableError):
        await provider.generate("test prompt")


@pytest.mark.asyncio
async def test_ollama_provider_maps_internal_server_error_to_ai_unavailable():
    provider = OllamaProvider()
    provider.client.chat.completions.create = AsyncMock(
        side_effect=InternalServerError(
            message="server error",
            response=create_mock_response(),
            body=None,
        )
    )

    with pytest.raises(AIProviderUnavailableError):
        await provider.generate("test prompt")


@pytest.mark.asyncio
async def test_openai_provider_maps_timeout_to_ai_timeout():
    settings.openai_api_key = 'fake'
    provider = OpenAIProvider()
    provider.client.responses.create = AsyncMock(
        side_effect=APITimeoutError(request=None)
    )

    with pytest.raises(AIProviderTimeoutError):
        await provider.generate("test prompt")


@pytest.mark.asyncio
async def test_openai_provider_maps_connection_error_to_ai_unavailable():
    settings.openai_api_key = 'fake'
    provider = OpenAIProvider()
    provider.client.responses.create = AsyncMock(
        side_effect=APIConnectionError(request=None)
    )

    with pytest.raises(AIProviderUnavailableError):
        await provider.generate("test prompt")


@pytest.mark.asyncio
async def test_openai_provider_maps_internal_server_error_to_ai_unavailable():
    settings.openai_api_key = 'fake'
    provider = OpenAIProvider()
    provider.client.responses.create = AsyncMock(
        side_effect=InternalServerError(
            message="server error",
            response=create_mock_response(),
            body=None,
        )
    )

    with pytest.raises(AIProviderUnavailableError):
        await provider.generate("test prompt")
