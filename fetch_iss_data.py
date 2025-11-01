import requests
import pandas as pd
from datetime import datetime
import time

def fetch_iss_position():
    """
    Fetch current ISS position from Open Notify API.
    Returns position data or None if error.
    """
    url = "http://api.open-notify.org/iss-now.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['message'] == 'success':
            return {
                'timestamp': datetime.fromtimestamp(data['timestamp']),
                'latitude': float(data['iss_position']['latitude']),
                'longitude': float(data['iss_position']['longitude'])
            }
        else:
            print(f"❌ Unexpected response: {data}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def fetch_people_in_space():
    """
    Fetch number of people currently in space.
    """
    url = "http://api.open-notify.org/astros.json"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'number': data['number'],
            'people': [person['name'] for person in data['people']]
        }
    except Exception as e:
        print(f"❌ Error fetching astronaut data: {e}")
        return None

def track_iss(duration_minutes=5, interval_seconds=10):
    """
    Track ISS position over time and save to CSV.
    
    Args:
        duration_minutes: How long to track (default 5 minutes)
        interval_seconds: How often to fetch position (default 10 seconds)
    """
    print("=" * 60)
    print("HERMES Space Tracker - ISS Position Monitor")
    print("=" * 60)
    print()
    
    # Get astronaut info
    astro_data = fetch_people_in_space()
    if astro_data:
        print(f"👨‍🚀 People in space right now: {astro_data['number']}")
        for name in astro_data['people']:
            print(f"   - {name}")
        print()
    
    positions = []
    end_time = time.time() + (duration_minutes * 60)
    
    print(f"📡 Tracking ISS position for {duration_minutes} minutes...")
    print(f"   (Fetching every {interval_seconds} seconds)")
    print()
    
    try:
        while time.time() < end_time:
            position = fetch_iss_position()
            
            if position:
                positions.append(position)
                
                # Display current position
                print(f"🛰️  {position['timestamp'].strftime('%H:%M:%S')}")
                print(f"   Lat: {position['latitude']:>7.3f}°")
                print(f"   Lon: {position['longitude']:>7.3f}°")
                print()
                
            # Wait before next fetch
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tracking stopped by user")
    
    # Save to CSV
    if positions:
        df = pd.DataFrame(positions)
        
        # Add calculated fields
        df['speed_kmh'] = 27600  # ISS travels at ~27,600 km/h
        df['altitude_km'] = 408  # ISS orbits at ~408 km
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data_ISS_{timestamp}.csv"
        
        # Save
        df.to_csv(filename, index=False)
        print("=" * 60)
        print(f"✅ Saved {len(df)} position records to {filename}")
        print("=" * 60)
        print()
        
        # Show summary
        print("📊 Tracking Summary:")
        print(f"   Duration: {duration_minutes} minutes")
        print(f"   Records: {len(df)}")
        print(f"   Start: {df['timestamp'].iloc[0]}")
        print(f"   End: {df['timestamp'].iloc[-1]}")
        print(f"   Distance traveled: ~{int(27600 * duration_minutes / 60)} km")
        print()
        
        return df
    else:
        print("❌ No data collected")
        return None

def main():
    """
    Main function - quick ISS position check or extended tracking.
    """
    print("=" * 60)
    print("ISS Tracker Options:")
    print("=" * 60)
    print("1. Quick position check (single reading)")
    print("2. Track for 5 minutes (30 readings)")
    print("3. Track for 1 minute (6 readings) - RECOMMENDED FOR TESTING")
    print()
    
    choice = input("Enter choice (1-3) or press Enter for option 3: ").strip()
    
    if choice == "1":
        print("\n📡 Fetching current ISS position...\n")
        position = fetch_iss_position()
        if position:
            print(f"🛰️  ISS Position at {position['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Latitude:  {position['latitude']:>7.3f}°")
            print(f"   Longitude: {position['longitude']:>7.3f}°")
            print(f"   Speed: ~27,600 km/h")
            print(f"   Altitude: ~408 km")
    
    elif choice == "2":
        track_iss(duration_minutes=5, interval_seconds=10)
    
    else:  # Default to 1 minute
        track_iss(duration_minutes=1, interval_seconds=10)

if __name__ == "__main__":
    main()
    