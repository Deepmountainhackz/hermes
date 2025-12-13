"""
World Bank Service
Business logic for fetching global development indicators from World Bank API.
Free API - No authentication required.
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from core.config import Config
from core.exceptions import APIError, ValidationError
from repositories.worldbank_repository import WorldBankRepository

logger = logging.getLogger(__name__)


class WorldBankService:
    """Service for World Bank development indicators."""

    # World Bank indicator codes for key development metrics
    # See: https://datahelpdesk.worldbank.org/knowledgebase/articles/898599
    DEFAULT_INDICATORS = {
        # Economic indicators
        'NY.GDP.MKTP.CD': {'name': 'GDP (Current US$)', 'category': 'Economy'},
        'NY.GDP.MKTP.KD.ZG': {'name': 'GDP Growth (Annual %)', 'category': 'Economy'},
        'NY.GDP.PCAP.CD': {'name': 'GDP Per Capita (Current US$)', 'category': 'Economy'},
        'FP.CPI.TOTL.ZG': {'name': 'Inflation (CPI Annual %)', 'category': 'Economy'},
        'GC.DOD.TOTL.GD.ZS': {'name': 'Government Debt (% of GDP)', 'category': 'Economy'},
        'BN.CAB.XOKA.GD.ZS': {'name': 'Current Account Balance (% of GDP)', 'category': 'Economy'},

        # Trade indicators
        'NE.EXP.GNFS.ZS': {'name': 'Exports (% of GDP)', 'category': 'Trade'},
        'NE.IMP.GNFS.ZS': {'name': 'Imports (% of GDP)', 'category': 'Trade'},
        'TG.VAL.TOTL.GD.ZS': {'name': 'Trade (% of GDP)', 'category': 'Trade'},
        'BX.KLT.DINV.WD.GD.ZS': {'name': 'Foreign Direct Investment (% of GDP)', 'category': 'Trade'},

        # Demographics
        'SP.POP.TOTL': {'name': 'Population (Total)', 'category': 'Demographics'},
        'SP.POP.GROW': {'name': 'Population Growth (Annual %)', 'category': 'Demographics'},
        'SP.URB.TOTL.IN.ZS': {'name': 'Urban Population (% of Total)', 'category': 'Demographics'},
        'SP.DYN.LE00.IN': {'name': 'Life Expectancy (Years)', 'category': 'Demographics'},

        # Health indicators (NEW)
        'SP.DYN.IMRT.IN': {'name': 'Infant Mortality Rate (per 1,000)', 'category': 'Health'},
        'SP.DYN.CDRT.IN': {'name': 'Death Rate (per 1,000)', 'category': 'Health'},
        'SP.DYN.CBRT.IN': {'name': 'Birth Rate (per 1,000)', 'category': 'Health'},
        'SH.XPD.CHEX.GD.ZS': {'name': 'Health Expenditure (% of GDP)', 'category': 'Health'},
        'SH.MED.PHYS.ZS': {'name': 'Physicians (per 1,000 people)', 'category': 'Health'},
        'SH.MED.BEDS.ZS': {'name': 'Hospital Beds (per 1,000 people)', 'category': 'Health'},
        'SH.STA.MMRT': {'name': 'Maternal Mortality Ratio (per 100,000)', 'category': 'Health'},
        'SH.DYN.MORT': {'name': 'Under-5 Mortality Rate (per 1,000)', 'category': 'Health'},
        'SH.IMM.IDPT': {'name': 'DPT Immunization (% of children)', 'category': 'Health'},
        'SH.IMM.MEAS': {'name': 'Measles Immunization (% of children)', 'category': 'Health'},

        # Education indicators (NEW)
        'SE.ADT.LITR.ZS': {'name': 'Literacy Rate - Adult (% age 15+)', 'category': 'Education'},
        'SE.ADT.1524.LT.ZS': {'name': 'Literacy Rate - Youth (% age 15-24)', 'category': 'Education'},
        'SE.PRM.ENRR': {'name': 'Primary School Enrollment (%)', 'category': 'Education'},
        'SE.SEC.ENRR': {'name': 'Secondary School Enrollment (%)', 'category': 'Education'},
        'SE.TER.ENRR': {'name': 'Tertiary School Enrollment (%)', 'category': 'Education'},
        'SE.XPD.TOTL.GD.ZS': {'name': 'Education Expenditure (% of GDP)', 'category': 'Education'},
        'SE.PRM.CMPT.ZS': {'name': 'Primary Completion Rate (%)', 'category': 'Education'},
        'SE.SEC.CMPT.LO.ZS': {'name': 'Lower Secondary Completion Rate (%)', 'category': 'Education'},

        # Labor & Social
        'SL.UEM.TOTL.ZS': {'name': 'Unemployment (% of Labor Force)', 'category': 'Labor'},
        'SL.TLF.CACT.ZS': {'name': 'Labor Force Participation (%)', 'category': 'Labor'},
        'SI.POV.NAHC': {'name': 'Poverty Rate (National)', 'category': 'Social'},
        'SI.POV.GINI': {'name': 'GINI Index (Income Inequality)', 'category': 'Social'},

        # Energy & Environment
        'EG.USE.PCAP.KG.OE': {'name': 'Energy Use (kg Oil Equiv Per Capita)', 'category': 'Energy'},
        'EN.ATM.CO2E.PC': {'name': 'CO2 Emissions (Metric Tons Per Capita)', 'category': 'Environment'},
        'EG.ELC.ACCS.ZS': {'name': 'Access to Electricity (% of Population)', 'category': 'Energy'},
        'EG.FEC.RNEW.ZS': {'name': 'Renewable Energy (% of Total)', 'category': 'Energy'},
    }

    # Countries to track (ISO 3166-1 alpha-2 codes)
    # Includes G20 + major economies
    DEFAULT_COUNTRIES = [
        'US',   # United States
        'CN',   # China
        'JP',   # Japan
        'DE',   # Germany
        'GB',   # United Kingdom
        'FR',   # France
        'IN',   # India
        'IT',   # Italy
        'BR',   # Brazil
        'CA',   # Canada
        'RU',   # Russia
        'KR',   # South Korea
        'AU',   # Australia
        'MX',   # Mexico
        'ID',   # Indonesia
        'SA',   # Saudi Arabia
        'TR',   # Turkey
        'AR',   # Argentina
        'ZA',   # South Africa
        'CH',   # Switzerland
    ]

    def __init__(self, config: Config, repository: WorldBankRepository):
        """Initialize the service."""
        self.config = config
        self.repository = repository
        self.base_url = "https://api.worldbank.org/v2"
        self.max_retries = config.API_MAX_RETRIES
        self.retry_delay = config.API_RETRY_DELAY
        self.timeout = config.API_TIMEOUT
        self.rate_limit_delay = 0.5  # World Bank is generous with rate limits

    def _make_api_request(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Make a request to World Bank API with retry logic."""
        if params is None:
            params = {}

        # Always request JSON format
        params['format'] = 'json'
        params['per_page'] = '100'

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # World Bank API returns a list: [metadata, data]
                if isinstance(data, list) and len(data) >= 2:
                    return {'metadata': data[0], 'data': data[1]}
                return {'metadata': {}, 'data': data}

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    raise APIError(f"Failed to fetch from World Bank after {self.max_retries} attempts: {e}")

        raise APIError("Unexpected error in API request")

    def fetch_indicator(self, indicator_code: str, country_codes: List[str],
                        mrv: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch indicator data for specified countries.

        Args:
            indicator_code: World Bank indicator code
            country_codes: List of ISO country codes
            mrv: Most recent values (number of observations)

        Returns:
            List of indicator data dictionaries
        """
        results = []
        countries_str = ';'.join(country_codes)

        try:
            endpoint = f"country/{countries_str}/indicator/{indicator_code}"
            params = {'mrv': str(mrv)}

            response = self._make_api_request(endpoint, params)
            data = response.get('data', [])

            if not data:
                logger.warning(f"No data returned for indicator {indicator_code}")
                return []

            indicator_info = self.DEFAULT_INDICATORS.get(indicator_code, {})
            indicator_name = indicator_info.get('name', indicator_code)
            category = indicator_info.get('category', 'Other')

            for record in data:
                if record is None:
                    continue

                value = record.get('value')
                if value is None:
                    continue

                results.append({
                    'indicator_code': indicator_code,
                    'indicator_name': indicator_name,
                    'category': category,
                    'country_code': record.get('countryiso3code', record.get('country', {}).get('id', '')),
                    'country_name': record.get('country', {}).get('value', ''),
                    'year': int(record.get('date', 0)),
                    'value': float(value),
                    'unit': record.get('unit', ''),
                    'timestamp': datetime.now()
                })

            logger.debug(f"Fetched {len(results)} records for {indicator_code}")
            return results

        except (APIError, ValidationError) as e:
            logger.error(f"Error fetching indicator {indicator_code}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching {indicator_code}: {e}")
            return []

    def fetch_all_indicators(self, indicators: Dict[str, Dict] = None,
                              countries: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch all configured indicators for all countries."""
        if indicators is None:
            indicators = self.DEFAULT_INDICATORS
        if countries is None:
            countries = self.DEFAULT_COUNTRIES

        all_results = []

        for indicator_code, info in indicators.items():
            logger.info(f"Fetching {info['name']}...")

            data = self.fetch_indicator(indicator_code, countries)
            all_results.extend(data)

            time.sleep(self.rate_limit_delay)

        return all_results

    def collect_and_store_data(self, indicators: Dict[str, Dict] = None,
                                countries: List[str] = None) -> Dict[str, Any]:
        """Collect World Bank data and store in database."""
        if indicators is None:
            indicators = self.DEFAULT_INDICATORS
        if countries is None:
            countries = self.DEFAULT_COUNTRIES

        logger.info("Starting World Bank data collection")
        start_time = datetime.now()

        # Fetch all indicators
        indicator_data = self.fetch_all_indicators(indicators, countries)

        successful = 0
        failed = 0

        # Store in database
        if indicator_data:
            try:
                inserted = self.repository.insert_bulk_indicator_data(indicator_data)
                successful = inserted
            except Exception as e:
                logger.error(f"Error storing World Bank data: {e}")
                failed = len(indicator_data)

        # Calculate stats
        total_expected = len(indicators) * len(countries)
        failed += max(0, total_expected - len(indicator_data))

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        results = {
            'total_expected': total_expected,
            'records_fetched': len(indicator_data),
            'successful': successful,
            'failed': failed,
            'duration_seconds': duration,
            'timestamp': end_time
        }

        logger.info(f"World Bank collection completed: {successful} records stored, {failed} failed")

        return results

    def get_latest_indicators(self) -> List[Dict[str, Any]]:
        """Get the latest World Bank indicators from database."""
        try:
            return self.repository.get_all_latest_indicators()
        except Exception as e:
            logger.error(f"Error getting latest indicators: {e}")
            return []

    def get_indicator_by_country(self, country_code: str) -> List[Dict[str, Any]]:
        """Get all indicators for a specific country."""
        try:
            return self.repository.get_indicators_by_country(country_code)
        except Exception as e:
            logger.error(f"Error getting country indicators: {e}")
            return []

    def get_indicator_history(self, indicator_code: str, country_code: str,
                               years: int = 10) -> List[Dict[str, Any]]:
        """Get historical data for an indicator."""
        try:
            return self.repository.get_indicator_history(indicator_code, country_code, years)
        except Exception as e:
            logger.error(f"Error getting indicator history: {e}")
            return []
