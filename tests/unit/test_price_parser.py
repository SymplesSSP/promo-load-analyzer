"""Unit tests for price parser utilities."""

from src.utils.price_parser import (
    calculate_discount_percentage,
    extract_currency,
    parse_price_string,
)


class TestParsePriceString:
    """Tests for parse_price_string function."""

    def test_parse_simple_price(self) -> None:
        """Test parsing simple decimal price."""
        assert parse_price_string("123.45") == 123.45

    def test_parse_price_with_euro_symbol_before(self) -> None:
        """Test parsing with € symbol before."""
        assert parse_price_string("€123.45") == 123.45

    def test_parse_price_with_euro_symbol_after(self) -> None:
        """Test parsing with € symbol after."""
        assert parse_price_string("123.45€") == 123.45

    def test_parse_price_with_dollar(self) -> None:
        """Test parsing with $ symbol."""
        assert parse_price_string("$99.99") == 99.99

    def test_parse_french_format_comma(self) -> None:
        """Test parsing French format with comma."""
        assert parse_price_string("123,45") == 123.45

    def test_parse_french_format_with_spaces(self) -> None:
        """Test parsing French format with spaces."""
        assert parse_price_string("1 234,56 €") == 1234.56

    def test_parse_us_format_with_comma_thousands(self) -> None:
        """Test parsing US format with comma thousands."""
        assert parse_price_string("1,234.56") == 1234.56

    def test_parse_price_with_non_breaking_space(self) -> None:
        """Test parsing with non-breaking space."""
        assert parse_price_string("1\xa0234,56 €") == 1234.56

    def test_parse_large_price(self) -> None:
        """Test parsing large price."""
        assert parse_price_string("12,345.67") == 12345.67

    def test_parse_price_integer(self) -> None:
        """Test parsing integer price."""
        assert parse_price_string("100") == 100.0

    def test_parse_empty_string(self) -> None:
        """Test that empty string returns None."""
        assert parse_price_string("") is None

    def test_parse_none(self) -> None:
        """Test that None returns None."""
        assert parse_price_string(None) is None  # type: ignore

    def test_parse_invalid_string(self) -> None:
        """Test that invalid string returns None."""
        assert parse_price_string("abc") is None

    def test_parse_only_currency_symbol(self) -> None:
        """Test that only currency symbol returns None."""
        assert parse_price_string("€") is None

    def test_parse_mixed_format_french(self) -> None:
        """Test French format with thousands separator."""
        assert parse_price_string("1.234,56") == 1234.56

    def test_parse_price_with_whitespace(self) -> None:
        """Test parsing price with leading/trailing whitespace."""
        assert parse_price_string("  123.45  ") == 123.45

    def test_parse_price_with_pound(self) -> None:
        """Test parsing with £ symbol."""
        assert parse_price_string("£45.99") == 45.99


class TestCalculateDiscountPercentage:
    """Tests for calculate_discount_percentage function."""

    def test_calculate_15_percent_discount(self) -> None:
        """Test calculating 15% discount."""
        result = calculate_discount_percentage(100.0, 85.0)
        assert result == 15.0

    def test_calculate_50_percent_discount(self) -> None:
        """Test calculating 50% discount."""
        result = calculate_discount_percentage(100.0, 50.0)
        assert result == 50.0

    def test_calculate_zero_discount(self) -> None:
        """Test zero discount (same price)."""
        result = calculate_discount_percentage(100.0, 100.0)
        assert result == 0.0

    def test_calculate_discount_with_decimals(self) -> None:
        """Test discount calculation with decimal prices."""
        result = calculate_discount_percentage(99.99, 79.99)
        assert abs(result - 20.0) < 0.1  # ~20% discount

    def test_negative_discount_clamped_to_zero(self) -> None:
        """Test that negative discount is clamped to 0."""
        result = calculate_discount_percentage(100.0, 110.0)
        assert result == 0.0

    def test_over_100_percent_discount_clamped(self) -> None:
        """Test that discount > 100% is clamped to 100."""
        result = calculate_discount_percentage(100.0, -10.0)
        assert result == 100.0

    def test_zero_regular_price(self) -> None:
        """Test with zero regular price."""
        result = calculate_discount_percentage(0.0, 0.0)
        assert result == 0.0

    def test_negative_regular_price(self) -> None:
        """Test with negative regular price."""
        result = calculate_discount_percentage(-100.0, 50.0)
        assert result == 0.0


class TestExtractCurrency:
    """Tests for extract_currency function."""

    def test_extract_euro(self) -> None:
        """Test extracting EUR currency."""
        assert extract_currency("€123.45") == "EUR"

    def test_extract_dollar(self) -> None:
        """Test extracting USD currency."""
        assert extract_currency("$99.99") == "USD"

    def test_extract_pound(self) -> None:
        """Test extracting GBP currency."""
        assert extract_currency("£45.99") == "GBP"

    def test_extract_yen(self) -> None:
        """Test extracting JPY currency."""
        assert extract_currency("¥1000") == "JPY"

    def test_extract_chf(self) -> None:
        """Test extracting CHF currency."""
        assert extract_currency("123.45 CHF") == "CHF"

    def test_no_currency_defaults_to_eur(self) -> None:
        """Test that no currency defaults to EUR."""
        assert extract_currency("123.45") == "EUR"

    def test_empty_string_defaults_to_eur(self) -> None:
        """Test that empty string defaults to EUR."""
        assert extract_currency("") == "EUR"

    def test_none_defaults_to_eur(self) -> None:
        """Test that None defaults to EUR."""
        assert extract_currency(None) == "EUR"  # type: ignore
