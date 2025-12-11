"""
Space Repository
Handles all database operations for space events data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class SpaceRepository:
    """Repository for space events data operations."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.

        Args:
            db_manager: Database manager instance for connection handling
        """
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the space_events table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS space_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            description TEXT,
            data JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_space_type ON space_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_space_timestamp ON space_events(timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("Space events table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating space events table: {e}")
            raise DatabaseError(f"Failed to create space table: {e}")

    def insert_bulk_space_data(self, space_data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple space event records in a single transaction.

        Args:
            space_data_list: List of space event data dictionaries

        Returns:
            Number of records inserted
        """
        if not space_data_list:
            logger.warning("No space data to insert")
            return 0

        insert_query = """
        INSERT INTO space_events (event_type, name, description, data, timestamp)
        VALUES (%(event_type)s, %(name)s, %(description)s, %(data)s, %(timestamp)s)
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in space_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            logger.info(f"Inserted {len(space_data_list)} space event records")
            return len(space_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk space data: {e}")
            raise DatabaseError(f"Failed to insert space data: {e}")

    def get_latest_space_events(self, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the most recent space events.

        Args:
            event_type: Optional filter by event type

        Returns:
            List of dictionaries with space event data
        """
        if event_type:
            query = """
            SELECT event_type, name, description, data, timestamp
            FROM space_events
            WHERE event_type = %s
            ORDER BY timestamp DESC
            LIMIT 10
            """
            params = (event_type,)
        else:
            query = """
            SELECT event_type, name, description, data, timestamp
            FROM space_events
            ORDER BY timestamp DESC
            LIMIT 10
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
                        'event_type': row[0],
                        'name': row[1],
                        'description': row[2],
                        'data': row[3],
                        'timestamp': row[4]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest space events: {e}")
            raise DatabaseError(f"Failed to get latest space events: {e}")

    def delete_old_records(self, days: int = 365) -> int:
        """
        Delete space event records older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of records deleted
        """
        delete_query = "DELETE FROM space_events WHERE timestamp < %s"
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old space event records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old space records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
