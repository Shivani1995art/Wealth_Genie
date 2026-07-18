# AI Agent Architecture

## Execution Order

```
                    ┌─────────────────────────┐
                    │   Universal Extractor    │
                    │  PDF → Financial JSON    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Financial JSON (DB)   │
                    └──┬──────────┬──────────┬┘
                       │          │          │
              ┌────────▼──┐  ┌────▼────┐  ┌─▼───────┐
              │ Debt Agent │  │Savings  │  │ Budget  │
              │            │  │  Agent  │  │  Agent  │
              └────────┬──┘  └────┬────┘  └─┬───────┘
                       │          │          │
                    ┌──▼──────────▼──────────▼──┐
                    │         AI CFO             │
                    │       (Synthesiser)        │
                    │  Reads all agent outputs   │
                    │  Produces unified report   │
                    └────────────┬───────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Report (saved DB)    │
                    └─────────────────────────┘
```

The three specialist agents (Debt, Savings, Budget) operate independently on the
Financial JSON and may execute in parallel. The AI CFO executes only after all three
have completed.

---

## Agent Definitions

### Universal Extractor

| Property | Value |
|----------|-------|
| **Role** | Parser and normaliser |
| **Input** | Raw PDF (bank statement, credit card statement, loan document, salary slip) |
| **Output** | Universal Financial JSON written to `financial_profiles.profile_json` |
| **Reads** | Raw file from Supabase Storage |
| **Writes** | `financial_profiles`, `documents.status` |

Responsibilities:
- Extract text from PDF
- Identify document type if not provided
- Populate all applicable sections of the Universal Financial JSON schema
- Leave sections empty (not null) for data not present in the document

---

### Debt Agent

| Property | Value |
|----------|-------|
| **Role** | Specialist — debt analysis |
| **Input** | `financial_profile.loans`, `financial_profile.credit_cards`, `financial_profile.summary` |
| **Output** | Debt analysis object written to `recommendations` (agent = `debt_agent`) |
| **Reads** | `financial_profiles.profile_json` |
| **Writes** | `recommendations` |

Responsibilities:
- Calculate total outstanding debt
- Identify highest-interest liabilities
- Compute debt-to-income ratio
- Recommend payoff strategy (avalanche or snowball)
- Flag minimum payments vs. full payoff timelines

---

### Savings Agent

| Property | Value |
|----------|-------|
| **Role** | Specialist — savings and income analysis |
| **Input** | `financial_profile.accounts`, `financial_profile.transactions`, `financial_profile.summary` |
| **Output** | Savings analysis object written to `recommendations` (agent = `savings_agent`) |
| **Reads** | `financial_profiles.profile_json` |
| **Writes** | `recommendations` |

Responsibilities:
- Verify and validate monthly income from salary slips and credits
- Calculate current savings rate
- Assess emergency fund adequacy (target: 3–6 months of expenses)
- Recommend savings targets and allocation

---

### Budget Agent

| Property | Value |
|----------|-------|
| **Role** | Specialist — spending and budget analysis |
| **Input** | `financial_profile.transactions`, `financial_profile.summary` |
| **Output** | Budget analysis object written to `recommendations` (agent = `budget_agent`) |
| **Reads** | `financial_profiles.profile_json` |
| **Writes** | `recommendations` |

Responsibilities:
- Categorise transactions (food, transport, utilities, entertainment, etc.)
- Identify spending patterns and anomalies
- Compare spending to income
- Recommend budget allocations per category

---

### AI CFO (Synthesiser)

| Property | Value |
|----------|-------|
| **Role** | Synthesiser — unified advisory report |
| **Input** | All three specialist agent outputs from `recommendations` |
| **Output** | Unified report written to `reports` |
| **Reads** | `recommendations` (all three agents), `financial_profiles.profile_json` (for context) |
| **Writes** | `reports`, `recommendations` (agent = `ai_cfo`) |

**The AI CFO does NOT orchestrate, call, or trigger the specialist agents.**
It executes only after the Debt, Savings, and Budget agents have all written their
outputs to `recommendations`.

Responsibilities:
- Synthesise the three specialist reports into a coherent narrative
- Prioritise recommendations across all domains (debt vs. savings vs. budget)
- Compute an overall financial health score
- Produce the final `executive_summary` and `priority_recommendations` for the Report

---

## Agent Runner

The agent pipeline is not a separate microservice. For MVP, all agents are Python
functions called sequentially within a FastAPI `BackgroundTask`.

Execution sequence within the background task:

```
1. universal_extractor.run(document_id)
2. debt_agent.run(financial_profile_id)        # can be parallelised in future
3. savings_agent.run(financial_profile_id)     # can be parallelised in future
4. budget_agent.run(financial_profile_id)      # can be parallelised in future
5. ai_cfo.run(financial_profile_id)            # must run after 2, 3, 4
```

See `13_ASYNC_PROCESSING.md` for the full pipeline flow and error handling.
