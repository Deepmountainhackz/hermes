"""
Forex (Foreign Exchange) Data Collector
Fetches currency exchange rates from Alpha Vantage and saves to PostgreSQL
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

class ForexDataCollector:
    """Collector for foreign exchange rate data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("ALPHA_VANTAGE_KEY not found in environment!")
        
    def fetch_exchange_rate(self, from_currency: str, to_currency: str = 'USD') -> Optional[Dict[str, Any]]:
        """
        Fetch exchange rate for a currency pair
        
        Args:
            from_currency: Source currency code (e.g., 'EUR', 'GBP')
            to_currency: Target currency code (default: 'USD')
            
        Returns:
            Dictionary containing exchange rate data or None if failed
        """
        if not self.api_key:
            logger.error("Alpha Vantage API key not provided")
            return None
        
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'apikey': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching rate for {from_currency}/{to_currency} (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check for API errors
                if 'Error Message' in data:
                    logger.error(f"API Error for {from_currency}/{to_currency}: {data['Error Message']}")
                    return None
                
                if 'Note' in data:
                    logger.warning(f"API Note for {from_currency}/{to_currency}: {data['Note']}")
                    return None
                
                if 'Realtime Currency Exchange Rate' not in data:
                    logger.error(f"Unexpected API response for {from_currency}/{to_currency}: {data}")
                    return None
                
                logger.info(f"✓ Successfully fetched rate for {from_currency}/{to_currency}")
                return data['Realtime Currency Exchange Rate']
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {from_currency}/{to_currency}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error for {from_currency}/{to_currency}: {e}")
                if e.response.status_code == 429:
                    logger.warning("Rate limit hit, waiting longer")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 5)
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {from_currency}/{to_currency}: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error for {from_currency}/{to_currency}: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error for {from_currency}/{to_currency}: {e}", exc_info=True)
                return None
        
        logger.error(f"All retry attempts failed for {from_currency}/{to_currency}")
        return None
    
    def save_to_database(self, from_currency: str, to_currency: str, rate_data: Dict[str, Any]) -> bool:
        """
        Save forex data to PostgreSQL database
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            rate_data: Exchange rate data from Alpha Vantage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse the data
            pair = f"{from_currency}/{to_currency}"
            exchange_rate = float(rate_data.get('5. Exchange Rate', 0))
            
            # Parse timestamp
            last_refreshed = rate_data.get('6. Last Refreshed', '')
            timestamp = datetime.strptime(last_refreshed, '%Y-%m-%d %H:%M:%S')
            
            forex_data = {
                'pair': pair,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'exchange_rate': exchange_rate,
                'timestamp': timestamp,
                'bid_price': float(rate_data.get('8. Bid Price', exchange_rate)),
                'ask_price': float(rate_data.get('9. Ask Price', exchange_rate))
            }
            
            # Insert into database using ON CONFLICT for upsert
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO forex 
                        (pair, from_currency, to_currency, exchange_rate, timestamp, bid_price, ask_price)
                        VALUES (%(pair)s, %(from_currency)s, %(to_currency)s, %(exchange_rate)s, 
                                %(timestamp)s, %(bid_price)s, %(ask_price)s)
                        ON CONFLICT (pair, timestamp) 
                        DO UPDATE SET
                            exchange_rate = EXCLUDED.exchange_rate,
                            bid_price = EXCLUDED.bid_price,
                            ask_price = EXCLUDED.ask_price,
                            collected_at = CURRENT_TIMESTAMP
                    """, forex_data)
            
            logger.info(f"✓ Saved {pair} to database: {exchange_rate:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {from_currency}/{to_currency} to database: {e}")
            return False
    
    def collect_forex_rates(self, currencies: List[str] = None, base: str = 'USD') -> Dict[str, Any]:
        """
        Collect exchange rates for multiple currencies
        
        Args:
            currencies: List of currency codes (default: major currencies)
            base: Base currency (default: USD)
            
        Returns:
            Dictionary with collection results
        """
        if currencies is None:
            currencies = ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY']
        
        results = {
            'total': len(currencies),
            'successful': 0,
            'failed': 0,
            'rates': [],
            'errors': []
        }
        
        for i, currency in enumerate(currencies):
            # Add delay between requests to avoid rate limits
            if i > 0:
                time.sleep(12)  # Alpha Vantage free tier: 5 calls/minute
            
            rate_data = self.fetch_exchange_rate(currency, base)
            
            if rate_data:
                if self.save_to_database(currency, base, rate_data):
                    results['successful'] += 1
                    results['rates'].append({
                        'pair': f"{currency}/{base}",
                        'rate': float(rate_data.get('5. Exchange Rate', 0)),
                        'timestamp': rate_data.get('6. Last Refreshed')
                    })
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{currency}/{base}: Failed to save to database")
            else:
                results['failed'] += 1
                results['errors'].append(f"{currency}/{base}: Failed to fetch data")
        
        return results

def main():
    """Main execution function"""
    logger.info("=== Forex Data Collection ===\n")
    
    collector = ForexDataCollector()
    
    # Major currency pairs (relative to USD)
    currencies = [
        'EUR',  # Euro
        'GBP',  # British Pound
        'JPY',  # Japanese Yen
        'CHF',  # Swiss Franc
        'AUD',  # Australian Dollar
        'CAD',  # Canadian Dollar
        'CNY'   # Chinese Yuan
    ]
    
    logger.info(f"Collecting rates for {len(currencies)} currency pairs")
    results = collector.collect_forex_rates(currencies)
    
    # Print results
    print(f"\n=== Collection Complete ===")
    print(f"Total: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if results['rates']:
        print(f"\n💱 Exchange Rates (to USD):")
        for rate in results['rates']:
            print(f"  {rate['pair']}: {rate['rate']:.4f}")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return results

if __name__ == "__main__":
    main()
