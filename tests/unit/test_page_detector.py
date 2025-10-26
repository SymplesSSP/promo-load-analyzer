"""Unit tests for page detector module."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.page_detector import (
    detect_page_type_from_dom,
    detect_page_type_from_url,
    extract_category_id_from_url,
    extract_product_id_from_url,
    is_valid_prestashop_url,
)


class TestDetectPageTypeFromUrl:
    """Tests for detect_page_type_from_url function."""

    def test_detect_homepage(self) -> None:
        """Test homepage detection."""
        result = detect_page_type_from_url("https://shop.example.com/")
        assert result.page_type == "catalog"
        assert result.detection_method == "regex"
        assert result.confidence == 1.0
        assert result.product_id is None
        assert result.category_id is None

    def test_detect_homepage_without_trailing_slash(self) -> None:
        """Test homepage detection without trailing slash."""
        result = detect_page_type_from_url("https://shop.example.com")
        assert result.page_type == "catalog"
        assert result.confidence == 1.0

    def test_detect_product_page(self) -> None:
        """Test product page detection with ID."""
        result = detect_page_type_from_url(
            "https://shop.example.com/123-awesome-product.html"
        )
        assert result.page_type == "product"
        assert result.product_id == 123
        assert result.category_id is None
        assert result.confidence == 1.0

    def test_detect_product_page_with_complex_name(self) -> None:
        """Test product page with complex name including dashes."""
        result = detect_page_type_from_url(
            "https://shop.example.com/456-very-long-product-name-with-many-words.html"
        )
        assert result.page_type == "product"
        assert result.product_id == 456

    def test_detect_category_page(self) -> None:
        """Test category page detection with ID."""
        result = detect_page_type_from_url("https://shop.example.com/electronics/42")
        assert result.page_type == "category"
        assert result.category_id == 42
        assert result.product_id is None
        assert result.confidence == 1.0

    def test_detect_category_page_with_dashes(self) -> None:
        """Test category page with dashes in name."""
        result = detect_page_type_from_url(
            "https://shop.example.com/home-and-garden/789"
        )
        assert result.page_type == "category"
        assert result.category_id == 789

    def test_detect_catalog_promotions(self) -> None:
        """Test catalog page detection for promotions."""
        result = detect_page_type_from_url("https://shop.example.com/promotions")
        assert result.page_type == "catalog"
        assert result.confidence == 1.0

    def test_detect_catalog_nouveautes(self) -> None:
        """Test catalog page detection for new products."""
        result = detect_page_type_from_url("https://shop.example.com/nouveautes")
        assert result.page_type == "catalog"

    def test_detect_catalog_meilleures_ventes(self) -> None:
        """Test catalog page detection for best sellers."""
        result = detect_page_type_from_url(
            "https://shop.example.com/meilleures-ventes"
        )
        assert result.page_type == "catalog"

    def test_detect_unknown_page(self) -> None:
        """Test unknown page type fallback."""
        result = detect_page_type_from_url("https://shop.example.com/about-us")
        assert result.page_type == "unknown"
        assert result.confidence == 0.5  # Lower confidence for unknown

    def test_detect_unknown_page_with_query_params(self) -> None:
        """Test unknown page with query parameters."""
        result = detect_page_type_from_url(
            "https://shop.example.com/search?q=test"
        )
        assert result.page_type == "unknown"

    def test_case_insensitive_detection(self) -> None:
        """Test that detection is case-insensitive."""
        result = detect_page_type_from_url(
            "HTTPS://SHOP.EXAMPLE.COM/PROMOTIONS"
        )
        assert result.page_type == "catalog"

    def test_product_page_with_http(self) -> None:
        """Test product page with HTTP (not HTTPS)."""
        result = detect_page_type_from_url(
            "http://shop.example.com/999-test-product.html"
        )
        assert result.page_type == "product"
        assert result.product_id == 999

    def test_invalid_url_empty_string(self) -> None:
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            detect_page_type_from_url("")

    def test_invalid_url_none(self) -> None:
        """Test that None URL raises ValueError."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            detect_page_type_from_url(None)  # type: ignore

    def test_invalid_url_malformed(self) -> None:
        """Test that malformed URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            detect_page_type_from_url("ht!tp://invalid")

    def test_invalid_url_no_scheme(self) -> None:
        """Test that URL without scheme raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            detect_page_type_from_url("shop.example.com/product")

    def test_url_with_subdirectories(self) -> None:
        """Test product URL with subdirectories."""
        result = detect_page_type_from_url(
            "https://shop.example.com/fr/category/123-product.html"
        )
        assert result.page_type == "product"
        assert result.product_id == 123


class TestExtractProductIdFromUrl:
    """Tests for extract_product_id_from_url function."""

    def test_extract_product_id_valid(self) -> None:
        """Test extracting product ID from valid URL."""
        product_id = extract_product_id_from_url(
            "https://shop.example.com/123-product.html"
        )
        assert product_id == 123

    def test_extract_product_id_large_number(self) -> None:
        """Test extracting large product ID."""
        product_id = extract_product_id_from_url(
            "https://shop.example.com/999999-product.html"
        )
        assert product_id == 999999

    def test_extract_product_id_from_category_url(self) -> None:
        """Test that category URL returns None."""
        product_id = extract_product_id_from_url(
            "https://shop.example.com/category/42"
        )
        assert product_id is None

    def test_extract_product_id_from_invalid_url(self) -> None:
        """Test that invalid URL returns None."""
        product_id = extract_product_id_from_url("not-a-url")
        assert product_id is None


class TestExtractCategoryIdFromUrl:
    """Tests for extract_category_id_from_url function."""

    def test_extract_category_id_valid(self) -> None:
        """Test extracting category ID from valid URL."""
        category_id = extract_category_id_from_url(
            "https://shop.example.com/electronics/42"
        )
        assert category_id == 42

    def test_extract_category_id_with_dashes(self) -> None:
        """Test extracting category ID with dashes in name."""
        category_id = extract_category_id_from_url(
            "https://shop.example.com/home-and-garden/789"
        )
        assert category_id == 789

    def test_extract_category_id_from_product_url(self) -> None:
        """Test that product URL returns None."""
        category_id = extract_category_id_from_url(
            "https://shop.example.com/123-product.html"
        )
        assert category_id is None

    def test_extract_category_id_from_invalid_url(self) -> None:
        """Test that invalid URL returns None."""
        category_id = extract_category_id_from_url("invalid")
        assert category_id is None


class TestIsValidPrestashopUrl:
    """Tests for is_valid_prestashop_url function."""

    def test_valid_https_url(self) -> None:
        """Test valid HTTPS URL."""
        assert is_valid_prestashop_url("https://shop.example.com/product") is True

    def test_valid_http_url(self) -> None:
        """Test valid HTTP URL."""
        assert is_valid_prestashop_url("http://shop.example.com") is True

    def test_invalid_url_no_scheme(self) -> None:
        """Test URL without scheme."""
        assert is_valid_prestashop_url("shop.example.com") is False

    def test_invalid_url_ftp(self) -> None:
        """Test FTP URL (not supported)."""
        assert is_valid_prestashop_url("ftp://shop.example.com") is False

    def test_invalid_url_empty(self) -> None:
        """Test empty URL."""
        assert is_valid_prestashop_url("") is False

    def test_invalid_url_malformed(self) -> None:
        """Test malformed URL."""
        assert is_valid_prestashop_url("ht!tp://invalid") is False


class TestDetectPageTypeFromDom:
    """Tests for detect_page_type_from_dom function."""

    @patch("src.page_detector.requests.get")
    def test_detect_product_page_with_add_to_cart(
        self, mock_get: Mock
    ) -> None:
        """Test product page detection via add-to-cart button."""
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <button class="add-to-cart">Add to Cart</button>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = detect_page_type_from_dom("https://shop.example.com/page")

        assert result.page_type == "product"
        assert result.detection_method == "dom_analysis"
        assert result.has_add_to_cart is True
        assert result.confidence == 0.9

    @patch("src.page_detector.requests.get")
    def test_detect_category_page_with_products(
        self, mock_get: Mock
    ) -> None:
        """Test category page detection via product list."""
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <div class="products">
                    <div class="product-miniature">Product 1</div>
                    <div class="product-miniature">Product 2</div>
                </div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = detect_page_type_from_dom("https://shop.example.com/page")

        assert result.page_type == "category"
        assert result.detection_method == "dom_analysis"
        assert result.has_add_to_cart is False
        assert result.confidence == 0.8

    @patch("src.page_detector.requests.get")
    def test_detect_promo_code_input(self, mock_get: Mock) -> None:
        """Test detection of promo code input."""
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <button class="add-to-cart">Add to Cart</button>
                <input name="discount_name" type="text" />
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = detect_page_type_from_dom("https://shop.example.com/page")

        assert result.page_type == "product"
        assert result.has_promo_code_input is True

    @patch("src.page_detector.requests.get")
    def test_detect_unknown_page(self, mock_get: Mock) -> None:
        """Test unknown page detection when no indicators found."""
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <div>Some content</div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = detect_page_type_from_dom("https://shop.example.com/page")

        assert result.page_type == "unknown"
        assert result.detection_method == "dom_analysis"
        assert result.confidence == 0.5

    @patch("src.page_detector.requests.get")
    def test_invalid_url_raises_error(self, mock_get: Mock) -> None:
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid URL"):
            detect_page_type_from_dom("not-a-url")

    @patch("src.page_detector.requests.get")
    def test_request_exception_raises(self, mock_get: Mock) -> None:
        """Test that request exception is propagated."""
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(requests.RequestException):
            detect_page_type_from_dom("https://shop.example.com/page")

    @patch("src.page_detector.requests.get")
    def test_http_error_raises(self, mock_get: Mock) -> None:
        """Test that HTTP error is raised."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            detect_page_type_from_dom("https://shop.example.com/page")

    @patch("src.page_detector.requests.get")
    def test_custom_timeout(self, mock_get: Mock) -> None:
        """Test custom timeout parameter."""
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        detect_page_type_from_dom("https://shop.example.com/page", timeout=5)

        mock_get.assert_called_once_with(
            "https://shop.example.com/page", timeout=5
        )

    @patch("src.page_detector.requests.get")
    def test_multiple_add_to_cart_selectors(self, mock_get: Mock) -> None:
        """Test detection with alternative add-to-cart selector."""
        mock_response = Mock()
        mock_response.text = """
        <html>
            <body>
                <button data-button-action="add-to-cart">Add</button>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = detect_page_type_from_dom("https://shop.example.com/page")

        assert result.page_type == "product"
        assert result.has_add_to_cart is True
