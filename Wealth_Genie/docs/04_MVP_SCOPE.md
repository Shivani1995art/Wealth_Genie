# MVP Scope

> The canonical MVP feature list is defined in `01_PROJECT_OVERVIEW.md`.
> This document defines scope boundaries only and does not redefine the feature list.

---

## In Scope

| Feature | Notes |
|---------|-------|
| Auth | Register, login, logout (Supabase + FastAPI JWT validation) |
| Document Upload | PDF only: Bank Statements, Credit Cards, Loans, Salary Slips |
| Universal Extraction | PDF → Universal Financial JSON |
| Financial Profile | JSON blob stored in `financial_profiles.profile_json` |
| Debt Agent | Analyses loan and credit card data |
| Savings Agent | Analyses income and savings patterns |
| Budget Agent | Analyses spending and categorisation |
| AI CFO | Synthesises specialist agent outputs into a unified report |
| Report | Persisted AI CFO output, viewable by user |
| Dashboard | Financial health summary and report access |
| AI Chat | Conversational Q&A over the user's financial data |
| Async Processing | FastAPI BackgroundTasks pipeline with status polling |

---

## Out of Scope (MVP)

| Feature | Deferred To |
|---------|-------------|
| Investment tracking | Phase 3 |
| Financial forecasting | Phase 4 |
| Goal Planner | Phase 4 |
| Relational tables for accounts, loans, credit cards | Phase 2 |
| Multi-document batch uploads | Phase 2 |
| Multi-currency support | Phase 2 |
| Celery / Redis task queue | Phase 2 |
| Token revocation / refresh endpoint | Phase 2 |

---

## Scope Decision Log

| Decision | Rationale |
|----------|-----------|
| Store financial data as JSON blob (not normalised tables) | Avoids premature schema complexity while the data model is still evolving. The Universal Financial JSON is the schema contract for MVP. |
| FastAPI BackgroundTasks (not Celery) | No additional infrastructure required for MVP. Acceptable limitation: jobs are lost on server restart. |
| Supabase Auth (not custom auth) | Removes the need to implement token issuance, hashing, and session management. |
