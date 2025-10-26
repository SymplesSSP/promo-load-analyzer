"""Unit tests for promo scraper module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.promo_scraper import _extract_striked_price_from_page, scrape_striked_price


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
