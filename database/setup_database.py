"""
Hermes Database Setup
Creates tables for all data layers
"""

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'hermes.db'

def create_database():
    """
    Create the Hermes database and all tables.
    """
    print("=" * 70)
    print("HERMES Database Setup")
    print("=" * 70)
    print()
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print(f"📁 Database location: {os.path.abspath(DATABASE_PATH)}")
    print()
    
    # ========================================
    # MARKETS LAYER
    # ========================================
    
    print("Creating markets tables...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            UNIQUE(date, symbol)
        )
    ''')
    
    # Index for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stocks_date ON stocks(date)')
    
    print("   ✅ stocks table created")
    
    # ========================================
    # SPACE LAYER
    # ========================================
    
    print("Creating space tables...")
    
    # ISS Positions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iss_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed_kmh REAL,
            altitude_km REAL
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_iss_timestamp ON iss_positions(timestamp)')
    
    print("   ✅ iss_positions table created")
    
    # Near-Earth Objects
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS near_earth_objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            neo_id TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            diameter_min_m REAL,
            diameter_max_m REAL,
            is_hazardous INTEGER,
            miss_distance_km REAL,
            miss_distance_lunar REAL,
            velocity_kmh REAL,
            orbiting_body TEXT,
            UNIQUE(neo_id, date)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_neo_date ON near_earth_objects(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_neo_hazardous ON near_earth_objects(is_hazardous)')
    
    print("   ✅ near_earth_objects table created")
    
    # Solar Flares
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solar_flares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            begin_time TEXT NOT NULL,
            peak_time TEXT,
            end_time TEXT,
            class_type TEXT NOT NULL,
            source_location TEXT,
            active_region TEXT,
            linked_events INTEGER,
            UNIQUE(begin_time, class_type)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_solar_begin_time ON solar_flares(begin_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_solar_class ON solar_flares(class_type)')
    
    print("   ✅ solar_flares table created")
    
    # ========================================
    # ENVIRONMENT LAYER
    # ========================================
    
    print("Creating environment tables...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT,
            temperature_c REAL,
            feels_like_c REAL,
            temp_min_c REAL,
            temp_max_c REAL,
            pressure_hpa REAL,
            humidity_percent INTEGER,
            weather_main TEXT,
            weather_description TEXT,
            wind_speed_ms REAL,
            clouds_percent INTEGER,
            latitude REAL,
            longitude REAL
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_city ON weather(city)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather(timestamp)')
    
    print("   ✅ weather table created")
    
    # ========================================
    # SOCIAL LAYER
    # ========================================
    
    print("Creating social tables...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            published TEXT,
            summary TEXT,
            UNIQUE(link)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_source ON news(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news(timestamp)')
    
    print("   ✅ news table created")
    
    # ========================================
    # METADATA TABLE
    # ========================================
    
    print("Creating metadata table...")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            layer TEXT NOT NULL,
            collector TEXT NOT NULL,
            status TEXT NOT NULL,
            records_collected INTEGER,
            error_message TEXT
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_timestamp ON collection_metadata(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metadata_layer ON collection_metadata(layer)')
    
    print("   ✅ collection_metadata table created")
    
    # Commit changes
    conn.commit()
    
    print()
    print("=" * 70)
    print("✅ Database setup complete!")
    print("=" * 70)
    print()
    
    # Show table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"📊 Created {len(tables)} tables:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]} ({count} rows)")
    
    print()
    print(f"🗄️  Database ready at: {os.path.abspath(DATABASE_PATH)}")
    print()
    
    conn.close()

def main():
    """Main function"""
    if os.path.exists(DATABASE_PATH):
        response = input(f"⚠️  Database '{DATABASE_PATH}' already exists. Recreate? (y/n): ").strip().lower()
        if response == 'y':
            os.remove(DATABASE_PATH)
            print(f"🗑️  Deleted existing database")
            print()
        else:
            print("Keeping existing database")
            print()
    
    create_database()

if __name__ == "__main__":
    main()