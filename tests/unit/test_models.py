"""Unit tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from src.models import (
    AutoCartRule,
    PageDetectionResult,
    PromotionData,
    StrikedPriceData,
)


class TestPageDetectionResult:
    """Tests for PageDetectionResult model."""

    def test_valid_product_page_detection(self) -> None:
        """Test valid product page detection result."""
        result = PageDetectionResult(
            page_type="product",
            detection_method="regex",
            url="https://example.com/product-123.html",
            product_id=123,
            confidence=1.0,
        )

        assert result.page_type == "product"
        assert result.detection_method == "regex"
        assert result.product_id == 123
        assert result.category_id is None
        assert result.confidence == 1.0

    def test_valid_category_page_detection(self) -> None:
        """Test valid category page detection result."""
        result = PageDetectionResult(
            page_type="category",
            detection_method="regex",
            url="https://example.com/category/42",
            category_id=42,
            confidence=1.0,
        )

        assert result.page_type == "category"
        assert result.category_id == 42
        assert result.product_id is None

    def test_dom_analysis_detection(self) -> None:
        """Test DOM analysis detection with features."""
        result = PageDetectionResult(
            page_type="product",
            detection_method="dom_analysis",
            url="https://example.com/page",
            confidence=0.8,
            has_add_to_cart=True,
            has_promo_code_input=True,
        )

        assert result.detection_method == "dom_analysis"
        assert result.has_add_to_cart is True
        assert result.has_promo_code_input is True
        assert result.confidence == 0.8

    def test_invalid_page_type(self) -> None:
        """Test that invalid page type raises validation error."""
        with pytest.raises(ValidationError):
            PageDetectionResult(
                page_type="invalid_type",  # type: ignore
                detection_method="regex",
                url="https://example.com",
            )

    def test_invalid_confidence(self) -> None:
        """Test that confidence outside 0-1 range raises error."""
        with pytest.raises(ValidationError):
            PageDetectionResult(
                page_type="product",
                detection_method="regex",
                url="https://example.com",
                confidence=1.5,  # Invalid: > 1.0
            )

    def test_json_serialization(self) -> None:
        """Test model can serialize to and from JSON."""
        result = PageDetectionResult(
            page_type="product",
            detection_method="regex",
            url="https://example.com/product-123.html",
            product_id=123,
        )

        json_data = result.model_dump_json()
        assert isinstance(json_data, str)

        # Deserialize
        result_copy = PageDetectionResult.model_validate_json(json_data)
        assert result_copy.page_type == result.page_type
        assert result_copy.product_id == result.product_id


class TestStrikedPriceData:
    """Tests for StrikedPriceData model."""

    def test_valid_striked_price(self) -> None:
        """Test valid striked price data."""
        striked = StrikedPriceData(
            regular_price=100.0,
            current_price=85.0,
            discount_percentage=15.0,
            currency="EUR",
        )

        assert striked.regular_price == 100.0
        assert striked.current_price == 85.0
        assert striked.discount_percentage == 15.0
        assert striked.currency == "EUR"

    def test_currency_uppercase_normalization(self) -> None:
        """Test that currency is normalized to uppercase."""
        striked = StrikedPriceData(
            regular_price=100.0,
            current_price=85.0,
            discount_percentage=15.0,
            currency="usd",
        )

        assert striked.currency == "USD"

    def test_current_price_must_be_less_than_regular(self) -> None:
        """Test that current price must be less than regular price."""
        with pytest.raises(ValidationError):
            StrikedPriceData(
                regular_price=100.0,
                current_price=100.0,  # Same as regular
                discount_percentage=0.0,
            )

    def test_negative_prices_rejected(self) -> None:
        """Test that negative prices are rejected."""
        with pytest.raises(ValidationError):
            StrikedPriceData(
                regular_price=-100.0,
                current_price=85.0,
                discount_percentage=15.0,
            )


class TestAutoCartRule:
    """Tests for AutoCartRule model."""

    def test_valid_cart_rule(self) -> None:
        """Test valid cart rule data."""
        rule = AutoCartRule(
            rule_id=42,
            rule_name="BLACK_FRIDAY_2025",
            amount=15.0,
            discount_type="percentage",
            is_active=True,
            priority=1,
        )

        assert rule.rule_id == 42
        assert rule.rule_name == "BLACK_FRIDAY_2025"
        assert rule.amount == 15.0
        assert rule.discount_type == "percentage"
        assert rule.is_active is True
        assert rule.priority == 1

    def test_free_shipping_discount_type(self) -> None:
        """Test free shipping discount type."""
        rule = AutoCartRule(
            rule_id=1,
            rule_name="FREE_SHIP_79",
            amount=0.0,
            discount_type="free_shipping",
        )

        assert rule.discount_type == "free_shipping"

    def test_invalid_discount_type(self) -> None:
        """Test that invalid discount type raises error."""
        with pytest.raises(ValidationError):
            AutoCartRule(
                rule_id=1,
                rule_name="TEST",
                amount=10.0,
                discount_type="invalid",  # type: ignore
            )


class TestPromotionData:
    """Tests for PromotionData model."""

    def test_valid_promotion_with_striked_price_only(self) -> None:
        """Test promotion with striked price only."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/product-123.html",
            striked_price=StrikedPriceData(
                regular_price=100.0,
                current_price=85.0,
                discount_percentage=15.0,
            ),
            complexity="LOW",
            estimated_server_impact=0.05,
        )

        assert promo.page_type == "product"
        assert promo.striked_price is not None
        assert promo.striked_price.discount_percentage == 15.0
        assert len(promo.auto_cart_rules) == 0
        assert promo.has_manual_code_input is False
        assert promo.complexity == "LOW"

    def test_valid_promotion_with_cart_rules(self) -> None:
        """Test promotion with auto cart rules."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/product-123.html",
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=42,
                    rule_name="BLACK_FRIDAY",
                    amount=15.0,
                    discount_type="percentage",
                )
            ],
            complexity="MEDIUM",
            estimated_server_impact=0.15,
        )

        assert len(promo.auto_cart_rules) == 1
        assert promo.auto_cart_rules[0].rule_name == "BLACK_FRIDAY"
        assert promo.complexity == "MEDIUM"

    def test_calculate_complexity_low(self) -> None:
        """Test complexity calculation for LOW."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            striked_price=StrikedPriceData(
                regular_price=100.0, current_price=85.0, discount_percentage=15.0
            ),
            complexity="LOW",
            estimated_server_impact=0.05,
        )

        assert promo.calculate_complexity() == "LOW"

    def test_calculate_complexity_medium(self) -> None:
        """Test complexity calculation for MEDIUM."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=1, rule_name="TEST", amount=10.0, discount_type="amount"
                )
            ],
            complexity="MEDIUM",
            estimated_server_impact=0.15,
        )

        assert promo.calculate_complexity() == "MEDIUM"

    def test_calculate_complexity_high(self) -> None:
        """Test complexity calculation for HIGH."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=1, rule_name="RULE1", amount=10.0, discount_type="amount"
                ),
                AutoCartRule(
                    rule_id=2,
                    rule_name="RULE2",
                    amount=5.0,
                    discount_type="percentage",
                ),
            ],
            complexity="HIGH",
            estimated_server_impact=0.30,
        )

        assert promo.calculate_complexity() == "HIGH"

    def test_estimate_server_impact_striked_only(self) -> None:
        """Test server impact estimation for striked price only."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            striked_price=StrikedPriceData(
                regular_price=100.0, current_price=85.0, discount_percentage=15.0
            ),
            complexity="LOW",
            estimated_server_impact=0.0,
        )

        assert promo.estimate_server_impact() == 0.05

    def test_estimate_server_impact_with_rules(self) -> None:
        """Test server impact estimation with cart rules."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=1, rule_name="RULE1", amount=10.0, discount_type="amount"
                ),
            ],
            complexity="MEDIUM",
            estimated_server_impact=0.0,
        )

        assert promo.estimate_server_impact() == 0.15

    def test_estimate_server_impact_manual_code(self) -> None:
        """Test server impact estimation with manual code input."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            has_manual_code_input=True,
            complexity="MEDIUM",
            estimated_server_impact=0.0,
        )

        assert promo.estimate_server_impact() == 0.25

    def test_estimate_server_impact_capped_at_one(self) -> None:
        """Test that server impact is capped at 1.0."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            striked_price=StrikedPriceData(
                regular_price=100.0, current_price=85.0, discount_percentage=15.0
            ),
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=i + 1,
                    rule_name=f"RULE{i}",
                    amount=10.0,
                    discount_type="amount",
                )
                for i in range(10)  # 10 rules * 0.15 = 1.5
            ],
            has_manual_code_input=True,
            complexity="HIGH",
            estimated_server_impact=0.0,
        )

        # 0.05 (striked) + 1.5 (10 rules) + 0.25 (manual) = 1.8, capped at 1.0
        assert promo.estimate_server_impact() == 1.0

    def test_calculate_complexity_manual_code_only(self) -> None:
        """Test complexity with manual code input only (MEDIUM)."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/cart",
            has_manual_code_input=True,
            complexity="MEDIUM",
            estimated_server_impact=0.25,
        )

        assert promo.calculate_complexity() == "MEDIUM"
        assert promo.auto_cart_rules == []
        assert promo.striked_price is None

    def test_calculate_complexity_manual_plus_one_rule(self) -> None:
        """Test complexity with manual code + 1 cart rule (HIGH)."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=1, rule_name="RULE1", amount=10.0, discount_type="amount"
                )
            ],
            has_manual_code_input=True,
            complexity="HIGH",
            estimated_server_impact=0.40,
        )

        assert promo.calculate_complexity() == "HIGH"

    def test_calculate_complexity_no_promotions(self) -> None:
        """Test complexity with no promotions at all (LOW)."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            complexity="LOW",
            estimated_server_impact=0.0,
        )

        assert promo.calculate_complexity() == "LOW"
        assert promo.estimate_server_impact() == 0.0

    def test_estimate_server_impact_combined(self) -> None:
        """Test server impact with all promotion types combined."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            striked_price=StrikedPriceData(
                regular_price=100.0, current_price=85.0, discount_percentage=15.0
            ),
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=1, rule_name="RULE1", amount=10.0, discount_type="amount"
                ),
                AutoCartRule(
                    rule_id=2,
                    rule_name="RULE2",
                    amount=5.0,
                    discount_type="percentage",
                ),
            ],
            has_manual_code_input=True,
            complexity="HIGH",
            estimated_server_impact=0.0,
        )

        # 0.05 (striked) + 0.30 (2 rules) + 0.25 (manual) = 0.60
        assert promo.estimate_server_impact() == 0.60

    def test_estimate_server_impact_three_rules(self) -> None:
        """Test server impact with 3 cart rules."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            auto_cart_rules=[
                AutoCartRule(
                    rule_id=i + 1,
                    rule_name=f"RULE{i}",
                    amount=10.0,
                    discount_type="amount",
                )
                for i in range(3)
            ],
            complexity="HIGH",
            estimated_server_impact=0.0,
        )

        # 3 rules * 0.15 = 0.45 (use approximate comparison for float precision)
        assert abs(promo.estimate_server_impact() - 0.45) < 0.01

    def test_calculate_complexity_striked_plus_manual(self) -> None:
        """Test complexity with striked price + manual code (MEDIUM)."""
        promo = PromotionData(
            page_type="product",
            url="https://example.com/test",
            striked_price=StrikedPriceData(
                regular_price=100.0, current_price=85.0, discount_percentage=15.0
            ),
            has_manual_code_input=True,
            complexity="MEDIUM",
            estimated_server_impact=0.30,
        )

        # Striked only is LOW, but adding manual makes it MEDIUM
        assert promo.calculate_complexity() == "MEDIUM"
        # 0.05 (striked) + 0.25 (manual) = 0.30
        assert promo.estimate_server_impact() == 0.30
