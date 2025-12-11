"""
Data access layer - Repository pattern for all domains.
"""

from services.data.base_repository import BaseRepository
from repositories.market_repository import MarketRepository

__all__ = [
    'BaseRepository',
    'MarketRepository',
]
