"""
Base repository class with common database operations.
All domain-specific repositories inherit from this.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.database import db
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BaseRepository(ABC):
    """Abstract base repository with common CRUD operations"""
    
    def __init__(self, table_name: str):
        """
        Initialize repository with table name.
        
        Args:
            table_name: Name of the database table
        """
        self.table_name = table_name
        self.db = db
    
    def find_all(self, limit: int = 100, order_by: str = "timestamp DESC") -> pd.DataFrame:
        """
        Get all records from table.
        
        Args:
            limit: Maximum number of records to return
            order_by: SQL ORDER BY clause
            
        Returns:
            DataFrame with results
        """
        query = f"SELECT * FROM {self.table_name} ORDER BY {order_by} LIMIT %s"
        
        try:
            with self.db.get_connection() as conn:
                return pd.read_sql(query, conn, params=(limit,))
        except Exception as e:
            logger.error(f"Error in find_all for {self.table_name}: {e}")
            return pd.DataFrame()
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Find single record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Dictionary with record data or None
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        return self.db.execute_query(query, (id,), fetch_one=True)
    
    def count(self) -> int:
        """
        Count total records in table.
        
        Returns:
            Total count
        """
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        result = self.db.execute_query(query, fetch_one=True)
        return result['count'] if result else 0
    
    def insert(self, data: Dict[str, Any]) -> Optional[int]:
        """
        Insert single record.
        
        Args:
            data: Dictionary of column names and values
            
        Returns:
            ID of inserted record
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id"
        
        try:
            return self.db.execute_insert(query, tuple(data.values()))
        except Exception as e:
            logger.error(f"Error inserting into {self.table_name}: {e}")
            return None
    
    def bulk_insert(self, records: List[Dict[str, Any]]) -> bool:
        """
        Insert multiple records efficiently.
        
        Args:
            records: List of dictionaries with record data
            
        Returns:
            True if successful, False otherwise
        """
        if not records:
            return True
        
        columns = ', '.join(records[0].keys())
        placeholders = ', '.join(['%s'] * len(records[0]))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        params_list = [tuple(record.values()) for record in records]
        
        try:
            self.db.execute_many(query, params_list)
            logger.info(f"Bulk inserted {len(records)} records into {self.table_name}")
            return True
        except Exception as e:
            logger.error(f"Error in bulk insert to {self.table_name}: {e}")
            return False
    
    def update(self, id: int, data: Dict[str, Any]) -> bool:
        """
        Update single record by ID.
        
        Args:
            id: Record ID
            data: Dictionary of columns to update
            
        Returns:
            True if successful, False otherwise
        """
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
        
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, tuple(data.values()) + (id,))
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating {self.table_name} id {id}: {e}")
            return False
    
    def delete(self, id: int) -> bool:
        """
        Delete single record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if successful, False otherwise
        """
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (id,))
                    return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting from {self.table_name} id {id}: {e}")
            return False
    
    def delete_old_records(self, days: int = 90) -> int:
        """
        Delete records older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of records deleted
        """
        query = f"DELETE FROM {self.table_name} WHERE timestamp < NOW() - INTERVAL '%s days'"
        
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (days,))
                    deleted_count = cursor.rowcount
                    logger.info(f"Deleted {deleted_count} old records from {self.table_name}")
                    return deleted_count
        except Exception as e:
            logger.error(f"Error deleting old records from {self.table_name}: {e}")
            return 0
    
    @abstractmethod
    def get_latest(self):
        """
        Get latest records - must be implemented by subclass.
        Each domain has different logic for "latest".
        """
        pass
