# API Specification

## Base URL

```
/api/v1
```

## Authentication

All endpoints except `POST /auth/register` and `POST /auth/login` require a valid
Supabase JWT in the `Authorization` header:

```
Authorization: Bearer <supabase_jwt>
```

FastAPI validates the JWT on every protected request. See `14_AUTH_FLOW.md`.

---

## Standard Error Schema

All error responses share this shape:

```json
{
  "error": "string",
  "detail": "string",
  "status_code": "number"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (validation failure) |
| 401 | Missing or invalid JWT |
| 403 | Valid JWT but insufficient permission |
| 404 | Resource not found |
| 422 | Unprocessable entity (FastAPI default) |
| 500 | Internal server error |

---

## Auth Endpoints

### `POST /auth/register`

Register a new user. Delegates to Supabase Auth.

**Request**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response `201 Created`**
```json
{
  "user_id": "uuid",
  "email": "string",
  "access_token": "string",
  "token_type": "bearer"
}
```

**Errors:** `400` if email already registered or password too weak.

---

### `POST /auth/login`

Login and receive a JWT.

**Request**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response `200 OK`**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

**Errors:** `401` if credentials are invalid.

---

### `POST /auth/logout`

Invalidate the current session. FastAPI holds no session state; this endpoint exists
for API consistency and future token revocation support.

**Request:** No body required.

**Response `204 No Content`**

---

## Document Endpoints

### `POST /documents/upload`

Upload a financial document. Saves the file to Supabase Storage and immediately
enqueues the async analysis pipeline.

**Content-Type:** `multipart/form-data`

**Request Fields**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | binary | Yes | PDF only |
| `document_type` | string | Yes | `bank_statement \| credit_card \| loan \| salary_slip` |

**Response `202 Accepted`**

Returns immediately. Processing is async.

```json
{
  "document_id": "uuid",
  "analysis_job_id": "uuid",
  "status": "queued"
}
```

**Errors:** `400` if file is not a PDF or `document_type` is invalid. `413` if file
exceeds size limit.

> **Note:** The 202 response does not indicate that processing has started. The client
> must poll `GET /analysis/status/{job_id}` to track progress.

---

## Analysis Endpoints

### `GET /analysis/status/{job_id}`

Poll the status of an async analysis pipeline job. The frontend calls this every 3
seconds after a document upload until status is `completed` or `failed`.

**Path Parameters**

| Param | Type | Notes |
|-------|------|-------|
| `job_id` | uuid | Returned by `POST /documents/upload` |

**Response `200 OK`**
```json
{
  "job_id": "uuid",
  "document_id": "uuid",
  "status": "queued | running | completed | failed",
  "started_at": "ISO8601 | null",
  "completed_at": "ISO8601 | null",
  "error_message": "string | null",
  "report_id": "uuid | null"
}
```

`report_id` is populated only when `status` is `completed`.

**Errors:** `404` if job not found or belongs to another user.

---

### `GET /analysis/{financial_profile_id}`

Retrieve the full Universal Financial JSON for a completed analysis.

**Response `200 OK`**
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "created_at": "ISO8601",
  "profile_json": {
    "user": {},
    "accounts": [],
    "transactions": [],
    "loans": [],
    "credit_cards": [],
    "summary": {},
    "analysis": {},
    "recommendations": []
  }
}
```

**Errors:** `404` if profile not found. `403` if the profile belongs to another user.

---

## Report Endpoints

### `GET /reports`

List all reports for the authenticated user, newest first.

**Response `200 OK`**
```json
{
  "reports": [
    {
      "id": "uuid",
      "financial_profile_id": "uuid",
      "created_at": "ISO8601"
    }
  ]
}
```

---

### `GET /reports/{id}`

Retrieve a single AI CFO synthesised report.

**Response `200 OK`**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "financial_profile_id": "uuid",
  "created_at": "ISO8601",
  "content": {
    "executive_summary": "string",
    "debt_summary": {},
    "savings_summary": {},
    "budget_summary": {},
    "priority_recommendations": [],
    "overall_financial_health_score": "number"
  }
}
```

**Errors:** `404` if report not found. `403` if report belongs to another user.

---

## Dashboard Endpoint

### `GET /dashboard`

Retrieve aggregated summary data for the authenticated user's dashboard view.
Computed from the most recent completed `financial_profile`.

**Response `200 OK`**
```json
{
  "user_id": "uuid",
  "total_monthly_income": "number",
  "total_monthly_expenses": "number",
  "total_debt": "number",
  "total_savings": "number",
  "savings_rate_percent": "number",
  "net_worth_estimate": "number",
  "latest_report_id": "uuid | null",
  "documents_processed": "number",
  "last_updated": "ISO8601 | null"
}
```

Returns all-zero values with `latest_report_id: null` if no documents have been
processed yet.

---

## Chat Endpoint

### `POST /chat`

Send a message and receive a response grounded in the user's financial profile.

**Request**
```json
{
  "message": "string",
  "financial_profile_id": "uuid",
  "conversation_history": [
    {
      "role": "user | assistant",
      "content": "string"
    }
  ]
}
```

`conversation_history` may be an empty array for the first message. The client is
responsible for maintaining and forwarding history across turns.

**Response `200 OK`**
```json
{
  "reply": "string",
  "financial_profile_id": "uuid"
}
```

**Errors:** `404` if `financial_profile_id` not found. `400` if `message` is empty.

---

## Endpoint Summary

| Method | Path | Auth | Async |
|--------|------|------|-------|
| POST | `/auth/register` | No | No |
| POST | `/auth/login` | No | No |
| POST | `/auth/logout` | Yes | No |
| POST | `/documents/upload` | Yes | Yes — returns 202 |
| GET | `/analysis/status/{job_id}` | Yes | No |
| GET | `/analysis/{financial_profile_id}` | Yes | No |
| GET | `/reports` | Yes | No |
| GET | `/reports/{id}` | Yes | No |
| GET | `/dashboard` | Yes | No |
| POST | `/chat` | Yes | No |
