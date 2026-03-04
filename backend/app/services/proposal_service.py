"""
Rayeva AI — Proposal Service (Module 2 Business Logic)
Multi-step AI pipeline with server-side cost validation.

Architecture:
  Step 1: AI recommends product mix
  Step 2: Business logic validates & recalculates all costs (AI does NOT do math)
  Step 3: AI generates impact positioning
  Step 4: Compile final proposal and store in DB
"""

import structlog
from sqlalchemy.orm import Session

from app.ai.service import AIService
from app.ai.models import AIResult
from app.models.proposal import Proposal
from app.models.product import Product
from app.schemas.proposal import (
    AIProposalOutput,
    AIImpactOutput,
    ProposalRequest,
    ProposalResponse,
    CostBreakdownResponse,
)
from app.prompts.proposal_v1 import (
    PROMPT_VERSION,
    PRODUCT_MIX_SYSTEM_PROMPT,
    IMPACT_SYSTEM_PROMPT,
    build_product_mix_user_prompt,
    build_impact_user_prompt,
)

logger = structlog.get_logger()

# ── Business Constants ───────────────────────────────────────

GST_PERCENT = 18.0
SHIPPING_RATE_PER_UNIT = 25.0  # ₹25 per unit (average)
VOLUME_DISCOUNT_THRESHOLDS = [
    (100, 5.0),   # 100+ units → 5% discount
    (250, 8.0),   # 250+ units → 8% discount
    (500, 12.0),  # 500+ units → 12% discount
]


def compute_discount_percent(total_quantity: int) -> float:
    """Volume-based discount — deterministic business rule."""
    discount = 0.0
    for threshold, pct in VOLUME_DISCOUNT_THRESHOLDS:
        if total_quantity >= threshold:
            discount = pct
    return discount


def validate_and_build_cost_breakdown(
    product_mix: list[dict],
    total_quantity: int,
) -> CostBreakdownResponse:
    """
    Server-side cost calculation. ALL MATH IS DONE HERE, NOT BY AI.
    AI provides product suggestions; Python does the arithmetic.
    """
    product_costs = []
    subtotal = 0.0

    for p in product_mix:
        # Recalculate subtotal from unit price × quantity (don't trust AI's math)
        unit_price = float(p["unit_price_estimate"])
        qty = int(p["recommended_quantity"])
        line_total = round(unit_price * qty, 2)
        subtotal += line_total
        product_costs.append({
            "product_name": p["product_name"],
            "unit_price": unit_price,
            "quantity": qty,
            "line_total": line_total,
        })

    # Apply business rules
    discount_pct = compute_discount_percent(total_quantity)
    discount_amount = round(subtotal * discount_pct / 100, 2)
    after_discount = subtotal - discount_amount

    gst_amount = round(after_discount * GST_PERCENT / 100, 2)
    shipping = round(total_quantity * SHIPPING_RATE_PER_UNIT, 2)
    grand_total = round(after_discount + gst_amount + shipping, 2)

    return CostBreakdownResponse(
        product_costs=product_costs,
        subtotal=round(subtotal, 2),
        gst_percent=GST_PERCENT,
        gst_amount=gst_amount,
        shipping_estimate=shipping,
        discount_percent=discount_pct,
        discount_amount=discount_amount,
        grand_total=grand_total,
    )


# ── Main Service ─────────────────────────────────────────────

class ProposalService:
    """
    Module 2 business logic.
    Multi-step pipeline: AI product mix → cost validation → AI impact → store.
    """

    def __init__(self, db: Session, correlation_id: str = ""):
        self.db = db
        self.ai_service = AIService(db=db, correlation_id=correlation_id)

    async def generate_proposal(self, request: ProposalRequest) -> ProposalResponse:
        """
        Full proposal generation pipeline.
        """
        total_latency = 0.0

        # ── Step 1: Get existing products from DB for context ────
        existing_products = []
        db_products = self.db.query(Product).filter(
            Product.primary_category.isnot(None)
        ).limit(20).all()
        for p in db_products:
            existing_products.append({
                "name": p.name,
                "price": p.price,
                "primary_category": p.primary_category,
            })

        # ── Step 2: AI generates product mix ─────────────────────
        user_prompt = build_product_mix_user_prompt(
            client_name=request.client_name,
            budget=request.budget,
            category_preferences=request.category_preferences,
            sustainability_goals=request.sustainability_goals,
            occasion=request.occasion,
            quantity_min=request.quantity_min,
            quantity_max=request.quantity_max,
            special_requirements=request.special_requirements,
            existing_products=existing_products if existing_products else None,
        )

        mix_result: AIResult[AIProposalOutput] = await self.ai_service.generate(
            module="proposal",
            prompt_version=PROMPT_VERSION,
            system_prompt=PRODUCT_MIX_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=AIProposalOutput,
        )
        total_latency += mix_result.latency_ms
        ai_mix = mix_result.parsed

        # ── Step 3: Business logic validates all costs ───────────
        product_mix_dicts = [p.model_dump() for p in ai_mix.product_recommendations]
        total_quantity = sum(p.recommended_quantity for p in ai_mix.product_recommendations)

        cost_breakdown = validate_and_build_cost_breakdown(
            product_mix=product_mix_dicts,
            total_quantity=total_quantity,
        )

        budget_utilization = round(
            (cost_breakdown.grand_total / request.budget) * 100, 1
        )

        # ── Step 4: AI generates impact assessment ───────────────
        impact_prompt = build_impact_user_prompt(
            client_name=request.client_name,
            product_mix=product_mix_dicts,
            total_cost=cost_breakdown.subtotal,
            total_quantity=total_quantity,
        )

        impact_result: AIResult[AIImpactOutput] = await self.ai_service.generate(
            module="proposal_impact",
            prompt_version=PROMPT_VERSION,
            system_prompt=IMPACT_SYSTEM_PROMPT,
            user_prompt=impact_prompt,
            output_schema=AIImpactOutput,
            temperature=0.7,  # Slightly creative for narrative
            thinking_level="LOW",
        )
        total_latency += impact_result.latency_ms
        ai_impact = impact_result.parsed

        # ── Step 5: Store in database ────────────────────────────
        proposal = Proposal(
            client_name=request.client_name,
            budget=request.budget,
            category_preferences=request.category_preferences,
            sustainability_goals=request.sustainability_goals,
            occasion=request.occasion,
            quantity_min=request.quantity_min,
            quantity_max=request.quantity_max,
            special_requirements=request.special_requirements,
            product_mix=product_mix_dicts,
            budget_allocation=ai_mix.category_allocation,
            cost_breakdown=cost_breakdown.model_dump(),
            impact_summary=ai_impact.model_dump(),
            status="generated",
        )
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)

        # ── Step 6: Build response ───────────────────────────────
        return ProposalResponse(
            proposal_id=proposal.id,
            client_name=request.client_name,
            budget=request.budget,
            product_mix=ai_mix.product_recommendations,
            category_allocation=ai_mix.category_allocation,
            strategy_summary=ai_mix.strategy_summary,
            cost_breakdown=cost_breakdown,
            impact=ai_impact,
            budget_utilization_percent=budget_utilization,
            ai_model=mix_result.model,
            prompt_version=PROMPT_VERSION,
            total_latency_ms=round(total_latency, 2),
        )
