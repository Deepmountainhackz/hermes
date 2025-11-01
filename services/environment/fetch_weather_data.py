import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()
OPENWEATHER_KEY = os.getenv('OPENWEATHER_KEY')

def fetch_weather_for_city(city_name):
    """
    Fetch current weather for a specific city.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant data
        weather_data = {
            'timestamp': datetime.now(),
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
        
        return weather_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {city_name}: {e}")
        return None
    except KeyError as e:
        print(f"❌ Unexpected data format for {city_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error for {city_name}: {e}")
        return None

def fetch_weather_for_cities(cities):
    """
    Fetch weather data for multiple cities.
    """
    print("=" * 70)
    print("HERMES Environment Tracker - Weather Monitor")
    print("=" * 70)
    print()
    
    all_weather = []
    
    for city in cities:
        print(f"🌡️  Fetching weather for {city}...")
        weather = fetch_weather_for_city(city)
        
        if weather:
            all_weather.append(weather)
            
            # Display current conditions
            print(f"   Temperature: {weather['temperature_c']:.1f}°C (feels like {weather['feels_like_c']:.1f}°C)")
            print(f"   Conditions: {weather['weather_description'].title()}")
            print(f"   Humidity: {weather['humidity_percent']}%")
            print(f"   Wind: {weather['wind_speed_ms']:.1f} m/s")
            print()
        else:
            print(f"   ⚠️  Failed to fetch data for {city}")
            print()
    
    if not all_weather:
        print("❌ No weather data collected")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_weather)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data_WEATHER_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    print("=" * 70)
    print(f"✅ Saved weather data for {len(df)} cities to {filename}")
    print("=" * 70)
    print()
    
    # Summary statistics
    print("📊 Weather Summary:")
    print(f"   Average Temperature: {df['temperature_c'].mean():.1f}°C")
    print(f"   Warmest: {df.loc[df['temperature_c'].idxmax(), 'city']} ({df['temperature_c'].max():.1f}°C)")
    print(f"   Coldest: {df.loc[df['temperature_c'].idxmin(), 'city']} ({df['temperature_c'].min():.1f}°C)")
    print(f"   Average Humidity: {df['humidity_percent'].mean():.0f}%")
    print()
    
    return df

def main():
    """Main function"""
    # Default cities - add your favorites!
    default_cities = [
        "London",
        "New York",
        "Tokyo",
        "Sydney",
        "Dubai",
        "Zurich"  # Added since you're in Switzerland!
    ]
    
    print("Weather Monitor")
    print("=" * 70)
    print()
    print("Default cities:", ", ".join(default_cities))
    print()
    
    custom = input("Use default cities? (y/n): ").strip().lower()
    
    if custom == 'n':
        print("\nEnter cities separated by commas (e.g., Paris, Berlin, Rome):")
        city_input = input("> ").strip()
        cities = [city.strip() for city in city_input.split(',')]
    else:
        cities = default_cities
    
    print()
    fetch_weather_for_cities(cities)

if __name__ == "__main__":
    main()