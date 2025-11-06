"""
Commodity Data Collector
Fetches commodity prices from Alpha Vantage and saves to PostgreSQL
"""

import requests
import logging
import os
import sys
from datetime import datetime
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

class CommodityDataCollector:
    """Collector for commodity price data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("ALPHA_VANTAGE_KEY not found in environment!")
        
    def fetch_commodity(self, symbol: str, interval: str = "daily") -> Optional[Dict[str, Any]]:
        """
        Fetch commodity price data
        
        Args:
            symbol: Commodity symbol (e.g., 'WTI', 'BRENT', 'NATURAL_GAS')
            interval: Time interval (daily, weekly, monthly)
            
        Returns:
            Dictionary containing commodity data or None if failed
        """
        if not self.api_key:
            logger.error("Alpha Vantage API key not provided")
            return None
        
        # Map commodity symbols to Alpha Vantage functions
        commodity_functions = {
            'WTI': 'WTI',           # Crude Oil
            'BRENT': 'BRENT',       # Brent Crude
            'NATURAL_GAS': 'NATURAL_GAS',
            'COPPER': 'COPPER',
            'ALUMINUM': 'ALUMINUM',
            'WHEAT': 'WHEAT',
            'CORN': 'CORN',
            'COTTON': 'COTTON',
            'SUGAR': 'SUGAR',
            'COFFEE': 'COFFEE'
        }
        
        if symbol not in commodity_functions:
            logger.error(f"Unsupported commodity: {symbol}")
            return None
        
        params = {
            'function': commodity_functions[symbol],
            'interval': interval,
            'apikey': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching data for {symbol} (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    logger.error(f"API Error for {symbol}: {data['Error Message']}")
                    return None
                
                if 'Note' in data:
                    logger.warning(f"API Note for {symbol}: {data['Note']}")
                    return None
                
                if 'data' not in data:
                    logger.error(f"Unexpected API response for {symbol}: {data}")
                    return None
                
                logger.info(f"✓ Successfully fetched data for {symbol}")
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {symbol}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error for {symbol}: {e}")
                if e.response.status_code == 429:
                    logger.warning("Rate limit hit, waiting longer")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 5)
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {symbol}: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error for {symbol}: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error for {symbol}: {e}", exc_info=True)
                return None
        
        logger.error(f"All retry attempts failed for {symbol}")
        return None
    
    def save_to_database(self, symbol: str, data: Dict[str, Any]) -> bool:
        """
        Save commodity data to PostgreSQL database
        
        Args:
            symbol: Commodity symbol
            data: Commodity data from Alpha Vantage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract latest data point
            commodity_data_list = data.get('data', [])
            if not commodity_data_list:
                logger.error(f"No data points for {symbol}")
                return False
            
            latest = commodity_data_list[0]
            
            # Parse the data
            timestamp = datetime.strptime(latest.get('date', ''), '%Y-%m-%d')
            
            commodity_record = {
                'symbol': symbol,
                'timestamp': timestamp,
                'price': float(latest.get('value', 0)),
                'unit': latest.get('unit', 'USD')
            }
            
            # Insert into database using ON CONFLICT for upsert
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO commodities 
                        (symbol, timestamp, price, unit)
                        VALUES (%(symbol)s, %(timestamp)s, %(price)s, %(unit)s)
                        ON CONFLICT (symbol, timestamp) 
                        DO UPDATE SET
                            price = EXCLUDED.price,
                            unit = EXCLUDED.unit,
                            collected_at = CURRENT_TIMESTAMP
                    """, commodity_record)
            
            logger.info(f"✓ Saved {symbol} data to database: ${commodity_record['price']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {symbol} to database: {e}")
            return False
    
    def collect_commodities(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Collect data for multiple commodities
        
        Args:
            symbols: List of commodity symbols
            
        Returns:
            Dictionary with collection results
        """
        if symbols is None:
            symbols = ['WTI', 'NATURAL_GAS', 'COPPER', 'WHEAT', 'CORN']
        
        results = {
            'total': len(symbols),
            'successful': 0,
            'failed': 0,
            'commodities': [],
            'errors': []
        }
        
        for i, symbol in enumerate(symbols):
            # Add delay between requests to avoid rate limits
            if i > 0:
                time.sleep(12)  # Alpha Vantage free tier: 5 calls/minute
            
            data = self.fetch_commodity(symbol)
            
            if data:
                if self.save_to_database(symbol, data):
                    results['successful'] += 1
                    
                    # Extract price for display
                    commodity_data_list = data.get('data', [])
                    if commodity_data_list:
                        latest = commodity_data_list[0]
                        results['commodities'].append({
                            'symbol': symbol,
                            'price': float(latest.get('value', 0)),
                            'date': latest.get('date'),
                            'unit': latest.get('unit', 'USD')
                        })
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{symbol}: Failed to save to database")
            else:
                results['failed'] += 1
                results['errors'].append(f"{symbol}: Failed to fetch data")
        
        return results

def main():
    """Main execution function"""
    logger.info("=== Commodity Data Collection ===\n")
    
    collector = CommodityDataCollector()
    
    # Commodity list - energy, metals, agriculture
    symbols = [
        'WTI',          # Crude Oil
        'NATURAL_GAS',  # Natural Gas
        'COPPER',       # Copper
        'WHEAT',        # Wheat
        'CORN'          # Corn
    ]
    
    logger.info(f"Collecting data for {len(symbols)} commodities: {', '.join(symbols)}")
    results = collector.collect_commodities(symbols)
    
    # Print results
    print(f"\n=== Collection Complete ===")
    print(f"Total: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if results['commodities']:
        print(f"\n💰 Commodity Prices:")
        for commodity in results['commodities']:
            print(f"  {commodity['symbol']}: ${commodity['price']:.2f} {commodity['unit']} ({commodity['date']})")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return results

if __name__ == "__main__":
    main()
