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
    # FRED has international data series for major economies
    DEFAULT_INDICATORS = {
        'USA': {
            'GDP': {'series_id': 'GDP', 'name': 'GDP', 'unit': 'Billions USD'},
            'UNEMPLOYMENT': {'series_id': 'UNRATE', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'CPIAUCSL', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INTEREST_RATE': {'series_id': 'FEDFUNDS', 'name': 'Federal Funds Rate', 'unit': '%'},
            'PMI_MANUFACTURING': {'series_id': 'MANEMP', 'name': 'Manufacturing Employment', 'unit': 'Thousands'},
            'CONSUMER_CONFIDENCE': {'series_id': 'UMCSENT', 'name': 'Consumer Sentiment', 'unit': 'Index'},
            'RETAIL_SALES': {'series_id': 'RSXFS', 'name': 'Retail Sales', 'unit': 'Millions USD'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'INDPRO', 'name': 'Industrial Production', 'unit': 'Index'},
            # Treasury Yields
            'TREASURY_3M': {'series_id': 'DGS3MO', 'name': '3-Month Treasury', 'unit': '%'},
            'TREASURY_2Y': {'series_id': 'DGS2', 'name': '2-Year Treasury', 'unit': '%'},
            'TREASURY_5Y': {'series_id': 'DGS5', 'name': '5-Year Treasury', 'unit': '%'},
            'TREASURY_10Y': {'series_id': 'DGS10', 'name': '10-Year Treasury', 'unit': '%'},
            'TREASURY_30Y': {'series_id': 'DGS30', 'name': '30-Year Treasury', 'unit': '%'},
            # Yield Curve Spread (10Y - 2Y, recession indicator)
            'YIELD_CURVE_10Y2Y': {'series_id': 'T10Y2Y', 'name': '10Y-2Y Yield Spread', 'unit': '%'},
            # VIX Volatility Index
            'VIX': {'series_id': 'VIXCLS', 'name': 'VIX Volatility Index', 'unit': 'Index'},
        },
        'EU': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQEA19', 'name': 'GDP', 'unit': 'Millions EUR'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTEZM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'EA19CPALTT01GYM', 'name': 'CPI Inflation', 'unit': '% Change'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03EZM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'EA19PRINTO01GYSAM', 'name': 'Industrial Production', 'unit': '% Change'},
        },
        'UK': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQUK', 'name': 'GDP', 'unit': 'Millions GBP'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTGBM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'GBRCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03GBM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'RETAIL_SALES': {'series_id': 'SLRTTO02GBM659S', 'name': 'Retail Sales', 'unit': '% Change'},
        },
        'Germany': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQDE', 'name': 'GDP', 'unit': 'Millions EUR'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTDEM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'DEUCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03DEM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'DEUPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
            'RETAIL_SALES': {'series_id': 'SLRTTO02DEM659S', 'name': 'Retail Sales', 'unit': '% Change'},
        },
        'France': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQFR', 'name': 'GDP', 'unit': 'Millions EUR'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTFRM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'FRACPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03FRM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'FRAPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Japan': {
            'GDP': {'series_id': 'JPNRGDPEXP', 'name': 'GDP', 'unit': 'Billions JPY'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTJPM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'JPNCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03JPM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'JPNPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'China': {
            'GDP': {'series_id': 'MKTGDPCNA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'INFLATION': {'series_id': 'CHNCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'CHNPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Canada': {
            'GDP': {'series_id': 'NGDPRSAXDCCAQ', 'name': 'GDP', 'unit': 'Millions CAD'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTCAM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'CANCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03CAM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'RETAIL_SALES': {'series_id': 'SLRTTO02CAM659S', 'name': 'Retail Sales', 'unit': '% Change'},
        },
        'Australia': {
            'GDP': {'series_id': 'AUSGDPDEFQISMEI', 'name': 'GDP Deflator', 'unit': 'Index'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTAUM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'AUSCPIALLQINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03AUM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'RETAIL_SALES': {'series_id': 'SLRTTO02AUM659S', 'name': 'Retail Sales', 'unit': '% Change'},
        },
        'India': {
            'GDP': {'series_id': 'MKTGDPINA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'INFLATION': {'series_id': 'INDCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'INDPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Brazil': {
            'GDP': {'series_id': 'MKTGDPBRA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTBRM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'BRACPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'BRAPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'South Korea': {
            'GDP': {'series_id': 'KORRGDPEXP', 'name': 'GDP', 'unit': 'Billions KRW'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTKOM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'KORCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03KRM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'KORPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Mexico': {
            'GDP': {'series_id': 'MKTGDPMXA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTMXM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'MEXCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'MEXPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Italy': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQIT', 'name': 'GDP', 'unit': 'Millions EUR'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTITM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'ITACPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03ITM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'ITAPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Spain': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQES', 'name': 'GDP', 'unit': 'Millions EUR'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTESM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'ESPCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'ESPPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Netherlands': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQNL', 'name': 'GDP', 'unit': 'Millions EUR'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTNLM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'NLDCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03NLM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
        },
        'Switzerland': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQCH', 'name': 'GDP', 'unit': 'Millions CHF'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTCHM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'CHECPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03CHM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
        },
        'Sweden': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQSE', 'name': 'GDP', 'unit': 'Millions SEK'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTSEM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'SWECPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'CONSUMER_CONFIDENCE': {'series_id': 'CSCICP03SEM665S', 'name': 'Consumer Confidence', 'unit': 'Index'},
        },
        'Poland': {
            'GDP': {'series_id': 'CLVMNACSCAB1GQPL', 'name': 'GDP', 'unit': 'Millions PLN'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTPLM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'POLCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'POLPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Turkey': {
            'GDP': {'series_id': 'MKTGDPTRA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTTRM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'TURCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'TURPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Indonesia': {
            'GDP': {'series_id': 'MKTGDPIDA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'INFLATION': {'series_id': 'IDNCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'IDNPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'South Africa': {
            'GDP': {'series_id': 'MKTGDPZAA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'UNEMPLOYMENT': {'series_id': 'LRHUTTTTZAM156S', 'name': 'Unemployment Rate', 'unit': '%'},
            'INFLATION': {'series_id': 'ZAFCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'ZAFPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
        'Russia': {
            'GDP': {'series_id': 'MKTGDPRUA646NWDB', 'name': 'GDP', 'unit': 'USD'},
            'INFLATION': {'series_id': 'RUSCPIALLMINMEI', 'name': 'CPI Inflation', 'unit': 'Index'},
            'INDUSTRIAL_PRODUCTION': {'series_id': 'RUSPROINDMISMEI', 'name': 'Industrial Production', 'unit': 'Index'},
        },
    }
    
    def __init__(self, config: Config, repository: EconomicsRepository):
        """Initialize the service."""
        self.config = config
        self.repository = repository
        self.api_key = config.FRED_API_KEY if hasattr(config, 'FRED_API_KEY') else None
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.max_retries = config.API_MAX_RETRIES
        self.retry_delay = config.API_RETRY_DELAY
        self.timeout = config.API_TIMEOUT
        self.rate_limit_delay = config.DEFAULT_RATE_LIMIT_DELAY
    
    def _make_api_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Make a request to FRED API with retry logic."""
        if self.api_key:
            params['api_key'] = self.api_key
        params['file_type'] = 'json'
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
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
                
                time.sleep(self.rate_limit_delay)  # Rate limiting
        
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
