"""
Weather Data Collector - FIXED VERSION
Fetches current weather data from OpenWeatherMap API
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeatherDataCollector:
    """Collector for current weather data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY')
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_data(self, city: str = None, lat: float = None, lon: float = None) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data
        
        Args:
            city: City name (e.g., 'London', 'New York')
            lat: Latitude (alternative to city)
            lon: Longitude (alternative to city)
            
        Returns:
            Dictionary containing weather data or None if failed
        """
        if not self.api_key or self.api_key == 'your_key_here':
            logger.warning("OpenWeatherMap API key not provided or invalid. Please set OPENWEATHER_API_KEY in .env file")
            logger.info("Get your free API key at: https://openweathermap.org/api")
            return None
        
        # Build parameters
        params = {
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        
        if city:
            params['q'] = city
        elif lat is not None and lon is not None:
            params['lat'] = lat
            params['lon'] = lon
        else:
            logger.error("Either city or lat/lon coordinates must be provided")
            return None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching weather data for {city or f'{lat},{lon}'} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response structure
                if not self._validate_response(data):
                    logger.error("Invalid response structure from Weather API")
                    return None
                
                # Enrich data with additional metadata
                enriched_data = self._enrich_data(data)
                
                logger.info(f"Successfully fetched weather data for {enriched_data['city']}: "
                          f"{enriched_data['temperature']}°C, {enriched_data['conditions']}")
                
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
                if e.response.status_code == 401:
                    logger.error("Invalid API key. Please check your OPENWEATHER_API_KEY")
                    return None
                elif e.response.status_code == 404:
                    logger.error(f"City not found: {city}")
                    return None
                elif e.response.status_code == 429:
                    logger.warning("Rate limit hit, waiting longer")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 3)
                else:
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
    
    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate Weather API response structure"""
        try:
            return (
                'main' in data and
                'temp' in data['main'] and
                'weather' in data and
                len(data['weather']) > 0 and
                'name' in data
            )
        except Exception:
            return False
    
    def _enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich weather data with additional metadata"""
        main = data['main']
        weather = data['weather'][0]
        
        return {
            'city': data['name'],
            'country': data.get('sys', {}).get('country'),
            'temperature': round(main['temp'], 1),
            'feels_like': round(main['feels_like'], 1),
            'temp_min': round(main['temp_min'], 1),
            'temp_max': round(main['temp_max'], 1),
            'pressure': main['pressure'],
            'humidity': main['humidity'],
            'conditions': weather['main'],
            'description': weather['description'],
            'wind_speed': data.get('wind', {}).get('speed'),
            'wind_direction': data.get('wind', {}).get('deg'),
            'clouds': data.get('clouds', {}).get('all'),
            'visibility': data.get('visibility'),
            'sunrise': data.get('sys', {}).get('sunrise'),
            'sunset': data.get('sys', {}).get('sunset'),
            'coordinates': {
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon']
            },
            'timestamp': data['dt'],
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success'
        }

def main():
    """Main execution function"""
    collector = WeatherDataCollector()
    
    logger.info("Starting weather data collection")
    data = collector.fetch_data(city='London')
    
    if data:
        logger.info("Weather data collection successful")
        print("\n=== Weather Data ===")
        print(f"City: {data['city']}, {data['country']}")
        print(f"Temperature: {data['temperature']}°C (Feels like: {data['feels_like']}°C)")
        print(f"Conditions: {data['conditions']} - {data['description']}")
        print(f"Humidity: {data['humidity']}%")
        print(f"Wind Speed: {data['wind_speed']} m/s")
        print(f"Collection Time: {data['collection_time']}")
        return data
    else:
        logger.error("Weather data collection failed")
        print("\n⚠️  Weather collection failed. Common issues:")
        print("   1. Missing or invalid API key in .env file")
        print("   2. Get your free API key at: https://openweathermap.org/api")
        print("   3. Copy .env.example to .env and add your key")
        return None

if __name__ == "__main__":
    main()
