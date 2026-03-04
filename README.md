# Rayeva AI Systems Assignment

Built for the Rayeva AI internship assignment. A full-stack AI platform for sustainable commerce — product categorization, B2B proposal generation, and impact reporting.

**Stack:** FastAPI · Next.js 14 · SQLite · grok-4 (Azure AI Foundry)

---

## What's inside

**Module 1 — AI Product Categorizer** (fully built)
Drop in a product name + description and the AI assigns a category, generates SEO tags, picks sustainability filters, and gives it a score. The score itself is deterministic Python logic, not AI ; keeps it auditable.

**Module 2 — B2B Proposal Generator** (fully built)
Two-step AI pipeline: first call picks the product mix, then server-side Python validates all the math (GST, shipping, discounts), then a second AI call adds the impact story. Frontend has PDF export.

**Module 3 & 4 — Impact Reporting / WhatsApp Bot** (architecture only)
Full design written up in `backend/app/services/module3_impact_architecture.py` and `module4_whatsapp_architecture.py`. Didn't implement them but the schemas, endpoints, and logic are all documented there.

---

## Architecture

The frontend never does any AI calls directly — everything goes through the FastAPI backend.

```
Browser (Next.js 14)
    │
    └─→ FastAPI :8000
            │
            ├─ Middleware adds correlation ID + response time to every request
            │
            ├─ API router validates input with Pydantic
            │
            ├─ Service layer runs the business logic
            │      (AI call → validate output → compute scores → save to DB)
            │
            └─ AI Provider (abstract class)
                   │
                   └─ grok-4 via Azure AI Foundry (OpenAI-compatible endpoint)

Database: SQLite via SQLAlchemy
Tables: categories · products · proposals · ai_logs
```

The `ai_logs` table captures every single AI call — prompt version, token counts, latency, raw input/output, and whether parsing succeeded. Makes debugging and prompt comparison much easier.

---

## AI prompt design

A few deliberate choices I made here:

**Constrained JSON output**
Rather than asking the model to "return JSON" and then parsing the response (which breaks on formatting quirks), I pass the expected Pydantic schema as part of the request config. The model is forced to produce output that matches the schema structure exactly with zero parsing failures.

**Retry with error context**
If an AI call fails validation (e.g. returns a category that's not in the predefined list), the retry doesn't just replay the same prompt. It injects the specific error into the next attempt: "Previous attempt returned 'eco-friendly' — that's not a valid category. Valid options are: ...". Gives the model something to actually fix.

**Prompt versioning**
Every prompt file has a `PROMPT_VERSION` constant. Every AI call logs this version. So if a new prompt regresses accuracy, you can immediately see which calls used which version and roll back.

**Separation of concerns across steps**
The proposal generator uses two separate AI calls on purpose. First call focuses purely on product selection given the budget and catalog. Second call focuses purely on estimating environmental impact from the final validated quantities. Doing both in one prompt made the output messier and harder to validate — splitting them cleaned things up significantly.

**Rules for tricky material logic**
The categorization prompt explicitly encodes things like "beeswax is NOT vegan" and "bamboo → plastic-free + biodegradable." Without these, the model would sometimes label beeswax candles as vegan or miss sustainability filters it should have caught. A few lines of explicit rules in the system prompt fixed it completely.

---

## Running it locally

**Backend**
```
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed_data
uvicorn app.main:app --reload --port 8000
```

API docs → http://localhost:8000/docs

**Frontend**
```
cd frontend
npm install
npm run dev
```

Dashboard → http://localhost:3000

---

## A few things worth noting

- AI suggests, Python validates. Prices, sustainability scores, and cost breakdowns never come from the AI — only from deterministic server logic.
- Every AI call is logged (tokens, latency, prompt version, raw I/O) in an `ai_logs` table. There is a logs page in the UI to browse them.
- The AI provider is behind an abstract class — swapping Gemini for OpenAI or Claude is just a new file.
- Light/dark mode toggle in the nav.

---

*Samir — Rayeva AI Systems Assignment*
