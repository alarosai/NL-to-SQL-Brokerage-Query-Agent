# NL-to-SQL Brokerage Query Agent

An AI-powered natural language interface for querying brokerage data. Ask questions in plain English — the agent generates SQL using Claude (Anthropic API), runs it against a local SQLite database, and returns results with a natural-language summary.

Built with **Next.js 14**, **Tailwind CSS**, **Framer Motion**, and **SQLite**.

---

## Quick Start
### 1. Install Dependencies
\`\`\`bash
npm install
\`\`\`

### 2. Set API Key
Create a \`.env.local\` file in the root directory:
\`\`\`bash
cp .env.example .env.local
\`\`\`
Edit \`.env.local\` and add your Gemini API key:
\`\`\`env
GEMINI_API_KEY=your_key_here
\`\`\`

### 3. Generate Database
Ensure you have Python installed and the \`faker\` package:
\`\`\`bash
pip install faker
python data/generate_db.py
\`\`\`
This creates \`data/brokerage.db\` with ~500 tickers, ~500K price rows, ~1K accounts, ~50K orders, and ~10K positions.

### 4. Run the Dev Server
\`\`\`bash
npm run dev
\`\`\`
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Architecture

\`\`\`
User Question (natural language)
        │
        ▼
┌─────────────────────────────────┐
│       Next.js API Route         │
│ 1. Guardrails Check             │ ← Block destructive SQL, PII, out-of-scope
│ 2. Claude SQL Generation        │ ← Schema-injected prompt to Claude 3.5 Sonnet
│ 3. Secondary Guardrail Check    │ ← Validate LLM's raw SQL
│ 4. SQLite Execution             │ ← Read-only execution via \`better-sqlite3\`
│ 5. Claude Summarization         │ ← Return SQL results to Claude for summary
└────────────────┬────────────────┘
                 │
                 ▼
          Next.js Client
     (Premium Framer Motion UI)
\`\`\`

## Database Schema

| Table | Rows | Description |
|-------|------|-------------|
| \`instruments\` | ~500 | Real NASDAQ/NYSE tickers with company names |
| \`prices\` | ~500K | OHLCV data across ~2 years of trading days |
| \`accounts\` | ~1,000 | Synthetic brokerage accounts (faker) |
| \`orders\` | ~50,000 | Synthetic orders seeded from real prices |
| \`positions\` | ~10,000 | Derived from filled orders |

## Example Queries ("Golden Set")

- "Find the ticker with the highest average position size"
- "What is the average order size for AAPL?"
- "Which tickers have the highest average order size?"
- "Show positions where unrealized loss exceeds 10%"

## Safety & Guardrails

- **Read-only enforcement**: Destructive verbs (DELETE, DROP, UPDATE) are hard-blocked BEFORE reaching the database. SQLite mode is also explicitly \`readonly\`.
- **PII protection**: Keys like SSN, PASSWORD, and EMAIL are automatically blocked by the route guardrails.
- **Row limits**: Maximum 1,000 rows returned per query to prevent overwhelming the browser and serverless function memory limit.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Google Gemini 2.5 Flash |
| Database | SQLite (\`better-sqlite3\`) |
| Frontend | Next.js (React), Tailwind CSS, Framer Motion |
| API Layer| Next.js App Router API |
| Language | TypeScript (App), Python (Data Script only) |
