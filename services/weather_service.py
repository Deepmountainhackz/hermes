"""Weather Service - OpenWeatherMap API integration."""
import requests, time, logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.config import Config
from core.exceptions import APIError
from repositories.weather_repository import WeatherRepository

logger = logging.getLogger(__name__)

class WeatherService:
    DEFAULT_CITIES = ['London', 'New York', 'Tokyo', 'Paris', 'Berlin', 'Moscow', 'Beijing', 'Sydney', 'Mumbai', 'Toronto']
    
    def __init__(self, config: Config, repository: WeatherRepository):
        self.config = config
        self.repository = repository
        self.api_key = config.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.timeout = config.API_TIMEOUT
        self.rate_limit_delay = config.DEFAULT_RATE_LIMIT_DELAY
    
    def fetch_weather(self, city: str) -> Optional[Dict]:
        try:
            params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            return {
                'city': city,
                'country': data.get('sys', {}).get('country'),
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'description': data['weather'][0]['description'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            return None
    
    def collect_and_store_data(self, cities=None) -> Dict:
        cities = cities or self.DEFAULT_CITIES
        results = []
        for city in cities:
            data = self.fetch_weather(city)
            if data:
                results.append(data)
            time.sleep(self.rate_limit_delay)
        
        successful = 0
        if results:
            successful = self.repository.insert_bulk_weather_data(results)
        
        return {
            'total_cities': len(cities),
            'successful': successful,
            'failed': len(cities) - len(results),
            'timestamp': datetime.now()
        }
    
    def get_latest_weather(self):
        return self.repository.get_all_latest_weather()
