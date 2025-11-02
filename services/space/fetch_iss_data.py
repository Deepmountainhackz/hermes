import sys
import requests
from datetime import datetime
import sqlite3

def is_interactive():
    """Check if running in an interactive terminal"""
    return sys.stdin.isatty()

def connect_db():
    """Connect to the Hermes database"""
    return sqlite3.connect('hermes.db')

def save_to_database(iss_data):
    """Save ISS data to SQLite database"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO iss_positions (
            timestamp, latitude, longitude, altitude_km, speed_kmh
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        iss_data['timestamp'],
        iss_data['latitude'],
        iss_data['longitude'],
        iss_data['altitude_km'],
        iss_data['speed_kmh']
    ))
    
    conn.commit()
    conn.close()
    return 1

def fetch_iss_data():
    """Fetch current ISS position from API"""
    url = "http://api.open-notify.org/iss-now.json"
    
    print("\n🛰️  Fetching ISS position...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['message'] != 'success':
            print("❌ Error: API returned non-success message")
            return None
        
        position = data['iss_position']
        
        iss_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'latitude': float(position['latitude']),
            'longitude': float(position['longitude']),
            'altitude_km': 408.0,  # Average ISS altitude
            'speed_kmh': 27600.0   # Average ISS speed
        }
        
        print(f"  ✓ Position: {iss_data['latitude']:.4f}°, {iss_data['longitude']:.4f}°")
        print(f"  ✓ Altitude: {iss_data['altitude_km']} km")
        print(f"  ✓ Speed: {iss_data['speed_kmh']:,} km/h")
        
        return iss_data
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching ISS data: {e}")
        return None

def main():
    print("="*70)
    print("ISS Tracker")
    print("="*70)
    
    # Fetch ISS data
    iss_data = fetch_iss_data()
    
    if not iss_data:
        print("\n❌ No ISS data collected")
        sys.exit(1)
    
    # Save to database
    print(f"\n💾 Saving to database...")
    records_saved = save_to_database(iss_data)
    print(f"✅ Saved {records_saved} ISS position to database")
    
    # Record collection metadata
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collection_metadata (timestamp, layer, collector, status, records_collected)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'space', 'iss', 'success', 1))
    conn.commit()
    conn.close()
    
    print("\n✅ ISS tracking complete!")

if __name__ == "__main__":
    main()
