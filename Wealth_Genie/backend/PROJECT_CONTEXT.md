# Wealth_Genie - Project Context

## Project Overview

Wealth_Genie is an AI-powered Financial Coach backend built with FastAPI and Supabase.

Architecture goals:

- Clean Architecture
- Provider-independent LLM layer
- Local-first where possible
- Deterministic validation
- Production-ready code
- Testable modules
- No business logic inside routes

---

# Current Milestone

Completed:

✅ Authentication
✅ Upload API
✅ Async Analysis Pipeline
✅ Universal Financial Extractor
✅ OCR Support
✅ Digital PDF Parser
✅ Image Parser
✅ CSV Parser
✅ Excel Parser
✅ Parser Registry
✅ Document Detector
✅ Universal Financial Schema
✅ OpenRouter Provider
✅ Shared LLM Prompt
✅ Deterministic Business Validation
✅ Evaluation Dataset Foundation

Current provider:

LLM_PROVIDER=openrouter

Model:

google/gemini-2.5-flash

---

# Architecture

Upload

↓

Background Analysis Pipeline

↓

UniversalExtractor

↓

DocumentDetector

↓

ParserRegistry

↓

Parser

↓

TextNormalizer

↓

OpenRouter LLM Provider

↓

Pydantic Validation

↓

Business Validation

↓

UniversalFinancialProfile

↓

FinancialProfilesRepository

↓

Supabase

---

# Current Folder Highlights

backend/

app/

services/

extraction/

llm/

pipeline/

repositories/

schemas_ext/

evaluation/

bank_statement/

hdfc_salary_account/

expected.json

metadata.json

README.md

evaluate.py

run_sample.py

---

# LLM Layer

Implemented:

LLMProvider (ABC)

Claude Provider

OpenRouter Provider

Factory Pattern

Shared Prompt

Current provider:

OpenRouter

Model:

google/gemini-2.5-flash

---

# Validation

Business validation currently checks:

- Statement period order
- Negative balances
- Transaction amount
- Transaction date within statement period
- Savings rate bounds

47 tests currently pass.

---

# Evaluation

Foundation completed.

Current status:

evaluation/

bank_statement/

hdfc_salary_account/

expected.json

metadata.json

README.md

evaluate.py

run_sample.py

The evaluation runner is intentionally paused.

Reason:

Current LLM extraction is non-deterministic.

We will build a semantic evaluator after AI agents are implemented.

---

# Current Git State

Universal Extractor is considered stable.

47/47 tests passing.

---

# Next Milestone

Milestone 4

Debt Agent

Goals:

- Read UniversalFinancialProfile
- Analyze loans
- Analyze credit cards
- Compute debt ratio
- Compute DTI
- Compute utilization
- Detect risky debt
- Generate structured debt analysis
- No LLM hallucinated calculations
- Deterministic financial calculations first
- LLM only for explanation

---

# Development Rules

Never duplicate business logic.

Keep UniversalExtractor unchanged unless necessary.

Use dependency injection.

Preserve provider independence.

Do not break existing tests.

Always run pytest after meaningful changes.

Prefer small incremental commits.

Explain architecture before implementation.

Do not rewrite files unnecessarily.

When modifying files:

- Show exactly what to replace.
- If replacing an entire file, provide the complete file.
- Otherwise specify:
  - file
  - line/function
  - what to replace
  - replacement code

Never assume project state.
Always inspect the latest code before modifying it.
