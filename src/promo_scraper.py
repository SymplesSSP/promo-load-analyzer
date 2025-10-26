"""Promotion scraping module using Playwright.

This module scrapes promotion data from PrestaShop pages using headless browser automation.
"""

from loguru import logger
from playwright.async_api import (
    Browser,
    Page,
    async_playwright,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from src.constants import SELECTOR_PRODUCT_PRICE
from src.models import AutoCartRule, StrikedPriceData
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


async def scrape_auto_cart_rules(url: str, timeout: int = 30000) -> list[AutoCartRule]:
    """Scrape auto-applied cart rules by simulating add-to-cart action.

    This function uses Playwright to load the page, click the add-to-cart button,
    and extract auto-applied vouchers from the PrestaShop cart object.

    Args:
        url: Product page URL
        timeout: Page load and action timeout in milliseconds (default: 30000)

    Returns:
        List of AutoCartRule objects (empty list if no rules found)

    Raises:
        Exception: If browser automation fails

    Example:
        >>> rules = await scrape_auto_cart_rules("https://shop.com/product-123.html")
        >>> for rule in rules:
        ...     print(f"Rule: {rule.rule_name}, {rule.amount} {rule.discount_type}")
    """
    logger.debug(f"Scraping auto cart rules from: {url}")

    async with async_playwright() as p:
        browser: Browser | None = None
        try:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to page
            await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            logger.debug(f"Page loaded: {url}")

            # Extract auto cart rules
            cart_rules = await _extract_auto_cart_rules_from_page(page, timeout)

            if cart_rules:
                logger.info(
                    f"Found {len(cart_rules)} auto cart rule(s) on {url}"
                )
            else:
                logger.debug(f"No auto cart rules found on: {url}")

            return cart_rules

        except Exception as e:
            logger.error(f"Failed to scrape auto cart rules from {url}: {e}")
            raise
        finally:
            if browser:
                await browser.close()


async def _extract_auto_cart_rules_from_page(
    page: Page, timeout: int = 30000
) -> list[AutoCartRule]:
    """Extract auto cart rules from a loaded page by simulating add-to-cart.

    Args:
        page: Playwright Page object
        timeout: Action timeout in milliseconds

    Returns:
        List of AutoCartRule objects (empty list if no rules found)
    """
    # Common PrestaShop selectors for add-to-cart button
    add_to_cart_selectors = [
        "button[data-button-action='add-to-cart']",
        ".add-to-cart",
        "button.add-to-cart",
        ".product-add-to-cart button",
        "button[name='add']",
    ]

    # Try to find and click add-to-cart button
    clicked = False
    for selector in add_to_cart_selectors:
        try:
            button = await page.query_selector(selector)
            if button:
                logger.debug(f"Found add-to-cart button with selector: {selector}")
                await button.click()
                clicked = True
                break
        except Exception as e:
            logger.debug(f"Failed to click selector '{selector}': {e}")
            continue

    if not clicked:
        logger.warning("No add-to-cart button found")
        return []

    # Wait for cart update (PrestaShop typically updates cart via AJAX)
    try:
        # Wait for cart modal or cart update indicator
        await page.wait_for_timeout(2000)  # Give AJAX time to complete
    except PlaywrightTimeoutError:
        logger.warning("Timeout waiting for cart update")
        return []

    # Extract vouchers from window.prestashop.cart.vouchers.added
    try:
        vouchers_data = await page.evaluate(
            """
            () => {
                if (window.prestashop &&
                    window.prestashop.cart &&
                    window.prestashop.cart.vouchers &&
                    window.prestashop.cart.vouchers.added) {
                    return window.prestashop.cart.vouchers.added;
                }
                return null;
            }
            """
        )
    except Exception as e:
        logger.warning(f"Failed to extract vouchers from page context: {e}")
        return []

    if not vouchers_data:
        logger.debug("No vouchers found in window.prestashop.cart.vouchers.added")
        return []

    # Parse vouchers data to AutoCartRule objects
    cart_rules: list[AutoCartRule] = []

    # vouchers_data could be a list or dict depending on PrestaShop version
    vouchers_list = vouchers_data if isinstance(vouchers_data, list) else [vouchers_data]

    for voucher in vouchers_list:
        try:
            # Extract fields from voucher object
            rule_id = voucher.get("id_cart_rule") or voucher.get("id")
            rule_name = voucher.get("code") or voucher.get("name", "UNKNOWN")

            # Amount could be in different fields
            amount_str = (
                voucher.get("value")
                or voucher.get("reduction_amount")
                or voucher.get("reduction_percent")
                or "0"
            )

            # Parse amount
            from src.utils.price_parser import parse_price_string
            amount = parse_price_string(str(amount_str))
            if amount is None:
                amount = 0.0

            # Determine discount type
            discount_type = "amount"  # Default
            if "reduction_percent" in voucher or "%" in str(amount_str):
                discount_type = "percentage"

            # Validate rule_id
            if not rule_id or not isinstance(rule_id, int | str):
                logger.warning(f"Invalid rule_id in voucher data: {voucher}")
                continue

            rule_id_int = int(rule_id)

            cart_rule = AutoCartRule(
                rule_id=rule_id_int,
                rule_name=rule_name,
                amount=amount,
                discount_type=discount_type,  # type: ignore[arg-type]
            )
            cart_rules.append(cart_rule)
            logger.debug(f"Parsed cart rule: {cart_rule}")

        except (ValueError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse voucher data: {voucher}, error: {e}")
            continue

    return cart_rules


async def detect_manual_code_input(url: str, timeout: int = 30000) -> bool:
    """Detect if manual promo code input field exists on page.

    This function uses Playwright to load the page and check for
    manual promo code input fields in PrestaShop.

    Args:
        url: Product or cart page URL
        timeout: Page load timeout in milliseconds (default: 30000)

    Returns:
        True if manual code input found, False otherwise

    Raises:
        Exception: If browser automation fails

    Example:
        >>> has_manual = await detect_manual_code_input("https://shop.com/cart")
        >>> if has_manual:
        ...     print("Manual promo code input available")
    """
    logger.debug(f"Detecting manual code input on: {url}")

    async with async_playwright() as p:
        browser: Browser | None = None
        try:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to page
            await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            logger.debug(f"Page loaded: {url}")

            # Check for manual code input
            has_input = await _check_manual_code_input_on_page(page)

            if has_input:
                logger.info(f"Found manual promo code input on {url}")
            else:
                logger.debug(f"No manual promo code input found on: {url}")

            return has_input

        except Exception as e:
            logger.error(f"Failed to detect manual code input on {url}: {e}")
            raise
        finally:
            if browser:
                await browser.close()


async def _check_manual_code_input_on_page(page: Page) -> bool:
    """Check if manual promo code input exists on a loaded page.

    Args:
        page: Playwright Page object

    Returns:
        True if manual code input found, False otherwise
    """
    # Common PrestaShop selectors for promo code input
    promo_code_selectors = [
        "input[name='discount_name']",
        "input[name='voucher']",
        "input[placeholder*='promo' i]",
        "input[placeholder*='code' i]",
        "input[placeholder*='coupon' i]",
        ".promo-code input",
        "#promo-code",
        ".discount-code input",
    ]

    # Try each selector
    for selector in promo_code_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                logger.debug(f"Found promo code input with selector: {selector}")
                return True
        except Exception as e:
            logger.debug(f"Selector '{selector}' failed: {e}")
            continue

    return False
