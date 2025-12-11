"""
Forex Repository
Handles all database operations for forex (currency exchange) data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class ForexRepository:
    """Repository for forex data operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.
        
        Args:
            db_manager: Database manager instance for connection pooling
        """
        self.db_manager = db_manager
    
    def create_tables(self) -> None:
        """Create the forex table if it doesn't exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS forex (
            id SERIAL PRIMARY KEY,
            pair VARCHAR(10) NOT NULL,
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate DECIMAL(15, 8),
            bid DECIMAL(15, 8),
            ask DECIMAL(15, 8),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pair, timestamp)
        );

        CREATE INDEX IF NOT EXISTS idx_forex_pair ON forex(pair);
        CREATE INDEX IF NOT EXISTS idx_forex_timestamp ON forex(timestamp);
        CREATE INDEX IF NOT EXISTS idx_forex_pair_timestamp ON forex(pair, timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_query)
                conn.commit()
            logger.info("Forex table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating forex table: {e}")
            raise DatabaseError(f"Failed to create forex table: {e}")
    
    def insert_forex_data(self, forex_data: Dict[str, Any]) -> bool:
        """
        Insert a single forex record.
        
        Args:
            forex_data: Dictionary containing forex information
            
        Returns:
            True if successful, False otherwise
        """
        insert_query = """
        INSERT INTO forex (pair, from_currency, to_currency, rate, bid, ask, timestamp)
        VALUES (%(pair)s, %(from_currency)s, %(to_currency)s, %(rate)s, %(bid)s, %(ask)s, %(timestamp)s)
        ON CONFLICT (pair, timestamp) DO UPDATE SET
            rate = EXCLUDED.rate,
            bid = EXCLUDED.bid,
            ask = EXCLUDED.ask
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_query, forex_data)
                conn.commit()
            logger.debug(f"Inserted forex data for {forex_data['pair']}")
            return True
        except Exception as e:
            logger.error(f"Error inserting forex data for {forex_data.get('pair', 'unknown')}: {e}")
            raise DatabaseError(f"Failed to insert forex data: {e}")
    
    def insert_bulk_forex_data(self, forex_data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple forex records in a single transaction.
        
        Args:
            forex_data_list: List of forex data dictionaries
            
        Returns:
            Number of records inserted
        """
        if not forex_data_list:
            logger.warning("No forex data to insert")
            return 0
        
        insert_query = """
        INSERT INTO forex (pair, from_currency, to_currency, rate, bid, ask, timestamp)
        VALUES (%(pair)s, %(from_currency)s, %(to_currency)s, %(rate)s, %(bid)s, %(ask)s, %(timestamp)s)
        ON CONFLICT (pair, timestamp) DO UPDATE SET
            rate = EXCLUDED.rate,
            bid = EXCLUDED.bid,
            ask = EXCLUDED.ask
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for forex_data in forex_data_list:
                        cur.execute(insert_query, forex_data)
                conn.commit()
            logger.info(f"Inserted {len(forex_data_list)} forex records")
            return len(forex_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk forex data: {e}")
            raise DatabaseError(f"Failed to insert bulk forex data: {e}")
    
    def get_latest_forex_rate(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent exchange rate for a specific currency pair.
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            
        Returns:
            Dictionary with forex data or None if not found
        """
        query = """
        SELECT pair, from_currency, to_currency, rate, bid, ask, timestamp
        FROM forex
        WHERE pair = %s
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (pair,))
                    row = cur.fetchone()
                    
                    if row:
                        return {
                            'pair': row[0],
                            'from_currency': row[1],
                            'to_currency': row[2],
                            'rate': float(row[3]) if row[3] else None,
                            'bid': float(row[4]) if row[4] else None,
                            'ask': float(row[5]) if row[5] else None,
                            'timestamp': row[6]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting latest forex rate for {pair}: {e}")
            raise DatabaseError(f"Failed to get latest forex rate: {e}")
    
    def get_all_latest_forex_rates(self) -> List[Dict[str, Any]]:
        """
        Get the most recent exchange rates for all currency pairs.
        
        Returns:
            List of dictionaries with forex data
        """
        query = """
        WITH latest_forex AS (
            SELECT pair, MAX(timestamp) as max_timestamp
            FROM forex
            GROUP BY pair
        )
        SELECT f.pair, f.from_currency, f.to_currency, f.rate, f.bid, f.ask, f.timestamp
        FROM forex f
        INNER JOIN latest_forex lf ON f.pair = lf.pair AND f.timestamp = lf.max_timestamp
        ORDER BY f.pair
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    
                    return [{
                        'pair': row[0],
                        'from_currency': row[1],
                        'to_currency': row[2],
                        'rate': float(row[3]) if row[3] else None,
                        'bid': float(row[4]) if row[4] else None,
                        'ask': float(row[5]) if row[5] else None,
                        'timestamp': row[6]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting all latest forex rates: {e}")
            raise DatabaseError(f"Failed to get all latest forex rates: {e}")
    
    def get_forex_history(self, pair: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical exchange rate data for a specific currency pair.
        
        Args:
            pair: Currency pair
            days: Number of days of history to retrieve
            
        Returns:
            List of dictionaries with historical forex data
        """
        query = """
        SELECT pair, from_currency, to_currency, rate, bid, ask, timestamp
        FROM forex
        WHERE pair = %s AND timestamp >= %s
        ORDER BY timestamp ASC
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (pair, start_date))
                    rows = cur.fetchall()
                    
                    return [{
                        'pair': row[0],
                        'from_currency': row[1],
                        'to_currency': row[2],
                        'rate': float(row[3]) if row[3] else None,
                        'bid': float(row[4]) if row[4] else None,
                        'ask': float(row[5]) if row[5] else None,
                        'timestamp': row[6]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting forex history for {pair}: {e}")
            raise DatabaseError(f"Failed to get forex history: {e}")
    
    def get_rate_history_for_sparkline(self, pair: str, days: int = 7) -> List[float]:
        """
        Get simplified rate history for sparkline charts.
        
        Args:
            pair: Currency pair
            days: Number of days of history
            
        Returns:
            List of rates ordered by time
        """
        query = """
        SELECT rate
        FROM forex
        WHERE pair = %s AND timestamp >= %s AND rate IS NOT NULL
        ORDER BY timestamp ASC
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (pair, start_date))
                    rows = cur.fetchall()
                    return [float(row[0]) for row in rows]
        except Exception as e:
            logger.error(f"Error getting sparkline data for {pair}: {e}")
            return []
    
    def delete_old_records(self, days: int = 365) -> int:
        """
        Delete forex records older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of records deleted
        """
        delete_query = """
        DELETE FROM forex
        WHERE timestamp < %s
        """
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old forex records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old forex records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
