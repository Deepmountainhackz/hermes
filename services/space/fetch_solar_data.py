import os
import requests
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load API key
load_dotenv()
NASA_API_KEY = os.getenv('NASA_API_KEY')

DATABASE_PATH = 'hermes.db'

def fetch_solar_flares(days_back=30):
    """
    Fetch recent solar flare activity from NASA DONKI.
    """
    print("=" * 70)
    print("HERMES Space Tracker - Solar Flare Monitor (Database Mode)")
    print("=" * 70)
    print()
    
    # Date range
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    url = f"https://api.nasa.gov/DONKI/FLR?startDate={start_date}&endDate={end_date}&api_key={NASA_API_KEY}"
    
    print(f"☀️  Fetching solar flare data from {start_date} to {end_date}...")
    print()
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        flares = response.json()
        
        if not flares:
            print("✅ No solar flares detected in this period")
            print("   (Quiet sun - good news!)")
            print()
            return None
        
        # Parse flare data
        flare_list = []
        for flare in flares:
            flare_list.append({
                'begin_time': flare['beginTime'],
                'peak_time': flare.get('peakTime', None),
                'end_time': flare.get('endTime', None),
                'class_type': flare['classType'],
                'source_location': flare.get('sourceLocation', 'Unknown'),
                'active_region': str(flare.get('activeRegionNum', 'N/A')),
                'linked_events': len(flare.get('linkedEvents', []))
            })
        
        df = pd.DataFrame(flare_list)
        df = df.sort_values('begin_time', ascending=False)
        
        # Display results
        print(f"⚠️  Found {len(df)} solar flares")
        print()
        
        x_class = df[df['class_type'].str.startswith('X')]
        m_class = df[df['class_type'].str.startswith('M')]
        c_class = df[df['class_type'].str.startswith('C')]
        
        print("📊 Classification:")
        print(f"   X-Class (Extreme): {len(x_class)} 🔴")
        print(f"   M-Class (Strong):  {len(m_class)} 🟠")
        print(f"   C-Class (Moderate): {len(c_class)} 🟡")
        print()
        
        if len(x_class) > 0:
            print("🔴 X-CLASS FLARES:")
            for idx, flare in x_class.iterrows():
                print(f"   {flare['class_type']} - {flare['begin_time']}")
        
        # Save to database
        conn = sqlite3.connect(DATABASE_PATH)
        
        try:
            df.to_sql('solar_flares', conn, if_exists='append', index=False)
            print()
            print(f"✅ Saved {len(df)} solar flare records to database")
        except sqlite3.IntegrityError:
            print()
            print(f"⚠️  Some solar flare data already exists in database (skipped duplicates)")
        finally:
            conn.close()
        
        print()
        
        return df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        return None

def fetch_geomagnetic_storms(days_back=30):
    """
    Fetch geomagnetic storm data.
    """
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    url = f"https://api.nasa.gov/DONKI/GST?startDate={start_date}&endDate={end_date}&api_key={NASA_API_KEY}"
    
    print("🌍 Checking for geomagnetic storms...")
    print()
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        storms = response.json()
        
        if not storms:
            print("✅ No geomagnetic storms detected")
            print()
            return None
        
        print(f"⚠️  Found {len(storms)} geomagnetic storm(s)")
        print()
        
        for storm in storms[:3]:
            print(f"   Storm: {storm.get('gstID', 'N/A')}")
            print(f"   Start: {storm.get('startTime', 'N/A')}")
            print()
        
        return storms
        
    except Exception as e:
        print(f"⚠️  Could not fetch storm data")
        print()
        return None

def main():
    """Main function"""
    days = 30
    fetch_solar_flares(days_back=days)
    fetch_geomagnetic_storms(days_back=days)
    
    print("=" * 70)
    print("Solar activity check complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()