"""
Markets Service
Business logic for fetching and processing market data from Alpha Vantage.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from core.config import Config
from core.exceptions import APIError, ValidationError
from repositories.markets_repository import MarketsRepository

logger = logging.getLogger(__name__)


class MarketsService:
    """Service for market data operations."""
    
    # Default stock symbols to track
    DEFAULT_SYMBOLS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'MA', 'HD', 'DIS',
        'BAC', 'XOM', 'KO', 'PFE', 'CSCO'
    ]
    
    def __init__(self, config: Config, repository: MarketsRepository):
        """
        Initialize the service.
        
        Args:
            config: Configuration instance
            repository: Markets repository instance
        """
        self.config = config
        self.repository = repository
        self.api_key = config.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.max_retries = config.API_MAX_RETRIES
        self.retry_delay = config.API_RETRY_DELAY
        self.timeout = config.API_TIMEOUT
        self.rate_limit_delay = config.ALPHA_VANTAGE_RATE_LIMIT_DELAY
    
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
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
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
    
    def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current quote for a single stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock data or None if failed
        """
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol
            }
            
            data = self._make_api_request(params)
            
            if 'Global Quote' not in data or not data['Global Quote']:
                logger.warning(f"No quote data returned for {symbol}")
                return None
            
            quote = data['Global Quote']
            
            # Parse and validate the data
            stock_data = {
                'symbol': symbol,
                'name': self._get_company_name(symbol),  # We'll fetch this separately
                'price': self._safe_float(quote.get('05. price')),
                'change': self._safe_float(quote.get('09. change')),
                'change_percent': self._safe_float(quote.get('10. change percent', '').rstrip('%')),
                'volume': self._safe_int(quote.get('06. volume')),
                'market_cap': None,  # Will need separate API call or calculation
                'timestamp': datetime.now()
            }
            
            # Validate required fields
            if stock_data['price'] is None:
                raise ValidationError(f"No price data for {symbol}")
            
            logger.debug(f"Successfully fetched quote for {symbol}: ${stock_data['price']}")
            return stock_data
            
        except (APIError, ValidationError) as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching quote for {symbol}: {e}")
            return None
    
    def fetch_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company overview including market cap.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company data or None if failed
        """
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol
            }
            
            data = self._make_api_request(params)
            
            if not data or 'Symbol' not in data:
                logger.warning(f"No overview data returned for {symbol}")
                return None
            
            return {
                'name': data.get('Name'),
                'market_cap': self._safe_int(data.get('MarketCapitalization')),
                'sector': data.get('Sector'),
                'industry': data.get('Industry')
            }
            
        except APIError as e:
            logger.error(f"Error fetching overview for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching overview for {symbol}: {e}")
            return None
    
    def fetch_multiple_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch quotes for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of stock data dictionaries
        """
        results = []
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Fetching quote for {symbol} ({i+1}/{len(symbols)})")
            
            stock_data = self.fetch_quote(symbol)
            if stock_data:
                results.append(stock_data)
            
            # Rate limiting: Alpha Vantage free tier = 5 calls/minute
            if i < len(symbols) - 1:
                time.sleep(self.rate_limit_delay)
        
        return results
    
    def collect_and_store_data(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Collect market data and store in database.
        
        Args:
            symbols: List of stock symbols (uses defaults if None)
            
        Returns:
            Dictionary with collection results
        """
        if symbols is None:
            symbols = self.DEFAULT_SYMBOLS
        
        logger.info(f"Starting market data collection for {len(symbols)} symbols")
        
        start_time = datetime.now()
        successful = 0
        failed = 0
        
        # Fetch quotes for all symbols
        stock_data_list = self.fetch_multiple_quotes(symbols)
        
        # Store in database
        if stock_data_list:
            try:
                inserted = self.repository.insert_bulk_stock_data(stock_data_list)
                successful = inserted
                logger.info(f"Successfully stored {inserted} stock records")
            except Exception as e:
                logger.error(f"Error storing stock data: {e}")
                failed = len(stock_data_list)
        
        failed += len(symbols) - len(stock_data_list)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'total_symbols': len(symbols),
            'successful': successful,
            'failed': failed,
            'duration_seconds': duration,
            'timestamp': end_time
        }
        
        logger.info(f"Market data collection completed: {successful} successful, {failed} failed, {duration:.2f}s")
        
        return results
    
    def get_latest_prices(self) -> List[Dict[str, Any]]:
        """
        Get the latest prices for all tracked stocks from database.
        
        Returns:
            List of stock data dictionaries
        """
        try:
            return self.repository.get_all_latest_stocks()
        except Exception as e:
            logger.error(f"Error getting latest prices: {e}")
            return []
    
    def get_stock_with_history(self, symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get stock data with historical prices.
        
        Args:
            symbol: Stock symbol
            days: Number of days of history
            
        Returns:
            Dictionary with current data and price history
        """
        try:
            latest = self.repository.get_latest_stock_price(symbol)
            if not latest:
                return None
            
            history = self.repository.get_stock_history(symbol, days)
            
            return {
                'current': latest,
                'history': history
            }
        except Exception as e:
            logger.error(f"Error getting stock with history for {symbol}: {e}")
            return None
    
    def get_sparkline_data(self, symbol: str, days: int = 7) -> List[float]:
        """
        Get price history for sparkline visualization.
        
        Args:
            symbol: Stock symbol
            days: Number of days of history
            
        Returns:
            List of prices
        """
        try:
            return self.repository.get_price_history_for_sparkline(symbol, days)
        except Exception as e:
            logger.error(f"Error getting sparkline data for {symbol}: {e}")
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
    
    @staticmethod
    def _safe_int(value: Any) -> Optional[int]:
        """Safely convert value to int."""
        try:
            if value is None or value == '':
                return None
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _get_company_name(symbol: str) -> str:
        """Get company name for symbol (simplified mapping)."""
        # In production, this would come from the OVERVIEW API call
        # For now, use a simplified mapping
        company_names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation',
            'JPM': 'JPMorgan Chase & Co.',
            'V': 'Visa Inc.',
            'JNJ': 'Johnson & Johnson',
            'WMT': 'Walmart Inc.',
            'PG': 'Procter & Gamble Co.',
            'MA': 'Mastercard Inc.',
            'HD': 'Home Depot Inc.',
            'DIS': 'Walt Disney Co.',
            'BAC': 'Bank of America Corp.',
            'XOM': 'Exxon Mobil Corporation',
            'KO': 'Coca-Cola Company',
            'PFE': 'Pfizer Inc.',
            'CSCO': 'Cisco Systems Inc.'
        }
        return company_names.get(symbol, symbol)
