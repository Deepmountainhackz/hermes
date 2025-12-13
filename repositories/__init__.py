"""
Repositories Package
Data access layer for the Hermes Intelligence Platform.

Each repository handles database operations (CRUD) for a specific
data domain, abstracting SQL from the service layer.
"""
from .markets_repository import MarketsRepository
from .commodities_repository import CommoditiesRepository
from .forex_repository import ForexRepository
from .economics_repository import EconomicsRepository
from .weather_repository import WeatherRepository
from .space_repository import SpaceRepository
from .disasters_repository import DisastersRepository
from .news_repository import NewsRepository
from .investor_relations_repository import InvestorRelationsRepository

__all__ = [
    'MarketsRepository',
    'CommoditiesRepository',
    'ForexRepository',
    'EconomicsRepository',
    'WeatherRepository',
    'SpaceRepository',
    'DisastersRepository',
    'NewsRepository',
    'InvestorRelationsRepository',
]
