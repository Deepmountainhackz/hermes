"""
Collectors Package
Orchestration layer for the Hermes Intelligence Platform.

Each collector coordinates the setup and data collection for a specific
data domain, wiring together Config, Repository, and Service layers.
"""
from .markets_collector import MarketsCollector
from .commodities_collector import CommoditiesCollector
from .forex_collector import ForexCollector
from .economics_collector import EconomicsCollector
from .weather_collector import WeatherCollector
from .space_collector import SpaceCollector
from .disasters_collector import DisastersCollector
from .news_collector import NewsCollector
from .crypto_collector import CryptoCollector
from .gdelt_collector import GdeltCollector

__all__ = [
    'MarketsCollector',
    'CommoditiesCollector',
    'ForexCollector',
    'EconomicsCollector',
    'WeatherCollector',
    'SpaceCollector',
    'DisastersCollector',
    'NewsCollector',
    'CryptoCollector',
    'GdeltCollector',
]
