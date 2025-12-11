"""
Test script for Markets Collector
Tests the complete end-to-end flow of the refactored architecture.
"""
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from collectors.markets_collector import MarketsCollector
from core.config import Config
from core.exceptions import APIError, DatabaseError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_markets_collector():
    """Test the markets collector end-to-end."""
    print("\n" + "=" * 70)
    print("TESTING MARKETS COLLECTOR - REFACTORED ARCHITECTURE")
    print("=" * 70 + "\n")
    
    try:
        # 1. Test Configuration
        print("1. Testing Configuration...")
        config = Config()
        print(f"   ✓ Config loaded")
        print(f"   - Database: {config.DATABASE_NAME}")
        print(f"   - Alpha Vantage API: {'✓ Configured' if config.ALPHA_VANTAGE_API_KEY else '✗ Missing'}")
        
        if not config.ALPHA_VANTAGE_API_KEY:
            print("\n✗ ERROR: ALPHA_VANTAGE_API_KEY not configured in .env file")
            return False
        
        # 2. Test Collector Initialization
        print("\n2. Testing Collector Initialization...")
        collector = MarketsCollector(config)
        print("   ✓ Collector initialized")
        
        # 3. Test Database Setup
        print("\n3. Testing Database Setup...")
        collector.setup()
        print("   ✓ Database tables created/verified")
        
        # 4. Test Data Collection (just 3 stocks to save API calls)
        print("\n4. Testing Data Collection...")
        print("   Collecting data for AAPL, MSFT, GOOGL (this will take ~40 seconds)...")
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']
        results = collector.collect(symbols=test_symbols)
        
        if 'error' in results:
            print(f"\n✗ Collection failed: {results['error']}")
            return False
        
        print(f"   ✓ Collection completed")
        print(f"   - Total: {results['total_symbols']}")
        print(f"   - Successful: {results['successful']}")
        print(f"   - Failed: {results['failed']}")
        print(f"   - Duration: {results['duration_seconds']:.2f}s")
        
        # 5. Test Data Retrieval
        print("\n5. Testing Data Retrieval...")
        latest_data = collector.get_latest_data()
        print(f"   ✓ Retrieved {len(latest_data)} stock records")
        
        if latest_data:
            sample = latest_data[0]
            print(f"   - Sample: {sample['symbol']} @ ${sample['price']}")
        
        # 6. Test Sparkline Data
        print("\n6. Testing Sparkline Data...")
        if latest_data:
            symbol = latest_data[0]['symbol']
            stock_with_sparkline = collector.get_stock_with_sparkline(symbol, days=7)
            if stock_with_sparkline:
                print(f"   ✓ Sparkline data retrieved for {symbol}")
                print(f"   - Data points: {len(stock_with_sparkline.get('sparkline', []))}")
            else:
                print(f"   ⚠ No sparkline data available yet (need multiple collection runs)")
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70 + "\n")
        
        return True
        
    except APIError as e:
        print(f"\n✗ API Error: {e}")
        return False
    except DatabaseError as e:
        print(f"\n✗ Database Error: {e}")
        return False
    except Exception as e:
        logger.exception("Unexpected error during testing")
        print(f"\n✗ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    success = test_markets_collector()
    sys.exit(0 if success else 1)
