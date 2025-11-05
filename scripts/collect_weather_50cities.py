#!/usr/bin/env python3
"""
Weather Data Collection Script for 50 Cities - Production Version
Includes comprehensive error handling, logging, retry logic, and validation
"""

import requests
import sqlite3
from datetime import datetime
import time
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
API_KEY = '4c0bbed2da66e72f1daa471eacebfe76'
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 1.2  # seconds between requests

# 50 Major Cities Worldwide
CITIES = [
    # NORTH AMERICA
    'New York', 'Los Angeles', 'Chicago', 'Toronto', 'Mexico City', 
    'Miami', 'Vancouver', 'San Francisco',
    
    # SOUTH AMERICA
    'São Paulo', 'Rio de Janeiro', 'Buenos Aires', 'Lima', 'Bogotá', 'Santiago',
    
    # EUROPE
    'London', 'Paris', 'Berlin', 'Madrid', 'Rome', 'Amsterdam', 
    'Moscow', 'Istanbul', 'Athens', 'Stockholm',
    
    # MIDDLE EAST & AFRICA
    'Dubai', 'Cairo', 'Tel Aviv', 'Riyadh', 'Johannesburg', 
    'Cape Town', 'Nairobi', 'Lagos',
    
    # ASIA
    'Tokyo', 'Beijing', 'Shanghai', 'Hong Kong', 'Singapore', 'Mumbai', 
    'Delhi', 'Bangkok', 'Seoul', 'Jakarta', 'Manila', 'Kuala Lumpur', 'Taipei',
    
    # OCEANIA
    'Sydney', 'Melbourne', 'Auckland', 'Perth', 'Brisbane'
]


class WeatherDataValidator:
    """Validates weather data before database insertion"""
    
    @staticmethod
    def validate_temperature(temp: float) -> bool:
        """Check if temperature is within reasonable bounds"""
        return -100 <= temp <= 60
    
    @staticmethod
    def validate_humidity(humidity: int) -> bool:
        """Check if humidity is valid percentage"""
        return 0 <= humidity <= 100
    
    @staticmethod
    def validate_wind_speed(speed: float) -> bool:
        """Check if wind speed is reasonable"""
        return 0 <= speed <= 200  # m/s


class WeatherCollector:
    """Handles weather data collection with error handling and retry logic"""
    
    def __init__(self, api_key: str, db_path: str = 'hermes.db'):
        self.api_key = api_key
        self.db_path = db_path
        self.validator = WeatherDataValidator()
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        logger.info("WeatherCollector initialized")
    
    def fetch_weather(self, city: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a city with retry logic
        
        Args:
            city: City name
            retry_count: Current retry attempt
            
        Returns:
            Weather data dict or None if failed
        """
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric'
        
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Successfully fetched weather for {city}")
                return data
            
            elif response.status_code == 401:
                logger.error(f"Invalid API key for {city}")
                return None
            
            elif response.status_code == 404:
                logger.warning(f"City not found: {city}")
                return None
            
            elif response.status_code == 429:
                logger.warning(f"Rate limit exceeded for {city}")
                if retry_count < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * (retry_count + 1))
                    return self.fetch_weather(city, retry_count + 1)
                return None
            
            else:
                logger.error(f"API error for {city}: {response.status_code}")
                if retry_count < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                    return self.fetch_weather(city, retry_count + 1)
                return None
        
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching weather for {city}")
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                return self.fetch_weather(city, retry_count + 1)
            return None
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {city}")
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                return self.fetch_weather(city, retry_count + 1)
            return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {city}: {str(e)}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error for {city}: {str(e)}")
            return None
    
    def parse_weather_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse and validate weather data
        
        Args:
            data: Raw API response
            
        Returns:
            Parsed weather dict or None if invalid
        """
        try:
            # Extract data
            parsed = {
                'city_name': data['name'],
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'humidity': data['main']['humidity'],
                'weather_main': data['weather'][0]['main'],
                'weather_desc': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'clouds': data['clouds']['all'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Validate
            if not self.validator.validate_temperature(parsed['temp']):
                logger.warning(f"Invalid temperature for {parsed['city_name']}: {parsed['temp']}")
                return None
            
            if not self.validator.validate_humidity(parsed['humidity']):
                logger.warning(f"Invalid humidity for {parsed['city_name']}: {parsed['humidity']}")
                return None
            
            if not self.validator.validate_wind_speed(parsed['wind_speed']):
                logger.warning(f"Invalid wind speed for {parsed['city_name']}: {parsed['wind_speed']}")
                return None
            
            return parsed
        
        except KeyError as e:
            logger.error(f"Missing field in weather data: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Error parsing weather data: {str(e)}")
            return None
    
    def save_to_database(self, weather_data: Dict[str, Any]) -> bool:
        """
        Save weather data to database
        
        Args:
            weather_data: Parsed weather dict
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO weather (
                city, temperature_c, feels_like_c, temp_min_c, temp_max_c,
                humidity_percent, weather_main, weather_description,
                wind_speed_ms, clouds_percent, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_data['city_name'],
                weather_data['temp'],
                weather_data['feels_like'],
                weather_data['temp_min'],
                weather_data['temp_max'],
                weather_data['humidity'],
                weather_data['weather_main'],
                weather_data['weather_desc'],
                weather_data['wind_speed'],
                weather_data['clouds'],
                weather_data['timestamp']
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Saved weather data for {weather_data['city_name']}")
            return True
        
        except sqlite3.Error as e:
            logger.error(f"Database error saving {weather_data['city_name']}: {str(e)}")
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error saving {weather_data['city_name']}: {str(e)}")
            return False
    
    def collect_all(self) -> Dict[str, int]:
        """
        Collect weather data for all cities
        
        Returns:
            Dict with success/failure counts
        """
        stats = {
            'total': len(CITIES),
            'successful': 0,
            'failed': 0,
            'invalid': 0
        }
        
        logger.info(f"Starting weather collection for {stats['total']} cities")
        logger.info(f"Estimated time: ~{stats['total'] * RATE_LIMIT_DELAY:.0f} seconds")
        
        print(f"\n{'='*70}")
        print(f"🌍 Collecting weather data for {stats['total']} cities worldwide...")
        print(f"⏱️  Estimated time: ~{stats['total'] * RATE_LIMIT_DELAY / 60:.1f} minutes")
        print(f"{'='*70}\n")
        
        for city in CITIES:
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
            
            # Fetch data
            data = self.fetch_weather(city)
            
            if data is None:
                print(f"❌ {city:20s} | Failed to fetch")
                stats['failed'] += 1
                continue
            
            # Parse and validate
            parsed = self.parse_weather_data(data)
            
            if parsed is None:
                print(f"⚠️  {city:20s} | Invalid data")
                stats['invalid'] += 1
                continue
            
            # Save to database
            if self.save_to_database(parsed):
                print(f"✅ {parsed['city_name']:20s} | {parsed['temp']:5.1f}°C | {parsed['weather_desc']}")
                stats['successful'] += 1
            else:
                print(f"❌ {city:20s} | Database error")
                stats['failed'] += 1
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 Collection Summary:")
        print(f"   Total cities: {stats['total']}")
        print(f"   ✅ Successful: {stats['successful']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print(f"   ⚠️  Invalid: {stats['invalid']}")
        print(f"   Success rate: {stats['successful']/stats['total']*100:.1f}%")
        print(f"{'='*70}\n")
        
        logger.info(f"Collection complete: {stats['successful']}/{stats['total']} successful")
        
        return stats


def main():
    """Main execution function"""
    try:
        # Validate API key
        if not API_KEY:
            logger.error("API key not found!")
            print("\n❌ ERROR: OPENWEATHER_API_KEY not configured")
            print("Get your free API key from: https://openweathermap.org/api")
            return 1
        
        # Create collector
        collector = WeatherCollector(API_KEY)
        
        # Collect data
        stats = collector.collect_all()
        
        # Exit code based on success rate
        if stats['successful'] == 0:
            logger.error("No data collected successfully")
            return 1
        elif stats['successful'] < stats['total'] * 0.5:
            logger.warning("Less than 50% success rate")
            return 1
        else:
            logger.info("Collection completed successfully")
            return 0
    
    except KeyboardInterrupt:
        logger.warning("Collection interrupted by user")
        print("\n\n⚠️  Collection interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Fatal error: {str(e)}")
        return 1


if __name__ == '__main__':
    exit(main())
