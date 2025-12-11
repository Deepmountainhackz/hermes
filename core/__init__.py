"""
Core package - Foundation infrastructure for Hermes Intelligence Platform.
"""
from core.config import Config, config
from core.database import DatabaseManager
from core.exceptions import (
    HermesException,
    ConfigurationError,
    DatabaseError,
    APIError,
    ValidationError,
    DataCollectionError,
    ServiceError
)
from core.models import (
    StockData,
    ForexData,
    CommodityData,
    EconomicIndicator,
    WeatherData,
    DisasterEvent,
    SpaceEvent,
    NewsArticle,
    CollectionResult
)
from core.validators import (
    validate_stock_symbol,
    validate_stock_symbols,
    validate_currency_code,
    validate_currency_pair,
    validate_commodity_symbol,
    validate_city_name,
    validate_positive_integer,
    validate_date_range,
    sanitize_string
)

__all__ = [
    "Config",
    "config",
    "DatabaseManager",
    "HermesException",
    "ConfigurationError",
    "DatabaseError",
    "APIError",
    "ValidationError",
    "DataCollectionError",
    "ServiceError",
    "StockData",
    "ForexData",
    "CommodityData",
    "EconomicIndicator",
    "WeatherData",
    "DisasterEvent",
    "SpaceEvent",
    "NewsArticle",
    "CollectionResult",
    # Validators
    "validate_stock_symbol",
    "validate_stock_symbols",
    "validate_currency_code",
    "validate_currency_pair",
    "validate_commodity_symbol",
    "validate_city_name",
    "validate_positive_integer",
    "validate_date_range",
    "sanitize_string",
]
