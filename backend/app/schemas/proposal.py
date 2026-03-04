"""
Rayeva AI — B2B Proposal Pydantic Schemas
Used for API validation AND AI response_schema enforcement.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── AI Output Schemas (response_schema for Gemini) ──────────

class AIProductRecommendation(BaseModel):
    """Single product recommendation from AI."""
    product_name: str = Field(description="Name of the recommended product")
    category: str = Field(description="Product category")
    unit_price_estimate: float = Field(description="Estimated unit price in INR")
    recommended_quantity: int = Field(description="Recommended quantity for this order")
    subtotal: float = Field(description="unit_price_estimate * recommended_quantity")
    sustainability_tags: list[str] = Field(description="Sustainability attributes of this product")
    selection_reasoning: str = Field(description="Why this product fits the client's needs")


class AIProposalOutput(BaseModel):
    """Full AI output for proposal generation — Step 1: Product Mix."""
    product_recommendations: list[AIProductRecommendation] = Field(
        description="3-8 recommended sustainable products"
    )
    category_allocation: dict[str, float] = Field(
        description="Percentage budget allocation per category (must sum close to 100)"
    )
    total_estimated_cost: float = Field(
        description="Sum of all product subtotals in INR"
    )
    budget_utilization_percent: float = Field(
        description="Percentage of client budget used (should be 85-100%)"
    )
    strategy_summary: str = Field(
        description="2-3 sentence summary of the product selection strategy"
    )


class AIImpactOutput(BaseModel):
    """AI output for impact positioning — Step 2."""
    headline: str = Field(description="Compelling one-line impact headline")
    impact_summary: str = Field(description="3-4 sentence impact narrative for the proposal")
    plastic_saved_kg: float = Field(description="Estimated plastic saved in kg")
    carbon_avoided_kg: float = Field(description="Estimated carbon emissions avoided in kg")
    trees_equivalent: float = Field(description="Environmental impact expressed in tree equivalents")
    local_artisans_supported: int = Field(description="Estimated number of local artisans supported")
    key_impact_points: list[str] = Field(description="3-5 bullet points for the proposal")


# ── API Request / Response Schemas ───────────────────────────

class ProposalRequest(BaseModel):
    """Client input for generating a B2B proposal."""
    client_name: str = Field(..., min_length=2, max_length=200)
    budget: float = Field(..., gt=0, description="Total budget in INR")
    category_preferences: list[str] = Field(
        default=[],
        description="Preferred product categories"
    )
    sustainability_goals: list[str] = Field(
        default=[],
        description="E.g., plastic-free, carbon-neutral, organic"
    )
    occasion: Optional[str] = Field(
        None, description="E.g., Diwali corporate gifting, employee welcome kits"
    )
    quantity_min: int = Field(default=10, ge=1)
    quantity_max: int = Field(default=100, ge=1)
    special_requirements: Optional[str] = Field(None, max_length=1000)


class CostBreakdownResponse(BaseModel):
    """Server-validated cost breakdown (math done in Python, not by AI)."""
    product_costs: list[dict]
    subtotal: float
    gst_percent: float
    gst_amount: float
    shipping_estimate: float
    discount_percent: float
    discount_amount: float
    grand_total: float


class ProposalResponse(BaseModel):
    """Full proposal API response."""
    proposal_id: int
    client_name: str
    budget: float

    # AI-generated (Step 1)
    product_mix: list[AIProductRecommendation]
    category_allocation: dict[str, float]
    strategy_summary: str

    # Server-validated cost breakdown (Step 2 — business logic, not AI)
    cost_breakdown: CostBreakdownResponse

    # AI-generated impact (Step 3)
    impact: AIImpactOutput

    # Metadata
    budget_utilization_percent: float
    ai_model: str
    prompt_version: str
    total_latency_ms: float
