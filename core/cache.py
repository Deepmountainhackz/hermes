"""
Enhanced Caching Module for Hermes Intelligence Platform
Provides in-memory caching with TTL, statistics, and selective invalidation.
"""
import streamlit as st
from typing import Callable, Any, Optional, Dict
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import logging
import threading

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a single cache entry with metadata."""

    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
        self.hits = 0
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    def access(self) -> Any:
        self.hits += 1
        return self.value


class InMemoryCache:
    """Thread-safe in-memory cache with TTL and statistics."""

    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key from function arguments."""
        key_data = {
            'prefix': prefix,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired."""
        with self._lock:
            self._stats['total_requests'] += 1

            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    self._stats['hits'] += 1
                    return entry.access()
                else:
                    # Entry expired, remove it
                    del self._cache[key]
                    self._stats['evictions'] += 1

            self._stats['misses'] += 1
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL."""
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)

    def delete(self, key: str) -> bool:
        """Delete a specific cache entry."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all cache entries. Returns count of cleared entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")
            return count

    def clear_prefix(self, prefix: str) -> int:
        """Clear all entries with keys starting with prefix."""
        with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
            logger.info(f"Cache cleared for prefix '{prefix}': {len(keys_to_delete)} entries")
            return len(keys_to_delete)

    def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
                self._stats['evictions'] += 1
            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            hit_rate = (
                self._stats['hits'] / self._stats['total_requests'] * 100
                if self._stats['total_requests'] > 0 else 0
            )
            return {
                'entries': len(self._cache),
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'evictions': self._stats['evictions'],
                'total_requests': self._stats['total_requests'],
                'hit_rate_percent': round(hit_rate, 2)
            }

    def get_entry_info(self) -> list:
        """Get information about all cache entries."""
        with self._lock:
            entries = []
            for key, entry in self._cache.items():
                entries.append({
                    'key': key[:16] + '...' if len(key) > 16 else key,
                    'created': entry.created_at.strftime('%H:%M:%S'),
                    'expires': entry.expires_at.strftime('%H:%M:%S'),
                    'hits': entry.hits,
                    'expired': entry.is_expired(),
                    'ttl': entry.ttl_seconds
                })
            return entries


# Global cache instance
_cache = InMemoryCache()


def get_cache() -> InMemoryCache:
    """Get the global cache instance."""
    return _cache


def cached(ttl_seconds: int = 300, prefix: str = ""):
    """
    Decorator for caching function results.

    Args:
        ttl_seconds: Time-to-live in seconds (default 5 minutes)
        prefix: Optional prefix for cache key organization
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = prefix + cache._generate_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result

        return wrapper
    return decorator


# Streamlit-specific caching wrappers
def cache_data(ttl: int = 300, show_spinner: bool = True):
    """Streamlit cache_data decorator wrapper."""
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
    return decorator


def cache_resource(show_spinner: bool = False):
    """Streamlit cache_resource decorator wrapper."""
    def decorator(func: Callable) -> Callable:
        return st.cache_resource(show_spinner=show_spinner)(func)
    return decorator


def clear_all_caches():
    """Clear both Streamlit and in-memory caches."""
    st.cache_data.clear()
    st.cache_resource.clear()
    _cache.clear()
    logger.info("All caches cleared (Streamlit + in-memory)")


# Cache TTL presets for different data types
class CacheTTL:
    """Standard TTL values for different data types."""
    REALTIME = 30          # 30 seconds - for frequently updating data
    SHORT = 60             # 1 minute - for market data
    MEDIUM = 300           # 5 minutes - for general API data
    LONG = 900             # 15 minutes - for less frequent updates
    HOURLY = 3600          # 1 hour - for relatively static data
    DAILY = 86400          # 24 hours - for reference data

    # Data-specific presets
    STOCK_PRICE = 60       # Stock prices
    CRYPTO_PRICE = 30      # Crypto prices (more volatile)
    FOREX_RATE = 60        # Forex rates
    WEATHER = 1800         # Weather data (30 min)
    NEWS = 900             # News articles (15 min)
    ECONOMIC = 3600        # Economic indicators (1 hour)
    REFERENCE = 86400      # Reference data (country info, etc.)
