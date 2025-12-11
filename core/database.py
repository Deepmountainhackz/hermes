"""
Database Manager
Handles database connections with connection pooling.
"""
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from contextlib import contextmanager
from typing import Generator, Optional, List, Any
import logging
import atexit

from .config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections with connection pooling.

    Uses psycopg3's ConnectionPool for efficient connection management.
    The pool is initialized lazily on first use and cleaned up at exit.
    """

    # Class-level pool for sharing across instances with same config
    _pools: dict = {}

    def __init__(self, config: Config):
        """
        Initialize database manager.

        Args:
            config: Configuration instance with database settings
        """
        self.config = config
        self._pool_key = self._get_pool_key()

    def _get_pool_key(self) -> str:
        """Generate a unique key for the connection pool based on config."""
        return f"{self.config.DATABASE_HOST}:{self.config.DATABASE_PORT}/{self.config.DATABASE_NAME}"

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

    def _get_pool(self) -> ConnectionPool:
        """
        Get or create the connection pool.

        Returns:
            ConnectionPool instance
        """
        if self._pool_key not in DatabaseManager._pools:
            logger.info(f"Creating connection pool for {self._pool_key}")
            pool = ConnectionPool(
                conninfo=self.get_connection_string(),
                min_size=2,
                max_size=10,
                kwargs={"row_factory": dict_row},
                open=True
            )
            DatabaseManager._pools[self._pool_key] = pool

            # Register cleanup at exit
            atexit.register(self._cleanup_pool)

        return DatabaseManager._pools[self._pool_key]

    def _cleanup_pool(self) -> None:
        """Clean up the connection pool on shutdown."""
        if self._pool_key in DatabaseManager._pools:
            try:
                DatabaseManager._pools[self._pool_key].close()
                del DatabaseManager._pools[self._pool_key]
                logger.info(f"Connection pool closed for {self._pool_key}")
            except Exception as e:
                logger.warning(f"Error closing connection pool: {e}")

    @contextmanager
    def get_connection(self) -> Generator:
        """
        Get a database connection from the pool as a context manager.

        The connection is automatically returned to the pool when the
        context manager exits.

        Yields:
            Database connection

        Example:
            with db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM table")
        """
        pool = self._get_pool()
        conn = None
        try:
            conn = pool.getconn()
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                pool.putconn(conn)

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

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Any]:
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

    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
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

    def get_pool_stats(self) -> dict:
        """
        Get connection pool statistics.

        Returns:
            Dictionary with pool statistics
        """
        try:
            pool = self._get_pool()
            return {
                'pool_key': self._pool_key,
                'min_size': pool.min_size,
                'max_size': pool.max_size,
                'size': pool.get_stats().get('pool_size', 0),
                'available': pool.get_stats().get('pool_available', 0),
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            return {'error': str(e)}
