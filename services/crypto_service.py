"""
Crypto Service - CoinGecko API integration for cryptocurrency prices.
Free API, no key required.
"""
import requests
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.config import Config
from core.exceptions import APIError

logger = logging.getLogger(__name__)


class CryptoService:
    """Service for cryptocurrency data operations."""

    # Top cryptocurrencies to track
    DEFAULT_CRYPTOS = [
        'bitcoin', 'ethereum', 'tether', 'binancecoin', 'solana',
        'ripple', 'cardano', 'dogecoin', 'polkadot', 'avalanche-2',
        'chainlink', 'polygon', 'litecoin', 'uniswap', 'stellar'
    ]

    def __init__(self, config: Config, repository):
        self.config = config
        self.repository = repository
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = getattr(config, 'API_TIMEOUT', 15)
        self.rate_limit_delay = 2  # CoinGecko rate limit: ~10-30 calls/min

    def fetch_prices(self, crypto_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch current prices for cryptocurrencies."""
        if crypto_ids is None:
            crypto_ids = self.DEFAULT_CRYPTOS

        try:
            # CoinGecko allows fetching multiple coins at once
            ids_param = ','.join(crypto_ids)
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': ids_param,
                'order': 'market_cap_desc',
                'per_page': len(crypto_ids),
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            results = []
            for coin in data:
                results.append({
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'price': coin.get('current_price'),
                    'change_24h': coin.get('price_change_24h'),
                    'change_percent_24h': coin.get('price_change_percentage_24h'),
                    'market_cap': coin.get('market_cap'),
                    'volume_24h': coin.get('total_volume'),
                    'timestamp': datetime.now()
                })

            logger.info(f"Fetched prices for {len(results)} cryptocurrencies")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching crypto prices: {e}")
            return []

    def collect_and_store_data(self, crypto_ids: List[str] = None) -> Dict[str, Any]:
        """Collect crypto data and store in database."""
        logger.info("Starting crypto data collection")

        start_time = datetime.now()

        # Fetch prices
        crypto_data = self.fetch_prices(crypto_ids)

        successful = 0
        if crypto_data:
            try:
                successful = self.repository.insert_bulk_crypto_data(crypto_data)
            except Exception as e:
                logger.error(f"Error storing crypto data: {e}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            'total_cryptos': len(self.DEFAULT_CRYPTOS),
            'successful': successful,
            'failed': len(self.DEFAULT_CRYPTOS) - successful,
            'duration_seconds': duration,
            'timestamp': end_time
        }

    def get_latest_prices(self) -> List[Dict[str, Any]]:
        """Get latest crypto prices from database."""
        try:
            return self.repository.get_all_latest_crypto()
        except Exception as e:
            logger.error(f"Error getting latest crypto prices: {e}")
            return []
