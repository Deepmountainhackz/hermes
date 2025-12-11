"""
Commodities Service
Business logic for fetching and processing commodities data from Alpha Vantage.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from core.config import Config
from core.exceptions import APIError, ValidationError
from repositories.commodities_repository import CommoditiesRepository

logger = logging.getLogger(__name__)


class CommoditiesService:
    """Service for commodities data operations."""
    
    # Default commodities to track with their Alpha Vantage symbols
    DEFAULT_COMMODITIES = {
        'WTI': {'name': 'WTI Crude Oil', 'unit': 'USD/barrel'},
        'BRENT': {'name': 'Brent Crude Oil', 'unit': 'USD/barrel'},
        'NATURAL_GAS': {'name': 'Natural Gas', 'unit': 'USD/MMBtu'},
        'COPPER': {'name': 'Copper', 'unit': 'USD/pound'},
        'WHEAT': {'name': 'Wheat', 'unit': 'USD/bushel'},
        'CORN': {'name': 'Corn', 'unit': 'USD/bushel'},
    }
    
    def __init__(self, config: Config, repository: CommoditiesRepository):
        """
        Initialize the service.
        
        Args:
            config: Configuration instance
            repository: Commodities repository instance
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
    
    def fetch_commodity_price(self, commodity_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current price for a single commodity.
        
        Args:
            commodity_symbol: Commodity symbol (e.g., 'WTI', 'BRENT')
            
        Returns:
            Dictionary with commodity data or None if failed
        """
        try:
            # Alpha Vantage uses different function names for different commodities
            params = {
                'function': self._get_function_for_commodity(commodity_symbol),
                'interval': 'daily'
            }
            
            data = self._make_api_request(params)
            
            # Parse the response based on commodity type
            commodity_data = self._parse_commodity_response(commodity_symbol, data)
            
            if not commodity_data:
                logger.warning(f"No commodity data returned for {commodity_symbol}")
                return None
            
            # Validate required fields
            if commodity_data['price'] is None:
                raise ValidationError(f"No price data for {commodity_symbol}")
            
            logger.debug(f"Successfully fetched price for {commodity_symbol}: ${commodity_data['price']}")
            return commodity_data
            
        except (APIError, ValidationError) as e:
            logger.error(f"Error fetching commodity price for {commodity_symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching commodity price for {commodity_symbol}: {e}")
            return None
    
    def _get_function_for_commodity(self, commodity_symbol: str) -> str:
        """Get the appropriate Alpha Vantage function for a commodity."""
        # Alpha Vantage commodity functions
        function_map = {
            'WTI': 'WTI',
            'BRENT': 'BRENT',
            'NATURAL_GAS': 'NATURAL_GAS',
            'COPPER': 'COPPER',
            'WHEAT': 'WHEAT',
            'CORN': 'CORN',
        }
        return function_map.get(commodity_symbol, 'WTI')
    
    def _parse_commodity_response(self, commodity_symbol: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Alpha Vantage commodity response.
        
        Args:
            commodity_symbol: Commodity symbol
            data: API response data
            
        Returns:
            Parsed commodity data or None
        """
        try:
            # Alpha Vantage returns data in 'data' key for commodities
            if 'data' not in data or not data['data']:
                return None
            
            # Get the latest data point
            latest = data['data'][0] if isinstance(data['data'], list) else data['data']
            
            # Get commodity metadata
            commodity_info = self.DEFAULT_COMMODITIES.get(commodity_symbol, {
                'name': commodity_symbol,
                'unit': 'USD'
            })
            
            commodity_data = {
                'commodity': commodity_symbol,
                'name': commodity_info['name'],
                'price': self._safe_float(latest.get('value')),
                'change': None,  # Calculate if previous data available
                'change_percent': None,  # Calculate if previous data available
                'unit': commodity_info['unit'],
                'timestamp': datetime.now()
            }
            
            return commodity_data
            
        except Exception as e:
            logger.error(f"Error parsing commodity response for {commodity_symbol}: {e}")
            return None
    
    def fetch_multiple_commodities(self, commodities: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch prices for multiple commodities.
        
        Args:
            commodities: List of commodity symbols
            
        Returns:
            List of commodity data dictionaries
        """
        results = []
        
        for i, commodity in enumerate(commodities):
            logger.info(f"Fetching price for {commodity} ({i+1}/{len(commodities)})")
            
            commodity_data = self.fetch_commodity_price(commodity)
            if commodity_data:
                results.append(commodity_data)
            
            # Rate limiting: Alpha Vantage free tier = 5 calls/minute
            if i < len(commodities) - 1:
                time.sleep(self.rate_limit_delay)
        
        return results
    
    def collect_and_store_data(self, commodities: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Collect commodities data and store in database.
        
        Args:
            commodities: List of commodity symbols (uses defaults if None)
            
        Returns:
            Dictionary with collection results
        """
        if commodities is None:
            commodities = list(self.DEFAULT_COMMODITIES.keys())
        
        logger.info(f"Starting commodities data collection for {len(commodities)} commodities")
        
        start_time = datetime.now()
        successful = 0
        failed = 0
        
        # Fetch prices for all commodities
        commodity_data_list = self.fetch_multiple_commodities(commodities)
        
        # Store in database
        if commodity_data_list:
            try:
                inserted = self.repository.insert_bulk_commodity_data(commodity_data_list)
                successful = inserted
                logger.info(f"Successfully stored {inserted} commodity records")
            except Exception as e:
                logger.error(f"Error storing commodity data: {e}")
                failed = len(commodity_data_list)
        
        failed += len(commodities) - len(commodity_data_list)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'total_commodities': len(commodities),
            'successful': successful,
            'failed': failed,
            'duration_seconds': duration,
            'timestamp': end_time
        }
        
        logger.info(f"Commodities data collection completed: {successful} successful, {failed} failed, {duration:.2f}s")
        
        return results
    
    def get_latest_prices(self) -> List[Dict[str, Any]]:
        """
        Get the latest prices for all tracked commodities from database.
        
        Returns:
            List of commodity data dictionaries
        """
        try:
            return self.repository.get_all_latest_commodities()
        except Exception as e:
            logger.error(f"Error getting latest commodity prices: {e}")
            return []
    
    def get_commodity_with_history(self, commodity: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get commodity data with historical prices.
        
        Args:
            commodity: Commodity symbol
            days: Number of days of history
            
        Returns:
            Dictionary with current data and price history
        """
        try:
            latest = self.repository.get_latest_commodity_price(commodity)
            if not latest:
                return None
            
            history = self.repository.get_commodity_history(commodity, days)
            
            return {
                'current': latest,
                'history': history
            }
        except Exception as e:
            logger.error(f"Error getting commodity with history for {commodity}: {e}")
            return None
    
    def get_sparkline_data(self, commodity: str, days: int = 7) -> List[float]:
        """
        Get price history for sparkline visualization.
        
        Args:
            commodity: Commodity symbol
            days: Number of days of history
            
        Returns:
            List of prices
        """
        try:
            return self.repository.get_price_history_for_sparkline(commodity, days)
        except Exception as e:
            logger.error(f"Error getting sparkline data for {commodity}: {e}")
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
