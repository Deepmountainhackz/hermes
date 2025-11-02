import os
import sys
import requests
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def is_interactive():
    """Check if running in an interactive terminal"""
    return sys.stdin.isatty()

def connect_db():
    """Connect to the Hermes database"""
    return sqlite3.connect('hermes.db')

def save_to_database(neo_data):
    """Save NEO data to SQLite database"""
    conn = connect_db()
    cursor = conn.cursor()
    
    saved_count = 0
    duplicate_count = 0
    
    for data in neo_data:
        try:
            cursor.execute('''
                INSERT INTO near_earth_objects (
                    date, neo_id, name, diameter_min_m, diameter_max_m,
                    is_hazardous, velocity_kmh, miss_distance_km,
                    miss_distance_lunar, orbiting_body
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['date'],
                data['neo_id'],
                data['name'],
                data['diameter_min_m'],
                data['diameter_max_m'],
                data['is_hazardous'],
                data['velocity_kmh'],
                data['miss_distance_km'],
                data['miss_distance_lunar'],
                data['orbiting_body']
            ))
            saved_count += 1
        except sqlite3.IntegrityError:
            duplicate_count += 1
            continue
    
    conn.commit()
    conn.close()
    return saved_count, duplicate_count

def fetch_neo_data(api_key, days=7):
    """Fetch Near-Earth Object data from NASA API"""
    base_url = "https://api.nasa.gov/neo/rest/v1/feed"
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days)
    
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'api_key': api_key
    }
    
    print(f"\n☄️  Fetching NEO data from {params['start_date']} to {params['end_date']}...")
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        neo_data = []
        total_neos = data['element_count']
        
        print(f"  ✓ Found {total_neos} near-earth objects")
        
        for date, neos in data['near_earth_objects'].items():
            for neo in neos:
                close_approach = neo['close_approach_data'][0]
                
                neo_entry = {
                    'date': date,
                    'neo_id': neo['id'],
                    'name': neo['name'],
                    'diameter_min_m': neo['estimated_diameter']['meters']['estimated_diameter_min'],
                    'diameter_max_m': neo['estimated_diameter']['meters']['estimated_diameter_max'],
                    'is_hazardous': 1 if neo['is_potentially_hazardous_asteroid'] else 0,
                    'velocity_kmh': float(close_approach['relative_velocity']['kilometers_per_hour']),
                    'miss_distance_km': float(close_approach['miss_distance']['kilometers']),
                    'miss_distance_lunar': float(close_approach['miss_distance']['lunar']),
                    'orbiting_body': close_approach['orbiting_body']
                }
                
                neo_data.append(neo_entry)
        
        return neo_data
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching NEO data: {e}")
        return []

def main():
    print("="*70)
    print("Near-Earth Object Monitor")
    print("="*70)
    
    # Get API key
    api_key = os.getenv('NASA_API_KEY')
    if not api_key:
        print("❌ Error: NASA_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Default: 7 days
    days = 7
    print(f"\nFetching NEO data for the next {days} days")
    
    # Fetch NEO data
    neo_data = fetch_neo_data(api_key, days)
    
    if not neo_data:
        print("\n❌ No NEO data collected")
        return
    
    # Save to database
    print(f"\n💾 Saving to database...")
    saved_count, duplicate_count = save_to_database(neo_data)
    print(f"✅ Saved {saved_count} new NEO records to database")
    
    if duplicate_count > 0:
        print(f"⚠️  Skipped {duplicate_count} duplicate records")
    
    # Record collection metadata
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collection_metadata (timestamp, layer, collector, status, records_collected)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'space', 'neo', 'success', saved_count))
    conn.commit()
    conn.close()
    
    print("\n✅ NEO collection complete!")

if __name__ == "__main__":
    main()
