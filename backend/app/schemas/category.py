"""
Rayeva AI — Category & Tag Pydantic Schemas
Used for both API request/response validation AND AI response_schema enforcement.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────

class PrimaryCategory(str, Enum):
    HOME_LIVING = "Home & Living"
    PERSONAL_CARE = "Personal Care"
    KITCHEN_DINING = "Kitchen & Dining"
    FASHION_ACCESSORIES = "Fashion & Accessories"
    STATIONERY_OFFICE = "Stationery & Office"
    FOOD_BEVERAGES = "Food & Beverages"
    CLEANING_HOUSEHOLD = "Cleaning & Household"
    BABY_KIDS = "Baby & Kids"
    PET_CARE = "Pet Care"
    GARDEN_OUTDOOR = "Garden & Outdoor"


class SustainabilityFilter(str, Enum):
    PLASTIC_FREE = "plastic-free"
    COMPOSTABLE = "compostable"
    VEGAN = "vegan"
    RECYCLED = "recycled"
    ORGANIC = "organic"
    FAIR_TRADE = "fair-trade"
    BIODEGRADABLE = "biodegradable"
    LOCALLY_SOURCED = "locally-sourced"
    ZERO_WASTE = "zero-waste"
    CRUELTY_FREE = "cruelty-free"
    HANDMADE = "handmade"
    UPCYCLED = "upcycled"


# ── AI Output Schema (used as response_schema in Gemini) ─────

class AICategoryOutput(BaseModel):
    """Schema enforced at Gemini's decoding level via response_schema."""

    primary_category: str = Field(
        description="One of the predefined categories: Home & Living, Personal Care, Kitchen & Dining, Fashion & Accessories, Stationery & Office, Food & Beverages, Cleaning & Household, Baby & Kids, Pet Care, Garden & Outdoor"
    )
    primary_category_confidence: float = Field(
        description="Confidence score 0.0-1.0 for the primary category assignment"
    )
    sub_category: str = Field(
        description="A more specific sub-category within the primary category"
    )
    sub_category_reasoning: str = Field(
        description="Brief explanation for why this sub-category was chosen"
    )
    seo_tags: list[str] = Field(
        description="5-10 SEO-optimized tags for the product"
    )
    sustainability_filters: list[str] = Field(
        description="Applicable sustainability filters from: plastic-free, compostable, vegan, recycled, organic, fair-trade, biodegradable, locally-sourced, zero-waste, cruelty-free, handmade, upcycled"
    )
    detected_materials: list[str] = Field(
        description="Materials detected or inferred from the product description"
    )
    sustainability_reasoning: str = Field(
        description="Brief explanation for the sustainability filter choices"
    )


# ── API Request / Response Schemas ───────────────────────────

class ProductInput(BaseModel):
    """Input from user/API to categorize a product."""
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None


class ProductCategorizationResponse(BaseModel):
    """Full API response after categorization."""
    product_id: int
    name: str
    description: str

    # AI-generated
    primary_category: str
    primary_category_confidence: float
    sub_category: str
    sub_category_reasoning: str
    seo_tags: list[str]
    sustainability_filters: list[str]
    detected_materials: list[str]
    sustainability_score: float
    sustainability_reasoning: str
    needs_human_review: bool

    # Metadata
    ai_model: str
    prompt_version: str
    latency_ms: float
    input_tokens: int
    output_tokens: int


class BatchCategorizationRequest(BaseModel):
    """Batch categorize multiple products."""
    products: list[ProductInput] = Field(..., min_length=1, max_length=50)


class BatchCategorizationResponse(BaseModel):
    """Batch response."""
    results: list[ProductCategorizationResponse]
    total: int
    successful: int
    failed: int
