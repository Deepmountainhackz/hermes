"""
Pytest Configuration and Fixtures
Shared fixtures for all tests in the Hermes Intelligence Platform.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List

from core.config import Config
from core.database import DatabaseManager


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock(spec=Config)
    config.DATABASE_HOST = 'localhost'
    config.DATABASE_PORT = 5432
    config.DATABASE_NAME = 'test_hermes'
    config.DATABASE_USER = 'test_user'
    config.DATABASE_PASSWORD = 'test_password'
    config.ALPHA_VANTAGE_API_KEY = 'test_alpha_vantage_key'
    config.OPENWEATHER_API_KEY = 'test_openweather_key'
    config.NASA_API_KEY = 'test_nasa_key'
    config.NEWSAPI_KEY = 'test_news_key'
    config.API_TIMEOUT = 15
    config.API_MAX_RETRIES = 3
    config.API_RETRY_DELAY = 2
    config.ALPHA_VANTAGE_RATE_LIMIT_DELAY = 12
    config.DEFAULT_RATE_LIMIT_DELAY = 1
    config.DATA_RETENTION_DAYS = 365
    return config


@pytest.fixture
def test_config():
    """Create a real Config instance for integration tests."""
    return Config()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db_manager(mock_config):
    """Create a mock database manager."""
    db_manager = Mock(spec=DatabaseManager)
    db_manager.config = mock_config
    return db_manager


@pytest.fixture
def mock_connection():
    """Create a mock database connection."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
    conn.cursor.return_value.__exit__ = Mock(return_value=None)
    return conn, cursor


@pytest.fixture
def mock_db_manager_with_connection(mock_db_manager, mock_connection):
    """Create a mock database manager with connection context manager."""
    conn, cursor = mock_connection
    mock_db_manager.get_connection.return_value.__enter__ = Mock(return_value=conn)
    mock_db_manager.get_connection.return_value.__exit__ = Mock(return_value=None)
    return mock_db_manager, conn, cursor


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_stock_data() -> Dict[str, Any]:
    """Sample stock data for testing."""
    return {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'price': 175.50,
        'change': 2.30,
        'change_percent': 1.33,
        'volume': 50000000,
        'market_cap': 2800000000000,
        'timestamp': datetime.now()
    }


@pytest.fixture
def sample_stock_list() -> List[Dict[str, Any]]:
    """Sample list of stock data for testing."""
    return [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'change': 2.30, 'change_percent': 1.33, 'timestamp': datetime.now()},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'price': 380.20, 'change': -1.50, 'change_percent': -0.39, 'timestamp': datetime.now()},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 140.80, 'change': 0.90, 'change_percent': 0.64, 'timestamp': datetime.now()},
    ]


@pytest.fixture
def sample_forex_data() -> Dict[str, Any]:
    """Sample forex data for testing."""
    return {
        'pair': 'EUR/USD',
        'from_currency': 'EUR',
        'to_currency': 'USD',
        'rate': 1.0850,
        'bid': 1.0848,
        'ask': 1.0852,
        'timestamp': datetime.now()
    }


@pytest.fixture
def sample_weather_data() -> Dict[str, Any]:
    """Sample weather data for testing."""
    return {
        'city': 'London',
        'country': 'GB',
        'temperature': 15.5,
        'feels_like': 14.0,
        'humidity': 75,
        'pressure': 1013,
        'wind_speed': 5.5,
        'description': 'partly cloudy',
        'timestamp': datetime.now()
    }


@pytest.fixture
def sample_commodity_data() -> Dict[str, Any]:
    """Sample commodity data for testing."""
    return {
        'symbol': 'WTI',
        'name': 'WTI Crude Oil',
        'price': 75.50,
        'change': 1.20,
        'change_percent': 1.61,
        'unit': 'USD/barrel',
        'timestamp': datetime.now()
    }


@pytest.fixture
def sample_economic_indicator() -> Dict[str, Any]:
    """Sample economic indicator data for testing."""
    return {
        'indicator': 'GDP',
        'country': 'USA',
        'name': 'Gross Domestic Product',
        'value': 25000.0,
        'unit': 'Billions USD',
        'timestamp': datetime.now()
    }


# ============================================================================
# API Response Fixtures
# ============================================================================

@pytest.fixture
def mock_alpha_vantage_quote_response() -> Dict[str, Any]:
    """Mock Alpha Vantage GLOBAL_QUOTE response."""
    return {
        'Global Quote': {
            '01. symbol': 'AAPL',
            '02. open': '174.50',
            '03. high': '176.00',
            '04. low': '174.00',
            '05. price': '175.50',
            '06. volume': '50000000',
            '07. latest trading day': '2024-01-15',
            '08. previous close': '173.20',
            '09. change': '2.30',
            '10. change percent': '1.33%'
        }
    }


@pytest.fixture
def mock_alpha_vantage_forex_response() -> Dict[str, Any]:
    """Mock Alpha Vantage CURRENCY_EXCHANGE_RATE response."""
    return {
        'Realtime Currency Exchange Rate': {
            '1. From_Currency Code': 'EUR',
            '2. From_Currency Name': 'Euro',
            '3. To_Currency Code': 'USD',
            '4. To_Currency Name': 'United States Dollar',
            '5. Exchange Rate': '1.0850',
            '6. Last Refreshed': '2024-01-15 12:00:00',
            '7. Time Zone': 'UTC',
            '8. Bid Price': '1.0848',
            '9. Ask Price': '1.0852'
        }
    }


@pytest.fixture
def mock_openweather_response() -> Dict[str, Any]:
    """Mock OpenWeatherMap API response."""
    return {
        'name': 'London',
        'sys': {'country': 'GB'},
        'main': {
            'temp': 15.5,
            'feels_like': 14.0,
            'humidity': 75,
            'pressure': 1013
        },
        'wind': {'speed': 5.5},
        'weather': [{'description': 'partly cloudy'}]
    }


@pytest.fixture
def mock_alpha_vantage_rate_limit_response() -> Dict[str, Any]:
    """Mock Alpha Vantage rate limit response."""
    return {
        'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day.'
    }


@pytest.fixture
def mock_alpha_vantage_error_response() -> Dict[str, Any]:
    """Mock Alpha Vantage error response."""
    return {
        'Error Message': 'Invalid API call. Please retry or visit the documentation.'
    }


# ============================================================================
# HTTP Request Mocking Helpers
# ============================================================================

@pytest.fixture
def mock_requests_get():
    """Create a mock for requests.get."""
    with patch('requests.get') as mock_get:
        yield mock_get


def create_mock_response(json_data: Dict[str, Any], status_code: int = 200):
    """Helper to create a mock response object."""
    mock_response = Mock()
    mock_response.json.return_value = json_data
    mock_response.status_code = status_code
    mock_response.raise_for_status = Mock()
    if status_code >= 400:
        mock_response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return mock_response
