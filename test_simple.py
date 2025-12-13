"""
Simple test for Markets Collector
Run from hermes root directory.
"""
import sys
sys.path.insert(0, '.')

print("Testing imports...")

try:
    from core.config import Config
    print("✓ Core config imported")
except Exception as e:
    print(f"✗ Core config failed: {e}")
    sys.exit(1)

try:
    from core.database import DatabaseManager
    print("✓ Database manager imported")
except Exception as e:
    print(f"✗ Database manager failed: {e}")
    sys.exit(1)

try:
    from repositories.markets_repository import MarketsRepository
    print("✓ Markets repository imported")
except Exception as e:
    print(f"✗ Markets repository failed: {e}")
    sys.exit(1)

try:
    from services.markets_service import MarketsService
    print("✓ Markets service imported")
except Exception as e:
    print(f"✗ Markets service failed: {e}")
    sys.exit(1)

try:
    from collectors.markets_collector import MarketsCollector
    print("✓ Markets collector imported")
except Exception as e:
    print(f"✗ Markets collector failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All imports successful! Testing collector...")
print("="*60 + "\n")

# Test configuration
config = Config()
print(f"Database: {config.DATABASE_NAME}")
print(f"Alpha Vantage: {'✓ Configured' if config.ALPHA_VANTAGE_API_KEY else '✗ Missing'}")

if not config.ALPHA_VANTAGE_API_KEY:
    print("\n✗ Need ALPHA_VANTAGE_API_KEY in .env")
    sys.exit(1)

# Test collector init
collector = MarketsCollector(config)
print("✓ Collector initialized")

# Test database setup
collector.setup()
print("✓ Database tables created")

print("\n" + "="*60)
print("READY TO COLLECT DATA")
print("="*60)
print("\nTo collect 3 stocks (takes ~40 seconds):")
print("  results = collector.collect(symbols=['AAPL', 'MSFT', 'GOOGL'])")
print("\nCollector is working!")
