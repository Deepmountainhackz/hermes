"""
Input Validators
Validation utilities for API parameters and data inputs.
"""
import re
from typing import List, Optional, Set
from datetime import datetime

from core.exceptions import ValidationError


# Valid stock symbol pattern (1-5 uppercase letters, optional dot)
STOCK_SYMBOL_PATTERN = re.compile(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$')

# Valid currency code pattern (3 uppercase letters)
CURRENCY_CODE_PATTERN = re.compile(r'^[A-Z]{3}$')

# Common valid stock exchanges
VALID_EXCHANGES = {'NYSE', 'NASDAQ', 'AMEX', 'LSE', 'TSE'}

# ISO 4217 currency codes (subset of common ones)
VALID_CURRENCY_CODES = {
    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY', 'HKD', 'NZD',
    'SEK', 'NOK', 'DKK', 'SGD', 'MXN', 'BRL', 'INR', 'RUB', 'ZAR', 'KRW'
}

# Valid commodity symbols
VALID_COMMODITY_SYMBOLS = {
    'WTI', 'BRENT', 'NATURAL_GAS', 'COPPER', 'ALUMINUM', 'ZINC',
    'WHEAT', 'CORN', 'SOYBEANS', 'COFFEE', 'SUGAR', 'COTTON',
    'GOLD', 'SILVER', 'PLATINUM', 'PALLADIUM'
}


def validate_stock_symbol(symbol: str) -> str:
    """
    Validate and normalize a stock symbol.

    Args:
        symbol: Stock symbol to validate

    Returns:
        Normalized uppercase symbol

    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol:
        raise ValidationError("Stock symbol cannot be empty")

    symbol = symbol.upper().strip()

    if not STOCK_SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid stock symbol format: '{symbol}'. "
            "Must be 1-5 uppercase letters, optionally followed by .XX"
        )

    return symbol


def validate_stock_symbols(symbols: List[str]) -> List[str]:
    """
    Validate and normalize a list of stock symbols.

    Args:
        symbols: List of stock symbols

    Returns:
        List of normalized symbols

    Raises:
        ValidationError: If any symbol is invalid
    """
    if not symbols:
        raise ValidationError("Stock symbols list cannot be empty")

    validated = []
    invalid = []

    for symbol in symbols:
        try:
            validated.append(validate_stock_symbol(symbol))
        except ValidationError:
            invalid.append(symbol)

    if invalid:
        raise ValidationError(f"Invalid stock symbols: {', '.join(invalid)}")

    return validated


def validate_currency_code(code: str) -> str:
    """
    Validate and normalize a currency code.

    Args:
        code: Currency code to validate

    Returns:
        Normalized uppercase currency code

    Raises:
        ValidationError: If code is invalid
    """
    if not code:
        raise ValidationError("Currency code cannot be empty")

    code = code.upper().strip()

    if not CURRENCY_CODE_PATTERN.match(code):
        raise ValidationError(
            f"Invalid currency code format: '{code}'. Must be 3 uppercase letters"
        )

    if code not in VALID_CURRENCY_CODES:
        # Warning but allow - could be a valid but uncommon currency
        pass

    return code


def validate_currency_pair(from_currency: str, to_currency: str) -> tuple:
    """
    Validate a currency pair.

    Args:
        from_currency: Source currency code
        to_currency: Target currency code

    Returns:
        Tuple of (from_currency, to_currency) normalized

    Raises:
        ValidationError: If either code is invalid or they are the same
    """
    from_curr = validate_currency_code(from_currency)
    to_curr = validate_currency_code(to_currency)

    if from_curr == to_curr:
        raise ValidationError("From and to currency codes must be different")

    return (from_curr, to_curr)


def validate_commodity_symbol(symbol: str) -> str:
    """
    Validate a commodity symbol.

    Args:
        symbol: Commodity symbol to validate

    Returns:
        Normalized uppercase symbol

    Raises:
        ValidationError: If symbol is not recognized
    """
    if not symbol:
        raise ValidationError("Commodity symbol cannot be empty")

    symbol = symbol.upper().strip()

    if symbol not in VALID_COMMODITY_SYMBOLS:
        raise ValidationError(
            f"Unknown commodity symbol: '{symbol}'. "
            f"Valid symbols: {', '.join(sorted(VALID_COMMODITY_SYMBOLS))}"
        )

    return symbol


def validate_city_name(city: str) -> str:
    """
    Validate and normalize a city name.

    Args:
        city: City name to validate

    Returns:
        Normalized city name

    Raises:
        ValidationError: If city name is invalid
    """
    if not city:
        raise ValidationError("City name cannot be empty")

    city = city.strip()

    if len(city) < 2:
        raise ValidationError("City name must be at least 2 characters")

    if len(city) > 100:
        raise ValidationError("City name must be less than 100 characters")

    # Basic sanitization - only allow letters, spaces, hyphens, apostrophes
    if not re.match(r"^[\w\s\-']+$", city, re.UNICODE):
        raise ValidationError(
            f"Invalid city name: '{city}'. Contains invalid characters"
        )

    return city


def validate_positive_integer(value: int, name: str = "value") -> int:
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate
        name: Name of the parameter for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If value is not a positive integer
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer, got {type(value).__name__}")

    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")

    return value


def validate_date_range(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_days: int = 365
) -> tuple:
    """
    Validate a date range.

    Args:
        start_date: Start of the date range
        end_date: End of the date range
        max_days: Maximum allowed days in range

    Returns:
        Tuple of (start_date, end_date)

    Raises:
        ValidationError: If date range is invalid
    """
    now = datetime.now()

    if end_date is None:
        end_date = now

    if start_date is None:
        from datetime import timedelta
        start_date = end_date - timedelta(days=30)

    if start_date > end_date:
        raise ValidationError("Start date must be before end date")

    if end_date > now:
        raise ValidationError("End date cannot be in the future")

    days_diff = (end_date - start_date).days
    if days_diff > max_days:
        raise ValidationError(
            f"Date range too large: {days_diff} days. Maximum allowed: {max_days}"
        )

    return (start_date, end_date)


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string input.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string

    Raises:
        ValidationError: If string is too long after sanitization
    """
    if not value:
        return ""

    # Strip whitespace
    value = value.strip()

    # Remove control characters
    value = ''.join(char for char in value if char.isprintable() or char in '\n\t')

    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]

    return value
