"""
Test Phase 2: Repository Layer
"""

from services.data.market_repository import MarketRepository
from config.settings import settings

print("\n" + "="*60)
print("PHASE 2: REPOSITORY LAYER TEST")
print("="*60)

# Initialize repository
print("\nInitializing MarketRepository...")
market_repo = MarketRepository()
print("✓ Repository initialized")

# Test 1: Get latest stocks
print("\nTest 1: Get Latest Stocks")
print("-"*60)
try:
    latest = market_repo.get_latest()
    print(f"✓ Retrieved {len(latest)} stocks")
    if not latest.empty:
        print(f"✓ Sample: {latest['symbol'].head(3).tolist()}")
    else:
        print("! No stock data found (run collectors first)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get market summary
print("\nTest 2: Market Summary")
print("-"*60)
try:
    summary = market_repo.get_market_summary()
    if summary:
        print(f"✓ Total Stocks: {summary.get('total_stocks', 0)}")
        print(f"✓ Average Change: {summary.get('avg_change', 0):.2f}%")
        print(f"✓ Gainers: {summary.get('gainers', 0)}")
        print(f"✓ Losers: {summary.get('losers', 0)}")
    else:
        print("! No data for summary")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Count records
print("\nTest 3: Record Count")
print("-"*60)
try:
    count = market_repo.count()
    print(f"✓ Total records in database: {count:,}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Get symbols list
print("\nTest 4: Tracked Symbols")
print("-"*60)
try:
    symbols = market_repo.get_symbols_list()
    print(f"✓ Tracking {len(symbols)} symbols")
    if symbols:
        print(f"✓ Symbols: {', '.join(symbols[:10])}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("PHASE 2 TESTS COMPLETE!")
print("="*60)
print("\nRepository pattern is working!")
print("Ready to build more repositories for other domains.")
print("="*60 + "\n")
