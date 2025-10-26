"""Promotion scraping module using Playwright.

This module scrapes promotion data from PrestaShop pages using headless browser automation.
"""

from loguru import logger
from playwright.async_api import Browser, Page, async_playwright

from src.constants import SELECTOR_PRODUCT_PRICE
from src.models import StrikedPriceData
from src.utils.price_parser import (
    calculate_discount_percentage,
    extract_currency,
    parse_price_string,
)


async def scrape_striked_price(url: str, timeout: int = 30000) -> StrikedPriceData | None:
    """Scrape striked price promotion from a product page.

    This function uses Playwright to load the page and extract price information
    when a product has a striked (crossed-out) regular price.

    Args:
        url: Product page URL
        timeout: Page load timeout in milliseconds (default: 30000)

    Returns:
        StrikedPriceData if striked price found, None otherwise

    Raises:
        Exception: If browser automation fails

    Example:
        >>> data = await scrape_striked_price("https://shop.com/product-123.html")
        >>> if data:
        ...     print(f"Discount: {data.discount_percentage}%")
    """
    logger.debug(f"Scraping striked price from: {url}")

    async with async_playwright() as p:
        browser: Browser | None = None
        try:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to page
            await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            logger.debug(f"Page loaded: {url}")

            # Look for striked price indicator
            striked_price_data = await _extract_striked_price_from_page(page)

            if striked_price_data:
                logger.info(
                    f"Found striked price on {url}: "
                    f"{striked_price_data.discount_percentage}% off"
                )
            else:
                logger.debug(f"No striked price found on: {url}")

            return striked_price_data

        except Exception as e:
            logger.error(f"Failed to scrape striked price from {url}: {e}")
            raise
        finally:
            if browser:
                await browser.close()


async def _extract_striked_price_from_page(page: Page) -> StrikedPriceData | None:
    """Extract striked price data from a loaded page.

    Args:
        page: Playwright Page object

    Returns:
        StrikedPriceData if found, None otherwise
    """
    # Common PrestaShop selectors for regular (striked) price
    regular_price_selectors = [
        ".regular-price",
        ".product-price-and-shipping .regular-price",
        "span.regular-price",
        ".price-old",
        ".old-price",
    ]

    # Selectors for current (discounted) price
    current_price_selectors = [
        ".current-price",
        ".product-price",
        SELECTOR_PRODUCT_PRICE,
        ".price",
        ".product-price-and-shipping .price",
    ]

    regular_price_text = None
    current_price_text = None

    # Try to find regular (striked) price
    for selector in regular_price_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                regular_price_text = await element.text_content()
                if regular_price_text and regular_price_text.strip():
                    logger.debug(f"Found regular price with selector '{selector}'")
                    break
        except Exception as e:
            logger.debug(f"Selector '{selector}' failed: {e}")
            continue

    # If no regular price found, no striked price promotion
    if not regular_price_text:
        return None

    # Try to find current price
    for selector in current_price_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                current_price_text = await element.text_content()
                if current_price_text and current_price_text.strip():
                    logger.debug(f"Found current price with selector '{selector}'")
                    break
        except Exception as e:
            logger.debug(f"Selector '{selector}' failed: {e}")
            continue

    if not current_price_text:
        logger.warning("Found regular price but no current price")
        return None

    # Parse prices
    regular_price = parse_price_string(regular_price_text)
    current_price = parse_price_string(current_price_text)

    if regular_price is None or current_price is None:
        logger.warning(
            f"Failed to parse prices: regular='{regular_price_text}', "
            f"current='{current_price_text}'"
        )
        return None

    # Validate prices
    if current_price >= regular_price:
        logger.warning(
            f"Current price ({current_price}) >= regular price ({regular_price}), "
            "not a valid discount"
        )
        return None

    # Calculate discount
    discount = calculate_discount_percentage(regular_price, current_price)

    # Extract currency
    currency = extract_currency(current_price_text or regular_price_text)

    # Create and return StrikedPriceData
    return StrikedPriceData(
        regular_price=regular_price,
        current_price=current_price,
        discount_percentage=discount,
        currency=currency,
    )
