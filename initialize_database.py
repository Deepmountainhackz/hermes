"""
Database Initialization Script
Creates all necessary tables in PostgreSQL using the new schema.
"""

import logging
import sys

from core.config import Config
from core.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL schemas for all tables - matches repository definitions
SCHEMAS = {
    'stocks': """
        DROP TABLE IF EXISTS stocks CASCADE;
        CREATE TABLE stocks (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            name VARCHAR(255),
            price DECIMAL(15, 4),
            change DECIMAL(15, 4),
            change_percent DECIMAL(10, 4),
            volume BIGINT,
            market_cap BIGINT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        );
        CREATE INDEX idx_stocks_symbol ON stocks(symbol);
        CREATE INDEX idx_stocks_timestamp ON stocks(timestamp);
    """,

    'forex': """
        DROP TABLE IF EXISTS forex CASCADE;
        CREATE TABLE forex (
            id SERIAL PRIMARY KEY,
            pair VARCHAR(10) NOT NULL,
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate DECIMAL(15, 8),
            bid DECIMAL(15, 8),
            ask DECIMAL(15, 8),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pair, timestamp)
        );
        CREATE INDEX idx_forex_pair ON forex(pair);
        CREATE INDEX idx_forex_timestamp ON forex(timestamp);
    """,

    'commodities': """
        DROP TABLE IF EXISTS commodities CASCADE;
        CREATE TABLE commodities (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            price DECIMAL(15, 4),
            change DECIMAL(15, 4),
            change_percent DECIMAL(10, 4),
            unit VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        );
        CREATE INDEX idx_commodities_symbol ON commodities(symbol);
        CREATE INDEX idx_commodities_timestamp ON commodities(timestamp);
    """,

    'weather': """
        DROP TABLE IF EXISTS weather CASCADE;
        CREATE TABLE weather (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(3),
            temperature DECIMAL(5, 2),
            feels_like DECIMAL(5, 2),
            humidity INT,
            pressure INT,
            wind_speed DECIMAL(5, 2),
            description VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(city, timestamp)
        );
        CREATE INDEX idx_weather_city ON weather(city);
        CREATE INDEX idx_weather_timestamp ON weather(timestamp);
    """,

    'news': """
        DROP TABLE IF EXISTS news CASCADE;
        CREATE TABLE news (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500),
            source VARCHAR(100),
            url TEXT,
            description TEXT,
            published_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_news_source ON news(source);
        CREATE INDEX idx_news_timestamp ON news(timestamp);
    """,

    'space_events': """
        DROP TABLE IF EXISTS space_events CASCADE;
        CREATE TABLE space_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            description TEXT,
            data JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_space_type ON space_events(event_type);
        CREATE INDEX idx_space_timestamp ON space_events(timestamp);
    """,

    'disasters': """
        DROP TABLE IF EXISTS disasters CASCADE;
        CREATE TABLE disasters (
            id SERIAL PRIMARY KEY,
            disaster_type VARCHAR(50),
            location VARCHAR(255),
            magnitude DECIMAL(5, 2),
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_disasters_type ON disasters(disaster_type);
        CREATE INDEX idx_disasters_timestamp ON disasters(timestamp);
    """,

    'economic_indicators': """
        DROP TABLE IF EXISTS economic_indicators CASCADE;
        CREATE TABLE economic_indicators (
            id SERIAL PRIMARY KEY,
            indicator VARCHAR(50) NOT NULL,
            country VARCHAR(3) NOT NULL,
            name VARCHAR(255),
            value DECIMAL(20, 4),
            unit VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(indicator, country, timestamp)
        );
        CREATE INDEX idx_econ_indicator ON economic_indicators(indicator);
        CREATE INDEX idx_econ_country ON economic_indicators(country);
        CREATE INDEX idx_econ_timestamp ON economic_indicators(timestamp);
    """,

    # Legacy tables for dashboard compatibility
    'iss_positions': """
        DROP TABLE IF EXISTS iss_positions CASCADE;
        CREATE TABLE iss_positions (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            altitude DECIMAL(10, 2),
            velocity DECIMAL(10, 2),
            UNIQUE(timestamp)
        );
        CREATE INDEX idx_iss_timestamp ON iss_positions(timestamp);
    """,

    'near_earth_objects': """
        DROP TABLE IF EXISTS near_earth_objects CASCADE;
        CREATE TABLE near_earth_objects (
            id SERIAL PRIMARY KEY,
            neo_id VARCHAR(50) NOT NULL,
            name VARCHAR(255),
            date DATE NOT NULL,
            estimated_diameter_min DECIMAL(10, 2),
            estimated_diameter_max DECIMAL(10, 2),
            relative_velocity DECIMAL(15, 2),
            miss_distance DECIMAL(20, 2),
            is_potentially_hazardous BOOLEAN,
            UNIQUE(neo_id, date)
        );
        CREATE INDEX idx_neo_date ON near_earth_objects(date);
    """,

    'solar_flares': """
        DROP TABLE IF EXISTS solar_flares CASCADE;
        CREATE TABLE solar_flares (
            id SERIAL PRIMARY KEY,
            flare_id VARCHAR(50) NOT NULL UNIQUE,
            begin_time TIMESTAMP,
            peak_time TIMESTAMP,
            end_time TIMESTAMP,
            class_type VARCHAR(10),
            source_location VARCHAR(50),
            active_region_num VARCHAR(20)
        );
    """,

    'countries': """
        DROP TABLE IF EXISTS countries CASCADE;
        CREATE TABLE countries (
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
            flag_url TEXT
        );
        CREATE INDEX idx_countries_region ON countries(region);
    """,

    'crypto': """
        DROP TABLE IF EXISTS crypto CASCADE;
        CREATE TABLE crypto (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name VARCHAR(255),
            price DECIMAL(20, 8),
            change_24h DECIMAL(20, 8),
            change_percent_24h DECIMAL(10, 4),
            market_cap DECIMAL(30, 2),
            volume_24h DECIMAL(30, 2),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, timestamp)
        );
        CREATE INDEX idx_crypto_symbol ON crypto(symbol);
        CREATE INDEX idx_crypto_timestamp ON crypto(timestamp);
    """,

    'gdelt_events': """
        DROP TABLE IF EXISTS gdelt_events CASCADE;
        CREATE TABLE gdelt_events (
            id SERIAL PRIMARY KEY,
            title TEXT,
            url TEXT,
            source VARCHAR(255),
            country VARCHAR(100),
            event_type VARCHAR(50),
            tone DECIMAL(10, 4),
            published_at TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_gdelt_country ON gdelt_events(country);
        CREATE INDEX idx_gdelt_event_type ON gdelt_events(event_type);
        CREATE INDEX idx_gdelt_timestamp ON gdelt_events(timestamp);
    """,

    'worldbank_indicators': """
        DROP TABLE IF EXISTS worldbank_indicators CASCADE;
        CREATE TABLE worldbank_indicators (
            id SERIAL PRIMARY KEY,
            indicator_code VARCHAR(50) NOT NULL,
            indicator_name VARCHAR(255),
            category VARCHAR(100),
            country_code VARCHAR(10) NOT NULL,
            country_name VARCHAR(255),
            year INTEGER,
            value DECIMAL(30, 6),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(indicator_code, country_code, year)
        );
        CREATE INDEX idx_wb_indicator ON worldbank_indicators(indicator_code);
        CREATE INDEX idx_wb_country ON worldbank_indicators(country_code);
        CREATE INDEX idx_wb_year ON worldbank_indicators(year);
    """,

    'earthquakes': """
        DROP TABLE IF EXISTS earthquakes CASCADE;
        CREATE TABLE earthquakes (
            id SERIAL PRIMARY KEY,
            location VARCHAR(255),
            magnitude DECIMAL(4, 2),
            depth DECIMAL(10, 2),
            latitude DECIMAL(10, 6),
            longitude DECIMAL(10, 6),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_earthquakes_magnitude ON earthquakes(magnitude);
        CREATE INDEX idx_earthquakes_timestamp ON earthquakes(timestamp);
    """,

    'collection_metadata': """
        DROP TABLE IF EXISTS collection_metadata CASCADE;
        CREATE TABLE collection_metadata (
            id SERIAL PRIMARY KEY,
            collector_name VARCHAR(50) UNIQUE NOT NULL,
            last_run TIMESTAMP,
            last_success TIMESTAMP,
            last_duration_seconds DECIMAL(10, 3),
            records_collected INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'idle',
            error_message TEXT,
            run_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_collection_status ON collection_metadata(status);
    """,

    'user_alerts': """
        DROP TABLE IF EXISTS user_alerts CASCADE;
        CREATE TABLE user_alerts (
            id SERIAL PRIMARY KEY,
            alert_type VARCHAR(50) NOT NULL,
            symbol VARCHAR(50),
            condition VARCHAR(20) NOT NULL,
            threshold DECIMAL(20, 8),
            is_active BOOLEAN DEFAULT TRUE,
            triggered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_alerts_active ON user_alerts(is_active);
        CREATE INDEX idx_alerts_symbol ON user_alerts(symbol);
    """,

    'alert_history': """
        DROP TABLE IF EXISTS alert_history CASCADE;
        CREATE TABLE alert_history (
            id SERIAL PRIMARY KEY,
            alert_id INTEGER REFERENCES user_alerts(id),
            triggered_value DECIMAL(20, 8),
            message TEXT,
            triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX idx_alert_history_time ON alert_history(triggered_at);
    """
}


def initialize_database():
    """Initialize all database tables using the new architecture."""

    try:
        config = Config()
        db_manager = DatabaseManager(config)

        logger.info("Connecting to PostgreSQL database...")
        logger.info(f"Host: {config.DATABASE_HOST}")
        logger.info(f"Database: {config.DATABASE_NAME}")

        # Test connection
        if not db_manager.test_connection():
            logger.error("Failed to connect to database!")
            return False

        logger.info("Connected successfully!")

        # Create each table
        with db_manager.get_connection() as conn:
            with conn.cursor() as cur:
                for table_name, schema in SCHEMAS.items():
                    logger.info(f"Creating table: {table_name}")
                    cur.execute(schema)
                    logger.info(f"  ✓ {table_name} created")
            conn.commit()

        logger.info("\n✓ All tables created successfully!")

        # Show table list
        tables = db_manager.execute_query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        logger.info("\nExisting tables:")
        for table in tables:
            logger.info(f"  - {table['table_name']}")

        return True

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("=== Hermes Database Initialization (New Schema) ===\n")
    success = initialize_database()

    if success:
        logger.info("\n✓ Database initialization complete!")
    else:
        logger.error("\n✗ Database initialization failed!")
        sys.exit(1)
