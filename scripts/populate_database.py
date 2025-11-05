"""
Database Population Script
Populates hermes.db with initial data from all collectors
"""

import sqlite3
import logging
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

from services.space.fetch_iss_data import ISSDataCollector
from services.space.fetch_neo_data import NEODataCollector
from services.space.fetch_solar_data import SolarDataCollector
from services.markets.fetch_market_data import MarketsDataCollector
from services.social.fetch_news_data import NewsDataCollector
from services.geography.fetch_country_data import CountryProfileCollector
from services.environment.fetch_weather_data import WeatherDataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabasePopulator:
    """Populates database with data from all collectors"""
    
    def __init__(self, db_path='hermes.db'):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        logger.info(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def populate_iss(self):
        """Populate ISS position data"""
        logger.info("\n" + "=" * 60)
        logger.info("POPULATING ISS DATA")
        logger.info("=" * 60)
        
        try:
            collector = ISSDataCollector()
            data = collector.fetch_data()
            
            if data:
                cursor = self.conn.cursor()
                cursor.execute("""
                INSERT INTO iss_positions (latitude, longitude, altitude_km, speed_kmh, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    data['latitude'],
                    data['longitude'],
                    408.0,
                    27600.0,
                    data['collection_time']
                ))
                self.conn.commit()
                logger.info("✓ ISS data saved")
                return True
        except Exception as e:
            logger.error(f"Failed to populate ISS data: {e}")
            return False
    
    def populate_weather(self, cities=None):
        """Populate weather data"""
        logger.info("\n" + "=" * 60)
        logger.info("POPULATING WEATHER DATA")
        logger.info("=" * 60)
        
        if cities is None:
            cities = ['London', 'New York', 'Tokyo', 'Singapore', 'Frankfurt']
        
        collector = WeatherDataCollector()
        success_count = 0
        
        for city in cities:
            try:
                data = collector.fetch_data(city=city)
                if data:
                    cursor = self.conn.cursor()
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
                    self.conn.commit()
                    logger.info(f"✓ Weather data for {city} saved")
                    success_count += 1
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Failed to populate weather for {city}: {e}")
        
        logger.info(f"Weather population complete: {success_count}/{len(cities)} cities")
        return success_count > 0
    
    def populate_markets(self):
        """Populate market data"""
        logger.info("\n" + "=" * 60)
        logger.info("POPULATING MARKET DATA")
        logger.info("=" * 60)
        
        try:
            collector = MarketsDataCollector()
            cryptos = ['bitcoin', 'ethereum', 'cardano', 'solana', 'polkadot']
            data = collector.fetch_data(cryptos)
            
            if data and 'cryptocurrencies' in data:
                cursor = self.conn.cursor()
                
                for crypto in data['cryptocurrencies']:
                    try:
                        cursor.execute("""
                        INSERT INTO stocks (symbol, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            crypto['id'].upper()[:10],
                            datetime.now().date().isoformat(),
                            crypto['price_usd'],
                            crypto['price_usd'],
                            crypto['price_usd'],
                            crypto['price_usd'],
                            crypto.get('volume_24h', 0) or 0
                        ))
                    except sqlite3.IntegrityError:
                        logger.warning(f"Entry already exists for {crypto['id']}")
                
                self.conn.commit()
                logger.info(f"✓ Market data for {len(data['cryptocurrencies'])} cryptos saved")
                return True
        except Exception as e:
            logger.error(f"Failed to populate market data: {e}")
            return False
    
    def populate_neo(self):
        """Populate Near Earth Objects data"""
        logger.info("\n" + "=" * 60)
        logger.info("POPULATING NEO DATA")
        logger.info("=" * 60)
        
        try:
            collector = NEODataCollector()
            data = collector.fetch_data(days=7)
            
            if data and 'all_objects' in data:
                cursor = self.conn.cursor()
                
                for neo in data['all_objects']:
                    try:
                        cursor.execute("""
                        INSERT INTO near_earth_objects (
                            name, diameter_min_m, diameter_max_m, velocity_kmh,
                            miss_distance_km, is_hazardous, date
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            neo['name'],
                            neo['diameter_min_km'] * 1000,
                            neo['diameter_max_km'] * 1000,
                            neo['relative_velocity_kmh'],
                            neo['miss_distance_km'],
                            1 if neo['potentially_hazardous'] else 0,
                            neo['date']
                        ))
                    except sqlite3.IntegrityError:
                        pass  # Entry exists
                
                self.conn.commit()
                logger.info(f"✓ NEO data for {len(data['all_objects'])} objects saved")
                return True
        except Exception as e:
            logger.error(f"Failed to populate NEO data: {e}")
            return False
    
    def populate_solar(self):
        """Populate solar activity data"""
        logger.info("\n" + "=" * 60)
        logger.info("POPULATING SOLAR DATA")
        logger.info("=" * 60)
        
        try:
            collector = SolarDataCollector()
            data = collector.fetch_data(days_back=30)
            
            if data and 'all_flares' in data:
                cursor = self.conn.cursor()
                
                for flare in data['all_flares']:
                    try:
                        cursor.execute("""
                        INSERT INTO solar_flares (
                            class_type, begin_time, peak_time, source_location
                        ) VALUES (?, ?, ?, ?)
                        """, (
                            flare.get('classType', 'Unknown'),
                            flare.get('beginTime'),
                            flare.get('peakTime'),
                            flare.get('sourceLocation', 'Unknown')
                        ))
                    except sqlite3.IntegrityError:
                        pass
                
                self.conn.commit()
                logger.info(f"✓ Solar data for {len(data['all_flares'])} flares saved")
                return True
        except Exception as e:
            logger.error(f"Failed to populate solar data: {e}")
            return False
    
    def populate_countries(self, limit=20):
        """Populate country data (quick sample)"""
        logger.info("\n" + "=" * 60)
        logger.info(f"POPULATING COUNTRY DATA (Top {limit})")
        logger.info("=" * 60)
        
        # Top countries by population
        top_countries = [
            'China', 'India', 'United States', 'Indonesia', 'Pakistan',
            'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico',
            'Japan', 'Ethiopia', 'Philippines', 'Egypt', 'Vietnam',
            'Germany', 'United Kingdom', 'France', 'Italy', 'Spain'
        ][:limit]
        
        collector = CountryProfileCollector()
        success_count = 0
        
        for country_name in top_countries:
            try:
                data = collector.fetch_data(country_name)
                if data:
                    cursor = self.conn.cursor()
                    cursor.execute("""
                    INSERT OR REPLACE INTO countries (
                        name, official_name, region, subregion, population, area_km2,
                        population_density, capital, languages, currencies, flag_emoji,
                        latitude, longitude, border_count, borders, timezones,
                        un_member, independent, landlocked, cca2, cca3, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['name'],
                        data['official_name'],
                        data['region'],
                        data['subregion'],
                        data['population'],
                        data['area_km2'],
                        data['population_density'],
                        ', '.join(data['capital']) if data['capital'] else None,
                        ', '.join(data['languages']) if data['languages'] else None,
                        ', '.join([c['name'] for c in data['currencies']]) if data['currencies'] else None,
                        data['flag_emoji'],
                        data['latitude'],
                        data['longitude'],
                        data['border_count'],
                        ', '.join(data['borders']) if data['borders'] else None,
                        ', '.join(data['timezones']) if data['timezones'] else None,
                        1 if data['un_member'] else 0,
                        1 if data['independent'] else 0,
                        1 if data['landlocked'] else 0,
                        data['cca2'],
                        data['cca3'],
                        datetime.utcnow().isoformat()
                    ))
                    self.conn.commit()
                    logger.info(f"✓ {data['flag_emoji']} {data['name']} saved")
                    success_count += 1
                    time.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to populate {country_name}: {e}")
        
        logger.info(f"Country population complete: {success_count}/{len(top_countries)} countries")
        return success_count > 0
    
    def populate_all(self):
        """Populate all data"""
        logger.info("\n" + "=" * 60)
        logger.info("🌐 HERMES DATABASE POPULATION")
        logger.info("=" * 60)
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        results = {
            'ISS': self.populate_iss(),
            'Weather': self.populate_weather(),
            'Markets': self.populate_markets(),
            'NEO': self.populate_neo(),
            'Solar': self.populate_solar(),
            'Countries': self.populate_countries(limit=20)
        }
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 POPULATION SUMMARY")
        logger.info("=" * 60)
        
        for name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{status} - {name}")
        
        passed = sum(results.values())
        total = len(results)
        
        logger.info(f"\nTotal: {passed}/{total} successful")
        logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        logger.info(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        if passed == total:
            logger.info("\n🎉 ALL DATA POPULATED SUCCESSFULLY!")
            logger.info("Run your dashboard: streamlit run hermes_dashboard.py")
        else:
            logger.warning(f"\n⚠️  {total - passed} data source(s) failed. Check logs above.")

def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("🌐 HERMES DATABASE POPULATOR")
    print("=" * 60)
    print("\nThis will populate your database with initial data from all collectors.")
    print("This may take 2-3 minutes.\n")
    
    choice = input("Continue? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("Cancelled.")
        return
    
    populator = DatabasePopulator()
    populator.connect()
    
    try:
        populator.populate_all()
    finally:
        populator.close()

if __name__ == "__main__":
    main()
