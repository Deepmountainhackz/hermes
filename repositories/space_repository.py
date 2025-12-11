"""Space Repository."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class SpaceRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_tables(self):
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
    
    def insert_bulk_space_data(self, space_data_list: List[Dict]) -> int:
        if not space_data_list:
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
            return len(space_data_list)
        except Exception as e:
            raise DatabaseError(f"Failed to insert space data: {e}")
