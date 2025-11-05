#!/usr/bin/env python3
"""
Test All Collectors - Fixed for scripts/ directory
===================================================
This script tests all data collectors to ensure they're working properly.
Now properly handles being run from the scripts/ directory.
"""

import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# FIX: Add project root to Python path
# Get the directory where this script is located (scripts/)
SCRIPT_DIR = Path(__file__).parent.absolute()
# Get the project root (one level up from scripts/)
PROJECT_ROOT = SCRIPT_DIR.parent
# Add project root to Python path so we can import from services/
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_iss():
    """Test ISS Position Tracker"""
    print("\n" + "="*60)
    print("🛰️  TESTING ISS POSITION TRACKER")
    print("="*60)
    
    try:
        from services.space.fetch_iss_data import ISSDataCollector
        
        collector = ISSDataCollector()
        data = collector.fetch_data()
        
        if data:
            print(f"✅ SUCCESS: Retrieved ISS position")
            print(f"   Latitude: {data.get('latitude', 'N/A')}")
            print(f"   Longitude: {data.get('longitude', 'N/A')}")
            print(f"   Altitude: {data.get('altitude_km', 'N/A')} km")
            return True
        else:
            print("❌ FAIL: No data returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("ISS test failed", exc_info=True)
        return False

def test_neo():
    """Test Near Earth Objects collector"""
    print("\n" + "="*60)
    print("🌠 TESTING NEAR EARTH OBJECTS (NEO)")
    print("="*60)
    
    try:
        from services.space.fetch_neo_data import NEODataCollector
        
        collector = NEODataCollector()
        data = collector.fetch_data()
        
        if data:
            print(f"✅ SUCCESS: Retrieved NEO data")
            # Just show that we got data, don't assume structure
            if isinstance(data, list) and len(data) > 0:
                print(f"   Objects: {len(data)}")
            elif isinstance(data, dict):
                print(f"   Data keys: {list(data.keys())[:3]}")
            return True
        else:
            print("⚠️  WARNING: No NEO data (this can be normal)")
            return True  # Not a failure
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("NEO test failed", exc_info=True)
        return False

def test_solar():
    """Test Solar Activity tracker"""
    print("\n" + "="*60)
    print("☀️  TESTING SOLAR ACTIVITY TRACKER")
    print("="*60)
    
    try:
        from services.space.fetch_solar_data import SolarDataCollector
        
        collector = SolarDataCollector()
        data = collector.fetch_data()
        
        if data:
            print(f"✅ SUCCESS: Retrieved solar data")
            # Just show that we got data, don't assume structure
            if isinstance(data, list) and len(data) > 0:
                print(f"   Events: {len(data)}")
            elif isinstance(data, dict):
                print(f"   Data keys: {list(data.keys())[:3]}")
            return True
        else:
            print("⚠️  WARNING: No solar activity (this can be normal)")
            return True  # Not a failure
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("Solar test failed", exc_info=True)
        return False

def test_markets():
    """Test Financial Markets collector"""
    print("\n" + "="*60)
    print("💰 TESTING FINANCIAL MARKETS (CRYPTO)")
    print("="*60)
    
    try:
        from services.markets.fetch_market_data import MarketsDataCollector
        
        collector = MarketsDataCollector()
        data = collector.fetch_data()
        
        if data:
            print(f"✅ SUCCESS: Retrieved market data")
            # Just show that we got data, don't assume structure
            if isinstance(data, list) and len(data) > 0:
                print(f"   Records: {len(data)}")
            elif isinstance(data, dict):
                print(f"   Data keys: {list(data.keys())[:3]}")
            return True
        else:
            print("❌ FAIL: No market data returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("Markets test failed", exc_info=True)
        return False

def test_news():
    """Test News Aggregator"""
    print("\n" + "="*60)
    print("📰 TESTING NEWS AGGREGATOR")
    print("="*60)
    
    try:
        from services.social.fetch_news_data import NewsDataCollector
        
        collector = NewsDataCollector()
        data = collector.fetch_data()
        
        if data:
            print(f"✅ SUCCESS: Retrieved news data")
            # Just show that we got data, don't assume structure
            if isinstance(data, list) and len(data) > 0:
                print(f"   Articles: {len(data)}")
            elif isinstance(data, dict):
                print(f"   Data keys: {list(data.keys())[:3]}")
            return True
        else:
            print("❌ FAIL: No news articles returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("News test failed", exc_info=True)
        return False

def test_countries():
    """Test Country Profile collector"""
    print("\n" + "="*60)
    print("🌍 TESTING COUNTRY PROFILE COLLECTOR")
    print("="*60)
    
    try:
        from services.geography.fetch_country_data import CountryProfileCollector
        
        collector = CountryProfileCollector()
        # Test with a specific country
        data = collector.fetch_data('United States')
        
        if data:
            print(f"✅ SUCCESS: Retrieved country profile")
            print(f"   Country: {data.get('name', 'N/A')}")
            print(f"   Capital: {data.get('capital', 'N/A')}")
            return True
        else:
            print("❌ FAIL: No country data returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("Countries test failed", exc_info=True)
        return False

def test_weather():
    """Test Weather Data collector"""
    print("\n" + "="*60)
    print("🌤️  TESTING WEATHER DATA COLLECTOR")
    print("="*60)
    
    try:
        from services.environment.fetch_weather_data import WeatherDataCollector
        
        collector = WeatherDataCollector()
        # Test with a specific city
        data = collector.fetch_data(city='London')
        
        if data:
            print(f"✅ SUCCESS: Retrieved weather data")
            print(f"   City: {data.get('city', 'N/A')}")
            print(f"   Temperature: {data.get('temperature_c', 'N/A')}°C")
            return True
        else:
            print("❌ FAIL: No weather data returned")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.error("Weather test failed", exc_info=True)
        return False

def main():
    """Run all collector tests"""
    print("\n" + "="*60)
    print("🚀 TESTING ALL DATA COLLECTORS")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python Path: {sys.path[0]}")
    
    # Run all tests
    tests = {
        'ISS': test_iss,
        'NEO': test_neo,
        'Solar': test_solar,
        'Markets': test_markets,
        'News': test_news,
        'Countries': test_countries,
        'Weather': test_weather
    }
    
    results = {}
    for name, test_func in tests.items():
        results[name] = test_func()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    # Calculate success rate
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
    
    print("-" * 60)
    print(f"Total: {passed_count}/{total_count} collectors passed")
    print(f"Success Rate: {success_rate:.1f}%")
    print("="*60)
    
    if passed_count == total_count:
        print("\n🎉 All collectors working perfectly!")
    elif passed_count > 0:
        print(f"\n⚠️  {total_count - passed_count} collector(s) need attention")
    else:
        print("\n❌ All collectors failed. Check:")
        print("   - Network connectivity")
        print("   - API keys in .env file")
        print("   - Python path configuration")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
