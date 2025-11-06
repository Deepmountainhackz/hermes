"""
Weather Data Collector
Fetches weather data for multiple cities and saves to PostgreSQL
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import time
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

# Major cities to track
CITIES = [
    'London', 'New York', 'Tokyo', 'Paris', 'Singapore',
    'Hong Kong', 'Dubai', 'Sydney', 'Toronto', 'Mumbai',
    'Shanghai', 'São Paulo', 'Mexico City', 'Moscow', 'Istanbul',
    'Bangkok', 'Seoul', 'Amsterdam', 'Frankfurt', 'Chicago',
    'Los Angeles', 'Beijing', 'Madrid', 'Rome', 'Berlin',
    'Vienna', 'Zurich', 'Stockholm', 'Copenhagen', 'Oslo',
    'Brussels', 'Dublin', 'Edinburgh', 'Milan', 'Barcelona',
    'Lisbon', 'Prague', 'Warsaw', 'Budapest', 'Athens',
    'Tel Aviv', 'Riyadh', 'Cape Town', 'Nairobi', 'Cairo',
    'Buenos Aires', 'Santiago', 'Lima', 'Bogotá', 'Caracas'
]

class WeatherDataCollector:
    """Collector for weather data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("OPENWEATHER_API_KEY not found in environment!")
    
    def fetch_city_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a single city
        
        Args:
            city: City name
            
        Returns:
            Weather data dictionary or None if failed
        """
        if not self.api_key:
            return None
        
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"✓ Fetched weather for {city}")
                return data
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to fetch weather for {city}: {e}")
                    return None
        
        return None
    
    def save_to_database(self, city: str, weather_data: Dict[str, Any]) -> bool:
        """
        Save weather data to PostgreSQL database
        
        Args:
            city: City name
            weather_data: Weather data from API
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract data
            timestamp = datetime.utcnow()
            
            data = {
                'city': city,
                'country': weather_data.get('sys', {}).get('country', ''),
                'timestamp': timestamp,
                'temperature': float(weather_data['main']['temp']),
                'feels_like': float(weather_data['main']['feels_like']),
                'temp_min': float(weather_data['main']['temp_min']),
                'temp_max': float(weather_data['main']['temp_max']),
                'pressure': int(weather_data['main']['pressure']),
                'humidity': int(weather_data['main']['humidity']),
                'description': weather_data['weather'][0]['description'],
                'wind_speed': float(weather_data.get('wind', {}).get('speed', 0)),
                'clouds': int(weather_data.get('clouds', {}).get('all', 0)),
                'latitude': float(weather_data['coord']['lat']),
                'longitude': float(weather_data['coord']['lon'])
            }
            
            # Insert into database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO weather 
                        (city, country, timestamp, temperature, feels_like, temp_min, temp_max,
                         pressure, humidity, description, wind_speed, clouds, latitude, longitude)
                        VALUES (%(city)s, %(country)s, %(timestamp)s, %(temperature)s, %(feels_like)s,
                                %(temp_min)s, %(temp_max)s, %(pressure)s, %(humidity)s, %(description)s,
                                %(wind_speed)s, %(clouds)s, %(latitude)s, %(longitude)s)
                        ON CONFLICT (city, timestamp) DO UPDATE SET
                            temperature = EXCLUDED.temperature,
                            feels_like = EXCLUDED.feels_like,
                            temp_min = EXCLUDED.temp_min,
                            temp_max = EXCLUDED.temp_max,
                            pressure = EXCLUDED.pressure,
                            humidity = EXCLUDED.humidity,
                            description = EXCLUDED.description,
                            wind_speed = EXCLUDED.wind_speed,
                            clouds = EXCLUDED.clouds,
                            collected_at = CURRENT_TIMESTAMP
                    """, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save weather data for {city}: {e}")
            return False
    
    def collect_all_cities(self, cities: List[str] = None) -> Dict[str, Any]:
        """
        Collect weather data for all cities
        
        Args:
            cities: List of city names (default: CITIES)
            
        Returns:
            Collection results
        """
        if cities is None:
            cities = CITIES
        
        results = {
            'total': len(cities),
            'successful': 0,
            'failed': 0
        }
        
        for i, city in enumerate(cities):
            # Rate limiting - 1 request per second
            if i > 0:
                time.sleep(1)
            
            weather_data = self.fetch_city_weather(city)
            
            if weather_data:
                if self.save_to_database(city, weather_data):
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1
        
        return results

def main():
    """Main execution function"""
    collector = WeatherDataCollector()
    
    logger.info(f"Starting weather data collection for {len(CITIES)} cities")
    results = collector.collect_all_cities()
    
    print(f"\n=== Weather Data Collection ===")
    print(f"Total cities: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    return results

if __name__ == "__main__":
    main()
