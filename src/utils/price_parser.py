"""Price parsing utilities.

This module provides functions to parse price strings from various formats.
"""

import re

from loguru import logger


def parse_price_string(price_str: str) -> float | None:
    """Parse a price string to float.

    Handles various formats:
    - "€123.45" or "123.45€"
    - "$123.45" or "123.45$"
    - "123,45 €" (French format)
    - "1 234,56 €" (with thousands separator)
    - "1,234.56" (US format)

    Args:
        price_str: Price string to parse

    Returns:
        Parsed price as float, or None if parsing fails

    Example:
        >>> parse_price_string("€123.45")
        123.45
        >>> parse_price_string("1 234,56 €")
        1234.56
    """
    if not price_str or not isinstance(price_str, str):
        return None

    # Remove whitespace and currency symbols
    cleaned = price_str.strip()
    cleaned = re.sub(r"[€$£¥]", "", cleaned)
    cleaned = cleaned.strip()

    # Remove non-breaking spaces and regular spaces
    cleaned = cleaned.replace("\xa0", "").replace(" ", "")

    if not cleaned:
        return None

    try:
        # Try to detect format
        # French/European format: 1.234,56 or 1234,56
        if "," in cleaned and "." in cleaned:
            # If both exist, check which is last (decimal separator)
            if cleaned.rfind(",") > cleaned.rfind("."):
                # French format: 1.234,56
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                # US format: 1,234.56
                cleaned = cleaned.replace(",", "")
        elif "," in cleaned:
            # Only comma - could be French decimal or thousands
            # If only one comma and digits after it <= 2, likely decimal
            parts = cleaned.split(",")
            if len(parts) == 2 and len(parts[1]) <= 2:
                # French decimal: 1234,56
                cleaned = cleaned.replace(",", ".")
            else:
                # Thousands separator: remove
                cleaned = cleaned.replace(",", "")
        elif "." in cleaned:
            # Only dot - could be decimal or thousands
            parts = cleaned.split(".")
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Decimal: 1234.56
                pass
            else:
                # Thousands separator: remove
                cleaned = cleaned.replace(".", "")

        # Parse to float
        price = float(cleaned)
        return price

    except (ValueError, AttributeError) as e:
        logger.warning(f"Failed to parse price string '{price_str}': {e}")
        return None


def calculate_discount_percentage(regular_price: float, current_price: float) -> float:
    """Calculate discount percentage.

    Args:
        regular_price: Original price before discount
        current_price: Current discounted price

    Returns:
        Discount percentage (0.0 to 100.0)

    Example:
        >>> calculate_discount_percentage(100.0, 85.0)
        15.0
    """
    if regular_price <= 0:
        return 0.0

    discount = ((regular_price - current_price) / regular_price) * 100
    return max(0.0, min(100.0, discount))  # Clamp to 0-100


def extract_currency(price_str: str) -> str:
    """Extract currency symbol from price string.

    Args:
        price_str: Price string containing currency

    Returns:
        Currency code (EUR, USD, GBP, etc.) or "EUR" as default

    Example:
        >>> extract_currency("€123.45")
        'EUR'
        >>> extract_currency("$99.99")
        'USD'
    """
    if not price_str:
        return "EUR"

    currency_map = {
        "€": "EUR",
        "$": "USD",
        "£": "GBP",
        "¥": "JPY",
        "CHF": "CHF",
    }

    for symbol, code in currency_map.items():
        if symbol in price_str:
            return code

    return "EUR"  # Default to EUR
