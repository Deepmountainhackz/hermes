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
]
