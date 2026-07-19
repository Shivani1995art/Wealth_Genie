"""
OpenRouter implementation of LLMProvider.

This is the only file in the codebase permitted to import the `openai` SDK
(used here purely as an OpenAI-compatible HTTP client pointed at OpenRouter's
Chat Completions endpoint). Everything else talks to `LLMProvider` (base.py).

OpenRouter proxies many underlying models (Gemini, Llama, Claude, GPT, etc.)
behind a single OpenAI-compatible API, so the same client works regardless of
which model string is configured via LLM_MODEL.
"""
from __future__ import annotations

import json
import re

import openai

from app.config import settings
from app.services.llm.base import LLMProvider, LLMProviderError

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_EXTRACTION_SYSTEM_PROMPT = """You are a deterministic financial document structuring \
engine. You convert normalized financial-document text into a single JSON object \
matching an exact schema. You NEVER invent values that are not present in the source \
text. Any field you cannot find must be omitted or left as null/empty, never guessed.

Respond with JSON ONLY. No prose, no markdown code fences, no explanations.

Schema (top-level keys, all required, unknown sub-fields may be omitted):
{
  "user": {"id": null, "name": null, "email": null},
  "accounts": [{"account_id": "", "bank_name": "", "account_type": "savings|current|salary",
                "currency": "", "opening_balance": 0, "closing_balance": 0,
                "statement_period_start": "YYYY-MM-DD", "statement_period_end": "YYYY-MM-DD"}],
  "transactions": [{"transaction_id": "", "account_id": "", "date": "YYYY-MM-DD",
                     "description": "", "amount": 0, "type": "credit|debit", "category": ""}],
  "loans": [{"loan_id": "", "lender": "", "loan_type": "home|personal|auto|education|other",
             "principal": 0, "outstanding_balance": 0, "interest_rate": 0, "emi": 0,
             "tenure_remaining_months": 0}],
  "credit_cards": [{"card_id": "", "issuer": "", "credit_limit": 0, "outstanding_balance": 0,
                     "minimum_due": 0, "due_date": "YYYY-MM-DD", "interest_rate": 0}],
  "summary": {"total_monthly_income": 0, "total_monthly_expenses": 0, "total_debt": 0,
              "total_savings": 0, "net_worth_estimate": 0, "savings_rate_percent": 0},
  "recommendations": []
}

The document_type hint tells you what kind of document this is, which sections are
most likely to be populated (e.g. salary_slip -> summary.total_monthly_income and
possibly one transaction; bank_statement -> accounts + transactions; credit_card ->
credit_cards; loan -> loans). Do not force-populate sections irrelevant to the
document type."""


class OpenRouterLLMProvider(LLMProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        resolved_key = api_key or settings.OPENROUTER_API_KEY
        if not resolved_key:
            raise LLMProviderError(
                "OPENROUTER_API_KEY is not set. Configure it in the environment "
                "(see .env.example) before using the openrouter LLM provider."
            )

        self._client = openai.AsyncOpenAI(
            api_key=resolved_key,
            base_url=_OPENROUTER_BASE_URL,
        )
        self._model = model or settings.LLM_MODEL

    async def extract_financial_json(self, normalized_text: str, document_type: str) -> dict:
        user_message = (
            f"document_type: {document_type}\n\n"
            f"--- BEGIN DOCUMENT TEXT ---\n{normalized_text}\n--- END DOCUMENT TEXT ---"
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )
        except openai.AuthenticationError as exc:
            raise LLMProviderError(
                f"OpenRouter authentication failed (invalid or missing OPENROUTER_API_KEY): {exc}"
            ) from exc
        except openai.PermissionDeniedError as exc:
            raise LLMProviderError(
                f"OpenRouter denied access to model '{self._model}': {exc}"
            ) from exc
        except openai.RateLimitError as exc:
            raise LLMProviderError(f"OpenRouter rate limit exceeded: {exc}") from exc
        except openai.APITimeoutError as exc:
            raise LLMProviderError(f"OpenRouter request timed out: {exc}") from exc
        except openai.APIConnectionError as exc:
            raise LLMProviderError(f"Could not reach OpenRouter (network error): {exc}") from exc
        except openai.APIStatusError as exc:
            raise LLMProviderError(
                f"OpenRouter returned an error (status {exc.status_code}): {exc}"
            ) from exc
        except openai.APIError as exc:
            raise LLMProviderError(f"OpenRouter request failed: {exc}") from exc

        choice = response.choices[0] if response.choices else None
        raw_text = (choice.message.content if choice and choice.message else "") or ""
        raw_text = raw_text.strip()

        if not raw_text:
            raise LLMProviderError("OpenRouter returned an empty response.")

        return self._parse_json(raw_text)

    @staticmethod
    def _parse_json(raw_text: str) -> dict:
        # Defensive: strip accidental markdown fences even though the prompt
        # forbids them, since LLM output is never fully deterministic.
        cleaned = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(f"LLM did not return valid JSON: {exc}") from exc
