"""
Economics Service
Business logic for fetching economic indicators from FRED API.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from core.config import Config
from core.exceptions import APIError, ValidationError
from repositories.economics_repository import EconomicsRepository

logger = logging.getLogger(__name__)


class EconomicsService:
    """Service for economic indicators operations."""
    
    # Default economic indicators to track (FRED series IDs)
    DEFAULT_INDICATORS = {
        'USA': {
            'GDP': {'series_id': 'GDP', 'name': 'GDP', 'unit': 'Billions USD'},
            'UNEMPLOYMENT': {'series_id': 'UNRATE', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'CPIAUCSL', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INTEREST_RATE': {'series_id': 'FEDFUNDS', 'name': 'Federal Funds Rate', 'unit': '%'},
        }
    }
    
    def __init__(self, config: Config, repository: EconomicsRepository):
        """Initialize the service."""
        self.config = config
        self.repository = repository
        self.api_key = config.FRED_API_KEY if hasattr(config, 'FRED_API_KEY') else None
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.max_retries = 3
        self.retry_delay = 2
    
    def _make_api_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make a request to FRED API with retry logic."""
        if self.api_key:
            params['api_key'] = self.api_key
        params['file_type'] = 'json'
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise APIError(f"Failed to fetch from FRED after {self.max_retries} attempts: {e}")
        
        raise APIError("Unexpected error in API request")
    
    def fetch_indicator(self, series_id: str, country: str, indicator_name: str, unit: str) -> Optional[Dict[str, Any]]:
        """Fetch current value for an economic indicator."""
        try:
            params = {
                'series_id': series_id,
                'limit': 1,
                'sort_order': 'desc'
            }
            
            data = self._make_api_request(params)
            
            if 'observations' not in data or not data['observations']:
                logger.warning(f"No data returned for {series_id}")
                return None
            
            latest = data['observations'][0]
            
            indicator_data = {
                'indicator': series_id,
                'country': country,
                'name': indicator_name,
                'value': self._safe_float(latest.get('value')),
                'unit': unit,
                'timestamp': datetime.now()
            }
            
            if indicator_data['value'] is None:
                raise ValidationError(f"No value for {series_id}")
            
            logger.debug(f"Fetched {series_id}: {indicator_data['value']}")
            return indicator_data
            
        except (APIError, ValidationError) as e:
            logger.error(f"Error fetching indicator {series_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {series_id}: {e}")
            return None
    
    def fetch_multiple_indicators(self, indicators: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Fetch multiple economic indicators."""
        results = []
        
        for country, country_indicators in indicators.items():
            for indicator_key, indicator_info in country_indicators.items():
                series_id = indicator_info['series_id']
                name = indicator_info['name']
                unit = indicator_info['unit']
                
                logger.info(f"Fetching {name} for {country}")
                
                data = self.fetch_indicator(series_id, country, name, unit)
                if data:
                    results.append(data)
                
                time.sleep(1)  # Rate limiting
        
        return results
    
    def collect_and_store_data(self, indicators: Optional[Dict] = None) -> Dict[str, Any]:
        """Collect economic data and store in database."""
        if indicators is None:
            indicators = self.DEFAULT_INDICATORS
        
        logger.info("Starting economic data collection")
        
        start_time = datetime.now()
        
        # Fetch indicators
        indicator_data_list = self.fetch_multiple_indicators(indicators)
        
        successful = 0
        failed = 0
        
        # Store in database
        if indicator_data_list:
            try:
                inserted = self.repository.insert_bulk_indicator_data(indicator_data_list)
                successful = inserted
            except Exception as e:
                logger.error(f"Error storing economic data: {e}")
                failed = len(indicator_data_list)
        
        # Calculate total expected
        total_expected = sum(len(country_indicators) for country_indicators in indicators.values())
        failed += total_expected - len(indicator_data_list)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'total_indicators': total_expected,
            'successful': successful,
            'failed': failed,
            'duration_seconds': duration,
            'timestamp': end_time
        }
        
        logger.info(f"Economic data collection completed: {successful} successful, {failed} failed")
        
        return results
    
    def get_latest_indicators(self) -> List[Dict[str, Any]]:
        """Get the latest economic indicators from database."""
        try:
            return self.repository.get_all_latest_indicators()
        except Exception as e:
            logger.error(f"Error getting latest indicators: {e}")
            return []
    
    @staticmethod
    def _safe_float(value: Any) -> Optional[float]:
        """Safely convert value to float."""
        try:
            if value is None or value == '' or value == '.':
                return None
            return float(value)
        except (ValueError, TypeError):
            return None
