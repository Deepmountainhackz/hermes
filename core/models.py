"""
Data Models
Type-safe dataclasses for domain objects.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from decimal import Decimal


@dataclass
class StockData:
    """Stock market data model."""
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'timestamp': self.timestamp
        }


@dataclass
class ForexData:
    """Foreign exchange rate data model."""
    pair: str
    from_currency: str
    to_currency: str
    rate: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'pair': self.pair,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': self.rate,
            'bid': self.bid,
            'ask': self.ask,
            'timestamp': self.timestamp
        }


@dataclass
class CommodityData:
    """Commodity price data model."""
    symbol: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    unit: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'unit': self.unit,
            'timestamp': self.timestamp
        }


@dataclass
class EconomicIndicator:
    """Economic indicator data model."""
    indicator: str
    country: str
    name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'indicator': self.indicator,
            'country': self.country,
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp
        }


@dataclass
class WeatherData:
    """Weather observation data model."""
    city: str
    country: Optional[str] = None
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[int] = None
    wind_speed: Optional[float] = None
    description: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'city': self.city,
            'country': self.country,
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'description': self.description,
            'timestamp': self.timestamp
        }


@dataclass
class DisasterEvent:
    """Disaster event data model."""
    disaster_type: str
    location: Optional[str] = None
    magnitude: Optional[float] = None
    description: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'disaster_type': self.disaster_type,
            'location': self.location,
            'magnitude': self.magnitude,
            'description': self.description,
            'timestamp': self.timestamp
        }


@dataclass
class SpaceEvent:
    """Space event data model."""
    event_type: str
    name: Optional[str] = None
    description: Optional[str] = None
    data: Optional[str] = None  # JSON string
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'event_type': self.event_type,
            'name': self.name,
            'description': self.description,
            'data': self.data,
            'timestamp': self.timestamp
        }


@dataclass
class NewsArticle:
    """News article data model."""
    title: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            'title': self.title,
            'source': self.source,
            'url': self.url,
            'description': self.description,
            'published_at': self.published_at,
            'timestamp': self.timestamp
        }


@dataclass
class CollectionResult:
    """Result of a data collection operation."""
    total: int
    successful: int
    failed: int
    duration_seconds: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100
