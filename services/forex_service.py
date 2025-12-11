"""
Forex Service
Business logic for fetching and processing forex data from Alpha Vantage.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from core.config import Config
from core.exceptions import APIError, ValidationError
from repositories.forex_repository import ForexRepository

logger = logging.getLogger(__name__)


class ForexService:
    """Service for forex data operations."""
    
    # Default currency pairs to track
    DEFAULT_PAIRS = [
        {'from': 'EUR', 'to': 'USD'},
        {'from': 'GBP', 'to': 'USD'},
        {'from': 'USD', 'to': 'JPY'},
        {'from': 'USD', 'to': 'CHF'},
        {'from': 'AUD', 'to': 'USD'},
        {'from': 'USD', 'to': 'CAD'},
        {'from': 'USD', 'to': 'CNY'},
    ]
    
    def __init__(self, config: Config, repository: ForexRepository):
        """
        Initialize the service.
        
        Args:
            config: Configuration instance
            repository: Forex repository instance
        """
        self.config = config
        self.repository = repository
        self.api_key = config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _make_api_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make a request to Alpha Vantage API with retry logic.
        
        Args:
            params: API request parameters
            
        Returns:
            JSON response from API
            
        Raises:
            APIError: If request fails after retries
        """
        params['apikey'] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                # Check for API error messages
                if 'Error Message' in data:
                    raise APIError(f"Alpha Vantage API error: {data['Error Message']}")
                
                if 'Note' in data:
                    # Rate limit hit
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Rate limit hit, retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise APIError("Alpha Vantage rate limit exceeded")
                
                return data
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise APIError(f"Failed to fetch data from Alpha Vantage after {self.max_retries} attempts: {e}")
        
        raise APIError("Unexpected error in API request")
    
    def fetch_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current exchange rate for a currency pair.
        
        Args:
            from_currency: Source currency code (e.g., 'EUR')
            to_currency: Target currency code (e.g., 'USD')
            
        Returns:
            Dictionary with forex data or None if failed
        """
        try:
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': from_currency,
                'to_currency': to_currency
            }
            
            data = self._make_api_request(params)
            
            if 'Realtime Currency Exchange Rate' not in data:
                logger.warning(f"No exchange rate data returned for {from_currency}/{to_currency}")
                return None
            
            rate_data = data['Realtime Currency Exchange Rate']
            
            pair = f"{from_currency}/{to_currency}"
            
            forex_data = {
                'pair': pair,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': self._safe_float(rate_data.get('5. Exchange Rate')),
                'bid': self._safe_float(rate_data.get('8. Bid Price')),
                'ask': self._safe_float(rate_data.get('9. Ask Price')),
                'timestamp': datetime.now()
            }
            
            # Validate required fields
            if forex_data['rate'] is None:
                raise ValidationError(f"No rate data for {pair}")
            
            logger.debug(f"Successfully fetched exchange rate for {pair}: {forex_data['rate']}")
            return forex_data
            
        except (APIError, ValidationError) as e:
            logger.error(f"Error fetching exchange rate for {from_currency}/{to_currency}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rate for {from_currency}/{to_currency}: {e}")
            return None
    
    def fetch_multiple_exchange_rates(self, currency_pairs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Fetch exchange rates for multiple currency pairs.
        
        Args:
            currency_pairs: List of dicts with 'from' and 'to' keys
            
        Returns:
            List of forex data dictionaries
        """
        results = []
        
        for i, pair in enumerate(currency_pairs):
            from_currency = pair['from']
            to_currency = pair['to']
            pair_str = f"{from_currency}/{to_currency}"
            
            logger.info(f"Fetching exchange rate for {pair_str} ({i+1}/{len(currency_pairs)})")
            
            forex_data = self.fetch_exchange_rate(from_currency, to_currency)
            if forex_data:
                results.append(forex_data)
            
            # Rate limiting: Alpha Vantage free tier = 5 calls/minute
            # Wait 12 seconds between calls to stay under limit
            if i < len(currency_pairs) - 1:
                time.sleep(12)
        
        return results
    
    def collect_and_store_data(self, currency_pairs: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Collect forex data and store in database.
        
        Args:
            currency_pairs: List of currency pair dicts (uses defaults if None)
            
        Returns:
            Dictionary with collection results
        """
        if currency_pairs is None:
            currency_pairs = self.DEFAULT_PAIRS
        
        logger.info(f"Starting forex data collection for {len(currency_pairs)} currency pairs")
        
        start_time = datetime.now()
        successful = 0
        failed = 0
        
        # Fetch exchange rates for all pairs
        forex_data_list = self.fetch_multiple_exchange_rates(currency_pairs)
        
        # Store in database
        if forex_data_list:
            try:
                inserted = self.repository.insert_bulk_forex_data(forex_data_list)
                successful = inserted
                logger.info(f"Successfully stored {inserted} forex records")
            except Exception as e:
                logger.error(f"Error storing forex data: {e}")
                failed = len(forex_data_list)
        
        failed += len(currency_pairs) - len(forex_data_list)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'total_pairs': len(currency_pairs),
            'successful': successful,
            'failed': failed,
            'duration_seconds': duration,
            'timestamp': end_time
        }
        
        logger.info(f"Forex data collection completed: {successful} successful, {failed} failed, {duration:.2f}s")
        
        return results
    
    def get_latest_rates(self) -> List[Dict[str, Any]]:
        """
        Get the latest exchange rates for all tracked currency pairs from database.
        
        Returns:
            List of forex data dictionaries
        """
        try:
            return self.repository.get_all_latest_forex_rates()
        except Exception as e:
            logger.error(f"Error getting latest forex rates: {e}")
            return []
    
    def get_forex_with_history(self, pair: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get forex data with historical rates.
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            days: Number of days of history
            
        Returns:
            Dictionary with current data and rate history
        """
        try:
            latest = self.repository.get_latest_forex_rate(pair)
            if not latest:
                return None
            
            history = self.repository.get_forex_history(pair, days)
            
            return {
                'current': latest,
                'history': history
            }
        except Exception as e:
            logger.error(f"Error getting forex with history for {pair}: {e}")
            return None
    
    def get_sparkline_data(self, pair: str, days: int = 7) -> List[float]:
        """
        Get rate history for sparkline visualization.
        
        Args:
            pair: Currency pair
            days: Number of days of history
            
        Returns:
            List of rates
        """
        try:
            return self.repository.get_rate_history_for_sparkline(pair, days)
        except Exception as e:
            logger.error(f"Error getting sparkline data for {pair}: {e}")
            return []
    
    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """Safely convert value to float."""
        try:
            if value is None or value == '':
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
