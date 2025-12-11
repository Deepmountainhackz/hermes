"""News Repository."""
from typing import List, Dict
from datetime import datetime
import logging
from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class NewsRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_tables(self):
        """Create the news table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500),
            source VARCHAR(100),
            url TEXT,
            description TEXT,
            published_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_news_source ON news(source);
        CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news(timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("News table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating news table: {e}")
            raise DatabaseError(f"Failed to create news table: {e}")
    
    def insert_bulk_news_data(self, news_data_list: List[Dict]) -> int:
        if not news_data_list:
            return 0
        
        insert_query = """
        INSERT INTO news (title, source, url, description, published_at, timestamp)
        VALUES (%(title)s, %(source)s, %(url)s, %(description)s, %(published_at)s, %(timestamp)s)
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in news_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            return len(news_data_list)
        except Exception as e:
            raise DatabaseError(f"Failed to insert news data: {e}")
