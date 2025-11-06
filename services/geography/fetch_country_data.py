"""
Country Data Collector
Fetches country information from REST Countries API and saves to PostgreSQL
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import time
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CountryDataCollector:
    """Collector for country data"""
    
    def __init__(self):
        # Use API without fields parameter
        self.base_url = "https://restcountries.com/v3.1/all"
        self.timeout = 20
        self.max_retries = 3
        self.retry_delay = 2
    
    def fetch_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all country data
        
        Returns:
            List of countries or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching country data (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"✓ Fetched data for {len(data)} countries")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def save_to_database(self, countries: List[Dict[str, Any]]) -> int:
        """
        Save country data to PostgreSQL database
        
        Args:
            countries: List of country data
            
        Returns:
            Number of countries saved
        """
        saved_count = 0
        
        try:
            for country in countries:
                try:
                    # Extract data
                    name = country.get('name', {}).get('common', '')
                    if not name:
                        continue
                    
                    # Get country code (cca2 or cca3)
                    code = country.get('cca2') or country.get('cca3', '')
                    if not code:
                        continue
                    
                    # Get capital
                    capital = None
                    if country.get('capital'):
                        capital = country['capital'][0] if isinstance(country['capital'], list) else country['capital']
                    
                    # Get coordinates
                    latlng = country.get('latlng', [])
                    latitude = latlng[0] if len(latlng) > 0 else None
                    longitude = latlng[1] if len(latlng) > 1 else None
                    
                    # Convert complex fields to JSON strings
                    timezones = json.dumps(country.get('timezones', []))
                    currencies = json.dumps(country.get('currencies', {}))
                    languages = json.dumps(country.get('languages', {}))
                    
                    country_data = {
                        'name': name[:255],
                        'code': code[:10],
                        'capital': capital[:255] if capital else None,
                        'region': country.get('region', '')[:100],
                        'subregion': country.get('subregion', '')[:100],
                        'population': int(country.get('population', 0)),
                        'area': float(country.get('area', 0)) if country.get('area') else None,
                        'latitude': latitude,
                        'longitude': longitude,
                        'timezones': timezones,
                        'currencies': currencies,
                        'languages': languages,
                        'flag_url': country.get('flags', {}).get('png', '')
                    }
                    
                    # Insert into database
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO countries 
                                (name, code, capital, region, subregion, population, area,
                                 latitude, longitude, timezones, currencies, languages, flag_url)
                                VALUES (%(name)s, %(code)s, %(capital)s, %(region)s, %(subregion)s,
                                        %(population)s, %(area)s, %(latitude)s, %(longitude)s,
                                        %(timezones)s, %(currencies)s, %(languages)s, %(flag_url)s)
                                ON CONFLICT (code) DO UPDATE SET
                                    name = EXCLUDED.name,
                                    capital = EXCLUDED.capital,
                                    region = EXCLUDED.region,
                                    subregion = EXCLUDED.subregion,
                                    population = EXCLUDED.population,
                                    area = EXCLUDED.area,
                                    latitude = EXCLUDED.latitude,
                                    longitude = EXCLUDED.longitude,
                                    timezones = EXCLUDED.timezones,
                                    currencies = EXCLUDED.currencies,
                                    languages = EXCLUDED.languages,
                                    flag_url = EXCLUDED.flag_url,
                                    collected_at = CURRENT_TIMESTAMP
                            """, country_data)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save country {country.get('name', {}).get('common', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"✓ Saved {saved_count} countries to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process country data: {e}")
            return saved_count

def main():
    """Main execution function"""
    collector = CountryDataCollector()
    
    logger.info("Starting country data collection")
    data = collector.fetch_data()
    
    if data:
        logger.info("Country data collection successful")
        
        # Save to database
        saved = collector.save_to_database(data)
        
        print(f"\n=== Country Data Collection ===")
        print(f"Total countries fetched: {len(data)}")
        print(f"Saved to database: {saved}")
        
        return data
    else:
        logger.error("Country data collection failed")
        return None

if __name__ == "__main__":
    main()
