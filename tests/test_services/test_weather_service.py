"""
Tests for WeatherService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from services.weather_service import WeatherService
from repositories.weather_repository import WeatherRepository


class TestWeatherService:
    """Test suite for WeatherService."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock weather repository."""
        return Mock(spec=WeatherRepository)

    @pytest.fixture
    def service(self, mock_config, mock_repository):
        """Create a WeatherService instance with mocked dependencies."""
        return WeatherService(mock_config, mock_repository)

    # =========================================================================
    # fetch_weather Tests
    # =========================================================================

    @pytest.mark.unit
    def test_fetch_weather_success(self, service, mock_openweather_response):
        """Test successful weather fetch."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_openweather_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = service.fetch_weather('London')

            assert result is not None
            assert result['city'] == 'London'
            assert result['temperature'] == 15.5
            assert result['humidity'] == 75
            assert result['description'] == 'partly cloudy'

    @pytest.mark.unit
    def test_fetch_weather_api_error(self, service):
        """Test handling of API error."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")

            result = service.fetch_weather('London')

            assert result is None

    @pytest.mark.unit
    def test_fetch_weather_timeout(self, service):
        """Test handling of request timeout."""
        import requests
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")

            result = service.fetch_weather('London')

            assert result is None

    # =========================================================================
    # collect_and_store_data Tests
    # =========================================================================

    @pytest.mark.unit
    def test_collect_and_store_data_success(self, service, mock_repository, mock_openweather_response):
        """Test collecting and storing weather data."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_openweather_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_weather_data.return_value = 3

            with patch('time.sleep'):
                result = service.collect_and_store_data(['London', 'Paris', 'Berlin'])

            assert result['total_cities'] == 3
            assert result['successful'] == 3
            mock_repository.insert_bulk_weather_data.assert_called_once()

    @pytest.mark.unit
    def test_collect_and_store_data_partial_failure(self, service, mock_repository, mock_openweather_response):
        """Test partial failures during collection."""
        with patch('requests.get') as mock_get:
            # First succeeds, second fails, third succeeds
            success_response = Mock()
            success_response.json.return_value = mock_openweather_response
            success_response.raise_for_status = Mock()

            mock_get.side_effect = [
                success_response,
                Exception("API Error"),
                success_response
            ]

            mock_repository.insert_bulk_weather_data.return_value = 2

            with patch('time.sleep'):
                result = service.collect_and_store_data(['London', 'InvalidCity', 'Paris'])

            assert result['total_cities'] == 3
            assert result['failed'] == 1

    @pytest.mark.unit
    def test_collect_and_store_data_with_default_cities(self, service, mock_repository, mock_openweather_response):
        """Test collection using default cities."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_openweather_response
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            mock_repository.insert_bulk_weather_data.return_value = len(WeatherService.DEFAULT_CITIES)

            with patch('time.sleep'):
                result = service.collect_and_store_data(None)

            assert result['total_cities'] == len(WeatherService.DEFAULT_CITIES)

    # =========================================================================
    # get_latest_weather Tests
    # =========================================================================

    @pytest.mark.unit
    def test_get_latest_weather(self, service, mock_repository, sample_weather_data):
        """Test getting latest weather from repository."""
        mock_repository.get_all_latest_weather.return_value = [sample_weather_data]

        result = service.get_latest_weather()

        assert len(result) == 1
        assert result[0]['city'] == 'London'
        mock_repository.get_all_latest_weather.assert_called_once()

    @pytest.mark.unit
    def test_get_latest_weather_empty(self, service, mock_repository):
        """Test getting latest weather when none exists."""
        mock_repository.get_all_latest_weather.return_value = []

        result = service.get_latest_weather()

        assert result == []
