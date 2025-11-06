"""
Stock Market Data Collector
Fetches stock data from Alpha Vantage and saves to PostgreSQL
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

class StockDataCollector:
    """Collector for stock market data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("ALPHA_VANTAGE_KEY not found in environment!")
        
    def fetch_stock_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current stock quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'GOOGL')
            
        Returns:
            Dictionary containing stock data or None if failed
        """
        if not self.api_key:
            logger.error("Alpha Vantage API key not provided")
            return None
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
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
                
                if 'Global Quote' not in data:
                    logger.error(f"Unexpected API response for {symbol}: {data}")
                    return None
                
                quote = data['Global Quote']
                
                if not quote:
                    logger.warning(f"No data returned for {symbol}")
                    return None
                
                logger.info(f"✓ Successfully fetched data for {symbol}")
                return quote
                
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
    
    def save_to_database(self, symbol: str, quote: Dict[str, Any]) -> bool:
        """
        Save stock data to PostgreSQL database
        
        Args:
            symbol: Stock symbol
            quote: Quote data from Alpha Vantage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse the data
            trading_day = quote.get('07. latest trading day', '')
            if not trading_day:
                logger.error(f"No trading day in quote for {symbol}")
                return False
            
            timestamp = datetime.strptime(trading_day, '%Y-%m-%d')
            
            stock_data = {
                'symbol': symbol,
                'timestamp': timestamp,
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'close': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0))
            }
            
            # Insert into database using ON CONFLICT for upsert
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO stocks 
                        (symbol, timestamp, open, high, low, close, volume)
                        VALUES (%(symbol)s, %(timestamp)s, %(open)s, %(high)s, 
                                %(low)s, %(close)s, %(volume)s)
                        ON CONFLICT (symbol, timestamp) 
                        DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume,
                            collected_at = CURRENT_TIMESTAMP
                    """, stock_data)
            
            logger.info(f"✓ Saved {symbol} data to database: ${stock_data['close']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {symbol} to database: {e}")
            return False
    
    def collect_stocks(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Collect data for multiple stocks
        
        Args:
            symbols: List of stock symbols (default: AAPL, GOOGL, MSFT)
            
        Returns:
            Dictionary with collection results
        """
        if symbols is None:
            symbols = ['AAPL', 'GOOGL', 'MSFT']
        
        results = {
            'total': len(symbols),
            'successful': 0,
            'failed': 0,
            'stocks': [],
            'errors': []
        }
        
        for i, symbol in enumerate(symbols):
            # Add delay between requests to avoid rate limits
            if i > 0:
                time.sleep(12)  # Alpha Vantage free tier: 5 calls/minute
            
            quote = self.fetch_stock_quote(symbol)
            
            if quote:
                if self.save_to_database(symbol, quote):
                    results['successful'] += 1
                    results['stocks'].append({
                        'symbol': symbol,
                        'price': float(quote.get('05. price', 0)),
                        'change': quote.get('09. change'),
                        'change_percent': quote.get('10. change percent'),
                        'volume': quote.get('06. volume')
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
    logger.info("=== Stock Market Data Collection ===\n")
    
    collector = StockDataCollector()
    
    # Default stock list - major tech companies
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    logger.info(f"Collecting data for {len(symbols)} stocks: {', '.join(symbols)}")
    results = collector.collect_stocks(symbols)
    
    # Print results
    print(f"\n=== Collection Complete ===")
    print(f"Total: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    if results['stocks']:
        print(f"\n📈 Stock Prices:")
        for stock in results['stocks']:
            change_symbol = "📈" if '+' in str(stock.get('change_percent', '')) else "📉"
            print(f"  {change_symbol} {stock['symbol']}: ${stock['price']:.2f} ({stock.get('change_percent', 'N/A')})")
    
    if results['errors']:
        print(f"\n❌ Errors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return results

if __name__ == "__main__":
    main()
