"""Weather Repository - Database operations for weather data."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from core.database import DatabaseManager
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class WeatherRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_tables(self) -> None:
        """Create the weather table if it doesn't exist."""
        create_query = """
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(3),
            temperature DECIMAL(5, 2),
            feels_like DECIMAL(5, 2),
            humidity INT,
            pressure INT,
            wind_speed DECIMAL(5, 2),
            description VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, timestamp)
        );

        CREATE INDEX IF NOT EXISTS idx_weather_city ON weather(city);
        CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather(timestamp);
        """

        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_query)
                conn.commit()
            logger.info("Weather table and indexes created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating weather table: {e}")
            raise DatabaseError(f"Failed to create weather table: {e}")
    
    def insert_bulk_weather_data(self, weather_data_list: List[Dict[str, Any]]) -> int:
        if not weather_data_list:
            return 0
        
        insert_query = """
        INSERT INTO weather (city, country, temperature, feels_like, humidity, pressure, wind_speed, description, timestamp)
        VALUES (%(city)s, %(country)s, %(temperature)s, %(feels_like)s, %(humidity)s, %(pressure)s, %(wind_speed)s, %(description)s, %(timestamp)s)
        ON CONFLICT (city, timestamp) DO UPDATE SET
            temperature = EXCLUDED.temperature,
            feels_like = EXCLUDED.feels_like,
            humidity = EXCLUDED.humidity,
            pressure = EXCLUDED.pressure,
            wind_speed = EXCLUDED.wind_speed,
            description = EXCLUDED.description
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    for data in weather_data_list:
                        cur.execute(insert_query, data)
                conn.commit()
            return len(weather_data_list)
        except Exception as e:
            raise DatabaseError(f"Failed to insert weather data: {e}")
    
    def get_all_latest_weather(self) -> List[Dict[str, Any]]:
        query = """
        WITH latest_weather AS (
            SELECT city, MAX(timestamp) as max_timestamp
            FROM weather GROUP BY city
        )
        SELECT w.city, w.country, w.temperature, w.feels_like, w.humidity, w.pressure, w.wind_speed, w.description, w.timestamp
        FROM weather w
        INNER JOIN latest_weather l ON w.city = l.city AND w.timestamp = l.max_timestamp
        ORDER BY w.city
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    return [{
                        'city': r[0], 'country': r[1], 'temperature': float(r[2]) if r[2] else None,
                        'feels_like': float(r[3]) if r[3] else None, 'humidity': r[4], 'pressure': r[5],
                        'wind_speed': float(r[6]) if r[6] else None, 'description': r[7], 'timestamp': r[8]
                    } for r in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to get weather data: {e}")
