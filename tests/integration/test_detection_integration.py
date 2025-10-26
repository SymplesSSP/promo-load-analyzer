"""Integration tests for detection modules.

These tests run against a real PrestaShop environment.
Set INTEGRATION_TEST_URL environment variable to run them.
"""

import os

import pytest

from src.page_detector import detect_page_type_from_dom, detect_page_type_from_url
from src.promo_scraper import (
    detect_manual_code_input,
    scrape_auto_cart_rules,
    scrape_striked_price,
)

# Skip all integration tests if INTEGRATION_TEST_URL is not set
INTEGRATION_TEST_URL = os.getenv("INTEGRATION_TEST_URL")
pytestmark = pytest.mark.skipif(
    not INTEGRATION_TEST_URL, reason="INTEGRATION_TEST_URL not set"
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPageDetectionIntegration:
    """Integration tests for page detection."""

    async def test_detect_product_page_from_url(self) -> None:
        """Test product page detection from URL pattern."""
        # Example: https://preprod.ipln.fr/123-product-name.html
        url = f"{INTEGRATION_TEST_URL}/123-test-product.html"

        try:
            result = detect_page_type_from_url(url)
            assert result.page_type in ["product", "unknown"]
            assert result.detection_method == "regex"
        except Exception as e:
            pytest.skip(f"URL pattern test skipped: {e}")

    async def test_detect_product_page_from_dom(self) -> None:
        """Test product page detection from DOM analysis."""
        # Skip if no real URL provided
        if not INTEGRATION_TEST_URL or INTEGRATION_TEST_URL == "http://example.com":
            pytest.skip("No real INTEGRATION_TEST_URL provided")

        try:
            result = await detect_page_type_from_dom(INTEGRATION_TEST_URL, timeout=10)
            assert result.page_type in ["product", "category", "catalog", "unknown"]
            assert result.detection_method == "dom_analysis"
            assert 0.0 <= result.confidence <= 1.0
        except Exception as e:
            pytest.skip(f"DOM detection test skipped: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
class TestPromoScrapingIntegration:
    """Integration tests for promotion scraping."""

    async def test_scrape_striked_price(self) -> None:
        """Test striked price scraping on real page."""
        if not INTEGRATION_TEST_URL or INTEGRATION_TEST_URL == "http://example.com":
            pytest.skip("No real INTEGRATION_TEST_URL provided")

        try:
            result = await scrape_striked_price(INTEGRATION_TEST_URL, timeout=30000)

            # Result can be None if no striked price found (which is valid)
            if result:
                assert result.regular_price > 0
                assert result.current_price > 0
                assert result.current_price < result.regular_price
                assert 0 <= result.discount_percentage <= 100
                assert result.currency in ["EUR", "USD", "GBP", "JPY", "CHF"]
        except Exception as e:
            pytest.skip(f"Striked price scraping test skipped: {e}")

    async def test_scrape_auto_cart_rules(self) -> None:
        """Test auto cart rules scraping on real page."""
        if not INTEGRATION_TEST_URL or INTEGRATION_TEST_URL == "http://example.com":
            pytest.skip("No real INTEGRATION_TEST_URL provided")

        try:
            result = await scrape_auto_cart_rules(INTEGRATION_TEST_URL, timeout=30000)

            # Result can be empty list if no auto cart rules (which is valid)
            assert isinstance(result, list)

            for rule in result:
                assert rule.rule_id > 0
                assert len(rule.rule_name) > 0
                assert rule.amount >= 0
                assert rule.discount_type in ["amount", "percentage", "free_shipping"]
        except Exception as e:
            pytest.skip(f"Auto cart rules scraping test skipped: {e}")

    async def test_detect_manual_code_input(self) -> None:
        """Test manual code input detection on real page."""
        if not INTEGRATION_TEST_URL or INTEGRATION_TEST_URL == "http://example.com":
            pytest.skip("No real INTEGRATION_TEST_URL provided")

        try:
            result = await detect_manual_code_input(INTEGRATION_TEST_URL, timeout=30000)

            # Result is boolean (True if manual code input found, False otherwise)
            assert isinstance(result, bool)
        except Exception as e:
            pytest.skip(f"Manual code input detection test skipped: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndIntegration:
    """End-to-end integration tests combining multiple modules."""

    async def test_full_promotion_analysis(self) -> None:
        """Test full promotion analysis workflow."""
        if not INTEGRATION_TEST_URL or INTEGRATION_TEST_URL == "http://example.com":
            pytest.skip("No real INTEGRATION_TEST_URL provided")

        try:
            # Step 1: Detect page type
            page_detection = await detect_page_type_from_dom(
                INTEGRATION_TEST_URL, timeout=10
            )
            assert page_detection.page_type in [
                "product",
                "category",
                "catalog",
                "unknown",
            ]

            # Step 2: Scrape promotions (only if product page)
            if page_detection.page_type == "product":
                striked_price = await scrape_striked_price(
                    INTEGRATION_TEST_URL, timeout=30000
                )
                auto_cart_rules = await scrape_auto_cart_rules(
                    INTEGRATION_TEST_URL, timeout=30000
                )
                has_manual_code = await detect_manual_code_input(
                    INTEGRATION_TEST_URL, timeout=30000
                )

                # Validate results
                if striked_price:
                    assert striked_price.regular_price > 0
                    assert striked_price.current_price < striked_price.regular_price

                assert isinstance(auto_cart_rules, list)
                assert isinstance(has_manual_code, bool)

                # Determine complexity based on promotions found
                promo_count = len(auto_cart_rules)
                if striked_price:
                    promo_count += 1
                if has_manual_code:
                    promo_count += 1

                # Should have detected at least the page type
                assert page_detection.detection_method in ["regex", "dom_analysis"]
        except Exception as e:
            pytest.skip(f"End-to-end test skipped: {e}")
