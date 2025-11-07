"""
Database connection manager for Hermes Intelligence Platform
Uses PostgreSQL with psycopg version 3 (Python 3.13 compatible)
"""

import os
import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Get PostgreSQL database connection using psycopg version 3
    Uses DATABASE_URL from environment variables
    """
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Connect using psycopg version 3
    conn = psycopg.connect(database_url)
    
    return conn

@contextmanager
def get_db_connection_context():
    """
    Context manager for database connections
    Automatically handles commit/rollback and close
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# For backwards compatibility with collectors using 'with get_db_connection() as conn'
# This makes get_db_connection() work as a context manager
class DatabaseConnection:
    def __init__(self):
        self.conn = None
    
    def __enter__(self):
        self.conn = get_db_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
        return False

# Monkey patch to make the function work as context manager
_original_get_db_connection = get_db_connection

def get_db_connection():
    """Get database connection - works both as function and context manager"""
    class ConnectionContextManager:
        def __init__(self):
            self.conn = None
        
        def __enter__(self):
            self.conn = _original_get_db_connection()
            return self.conn
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
            return False
    
    return ConnectionContextManager()
