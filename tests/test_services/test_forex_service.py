"""
Tests for ForexService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.forex_service import ForexService
from repositories.forex_repository import ForexRepository
from core.exceptions import APIError


class TestForexService:
    """Test suite for ForexService."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock forex repository."""
        return Mock(spec=ForexRepository)

    @pytest.fixture
    def service(self, mock_config, mock_repository):
        """Create a ForexService instance with mocked dependencies."""
        return ForexService(mock_config, mock_repository)

    @pytest.fixture
    def mock_forex_api_response(self):
        """Mock Alpha Vantage forex API response."""
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

    # =========================================================================
    # fetch_exchange_rate Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_exchange_rate_success(self, service, mock_forex_api_response):
        """Test successful exchange rate fetch."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_forex_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_exchange_rate('EUR', 'USD')

            assert result is not None
            assert result['pair'] == 'EUR/USD'
            assert result['from_currency'] == 'EUR'
            assert result['to_currency'] == 'USD'
            assert result['rate'] == 1.0850
            assert result['bid'] == 1.0848
            assert result['ask'] == 1.0852

    @pytest.mark.unit
    def test_fetch_exchange_rate_empty_response(self, service):
        """Test handling of empty API response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_exchange_rate('EUR', 'USD')

            assert result is None

    @pytest.mark.unit
    def test_fetch_exchange_rate_api_error(self, service):
        """Test handling of API error response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'Error Message': 'Invalid API call'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_exchange_rate('INVALID', 'USD')

            assert result is None

    @pytest.mark.unit
    def test_fetch_exchange_rate_network_error_retry(self, service, mock_forex_api_response):
        """Test network error handling with retry."""
        with patch('requests.get') as mock_get:
            import requests
            success_response = Mock()
            success_response.json.return_value = mock_forex_api_response
            success_response.raise_for_status = Mock()

            mock_get.side_effect = [
                requests.exceptions.ConnectionError("Network error"),
                success_response
            ]

            with patch('time.sleep'):
                result = service.fetch_exchange_rate('EUR', 'USD')

            assert result is not None
            assert result['rate'] == 1.0850

    # =========================================================================
    # fetch_multiple_exchange_rates Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_multiple_exchange_rates_success(self, service, mock_forex_api_response):
        """Test fetching multiple exchange rates."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_forex_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch('time.sleep'):
                results = service.fetch_multiple_exchange_rates([
                    {'from': 'EUR', 'to': 'USD'},
                    {'from': 'GBP', 'to': 'USD'}
                ])

            assert len(results) == 2

    # =========================================================================
    # collect_and_store_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_collect_and_store_data_success(self, service, mock_repository, mock_forex_api_response):
        """Test collecting and storing forex data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_forex_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_forex_data.return_value = 2

            with patch('time.sleep'):
                result = service.collect_and_store_data([
                    {'from': 'EUR', 'to': 'USD'},
                    {'from': 'GBP', 'to': 'USD'}
                ])

            assert result['successful'] == 2
            assert 'duration_seconds' in result
            mock_repository.insert_bulk_forex_data.assert_called_once()

    @pytest.mark.unit
    def test_collect_and_store_data_with_defaults(self, service, mock_repository, mock_forex_api_response):
        """Test collection using default currency pairs."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_forex_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_forex_data.return_value = len(ForexService.DEFAULT_PAIRS)

            with patch('time.sleep'):
                result = service.collect_and_store_data(None)

            assert result['total_pairs'] == len(ForexService.DEFAULT_PAIRS)

    # =========================================================================
    # get_latest_rates Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_latest_rates(self, service, mock_repository):
        """Test getting latest rates from repository."""
        mock_repository.get_all_latest_forex_rates.return_value = [
            {'pair': 'EUR/USD', 'rate': 1.0850},
            {'pair': 'GBP/USD', 'rate': 1.2650}
        ]

        result = service.get_latest_rates()

        assert len(result) == 2
        mock_repository.get_all_latest_forex_rates.assert_called_once()

    @pytest.mark.unit
    def test_get_latest_rates_empty(self, service, mock_repository):
        """Test getting latest rates when none exist."""
        mock_repository.get_all_latest_forex_rates.return_value = []

        result = service.get_latest_rates()

        assert result == []

    # =========================================================================
    # Helper Method Tests
    # =========================================================================

    @pytest.mark.unit
    def test_safe_float_valid(self, service):
        """Test _safe_float with valid input."""
        assert service._safe_float('1.0850') == 1.0850
        assert service._safe_float(100.5) == 100.5

    @pytest.mark.unit
    def test_safe_float_invalid(self, service):
        """Test _safe_float with invalid input."""
        assert service._safe_float(None) is None
        assert service._safe_float('') is None
        assert service._safe_float('invalid') is None
