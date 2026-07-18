# Authentication Flow

## Overview

Authentication is split across two responsibilities:

| Layer | Responsibility |
|-------|---------------|
| **Supabase Auth** | Issues JWTs, manages sessions, stores user identity |
| **FastAPI** | Validates JWTs on every protected request, extracts `user_id` |

The Next.js frontend never calls FastAPI for login or registration. It calls Supabase
directly. FastAPI trusts Supabase-issued JWTs and never issues tokens of its own.

---

## Registration Flow

```
User fills register form (Next.js)
  │
  └─► supabase.auth.signUp({ email, password })
        │
        └─► Supabase Auth creates user in auth.users
              │
              └─► Returns { user, session: { access_token, refresh_token } }
                    │
                    └─► Frontend stores session and redirects to dashboard
```

No FastAPI backend call is made during registration. Supabase manages user signups client-side.

---

## Login Flow

```
User fills login form (Next.js)
  │
  └─► supabase.auth.signInWithPassword({ email, password })
        │
        └─► Supabase Auth validates credentials
              │
              └─► Returns { user, session: { access_token, refresh_token } }
                    │
                    └─► Frontend stores access_token in memory
                          (Supabase JS client handles refresh automatically)
```

---

## Authenticated API Request Flow

```
Next.js (any protected page/action)
  │
  └─► const { data: { session } } = await supabase.auth.getSession()
        │
        └─► fetch('/api/v1/<endpoint>', {
              headers: {
                'Authorization': `Bearer ${session.access_token}`
              }
            })
              │
              └─► FastAPI receives request
                    │
                    └─► JWT Middleware / Dependency:
                          1. Extract token from Authorization header
                          2. Decode JWT using SUPABASE_JWT_SECRET (HS256)
                          3. Validate: signature, exp, aud = "authenticated"
                          4. Extract sub claim → user_id (uuid)
                          5. Inject user_id into request context
                          │
                          └─► Route handler receives user_id
                                (No database lookup required)
```

---

## JWT Validation (FastAPI)

FastAPI validates every protected request using a shared dependency:

**Library:** `python-jose[cryptography]` or `PyJWT`

**Algorithm:** `HS256`

**Secret:** `SUPABASE_JWT_SECRET` (environment variable, never committed to source)

**Claims validated:**

| Claim | Expected Value |
|-------|---------------|
| `aud` | `"authenticated"` |
| `exp` | Must be in the future |
| `sub` | UUID — becomes `user_id` in route handlers |
| `role` | `"authenticated"` |

A missing, expired, or tampered JWT returns:

```json
{
  "error": "Unauthorized",
  "detail": "Invalid or expired token",
  "status_code": 401
}
```

---

## Session Refresh

The Supabase JS client automatically refreshes the `access_token` using the
`refresh_token` before it expires. No FastAPI endpoint handles token refresh.

---

## Logout Flow

```
User clicks Logout (Next.js)
  │
  └─► supabase.auth.signOut()
        │
        └─► Supabase invalidates session client-side
              │
              └─► Frontend redirects to /login
```

No FastAPI backend call is made during logout.

---

## Row-Level Security (RLS) Integration

Supabase RLS policies use `auth.uid()` to restrict row access per user. For operations
that go through the Supabase client directly (e.g., file storage), RLS enforces
isolation automatically.

For all FastAPI database operations, the `user_id` extracted from the JWT is passed
explicitly in every query's `WHERE user_id = :user_id` clause. FastAPI does NOT use
the Supabase client's RLS context — it uses the service role key for server-side DB
access and enforces ownership checks in application code.

---

## Environment Variables

```bash
# Required on the frontend (Next.js)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=

# Required on the backend (FastAPI)
SUPABASE_URL=
SUPABASE_JWT_SECRET=          # Used to validate JWTs — keep secret
SUPABASE_SERVICE_ROLE_KEY=    # Used for server-side DB access — keep secret
```

**Security rules:**

| Variable | Client-side safe? | Notes |
|----------|------------------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase design; safe to expose |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase design; safe to expose |
| `SUPABASE_JWT_SECRET` | **No** | Exposes ability to forge JWTs |
| `SUPABASE_SERVICE_ROLE_KEY` | **No** | Bypasses all RLS — never expose |

---

## Protected vs. Public Endpoints

All backend endpoints are protected and require a valid Supabase JWT Bearer token in the `Authorization` header.

| Endpoint | Auth Required |
|----------|--------------|
| All endpoints | Yes — JWT required |
