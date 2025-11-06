"""
Database Initialization Script
Creates all necessary tables in PostgreSQL
"""

import os
import sys
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL schemas for all tables
SCHEMAS = {
    'stocks': """
        CREATE TABLE IF NOT EXISTS stocks (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            open DECIMAL(10, 2),
            high DECIMAL(10, 2),
            low DECIMAL(10, 2),
            close DECIMAL(10, 2),
            volume BIGINT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        )
    """,
    
    'iss_positions': """
        CREATE TABLE IF NOT EXISTS iss_positions (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            altitude DECIMAL(10, 2),
            velocity DECIMAL(10, 2),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(timestamp)
        )
    """,
    
    'near_earth_objects': """
        CREATE TABLE IF NOT EXISTS near_earth_objects (
            id SERIAL PRIMARY KEY,
            neo_id VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            date DATE NOT NULL,
            estimated_diameter_min DECIMAL(10, 2),
            estimated_diameter_max DECIMAL(10, 2),
            relative_velocity DECIMAL(15, 2),
            miss_distance DECIMAL(20, 2),
            is_potentially_hazardous BOOLEAN,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(neo_id, date)
        )
    """,
    
    'solar_flares': """
        CREATE TABLE IF NOT EXISTS solar_flares (
            id SERIAL PRIMARY KEY,
            flare_id VARCHAR(50) NOT NULL,
            begin_time TIMESTAMP,
            peak_time TIMESTAMP,
            end_time TIMESTAMP,
            class_type VARCHAR(10),
            source_location VARCHAR(50),
            active_region_num VARCHAR(20),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(flare_id)
        )
    """,
    
    'weather': """
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(10),
            timestamp TIMESTAMP NOT NULL,
            temperature DECIMAL(5, 2),
            feels_like DECIMAL(5, 2),
            temp_min DECIMAL(5, 2),
            temp_max DECIMAL(5, 2),
            pressure INTEGER,
            humidity INTEGER,
            description VARCHAR(255),
            wind_speed DECIMAL(5, 2),
            clouds INTEGER,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, timestamp)
        )
    """,
    
    'news': """
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT,
            source VARCHAR(255),
            published_at TIMESTAMP,
            author VARCHAR(255),
            category VARCHAR(50),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, source)
        )
    """,
    
    'countries': """
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(10) UNIQUE,
            capital VARCHAR(255),
            region VARCHAR(100),
            subregion VARCHAR(100),
            population BIGINT,
            area DECIMAL(15, 2),
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            timezones TEXT,
            currencies TEXT,
            languages TEXT,
            flag_url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code)
        )
    """,
    
    'commodities': """
        CREATE TABLE IF NOT EXISTS commodities (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(50) NOT NULL,
            timestamp DATE NOT NULL,
            price DECIMAL(15, 4),
            unit VARCHAR(20),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        )
    """,
    
    'forex': """
        CREATE TABLE IF NOT EXISTS forex (
            id SERIAL PRIMARY KEY,
            pair VARCHAR(20) NOT NULL,
            from_currency VARCHAR(10) NOT NULL,
            to_currency VARCHAR(10) NOT NULL,
            exchange_rate DECIMAL(15, 6),
            timestamp TIMESTAMP NOT NULL,
            bid_price DECIMAL(15, 6),
            ask_price DECIMAL(15, 6),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pair, timestamp)
        )
    """,
    
    'earthquakes': """
        CREATE TABLE IF NOT EXISTS earthquakes (
            id SERIAL PRIMARY KEY,
            earthquake_id VARCHAR(100) UNIQUE NOT NULL,
            magnitude DECIMAL(3, 1),
            place VARCHAR(500),
            timestamp TIMESTAMP,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            depth_km DECIMAL(10, 2),
            magnitude_type VARCHAR(10),
            event_type VARCHAR(50),
            tsunami BOOLEAN DEFAULT FALSE,
            significance INTEGER,
            url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'storms': """
        CREATE TABLE IF NOT EXISTS storms (
            id SERIAL PRIMARY KEY,
            storm_id VARCHAR(100) UNIQUE NOT NULL,
            title VARCHAR(500),
            timestamp TIMESTAMP,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            status VARCHAR(50),
            category VARCHAR(100),
            source_url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'wildfires': """
        CREATE TABLE IF NOT EXISTS wildfires (
            id SERIAL PRIMARY KEY,
            fire_id VARCHAR(100) UNIQUE NOT NULL,
            title VARCHAR(500),
            timestamp TIMESTAMP,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            status VARCHAR(50),
            source_url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    
    'economic_indicators': """
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id SERIAL PRIMARY KEY,
            country VARCHAR(100) NOT NULL,
            indicator_type VARCHAR(100) NOT NULL,
            indicator_name VARCHAR(200),
            series_id VARCHAR(100) NOT NULL,
            timestamp DATE NOT NULL,
            value DECIMAL(20, 4),
            unit VARCHAR(100),
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(series_id, timestamp)
        )
    """
}

def initialize_database():
    """Initialize all database tables"""
    
    # Get database URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set!")
        sys.exit(1)
    
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Create each table
        for table_name, schema in SCHEMAS.items():
            logger.info(f"Creating table: {table_name}")
            cur.execute(schema)
            logger.info(f"✓ Table {table_name} created successfully")
        
        # Commit changes
        conn.commit()
        logger.info("✓ All tables created successfully!")
        
        # Show table list
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        logger.info("\nExisting tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Hermes Database Initialization ===\n")
    success = initialize_database()
    
    if success:
        logger.info("\n✓ Database initialization complete!")
    else:
        logger.error("\n✗ Database initialization failed!")
        sys.exit(1)
