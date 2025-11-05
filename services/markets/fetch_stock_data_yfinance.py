"""
Stock Market Data Collector
Fetches real-time stock market data using yfinance (Yahoo Finance)
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockDataCollector:
    """Collector for stock market data using yfinance"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
        
        # Try to import yfinance
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            logger.error("yfinance not installed. Install with: pip install yfinance --break-system-packages")
            self.yf = None
        
    def fetch_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real-time quote for a stock
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
            
        Returns:
            Dictionary containing stock quote or None if failed
        """
        if not self.yf:
            logger.error("yfinance not available")
            return None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching quote for {symbol} (attempt {attempt + 1}/{self.max_retries})")
                
                # Create ticker object
                ticker = self.yf.Ticker(symbol)
                
                # Get current data
                info = ticker.info
                hist = ticker.history(period="5d")
                
                if hist.empty or not info:
                    logger.error(f"No data available for {symbol}")
                    return None
                
                # Get latest price
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                
                # Calculate change
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close != 0 else 0
                
                quote_data = {
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'price': round(float(current_price), 2),
                    'change': round(float(change), 2),
                    'change_percent': round(float(change_percent), 2),
                    'open': round(float(hist['Open'].iloc[-1]), 2) if 'Open' in hist.columns else None,
                    'high': round(float(hist['High'].iloc[-1]), 2) if 'High' in hist.columns else None,
                    'low': round(float(hist['Low'].iloc[-1]), 2) if 'Low' in hist.columns else None,
                    'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    'previous_close': round(float(prev_close), 2),
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    'dividend_yield': info.get('dividendYield'),
                    'week_52_high': info.get('fiftyTwoWeekHigh'),
                    'week_52_low': info.get('fiftyTwoWeekLow'),
                    'avg_volume': info.get('averageVolume'),
                    'sector': info.get('sector'),
                    'industry': info.get('industry'),
                    'currency': info.get('currency', 'USD'),
                    'exchange': info.get('exchange'),
                    'collection_time': datetime.utcnow().isoformat(),
                    'status': 'success'
                }
                
                logger.info(f"Successfully fetched {symbol}: ${quote_data['price']} ({quote_data['change_percent']:+.2f}%)")
                
                return quote_data
                
            except Exception as e:
                logger.error(f"Error fetching {symbol} on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"All retry attempts failed for {symbol}")
        return None
    
    def fetch_data(self, symbols: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols (default: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
            
        Returns:
            Dictionary containing all stock data or None if all failed
        """
        if symbols is None:
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']
        
        logger.info(f"Starting stock market data collection for {len(symbols)} symbols")
        
        quotes = []
        failed = []
        
        for symbol in symbols:
            quote = self.fetch_quote(symbol)
            if quote:
                quotes.append(quote)
            else:
                failed.append(symbol)
            
            # Small delay between requests
            time.sleep(0.5)
        
        if not quotes:
            logger.error("All stock data collection failed")
            return None
        
        # Calculate market summary
        total_market_cap = sum(q['market_cap'] for q in quotes if q['market_cap'])
        avg_change = sum(q['change_percent'] for q in quotes) / len(quotes)
        
        gainers = [q for q in quotes if q['change'] > 0]
        losers = [q for q in quotes if q['change'] < 0]
        
        return {
            'stocks': quotes,
            'total_stocks': len(quotes),
            'failed_stocks': failed,
            'total_market_cap': total_market_cap,
            'average_change_percent': round(avg_change, 2),
            'gainers_count': len(gainers),
            'losers_count': len(losers),
            'top_gainer': max(quotes, key=lambda x: x['change_percent']) if quotes else None,
            'top_loser': min(quotes, key=lambda x: x['change_percent']) if quotes else None,
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success' if not failed else 'partial_success'
        }

def main():
    """Main execution function"""
    collector = StockDataCollector()
    
    logger.info("Starting stock market data collection")
    
    # Fetch data for major tech stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    data = collector.fetch_data(symbols)
    
    if data:
        logger.info("Stock market data collection successful")
        print("\n=== Stock Market Data ===")
        print(f"Total Stocks: {data['total_stocks']}")
        print(f"Average Change: {data['average_change_percent']:+.2f}%")
        print(f"Gainers: {data['gainers_count']} | Losers: {data['losers_count']}")
        
        print("\n📈 Stock Quotes:")
        for stock in data['stocks']:
            change_symbol = "📈" if stock['change'] > 0 else "📉"
            print(f"\n{change_symbol} {stock['symbol']} - {stock['name']}")
            print(f"   Price: ${stock['price']:.2f}")
            print(f"   Change: {stock['change']:+.2f} ({stock['change_percent']:+.2f}%)")
            print(f"   Volume: {stock['volume']:,}")
            if stock['market_cap']:
                print(f"   Market Cap: ${stock['market_cap']:,.0f}")
        
        if data['top_gainer']:
            print(f"\n🏆 Top Gainer: {data['top_gainer']['symbol']} ({data['top_gainer']['change_percent']:+.2f}%)")
        
        if data['top_loser']:
            print(f"📉 Top Loser: {data['top_loser']['symbol']} ({data['top_loser']['change_percent']:+.2f}%)")
        
        if data['failed_stocks']:
            print(f"\n⚠️  Failed to fetch: {', '.join(data['failed_stocks'])}")
        
        print(f"\nCollection Time: {data['collection_time']}")
        
        return data
    else:
        logger.error("Stock market data collection failed")
        print("\n⚠️  Stock collection failed. Make sure yfinance is installed:")
        print("   pip install yfinance --break-system-packages")
        return None

if __name__ == "__main__":
    main()
