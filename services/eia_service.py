"""
EIA (Energy Information Administration) Service
Business logic for fetching detailed energy data from the US EIA API.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from core.config import Config
from core.exceptions import APIError

logger = logging.getLogger(__name__)


class EIAService:
    """Service for EIA energy data operations."""

    # EIA API series IDs for key energy data
    EIA_SERIES = {
        # Petroleum
        'CRUDE_PRODUCTION': {
            'series_id': 'PET.WCRFPUS2.W',
            'name': 'US Crude Oil Production',
            'unit': 'Thousand Barrels/Day',
            'category': 'Petroleum'
        },
        'CRUDE_STOCKS': {
            'series_id': 'PET.WCESTUS1.W',
            'name': 'US Crude Oil Stocks',
            'unit': 'Thousand Barrels',
            'category': 'Petroleum'
        },
        'CRUDE_IMPORTS': {
            'series_id': 'PET.WCRIMUS2.W',
            'name': 'US Crude Oil Imports',
            'unit': 'Thousand Barrels/Day',
            'category': 'Petroleum'
        },
        'GASOLINE_STOCKS': {
            'series_id': 'PET.WGTSTUS1.W',
            'name': 'US Gasoline Stocks',
            'unit': 'Thousand Barrels',
            'category': 'Petroleum'
        },
        'GASOLINE_DEMAND': {
            'series_id': 'PET.WGFUPUS2.W',
            'name': 'US Gasoline Demand',
            'unit': 'Thousand Barrels/Day',
            'category': 'Petroleum'
        },
        'DISTILLATE_STOCKS': {
            'series_id': 'PET.WDISTUS1.W',
            'name': 'US Distillate Stocks',
            'unit': 'Thousand Barrels',
            'category': 'Petroleum'
        },
        'REFINERY_UTILIZATION': {
            'series_id': 'PET.WPULEUS3.W',
            'name': 'US Refinery Utilization',
            'unit': 'Percent',
            'category': 'Petroleum'
        },
        'CUSHING_STOCKS': {
            'series_id': 'PET.WCRSTUS1.W',
            'name': 'Cushing OK Crude Stocks',
            'unit': 'Thousand Barrels',
            'category': 'Petroleum'
        },

        # Natural Gas
        'NG_PRODUCTION': {
            'series_id': 'NG.N9070US2.M',
            'name': 'US Natural Gas Production',
            'unit': 'Billion Cubic Feet',
            'category': 'Natural Gas'
        },
        'NG_STORAGE': {
            'series_id': 'NG.NW2_EPG0_SWO_R48_BCF.W',
            'name': 'US Natural Gas Storage',
            'unit': 'Billion Cubic Feet',
            'category': 'Natural Gas'
        },
        'NG_CONSUMPTION': {
            'series_id': 'NG.N9140US2.M',
            'name': 'US Natural Gas Consumption',
            'unit': 'Billion Cubic Feet',
            'category': 'Natural Gas'
        },
        'NG_EXPORTS_LNG': {
            'series_id': 'NG.N9133US2.M',
            'name': 'US LNG Exports',
            'unit': 'Billion Cubic Feet',
            'category': 'Natural Gas'
        },

        # Electricity
        'ELECTRICITY_GENERATION': {
            'series_id': 'ELEC.GEN.ALL-US-99.M',
            'name': 'US Electricity Generation',
            'unit': 'Thousand MWh',
            'category': 'Electricity'
        },
        'COAL_GENERATION': {
            'series_id': 'ELEC.GEN.COW-US-99.M',
            'name': 'Coal Generation',
            'unit': 'Thousand MWh',
            'category': 'Electricity'
        },
        'NG_GENERATION': {
            'series_id': 'ELEC.GEN.NG-US-99.M',
            'name': 'Natural Gas Generation',
            'unit': 'Thousand MWh',
            'category': 'Electricity'
        },
        'NUCLEAR_GENERATION': {
            'series_id': 'ELEC.GEN.NUC-US-99.M',
            'name': 'Nuclear Generation',
            'unit': 'Thousand MWh',
            'category': 'Electricity'
        },
        'WIND_GENERATION': {
            'series_id': 'ELEC.GEN.WND-US-99.M',
            'name': 'Wind Generation',
            'unit': 'Thousand MWh',
            'category': 'Electricity'
        },
        'SOLAR_GENERATION': {
            'series_id': 'ELEC.GEN.SUN-US-99.M',
            'name': 'Solar Generation',
            'unit': 'Thousand MWh',
            'category': 'Electricity'
        },

        # Coal
        'COAL_PRODUCTION': {
            'series_id': 'COAL.PRODUCTION.TOT-US-TOT.Q',
            'name': 'US Coal Production',
            'unit': 'Thousand Short Tons',
            'category': 'Coal'
        },
        'COAL_STOCKS': {
            'series_id': 'COAL.STOCKS.TOT-US-TOT.Q',
            'name': 'US Coal Stocks',
            'unit': 'Thousand Short Tons',
            'category': 'Coal'
        },

        # Prices
        'WTI_SPOT': {
            'series_id': 'PET.RWTC.D',
            'name': 'WTI Crude Spot Price',
            'unit': 'USD/Barrel',
            'category': 'Prices'
        },
        'BRENT_SPOT': {
            'series_id': 'PET.RBRTE.D',
            'name': 'Brent Crude Spot Price',
            'unit': 'USD/Barrel',
            'category': 'Prices'
        },
        'HENRY_HUB': {
            'series_id': 'NG.RNGWHHD.D',
            'name': 'Henry Hub Natural Gas Spot',
            'unit': 'USD/MMBtu',
            'category': 'Prices'
        },
        'GASOLINE_RETAIL': {
            'series_id': 'PET.EMM_EPMR_PTE_NUS_DPG.W',
            'name': 'US Retail Gasoline Price',
            'unit': 'USD/Gallon',
            'category': 'Prices'
        },
    }

    def __init__(self, config: Config):
        """
        Initialize the EIA service.

        Args:
            config: Configuration instance with EIA_API_KEY
        """
        self.config = config
        self.api_key = config.EIA_API_KEY
        self.base_url = "https://api.eia.gov/v2"
        self.max_retries = config.API_MAX_RETRIES
        self.retry_delay = config.API_RETRY_DELAY
        self.timeout = config.API_TIMEOUT

    def _make_api_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to EIA API with retry logic.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response from API

        Raises:
            APIError: If request fails after retries
        """
        if not self.api_key:
            raise APIError("EIA API key not configured")

        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params['api_key'] = self.api_key

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()

                if 'error' in data:
                    raise APIError(f"EIA API error: {data['error']}")

                return data

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"EIA request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise APIError(f"Failed to fetch data from EIA after {self.max_retries} attempts: {e}")

        raise APIError("Unexpected error in EIA API request")

    def fetch_series_data(self, series_key: str, num_observations: int = 52) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a specific EIA series.

        Args:
            series_key: Key from EIA_SERIES dict
            num_observations: Number of data points to retrieve

        Returns:
            Dictionary with series data or None if failed
        """
        if series_key not in self.EIA_SERIES:
            logger.error(f"Unknown EIA series: {series_key}")
            return None

        series_info = self.EIA_SERIES[series_key]
        series_id = series_info['series_id']

        try:
            # Parse series ID to build correct endpoint
            # EIA v2 API uses different endpoints for different data types
            params = {
                'frequency': self._get_frequency(series_id),
                'data[0]': 'value',
                'sort[0][column]': 'period',
                'sort[0][direction]': 'desc',
                'length': num_observations
            }

            # Determine endpoint from series ID
            endpoint = self._get_endpoint(series_id)

            data = self._make_api_request(endpoint, params)

            if 'response' not in data or 'data' not in data['response']:
                logger.warning(f"No data returned for series {series_key}")
                return None

            series_data = data['response']['data']

            return {
                'key': series_key,
                'series_id': series_id,
                'name': series_info['name'],
                'unit': series_info['unit'],
                'category': series_info['category'],
                'data': series_data,
                'latest_value': series_data[0]['value'] if series_data else None,
                'latest_period': series_data[0]['period'] if series_data else None,
                'timestamp': datetime.now()
            }

        except APIError as e:
            logger.error(f"Error fetching EIA series {series_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching EIA series {series_key}: {e}")
            return None

    def _get_frequency(self, series_id: str) -> str:
        """Determine frequency from series ID suffix."""
        if series_id.endswith('.D'):
            return 'daily'
        elif series_id.endswith('.W'):
            return 'weekly'
        elif series_id.endswith('.M'):
            return 'monthly'
        elif series_id.endswith('.Q'):
            return 'quarterly'
        elif series_id.endswith('.A'):
            return 'annual'
        return 'weekly'

    def _get_endpoint(self, series_id: str) -> str:
        """Determine API endpoint from series ID."""
        if series_id.startswith('PET.'):
            return 'petroleum/sum/sndw/data'
        elif series_id.startswith('NG.'):
            return 'natural-gas/sum/lsum/data'
        elif series_id.startswith('ELEC.'):
            return 'electricity/electric-power-operational-data/data'
        elif series_id.startswith('COAL.'):
            return 'coal/aggregate/data'
        return 'petroleum/sum/sndw/data'

    def fetch_petroleum_summary(self) -> Dict[str, Any]:
        """
        Fetch summary of key petroleum indicators.

        Returns:
            Dictionary with petroleum data
        """
        petroleum_keys = [k for k, v in self.EIA_SERIES.items() if v['category'] == 'Petroleum']

        results = {}
        for key in petroleum_keys:
            data = self.fetch_series_data(key, num_observations=10)
            if data:
                results[key] = data
            time.sleep(0.5)  # Rate limiting

        return results

    def fetch_natural_gas_summary(self) -> Dict[str, Any]:
        """
        Fetch summary of key natural gas indicators.

        Returns:
            Dictionary with natural gas data
        """
        ng_keys = [k for k, v in self.EIA_SERIES.items() if v['category'] == 'Natural Gas']

        results = {}
        for key in ng_keys:
            data = self.fetch_series_data(key, num_observations=10)
            if data:
                results[key] = data
            time.sleep(0.5)

        return results

    def fetch_electricity_mix(self) -> Dict[str, Any]:
        """
        Fetch electricity generation mix data.

        Returns:
            Dictionary with electricity generation by source
        """
        elec_keys = [k for k, v in self.EIA_SERIES.items() if v['category'] == 'Electricity']

        results = {}
        for key in elec_keys:
            data = self.fetch_series_data(key, num_observations=12)
            if data:
                results[key] = data
            time.sleep(0.5)

        return results

    def fetch_energy_prices(self) -> Dict[str, Any]:
        """
        Fetch current energy prices.

        Returns:
            Dictionary with energy prices
        """
        price_keys = [k for k, v in self.EIA_SERIES.items() if v['category'] == 'Prices']

        results = {}
        for key in price_keys:
            data = self.fetch_series_data(key, num_observations=30)
            if data:
                results[key] = data
            time.sleep(0.5)

        return results

    def get_weekly_inventory_report(self) -> Dict[str, Any]:
        """
        Get data similar to weekly EIA petroleum inventory report.

        Returns:
            Dictionary with inventory data and week-over-week changes
        """
        inventory_keys = ['CRUDE_STOCKS', 'GASOLINE_STOCKS', 'DISTILLATE_STOCKS',
                         'CUSHING_STOCKS', 'REFINERY_UTILIZATION']

        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'inventories': {}
        }

        for key in inventory_keys:
            data = self.fetch_series_data(key, num_observations=5)
            if data and data['data'] and len(data['data']) >= 2:
                current = float(data['data'][0]['value']) if data['data'][0]['value'] else 0
                previous = float(data['data'][1]['value']) if data['data'][1]['value'] else 0
                change = current - previous

                report['inventories'][key] = {
                    'name': data['name'],
                    'current': current,
                    'previous': previous,
                    'change': change,
                    'change_pct': (change / previous * 100) if previous else 0,
                    'unit': data['unit'],
                    'period': data['latest_period']
                }
            time.sleep(0.5)

        return report

    def get_all_series_metadata(self) -> List[Dict[str, str]]:
        """
        Get metadata for all available EIA series.

        Returns:
            List of series metadata
        """
        return [
            {
                'key': key,
                'series_id': info['series_id'],
                'name': info['name'],
                'unit': info['unit'],
                'category': info['category']
            }
            for key, info in self.EIA_SERIES.items()
        ]
