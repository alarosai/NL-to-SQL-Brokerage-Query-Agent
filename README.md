# NL-to-SQL Brokerage Query Agent

[Live Demo](https://nl-to-sql-brokerage-query-agent.vercel.app/)

An AI-powered natural language interface for querying brokerage data. Ask questions in plain English — the agent generates SQL using Google Gemini 2.5 Flash, runs it against a local SQLite database, and returns results with a natural-language summary.

Built with **Next.js 14**, **Tailwind CSS**, **Framer Motion**, and **SQLite**.

## Architecture

```
User Question (natural language)
        │
        ▼
┌─────────────────────────────────┐
│       Next.js API Route         │
│ 1. Guardrails Check             │ ← Block destructive SQL, PII, out-of-scope
│ 2. Gemini SQL Generation        │ ← Schema-injected prompt to Gemini 2.5 Flash
│ 3. Secondary Guardrail Check    │ ← Validate LLM's raw SQL
│ 4. SQLite Execution             │ ← Read-only execution via `better-sqlite3`
│ 5. Gemini Summarization         │ ← Return SQL results to Gemini for summary
└────────────────┬────────────────┘
                 │
                 ▼
          Next.js Client
     (Premium Framer Motion UI)
```

## Database Schema

| Table | Rows | Description |
|-------|------|-------------|
| `instruments` | ~500 | Real NASDAQ/NYSE tickers with company names |
| `prices` | ~500K | OHLCV data across ~2 years of trading days |
| `accounts` | ~1,000 | Synthetic brokerage accounts (faker) |
| `orders` | ~50,000 | Synthetic orders seeded from real prices |
| `positions` | ~10,000 | Derived from filled orders |

## Example Queries ("Golden Set")

- "Find the ticker with the highest average position size"
- "What is the average order size for AAPL?"
- "Which tickers have the highest average order size?"
- "Show positions where unrealized loss exceeds 10%"

## Safety & Guardrails

- **Read-only enforcement**: Destructive verbs (DELETE, DROP, UPDATE) are hard-blocked BEFORE reaching the database. SQLite mode is also explicitly `readonly`.
- **PII protection**: Keys like SSN, PASSWORD, and EMAIL are automatically blocked by the route guardrails.
- **Row limits**: Maximum 1,000 rows returned per query to prevent overwhelming the browser and serverless function memory limit.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 2.5 Flash |
| Database | SQLite (`better-sqlite3`) |
| Frontend | Next.js (React), Tailwind CSS, Framer Motion |
| API Layer| Next.js App Router API |
| Language | TypeScript (App), Python (Data Script only) |
