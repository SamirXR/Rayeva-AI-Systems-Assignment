# Rayeva AI Systems Assignment

Built for the Rayeva AI internship assignment. A full-stack AI platform for sustainable commerce — product categorization, B2B proposal generation, and impact reporting.

**Stack:** FastAPI · Next.js 14 · SQLite · grok-4 (Azure AI Foundry)

---

## What's inside

**Module 1 — AI Product Categorizer** (fully built)
Drop in a product name + description and the AI assigns a category, generates SEO tags, picks sustainability filters, and gives it a score. The score itself is deterministic Python logic, not AI — keeps it auditable.

**Module 2 — B2B Proposal Generator** (fully built)
Two-step AI pipeline: first call picks the product mix, then server-side Python validates all the math (GST, shipping, discounts), then a second AI call adds the impact story. Frontend has PDF export.

**Module 3 & 4 — Impact Reporting / WhatsApp Bot** (architecture only)
Full design written up in `backend/app/services/module3_impact_architecture.py` and `module4_whatsapp_architecture.py`. Didn't implement them but the schemas, endpoints, and logic are all documented there.

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
