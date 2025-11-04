"""
Country Profile Data Collector
Fetches comprehensive country data including demographics, languages, and statistics
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CountryProfileCollector:
    """Collector for country profile and demographic data"""
    
    def __init__(self):
        # REST Countries API - comprehensive, free, no key required
        self.base_url = "https://restcountries.com/v3.1"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_country_by_name(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch country profile by name
        
        Args:
            country_name: Country name (e.g., 'Germany', 'Japan', 'Brazil')
            
        Returns:
            Dictionary containing country profile or None if failed
        """
        endpoint = f"{self.base_url}/name/{country_name}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching country profile for {country_name} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # API returns array, get first match
                if not data or len(data) == 0:
                    logger.error(f"No data found for country: {country_name}")
                    return None
                
                country_data = data[0]
                
                # Process and enrich the data
                enriched_data = self._enrich_country_data(country_data)
                
                logger.info(f"Successfully fetched profile for {enriched_data['name']}: "
                          f"Pop {enriched_data['population']:,}, "
                          f"{len(enriched_data['languages'])} languages")
                
                return enriched_data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if e.response.status_code == 404:
                    logger.error(f"Country not found: {country_name}")
                return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def fetch_country_by_code(self, country_code: str) -> Optional[Dict[str, Any]]:
        """
        Fetch country profile by ISO code
        
        Args:
            country_code: ISO 3166-1 alpha-2 or alpha-3 code (e.g., 'US', 'USA', 'GB', 'GBR')
            
        Returns:
            Dictionary containing country profile or None if failed
        """
        endpoint = f"{self.base_url}/alpha/{country_code}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching country profile for code {country_code} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    logger.error(f"No data found for country code: {country_code}")
                    return None
                
                # Process and enrich the data
                enriched_data = self._enrich_country_data(data)
                
                logger.info(f"Successfully fetched profile for {enriched_data['name']}")
                
                return enriched_data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if e.response.status_code == 404:
                    logger.error(f"Country code not found: {country_code}")
                return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def fetch_countries_by_region(self, region: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all countries in a region
        
        Args:
            region: Region name (e.g., 'Europe', 'Asia', 'Africa', 'Americas', 'Oceania')
            
        Returns:
            List of country profiles or None if failed
        """
        endpoint = f"{self.base_url}/region/{region}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching countries in region {region} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    logger.error(f"No data found for region: {region}")
                    return None
                
                # Process each country
                enriched_countries = [self._enrich_country_data(country) for country in data]
                
                logger.info(f"Successfully fetched {len(enriched_countries)} countries from {region}")
                
                return enriched_countries
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def _enrich_country_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enrich country data with structured information"""
        
        # Extract languages
        languages = []
        if 'languages' in data and data['languages']:
            languages = list(data['languages'].values())
        
        # Extract currencies
        currencies = []
        if 'currencies' in data and data['currencies']:
            for code, info in data['currencies'].items():
                currencies.append({
                    'code': code,
                    'name': info.get('name'),
                    'symbol': info.get('symbol')
                })
        
        # Extract name variations
        name_info = data.get('name', {})
        
        # Calculate population density if area available
        population = data.get('population', 0)
        area = data.get('area', 0)
        density = round(population / area, 2) if area > 0 else None
        
        # Extract capital(s)
        capitals = data.get('capital', [])
        if not isinstance(capitals, list):
            capitals = [capitals] if capitals else []
        
        # Extract timezones
        timezones = data.get('timezones', [])
        
        # Extract borders (neighboring countries)
        borders = data.get('borders', [])
        
        # Extract geographic coordinates
        latlng = data.get('latlng', [])
        latitude = latlng[0] if len(latlng) > 0 else None
        longitude = latlng[1] if len(latlng) > 1 else None
        
        # Build enriched profile
        return {
            # Basic Info
            'name': name_info.get('common', 'Unknown'),
            'official_name': name_info.get('official', ''),
            'native_names': name_info.get('nativeName', {}),
            
            # Codes
            'cca2': data.get('cca2'),  # ISO 3166-1 alpha-2
            'cca3': data.get('cca3'),  # ISO 3166-1 alpha-3
            'ccn3': data.get('ccn3'),  # ISO 3166-1 numeric
            'cioc': data.get('cioc'),  # International Olympic Committee
            
            # Demographics
            'population': population,
            'area_km2': area,
            'population_density': density,
            
            # Languages
            'languages': languages,
            'total_languages': len(languages),
            
            # Geographic
            'region': data.get('region'),
            'subregion': data.get('subregion'),
            'continents': data.get('continents', []),
            'capital': capitals,
            'latitude': latitude,
            'longitude': longitude,
            'landlocked': data.get('landlocked', False),
            'borders': borders,
            'border_count': len(borders),
            
            # Economic
            'currencies': currencies,
            'gini': data.get('gini', {}),  # Gini coefficient (income inequality)
            
            # Political
            'independent': data.get('independent'),
            'un_member': data.get('unMember'),
            'status': data.get('status'),
            
            # Time & Communication
            'timezones': timezones,
            'timezone_count': len(timezones),
            'tld': data.get('tld', []),  # Top-level domain
            'calling_codes': data.get('idd', {}).get('root', '') + ''.join(data.get('idd', {}).get('suffixes', [])),
            
            # Cultural
            'flag_emoji': data.get('flag'),
            'coat_of_arms': data.get('coatOfArms', {}).get('png'),
            'start_of_week': data.get('startOfWeek'),
            
            # Additional
            'maps': {
                'google': data.get('maps', {}).get('googleMaps'),
                'openstreetmap': data.get('maps', {}).get('openStreetMaps')
            },
            'fifa': data.get('fifa'),
            
            # Metadata
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success'
        }
    
    def fetch_data(self, country: str, by_code: bool = False) -> Optional[Dict[str, Any]]:
        """
        Main method to fetch country profile
        
        Args:
            country: Country name or code
            by_code: If True, treat country as ISO code, otherwise as name
            
        Returns:
            Dictionary containing country profile or None if failed
        """
        if by_code:
            return self.fetch_country_by_code(country)
        else:
            return self.fetch_country_by_name(country)

def main():
    """Main execution function"""
    collector = CountryProfileCollector()
    
    logger.info("Starting country profile data collection")
    
    print("\n" + "="*60)
    print("🌍 COUNTRY PROFILE COLLECTOR")
    print("="*60)
    
    # Example 1: Fetch by name
    print("\n📊 Fetching Germany profile...")
    germany = collector.fetch_data('Germany')
    
    if germany:
        print(f"\n🇩🇪 {germany['name']} ({germany['official_name']})")
        print(f"   Region: {germany['region']} - {germany['subregion']}")
        print(f"   Population: {germany['population']:,} people")
        print(f"   Area: {germany['area_km2']:,.0f} km²")
        print(f"   Density: {germany['population_density']:.2f} people/km²")
        print(f"   Capital: {', '.join(germany['capital'])}")
        print(f"   Languages: {', '.join(germany['languages'])}")
        print(f"   Currencies: {', '.join([c['name'] for c in germany['currencies']])}")
        print(f"   Bordering Countries: {germany['border_count']} ({', '.join(germany['borders'])})")
        print(f"   Timezones: {', '.join(germany['timezones'])}")
        print(f"   UN Member: {'Yes' if germany['un_member'] else 'No'}")
        print(f"   Flag: {germany['flag_emoji']}")
    
    # Example 2: Fetch by code
    print("\n\n📊 Fetching Japan profile (by code)...")
    japan = collector.fetch_data('JP', by_code=True)
    
    if japan:
        print(f"\n🇯🇵 {japan['name']}")
        print(f"   Population: {japan['population']:,}")
        print(f"   Languages: {', '.join(japan['languages'])}")
        print(f"   Density: {japan['population_density']:.2f} people/km²")
    
    # Example 3: Fetch region
    print("\n\n📊 Fetching Scandinavia (Europe region sample)...")
    nordic = ['Sweden', 'Norway', 'Denmark', 'Finland']
    
    for country_name in nordic:
        country = collector.fetch_data(country_name)
        if country:
            print(f"   {country['flag_emoji']} {country['name']}: "
                  f"{country['population']:,} people, "
                  f"{len(country['languages'])} languages")
    
    print("\n" + "="*60)
    print("✅ Country profile collection complete!")
    print("="*60)

if __name__ == "__main__":
    main()
