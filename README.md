# Rayeva AI — Sustainable Commerce Platform

> **AI-Powered Product Categorization, B2B Proposal Generation & Impact Reporting**

Built for the **Rayeva AI Systems Assignment** (Full Stack / AI Intern).

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Gemini](https://img.shields.io/badge/Gemini-3.1_Flash_Lite-orange)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Module 1: AI Auto-Category & Tag Generator](#module-1-ai-auto-category--tag-generator)
- [Module 2: AI B2B Proposal Generator](#module-2-ai-b2b-proposal-generator)
- [Module 3: AI Impact Reporting (Architecture)](#module-3-ai-impact-reporting-architecture)
- [Module 4: AI WhatsApp Bot (Architecture)](#module-4-ai-whatsapp-bot-architecture)
- [AI Prompt Design & Strategy](#ai-prompt-design--strategy)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Setup & Run](#setup--run)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Design Decisions & Trade-offs](#design-decisions--trade-offs)
- [What I'd Build Next](#what-id-build-next)

---

## Overview

This project implements **four AI-powered modules** for Rayeva's sustainable commerce platform:

| Module | Status | Description |
|--------|--------|-------------|
| **Module 1** — Auto-Category & Tags | ✅ Fully Implemented | AI categorizes products into 10 predefined categories, assigns SEO tags & sustainability filters, computes a rules-based sustainability score |
| **Module 2** — B2B Proposal Generator | ✅ Fully Implemented | Multi-step AI pipeline: product mix recommendation → server-side cost validation → impact estimation → complete proposal |
| **Module 3** — Impact Reporting | 📐 Architecture Outline | DB schema, API design, estimation formulas, AI prompt for narrative generation |
| **Module 4** — WhatsApp Bot | 📐 Architecture Outline | Webhook-based design, intent classification, escalation rules, adapter pattern |

**Key principle:** _"AI suggests, business logic validates."_ The AI generates recommendations but all pricing math, sustainability scores, and category validation are deterministic server-side logic.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js 14)                     │
│  Dashboard │ Categorizer │ Proposals │ Logs                  │
│                  ↕ /api proxy → :8000                        │
├─────────────────────────────────────────────────────────────┤
│                  FASTAPI BACKEND (:8000)                     │
│                                                              │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ API v1  │  │  Services    │  │ AI Provider  │            │
│  │ Routers │→ │ (Biz Logic)  │→ │  Abstraction │            │
│  └─────────┘  └──────────────┘  └──────┬───────┘            │
│       │              │                  │                    │
│       │     ┌────────┴────────┐    ┌────┴──────┐            │
│       │     │  Pydantic v2    │    │  Gemini   │            │
│       │     │  Validation     │    │  3.1 API  │            │
│       │     └────────┬────────┘    └───────────┘            │
│       │              │                                       │
│  ┌────┴──────────────┴─────────────────────────┐            │
│  │           SQLAlchemy 2.0 + SQLite            │            │
│  │  products │ categories │ proposals │ ai_logs  │            │
│  └──────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

1. **Client** sends request (e.g., categorize product)
2. **CorrelationIDMiddleware** assigns UUID, tracks response time
3. **API router** validates input via Pydantic schema
4. **Service layer** orchestrates: AI call → business logic validation → DB persistence
5. **AIService** wraps the provider with retry logic (up to 2 retries with error context injection)
6. **GeminiProvider** calls `google-genai` SDK with `response_schema` for constrained JSON
7. All AI calls are logged to `ai_logs` table (tokens, latency, prompt version, success)

---

## Module 1: AI Auto-Category & Tag Generator

### What It Does

Given a product (name, description, materials, price), the AI:
1. Assigns a **primary category** from 10 predefined categories
2. Generates **5 SEO tags** optimized for search
3. Selects **sustainability filters** from 12 predefined options
4. Server-side logic computes a **sustainability score (0–10)** using material analysis

### AI → Validation Pipeline

```
Product Input
    │
    ├─→ AI: Classify category + tags + filters
    │     Uses: Constrained JSON decoding (response_schema)
    │     Model: gemini-3.1-flash-lite-preview
    │
    ├─→ Validate: Is category in predefined list?
    │     Yes → continue
    │     No  → fuzzy match → flag for review
    │
    ├─→ Compute: Sustainability score (rules-based)
    │     Material analysis (bamboo +1.5, organic-cotton +1.5, etc.)
    │     Filter bonuses (plastic-free +1.0, biodegradable +0.8, etc.)
    │     Normalized to 0–10 scale
    │
    └─→ Store: Product + AI metadata in database
```

### Sustainability Scoring (Business Logic, Not AI)

The sustainability score is **deterministic** — computed from material keywords and sustainability filters:

| Material | Score | Filter | Score |
|----------|-------|--------|-------|
| Bamboo | +1.5 | Plastic-free | +1.0 |
| Organic cotton | +1.5 | Biodegradable | +0.8 |
| Recycled | +1.2 | Vegan | +0.6 |
| Jute/hemp | +1.3 | Fair-trade | +0.7 |
| Beeswax | +1.0 | Handmade | +0.5 |
| Coconut | +0.8 | Refillable | +0.9 |

**Why not let AI score it?** Sustainability scores affect business decisions (pricing, partnerships). A rules-based approach is auditable, consistent, and doesn't hallucinate numbers.

### Categories (10 Predefined)

Kitchen & Dining · Personal Care · Home & Living · Fashion & Accessories · Stationery & Office · Garden & Outdoor · Baby & Kids · Travel & On-the-Go · Cleaning & Household · Gifting & Hampers

---

## Module 2: AI B2B Proposal Generator

### What It Does

Given client requirements (company name, budget, quantity, occasion), generates a complete B2B proposal:
1. **AI Step 1:** Recommend product mix with quantities and pricing
2. **Server-side:** Validate costs, apply GST (18%), shipping (₹25/unit), volume discounts
3. **AI Step 2:** Estimate environmental impact (plastic saved, carbon avoided)
4. **Combine:** Full proposal with cost breakdown and impact summary

### Multi-Step Pipeline

```
Client Requirements
    │
    ├─→ Step 1: Query DB for available products
    │
    ├─→ Step 2: AI recommends product mix
    │     Input: budget, quantity, category preference, products catalog
    │     Output: [{product, quantity, unit_price, reason}]
    │
    ├─→ Step 3: Business Logic validates costs
    │     ├─ Unit prices within ±20% of catalog
    │     ├─ Total ≤ budget
    │     ├─ GST = 18% of subtotal
    │     ├─ Shipping = ₹25 × total_units
    │     ├─ Volume discount:
    │     │    100+ units → 5%
    │     │    250+ units → 8%
    │     │    500+ units → 12%
    │     └─ Grand total = subtotal + GST + shipping − discount
    │
    ├─→ Step 4: AI estimates environmental impact
    │     Input: product mix with quantities and materials
    │     Output: plastic_saved, carbon_avoided, water_saved, artisans_supported
    │
    └─→ Step 5: Store proposal + return complete response
```

### Why Two AI Calls?

Separation of concerns. The product recommendation call needs the product catalog and budget constraints. The impact estimation call needs the final validated quantities. Chaining them through a single prompt would make the output harder to validate.

---

## Module 3: AI Impact Reporting (Architecture)

> **📐 Designed but not implemented** — See `backend/app/services/module3_impact_architecture.py` for full detail.

### Key Design Points

- **DB Schema:** `orders` and `impact_reports` tables with full calculation transparency
- **Estimation Logic:** Deterministic formulas per product type (e.g., bamboo cutlery → 0.3 kg plastic saved/unit)
- **AI Role:** Only generates the human-readable impact narrative — all numbers come from business logic
- **Endpoints:** POST `/orders/{id}/impact-report`, GET dashboard aggregates

### Estimation Formulas

```
Plastic Saved = Σ (product_plastic_factor × quantity)
Carbon Avoided = Σ ((0.8 + local_bonus + organic_bonus) × quantity)
Trees Equivalent = carbon_avoided / 22.0 kg CO₂
```

---

## Module 4: AI WhatsApp Bot (Architecture)

> **📐 Designed but not implemented** — See `backend/app/services/module4_whatsapp_architecture.py` for full detail.

### Key Design Points

- **Webhook-based:** Compatible with WhatsApp Business API, demo runs via web chat UI
- **Intent Classification:** order_status, return_policy, refund_request, product_inquiry, general, escalation
- **Adapter Pattern:** `MessageAdapter` ABC → `WebChatAdapter` (demo) / `TwilioAdapter` / `MetaAdapter`
- **Auto-Escalation Rules:**
  - All refund requests → human agent
  - Order value > ₹5,000 + complaint → human agent
  - 3+ messages without resolution → human agent
  - AI confidence < 0.5 → human agent
- **Streaming:** Uses `generate_content_stream` for real-time typing feel

---

## AI Prompt Design & Strategy

### Constrained JSON Decoding

Instead of asking the AI to "return JSON" and hoping for the best, I use the `google-genai` SDK's `response_schema` parameter. This forces the model to output valid JSON matching a Pydantic schema:

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=user_prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        response_schema=AICategoryOutput,  # Pydantic model
        thinking_config=types.ThinkingConfig(thinking_budget=1024),
    ),
)
```

**Why this matters:** Zero parsing failures. The model is structurally forced to produce valid output matching the schema, eliminating the need for regex extraction or JSON repair.

### Retry with Error Context

When an AI call fails validation (e.g., returns a category not in the predefined list), the retry doesn't just repeat the same prompt. It injects the error message into the prompt:

```python
# On retry, the prompt becomes:
f"Previous attempt failed: '{error_message}'. "
f"Correct the issue and try again.\n\n{original_prompt}"
```

This gives the model actionable feedback, making retries much more likely to succeed.

### Prompt Versioning

Every prompt file has a `PROMPT_VERSION` constant (e.g., `"v1"`). Every AI call logs this version in the `ai_logs` table. This enables:
- A/B testing between prompt versions
- Debugging which prompt version caused a specific output
- Rolling back to previous prompts if a new version regresses

### Few-Shot Examples

The categorization prompt includes 2 worked examples with reasoning:

```
Example 1:
Product: "Bamboo Cutlery Set – Reusable fork, knife, spoon made from 100% organic bamboo"
→ Category: kitchen-and-dining
→ Tags: ["bamboo cutlery set", "reusable utensils", ...]
→ Filters: ["plastic-free", "biodegradable", "vegan"]
→ Reasoning: Kitchen utensil → kitchen-and-dining. Bamboo = plastic-free + biodegradable.
```

### Material Detection Rules

The prompt encodes specific material→filter mappings to reduce hallucination:

```
bamboo → plastic-free, biodegradable
beeswax → NOT vegan (beeswax is animal-derived)
organic cotton → organic, chemical-free
recycled materials → recycled
```

This is critical because an LLM might incorrectly label beeswax products as "vegan" without explicit guidance.

---

## Database Schema

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  categories  │     │   products   │     │  proposals   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ id           │←────│ primary_      │     │ id           │
│ name         │     │  category_id  │     │ client_name  │
│ slug         │     │ name          │     │ budget       │
│ description  │     │ description   │     │ product_mix  │
│ icon         │     │ materials     │     │ cost_        │
│              │     │ price         │     │  breakdown   │
│              │     │ seo_tags (JSON)│    │ impact_      │
│              │     │ sustainability│     │  summary     │
│              │     │  _filters(JSON)│    │ total_cost   │
│              │     │ sustainability│     │ status       │
│              │     │  _score       │     │              │
│              │     │ ai_metadata   │     │              │
└──────────────┘     └──────────────┘     └──────────────┘

                     ┌──────────────┐
                     │   ai_logs    │
                     ├──────────────┤
                     │ id           │
                     │ correlation_ │
                     │  id          │
                     │ module       │
                     │ prompt_      │
                     │  version     │
                     │ model_name   │
                     │ input_tokens │
                     │ output_tokens│
                     │ latency_ms   │
                     │ raw_input    │
                     │ raw_output   │
                     │ parsed_      │
                     │  success     │
                     │ error_msg    │
                     └──────────────┘
```

---

## API Reference

### Module 1 — Categorization

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/categorize` | Categorize a single product |
| `POST` | `/api/v1/categorize/batch` | Categorize up to 20 products (concurrent, semaphore=5) |
| `GET`  | `/api/v1/categories` | List all 10 predefined categories |
| `GET`  | `/api/v1/products` | List all categorized products |
| `GET`  | `/api/v1/products/{id}` | Get product with AI metadata |

### Module 2 — Proposals

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/proposals/generate` | Generate a B2B proposal |
| `GET`  | `/api/v1/proposals/{id}` | Get proposal by ID |
| `GET`  | `/api/v1/proposals` | List all proposals |

### Observability

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/v1/logs` | AI call logs (filter by module, success) |
| `GET`  | `/api/v1/metrics` | Aggregated metrics (call count, avg latency, success rate) |
| `GET`  | `/health` | Health check |

---

## Setup & Run

### Prerequisites

- **Python 3.11+** (tested on 3.13.2)
- **Node.js 18+** (tested on 22.14.0)
- **Gemini API key** from [Google AI Studio](https://aistudio.google.com/apikey) (free tier)

### 1. Clone & Environment

```bash
git clone https://github.com/YOUR_USERNAME/rayeva-ai.git
cd rayeva-ai

# Create .env file
cp .env.example .env
# Edit .env → add your GOOGLE_API_KEY
```

### 2. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed sample products (optional — 20 pre-built sustainable products)
python -m app.seed_data

# Run server
uvicorn app.main:app --reload --port 8000
```

The API is now live at **http://localhost:8000** — visit **http://localhost:8000/docs** for interactive Swagger docs.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard is now live at **http://localhost:3000**.

### 4. Quick Test

```bash
# Categorize a product
curl -X POST http://localhost:8000/api/v1/categorize \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bamboo Cutlery Set",
    "description": "Reusable fork, knife, and spoon made from organic bamboo",
    "materials": ["bamboo", "organic cotton pouch"],
    "price": 299.0
  }'

# Generate a B2B proposal
curl -X POST http://localhost:8000/api/v1/proposals/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "TechCorp India",
    "budget": 50000,
    "quantity": 200,
    "occasion": "employee-welcome-kit",
    "category_preference": "kitchen-and-dining"
  }'
```

---

## Project Structure

```
rayeva-ai/
├── README.md
├── .env.example
├── .gitignore
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan
│   │   ├── config.py               # Pydantic Settings (env-based)
│   │   ├── database.py             # SQLAlchemy 2.0 + SQLite
│   │   ├── middleware.py            # Correlation ID + response time
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── category.py          # 10 predefined categories
│   │   │   ├── product.py           # Products with AI metadata
│   │   │   ├── proposal.py          # B2B proposals
│   │   │   └── ai_log.py            # AI call observability
│   │   │
│   │   ├── schemas/                 # Pydantic I/O schemas
│   │   │   ├── category.py          # Enums, AI output schema
│   │   │   └── proposal.py          # Multi-step output schemas
│   │   │
│   │   ├── ai/                      # AI abstraction layer
│   │   │   ├── base.py              # AIProvider ABC
│   │   │   ├── gemini.py            # Gemini provider implementation
│   │   │   ├── service.py           # Orchestrator (retry, logging)
│   │   │   └── models.py            # AIResult[T], AIError
│   │   │
│   │   ├── prompts/                 # Versioned prompt templates
│   │   │   ├── category_v1.py       # Categorization prompt + few-shot
│   │   │   └── proposal_v1.py       # Two-step proposal prompts
│   │   │
│   │   ├── services/                # Business logic orchestrators
│   │   │   ├── category_service.py   # AI + validation + scoring
│   │   │   ├── proposal_service.py   # Multi-step pipeline
│   │   │   ├── module3_impact_architecture.py
│   │   │   └── module4_whatsapp_architecture.py
│   │   │
│   │   ├── api/v1/                   # Route handlers
│   │   │   ├── category.py
│   │   │   ├── proposals.py
│   │   │   └── logs.py
│   │   │
│   │   └── seed_data.py             # 20 sample sustainable products
│   │
│   └── tests/
│       └── test_business_logic.py    # 12 tests (scoring, validation, math)
│
└── frontend/
    ├── package.json
    ├── next.config.js               # API proxy → :8000
    ├── tailwind.config.js
    ├── lib/api.ts                   # Typed API client
    └── app/
        ├── layout.tsx               # Nav bar + shell
        ├── page.tsx                 # Dashboard (metrics, charts)
        ├── categorize/page.tsx      # Product categorizer
        ├── proposals/page.tsx       # Proposal generator
        └── logs/page.tsx            # AI call log viewer
```

---

## Testing

```bash
cd backend
pytest tests/test_business_logic.py -v
```

### Test Coverage

| Suite | Tests | What's Verified |
|-------|-------|-----------------|
| Sustainability Scoring | 5 | Bamboo score, organic cotton, beeswax, recycled materials, score normalization to 0–10 |
| Category Validation | 4 | Exact match, case-insensitive match, invalid category flagging, slug normalization |
| Cost Breakdown | 3 | Volume discount tiers (100/250/500), GST calculation, shipping calculation |

All 12 tests passing ✅

---

## Design Decisions & Trade-offs

### 1. SQLite over PostgreSQL
**Why:** Zero setup, single file (`rayeva.db`), perfect for demo/assignment scope. The app uses SQLAlchemy ORM — switching to Postgres requires changing one environment variable (`DATABASE_URL=postgresql://...`). No code changes needed.

### 2. Constrained Decoding over Free-Text + Parsing
**Why:** Using `response_schema` with `response_mime_type="application/json"` eliminates JSON parsing failures entirely. The model is structurally forced to output valid data matching the Pydantic schema. This is more reliable than extracting JSON from free-text with regex.

### 3. Rules-Based Scoring over AI Scoring
**Why:** Sustainability scores appear in B2B proposals and affect pricing decisions. A rules-based approach is:
- **Auditable** — you can explain exactly why a product scored 7.2
- **Consistent** — same product always gets the same score
- **Fast** — no API call needed for scoring

### 4. Provider Abstraction (AIProvider ABC)
**Why:** The `GeminiProvider` implements an abstract base class. Adding OpenAI, Claude, or Mistral as alternatives requires only implementing 2 methods (`generate`, `generate_stream`). Zero changes to service layer code.

### 5. Two-Step Proposal Pipeline over Single Prompt
**Why:** Separating product recommendation from impact estimation allows:
- Validating and correcting prices between steps
- Using different prompt strategies for each task
- Independent retry on failure (Step 1 might succeed but Step 2 fail)

### 6. Correlation IDs for Observability
**Why:** Every request gets a UUID. Every AI call logs this UUID. When debugging "why did this product get categorized wrong?", you can trace the exact prompt, model output, and validation steps from a single correlation ID in the `ai_logs` table.

---

## What I'd Build Next

Given more time, here's what I'd prioritize:

1. **PDF Export** — Generate branded B2B proposal PDFs using WeasyPrint (dependency already in `requirements.txt`)
2. **A/B Prompt Testing** — Prompt version tracking is already built; add a UI to compare accuracy across prompt versions
3. **WebSocket Streaming** — The `generate_stream` method is implemented in `GeminiProvider`; wire it to a WebSocket endpoint for real-time proposal generation
4. **Rate Limiting** — Add `slowapi` middleware with per-IP rate limits on AI endpoints
5. **Alembic Migrations** — The setup currently uses `create_all()` at startup; Alembic would enable safe schema evolution in production
6. **Module 3 & 4 Implementation** — The architecture is fully designed; implementation would follow the same pattern as Modules 1 & 2

---

## Tech Stack Summary

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI + Pydantic v2 | Type-safe, async, auto-generates OpenAPI docs |
| AI | google-genai + Gemini 3.1 Flash Lite | Constrained JSON decoding, free tier, fast |
| Database | SQLAlchemy 2.0 + SQLite | Zero setup, ORM-based, swappable to Postgres |
| Frontend | Next.js 14 + Tailwind CSS | App Router, server-side rendering, rapid UI |
| Testing | pytest | Industry standard, async support |
| Logging | structlog (JSON) | Structured logs, correlation IDs |
| Observability | ai_logs table + /metrics endpoint | Every AI call tracked with prompt version, tokens, latency |

---

*Built by Samir — Rayeva AI Systems Assignment Submission*
