# Project Overview

## Vision

Personalized multi-agent financial advisor that extracts, analyses, and advises on a
user's complete financial picture from real documents.

---

## Canonical MVP Feature List

> **This is the single authoritative MVP feature list.**
> All other documents defer to this table. If any other document conflicts with this
> list, this document wins.

| # | Feature | Description |
|---|---------|-------------|
| 1 | Auth | Register, login, and logout via Supabase. JWT forwarded to FastAPI for validation on every protected request. |
| 2 | Document Upload | Upload Bank Statements, Credit Cards, Loans, and Salary Slips (PDF). |
| 3 | Universal Extraction | Parse uploaded PDFs into the Universal Financial JSON schema via the Universal Extractor agent. |
| 4 | Financial Profile | Store extracted Financial JSON as a single JSON blob in `financial_profiles.profile_json`. Relational normalisation is deferred to Phase 2. |
| 5 | Debt Agent | Analyse loans and credit card data; produce debt recommendations. |
| 6 | Savings Agent | Analyse income and savings patterns; produce savings recommendations. |
| 7 | Budget Agent | Analyse spending patterns; produce budget recommendations. |
| 8 | AI CFO | Synthesise outputs from all three specialist agents into a unified advisory report. The AI CFO executes after the specialist agents complete — it is a synthesiser, not an orchestrator. |
| 9 | Report | Persisted AI CFO synthesis, viewable by the user. |
| 10 | Dashboard | Summary view of financial health, key metrics, and report access. |
| 11 | AI Chat | Conversational interface grounded in the user's financial profile. |

---

## Out of Scope for MVP

- Investment tracking
- Financial forecasting
- Goal Planner
- Relational normalisation of accounts, loans, and credit card tables (deferred to Phase 2)
- Multi-document batch processing (deferred to Phase 2)
- Multi-currency support

---

## Phased Roadmap Summary

| Phase | Theme |
|-------|-------|
| 1 | MVP (features above) |
| 2 | Multi-document + relational DB normalisation |
| 3 | Investments |
| 4 | Forecasting |
| 5 | Financial OS |
