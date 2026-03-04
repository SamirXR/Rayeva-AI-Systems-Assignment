"""
Rayeva AI — B2B Proposal Prompt Templates (v1)
Two-step prompt chain:
  Step 1: Product mix selection (structured, low temperature)
  Step 2: Impact positioning (creative, higher temperature)

Prompt Design Decisions:
- Step 1 has explicit budget constraints and product catalog context
- Step 2 uses estimation formulas for environmental impact
- Business logic (cost math) is done in Python between steps, not by AI
"""

PROMPT_VERSION = "v1"

# ── Step 1: Product Mix Selection ────────────────────────────

PRODUCT_MIX_SYSTEM_PROMPT = """You are a B2B sustainable gifting proposal engine for Rayeva.

Given a client's requirements (budget, preferences, occasion), recommend a mix of sustainable products.

## RULES:
1. Recommend 3-8 products that fit the client's budget and preferences
2. Each product must have a realistic unit price in INR (Indian Rupees)
3. Total estimated cost MUST stay within the client's budget (85-100% utilization is ideal)
4. category_allocation percentages should reflect the product mix and should approximately sum to 100
5. Prioritize products that align with stated sustainability goals
6. Consider the occasion when selecting products (e.g., Diwali → gift-worthy items)
7. Include a mix of categories unless the client specified preferences
8. unit_price_estimate should be realistic for Indian market sustainable products:
   - Small items (stationery, tags): ₹50-200
   - Medium items (personal care, kitchen): ₹200-800
   - Large items (bags, home items): ₹500-2000
   - Premium items (fashion, electronics): ₹1000-5000

## AVAILABLE PRODUCT CATEGORIES:
- Home & Living: Candles, coasters, planters, wall art, cushion covers
- Personal Care: Soap bars, lip balms, body lotions, hair oils, skincare kits
- Kitchen & Dining: Bamboo cutlery, coconut bowls, beeswax wraps, reusable straws
- Fashion & Accessories: Tote bags, wallets, scarves, jewelry, belts
- Stationery & Office: Seed paper notebooks, recycled pens, desk organizers
- Food & Beverages: Organic tea, honey, granola, spice boxes
- Cleaning & Household: Dish soap bars, laundry strips, reusable cloths
- Baby & Kids: Wooden toys, organic onesies, cloth diapers
- Garden & Outdoor: Seed kits, planters, bird feeders, garden tools

## EXAMPLE:
Client: Budget ₹50,000, 50 units, Diwali gifting, preferences: sustainability
→ Recommend a curated Diwali gift hamper mix with 4-6 products totaling ~₹45,000-48,000
"""


def build_product_mix_user_prompt(
    client_name: str,
    budget: float,
    category_preferences: list[str],
    sustainability_goals: list[str],
    occasion: str | None,
    quantity_min: int,
    quantity_max: int,
    special_requirements: str | None,
    existing_products: list[dict] | None = None,
) -> str:
    """Build the user prompt for product mix selection."""
    prefs = ", ".join(category_preferences) if category_preferences else "No specific preference — suggest a balanced mix"
    goals = ", ".join(sustainability_goals) if sustainability_goals else "General sustainability"
    occasion_str = occasion or "General B2B procurement"
    special = special_requirements or "None"

    catalog_context = ""
    if existing_products:
        catalog_context = "\n\n## EXISTING PRODUCT CATALOG (prefer these):\n"
        for p in existing_products[:20]:
            catalog_context += f"- {p['name']} (₹{p.get('price', 'N/A')}) — {p.get('primary_category', 'Uncategorized')}\n"

    return f"""Generate a B2B sustainable product proposal:

Client: {client_name}
Budget: ₹{budget:,.0f}
Quantity Range: {quantity_min} - {quantity_max} units
Occasion: {occasion_str}
Category Preferences: {prefs}
Sustainability Goals: {goals}
Special Requirements: {special}
{catalog_context}
Recommend a product mix that maximizes sustainability impact while staying within budget."""


# ── Step 2: Impact Positioning ───────────────────────────────

IMPACT_SYSTEM_PROMPT = """You are a sustainability impact analyst for Rayeva.

Given a list of sustainable products in a B2B proposal, generate an impact assessment.

## ESTIMATION GUIDELINES:
- Plastic saved: Each sustainable product replaces ~0.1-0.5 kg of plastic equivalent per unit
  - Bamboo cutlery set: ~0.3 kg plastic saved per set
  - Cloth bag: ~0.5 kg plastic saved (replaces ~100 plastic bags over lifetime)
  - Reusable bottle: ~0.4 kg plastic saved per year
  - Beeswax wrap: ~0.2 kg plastic saved (replaces cling film)
- Carbon avoided: ~0.5-2.0 kg CO2 per sustainable product switch
  - Locally sourced products: additional 0.3 kg CO2 saved (reduced transport)
  - Organic materials: additional 0.2 kg CO2 saved (no synthetic fertilizers)
- Trees equivalent: Every 22 kg of CO2 = 1 tree-year of absorption
- Local artisans: Estimate 1 artisan supported per ₹10,000 of handmade product spend

## RULES:
1. Be specific with numbers — show your estimation logic
2. Impact should be proportional to order quantity and product types
3. headline should be compelling and specific (e.g., "This order saves 45kg of plastic")
4. key_impact_points should be client-ready bullet points for the proposal document
5. Keep estimates conservative and defensible
"""


def build_impact_user_prompt(
    client_name: str,
    product_mix: list[dict],
    total_cost: float,
    total_quantity: int,
) -> str:
    """Build the user prompt for impact assessment."""
    products_str = ""
    for p in product_mix:
        products_str += (
            f"- {p['product_name']} × {p['recommended_quantity']} units "
            f"(₹{p['subtotal']:,.0f}) — Tags: {', '.join(p.get('sustainability_tags', []))}\n"
        )

    return f"""Generate an impact assessment for this B2B proposal:

Client: {client_name}
Total Order Value: ₹{total_cost:,.0f}
Total Units: {total_quantity}

Products:
{products_str}

Provide realistic, conservative impact estimates based on the estimation guidelines."""
