"""Unit tests for promo scraper module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.promo_scraper import (
    _extract_auto_cart_rules_from_page,
    _extract_striked_price_from_page,
    scrape_auto_cart_rules,
    scrape_striked_price,
)


class TestScrapeStrikedPrice:
    """Tests for scrape_striked_price function."""

    @pytest.mark.asyncio
    async def test_scrape_striked_price_success(self) -> None:
        """Test successful striked price scraping."""
        # Mock Playwright components
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = MagicMock()
        mock_chromium = AsyncMock()

        # Setup mock hierarchy
        mock_chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_playwright.chromium = mock_chromium

        # Mock page elements
        mock_regular_element = AsyncMock()
        mock_regular_element.text_content.return_value = "€100.00"

        mock_current_element = AsyncMock()
        mock_current_element.text_content.return_value = "€85.00"

        # Configure query_selector to return elements based on selector
        async def mock_query_selector(selector: str):  # type: ignore
            if "regular-price" in selector:
                return mock_regular_element
            elif "current-price" in selector or "product-price" in selector:
                return mock_current_element
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        # Patch async_playwright
        with patch("src.promo_scraper.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__.return_value = mock_playwright

            result = await scrape_striked_price("https://shop.com/product")

        assert result is not None
        assert result.regular_price == 100.0
        assert result.current_price == 85.0
        assert result.discount_percentage == 15.0
        assert result.currency == "EUR"

    @pytest.mark.asyncio
    async def test_scrape_no_striked_price(self) -> None:
        """Test scraping when no striked price exists."""
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = MagicMock()
        mock_chromium = AsyncMock()

        mock_chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_playwright.chromium = mock_chromium

        # No regular price element found
        mock_page.query_selector.return_value = None

        with patch("src.promo_scraper.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__.return_value = mock_playwright

            result = await scrape_striked_price("https://shop.com/product")

        assert result is None

    @pytest.mark.asyncio
    async def test_scrape_handles_exception(self) -> None:
        """Test that exceptions are raised properly."""
        mock_playwright = MagicMock()
        mock_chromium = AsyncMock()
        mock_chromium.launch.side_effect = Exception("Browser launch failed")
        mock_playwright.chromium = mock_chromium

        with patch("src.promo_scraper.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__.return_value = mock_playwright

            with pytest.raises(Exception, match="Browser launch failed"):
                await scrape_striked_price("https://shop.com/product")


class TestExtractStrikedPriceFromPage:
    """Tests for _extract_striked_price_from_page function."""

    @pytest.mark.asyncio
    async def test_extract_with_regular_price_selector(self) -> None:
        """Test extraction with .regular-price selector."""
        mock_page = AsyncMock()

        mock_regular = AsyncMock()
        mock_regular.text_content.return_value = "€120.00"

        mock_current = AsyncMock()
        mock_current.text_content.return_value = "€100.00"

        async def mock_query_selector(selector: str):  # type: ignore
            if ".regular-price" in selector:
                return mock_regular
            elif "product-price" in selector or ".price" in selector:
                return mock_current
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        result = await _extract_striked_price_from_page(mock_page)

        assert result is not None
        assert result.regular_price == 120.0
        assert result.current_price == 100.0
        assert abs(result.discount_percentage - 16.67) < 0.1

    @pytest.mark.asyncio
    async def test_extract_no_regular_price(self) -> None:
        """Test extraction when no regular price found."""
        mock_page = AsyncMock()
        mock_page.query_selector.return_value = None

        result = await _extract_striked_price_from_page(mock_page)

        assert result is None

    @pytest.mark.asyncio
    async def test_extract_no_current_price(self) -> None:
        """Test extraction when regular price found but no current price."""
        mock_page = AsyncMock()

        mock_regular = AsyncMock()
        mock_regular.text_content.return_value = "€100.00"

        async def mock_query_selector(selector: str):  # type: ignore
            if "regular" in selector:
                return mock_regular
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        result = await _extract_striked_price_from_page(mock_page)

        assert result is None

    @pytest.mark.asyncio
    async def test_extract_invalid_price_format(self) -> None:
        """Test extraction with invalid price format."""
        mock_page = AsyncMock()

        mock_regular = AsyncMock()
        mock_regular.text_content.return_value = "invalid price"

        mock_current = AsyncMock()
        mock_current.text_content.return_value = "also invalid"

        async def mock_query_selector(selector: str):  # type: ignore
            if "regular" in selector:
                return mock_regular
            elif "price" in selector:
                return mock_current
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        result = await _extract_striked_price_from_page(mock_page)

        assert result is None

    @pytest.mark.asyncio
    async def test_extract_current_price_higher_than_regular(self) -> None:
        """Test extraction when current price is higher (invalid discount)."""
        mock_page = AsyncMock()

        mock_regular = AsyncMock()
        mock_regular.text_content.return_value = "€80.00"

        mock_current = AsyncMock()
        mock_current.text_content.return_value = "€100.00"

        async def mock_query_selector(selector: str):  # type: ignore
            if "regular" in selector:
                return mock_regular
            elif "price" in selector:
                return mock_current
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        result = await _extract_striked_price_from_page(mock_page)

        assert result is None

    @pytest.mark.asyncio
    async def test_extract_with_alternative_selectors(self) -> None:
        """Test extraction using alternative CSS selectors."""
        mock_page = AsyncMock()

        mock_regular = AsyncMock()
        mock_regular.text_content.return_value = "$199.99"

        mock_current = AsyncMock()
        mock_current.text_content.return_value = "$149.99"

        async def mock_query_selector(selector: str):  # type: ignore
            if ".old-price" in selector or ".price-old" in selector:
                return mock_regular
            elif ".price" in selector:
                return mock_current
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        result = await _extract_striked_price_from_page(mock_page)

        assert result is not None
        assert result.regular_price == 199.99
        assert result.current_price == 149.99
        assert result.currency == "USD"

    @pytest.mark.asyncio
    async def test_extract_with_french_format(self) -> None:
        """Test extraction with French price format."""
        mock_page = AsyncMock()

        mock_regular = AsyncMock()
        mock_regular.text_content.return_value = "1 234,56 €"

        mock_current = AsyncMock()
        mock_current.text_content.return_value = "987,65 €"

        async def mock_query_selector(selector: str):  # type: ignore
            if "regular" in selector:
                return mock_regular
            elif "price" in selector:
                return mock_current
            return None

        mock_page.query_selector.side_effect = mock_query_selector

        result = await _extract_striked_price_from_page(mock_page)

        assert result is not None
        assert result.regular_price == 1234.56
        assert result.current_price == 987.65
        assert result.currency == "EUR"


class TestScrapeAutoCartRules:
    """Tests for scrape_auto_cart_rules function."""

    @pytest.mark.asyncio
    async def test_scrape_auto_cart_rules_success(self) -> None:
        """Test successful auto cart rules scraping."""
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = MagicMock()
        mock_chromium = AsyncMock()

        mock_chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_playwright.chromium = mock_chromium

        # Mock add-to-cart button
        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button

        # Mock page.evaluate to return voucher data
        mock_page.evaluate.return_value = [
            {
                "id_cart_rule": 1,
                "code": "PROMO10",
                "value": "10.00",
            },
            {
                "id_cart_rule": 2,
                "code": "FREE_SHIPPING",
                "reduction_amount": "5.00",
            },
        ]

        with patch("src.promo_scraper.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__.return_value = mock_playwright

            result = await scrape_auto_cart_rules("https://shop.com/product")

        assert len(result) == 2
        assert result[0].rule_id == 1
        assert result[0].rule_name == "PROMO10"
        assert result[0].amount == 10.0
        assert result[1].rule_id == 2
        assert result[1].rule_name == "FREE_SHIPPING"

    @pytest.mark.asyncio
    async def test_scrape_no_cart_rules(self) -> None:
        """Test scraping when no cart rules exist."""
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = MagicMock()
        mock_chromium = AsyncMock()

        mock_chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_playwright.chromium = mock_chromium

        # Mock add-to-cart button
        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button

        # No vouchers
        mock_page.evaluate.return_value = None

        with patch("src.promo_scraper.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__.return_value = mock_playwright

            result = await scrape_auto_cart_rules("https://shop.com/product")

        assert result == []

    @pytest.mark.asyncio
    async def test_scrape_handles_exception(self) -> None:
        """Test that exceptions are raised properly."""
        mock_playwright = MagicMock()
        mock_chromium = AsyncMock()
        mock_chromium.launch.side_effect = Exception("Browser launch failed")
        mock_playwright.chromium = mock_chromium

        with patch("src.promo_scraper.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.__aenter__.return_value = mock_playwright

            with pytest.raises(Exception, match="Browser launch failed"):
                await scrape_auto_cart_rules("https://shop.com/product")


class TestExtractAutoCartRulesFromPage:
    """Tests for _extract_auto_cart_rules_from_page function."""

    @pytest.mark.asyncio
    async def test_extract_with_single_rule(self) -> None:
        """Test extraction with single cart rule."""
        mock_page = AsyncMock()

        # Mock add-to-cart button
        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button

        # Mock voucher data
        mock_page.evaluate.return_value = {
            "id_cart_rule": 5,
            "code": "SAVE20",
            "value": "20.00",
        }

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert len(result) == 1
        assert result[0].rule_id == 5
        assert result[0].rule_name == "SAVE20"
        assert result[0].amount == 20.0
        assert result[0].discount_type == "amount"

    @pytest.mark.asyncio
    async def test_extract_with_percentage_discount(self) -> None:
        """Test extraction with percentage discount."""
        mock_page = AsyncMock()

        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button

        mock_page.evaluate.return_value = [
            {
                "id_cart_rule": 10,
                "code": "PERCENT15",
                "reduction_percent": "15",
            }
        ]

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert len(result) == 1
        assert result[0].discount_type == "percentage"
        assert result[0].rule_name == "PERCENT15"

    @pytest.mark.asyncio
    async def test_extract_no_add_to_cart_button(self) -> None:
        """Test extraction when no add-to-cart button found."""
        mock_page = AsyncMock()
        mock_page.query_selector.return_value = None

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert result == []

    @pytest.mark.asyncio
    async def test_extract_no_vouchers(self) -> None:
        """Test extraction when no vouchers in cart."""
        mock_page = AsyncMock()

        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button
        mock_page.evaluate.return_value = None

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert result == []

    @pytest.mark.asyncio
    async def test_extract_with_invalid_voucher_data(self) -> None:
        """Test extraction with invalid voucher data."""
        mock_page = AsyncMock()

        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button

        # Invalid voucher data (missing id_cart_rule)
        mock_page.evaluate.return_value = [
            {
                "code": "INVALID",
                "value": "10.00",
                # Missing id_cart_rule
            }
        ]

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert result == []

    @pytest.mark.asyncio
    async def test_extract_multiple_rules(self) -> None:
        """Test extraction with multiple cart rules."""
        mock_page = AsyncMock()

        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button

        mock_page.evaluate.return_value = [
            {"id": 1, "name": "RULE1", "value": "5.00"},
            {"id": 2, "name": "RULE2", "reduction_amount": "10.00"},
            {"id": 3, "code": "RULE3", "reduction_percent": "15%"},
        ]

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert len(result) == 3
        assert result[0].rule_name == "RULE1"
        assert result[1].rule_name == "RULE2"
        assert result[2].rule_name == "RULE3"
        assert result[2].discount_type == "percentage"

    @pytest.mark.asyncio
    async def test_extract_with_evaluate_exception(self) -> None:
        """Test extraction when page.evaluate throws exception."""
        mock_page = AsyncMock()

        mock_button = AsyncMock()
        mock_page.query_selector.return_value = mock_button
        mock_page.evaluate.side_effect = Exception("JavaScript error")

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert result == []

    @pytest.mark.asyncio
    async def test_extract_with_alternative_selector(self) -> None:
        """Test extraction using alternative add-to-cart selector."""
        mock_page = AsyncMock()

        # First selector fails, second succeeds
        mock_button = AsyncMock()

        call_count = 0

        async def mock_query_selector(selector: str):  # type: ignore
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return None  # First selector fails
            return mock_button  # Second selector succeeds

        mock_page.query_selector.side_effect = mock_query_selector

        mock_page.evaluate.return_value = {
            "id_cart_rule": 7,
            "code": "TEST",
            "value": "5.00",
        }

        result = await _extract_auto_cart_rules_from_page(mock_page)

        assert len(result) == 1
        assert result[0].rule_id == 7
