"""
Commodities Repository
Handles all database operations for commodities data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class CommoditiesRepository:
    """Repository for commodities data operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.
        
        Args:
            db_manager: Database manager instance for connection pooling
        """
        self.db_manager = db_manager
    
    def create_tables(self) -> None:
        """Create the commodities table if it doesn't exist."""
        # Drop existing table if schema is wrong
        drop_table_query = "DROP TABLE IF EXISTS commodities CASCADE;"
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS commodities (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            price DECIMAL(15, 4),
            change DECIMAL(15, 4),
            change_percent DECIMAL(10, 4),
            unit VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        );
        """
        
        create_indexes_query = """
        CREATE INDEX IF NOT EXISTS idx_commodities_symbol ON commodities(symbol);
        CREATE INDEX IF NOT EXISTS idx_commodities_timestamp ON commodities(timestamp);
        CREATE INDEX IF NOT EXISTS idx_commodities_symbol_timestamp ON commodities(symbol, timestamp);
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    # Drop old table
                    cur.execute(drop_table_query)
                    # Create new table
                    cur.execute(create_table_query)
                    # Create indexes
                    cur.execute(create_indexes_query)
                conn.commit()
            logger.info("Commodities table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating commodities table: {e}")
            raise DatabaseError(f"Failed to create commodities table: {e}")
    
    def insert_commodity_data(self, commodity_data: Dict[str, Any]) -> bool:
        """
        Insert a single commodity record.
        
        Args:
            commodity_data: Dictionary containing commodity information
            
        Returns:
            True if successful, False otherwise
        """
        insert_query = """
        INSERT INTO commodities (symbol, name, price, change, change_percent, unit, timestamp)
        VALUES (%(symbol)s, %(name)s, %(price)s, %(change)s, %(change_percent)s, %(unit)s, %(timestamp)s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            name = EXCLUDED.name,
            price = EXCLUDED.price,
            change = EXCLUDED.change,
            change_percent = EXCLUDED.change_percent,
            unit = EXCLUDED.unit
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_query, commodity_data)
                conn.commit()
            logger.debug(f"Inserted commodity data for {commodity_data['symbol']}")
            return True
        except Exception as e:
            logger.error(f"Error inserting commodity data for {commodity_data.get('symbol', 'unknown')}: {e}")
            raise DatabaseError(f"Failed to insert commodity data: {e}")
    
    def insert_bulk_commodity_data(self, commodity_data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple commodity records in a single transaction.
        
        Args:
            commodity_data_list: List of commodity data dictionaries
            
        Returns:
            Number of records inserted
        """
        if not commodity_data_list:
            logger.warning("No commodity data to insert")
            return 0
        
        insert_query = """
        INSERT INTO commodities (symbol, name, price, change, change_percent, unit, timestamp)
        VALUES (%(symbol)s, %(name)s, %(price)s, %(change)s, %(change_percent)s, %(unit)s, %(timestamp)s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            name = EXCLUDED.name,
            price = EXCLUDED.price,
            change = EXCLUDED.change,
            change_percent = EXCLUDED.change_percent,
            unit = EXCLUDED.unit
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for commodity_data in commodity_data_list:
                        cur.execute(insert_query, commodity_data)
                conn.commit()
            logger.info(f"Inserted {len(commodity_data_list)} commodity records")
            return len(commodity_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk commodity data: {e}")
            raise DatabaseError(f"Failed to insert bulk commodity data: {e}")
    
    def get_latest_commodity_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent price data for a specific commodity.
        
        Args:
            symbol: Commodity symbol
            
        Returns:
            Dictionary with commodity data or None if not found
        """
        query = """
        SELECT symbol, name, price, change, change_percent, unit, timestamp
        FROM commodities
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
                            'unit': row[5],
                            'timestamp': row[6]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting latest commodity price for {symbol}: {e}")
            raise DatabaseError(f"Failed to get latest commodity price: {e}")
    
    def get_all_latest_commodities(self) -> List[Dict[str, Any]]:
        """
        Get the most recent price data for all commodities.
        
        Returns:
            List of dictionaries with commodity data
        """
        query = """
        WITH latest_commodities AS (
            SELECT symbol, MAX(timestamp) as max_timestamp
            FROM commodities
            GROUP BY symbol
        )
        SELECT c.symbol, c.name, c.price, c.change, c.change_percent, c.unit, c.timestamp
        FROM commodities c
        INNER JOIN latest_commodities lc ON c.symbol = lc.symbol AND c.timestamp = lc.max_timestamp
        ORDER BY c.symbol
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
                        'unit': row[5],
                        'timestamp': row[6]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting all latest commodities: {e}")
            raise DatabaseError(f"Failed to get all latest commodities: {e}")
    
    def get_commodity_history(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical price data for a specific commodity.
        
        Args:
            symbol: Commodity symbol
            days: Number of days of history to retrieve
            
        Returns:
            List of dictionaries with historical commodity data
        """
        query = """
        SELECT symbol, name, price, change, change_percent, unit, timestamp
        FROM commodities
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
                        'unit': row[5],
                        'timestamp': row[6]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting commodity history for {symbol}: {e}")
            raise DatabaseError(f"Failed to get commodity history: {e}")
    
    def get_price_history_for_sparkline(self, symbol: str, days: int = 7) -> List[float]:
        """
        Get simplified price history for sparkline charts.
        
        Args:
            symbol: Commodity symbol
            days: Number of days of history
            
        Returns:
            List of prices ordered by time
        """
        query = """
        SELECT price
        FROM commodities
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
        Delete commodity records older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of records deleted
        """
        delete_query = """
        DELETE FROM commodities
        WHERE timestamp < %s
        """
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old commodity records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old commodity records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
