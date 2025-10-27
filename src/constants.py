"""Application-wide constants for Promo Load Analyzer.

This module defines all constants used throughout the application.
These values should not be changed at runtime.
"""

from typing import Final

# Application Metadata
APP_NAME: Final[str] = "Promo Load Analyzer"
APP_VERSION: Final[str] = "0.1.0"
APP_DESCRIPTION: Final[str] = (
    "CLI tool for load testing PrestaShop promotions before Black Friday"
)

# Page Types
PAGE_TYPE_CATEGORY: Final[str] = "category"
PAGE_TYPE_PRODUCT: Final[str] = "product"
PAGE_TYPE_CATALOG: Final[str] = "catalog"
PAGE_TYPE_UNKNOWN: Final[str] = "unknown"

VALID_PAGE_TYPES: Final[tuple[str, ...]] = (
    PAGE_TYPE_CATEGORY,
    PAGE_TYPE_PRODUCT,
    PAGE_TYPE_CATALOG,
)

# Promotion Types
PROMO_TYPE_PERCENTAGE: Final[str] = "percentage"  # e.g., -15%
PROMO_TYPE_SECOND_HALF_PRICE: Final[str] = "second_half_price"  # 2nd half price
PROMO_TYPE_FREE_SHIPPING: Final[str] = "free_shipping"  # Free shipping >79€

VALID_PROMO_TYPES: Final[tuple[str, ...]] = (
    PROMO_TYPE_PERCENTAGE,
    PROMO_TYPE_SECOND_HALF_PRICE,
    PROMO_TYPE_FREE_SHIPPING,
)

# Environments
ENV_PREPROD: Final[str] = "PREPROD"
ENV_PROD: Final[str] = "PROD"

VALID_ENVIRONMENTS: Final[tuple[str, ...]] = (ENV_PREPROD, ENV_PROD)

# PROD Safety Limits (hardcoded for safety)
PROD_ABSOLUTE_MAX_VUS: Final[int] = 100
PROD_ABSOLUTE_MAX_DURATION_HOURS: Final[int] = 2

# Performance Grades
GRADE_A: Final[str] = "A"
GRADE_B: Final[str] = "B"
GRADE_C: Final[str] = "C"
GRADE_D: Final[str] = "D"
GRADE_F: Final[str] = "F"

VALID_GRADES: Final[tuple[str, ...]] = (
    GRADE_A,
    GRADE_B,
    GRADE_C,
    GRADE_D,
    GRADE_F,
)

# Scoring Weights
WEIGHT_P95: Final[float] = 0.6  # 60% weight for p95 response time
WEIGHT_ERROR_RATE: Final[float] = 0.4  # 40% weight for error rate

# K6 Exit Codes
K6_EXIT_SUCCESS: Final[int] = 0
K6_EXIT_THRESHOLD_ABORT: Final[int] = 99  # Expected when thresholds fail
K6_EXIT_ERROR: Final[int] = 1  # Generic error

# HTTP Status Codes
HTTP_OK: Final[int] = 200
HTTP_CREATED: Final[int] = 201
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_FORBIDDEN: Final[int] = 403
HTTP_NOT_FOUND: Final[int] = 404
HTTP_SERVER_ERROR: Final[int] = 500

SUCCESS_STATUS_CODES: Final[tuple[int, ...]] = (HTTP_OK, HTTP_CREATED)

# Regex Patterns for Page Detection
REGEX_PRODUCT_PAGE: Final[str] = r"/(\d+)(?:-\d+)?-[\w-]+"  # Captures product ID (with optional attribute ID, with or without .html)
REGEX_CATEGORY_PAGE: Final[str] = r"/[\w-]+/(\d+)(?!-\d)"  # Captures category ID (but not product URLs like /cat/123-456-name)
REGEX_CATALOG_PAGE: Final[str] = r"/(nouveautes|promotions|meilleures-ventes)"
REGEX_HOMEPAGE: Final[str] = r"^https?://[^/]+/?$"  # Matches root URL only

# PrestaShop Selectors
SELECTOR_PROMO_BADGE: Final[str] = ".product-flag.discount"
SELECTOR_PRODUCT_PRICE: Final[str] = ".product-price"
SELECTOR_PRODUCT_TITLE: Final[str] = ".product-title"
SELECTOR_ADD_TO_CART: Final[str] = ".add-to-cart"

# K6 Template Placeholders
K6_PLACEHOLDER_URL: Final[str] = "{{TARGET_URL}}"
K6_PLACEHOLDER_VUS: Final[str] = "{{VUS}}"
K6_PLACEHOLDER_DURATION: Final[str] = "{{DURATION}}"
K6_PLACEHOLDER_RAMP_UP: Final[str] = "{{RAMP_UP}}"

# File Extensions
EXT_JSON: Final[str] = ".json"
EXT_HTML: Final[str] = ".html"
EXT_JS: Final[str] = ".js"
EXT_LOG: Final[str] = ".log"

# Timeouts (milliseconds)
TIMEOUT_PAGE_LOAD: Final[int] = 30000
TIMEOUT_NETWORK: Final[int] = 15000
TIMEOUT_K6_EXECUTION: Final[int] = 600000  # 10 minutes

# Retry Configuration
MAX_RETRIES_API: Final[int] = 2
MAX_RETRIES_SCRAPING: Final[int] = 2
RETRY_BACKOFF_FACTOR: Final[float] = 2.0  # Exponential backoff

# CLI Output Colors (for rich formatting)
COLOR_SUCCESS: Final[str] = "green"
COLOR_WARNING: Final[str] = "yellow"
COLOR_ERROR: Final[str] = "red"
COLOR_INFO: Final[str] = "blue"

# Correlation ID
CORRELATION_ID_LENGTH: Final[int] = 16
CORRELATION_ID_PREFIX: Final[str] = "PLA"
