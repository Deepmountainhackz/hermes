import os
import sys
import requests
from datetime import datetime
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def is_interactive():
    """Check if running in an interactive terminal"""
    return sys.stdin.isatty()

def get_user_input(prompt, default='y'):
    """Get user input if interactive, otherwise use default"""
    if is_interactive():
        return input(prompt).strip().lower()
    return default

def connect_db():
    """Connect to the Hermes database"""
    return sqlite3.connect('hermes.db')

def save_to_database(weather_data):
    """Save weather data to SQLite database"""
    conn = connect_db()
    cursor = conn.cursor()
    
    for data in weather_data:
        cursor.execute('''
            INSERT INTO weather (
                timestamp, city, country, temperature_c, feels_like_c,
                temp_min_c, temp_max_c, pressure_hpa, humidity_percent,
                weather_main, weather_description, wind_speed_ms,
                clouds_percent, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['city'],
            data['country'],
            data['temperature_c'],
            data['feels_like_c'],
            data['temp_min_c'],
            data['temp_max_c'],
            data['pressure_hpa'],
            data['humidity_percent'],
            data['weather_main'],
            data['weather_description'],
            data['wind_speed_ms'],
            data['clouds_percent'],
            data['latitude'],
            data['longitude']
        ))
    
    conn.commit()
    records_saved = cursor.rowcount
    conn.close()
    return records_saved

def fetch_weather(api_key, cities):
    """Fetch weather data from OpenWeatherMap API"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    weather_data = []
    
    print(f"\n🌦️  Fetching weather data for {len(cities)} cities...")
    
    for city in cities:
        try:
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric'
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather_entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature_c': data['main']['temp'],
                'feels_like_c': data['main']['feels_like'],
                'temp_min_c': data['main']['temp_min'],
                'temp_max_c': data['main']['temp_max'],
                'pressure_hpa': data['main']['pressure'],
                'humidity_percent': data['main']['humidity'],
                'weather_main': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'wind_speed_ms': data['wind']['speed'],
                'clouds_percent': data['clouds']['all'],
                'latitude': data['coord']['lat'],
                'longitude': data['coord']['lon']
            }
            
            weather_data.append(weather_entry)
            print(f"  ✓ {city}: {data['main']['temp']:.1f}°C - {data['weather'][0]['description']}")
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error fetching data for {city}: {e}")
            continue
    
    return weather_data

def main():
    print("="*70)
    print("Weather Monitor")
    print("="*70)
    
    # Get API key
    api_key = os.getenv('OPENWEATHER_KEY')
    if not api_key:
        print("❌ Error: OPENWEATHER_KEY not found in environment variables")
        sys.exit(1)
    
    # Default cities
    default_cities = ['London', 'New York', 'Tokyo', 'Sydney', 'Dubai', 'Zurich']
    
    print(f"\nDefault cities: {', '.join(default_cities)}")
    
    # Ask user if they want to use default cities (auto-yes in automation)
    use_default = get_user_input("Use default cities? (y/n): ", 'y')
    
    if use_default == 'y':
        cities = default_cities
    else:
        custom_input = input("Enter cities separated by commas: ")
        cities = [city.strip() for city in custom_input.split(',')]
    
    # Fetch weather data
    weather_data = fetch_weather(api_key, cities)
    
    if not weather_data:
        print("\n❌ No weather data collected")
        return
    
    # Save to database
    print(f"\n💾 Saving to database...")
    records_saved = save_to_database(weather_data)
    print(f"✅ Saved {records_saved} weather records to database")
    
    # Record collection metadata
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collection_metadata (timestamp, layer, collector, status, records_collected)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'environment', 'weather', 'success', len(weather_data)))
    conn.commit()
    conn.close()
    
    print("\n✅ Weather collection complete!")

if __name__ == "__main__":
    main()
