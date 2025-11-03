#!/usr/bin/env python3
"""
Weather Data Collection Script for 50 Cities
Collects weather data for all major cities worldwide and stores in SQLite database
"""

import requests
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenWeather API key (get from environment variable)
API_KEY = os.getenv('OPENWEATHER_API_KEY')

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

def collect_weather():
    """Collect weather data for all cities"""
    
    if not API_KEY:
        print("ERROR: OPENWEATHER_API_KEY not found in environment variables!")
        print("Get your free API key from: https://openweathermap.org/api")
        return
    
    # Connect to database
    conn = sqlite3.connect('hermes.db')
    cursor = conn.cursor()
    
    # Create weather table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        temperature_c REAL,
        feels_like_c REAL,
        temp_min_c REAL,
        temp_max_c REAL,
        humidity_percent INTEGER,
        weather_main TEXT,
        weather_description TEXT,
        wind_speed_ms REAL,
        clouds_percent INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    successful = 0
    failed = 0
    
    print(f"🌍 Collecting weather data for {len(CITIES)} cities worldwide...")
    print("-" * 70)
    
    for city in CITIES:
        try:
            # API request
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract data
                city_name = data['name']
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                temp_min = data['main']['temp_min']
                temp_max = data['main']['temp_max']
                humidity = data['main']['humidity']
                weather_main = data['weather'][0]['main']
                weather_desc = data['weather'][0]['description']
                wind_speed = data['wind']['speed']
                clouds = data['clouds']['all']
                timestamp = datetime.now().isoformat()
                
                # Insert into database
                cursor.execute('''
                INSERT INTO weather (
                    city, temperature_c, feels_like_c, temp_min_c, temp_max_c,
                    humidity_percent, weather_main, weather_description,
                    wind_speed_ms, clouds_percent, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    city_name, temp, feels_like, temp_min, temp_max,
                    humidity, weather_main, weather_desc,
                    wind_speed, clouds, timestamp
                ))
                
                print(f"✅ {city_name:20s} | {temp:5.1f}°C | {weather_desc}")
                successful += 1
                
            else:
                print(f"❌ {city:20s} | Error: {response.status_code}")
                failed += 1
                
        except Exception as e:
            print(f"❌ {city:20s} | Error: {str(e)[:50]}")
            failed += 1
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("-" * 70)
    print(f"✅ Successfully collected: {successful}/{len(CITIES)} cities")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(CITIES)} cities")
    print(f"💾 Data saved to hermes.db")

if __name__ == '__main__':
    collect_weather()
