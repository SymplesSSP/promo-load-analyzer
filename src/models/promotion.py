"""Data models for promotion detection and analysis.

This module defines Pydantic models for promotion data scraped from PrestaShop pages.
"""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class StrikedPriceData(BaseModel):
    """Striked price promotion data.

    Represents a simple price discount shown with strikethrough on the regular price.

    Attributes:
        regular_price: Original price before discount
        current_price: Current discounted price
        discount_percentage: Calculated discount percentage
        currency: Currency code (EUR, USD, etc.)
    """

    regular_price: float = Field(description="Regular price", gt=0.0)

    current_price: float = Field(description="Current discounted price", gt=0.0)

    discount_percentage: float = Field(
        description="Discount percentage", ge=0.0, le=100.0
    )

    currency: str = Field(default="EUR", description="Currency code", min_length=3)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency is uppercase."""
        return v.upper()

    @model_validator(mode="after")
    def validate_current_less_than_regular(self) -> "StrikedPriceData":
        """Validate current price is less than regular price."""
        if self.current_price >= self.regular_price:
            raise ValueError("current_price must be less than regular_price")
        return self

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "regular_price": 100.0,
                "current_price": 85.0,
                "discount_percentage": 15.0,
                "currency": "EUR",
            }
        }


class AutoCartRule(BaseModel):
    """Auto-applied cart rule (promotional code).

    Represents a promotional code automatically applied when product is added to cart.

    Attributes:
        rule_id: PrestaShop cart rule ID
        rule_name: Cart rule name (e.g., "BLACK_FRIDAY_2025")
        amount: Discount amount (absolute or percentage)
        discount_type: Type of discount (percentage, amount, free_shipping)
        is_active: Whether rule is currently active
        priority: Rule priority (higher = applied first)
    """

    rule_id: int = Field(description="PrestaShop cart rule ID", ge=1)

    rule_name: str = Field(description="Cart rule name", min_length=1)

    amount: float = Field(description="Discount amount", ge=0.0)

    discount_type: Literal["percentage", "amount", "free_shipping"] = Field(
        description="Type of discount"
    )

    is_active: bool = Field(default=True, description="Whether rule is active")

    priority: int = Field(default=1, description="Rule priority", ge=1)

    @field_validator("discount_type")
    @classmethod
    def validate_discount_type(cls, v: str) -> str:
        """Validate discount type is lowercase."""
        return v.lower()

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "rule_id": 42,
                "rule_name": "BLACK_FRIDAY_2025",
                "amount": 15.0,
                "discount_type": "percentage",
                "is_active": True,
                "priority": 1,
            }
        }


class PromotionData(BaseModel):
    """Complete promotion data scraped from a page.

    Aggregates all promotion information detected on a PrestaShop page.

    Attributes:
        page_type: Type of page analyzed
        url: Page URL
        striked_price: Striked price data (if detected)
        auto_cart_rules: List of auto-applied cart rules
        has_manual_code_input: Whether page has manual promo code input
        complexity: Promotion complexity (LOW, MEDIUM, HIGH)
        estimated_server_impact: Estimated server load impact (0.0 to 1.0)
    """

    page_type: Literal["category", "product", "catalog", "unknown"] = Field(
        description="Page type analyzed"
    )

    url: HttpUrl = Field(description="Page URL")

    striked_price: StrikedPriceData | None = Field(
        default=None, description="Striked price data"
    )

    auto_cart_rules: list[AutoCartRule] = Field(
        default_factory=list, description="Auto-applied cart rules"
    )

    has_manual_code_input: bool = Field(
        default=False, description="Has manual promo code input"
    )

    complexity: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Promotion complexity"
    )

    estimated_server_impact: float = Field(
        description="Estimated server impact (0.0 to 1.0)", ge=0.0, le=1.0
    )

    @field_validator("page_type")
    @classmethod
    def validate_page_type(cls, v: str) -> str:
        """Validate page type is lowercase."""
        return v.lower()

    @field_validator("complexity")
    @classmethod
    def validate_complexity(cls, v: str) -> str:
        """Validate complexity is uppercase."""
        return v.upper()

    def calculate_complexity(self) -> Literal["LOW", "MEDIUM", "HIGH"]:
        """Calculate promotion complexity based on detected elements.

        Returns:
            Complexity level (LOW, MEDIUM, HIGH)

        Rules:
            - LOW: Only striked price
            - MEDIUM: 1 auto cart rule OR manual code input
            - HIGH: 2+ auto cart rules OR manual + auto
        """
        has_striked = self.striked_price is not None
        num_auto_rules = len(self.auto_cart_rules)
        has_manual = self.has_manual_code_input

        if num_auto_rules >= 2 or (has_manual and num_auto_rules >= 1):
            return "HIGH"
        elif num_auto_rules == 1 or has_manual:
            return "MEDIUM"
        elif has_striked:
            return "LOW"
        else:
            return "LOW"

    def estimate_server_impact(self) -> float:
        """Estimate server impact based on promotion complexity.

        Returns:
            Server impact score (0.0 to 1.0)

        Impact factors:
            - Striked price: +0.05
            - Each auto cart rule: +0.15
            - Manual code input: +0.25
        """
        impact = 0.0

        if self.striked_price is not None:
            impact += 0.05

        impact += len(self.auto_cart_rules) * 0.15

        if self.has_manual_code_input:
            impact += 0.25

        return min(impact, 1.0)  # Cap at 1.0

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "page_type": "product",
                "url": "https://example.com/product-123.html",
                "striked_price": {
                    "regular_price": 100.0,
                    "current_price": 85.0,
                    "discount_percentage": 15.0,
                    "currency": "EUR",
                },
                "auto_cart_rules": [
                    {
                        "rule_id": 42,
                        "rule_name": "BLACK_FRIDAY_2025",
                        "amount": 15.0,
                        "discount_type": "percentage",
                        "is_active": True,
                        "priority": 1,
                    }
                ],
                "has_manual_code_input": False,
                "complexity": "MEDIUM",
                "estimated_server_impact": 0.20,
            }
        }
