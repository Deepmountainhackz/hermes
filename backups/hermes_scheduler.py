"""
Hermes Automated Data Collection Scheduler
Runs all collectors automatically at specified intervals
"""

import schedule
import time
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# Add project root to path
sys.path.insert(0, '.')

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hermes_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import collectors
try:
    from services.space.fetch_iss_data import ISSDataCollector
    from services.space.fetch_neo_data import NEODataCollector
    from services.space.fetch_solar_data import SolarDataCollector
    from services.markets.fetch_market_data import MarketsDataCollector
    from services.social.fetch_news_data import NewsDataCollector
    from services.geography.fetch_country_data import CountryProfileCollector
    from services.environment.fetch_weather_data import WeatherDataCollector
    
    COLLECTORS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import collectors: {e}")
    COLLECTORS_AVAILABLE = False

# Database connection
def get_db_connection():
    """Get database connection"""
    db_path = os.environ.get('DATABASE_PATH', 'hermes.db')
    return sqlite3.connect(db_path)

# ============================================================================
# DATA SAVING FUNCTIONS
# ============================================================================

def save_iss_data(data):
    """Save ISS data to database"""
    if not data:
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO iss_positions (latitude, longitude, altitude_km, speed_kmh, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (
            data['latitude'],
            data['longitude'],
            408.0,  # ISS altitude is roughly constant
            27600.0,  # ISS speed is roughly constant
            data['collection_time']
        ))
        
        conn.commit()
        conn.close()
        logger.info("✓ ISS data saved to database")
        return True
    except Exception as e:
        logger.error(f"Failed to save ISS data: {e}")
        return False

def save_weather_data(city, data):
    """Save weather data to database"""
    if not data:
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO weather (
            city, temperature_c, feels_like_c, temp_min_c, temp_max_c,
            humidity_percent, weather_main, weather_description,
            wind_speed_ms, clouds_percent, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['city'],
            data['temperature'],
            data['feels_like'],
            data['temp_min'],
            data['temp_max'],
            data['humidity'],
            data['conditions'],
            data['description'],
            data['wind_speed'],
            data['clouds'],
            data['collection_time']
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"✓ Weather data for {city} saved to database")
        return True
    except Exception as e:
        logger.error(f"Failed to save weather data for {city}: {e}")
        return False

def save_market_data(data):
    """Save crypto market data to database"""
    if not data or 'cryptocurrencies' not in data:
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for crypto in data['cryptocurrencies']:
            # For now, we'll use the stocks table structure
            # In a real scenario, you'd want a separate crypto table
            try:
                cursor.execute("""
                INSERT INTO stocks (symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    crypto['id'].upper()[:10],
                    datetime.now().date().isoformat(),
                    crypto['price_usd'],
                    crypto['price_usd'],  # We don't have high/low for instant data
                    crypto['price_usd'],
                    crypto['price_usd'],
                    crypto.get('volume_24h', 0) or 0
                ))
            except sqlite3.IntegrityError:
                # Entry already exists for today
                pass
        
        conn.commit()
        conn.close()
        logger.info(f"✓ Market data for {len(data['cryptocurrencies'])} cryptos saved")
        return True
    except Exception as e:
        logger.error(f"Failed to save market data: {e}")
        return False

# ============================================================================
# COLLECTION JOBS
# ============================================================================

def collect_iss():
    """Collect ISS position data"""
    logger.info("=" * 60)
    logger.info("COLLECTING ISS DATA")
    logger.info("=" * 60)
    
    try:
        collector = ISSDataCollector()
        data = collector.fetch_data()
        
        if data:
            save_iss_data(data)
            return True
        return False
    except Exception as e:
        logger.error(f"ISS collection failed: {e}")
        return False

def collect_weather():
    """Collect weather data for all configured cities"""
    logger.info("=" * 60)
    logger.info("COLLECTING WEATHER DATA")
    logger.info("=" * 60)
    
    cities_str = os.environ.get('WEATHER_CITIES', 'London,New York,Tokyo')
    cities = [c.strip() for c in cities_str.split(',')]
    
    collector = WeatherDataCollector()
    success_count = 0
    
    for city in cities:
        try:
            data = collector.fetch_data(city=city)
            if data and save_weather_data(city, data):
                success_count += 1
            time.sleep(1)  # Delay between cities
        except Exception as e:
            logger.error(f"Failed to collect weather for {city}: {e}")
    
    logger.info(f"Weather collection complete: {success_count}/{len(cities)} cities")
    return success_count > 0

def collect_markets():
    """Collect cryptocurrency market data"""
    logger.info("=" * 60)
    logger.info("COLLECTING MARKET DATA")
    logger.info("=" * 60)
    
    try:
        crypto_str = os.environ.get('CRYPTO_SYMBOLS', 'bitcoin,ethereum,cardano')
        cryptos = [c.strip() for c in crypto_str.split(',')]
        
        collector = MarketsDataCollector()
        data = collector.fetch_data(cryptos)
        
        if data:
            save_market_data(data)
            return True
        return False
    except Exception as e:
        logger.error(f"Market collection failed: {e}")
        return False

def collect_news():
    """Collect news data"""
    logger.info("=" * 60)
    logger.info("COLLECTING NEWS DATA")
    logger.info("=" * 60)
    
    try:
        collector = NewsDataCollector()
        data = collector.fetch_data(newsapi_category='technology', hn_limit=10)
        
        if data:
            # Save to database (you'll need to implement save_news_data)
            logger.info(f"✓ Collected {data['total_articles']} news articles")
            return True
        return False
    except Exception as e:
        logger.error(f"News collection failed: {e}")
        return False

def collect_neo():
    """Collect Near Earth Objects data"""
    logger.info("=" * 60)
    logger.info("COLLECTING NEO DATA")
    logger.info("=" * 60)
    
    try:
        collector = NEODataCollector()
        data = collector.fetch_data(days=1)
        
        if data:
            # Save to database (you'll need to implement save_neo_data)
            logger.info(f"✓ Collected {data['total_objects']} NEO objects")
            return True
        return False
    except Exception as e:
        logger.error(f"NEO collection failed: {e}")
        return False

def collect_solar():
    """Collect solar activity data"""
    logger.info("=" * 60)
    logger.info("COLLECTING SOLAR DATA")
    logger.info("=" * 60)
    
    try:
        collector = SolarDataCollector()
        data = collector.fetch_data(days_back=7)
        
        if data:
            # Save to database (you'll need to implement save_solar_data)
            logger.info(f"✓ Collected solar data: {data['total_flares']} flares, {data['total_cme']} CMEs")
            return True
        return False
    except Exception as e:
        logger.error(f"Solar collection failed: {e}")
        return False

# ============================================================================
# SCHEDULER SETUP
# ============================================================================

def setup_schedule():
    """Setup the collection schedule"""
    
    # Get frequencies from environment (in minutes)
    iss_freq = int(os.environ.get('COLLECT_ISS_FREQUENCY', 10))
    weather_freq = int(os.environ.get('COLLECT_WEATHER_FREQUENCY', 30))
    markets_freq = int(os.environ.get('COLLECT_MARKETS_FREQUENCY', 5))
    news_freq = int(os.environ.get('COLLECT_NEWS_FREQUENCY', 60))
    neo_freq = int(os.environ.get('COLLECT_NEO_FREQUENCY', 1440))
    solar_freq = int(os.environ.get('COLLECT_SOLAR_FREQUENCY', 1440))
    
    # Schedule jobs
    schedule.every(iss_freq).minutes.do(collect_iss)
    schedule.every(weather_freq).minutes.do(collect_weather)
    schedule.every(markets_freq).minutes.do(collect_markets)
    schedule.every(news_freq).minutes.do(collect_news)
    schedule.every(neo_freq).minutes.do(collect_neo)
    schedule.every(solar_freq).minutes.do(collect_solar)
    
    logger.info("=" * 60)
    logger.info("SCHEDULER CONFIGURED")
    logger.info("=" * 60)
    logger.info(f"ISS: Every {iss_freq} minutes")
    logger.info(f"Weather: Every {weather_freq} minutes")
    logger.info(f"Markets: Every {markets_freq} minutes")
    logger.info(f"News: Every {news_freq} minutes")
    logger.info(f"NEO: Every {neo_freq} minutes ({neo_freq/60:.1f} hours)")
    logger.info(f"Solar: Every {solar_freq} minutes ({solar_freq/60:.1f} hours)")
    logger.info("=" * 60)

def run_initial_collection():
    """Run all collectors once at startup"""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING INITIAL DATA COLLECTION")
    logger.info("=" * 60 + "\n")
    
    collect_iss()
    time.sleep(2)
    
    collect_weather()
    time.sleep(2)
    
    collect_markets()
    time.sleep(2)
    
    collect_news()
    time.sleep(2)
    
    logger.info("\n" + "=" * 60)
    logger.info("INITIAL COLLECTION COMPLETE")
    logger.info("=" * 60 + "\n")

def main():
    """Main scheduler loop"""
    
    if not COLLECTORS_AVAILABLE:
        logger.error("Collectors not available. Cannot start scheduler.")
        return
    
    logger.info("\n" + "=" * 60)
    logger.info("🌐 HERMES INTELLIGENCE PLATFORM")
    logger.info("   Automated Data Collection Scheduler")
    logger.info("=" * 60 + "\n")
    
    # Setup schedule
    setup_schedule()
    
    # Run initial collection
    run_initial_collection()
    
    # Start scheduler loop
    logger.info("✓ Scheduler started. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("SCHEDULER STOPPED")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()
