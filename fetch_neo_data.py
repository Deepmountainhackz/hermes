import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load API key
load_dotenv()
NASA_API_KEY = os.getenv('NASA_API_KEY')

def fetch_neo_data(days=7):
    """
    Fetch Near-Earth Objects (asteroids) approaching Earth.
    
    Args:
        days: Number of days to look ahead (default 7)
    """
    print("=" * 70)
    print("HERMES Space Tracker - Near-Earth Object Monitor")
    print("=" * 70)
    print()
    
    # Date range
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={NASA_API_KEY}"
    
    print(f"🔭 Fetching asteroid data from {start_date} to {end_date}...")
    print()
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Parse asteroid data
        all_asteroids = []
        
        for date, asteroids in data['near_earth_objects'].items():
            for asteroid in asteroids:
                close_approach = asteroid['close_approach_data'][0]
                
                all_asteroids.append({
                    'date': date,
                    'name': asteroid['name'],
                    'id': asteroid['id'],
                    'diameter_min_m': asteroid['estimated_diameter']['meters']['estimated_diameter_min'],
                    'diameter_max_m': asteroid['estimated_diameter']['meters']['estimated_diameter_max'],
                    'is_hazardous': asteroid['is_potentially_hazardous_asteroid'],
                    'miss_distance_km': float(close_approach['miss_distance']['kilometers']),
                    'miss_distance_lunar': float(close_approach['miss_distance']['lunar']),
                    'velocity_kmh': float(close_approach['relative_velocity']['kilometers_per_hour']),
                    'orbiting_body': close_approach['orbiting_body']
                })
        
        # Convert to DataFrame
        df = pd.DataFrame(all_asteroids)
        df = df.sort_values('miss_distance_km')
        
        # Display results
        print(f"✅ Found {len(df)} asteroids approaching Earth")
        print()
        
        # Show hazardous asteroids
        hazardous = df[df['is_hazardous'] == True]
        if len(hazardous) > 0:
            print(f"⚠️  {len(hazardous)} POTENTIALLY HAZARDOUS asteroids detected:")
            print()
            for idx, asteroid in hazardous.iterrows():
                print(f"   {asteroid['name']}")
                print(f"      Date: {asteroid['date']}")
                print(f"      Miss Distance: {asteroid['miss_distance_km']:,.0f} km ({asteroid['miss_distance_lunar']:.2f} LD)")
                print(f"      Diameter: {asteroid['diameter_min_m']:.0f}-{asteroid['diameter_max_m']:.0f} meters")
                print(f"      Velocity: {asteroid['velocity_kmh']:,.0f} km/h")
                print()
        else:
            print("✅ No potentially hazardous asteroids in this period")
            print()
        
        # Show closest approaches
        print("🎯 Top 5 Closest Approaches:")
        print()
        for idx, asteroid in df.head(5).iterrows():
            hazard_icon = "⚠️ " if asteroid['is_hazardous'] else "✅"
            print(f"   {hazard_icon} {asteroid['name']}")
            print(f"      Date: {asteroid['date']}")
            print(f"      Miss Distance: {asteroid['miss_distance_km']:,.0f} km ({asteroid['miss_distance_lunar']:.2f} LD)")
            print(f"      Size: {asteroid['diameter_max_m']:.0f} meters")
            print()
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data_NEO_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print("=" * 70)
        print(f"✅ Saved {len(df)} asteroid records to {filename}")
        print("=" * 70)
        print()
        print("📊 Summary:")
        print(f"   Total asteroids: {len(df)}")
        print(f"   Potentially hazardous: {len(hazardous)}")
        print(f"   Closest approach: {df['miss_distance_km'].min():,.0f} km")
        print(f"   Largest asteroid: {df['diameter_max_m'].max():,.0f} meters")
        print()
        
        # Fun fact
        moon_distance = 384400  # km
        closest_in_moon_distances = df['miss_distance_km'].min() / moon_distance
        print(f"💡 Fun fact: The closest asteroid will pass at {closest_in_moon_distances:.2f} times the Moon's distance")
        print(f"   (The Moon is {moon_distance:,} km away)")
        print()
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def main():
    """Main function"""
    print("How many days ahead should we check for asteroids?")
    print("(Default: 7 days, Max: 7 days per NASA API limits)")
    print()
    
    days_input = input("Enter number of days (1-7) or press Enter for 7: ").strip()
    
    if days_input:
        try:
            days = int(days_input)
            days = max(1, min(7, days))  # Clamp between 1 and 7
        except ValueError:
            days = 7
    else:
        days = 7
    
    print()
    fetch_neo_data(days=days)

if __name__ == "__main__":
    main()
    