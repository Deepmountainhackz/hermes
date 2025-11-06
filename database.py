"""
PostgreSQL Database Connection Utility
Centralized database connection management for Hermes
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import Optional
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """Get database URL from environment"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return db_url

@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    
    Usage:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM stocks")
                results = cur.fetchall()
    """
    conn = None
    try:
        db_url = get_database_url()
        conn = psycopg2.connect(db_url)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """
    Execute a SQL query
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch: Whether to fetch results (default True)
        
    Returns:
        Query results if fetch=True, None otherwise
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            return None

def insert_data(table: str, data: dict):
    """
    Insert data into a table
    
    Args:
        table: Table name
        data: Dictionary of column: value pairs
    """
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(data.values()))

def table_exists(table_name: str) -> bool:
    """Check if a table exists"""
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
    """
    result = execute_query(query, (table_name,))
    return result[0]['exists'] if result else False
