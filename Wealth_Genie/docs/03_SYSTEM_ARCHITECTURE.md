# System Architecture

## High-Level Pipeline

```
User (Browser)
  │
  ├─ POST /auth/login  ──────────────────────────► Supabase Auth
  │                                                 Returns JWT
  │
  ├─ POST /documents/upload  ────────────────────► FastAPI
  │     (JWT in Authorization header)               │
  │     Returns 202 Accepted immediately            ├─ Save file → Supabase Storage
  │                                                 ├─ Create documents record
  │                                                 ├─ Create analysis_jobs record
  │                                                 └─ Enqueue BackgroundTask
  │                                                       │
  │                                                       ▼
  │                                               [Async Pipeline]
  │                                                Universal Extractor
  │                                                       │
  │                                                 Financial JSON
  │                                                 ┌─────┼─────┐
  │                                                 ▼     ▼     ▼
  │                                              Debt  Savings Budget
  │                                              Agent  Agent  Agent
  │                                                 └─────┼─────┘
  │                                                       ▼
  │                                                    AI CFO
  │                                                 (Synthesiser)
  │                                                       │
  │                                                       ▼
  │                                               Report saved to DB
  │
  ├─ GET /analysis/status/{job_id}  ─────────────► Poll until completed
  │     (Frontend polls every 3 seconds)
  │
  ├─ GET /reports/{id}  ─────────────────────────► Report data
  │
  ├─ GET /dashboard  ────────────────────────────► Aggregated summary
  │
  └─ POST /chat  ────────────────────────────────► AI Chat response
```

---

## Agent Execution Order

The three specialist agents (Debt, Savings, Budget) execute on the Financial JSON
independently and can run in parallel. The AI CFO executes only after all three
specialist agents have completed.

**The AI CFO is a synthesiser, not an orchestrator.**
It reads the completed outputs of the three specialist agents and produces a unified
advisory report. It does not call, trigger, or manage the specialist agents.

See `08_AI_AGENT_ARCHITECTURE.md` for full agent role definitions.

---

## Asynchronous Document Processing

Document upload returns immediately (HTTP 202). The full analysis pipeline runs as a
FastAPI `BackgroundTask`. The frontend polls the status endpoint until the pipeline
completes or fails.

See `13_ASYNC_PROCESSING.md` for the complete async architecture.

---

## Authentication

Supabase handles authentication client-side (register, login, session refresh). The
resulting JWT is forwarded to FastAPI on every protected API request. FastAPI validates
the JWT signature and claims using the `SUPABASE_JWT_SECRET`. No custom user session
table is required.

See `14_AUTH_FLOW.md` for the complete auth flow.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | FastAPI, Python |
| Database | Supabase (PostgreSQL + Storage + Auth) |
| Background Tasks | FastAPI `BackgroundTasks` (MVP); Celery + Redis (Phase 2) |
