"""
Markets Repository
Handles all database operations for market data (stocks).
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class MarketsRepository:
    """Repository for market data operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.
        
        Args:
            db_manager: Database manager instance for connection pooling
        """
        self.db_manager = db_manager
    
    def create_tables(self) -> None:
        """Create the stocks table if it doesn't exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS stocks (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            name VARCHAR(255),
            price DECIMAL(15, 4),
            change DECIMAL(15, 4),
            change_percent DECIMAL(10, 4),
            volume BIGINT,
            market_cap BIGINT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        );
        
        CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
        CREATE INDEX IF NOT EXISTS idx_stocks_timestamp ON stocks(timestamp);
        CREATE INDEX IF NOT EXISTS idx_stocks_symbol_timestamp ON stocks(symbol, timestamp);
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_query)
                conn.commit()
            logger.info("Stocks table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating stocks table: {e}")
            raise DatabaseError(f"Failed to create stocks table: {e}")
    
    def insert_stock_data(self, stock_data: Dict[str, Any]) -> bool:
        """
        Insert a single stock record.
        
        Args:
            stock_data: Dictionary containing stock information
            
        Returns:
            True if successful, False otherwise
        """
        insert_query = """
        INSERT INTO stocks (symbol, name, price, change, change_percent, volume, market_cap, timestamp)
        VALUES (%(symbol)s, %(name)s, %(price)s, %(change)s, %(change_percent)s, %(volume)s, %(market_cap)s, %(timestamp)s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            name = EXCLUDED.name,
            price = EXCLUDED.price,
            change = EXCLUDED.change,
            change_percent = EXCLUDED.change_percent,
            volume = EXCLUDED.volume,
            market_cap = EXCLUDED.market_cap
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_query, stock_data)
                conn.commit()
            logger.debug(f"Inserted stock data for {stock_data['symbol']}")
            return True
        except Exception as e:
            logger.error(f"Error inserting stock data for {stock_data.get('symbol', 'unknown')}: {e}")
            raise DatabaseError(f"Failed to insert stock data: {e}")
    
    def insert_bulk_stock_data(self, stock_data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple stock records in a single transaction.
        
        Args:
            stock_data_list: List of stock data dictionaries
            
        Returns:
            Number of records inserted
        """
        if not stock_data_list:
            logger.warning("No stock data to insert")
            return 0
        
        insert_query = """
        INSERT INTO stocks (symbol, name, price, change, change_percent, volume, market_cap, timestamp)
        VALUES (%(symbol)s, %(name)s, %(price)s, %(change)s, %(change_percent)s, %(volume)s, %(market_cap)s, %(timestamp)s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            name = EXCLUDED.name,
            price = EXCLUDED.price,
            change = EXCLUDED.change,
            change_percent = EXCLUDED.change_percent,
            volume = EXCLUDED.volume,
            market_cap = EXCLUDED.market_cap
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for stock_data in stock_data_list:
                        cur.execute(insert_query, stock_data)
                conn.commit()
            logger.info(f"Inserted {len(stock_data_list)} stock records")
            return len(stock_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk stock data: {e}")
            raise DatabaseError(f"Failed to insert bulk stock data: {e}")
    
    def get_latest_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent price data for a specific stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock data or None if not found
        """
        query = """
        SELECT symbol, name, price, change, change_percent, volume, market_cap, timestamp
        FROM stocks
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (symbol,))
                    row = cur.fetchone()
                    
                    if row:
                        return {
                            'symbol': row[0],
                            'name': row[1],
                            'price': float(row[2]) if row[2] else None,
                            'change': float(row[3]) if row[3] else None,
                            'change_percent': float(row[4]) if row[4] else None,
                            'volume': int(row[5]) if row[5] else None,
                            'market_cap': int(row[6]) if row[6] else None,
                            'timestamp': row[7]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting latest stock price for {symbol}: {e}")
            raise DatabaseError(f"Failed to get latest stock price: {e}")
    
    def get_all_latest_stocks(self) -> List[Dict[str, Any]]:
        """
        Get the most recent price data for all stocks.
        
        Returns:
            List of dictionaries with stock data
        """
        query = """
        WITH latest_stocks AS (
            SELECT symbol, MAX(timestamp) as max_timestamp
            FROM stocks
            GROUP BY symbol
        )
        SELECT s.symbol, s.name, s.price, s.change, s.change_percent, 
               s.volume, s.market_cap, s.timestamp
        FROM stocks s
        INNER JOIN latest_stocks ls ON s.symbol = ls.symbol AND s.timestamp = ls.max_timestamp
        ORDER BY s.symbol
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    
                    return [{
                        'symbol': row[0],
                        'name': row[1],
                        'price': float(row[2]) if row[2] else None,
                        'change': float(row[3]) if row[3] else None,
                        'change_percent': float(row[4]) if row[4] else None,
                        'volume': int(row[5]) if row[5] else None,
                        'market_cap': int(row[6]) if row[6] else None,
                        'timestamp': row[7]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting all latest stocks: {e}")
            raise DatabaseError(f"Failed to get all latest stocks: {e}")
    
    def get_stock_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical price data for a specific stock.
        
        Args:
            symbol: Stock symbol
            days: Number of days of history to retrieve
            
        Returns:
            List of dictionaries with historical stock data
        """
        query = """
        SELECT symbol, name, price, change, change_percent, volume, market_cap, timestamp
        FROM stocks
        WHERE symbol = %s AND timestamp >= %s
        ORDER BY timestamp ASC
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (symbol, start_date))
                    rows = cur.fetchall()
                    
                    return [{
                        'symbol': row[0],
                        'name': row[1],
                        'price': float(row[2]) if row[2] else None,
                        'change': float(row[3]) if row[3] else None,
                        'change_percent': float(row[4]) if row[4] else None,
                        'volume': int(row[5]) if row[5] else None,
                        'market_cap': int(row[6]) if row[6] else None,
                        'timestamp': row[7]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting stock history for {symbol}: {e}")
            raise DatabaseError(f"Failed to get stock history: {e}")
    
    def get_price_history_for_sparkline(self, symbol: str, days: int = 7) -> List[float]:
        """
        Get simplified price history for sparkline charts.
        
        Args:
            symbol: Stock symbol
            days: Number of days of history
            
        Returns:
            List of prices ordered by time
        """
        query = """
        SELECT price
        FROM stocks
        WHERE symbol = %s AND timestamp >= %s AND price IS NOT NULL
        ORDER BY timestamp ASC
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (symbol, start_date))
                    rows = cur.fetchall()
                    return [float(row[0]) for row in rows]
        except Exception as e:
            logger.error(f"Error getting sparkline data for {symbol}: {e}")
            return []
    
    def delete_old_records(self, days: int = 365) -> int:
        """
        Delete stock records older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of records deleted
        """
        delete_query = """
        DELETE FROM stocks
        WHERE timestamp < %s
        """
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old stock records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old stock records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
