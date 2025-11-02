import sqlite3
import pandas as pd
from datetime import datetime
from tabulate import tabulate

def connect_db():
    """Connect to the Hermes database"""
    return sqlite3.connect('hermes.db')

def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def query_latest_stocks():
    """Get latest stock prices with daily changes"""
    print_section_header("📈 LATEST STOCK PRICES")
    
    conn = connect_db()
    query = """
    SELECT 
        symbol,
        date,
        close as price,
        volume,
        ROUND(((close - open) / open * 100), 2) as daily_change_pct
    FROM stocks
    WHERE date = (SELECT MAX(date) FROM stocks)
    ORDER BY symbol
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ No stock data found")
        return
    
    # Format the output
    df['volume'] = df['volume'].apply(lambda x: f"{x:,.0f}")
    df['daily_change_pct'] = df['daily_change_pct'].apply(lambda x: f"{x:+.2f}%")
    
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def query_iss_position():
    """Get current ISS position"""
    print_section_header("🛰️  INTERNATIONAL SPACE STATION")
    
    conn = connect_db()
    query = """
    SELECT 
        latitude,
        longitude,
        altitude_km,
        speed_kmh,
        timestamp
    FROM iss_positions
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ No ISS data found")
        return
    
    print(f"📍 Position: {df['latitude'][0]:.4f}°, {df['longitude'][0]:.4f}°")
    print(f"🚀 Altitude: {df['altitude_km'][0]:.2f} km")
    print(f"⚡ Speed: {df['speed_kmh'][0]:,.2f} km/h")
    print(f"🕐 Last Updated: {df['timestamp'][0]}")

def query_near_earth_objects():
    """Get upcoming near-earth objects"""
    print_section_header("☄️  NEAR-EARTH OBJECTS (Next 7 Days)")
    
    conn = connect_db()
    query = """
    SELECT 
        name,
        ROUND(diameter_min_m / 1000.0, 3) as min_diameter_km,
        ROUND(diameter_max_m / 1000.0, 3) as max_diameter_km,
        ROUND(velocity_kmh, 0) as velocity_kmh,
        ROUND(miss_distance_km, 0) as miss_distance_km,
        is_hazardous,
        date as close_approach_date
    FROM near_earth_objects
    WHERE date(date) >= date('now')
    ORDER BY date ASC
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ No NEO data found")
        return
    
    # Format hazardous column
    df['is_hazardous'] = df['is_hazardous'].apply(
        lambda x: '⚠️  YES' if x == 1 else '✅ No'
    )
    
    # Format numbers
    df['velocity_kmh'] = df['velocity_kmh'].apply(lambda x: f"{x:,.0f}")
    df['miss_distance_km'] = df['miss_distance_km'].apply(lambda x: f"{x:,.0f}")
    
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def query_solar_flares():
    """Get recent solar flares"""
    print_section_header("☀️  SOLAR FLARES (Last 7 Days)")
    
    conn = connect_db()
    query = """
    SELECT 
        class_type,
        begin_time,
        peak_time,
        end_time,
        source_location
    FROM solar_flares
    WHERE date(begin_time) >= date('now', '-7 days')
    ORDER BY begin_time DESC
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ No solar flare data found (This is normal - flares are rare!)")
        return
    
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def query_weather():
    """Get current weather for all cities"""
    print_section_header("🌦️  CURRENT WEATHER")
    
    conn = connect_db()
    query = """
    SELECT 
        city,
        ROUND(temperature_c, 1) as temp_c,
        ROUND(feels_like_c, 1) as feels_like_c,
        humidity_percent as humidity,
        weather_description as description,
        wind_speed_ms,
        timestamp
    FROM weather
    WHERE timestamp = (SELECT MAX(timestamp) FROM weather)
    ORDER BY city
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ No weather data found")
        return
    
    # Format temperature with degree symbol
    df['temp_c'] = df['temp_c'].apply(lambda x: f"{x}°C")
    df['feels_like_c'] = df['feels_like_c'].apply(lambda x: f"{x}°C")
    df['humidity'] = df['humidity'].apply(lambda x: f"{x}%")
    df['wind_speed_ms'] = df['wind_speed_ms'].apply(lambda x: f"{x} m/s")
    
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def query_latest_news():
    """Get latest news headlines"""
    print_section_header("📰 LATEST NEWS HEADLINES")
    
    conn = connect_db()
    query = """
    SELECT 
        source,
        title,
        published
    FROM news
    ORDER BY published DESC
    LIMIT 15
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("❌ No news data found")
        return
    
    # Print news in a more readable format
    for idx, row in df.iterrows():
        print(f"[{row['source']}] {row['title']}")
        print(f"   └─ {row['published']}\n")

def query_database_stats():
    """Get overall database statistics"""
    print_section_header("📊 DATABASE STATISTICS")
    
    conn = connect_db()
    
    stats = {
        'Stock Records': pd.read_sql_query("SELECT COUNT(*) as count FROM stocks", conn)['count'][0],
        'ISS Positions': pd.read_sql_query("SELECT COUNT(*) as count FROM iss_positions", conn)['count'][0],
        'Near-Earth Objects': pd.read_sql_query("SELECT COUNT(*) as count FROM near_earth_objects", conn)['count'][0],
        'Solar Flares': pd.read_sql_query("SELECT COUNT(*) as count FROM solar_flares", conn)['count'][0],
        'Weather Records': pd.read_sql_query("SELECT COUNT(*) as count FROM weather", conn)['count'][0],
        'News Articles': pd.read_sql_query("SELECT COUNT(*) as count FROM news", conn)['count'][0],
    }
    
    # Get date range
    try:
        date_query = """
        SELECT 
            MIN(timestamp) as first_collection,
            MAX(timestamp) as last_collection
        FROM collection_metadata
        """
        date_df = pd.read_sql_query(date_query, conn)
    except:
        date_df = pd.DataFrame()
    
    conn.close()
    
    print(f"Total Records Collected:")
    for key, value in stats.items():
        print(f"  • {key}: {value:,}")
    
    if not date_df.empty and date_df['first_collection'][0]:
        print(f"\n📅 Data Range:")
        print(f"  • First Collection: {date_df['first_collection'][0]}")
        print(f"  • Last Collection: {date_df['last_collection'][0]}")

def main():
    """Main function to run all queries"""
    print("\n" + "="*80)
    print("  🌐 HERMES INTELLIGENCE PLATFORM - DATA EXPLORER")
    print("="*80)
    
    try:
        # Database stats overview
        query_database_stats()
        
        # Query each data layer
        query_latest_stocks()
        query_iss_position()
        query_near_earth_objects()
        query_solar_flares()
        query_weather()
        query_latest_news()
        
        print("\n" + "="*80)
        print("  ✅ Query Complete!")
        print("="*80 + "\n")
        
    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
