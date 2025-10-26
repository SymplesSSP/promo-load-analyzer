"""Page type detection module.

This module detects PrestaShop page types from URLs using regex patterns.
Supports product, category, catalog (homepage variants), and unknown pages.
"""

import re
from urllib.parse import urlparse

from loguru import logger

from src.constants import (
    PAGE_TYPE_CATALOG,
    PAGE_TYPE_CATEGORY,
    PAGE_TYPE_PRODUCT,
    PAGE_TYPE_UNKNOWN,
    REGEX_CATALOG_PAGE,
    REGEX_CATEGORY_PAGE,
    REGEX_HOMEPAGE,
    REGEX_PRODUCT_PAGE,
)
from src.models import PageDetectionResult


def detect_page_type_from_url(url: str) -> PageDetectionResult:
    """Detect page type from URL using regex patterns.

    Detection strategy:
    1. Homepage: Root URL (http://example.com/)
    2. Product: /123-product-name.html (with product ID)
    3. Category: /category-name/456 (with category ID)
    4. Catalog: /nouveautes, /promotions, /meilleures-ventes
    5. Unknown: Fallback for unrecognized patterns

    Args:
        url: The URL to analyze

    Returns:
        PageDetectionResult with detected type, IDs, and metadata

    Raises:
        ValueError: If URL is invalid or malformed

    Example:
        >>> result = detect_page_type_from_url("https://shop.com/123-product.html")
        >>> result.page_type
        'product'
        >>> result.product_id
        123
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    # Validate URL format
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {url}") from e

    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL format: {url}")

    # Normalize URL for matching
    url_lower = url.lower()
    path = parsed.path.lower()  # Lowercase path for case-insensitive matching

    logger.debug(f"Detecting page type for URL: {url}")

    # 1. Check for homepage
    if re.match(REGEX_HOMEPAGE, url_lower):
        logger.info(f"Detected homepage: {url}")
        return PageDetectionResult(
            page_type=PAGE_TYPE_CATALOG,  # type: ignore[arg-type]
            detection_method="regex",
            url=url,  # type: ignore[arg-type]
            confidence=1.0,
        )

    # 2. Check for product page
    product_match = re.search(REGEX_PRODUCT_PAGE, path)
    if product_match:
        product_id = int(product_match.group(1))
        logger.info(f"Detected product page: {url} (ID: {product_id})")
        return PageDetectionResult(
            page_type=PAGE_TYPE_PRODUCT,  # type: ignore[arg-type]
            detection_method="regex",
            url=url,  # type: ignore[arg-type]
            product_id=product_id,
            confidence=1.0,
        )

    # 3. Check for category page
    category_match = re.search(REGEX_CATEGORY_PAGE, path)
    if category_match:
        category_id = int(category_match.group(1))
        logger.info(f"Detected category page: {url} (ID: {category_id})")
        return PageDetectionResult(
            page_type=PAGE_TYPE_CATEGORY,  # type: ignore[arg-type]
            detection_method="regex",
            url=url,  # type: ignore[arg-type]
            category_id=category_id,
            confidence=1.0,
        )

    # 4. Check for catalog page (promotions, new products, best sellers)
    catalog_match = re.search(REGEX_CATALOG_PAGE, path)
    if catalog_match:
        catalog_type = catalog_match.group(1)
        logger.info(f"Detected catalog page: {url} (type: {catalog_type})")
        return PageDetectionResult(
            page_type=PAGE_TYPE_CATALOG,  # type: ignore[arg-type]
            detection_method="regex",
            url=url,  # type: ignore[arg-type]
            confidence=1.0,
        )

    # 5. Fallback to unknown
    logger.warning(f"Could not detect page type for: {url}")
    return PageDetectionResult(
        page_type=PAGE_TYPE_UNKNOWN,  # type: ignore[arg-type]
        detection_method="regex",
        url=url,  # type: ignore[arg-type]
        confidence=0.5,  # Lower confidence for unknown pages
    )


def extract_product_id_from_url(url: str) -> int | None:
    """Extract product ID from a PrestaShop product URL.

    Args:
        url: Product page URL

    Returns:
        Product ID if found, None otherwise

    Example:
        >>> extract_product_id_from_url("https://shop.com/123-product.html")
        123
    """
    try:
        parsed = urlparse(url)
        match = re.search(REGEX_PRODUCT_PAGE, parsed.path)
        if match:
            return int(match.group(1))
    except Exception as e:
        logger.warning(f"Failed to extract product ID from {url}: {e}")
    return None


def extract_category_id_from_url(url: str) -> int | None:
    """Extract category ID from a PrestaShop category URL.

    Args:
        url: Category page URL

    Returns:
        Category ID if found, None otherwise

    Example:
        >>> extract_category_id_from_url("https://shop.com/electronics/42")
        42
    """
    try:
        parsed = urlparse(url)
        match = re.search(REGEX_CATEGORY_PAGE, parsed.path)
        if match:
            return int(match.group(1))
    except Exception as e:
        logger.warning(f"Failed to extract category ID from {url}: {e}")
    return None


def is_valid_prestashop_url(url: str) -> bool:
    """Check if URL is a valid PrestaShop URL.

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False
