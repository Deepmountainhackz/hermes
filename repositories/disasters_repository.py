"""Disasters Repository."""
from typing import List, Dict
from datetime import datetime
import logging
from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class DisastersRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_tables(self):
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
    
    def insert_bulk_disaster_data(self, disaster_data_list: List[Dict]) -> int:
        if not disaster_data_list:
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
            return len(disaster_data_list)
        except Exception as e:
            raise DatabaseError(f"Failed to insert disaster data: {e}")
