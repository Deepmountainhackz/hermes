import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _pool: Optional[SimpleConnectionPool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        from config.settings import settings
        
        try:
            self._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=settings.DB_HOST,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                port=settings.DB_PORT
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, return_dict: bool = True):
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if return_dict else None
            with conn.cursor(cursor_factory=cursor_factory) as cursor:
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result and return_dict else result
                else:
                    results = cursor.fetchall()
                    return [dict(row) for row in results] if return_dict else results
    
    def execute_insert(self, query: str, params: tuple, return_id: bool = True):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if return_id:
                    result = cursor.fetchone()
                    return result[0] if result else None
    
    def execute_many(self, query: str, params_list: List[tuple]):
        if not params_list:
            return
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                logger.info(f"Batch operation completed: {cursor.rowcount} rows affected")
    
    def health_check(self) -> bool:
        try:
            result = self.execute_query("SELECT 1", fetch_one=True)
            return result is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close_all_connections(self):
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")

db = DatabaseManager()
