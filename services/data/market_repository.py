"""
Repository for market data (stocks, forex, commodities).
"""

from typing import List, Optional
import pandas as pd
import streamlit as st
from services.data.base_repository import BaseRepository
from core.database import db
import logging

logger = logging.getLogger(__name__)

class MarketRepository(BaseRepository):
    """Repository for market data"""
    
    def __init__(self):
        super().__init__('stocks')
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_latest(_self) -> pd.DataFrame:
        """
        Get latest stock prices with 30-day history.
        Cached for 5 minutes.
        
        Returns:
            DataFrame with latest prices and historical data
        """
        query = """
            WITH latest AS (
                SELECT DISTINCT ON (symbol)
                    symbol,
                    latest_price as price,
                    daily_change_pct as change_pct,
                    volume,
                    market_cap,
                    timestamp
                FROM stocks
                ORDER BY symbol, timestamp DESC
            ),
            historical AS (
                SELECT 
                    symbol,
                    ARRAY_AGG(latest_price ORDER BY timestamp) as price_history,
                    ARRAY_AGG(timestamp ORDER BY timestamp) as dates
                FROM stocks
                WHERE timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY symbol
            )
            SELECT 
                l.symbol,
                l.price,
                l.change_pct,
                l.volume,
                l.market_cap,
                l.timestamp,
                h.price_history,
                h.dates
            FROM latest l
            LEFT JOIN historical h ON l.symbol = h.symbol
            ORDER BY l.market_cap DESC NULLS LAST
        """
        
        try:
            with db.get_connection() as conn:
                df = pd.read_sql(query, conn)
                logger.info(f"Retrieved {len(df)} stocks with latest prices")
                return df
        except Exception as e:
            logger.error(f"Error fetching latest market data: {e}")
            return pd.DataFrame()
    
    def get_by_symbol(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Get historical data for specific symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            days: Number of days of history
            
        Returns:
            DataFrame with historical data
        """
        query = """
            SELECT 
                symbol,
                latest_price,
                daily_change_pct,
                volume,
                market_cap,
                timestamp
            FROM stocks
            WHERE symbol = %s
            AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """
        
        try:
            with self.db.get_connection() as conn:
                return pd.read_sql(query, conn, params=(symbol, days))
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_top_movers(self, limit: int = 10, direction: str = 'both') -> pd.DataFrame:
        """
        Get stocks with biggest daily moves.
        
        Args:
            limit: Number of stocks to return
            direction: 'up', 'down', or 'both'
            
        Returns:
            DataFrame with top movers
        """
        if direction == 'up':
            order = 'daily_change_pct DESC'
        elif direction == 'down':
            order = 'daily_change_pct ASC'
        else:
            order = 'ABS(daily_change_pct) DESC'
        
        query = f"""
            SELECT DISTINCT ON (symbol)
                symbol,
                latest_price,
                daily_change_pct,
                volume,
                market_cap,
                timestamp
            FROM stocks
            ORDER BY symbol, timestamp DESC
            LIMIT 1000
        """
        
        try:
            with self.db.get_connection() as conn:
                df = pd.read_sql(query, conn)
                
                if direction == 'up':
                    df = df.nlargest(limit, 'daily_change_pct')
                elif direction == 'down':
                    df = df.nsmallest(limit, 'daily_change_pct')
                else:
                    df['abs_change'] = df['daily_change_pct'].abs()
                    df = df.nlargest(limit, 'abs_change')
                    df = df.drop('abs_change', axis=1)
                
                return df
        except Exception as e:
            logger.error(f"Error fetching top movers: {e}")
            return pd.DataFrame()
    
    def get_market_summary(self) -> dict:
        """
        Get aggregated market summary statistics.
        
        Returns:
            Dictionary with summary stats
        """
        query = """
            WITH latest AS (
                SELECT DISTINCT ON (symbol)
                    symbol,
                    latest_price,
                    daily_change_pct,
                    volume,
                    market_cap
                FROM stocks
                ORDER BY symbol, timestamp DESC
            )
            SELECT 
                COUNT(*) as total_stocks,
                AVG(daily_change_pct) as avg_change,
                SUM(CASE WHEN daily_change_pct > 0 THEN 1 ELSE 0 END) as gainers,
                SUM(CASE WHEN daily_change_pct < 0 THEN 1 ELSE 0 END) as losers,
                SUM(CASE WHEN daily_change_pct = 0 THEN 1 ELSE 0 END) as unchanged,
                MAX(daily_change_pct) as max_gain,
                MIN(daily_change_pct) as max_loss
            FROM latest
        """
        
        try:
            result = self.db.execute_query(query, fetch_one=True)
            return result if result else {}
        except Exception as e:
            logger.error(f"Error fetching market summary: {e}")
            return {}
    
    def get_symbols_list(self) -> List[str]:
        """
        Get list of all tracked symbols.
        
        Returns:
            List of stock symbols
        """
        query = "SELECT DISTINCT symbol FROM stocks ORDER BY symbol"
        
        try:
            results = self.db.execute_query(query)
            return [r['symbol'] for r in results] if results else []
        except Exception as e:
            logger.error(f"Error fetching symbols list: {e}")
            return []
    
    def store_stock_data(self, symbol: str, price: float, change_pct: float, 
                         volume: int, market_cap: Optional[int] = None) -> bool:
        """
        Store new stock data point.
        
        Args:
            symbol: Stock symbol
            price: Current price
            change_pct: Daily change percentage
            volume: Trading volume
            market_cap: Market capitalization (optional)
            
        Returns:
            True if successful
        """
        data = {
            'symbol': symbol,
            'latest_price': price,
            'daily_change_pct': change_pct,
            'volume': volume,
            'market_cap': market_cap
        }
        
        return self.insert(data) is not None
