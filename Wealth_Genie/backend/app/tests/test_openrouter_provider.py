"""
Tests for app/services/llm/openrouter.py.

All OpenAI SDK calls are mocked — no real network requests are made to
OpenRouter. These tests verify:
  - successful extraction returns parsed JSON
  - markdown-fenced JSON responses are still parsed correctly
  - malformed JSON raises LLMProviderError
  - empty response raises LLMProviderError
  - missing API key raises LLMProviderError at construction time
  - HTTP/SDK failures (401, 403, 429, 500, timeout, network error) are mapped
    onto LLMProviderError rather than leaking raw SDK/HTTP exceptions
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import openai
import pytest

from app.services.llm.base import LLMProviderError
from app.services.llm.openrouter import OpenRouterLLMProvider


def _make_chat_response(content: str):
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


def _make_provider(monkeypatch, api_key: str | None = "sk-or-test-key"):
    monkeypatch.setattr("app.services.llm.openrouter.settings.OPENROUTER_API_KEY", api_key)
    monkeypatch.setattr("app.services.llm.openrouter.settings.LLM_MODEL", "google/gemini-2.5-flash")
    return OpenRouterLLMProvider()


@pytest.mark.asyncio
async def test_missing_api_key_raises_llm_provider_error(monkeypatch):
    monkeypatch.setattr("app.services.llm.openrouter.settings.OPENROUTER_API_KEY", None)

    with pytest.raises(LLMProviderError, match="OPENROUTER_API_KEY"):
        OpenRouterLLMProvider()


@pytest.mark.asyncio
async def test_successful_extraction_returns_parsed_json(monkeypatch):
    provider = _make_provider(monkeypatch)
    fake_payload = '{"summary": {"total_monthly_income": 6000}}'
    provider._client.chat.completions.create = AsyncMock(
        return_value=_make_chat_response(fake_payload)
    )

    result = await provider.extract_financial_json(
        normalized_text="Net Pay: 6000.00", document_type="salary_slip"
    )

    assert result == {"summary": {"total_monthly_income": 6000}}
    provider._client.chat.completions.create.assert_awaited_once()
    call_kwargs = provider._client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "google/gemini-2.5-flash"


@pytest.mark.asyncio
async def test_strips_markdown_fences_before_parsing(monkeypatch):
    provider = _make_provider(monkeypatch)
    fenced_payload = '```json\n{"accounts": []}\n```'
    provider._client.chat.completions.create = AsyncMock(
        return_value=_make_chat_response(fenced_payload)
    )

    result = await provider.extract_financial_json("some text", "bank_statement")

    assert result == {"accounts": []}


@pytest.mark.asyncio
async def test_malformed_json_raises_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        return_value=_make_chat_response("not valid json at all")
    )

    with pytest.raises(LLMProviderError, match="did not return valid JSON"):
        await provider.extract_financial_json("some text", "loan")


@pytest.mark.asyncio
async def test_empty_response_raises_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        return_value=_make_chat_response("")
    )

    with pytest.raises(LLMProviderError, match="empty response"):
        await provider.extract_financial_json("some text", "credit_card")


@pytest.mark.asyncio
async def test_authentication_error_maps_to_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        side_effect=openai.AuthenticationError(
            message="invalid api key",
            response=SimpleNamespace(status_code=401, headers={}, request=SimpleNamespace()),
            body=None,
        )
    )

    with pytest.raises(LLMProviderError, match="authentication failed"):
        await provider.extract_financial_json("text", "bank_statement")


@pytest.mark.asyncio
async def test_permission_denied_error_maps_to_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        side_effect=openai.PermissionDeniedError(
            message="forbidden",
            response=SimpleNamespace(status_code=403, headers={}, request=SimpleNamespace()),
            body=None,
        )
    )

    with pytest.raises(LLMProviderError, match="denied access"):
        await provider.extract_financial_json("text", "bank_statement")


@pytest.mark.asyncio
async def test_rate_limit_error_maps_to_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        side_effect=openai.RateLimitError(
            message="rate limited",
            response=SimpleNamespace(status_code=429, headers={}, request=SimpleNamespace()),
            body=None,
        )
    )

    with pytest.raises(LLMProviderError, match="rate limit"):
        await provider.extract_financial_json("text", "bank_statement")


@pytest.mark.asyncio
async def test_internal_server_error_maps_to_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        side_effect=openai.InternalServerError(
            message="server error",
            response=SimpleNamespace(status_code=500, headers={}, request=SimpleNamespace()),
            body=None,
        )
    )

    with pytest.raises(LLMProviderError, match="status 500"):
        await provider.extract_financial_json("text", "bank_statement")


@pytest.mark.asyncio
async def test_timeout_error_maps_to_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        side_effect=openai.APITimeoutError(request=SimpleNamespace())
    )

    with pytest.raises(LLMProviderError, match="timed out"):
        await provider.extract_financial_json("text", "bank_statement")


@pytest.mark.asyncio
async def test_connection_error_maps_to_llm_provider_error(monkeypatch):
    provider = _make_provider(monkeypatch)
    provider._client.chat.completions.create = AsyncMock(
        side_effect=openai.APIConnectionError(request=SimpleNamespace())
    )

    with pytest.raises(LLMProviderError, match="network error"):
        await provider.extract_financial_json("text", "bank_statement")
