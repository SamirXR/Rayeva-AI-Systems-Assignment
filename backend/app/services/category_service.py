"""
Rayeva AI — Category Service (Module 1 Business Logic)
Orchestrates AI categorization with business rule validation and sustainability scoring.

Architecture: AI suggests → Business logic validates → Database stores.
The sustainability score is computed via a transparent rules-based algorithm,
not by the AI. AI augments business logic, it doesn't replace it.
"""

import asyncio
from datetime import datetime
from typing import Optional

import structlog
from sqlalchemy.orm import Session

from app.ai.service import AIService
from app.ai.models import AIResult
from app.models.product import Product
from app.schemas.category import (
    AICategoryOutput,
    ProductInput,
    ProductCategorizationResponse,
    PrimaryCategory,
)
from app.prompts.category_v2 import SYSTEM_PROMPT, build_user_prompt, PROMPT_VERSION

logger = structlog.get_logger()


# ── Sustainability Scoring Algorithm (rules-based, not AI) ───

MATERIAL_SCORES: dict[str, float] = {
    "bamboo": 4.0,
    "organic cotton": 3.5,
    "hemp": 4.0,
    "jute": 3.5,
    "coconut shell": 3.0,
    "coconut": 3.0,
    "cork": 3.5,
    "recycled paper": 3.0,
    "recycled plastic": 2.0,
    "reclaimed wood": 3.0,
    "wood": 2.0,
    "soy wax": 2.5,
    "beeswax": 2.5,
    "stainless steel": 1.5,
    "glass": 2.0,
    "cotton": 2.0,
    "linen": 2.5,
    "clay": 2.5,
    "ceramic": 2.0,
    "natural rubber": 2.5,
    "sisal": 3.0,
    "loofah": 3.5,
}

FILTER_SCORES: dict[str, float] = {
    "plastic-free": 2.0,
    "compostable": 2.5,
    "vegan": 1.0,
    "recycled": 2.0,
    "organic": 2.0,
    "fair-trade": 1.5,
    "biodegradable": 2.0,
    "locally-sourced": 1.5,
    "zero-waste": 2.5,
    "cruelty-free": 1.0,
    "handmade": 1.0,
    "upcycled": 2.5,
}


def compute_sustainability_score(
    detected_materials: list[str],
    sustainability_filters: list[str],
) -> float:
    """
    Transparent, rules-based sustainability scoring.
    Returns a score from 0.0 to 10.0.

    Formula: (material_score + filter_score) / max_possible, scaled to 10.
    This is deterministic and auditable — not an AI black box.
    """
    material_score = 0.0
    for material in detected_materials:
        mat_lower = material.lower().strip()
        for key, score in MATERIAL_SCORES.items():
            if key in mat_lower:
                material_score += score
                break

    filter_score = 0.0
    for f in sustainability_filters:
        f_lower = f.lower().strip()
        filter_score += FILTER_SCORES.get(f_lower, 0.0)

    total = material_score + filter_score
    # Normalize to 0-10 scale (cap at 10)
    normalized = min(total / 3.0, 10.0)
    return round(normalized, 2)


# ── Validation: category must be from predefined list ────────

VALID_CATEGORIES = {c.value for c in PrimaryCategory}


def validate_category(category: str) -> tuple[str, bool]:
    """
    Ensure the AI's category is from the predefined list.
    Returns (validated_category, needs_review).
    """
    if category in VALID_CATEGORIES:
        return category, False

    # Fuzzy match: try case-insensitive
    for valid in VALID_CATEGORIES:
        if category.lower().strip() == valid.lower().strip():
            return valid, False

    # AI hallucinated a category — flag for review
    logger.warning("invalid_category_from_ai", ai_category=category)
    return category, True


# ── Main Service ─────────────────────────────────────────────

class CategoryService:
    """
    Module 1 business logic.
    AI categorizes → business rules validate → sustainability scored → stored in DB.
    """

    def __init__(self, db: Session, correlation_id: str = ""):
        self.db = db
        self.ai_service = AIService(db=db, correlation_id=correlation_id)

    async def categorize_product(self, product_input: ProductInput) -> ProductCategorizationResponse:
        """
        Full pipeline: input → AI categorization → validation → scoring → DB storage.
        """
        # 1. Call AI with structured output schema
        result: AIResult[AICategoryOutput] = await self.ai_service.generate(
            module="category",
            prompt_version=PROMPT_VERSION,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(product_input.name, product_input.description, price=product_input.price),
            output_schema=AICategoryOutput,
        )

        ai_output = result.parsed

        # 2. Validate category against predefined list (business logic, not AI)
        validated_category, needs_review = validate_category(ai_output.primary_category)

        # 3. Flag for human review if confidence is low
        if ai_output.primary_category_confidence < 0.7:
            needs_review = True

        # 4. Compute sustainability score (rules-based algorithm, not AI)
        sustainability_score = compute_sustainability_score(
            detected_materials=ai_output.detected_materials,
            sustainability_filters=ai_output.sustainability_filters,
        )

        # 5. Save to database
        product = Product(
            name=product_input.name,
            description=product_input.description,
            price=product_input.price,
            image_url=product_input.image_url,
            primary_category=validated_category,
            sub_category=ai_output.sub_category,
            category_confidence=ai_output.primary_category_confidence,
            seo_tags=ai_output.seo_tags,
            sustainability_filters=ai_output.sustainability_filters,
            detected_materials=ai_output.detected_materials,
            sustainability_score=sustainability_score,
            ai_metadata={
                "prompt_version": PROMPT_VERSION,
                "model": result.model,
                "latency_ms": result.latency_ms,
                "thinking_tokens": result.thinking_tokens,
                "sub_category_reasoning": ai_output.sub_category_reasoning,
                "sustainability_reasoning": ai_output.sustainability_reasoning,
            },
            categorized_at=datetime.utcnow(),
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)

        # 6. Build response
        return ProductCategorizationResponse(
            product_id=product.id,
            name=product.name,
            description=product.description,
            primary_category=validated_category,
            primary_category_confidence=ai_output.primary_category_confidence,
            sub_category=ai_output.sub_category,
            sub_category_reasoning=ai_output.sub_category_reasoning,
            seo_tags=ai_output.seo_tags,
            sustainability_filters=ai_output.sustainability_filters,
            detected_materials=ai_output.detected_materials,
            sustainability_score=sustainability_score,
            sustainability_reasoning=ai_output.sustainability_reasoning,
            needs_human_review=needs_review,
            ai_model=result.model,
            prompt_version=PROMPT_VERSION,
            latency_ms=result.latency_ms,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )

    async def batch_categorize(
        self, products: list[ProductInput]
    ) -> list[ProductCategorizationResponse | dict]:
        """
        Batch categorize products with concurrency limit.
        Returns list of results (success) or error dicts (failure).
        """
        semaphore = asyncio.Semaphore(5)  # max 5 concurrent AI calls
        results = []

        async def _categorize_one(p: ProductInput):
            async with semaphore:
                try:
                    return await self.categorize_product(p)
                except Exception as e:
                    logger.error("batch_categorize_error", product=p.name, error=str(e))
                    return {"product_name": p.name, "error": str(e)}

        tasks = [_categorize_one(p) for p in products]
        results = await asyncio.gather(*tasks)
        return list(results)
