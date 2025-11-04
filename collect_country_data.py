"""
Collect Country Data and Save to Database
Fetches country profiles and stores them in hermes.db
"""

import sqlite3
import logging
from datetime import datetime
import sys
import time

# Add project root to path
sys.path.insert(0, '.')

from services.geography.fetch_country_data import CountryProfileCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_countries_table(conn):
    """Create the countries table if it doesn't exist"""
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        official_name TEXT,
        region TEXT,
        subregion TEXT,
        population INTEGER,
        area_km2 REAL,
        population_density REAL,
        capital TEXT,
        languages TEXT,
        currencies TEXT,
        flag_emoji TEXT,
        latitude REAL,
        longitude REAL,
        border_count INTEGER,
        borders TEXT,
        timezones TEXT,
        un_member INTEGER,
        independent INTEGER,
        landlocked INTEGER,
        cca2 TEXT,
        cca3 TEXT,
        timestamp TEXT
    )
    """)
    
    conn.commit()
    logger.info("Countries table created/verified")

def save_country_to_db(conn, country_data):
    """Save a single country's data to the database"""
    cursor = conn.cursor()
    
    try:
        # Prepare data for insertion
        data = {
            'name': country_data['name'],
            'official_name': country_data['official_name'],
            'region': country_data['region'],
            'subregion': country_data['subregion'],
            'population': country_data['population'],
            'area_km2': country_data['area_km2'],
            'population_density': country_data['population_density'],
            'capital': ', '.join(country_data['capital']) if country_data['capital'] else None,
            'languages': ', '.join(country_data['languages']) if country_data['languages'] else None,
            'currencies': ', '.join([c['name'] for c in country_data['currencies']]) if country_data['currencies'] else None,
            'flag_emoji': country_data['flag_emoji'],
            'latitude': country_data['latitude'],
            'longitude': country_data['longitude'],
            'border_count': country_data['border_count'],
            'borders': ', '.join(country_data['borders']) if country_data['borders'] else None,
            'timezones': ', '.join(country_data['timezones']) if country_data['timezones'] else None,
            'un_member': 1 if country_data['un_member'] else 0,
            'independent': 1 if country_data['independent'] else 0,
            'landlocked': 1 if country_data['landlocked'] else 0,
            'cca2': country_data['cca2'],
            'cca3': country_data['cca3'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Insert or replace (upsert)
        cursor.execute("""
        INSERT OR REPLACE INTO countries (
            name, official_name, region, subregion, population, area_km2,
            population_density, capital, languages, currencies, flag_emoji,
            latitude, longitude, border_count, borders, timezones,
            un_member, independent, landlocked, cca2, cca3, timestamp
        ) VALUES (
            :name, :official_name, :region, :subregion, :population, :area_km2,
            :population_density, :capital, :languages, :currencies, :flag_emoji,
            :latitude, :longitude, :border_count, :borders, :timezones,
            :un_member, :independent, :landlocked, :cca2, :cca3, :timestamp
        )
        """, data)
        
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error saving {country_data['name']}: {e}")
        return False

def collect_countries_by_region(collector, conn, region):
    """Collect all countries in a specific region"""
    logger.info(f"Fetching countries in {region}...")
    
    countries = collector.fetch_countries_by_region(region)
    
    if not countries:
        logger.warning(f"No countries found for region: {region}")
        return 0
    
    saved_count = 0
    for country in countries:
        if save_country_to_db(conn, country):
            saved_count += 1
            logger.info(f"✓ Saved: {country['flag_emoji']} {country['name']}")
        
        # Small delay to be nice to the API
        time.sleep(0.2)
    
    return saved_count

def collect_all_countries():
    """Main function to collect all country data"""
    logger.info("="*60)
    logger.info("STARTING COUNTRY DATA COLLECTION")
    logger.info("="*60)
    
    # Connect to database
    conn = sqlite3.connect('hermes.db')
    logger.info("Connected to database")
    
    # Create table
    create_countries_table(conn)
    
    # Initialize collector
    collector = CountryProfileCollector()
    
    # Define regions to collect
    regions = ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']
    
    total_saved = 0
    
    # Collect each region
    for region in regions:
        logger.info(f"\n{'='*60}")
        logger.info(f"REGION: {region}")
        logger.info(f"{'='*60}")
        
        saved = collect_countries_by_region(collector, conn, region)
        total_saved += saved
        
        logger.info(f"✓ Saved {saved} countries from {region}")
        
        # Longer delay between regions
        time.sleep(1)
    
    # Close connection
    conn.close()
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("COLLECTION COMPLETE")
    logger.info("="*60)
    logger.info(f"Total countries saved: {total_saved}")
    logger.info(f"Database: hermes.db")
    logger.info(f"Table: countries")
    
    return total_saved

def collect_specific_countries(country_names):
    """Collect data for specific countries by name"""
    logger.info("="*60)
    logger.info("COLLECTING SPECIFIC COUNTRIES")
    logger.info("="*60)
    
    # Connect to database
    conn = sqlite3.connect('hermes.db')
    
    # Create table
    create_countries_table(conn)
    
    # Initialize collector
    collector = CountryProfileCollector()
    
    saved_count = 0
    
    for country_name in country_names:
        logger.info(f"\nFetching: {country_name}")
        country_data = collector.fetch_data(country_name)
        
        if country_data:
            if save_country_to_db(conn, country_data):
                saved_count += 1
                logger.info(f"✓ Saved: {country_data['flag_emoji']} {country_data['name']}")
        else:
            logger.warning(f"✗ Failed to fetch: {country_name}")
        
        time.sleep(0.5)
    
    conn.close()
    
    logger.info(f"\nSaved {saved_count}/{len(country_names)} countries")
    return saved_count

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌍 COUNTRY DATA COLLECTOR")
    print("="*60)
    print("\nWhat would you like to do?")
    print("1. Collect ALL countries (250+ countries, ~5 minutes)")
    print("2. Collect specific countries")
    print("3. Collect top 20 most populous countries (quick)")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\nCollecting all countries... This will take a few minutes.")
        print("Please be patient! 🌍\n")
        total = collect_all_countries()
        print(f"\n✅ SUCCESS! Collected {total} countries!")
        print("Run your dashboard to see the data: streamlit run hermes_dashboard.py")
        
    elif choice == "2":
        print("\nEnter country names separated by commas")
        print("Example: Germany, Japan, Brazil, Australia")
        countries_input = input("\nCountries: ").strip()
        
        if countries_input:
            country_list = [c.strip() for c in countries_input.split(',')]
            print(f"\nCollecting {len(country_list)} countries...\n")
            total = collect_specific_countries(country_list)
            print(f"\n✅ SUCCESS! Collected {total} countries!")
        else:
            print("❌ No countries entered!")
            
    elif choice == "3":
        print("\nCollecting top 20 most populous countries...\n")
        
        # Top 20 by population
        top_countries = [
            'China', 'India', 'United States', 'Indonesia', 'Pakistan',
            'Brazil', 'Nigeria', 'Bangladesh', 'Russia', 'Mexico',
            'Japan', 'Ethiopia', 'Philippines', 'Egypt', 'Vietnam',
            'DR Congo', 'Turkey', 'Iran', 'Germany', 'Thailand'
        ]
        
        total = collect_specific_countries(top_countries)
        print(f"\n✅ SUCCESS! Collected {total} countries!")
        print("Run your dashboard to see the data: streamlit run hermes_dashboard.py")
        
    else:
        print("❌ Invalid choice!")
