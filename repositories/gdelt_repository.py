"""
GDELT Repository
Handles all database operations for GDELT events data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class GdeltRepository:
    """Repository for GDELT events data operations."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize the repository."""
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the GDELT events table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS gdelt_events (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500),
            url TEXT UNIQUE,
            source VARCHAR(200),
            country VARCHAR(50),
            event_type VARCHAR(50),
            tone DECIMAL(10, 4),
            published_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_gdelt_country ON gdelt_events(country);
        CREATE INDEX IF NOT EXISTS idx_gdelt_event_type ON gdelt_events(event_type);
        CREATE INDEX IF NOT EXISTS idx_gdelt_timestamp ON gdelt_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_gdelt_tone ON gdelt_events(tone);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("GDELT events table created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating GDELT events table: {e}")
            raise DatabaseError(f"Failed to create GDELT events table: {e}")

    def insert_bulk_events(self, events_list: List[Dict[str, Any]]) -> int:
        """Insert multiple GDELT event records."""
        if not events_list:
            logger.warning("No GDELT events to insert")
            return 0

        insert_query = """
        INSERT INTO gdelt_events (title, url, source, country, event_type, tone, published_at, timestamp)
        VALUES (%(title)s, %(url)s, %(source)s, %(country)s, %(event_type)s, %(tone)s, %(published_at)s, %(timestamp)s)
        ON CONFLICT (url) DO UPDATE SET
            tone = EXCLUDED.tone,
            timestamp = EXCLUDED.timestamp
        """

        inserted = 0
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for event in events_list:
                        try:
                            cur.execute(insert_query, event)
                            inserted += 1
                        except Exception as e:
                            logger.warning(f"Failed to insert event: {e}")
                conn.commit()
            logger.info(f"Inserted {inserted} GDELT event records")
            return inserted
        except Exception as e:
            logger.error(f"Error inserting bulk GDELT events: {e}")
            raise DatabaseError(f"Failed to insert GDELT events: {e}")

    def get_latest_events(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the most recent GDELT events."""
        if event_type:
            query = """
            SELECT title, url, source, country, event_type, tone, published_at, timestamp
            FROM gdelt_events
            WHERE event_type = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """
            params = (event_type, limit)
        else:
            query = """
            SELECT title, url, source, country, event_type, tone, published_at, timestamp
            FROM gdelt_events
            ORDER BY timestamp DESC
            LIMIT %s
            """
            params = (limit,)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall()

                    return [{
                        'title': row[0],
                        'url': row[1],
                        'source': row[2],
                        'country': row[3],
                        'event_type': row[4],
                        'tone': float(row[5]) if row[5] else 0,
                        'published_at': row[6],
                        'timestamp': row[7]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest GDELT events: {e}")
            raise DatabaseError(f"Failed to get GDELT events: {e}")

    def get_events_by_country(self, country: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get events for a specific country."""
        query = """
        SELECT title, url, source, country, event_type, tone, published_at, timestamp
        FROM gdelt_events
        WHERE country = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (country, limit))
                    rows = cur.fetchall()

                    return [{
                        'title': row[0],
                        'url': row[1],
                        'source': row[2],
                        'country': row[3],
                        'event_type': row[4],
                        'tone': float(row[5]) if row[5] else 0,
                        'published_at': row[6],
                        'timestamp': row[7]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting GDELT events for {country}: {e}")
            raise DatabaseError(f"Failed to get events for {country}: {e}")

    def get_event_counts_by_type(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get event counts by type for the last N days."""
        query = """
        SELECT event_type, COUNT(*) as count
        FROM gdelt_events
        WHERE timestamp >= %s
        GROUP BY event_type
        ORDER BY count DESC
        """
        cutoff = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (cutoff,))
                    rows = cur.fetchall()
                    return [{'event_type': row[0], 'count': row[1]} for row in rows]
        except Exception as e:
            logger.error(f"Error getting event counts: {e}")
            return []

    def get_average_tone_by_country(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get average sentiment tone by country."""
        query = """
        SELECT country, AVG(tone) as avg_tone, COUNT(*) as event_count
        FROM gdelt_events
        WHERE timestamp >= %s AND tone IS NOT NULL
        GROUP BY country
        ORDER BY avg_tone ASC
        LIMIT 20
        """
        cutoff = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (cutoff,))
                    rows = cur.fetchall()
                    return [{
                        'country': row[0],
                        'avg_tone': float(row[1]) if row[1] else 0,
                        'event_count': row[2]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting tone by country: {e}")
            return []

    def delete_old_records(self, days: int = 30) -> int:
        """Delete GDELT records older than specified days."""
        delete_query = "DELETE FROM gdelt_events WHERE timestamp < %s"
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old GDELT event records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old GDELT records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
