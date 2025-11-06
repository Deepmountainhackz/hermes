"""
Economic Indicators Data Collector
Fetches key economic indicators from FRED (Federal Reserve Economic Data)
"""

import requests
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for database import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EconomicDataCollector:
    """Collector for economic indicators from FRED"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("FRED_API_KEY not found in environment!")
        
        # Key economic indicators by country
        self.indicators = {
            'United States': {
                'GDP': {'series_id': 'GDP', 'name': 'GDP', 'unit': 'Billions of USD'},
                'Unemployment': {'series_id': 'UNRATE', 'name': 'Unemployment Rate', 'unit': 'Percent'},
                'Inflation': {'series_id': 'CPIAUCSL', 'name': 'CPI', 'unit': 'Index'},
                'Interest Rate': {'series_id': 'FEDFUNDS', 'name': 'Federal Funds Rate', 'unit': 'Percent'}
            },
            'Eurozone': {
                'GDP': {'series_id': 'CLVMNACSCAB1GQEU272020', 'name': 'GDP', 'unit': 'Billions of EUR'},
                'Unemployment': {'series_id': 'LRHUTTTTEZM156S', 'name': 'Unemployment Rate', 'unit': 'Percent'},
                'Inflation': {'series_id': 'CP0000EZ19M086NEST', 'name': 'HICP', 'unit': 'Index'}
            },
            'China': {
                'GDP': {'series_id': 'MKTGDPCNA646NWDB', 'name': 'GDP', 'unit': 'Billions of USD'},
                'Unemployment': {'series_id': 'CHNUEMPALLPERSONS', 'name': 'Unemployment Rate', 'unit': 'Millions'}  # Changed
            },
            'Japan': {
                'GDP': {'series_id': 'JPNRGDPEXP', 'name': 'GDP', 'unit': 'Billions of USD'},
                'Unemployment': {'series_id': 'LRHUTTTTJPM156S', 'name': 'Unemployment Rate', 'unit': 'Percent'},
                'Inflation': {'series_id': 'FPCPITOTLZGJPN', 'name': 'CPI', 'unit': 'Percent'}  # Changed to YoY%
            },
            'United Kingdom': {
                'GDP': {'series_id': 'MKTGDPGBA646NWDB', 'name': 'GDP', 'unit': 'Billions of USD'},  # Changed
                'Unemployment': {'series_id': 'LRHUTTTTGBM156S', 'name': 'Unemployment Rate', 'unit': 'Percent'},
                'Inflation': {'series_id': 'GBRCPIALLMINMEI', 'name': 'CPI', 'unit': 'Index'}
            }
        }
    
    def fetch_indicator(self, series_id: str, limit: int = 1) -> Optional[Dict[str, Any]]:
        """
        Fetch latest data for an economic indicator
        
        Args:
            series_id: FRED series ID
            limit: Number of most recent observations (default: 1)
            
        Returns:
            Dictionary containing indicator data or None if failed
        """
        if not self.api_key:
            logger.error("FRED API key not provided")
            return None
        
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'sort_order': 'desc',  # Most recent first
            'limit': limit
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {series_id} (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for errors
                if 'error_message' in data:
                    logger.error(f"API Error for {series_id}: {data['error_message']}")
                    return None
                
                observations = data.get('observations', [])
                if not observations:
                    logger.warning(f"No data for {series_id}")
                    return None
                
                logger.info(f"✓ Successfully fetched {series_id}")
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {series_id}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {series_id}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error for {series_id}: {e}", exc_info=True)
                return None
        
        logger.error(f"All retry attempts failed for {series_id}")
        return None
    
    def save_to_database(self, country: str, indicator_type: str, indicator_name: str, 
                        data: Dict[str, Any], unit: str) -> bool:
        """
        Save economic indicator to PostgreSQL database
        
        Args:
            country: Country name
            indicator_type: Type of indicator (GDP, Unemployment, etc.)
            indicator_name: Name of indicator
            data: Data from FRED
            unit: Unit of measurement
            
        Returns:
            True if successful, False otherwise
        """
        try:
            observations = data.get('observations', [])
            if not observations:
                return False
            
            # Get most recent observation
            latest = observations[0]
            
            # Parse data
            date_str = latest.get('date', '')
            value_str = latest.get('value', '.')
            
            # Skip if value is missing
            if value_str == '.':
                logger.warning(f"Missing value for {country} {indicator_type}")
                return False
            
            timestamp = datetime.strptime(date_str, '%Y-%m-%d')
            value = float(value_str)
            
            series_id = latest.get('series_id', '')
            
            indicator_record = {
                'country': country,
                'indicator_type': indicator_type,
                'indicator_name': indicator_name,
                'series_id': series_id,
                'timestamp': timestamp,
                'value': value,
                'unit': unit
            }
            
            # Insert into database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO economic_indicators 
                        (country, indicator_type, indicator_name, series_id, timestamp, value, unit)
                        VALUES (%(country)s, %(indicator_type)s, %(indicator_name)s, %(series_id)s,
                                %(timestamp)s, %(value)s, %(unit)s)
                        ON CONFLICT (series_id, timestamp) 
                        DO UPDATE SET
                            value = EXCLUDED.value,
                            collected_at = CURRENT_TIMESTAMP
                    """, indicator_record)
            
            logger.info(f"✓ Saved {country} {indicator_type}: {value} {unit} ({date_str})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {country} {indicator_type}: {e}")
            return False
    
    def collect_all_indicators(self) -> Dict[str, Any]:
        """
        Collect all economic indicators
        
        Returns:
            Dictionary with collection results
        """
        results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'indicators': [],
            'errors': []
        }
        
        for country, indicators in self.indicators.items():
            for indicator_type, details in indicators.items():
                results['total'] += 1
                
                # Small delay between requests
                time.sleep(0.5)
                
                series_id = details['series_id']
                indicator_name = details['name']
                unit = details['unit']
                
                data = self.fetch_indicator(series_id)
                
                if data:
                    if self.save_to_database(country, indicator_type, indicator_name, data, unit):
                        results['successful'] += 1
                        
                        # Extract value for display
                        observations = data.get('observations', [])
                        if observations:
                            latest = observations[0]
                            value = latest.get('value', '.')
                            date = latest.get('date', '')
                            
                            if value != '.':
                                results['indicators'].append({
                                    'country': country,
                                    'indicator': indicator_type,
                                    'value': float(value),
                                    'unit': unit,
                                    'date': date
                                })
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"{country} {indicator_type}: Failed to save")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{country} {indicator_type}: Failed to fetch")
        
        return results

def main():
    """Main execution function"""
    logger.info("=== Economic Indicators Data Collection ===\n")
    
    collector = EconomicDataCollector()
    
    if not collector.api_key:
        print("❌ FRED_API_KEY not found!")
        print("Please add FRED_API_KEY to your .env file")
        print("Get your key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        return
    
    logger.info("Collecting economic indicators for major economies")
    results = collector.collect_all_indicators()
    
    # Print results
    print(f"\n=== Collection Complete ===")
    print(f"Total indicators: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if results['indicators']:
        print(f"\n📊 Latest Economic Indicators:\n")
        
        # Group by country
        by_country = {}
        for ind in results['indicators']:
            country = ind['country']
            if country not in by_country:
                by_country[country] = []
            by_country[country].append(ind)
        
        for country, indicators in by_country.items():
            print(f"  {country}:")
            for ind in indicators:
                value = ind['value']
                unit = ind['unit']
                indicator = ind['indicator']
                
                # Format differently based on indicator type
                if 'Percent' in unit:
                    print(f"    {indicator}: {value:.1f}%")
                elif 'Billions' in unit:
                    print(f"    {indicator}: ${value:,.0f}B")
                elif 'Index' in unit:
                    print(f"    {indicator}: {value:.1f}")
                else:
                    print(f"    {indicator}: {value}")
            print()
    
    if results['errors']:
        print(f"❌ Errors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return results

if __name__ == "__main__":
    main()
