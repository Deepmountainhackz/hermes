"""
Economics Repository
Handles all database operations for economic indicators data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class EconomicsRepository:
    """Repository for economic indicators data operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the repository."""
        self.db_manager = db_manager
    
    def create_tables(self) -> None:
        """Create the economic_indicators table if it doesn't exist."""
        drop_table_query = "DROP TABLE IF EXISTS economic_indicators CASCADE;"
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id SERIAL PRIMARY KEY,
            indicator VARCHAR(50) NOT NULL,
            country VARCHAR(3) NOT NULL,
            name VARCHAR(255),
            value DECIMAL(20, 4),
            unit VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(indicator, country, timestamp)
        );
        """
        
        create_indexes_query = """
        CREATE INDEX IF NOT EXISTS idx_econ_indicator ON economic_indicators(indicator);
        CREATE INDEX IF NOT EXISTS idx_econ_country ON economic_indicators(country);
        CREATE INDEX IF NOT EXISTS idx_econ_timestamp ON economic_indicators(timestamp);
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(drop_table_query)
                    cur.execute(create_table_query)
                    cur.execute(create_indexes_query)
                conn.commit()
            logger.info("Economic indicators table created successfully")
        except Exception as e:
            logger.error(f"Error creating economic indicators table: {e}")
            raise DatabaseError(f"Failed to create economic indicators table: {e}")
    
    def insert_indicator_data(self, indicator_data: Dict[str, Any]) -> bool:
        """Insert a single economic indicator record."""
        insert_query = """
        INSERT INTO economic_indicators (indicator, country, name, value, unit, timestamp)
        VALUES (%(indicator)s, %(country)s, %(name)s, %(value)s, %(unit)s, %(timestamp)s)
        ON CONFLICT (indicator, country, timestamp) DO UPDATE SET
            value = EXCLUDED.value
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_query, indicator_data)
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error inserting indicator data: {e}")
            raise DatabaseError(f"Failed to insert indicator data: {e}")
    
    def insert_bulk_indicator_data(self, indicator_data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple economic indicator records."""
        if not indicator_data_list:
            return 0
        
        insert_query = """
        INSERT INTO economic_indicators (indicator, country, name, value, unit, timestamp)
        VALUES (%(indicator)s, %(country)s, %(name)s, %(value)s, %(unit)s, %(timestamp)s)
        ON CONFLICT (indicator, country, timestamp) DO UPDATE SET
            value = EXCLUDED.value
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in indicator_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            logger.info(f"Inserted {len(indicator_data_list)} economic indicator records")
            return len(indicator_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk indicator data: {e}")
            raise DatabaseError(f"Failed to insert bulk indicator data: {e}")
    
    def get_latest_indicator(self, indicator: str, country: str) -> Optional[Dict[str, Any]]:
        """Get the most recent value for a specific indicator."""
        query = """
        SELECT indicator, country, name, value, unit, timestamp
        FROM economic_indicators
        WHERE indicator = %s AND country = %s
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (indicator, country))
                    row = cur.fetchone()
                    
                    if row:
                        return {
                            'indicator': row[0],
                            'country': row[1],
                            'name': row[2],
                            'value': float(row[3]) if row[3] else None,
                            'unit': row[4],
                            'timestamp': row[5]
                        }
                    return None
        except Exception as e:
            logger.error(f"Error getting latest indicator: {e}")
            raise DatabaseError(f"Failed to get latest indicator: {e}")
    
    def get_all_latest_indicators(self) -> List[Dict[str, Any]]:
        """Get the most recent values for all indicators."""
        query = """
        WITH latest_indicators AS (
            SELECT indicator, country, MAX(timestamp) as max_timestamp
            FROM economic_indicators
            GROUP BY indicator, country
        )
        SELECT e.indicator, e.country, e.name, e.value, e.unit, e.timestamp
        FROM economic_indicators e
        INNER JOIN latest_indicators l 
            ON e.indicator = l.indicator 
            AND e.country = l.country 
            AND e.timestamp = l.max_timestamp
        ORDER BY e.country, e.indicator
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    
                    return [{
                        'indicator': row[0],
                        'country': row[1],
                        'name': row[2],
                        'value': float(row[3]) if row[3] else None,
                        'unit': row[4],
                        'timestamp': row[5]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting all latest indicators: {e}")
            raise DatabaseError(f"Failed to get all latest indicators: {e}")
    
    def delete_old_records(self, days: int = 365) -> int:
        """Delete old economic indicator records."""
        delete_query = "DELETE FROM economic_indicators WHERE timestamp < %s"
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old economic indicator records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
