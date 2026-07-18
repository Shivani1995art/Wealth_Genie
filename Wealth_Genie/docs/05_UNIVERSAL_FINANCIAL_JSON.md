# Universal Financial JSON

## Purpose

This schema is the normalised contract between the Universal Extractor and all downstream
agents (Debt, Savings, Budget, AI CFO). Every agent reads from this structure. Every
extractor writes to this structure.

## MVP Storage

For MVP the entire document below is stored as a single `jsonb` blob in
`financial_profiles.profile_json`. Individual arrays (accounts, loans, credit_cards,
transactions) are NOT stored in separate relational tables. Relational normalisation is
deferred to Phase 2.

---

## Schema

```json
{
  "user": {
    "id": "uuid",
    "name": "string",
    "email": "string"
  },
  "accounts": [
    {
      "account_id": "string",
      "bank_name": "string",
      "account_type": "savings | current | salary",
      "currency": "string",
      "opening_balance": "number",
      "closing_balance": "number",
      "statement_period_start": "ISO8601",
      "statement_period_end": "ISO8601"
    }
  ],
  "transactions": [
    {
      "transaction_id": "string",
      "account_id": "string",
      "date": "ISO8601",
      "description": "string",
      "amount": "number",
      "type": "credit | debit",
      "category": "string"
    }
  ],
  "loans": [
    {
      "loan_id": "string",
      "lender": "string",
      "loan_type": "home | personal | auto | education | other",
      "principal": "number",
      "outstanding_balance": "number",
      "interest_rate": "number",
      "emi": "number",
      "tenure_remaining_months": "number"
    }
  ],
  "credit_cards": [
    {
      "card_id": "string",
      "issuer": "string",
      "credit_limit": "number",
      "outstanding_balance": "number",
      "minimum_due": "number",
      "due_date": "ISO8601",
      "interest_rate": "number"
    }
  ],
  "summary": {
    "total_monthly_income": "number",
    "total_monthly_expenses": "number",
    "total_debt": "number",
    "total_savings": "number",
    "net_worth_estimate": "number",
    "savings_rate_percent": "number"
  },
  "analysis": {
    "debt_agent": {},
    "savings_agent": {},
    "budget_agent": {}
  },
  "recommendations": [
    {
      "agent": "debt_agent | savings_agent | budget_agent | ai_cfo",
      "priority": "high | medium | low",
      "title": "string",
      "detail": "string"
    }
  ]
}
```

---

## Field Ownership

| Section | Written By | Read By |
|---------|-----------|---------|
| `user` | System (auth context) | All agents |
| `accounts` | Universal Extractor | Savings Agent, Budget Agent |
| `transactions` | Universal Extractor | Budget Agent, Savings Agent |
| `loans` | Universal Extractor | Debt Agent |
| `credit_cards` | Universal Extractor | Debt Agent |
| `summary` | Universal Extractor | All agents, AI CFO |
| `analysis` | Debt / Savings / Budget Agents | AI CFO |
| `recommendations` | All agents + AI CFO | Report, Dashboard, Chat |
