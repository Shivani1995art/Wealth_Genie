# Asynchronous Processing Architecture

## Problem

Document parsing and multi-agent analysis take 15–60 seconds per document. A
synchronous HTTP response would time out in any standard API gateway, reverse proxy,
or browser.

---

## Solution: FastAPI `BackgroundTasks`

The `POST /documents/upload` endpoint does the minimum synchronous work, returns
`202 Accepted` immediately, then delegates all heavy processing to a FastAPI
`BackgroundTask` running in the same process.

### Synchronous steps (in the request handler, before 202 response):

1. Validate file type (PDF) and `document_type` field.
2. Upload the file to Supabase Storage.
3. Insert a row into `documents` with `status = 'uploaded'`.
4. Insert a row into `analysis_jobs` with `status = 'queued'`.
5. Register `run_analysis_pipeline` as a `BackgroundTask`.
6. Return `202 Accepted` with `{ document_id, analysis_job_id, status: "queued" }`.

---

## Background Task: `run_analysis_pipeline`

```
run_analysis_pipeline(document_id, user_id)

  Step 1:  UPDATE analysis_jobs SET status = 'running', started_at = now()
           UPDATE documents SET status = 'processing'

  Step 2:  Download file bytes from Supabase Storage

  Step 3:  universal_extractor.run(file_bytes, document_type)
           → Returns Financial JSON
           INSERT into financial_profiles (profile_json = <Financial JSON>)
           → Returns financial_profile_id

  Step 4:  debt_agent.run(financial_profile_id)
           → INSERT into recommendations (agent = 'debt_agent', content = <output>)

  Step 5:  savings_agent.run(financial_profile_id)
           → INSERT into recommendations (agent = 'savings_agent', content = <output>)

  Step 6:  budget_agent.run(financial_profile_id)
           → INSERT into recommendations (agent = 'budget_agent', content = <output>)

  Step 7:  ai_cfo.run(financial_profile_id)
           → INSERT into reports (content = <synthesised report>)
           → INSERT into recommendations (agent = 'ai_cfo', content = <output>)
           → Returns report_id

  Step 8:  UPDATE documents SET status = 'completed'
           UPDATE analysis_jobs SET
             status = 'completed',
             completed_at = now()
             report_id = <report_id>    ← stored in analysis_jobs for polling

  On any unhandled exception at any step:
    UPDATE documents SET status = 'failed'
    UPDATE analysis_jobs SET
      status = 'failed',
      completed_at = now(),
      error_message = <exception message>
```

---

## Status Polling

The frontend polls `GET /analysis/status/{job_id}` every **3 seconds** after receiving
the `202` response from upload.

```
Frontend polling loop:

  while true:
    response = GET /analysis/status/{job_id}

    if response.status == 'completed':
      navigate to /reports/{response.report_id}
      break

    if response.status == 'failed':
      show error message (response.error_message)
      break

    if response.status in ['queued', 'running']:
      wait 3 seconds
      continue
```

The status endpoint reads a single row from `analysis_jobs`. It is fast and cheap.

---

## Progress States

| `analysis_jobs.status` | `documents.status` | Meaning |
|------------------------|-------------------|---------|
| `queued` | `uploaded` | Background task registered, not yet started |
| `running` | `processing` | Pipeline is actively running |
| `completed` | `completed` | All agents finished, report saved |
| `failed` | `failed` | An error occurred; see `error_message` |

---

## Why FastAPI `BackgroundTasks` (not Celery)?

For MVP, `BackgroundTasks` is sufficient because:

- No additional infrastructure is required (no Redis, no Celery worker process)
- Everything runs in the same FastAPI process
- Simple to implement, test, and debug
- Adequate for single-server MVP deployment

**Known limitation:** If the FastAPI server restarts while a background task is running,
the task is lost. The `analysis_jobs` row will remain stuck at `running`. For MVP this
is an acceptable trade-off.

**Recovery note (MVP):** A stuck job (status = `running` for > 5 minutes) can be
manually reset to `failed` for retry.

---

## Phase 2 Upgrade Path

In Phase 2 (Multi-document), replace `BackgroundTasks` with **Celery + Redis**:

| Concern | BackgroundTasks (MVP) | Celery + Redis (Phase 2) |
|---------|----------------------|--------------------------|
| Durability | Lost on server restart | Persisted in Redis |
| Retries | Manual | Automatic with backoff |
| Concurrency | Limited by server threads | Horizontal worker scaling |
| Monitoring | Logs only | Flower dashboard |
| Parallelism | Sequential agent calls | Parallel agent tasks |

The `analysis_jobs` table and the `run_analysis_pipeline` interface are designed to be
compatible with Celery task signatures, making this upgrade non-breaking for the rest
of the system.

---

## File Size and Timeout Limits (MVP)

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max upload file size | 10 MB | Sufficient for all supported PDF types |
| Analysis timeout | 120 seconds | Generous ceiling for LLM agent calls |
| Polling interval | 3 seconds | Low enough for good UX, high enough to avoid rate limits |
