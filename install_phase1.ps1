# Phase 1 Setup Script for Hermes Platform
Write-Host "Creating Phase 1 files..." -ForegroundColor Cyan

# config/settings.py
$content = @'
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    APP_NAME: str = "Hermes Intelligence Platform"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    DB_HOST: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int = 5432
    
    ALPHA_VANTAGE_API_KEY: str
    OPENWEATHER_API_KEY: str
    NASA_API_KEY: str = "DEMO_KEY"
    NEWS_API_KEY: str
    USDA_NASS_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    COLLECTION_INTERVAL_HOURS: int = 2
    HISTORICAL_DATA_RETENTION_DAYS: int = 90
    CACHE_TTL_SECONDS: int = 300
    API_RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

settings = Settings()
'@
[System.IO.File]::WriteAllText("$PWD\config\settings.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ config/settings.py" -ForegroundColor Green

# config/tracked_assets.py
$content = @'
TRACKED_STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'JPM', 'GS', 
    'CVX', 'JNJ', 'UNH', 'PG', 'V', 'WMT', 'XOM'
]

TRACKED_COMMODITIES = [
    {'symbol': 'CL=F', 'name': 'WTI Crude Oil'},
    {'symbol': 'BZ=F', 'name': 'Brent Crude Oil'},
    {'symbol': 'NG=F', 'name': 'Natural Gas'},
    {'symbol': 'GC=F', 'name': 'Gold'},
    {'symbol': 'SI=F', 'name': 'Silver'},
    {'symbol': 'HG=F', 'name': 'Copper'},
]

TRACKED_FOREX_PAIRS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 
    'AUDUSD=X', 'USDCAD=X'
]

TRACKED_ECONOMIC_INDICATORS = {
    'US': ['GDP', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS', 'INDPRO']
}

TRACKED_WEATHER_CITIES = [
    {'name': 'New York', 'country': 'US', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'London', 'country': 'GB', 'lat': 51.5074, 'lon': -0.1278},
    {'name': 'Tokyo', 'country': 'JP', 'lat': 35.6762, 'lon': 139.6503},
]

TRACKED_CROPS = ['CORN', 'SOYBEANS', 'WHEAT', 'COTTON', 'RICE']

MAJOR_AG_REGIONS = {
    'US_Corn_Belt': {'lat': 41.5, 'lon': -93.5, 'name': 'US Corn Belt'},
    'Brazil_Cerrado': {'lat': -15.8, 'lon': -47.9, 'name': 'Brazilian Cerrado'},
}
'@
[System.IO.File]::WriteAllText("$PWD\config\tracked_assets.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ config/tracked_assets.py" -ForegroundColor Green

# config/alert_rules.py
$content = @'
ALERT_RULES = {
    'markets': {
        'sp500_daily_change': {'high': 3.0, 'medium': 2.0},
        'vix_level': {'high': 30, 'medium': 25},
    },
    
    'commodities': {
        'oil_daily_change': {'high': 5.0, 'medium': 3.0},
        'wheat_weekly_change': {'high': 10.0, 'medium': 7.0},
    },
    
    'economics': {
        'unemployment_change': {'high': 0.3, 'medium': 0.2},
        'inflation_rate': {'high': 5.0, 'medium': 3.5},
    },
    
    'weather': {
        'extreme_temp_high': 40,
        'extreme_temp_low': -20,
        'storm_count_24h': 3,
    },
    
    'disasters': {
        'earthquake_magnitude': {'high': 6.0, 'medium': 5.0},
        'wildfire_count_weekly': {'high': 10, 'medium': 5},
    },
    
    'agriculture': {
        'yield_change_yoy': {'high': -15, 'medium': -10},
        'production_change_yoy': {'high': -20, 'medium': -15},
    }
}
'@
[System.IO.File]::WriteAllText("$PWD\config\alert_rules.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ config/alert_rules.py" -ForegroundColor Green

# core/exceptions.py
$content = @'
class HermesException(Exception):
    """Base exception for all Hermes-specific errors"""
    pass

class DataCollectionError(HermesException):
    """Raised when data collection fails"""
    pass

class DataValidationError(HermesException):
    """Raised when data validation fails"""
    pass

class DatabaseError(HermesException):
    """Raised when database operations fail"""
    pass

class APIError(HermesException):
    """Raised when external API calls fail"""
    pass

class ConfigurationError(HermesException):
    """Raised when configuration is invalid"""
    pass
'@
[System.IO.File]::WriteAllText("$PWD\core\exceptions.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ core/exceptions.py" -ForegroundColor Green

# core/logging_config.py
$content = @'
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    
    handlers = [console_handler]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        handlers.append(file_handler)
    
    logging.basicConfig(level=log_level, handlers=handlers, force=True)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at {log_level} level")
'@
[System.IO.File]::WriteAllText("$PWD\core\logging_config.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ core/logging_config.py" -ForegroundColor Green

# core/cache.py
$content = @'
import streamlit as st
from typing import Callable
import logging

logger = logging.getLogger(__name__)

def cache_data(ttl: int = 300, show_spinner: bool = True):
    def decorator(func: Callable) -> Callable:
        return st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
    return decorator

def cache_resource(show_spinner: bool = False):
    def decorator(func: Callable) -> Callable:
        return st.cache_resource(show_spinner=show_spinner)(func)
    return decorator

def clear_all_caches():
    st.cache_data.clear()
    st.cache_resource.clear()
    logger.info("All caches cleared")
'@
[System.IO.File]::WriteAllText("$PWD\core\cache.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ core/cache.py" -ForegroundColor Green

# core/database.py
$content = @'
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
'@
[System.IO.File]::WriteAllText("$PWD\core\database.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ core/database.py" -ForegroundColor Green

# test_config_quick.py
$content = @'
from config.settings import settings

print("\n" + "="*60)
print("CONFIGURATION TEST")
print("="*60)
print(f"App Name: {settings.APP_NAME}")
print(f"Database Host: {settings.DB_HOST}")
print(f"Database Name: {settings.DB_NAME}")
print(f"Database User: {settings.DB_USER}")
print(f"Database Port: {settings.DB_PORT}")
print(f"Log Level: {settings.LOG_LEVEL}")
print("="*60)
print("✓ Configuration loaded successfully!")
print("="*60 + "\n")
'@
[System.IO.File]::WriteAllText("$PWD\test_config_quick.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ test_config_quick.py" -ForegroundColor Green

# test_db_quick.py
$content = @'
from core.database import db
from config.settings import settings

print("\n" + "="*60)
print("DATABASE CONNECTION TEST")
print("="*60)

try:
    print(f"Connecting to: {settings.DB_HOST}...")
    
    if db.health_check():
        print("✓ Database connection successful!")
        
        result = db.execute_query("SELECT version()", fetch_one=True)
        print(f"✓ PostgreSQL Version: {result['version'][:50]}...")
        
        print("="*60)
        print("✓ ALL DATABASE TESTS PASSED!")
        print("="*60 + "\n")
    else:
        print("✗ Database health check failed")
        
except Exception as e:
    print(f"✗ Database error: {e}")
    print("\nCheck your .env credentials!")
'@
[System.IO.File]::WriteAllText("$PWD\test_db_quick.py", $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "✓ test_db_quick.py" -ForegroundColor Green

Write-Host "`nAll files created successfully!" -ForegroundColor Cyan
Write-Host "Run: python test_config_quick.py" -ForegroundColor Yellow
