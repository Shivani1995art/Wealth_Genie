# Database Schema

## MVP Storage Decision

**For MVP, the complete extracted financial data is stored as a single `jsonb` blob in
the `financial_profiles` table (`profile_json` column).**

This means `accounts`, `transactions`, `loans`, and `credit_cards` are NOT stored in
separate relational tables in the MVP. Relational normalisation is explicitly deferred
to Phase 2 (Multi-document).

**Rationale:** The Universal Financial JSON schema is still evolving across document
types. Normalising prematurely would require costly migrations before the schema
stabilises. The `jsonb` type in PostgreSQL is fully queryable for the subset of fields
needed by MVP endpoints (e.g., dashboard aggregates).

---

## Tables

### `auth.users` (Supabase-managed)

Supabase Auth owns user identity. No custom `users` table is required for MVP.
FastAPI reads the `sub` claim from the validated JWT to obtain `user_id`.

---

### `documents`

Tracks every uploaded file and its processing status.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `user_id` | `uuid` | FK → `auth.users.id`, NOT NULL | Row-level security key |
| `file_name` | `text` | NOT NULL | Original uploaded filename |
| `file_path` | `text` | NOT NULL | Supabase Storage object path |
| `document_type` | `text` | NOT NULL | `bank_statement \| credit_card \| loan \| salary_slip` |
| `status` | `text` | NOT NULL, default `'uploaded'` | `uploaded \| processing \| completed \| failed` |
| `uploaded_at` | `timestamptz` | NOT NULL, default `now()` | |

---

### `analysis_jobs`

Tracks the async background pipeline triggered after each upload.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `document_id` | `uuid` | FK → `documents.id`, NOT NULL | |
| `user_id` | `uuid` | FK → `auth.users.id`, NOT NULL | Denormalised for fast auth checks |
| `status` | `text` | NOT NULL, default `'queued'` | `queued \| running \| completed \| failed` |
| `error_message` | `text` | NULLABLE | Populated only on `failed` |
| `started_at` | `timestamptz` | NULLABLE | Set when pipeline begins |
| `completed_at` | `timestamptz` | NULLABLE | Set when pipeline ends (success or failure) |
| `report_id` | `uuid` | FK → `reports.id`, NULLABLE | Populated when `status = 'completed'`; used by the status-polling endpoint to return the report link |

---

### `financial_profiles`

Stores the complete Universal Financial JSON produced by the Universal Extractor.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `user_id` | `uuid` | FK → `auth.users.id`, NOT NULL | |
| `document_id` | `uuid` | FK → `documents.id`, NOT NULL | One profile per document in MVP |
| `profile_json` | `jsonb` | NOT NULL | Full Universal Financial JSON blob |
| `created_at` | `timestamptz` | NOT NULL, default `now()` | |
| `updated_at` | `timestamptz` | NOT NULL, default `now()` | |

> **Note:** `profile_json` stores the complete structure including `accounts`,
> `transactions`, `loans`, `credit_cards`, `summary`, `analysis`, and `recommendations`.
> In Phase 2 these will be extracted into dedicated relational tables.

---

### `recommendations`

Stores the output of each specialist agent individually, enabling per-agent retrieval
and audit.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `user_id` | `uuid` | FK → `auth.users.id`, NOT NULL | |
| `financial_profile_id` | `uuid` | FK → `financial_profiles.id`, NOT NULL | |
| `agent` | `text` | NOT NULL | `debt_agent \| savings_agent \| budget_agent \| ai_cfo` |
| `content` | `jsonb` | NOT NULL | Agent-specific output JSON |
| `created_at` | `timestamptz` | NOT NULL, default `now()` | |

---

### `reports`

Stores the AI CFO synthesised report.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | `uuid` | PK, default `gen_random_uuid()` | |
| `user_id` | `uuid` | FK → `auth.users.id`, NOT NULL | |
| `financial_profile_id` | `uuid` | FK → `financial_profiles.id`, NOT NULL | |
| `content` | `jsonb` | NOT NULL | AI CFO synthesised report JSON |
| `created_at` | `timestamptz` | NOT NULL, default `now()` | |

---

## Row-Level Security (RLS)

All tables must have RLS enabled in Supabase. The policy for every table is:

> A user may only SELECT, INSERT, or UPDATE rows where `user_id = auth.uid()`.

No user may access another user's documents, profiles, recommendations, or reports.

---

## Phase 2 Additions (Deferred)

The following tables are explicitly out of scope for MVP. They will be introduced in
Phase 2 when multi-document support and relational queries are required.

- `accounts`
- `loans`
- `credit_cards`
- `transactions` (relational, indexed by `account_id` and `date`)
