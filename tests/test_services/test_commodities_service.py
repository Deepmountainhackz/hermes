"""
Tests for CommoditiesService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.commodities_service import CommoditiesService
from repositories.commodities_repository import CommoditiesRepository
from core.exceptions import APIError


class TestCommoditiesService:
    """Test suite for CommoditiesService."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock commodities repository."""
        return Mock(spec=CommoditiesRepository)

    @pytest.fixture
    def service(self, mock_config, mock_repository):
        """Create a CommoditiesService instance with mocked dependencies."""
        return CommoditiesService(mock_config, mock_repository)

    @pytest.fixture
    def mock_commodity_api_response(self):
        """Mock Alpha Vantage commodity API response."""
        return {
            'name': 'Crude Oil Prices WTI',
            'unit': 'dollars per barrel',
            'data': [
                {'date': '2024-01-15', 'value': '72.50'},
                {'date': '2024-01-14', 'value': '71.80'},
                {'date': '2024-01-13', 'value': '72.10'}
            ]
        }

    # =========================================================================
    # fetch_commodity_price Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_commodity_price_success(self, service, mock_commodity_api_response):
        """Test successful commodity price fetch."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_commodity_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_commodity_price('WTI')

            assert result is not None
            assert result['commodity'] == 'WTI'
            assert result['price'] == 72.50
            assert result['name'] == 'WTI Crude Oil'

    @pytest.mark.unit
    def test_fetch_commodity_price_empty_response(self, service):
        """Test handling of empty API response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'data': []}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_commodity_price('WTI')

            assert result is None

    @pytest.mark.unit
    def test_fetch_commodity_price_api_error(self, service):
        """Test handling of API error response."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'Error Message': 'Invalid API call'}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_commodity_price('INVALID')

            assert result is None

    @pytest.mark.unit
    def test_fetch_commodity_price_network_error_retry(self, service, mock_commodity_api_response):
        """Test network error handling with retry."""
        with patch('requests.get') as mock_get:
            import requests
            success_response = Mock()
            success_response.json.return_value = mock_commodity_api_response
            success_response.raise_for_status = Mock()

            mock_get.side_effect = [
                requests.exceptions.ConnectionError("Network error"),
                success_response
            ]

            with patch('time.sleep'):
                result = service.fetch_commodity_price('WTI')

            assert result is not None
            assert result['price'] == 72.50

    # =========================================================================
    # _get_function_for_commodity Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_function_for_commodity(self, service):
        """Test getting API function for different commodities."""
        assert service._get_function_for_commodity('WTI') == 'WTI'
        assert service._get_function_for_commodity('BRENT') == 'BRENT'
        assert service._get_function_for_commodity('NATURAL_GAS') == 'NATURAL_GAS'
        assert service._get_function_for_commodity('UNKNOWN') == 'WTI'  # Default

    # =========================================================================
    # fetch_multiple_commodities Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_multiple_commodities_success(self, service, mock_commodity_api_response):
        """Test fetching multiple commodities."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_commodity_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            with patch('time.sleep'):
                results = service.fetch_multiple_commodities(['WTI', 'BRENT'])

            assert len(results) == 2

    # =========================================================================
    # collect_and_store_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_collect_and_store_data_success(self, service, mock_repository, mock_commodity_api_response):
        """Test collecting and storing commodity data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_commodity_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_commodity_data.return_value = 2

            with patch('time.sleep'):
                result = service.collect_and_store_data(['WTI', 'BRENT'])

            assert result['successful'] == 2
            assert 'duration_seconds' in result
            mock_repository.insert_bulk_commodity_data.assert_called_once()

    @pytest.mark.unit
    def test_collect_and_store_data_with_defaults(self, service, mock_repository, mock_commodity_api_response):
        """Test collection using default commodities."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_commodity_api_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_commodity_data.return_value = len(CommoditiesService.DEFAULT_COMMODITIES)

            with patch('time.sleep'):
                result = service.collect_and_store_data(None)

            assert result['total_commodities'] == len(CommoditiesService.DEFAULT_COMMODITIES)

    # =========================================================================
    # get_latest_prices Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_latest_prices(self, service, mock_repository):
        """Test getting latest prices from repository."""
        mock_repository.get_all_latest_commodities.return_value = [
            {'commodity': 'WTI', 'price': 72.50},
            {'commodity': 'BRENT', 'price': 77.80}
        ]

        result = service.get_latest_prices()

        assert len(result) == 2
        mock_repository.get_all_latest_commodities.assert_called_once()

    @pytest.mark.unit
    def test_get_latest_prices_empty(self, service, mock_repository):
        """Test getting latest prices when none exist."""
        mock_repository.get_all_latest_commodities.return_value = []

        result = service.get_latest_prices()

        assert result == []

    # =========================================================================
    # get_commodity_with_history Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_commodity_with_history(self, service, mock_repository):
        """Test getting commodity with history."""
        mock_repository.get_latest_commodity_price.return_value = {'commodity': 'WTI', 'price': 72.50}
        mock_repository.get_commodity_history.return_value = [
            {'date': '2024-01-15', 'price': 72.50},
            {'date': '2024-01-14', 'price': 71.80}
        ]

        result = service.get_commodity_with_history('WTI', days=7)

        assert result is not None
        assert 'current' in result
        assert 'history' in result

    @pytest.mark.unit
    def test_get_commodity_with_history_not_found(self, service, mock_repository):
        """Test getting commodity with history when not found."""
        mock_repository.get_latest_commodity_price.return_value = None

        result = service.get_commodity_with_history('INVALID', days=7)

        assert result is None

    # =========================================================================
    # get_sparkline_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_sparkline_data(self, service, mock_repository):
        """Test getting sparkline data."""
        mock_repository.get_price_history_for_sparkline.return_value = [72.50, 71.80, 72.10]

        result = service.get_sparkline_data('WTI', days=7)

        assert result == [72.50, 71.80, 72.10]
        mock_repository.get_price_history_for_sparkline.assert_called_once_with('WTI', 7)

    @pytest.mark.unit
    def test_get_sparkline_data_error(self, service, mock_repository):
        """Test sparkline data with error returns empty list."""
        mock_repository.get_price_history_for_sparkline.side_effect = Exception("DB error")

        result = service.get_sparkline_data('WTI', days=7)

        assert result == []

    # =========================================================================
    # Helper Method Tests
    # =========================================================================

    @pytest.mark.unit
    def test_safe_float_valid(self, service):
        """Test _safe_float with valid input."""
        assert service._safe_float('72.50') == 72.50
        assert service._safe_float(100.5) == 100.5

    @pytest.mark.unit
    def test_safe_float_invalid(self, service):
        """Test _safe_float with invalid input."""
        assert service._safe_float(None) is None
        assert service._safe_float('') is None
        assert service._safe_float('invalid') is None
