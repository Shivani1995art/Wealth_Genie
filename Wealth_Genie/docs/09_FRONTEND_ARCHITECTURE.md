# Frontend Architecture

## Stack

| Library | Purpose |
|---------|---------|
| Next.js 15 | App framework (App Router) |
| TypeScript | Type safety across all components and API calls |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Component library (built on Radix UI) |
| Recharts | Data visualisation for the Dashboard |
| @supabase/supabase-js | Auth, Storage, and Realtime client |

## Notes

- The frontend communicates with Supabase directly for auth and file upload.
- All other data fetching goes through the FastAPI backend (`/api/v1/*`).
- The Supabase JWT is attached to every FastAPI request via the Authorization header.
- See `14_AUTH_FLOW.md` for the full auth integration pattern.
