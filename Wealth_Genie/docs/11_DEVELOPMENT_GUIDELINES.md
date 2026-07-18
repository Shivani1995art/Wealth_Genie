# Development Guidelines

1. **One feature at a time.** No feature is started until the previous one is complete
   and reviewed.

2. **Deterministic calculations.** All financial calculations (totals, ratios, EMIs)
   must use deterministic arithmetic — no rounding surprises, no float drift.
   Use `Decimal` in Python for all money values.

3. **Typed APIs.** Every FastAPI endpoint must have Pydantic request and response
   models. Every Next.js fetch call must have a TypeScript interface for the response.

4. **Commit often.** One logical change per commit. Never commit broken code to main.

5. **No placeholder code.** Do not generate stub functions, TODO comments, or mock
   return values unless explicitly requested.

6. **No unnecessary libraries.** Every new dependency must be justified. Prefer the
   standard library and already-approved packages.

7. **Clean architecture over shortcuts.** Favour clear separation of concerns over
   convenient hacks, even if it takes longer.

8. **Environment variables only.** No secrets in source code, ever. Use `.env.local`
   for local development; production secrets go in the deployment environment.

9. **RLS on every table.** Every Supabase table must have Row-Level Security enabled
   before any data is written to it.

10. **Docs first.** If a feature requires a new API endpoint or schema change, update
    the relevant documentation file before writing application code.
