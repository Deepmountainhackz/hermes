"""
Disasters Repository
Handles all database operations for disaster events data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class DisastersRepository:
    """Repository for disaster events data operations."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.

        Args:
            db_manager: Database manager instance for connection handling
        """
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the disasters table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS disasters (
            id SERIAL PRIMARY KEY,
            disaster_type VARCHAR(50),
            location VARCHAR(255),
            magnitude DECIMAL(5, 2),
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_disasters_type ON disasters(disaster_type);
        CREATE INDEX IF NOT EXISTS idx_disasters_timestamp ON disasters(timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("Disasters table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating disasters table: {e}")
            raise DatabaseError(f"Failed to create disasters table: {e}")

    def insert_bulk_disaster_data(self, disaster_data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple disaster event records in a single transaction.

        Args:
            disaster_data_list: List of disaster event data dictionaries

        Returns:
            Number of records inserted
        """
        if not disaster_data_list:
            logger.warning("No disaster data to insert")
            return 0

        insert_query = """
        INSERT INTO disasters (disaster_type, location, magnitude, description, timestamp)
        VALUES (%(disaster_type)s, %(location)s, %(magnitude)s, %(description)s, %(timestamp)s)
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in disaster_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            logger.info(f"Inserted {len(disaster_data_list)} disaster records")
            return len(disaster_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk disaster data: {e}")
            raise DatabaseError(f"Failed to insert disaster data: {e}")

    def get_latest_disasters(self, disaster_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the most recent disaster events.

        Args:
            disaster_type: Optional filter by disaster type

        Returns:
            List of dictionaries with disaster event data
        """
        if disaster_type:
            query = """
            SELECT disaster_type, location, magnitude, description, timestamp
            FROM disasters
            WHERE disaster_type = %s
            ORDER BY timestamp DESC
            LIMIT 20
            """
            params = (disaster_type,)
        else:
            query = """
            SELECT disaster_type, location, magnitude, description, timestamp
            FROM disasters
            ORDER BY timestamp DESC
            LIMIT 20
            """
            params = None

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    if params:
                        cur.execute(query, params)
                    else:
                        cur.execute(query)
                    rows = cur.fetchall()

                    return [{
                        'disaster_type': row[0],
                        'location': row[1],
                        'magnitude': float(row[2]) if row[2] else None,
                        'description': row[3],
                        'timestamp': row[4]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest disasters: {e}")
            raise DatabaseError(f"Failed to get latest disasters: {e}")

    def delete_old_records(self, days: int = 365) -> int:
        """
        Delete disaster records older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of records deleted
        """
        delete_query = "DELETE FROM disasters WHERE timestamp < %s"
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old disaster records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old disaster records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
