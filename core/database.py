"""
Database Manager
Handles database connections with connection pooling.
"""
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from typing import Generator
import logging

from .config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections with pooling."""
    
    def __init__(self, config: Config):
        """
        Initialize database manager.
        
        Args:
            config: Configuration instance with database settings
        """
        self.config = config
        self._connection_pool = None
        
    def get_connection_string(self) -> str:
        """
        Build PostgreSQL connection string.
        
        Returns:
            Connection string
        """
        return (
            f"host={self.config.DATABASE_HOST} "
            f"port={self.config.DATABASE_PORT} "
            f"dbname={self.config.DATABASE_NAME} "
            f"user={self.config.DATABASE_USER} "
            f"password={self.config.DATABASE_PASSWORD}"
        )
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Get a database connection as a context manager.
        
        Yields:
            Database connection
            
        Example:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = psycopg.connect(
                self.get_connection_string(),
                row_factory=dict_row
            )
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result rows
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE command.
        
        Args:
            command: SQL command
            params: Command parameters
            
        Returns:
            Number of affected rows
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(command, params or ())
                    affected = cur.rowcount
                conn.commit()
                return affected
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise
