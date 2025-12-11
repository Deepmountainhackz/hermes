"""
Tests for MarketsService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.markets_service import MarketsService
from repositories.markets_repository import MarketsRepository
from core.exceptions import APIError


class TestMarketsService:
    """Test suite for MarketsService."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock markets repository."""
        return Mock(spec=MarketsRepository)

    @pytest.fixture
    def service(self, mock_config, mock_repository):
        """Create a MarketsService instance with mocked dependencies."""
        return MarketsService(mock_config, mock_repository)

    # =========================================================================
    # fetch_quote Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_quote_success(self, service, mock_alpha_vantage_quote_response):
        """Test successful stock quote fetch."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_alpha_vantage_quote_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_quote('AAPL')

            assert result is not None
            assert result['symbol'] == 'AAPL'
            assert result['price'] == 175.50
            assert result['change'] == 2.30

    @pytest.mark.unit
    def test_fetch_quote_empty_response(self, service):
        """Test handling of empty API response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'Global Quote': {}}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_quote('INVALID')

            assert result is None

    @pytest.mark.unit
    def test_fetch_quote_api_error(self, service, mock_alpha_vantage_error_response):
        """Test handling of API error response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_alpha_vantage_error_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_quote('AAPL')

            assert result is None

    @pytest.mark.unit
    def test_fetch_quote_rate_limit_retry(self, service, mock_alpha_vantage_rate_limit_response, mock_alpha_vantage_quote_response):
        """Test rate limit handling with retry."""
        with patch('requests.get') as mock_get:
            # First call returns rate limit, second call succeeds
            rate_limit_response = Mock()
            rate_limit_response.json.return_value = mock_alpha_vantage_rate_limit_response
            rate_limit_response.raise_for_status = Mock()

            success_response = Mock()
            success_response.json.return_value = mock_alpha_vantage_quote_response
            success_response.raise_for_status = Mock()

            mock_get.side_effect = [rate_limit_response, success_response]

            with patch('time.sleep'):  # Skip actual sleep
                result = service.fetch_quote('AAPL')

            assert result is not None
            assert result['symbol'] == 'AAPL'

    @pytest.mark.unit
    def test_fetch_quote_network_error_retry(self, service, mock_alpha_vantage_quote_response):
        """Test network error handling with retry."""
        with patch('requests.get') as mock_get:
            import requests
            # First call fails, second succeeds
            success_response = Mock()
            success_response.json.return_value = mock_alpha_vantage_quote_response
            success_response.raise_for_status = Mock()

            mock_get.side_effect = [
                requests.exceptions.ConnectionError("Network error"),
                success_response
            ]

            with patch('time.sleep'):
                result = service.fetch_quote('AAPL')

            assert result is not None

    # =========================================================================
    # fetch_multiple_quotes Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_multiple_quotes_success(self, service, mock_alpha_vantage_quote_response):
        """Test fetching multiple quotes."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_alpha_vantage_quote_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch('time.sleep'):
                results = service.fetch_multiple_quotes(['AAPL', 'MSFT'])

            assert len(results) == 2

    # =========================================================================
    # collect_and_store_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_collect_and_store_data_success(self, service, mock_repository, mock_alpha_vantage_quote_response):
        """Test collecting and storing market data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_alpha_vantage_quote_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_stock_data.return_value = 3

            with patch('time.sleep'):
                result = service.collect_and_store_data(['AAPL', 'MSFT', 'GOOGL'])

            assert result['successful'] > 0
            assert 'duration_seconds' in result
            mock_repository.insert_bulk_stock_data.assert_called_once()

    @pytest.mark.unit
    def test_collect_and_store_data_with_default_symbols(self, service, mock_repository, mock_alpha_vantage_quote_response):
        """Test collection using default symbols."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_alpha_vantage_quote_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_stock_data.return_value = len(MarketsService.DEFAULT_SYMBOLS)

            with patch('time.sleep'):
                result = service.collect_and_store_data(None)

            assert result['total_stocks'] == len(MarketsService.DEFAULT_SYMBOLS)

    # =========================================================================
    # get_latest_stocks Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_latest_stocks(self, service, mock_repository, sample_stock_list):
        """Test getting latest stocks from repository."""
        mock_repository.get_all_latest_stocks.return_value = sample_stock_list

        result = service.get_latest_stocks()

        assert len(result) == 3
        mock_repository.get_all_latest_stocks.assert_called_once()

    @pytest.mark.unit
    def test_get_latest_stocks_empty(self, service, mock_repository):
        """Test getting latest stocks when none exist."""
        mock_repository.get_all_latest_stocks.return_value = []

        result = service.get_latest_stocks()

        assert result == []

    # =========================================================================
    # Helper Method Tests
    # =========================================================================

    @pytest.mark.unit
    def test_safe_float_valid(self, service):
        """Test _safe_float with valid input."""
        assert service._safe_float('123.45') == 123.45
        assert service._safe_float(100) == 100.0

    @pytest.mark.unit
    def test_safe_float_invalid(self, service):
        """Test _safe_float with invalid input."""
        assert service._safe_float(None) is None
        assert service._safe_float('') is None
        assert service._safe_float('.') is None
        assert service._safe_float('invalid') is None

    @pytest.mark.unit
    def test_safe_int_valid(self, service):
        """Test _safe_int with valid input."""
        assert service._safe_int('12345') == 12345
        assert service._safe_int(100) == 100

    @pytest.mark.unit
    def test_safe_int_invalid(self, service):
        """Test _safe_int with invalid input."""
        assert service._safe_int(None) is None
        assert service._safe_int('') is None
        assert service._safe_int('invalid') is None
