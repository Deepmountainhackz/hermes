"""
News Repository
Handles all database operations for news article data.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class NewsRepository:
    """Repository for news article data operations."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the repository.

        Args:
            db_manager: Database manager instance for connection handling
        """
        self.db_manager = db_manager

    def create_tables(self) -> None:
        """Create the news table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500),
            source VARCHAR(100),
            url TEXT UNIQUE,
            description TEXT,
            published_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);
        CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news(timestamp);
        CREATE INDEX IF NOT EXISTS idx_news_url ON news(url);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                    # Add unique constraint if it doesn't exist (for existing tables)
                    cur.execute("""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint WHERE conname = 'news_url_key'
                            ) THEN
                                -- Remove duplicates first, keeping only the latest
                                DELETE FROM news a USING news b
                                WHERE a.id < b.id AND a.url = b.url;
                                -- Add unique constraint
                                ALTER TABLE news ADD CONSTRAINT news_url_key UNIQUE (url);
                            END IF;
                        END $$;
                    """)
                conn.commit()
            logger.info("News table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating news table: {e}")
            raise DatabaseError(f"Failed to create news table: {e}")

    def insert_bulk_news_data(self, news_data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple news article records in a single transaction.

        Args:
            news_data_list: List of news article data dictionaries

        Returns:
            Number of records inserted
        """
        if not news_data_list:
            logger.warning("No news data to insert")
            return 0

        insert_query = """
        INSERT INTO news (title, source, url, description, published_at, timestamp)
        VALUES (%(title)s, %(source)s, %(url)s, %(description)s, %(published_at)s, %(timestamp)s)
        ON CONFLICT (url) DO NOTHING
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in news_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            logger.info(f"Inserted {len(news_data_list)} news article records")
            return len(news_data_list)
        except Exception as e:
            logger.error(f"Error inserting bulk news data: {e}")
            raise DatabaseError(f"Failed to insert news data: {e}")

    def get_latest_news(self, source: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the most recent news articles.

        Args:
            source: Optional filter by news source
            limit: Maximum number of articles to return

        Returns:
            List of dictionaries with news article data
        """
        if source:
            query = """
            SELECT title, source, url, description, published_at, timestamp
            FROM news
            WHERE source = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """
            params = (source, limit)
        else:
            query = """
            SELECT title, source, url, description, published_at, timestamp
            FROM news
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
                        'source': row[1],
                        'url': row[2],
                        'description': row[3],
                        'published_at': row[4],
                        'timestamp': row[5]
                    } for row in rows]
        except Exception as e:
            logger.error(f"Error getting latest news: {e}")
            raise DatabaseError(f"Failed to get latest news: {e}")

    def delete_old_records(self, days: int = 30) -> int:
        """
        Delete news records older than specified days.

        Args:
            days: Number of days to retain (default 30 for news)

        Returns:
            Number of records deleted
        """
        delete_query = "DELETE FROM news WHERE timestamp < %s"
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(delete_query, (cutoff_date,))
                    deleted_count = cur.rowcount
                conn.commit()
            logger.info(f"Deleted {deleted_count} old news records")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old news records: {e}")
            raise DatabaseError(f"Failed to delete old records: {e}")
