"""
Tests for app/services/llm/factory.py.

These tests only verify dispatch logic (which provider class is instantiated
for a given LLM_PROVIDER value) and error handling for unknown providers /
missing credentials. No real network calls are made.
"""
from __future__ import annotations

import pytest

from app.services.llm.base import LLMProviderError
from app.services.llm.openrouter import OpenRouterLLMProvider
from app.services.llm.claude import ClaudeLLMProvider
from app.services.llm.factory import get_llm_provider


def test_factory_returns_openrouter_provider(monkeypatch):
    monkeypatch.setattr("app.services.llm.factory.settings.LLM_PROVIDER", "openrouter")
    monkeypatch.setattr("app.services.llm.openrouter.settings.OPENROUTER_API_KEY", "sk-or-test-key")

    provider = get_llm_provider()

    assert isinstance(provider, OpenRouterLLMProvider)


def test_factory_returns_openrouter_provider_case_insensitive(monkeypatch):
    monkeypatch.setattr("app.services.llm.factory.settings.LLM_PROVIDER", "OpenRouter")
    monkeypatch.setattr("app.services.llm.openrouter.settings.OPENROUTER_API_KEY", "sk-or-test-key")

    provider = get_llm_provider()

    assert isinstance(provider, OpenRouterLLMProvider)


def test_factory_returns_claude_provider_for_legacy_config(monkeypatch):
    monkeypatch.setattr("app.services.llm.factory.settings.LLM_PROVIDER", "claude")
    monkeypatch.setattr("app.services.llm.claude.settings.ANTHROPIC_API_KEY", "sk-ant-test-key")

    provider = get_llm_provider()

    assert isinstance(provider, ClaudeLLMProvider)


def test_factory_raises_for_unknown_provider(monkeypatch):
    monkeypatch.setattr("app.services.llm.factory.settings.LLM_PROVIDER", "gemini-direct")

    with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
        get_llm_provider()


def test_factory_raises_llm_provider_error_when_openrouter_key_missing(monkeypatch):
    monkeypatch.setattr("app.services.llm.factory.settings.LLM_PROVIDER", "openrouter")
    monkeypatch.setattr("app.services.llm.openrouter.settings.OPENROUTER_API_KEY", None)

    with pytest.raises(LLMProviderError, match="OPENROUTER_API_KEY"):
        get_llm_provider()
