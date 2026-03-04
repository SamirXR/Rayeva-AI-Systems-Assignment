"""
Rayeva AI — Tests for Module 1 (Category Service)
Tests business logic: sustainability scoring, category validation.
"""

import pytest
from app.services.category_service import (
    compute_sustainability_score,
    validate_category,
    VALID_CATEGORIES,
)


class TestSustainabilityScoring:
    """Test the rules-based sustainability scoring algorithm."""

    def test_high_sustainability_product(self):
        """Bamboo + organic cotton with many filters → high score."""
        score = compute_sustainability_score(
            detected_materials=["bamboo", "organic cotton"],
            sustainability_filters=["plastic-free", "biodegradable", "organic", "vegan", "zero-waste"],
        )
        assert score > 5.0
        assert score <= 10.0

    def test_medium_sustainability_product(self):
        """Stainless steel with some filters → moderate score."""
        score = compute_sustainability_score(
            detected_materials=["stainless steel"],
            sustainability_filters=["plastic-free"],
        )
        assert 1.0 <= score <= 5.0

    def test_empty_inputs(self):
        """No materials or filters → zero score."""
        score = compute_sustainability_score(
            detected_materials=[],
            sustainability_filters=[],
        )
        assert score == 0.0

    def test_score_capped_at_ten(self):
        """Score never exceeds 10.0."""
        score = compute_sustainability_score(
            detected_materials=["bamboo", "organic cotton", "hemp", "jute", "cork", "coconut shell"],
            sustainability_filters=["plastic-free", "compostable", "vegan", "recycled", "organic",
                                    "biodegradable", "zero-waste", "fair-trade", "handmade", "upcycled"],
        )
        assert score <= 10.0

    def test_material_case_insensitive(self):
        """Material matching should work regardless of case."""
        score1 = compute_sustainability_score(["Bamboo"], [])
        score2 = compute_sustainability_score(["bamboo"], [])
        assert score1 == score2


class TestCategoryValidation:
    """Test category validation against predefined list."""

    def test_valid_category(self):
        category, needs_review = validate_category("Home & Living")
        assert category == "Home & Living"
        assert needs_review is False

    def test_valid_category_all(self):
        """All predefined categories should validate."""
        for cat in VALID_CATEGORIES:
            category, needs_review = validate_category(cat)
            assert needs_review is False

    def test_case_insensitive_match(self):
        category, needs_review = validate_category("home & living")
        assert category == "Home & Living"
        assert needs_review is False

    def test_invalid_category_flagged(self):
        category, needs_review = validate_category("Imaginary Category")
        assert needs_review is True


class TestCostBreakdown:
    """Test server-side cost calculations for proposals."""

    def test_discount_thresholds(self):
        from app.services.proposal_service import compute_discount_percent

        assert compute_discount_percent(50) == 0.0
        assert compute_discount_percent(100) == 5.0
        assert compute_discount_percent(250) == 8.0
        assert compute_discount_percent(500) == 12.0

    def test_cost_breakdown_math(self):
        from app.services.proposal_service import validate_and_build_cost_breakdown

        product_mix = [
            {"product_name": "Test A", "unit_price_estimate": 100.0, "recommended_quantity": 10},
            {"product_name": "Test B", "unit_price_estimate": 200.0, "recommended_quantity": 5},
        ]
        breakdown = validate_and_build_cost_breakdown(product_mix, total_quantity=15)

        assert breakdown.subtotal == 2000.0  # (100*10) + (200*5)
        assert breakdown.discount_percent == 0.0  # 15 units → no discount
        assert breakdown.gst_percent == 18.0
        assert breakdown.gst_amount == 360.0  # 2000 * 0.18
        assert breakdown.shipping_estimate == 375.0  # 15 * 25
        assert breakdown.grand_total == 2735.0  # 2000 + 360 + 375

    def test_volume_discount_applied(self):
        from app.services.proposal_service import validate_and_build_cost_breakdown

        product_mix = [
            {"product_name": "Bulk A", "unit_price_estimate": 100.0, "recommended_quantity": 300},
        ]
        breakdown = validate_and_build_cost_breakdown(product_mix, total_quantity=300)

        assert breakdown.subtotal == 30000.0
        assert breakdown.discount_percent == 8.0  # 300 units → 8%
        assert breakdown.discount_amount == 2400.0
        # After discount: 27600, GST: 4968, Shipping: 7500
        assert breakdown.grand_total == 40068.0
