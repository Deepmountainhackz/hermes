"""
Demo Script - Test All Data Collectors
Works with services folder structure
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

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
            print(f"✅ SUCCESS!")
            print(f"   Location: {data['latitude']:.2f}°, {data['longitude']:.2f}°")
            print(f"   Time: {data['timestamp_readable']}")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("ISS test failed")
        return False

def test_neo():
    """Test Near Earth Objects"""
    print("\n" + "="*60)
    print("🌠 TESTING NEAR EARTH OBJECTS (NEO)")
    print("="*60)
    
    try:
        from services.space.fetch_neo_data import NEODataCollector
        collector = NEODataCollector()
        data = collector.fetch_data(days=1)
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   Total Objects: {data['total_objects']}")
            print(f"   Potentially Hazardous: {data['potentially_hazardous_count']}")
            if data['potentially_hazardous_count'] > 0:
                print(f"   ⚠️  First Hazardous: {data['potentially_hazardous'][0]['name']}")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("NEO test failed")
        return False

def test_solar():
    """Test Solar Activity"""
    print("\n" + "="*60)
    print("☀️  TESTING SOLAR ACTIVITY TRACKER")
    print("="*60)
    
    try:
        from services.space.fetch_solar_data import SolarDataCollector
        collector = SolarDataCollector()
        data = collector.fetch_data(days_back=7)
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   Total Flares: {data['total_flares']}")
            print(f"   X-Class (Most Intense): {data['flare_breakdown']['X_class']}")
            print(f"   M-Class: {data['flare_breakdown']['M_class']}")
            print(f"   CME Events: {data['total_cme']}")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("Solar test failed")
        return False

def test_markets():
    """Test Financial Markets"""
    print("\n" + "="*60)
    print("💰 TESTING FINANCIAL MARKETS (CRYPTO)")
    print("="*60)
    
    try:
        from services.markets.fetch_market_data import MarketsDataCollector
        collector = MarketsDataCollector()
        data = collector.fetch_data(['bitcoin', 'ethereum', 'cardano'])
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   Total Coins Tracked: {data['total_coins_tracked']}")
            if data['global_market_cap_usd']:
                print(f"   Global Market Cap: ${data['global_market_cap_usd']:,.0f}")
            if data['cryptocurrencies']:
                btc = data['cryptocurrencies'][0]
                print(f"   Bitcoin: ${btc['price_usd']:,.2f} ({btc['change_24h']:+.2f}% 24h)")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("Markets test failed")
        return False

def test_news():
    """Test News Aggregator"""
    print("\n" + "="*60)
    print("📰 TESTING NEWS AGGREGATOR")
    print("="*60)
    
    try:
        from services.social.fetch_news_data import NewsDataCollector
        collector = NewsDataCollector()
        data = collector.fetch_data(newsapi_category='technology', hn_limit=5)
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   Total Articles: {data['total_articles']}")
            print(f"   NewsAPI: {data['newsapi_count']}")
            print(f"   Hacker News: {data['hackernews_count']}")
            if data['hackernews_stories']:
                top = data['hackernews_stories'][0]
                print(f"   Top HN Story: {top['title'][:50]}...")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("News test failed")
        return False

def test_countries():
    """Test Country Profile Collector"""
    print("\n" + "="*60)
    print("🌍 TESTING COUNTRY PROFILE COLLECTOR")
    print("="*60)
    
    try:
        from services.geography.fetch_country_data import CountryProfileCollector
        collector = CountryProfileCollector()
        data = collector.fetch_data('Japan')
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   Country: {data['flag_emoji']} {data['name']}")
            print(f"   Population: {data['population']:,}")
            print(f"   Languages: {', '.join(data['languages'])}")
            print(f"   Capital: {', '.join(data['capital'])}")
            print(f"   Density: {data['population_density']:.2f} people/km²")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("Countries test failed")
        return False

def test_weather():
    """Test Weather Data"""
    print("\n" + "="*60)
    print("🌤️  TESTING WEATHER DATA COLLECTOR")
    print("="*60)
    
    try:
        from services.environment.fetch_weather_data import WeatherDataCollector
        collector = WeatherDataCollector()
        data = collector.fetch_data(city='London')
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   City: {data.get('city', 'N/A')}")
            print(f"   Temperature: {data.get('temperature', 'N/A')}°C")
            print(f"   Conditions: {data.get('conditions', 'N/A')}")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        logger.exception("Weather test failed")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 TESTING ALL DATA COLLECTORS")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {project_root}")
    
    results = {
        'ISS': test_iss(),
        'NEO': test_neo(),
        'Solar': test_solar(),
        'Markets': test_markets(),
        'News': test_news(),
        'Countries': test_countries(),  # NEW!
        'Weather': test_weather()
    }
    
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} collectors passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL COLLECTORS WORKING! Ready for production!")
    elif passed > 0:
        print(f"\n⚠️  {total - passed} collector(s) failed. Check logs above.")
        print("\n💡 Common issues:")
        print("   - Missing API keys (NASA_API_KEY, NEWSAPI_KEY, OPENWEATHER_API_KEY)")
        print("   - Network connectivity")
        print("   - Missing __init__.py files in service folders")
    else:
        print("\n❌ All collectors failed. Check:")
        print("   - Network connectivity")
        print("   - Python path configuration")
        print("   - Missing __init__.py files")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
