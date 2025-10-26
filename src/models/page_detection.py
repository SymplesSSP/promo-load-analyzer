"""Data models for page detection results.

This module defines Pydantic models for page type detection and metadata extraction.
"""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class PageDetectionResult(BaseModel):
    """Result of page type detection from URL or DOM analysis.

    Attributes:
        page_type: Type of page detected (category, product, catalog, unknown)
        detection_method: Method used for detection (regex, dom_analysis)
        url: Original URL analyzed
        product_id: Extracted product ID (if product page)
        category_id: Extracted category ID (if category page)
        confidence: Detection confidence score (0.0 to 1.0)
        has_add_to_cart: Whether page has add-to-cart button (DOM analysis only)
        has_promo_code_input: Whether page has promo code input (DOM analysis only)
    """

    page_type: Literal["category", "product", "catalog", "unknown"] = Field(
        description="Detected page type"
    )

    detection_method: Literal["regex", "dom_analysis"] = Field(
        description="Detection method used"
    )

    url: HttpUrl = Field(description="Original URL analyzed")

    product_id: int | None = Field(
        default=None, description="Product ID extracted from URL", ge=1
    )

    category_id: int | None = Field(
        default=None, description="Category ID extracted from URL", ge=1
    )

    confidence: float = Field(
        default=1.0,
        description="Detection confidence (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )

    has_add_to_cart: bool = Field(
        default=False, description="Has add-to-cart button (DOM analysis)"
    )

    has_promo_code_input: bool = Field(
        default=False, description="Has promo code input (DOM analysis)"
    )

    @field_validator("page_type")
    @classmethod
    def validate_page_type(cls, v: str) -> str:
        """Validate page type is lowercase."""
        return v.lower()

    @field_validator("detection_method")
    @classmethod
    def validate_detection_method(cls, v: str) -> str:
        """Validate detection method is lowercase."""
        return v.lower()

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "page_type": "product",
                "detection_method": "regex",
                "url": "https://example.com/product-123.html",
                "product_id": 123,
                "category_id": None,
                "confidence": 1.0,
                "has_add_to_cart": False,
                "has_promo_code_input": False,
            }
        }
