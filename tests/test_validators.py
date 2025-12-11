"""
Tests for Input Validators
"""
import pytest
from datetime import datetime, timedelta

from core.validators import (
    validate_stock_symbol,
    validate_stock_symbols,
    validate_currency_code,
    validate_currency_pair,
    validate_commodity_symbol,
    validate_city_name,
    validate_positive_integer,
    validate_date_range,
    sanitize_string,
    VALID_CURRENCY_CODES,
    VALID_COMMODITY_SYMBOLS
)
from core.exceptions import ValidationError


class TestStockSymbolValidation:
    """Test suite for stock symbol validation."""

    @pytest.mark.unit
    def test_validate_stock_symbol_valid(self):
        """Test valid stock symbols."""
        assert validate_stock_symbol('AAPL') == 'AAPL'
        assert validate_stock_symbol('msft') == 'MSFT'
        assert validate_stock_symbol('  googl  ') == 'GOOGL'
        assert validate_stock_symbol('BRK.A') == 'BRK.A'
        assert validate_stock_symbol('BRK.B') == 'BRK.B'

    @pytest.mark.unit
    def test_validate_stock_symbol_empty(self):
        """Test empty stock symbol raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_stock_symbol('')
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_stock_symbol(None)

    @pytest.mark.unit
    def test_validate_stock_symbol_invalid_format(self):
        """Test invalid format raises error."""
        with pytest.raises(ValidationError, match="Invalid stock symbol format"):
            validate_stock_symbol('TOOLONG')  # More than 5 chars
        with pytest.raises(ValidationError, match="Invalid stock symbol format"):
            validate_stock_symbol('123')  # Numbers only
        with pytest.raises(ValidationError, match="Invalid stock symbol format"):
            validate_stock_symbol('AAP L')  # Contains space

    @pytest.mark.unit
    def test_validate_stock_symbols_list(self):
        """Test validating list of stock symbols."""
        result = validate_stock_symbols(['AAPL', 'msft', 'GOOGL'])
        assert result == ['AAPL', 'MSFT', 'GOOGL']

    @pytest.mark.unit
    def test_validate_stock_symbols_empty_list(self):
        """Test empty list raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_stock_symbols([])

    @pytest.mark.unit
    def test_validate_stock_symbols_with_invalid(self):
        """Test list with invalid symbols raises error."""
        with pytest.raises(ValidationError, match="Invalid stock symbols"):
            validate_stock_symbols(['AAPL', 'INVALID123', 'TOOLONGSYMBOL'])


class TestCurrencyValidation:
    """Test suite for currency code validation."""

    @pytest.mark.unit
    def test_validate_currency_code_valid(self):
        """Test valid currency codes."""
        assert validate_currency_code('USD') == 'USD'
        assert validate_currency_code('eur') == 'EUR'
        assert validate_currency_code('  gbp  ') == 'GBP'

    @pytest.mark.unit
    def test_validate_currency_code_empty(self):
        """Test empty currency code raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_currency_code('')

    @pytest.mark.unit
    def test_validate_currency_code_invalid_format(self):
        """Test invalid format raises error."""
        with pytest.raises(ValidationError, match="Invalid currency code format"):
            validate_currency_code('US')  # Too short
        with pytest.raises(ValidationError, match="Invalid currency code format"):
            validate_currency_code('USDD')  # Too long
        with pytest.raises(ValidationError, match="Invalid currency code format"):
            validate_currency_code('123')  # Numbers

    @pytest.mark.unit
    def test_validate_currency_pair_valid(self):
        """Test valid currency pair."""
        result = validate_currency_pair('EUR', 'USD')
        assert result == ('EUR', 'USD')

    @pytest.mark.unit
    def test_validate_currency_pair_same_currency(self):
        """Test same currency raises error."""
        with pytest.raises(ValidationError, match="must be different"):
            validate_currency_pair('USD', 'USD')


class TestCommodityValidation:
    """Test suite for commodity symbol validation."""

    @pytest.mark.unit
    def test_validate_commodity_symbol_valid(self):
        """Test valid commodity symbols."""
        assert validate_commodity_symbol('WTI') == 'WTI'
        assert validate_commodity_symbol('gold') == 'GOLD'
        assert validate_commodity_symbol('  COPPER  ') == 'COPPER'

    @pytest.mark.unit
    def test_validate_commodity_symbol_empty(self):
        """Test empty commodity symbol raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_commodity_symbol('')

    @pytest.mark.unit
    def test_validate_commodity_symbol_unknown(self):
        """Test unknown commodity raises error."""
        with pytest.raises(ValidationError, match="Unknown commodity symbol"):
            validate_commodity_symbol('UNOBTAINIUM')


class TestCityValidation:
    """Test suite for city name validation."""

    @pytest.mark.unit
    def test_validate_city_name_valid(self):
        """Test valid city names."""
        assert validate_city_name('London') == 'London'
        assert validate_city_name('New York') == 'New York'
        assert validate_city_name("Saint-Denis") == "Saint-Denis"
        assert validate_city_name("O'Fallon") == "O'Fallon"

    @pytest.mark.unit
    def test_validate_city_name_empty(self):
        """Test empty city name raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_city_name('')

    @pytest.mark.unit
    def test_validate_city_name_too_short(self):
        """Test too short city name raises error."""
        with pytest.raises(ValidationError, match="at least 2 characters"):
            validate_city_name('A')

    @pytest.mark.unit
    def test_validate_city_name_too_long(self):
        """Test too long city name raises error."""
        with pytest.raises(ValidationError, match="less than 100 characters"):
            validate_city_name('A' * 101)


class TestNumericValidation:
    """Test suite for numeric validation."""

    @pytest.mark.unit
    def test_validate_positive_integer_valid(self):
        """Test valid positive integers."""
        assert validate_positive_integer(1) == 1
        assert validate_positive_integer(100) == 100

    @pytest.mark.unit
    def test_validate_positive_integer_zero(self):
        """Test zero raises error."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_integer(0)

    @pytest.mark.unit
    def test_validate_positive_integer_negative(self):
        """Test negative raises error."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_positive_integer(-5)

    @pytest.mark.unit
    def test_validate_positive_integer_non_integer(self):
        """Test non-integer raises error."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_integer(3.14)
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_positive_integer("5")


class TestDateRangeValidation:
    """Test suite for date range validation."""

    @pytest.mark.unit
    def test_validate_date_range_defaults(self):
        """Test default date range."""
        start, end = validate_date_range()
        assert end <= datetime.now()
        assert (end - start).days == 30

    @pytest.mark.unit
    def test_validate_date_range_valid(self):
        """Test valid date range."""
        end = datetime.now()
        start = end - timedelta(days=7)
        result_start, result_end = validate_date_range(start, end)
        assert result_start == start
        assert result_end == end

    @pytest.mark.unit
    def test_validate_date_range_invalid_order(self):
        """Test invalid date order raises error."""
        end = datetime.now()
        start = end + timedelta(days=1)
        with pytest.raises(ValidationError, match="before end date"):
            validate_date_range(start, end)

    @pytest.mark.unit
    def test_validate_date_range_future(self):
        """Test future end date raises error."""
        end = datetime.now() + timedelta(days=1)
        start = datetime.now()
        with pytest.raises(ValidationError, match="cannot be in the future"):
            validate_date_range(start, end)

    @pytest.mark.unit
    def test_validate_date_range_too_large(self):
        """Test too large date range raises error."""
        end = datetime.now()
        start = end - timedelta(days=400)
        with pytest.raises(ValidationError, match="too large"):
            validate_date_range(start, end)


class TestStringSanitization:
    """Test suite for string sanitization."""

    @pytest.mark.unit
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        assert sanitize_string('  hello  ') == 'hello'
        assert sanitize_string('hello\nworld') == 'hello\nworld'
        assert sanitize_string('hello\tworld') == 'hello\tworld'

    @pytest.mark.unit
    def test_sanitize_string_empty(self):
        """Test empty string returns empty."""
        assert sanitize_string('') == ''
        assert sanitize_string(None) == ''

    @pytest.mark.unit
    def test_sanitize_string_truncation(self):
        """Test string truncation."""
        long_string = 'a' * 1000
        result = sanitize_string(long_string, max_length=100)
        assert len(result) == 100
