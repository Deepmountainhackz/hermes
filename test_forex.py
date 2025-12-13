"""
Simple test for Forex Collector
Run from hermes root directory.
"""
import sys
sys.path.insert(0, '.')

print("Testing forex collector imports...")

try:
    from core.config import Config
    print("✓ Core config imported")
except Exception as e:
    print(f"✗ Core config failed: {e}")
    sys.exit(1)

try:
    from repositories.forex_repository import ForexRepository
    print("✓ Forex repository imported")
except Exception as e:
    print(f"✗ Forex repository failed: {e}")
    sys.exit(1)

try:
    from services.forex_service import ForexService
    print("✓ Forex service imported")
except Exception as e:
    print(f"✗ Forex service failed: {e}")
    sys.exit(1)

try:
    from collectors.forex_collector import ForexCollector
    print("✓ Forex collector imported")
except Exception as e:
    print(f"✗ Forex collector failed: {e}")
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
collector = ForexCollector(config)
print("✓ Collector initialized")

# Test database setup
collector.setup()
print("✓ Database tables created")

print("\n" + "="*60)
print("READY TO COLLECT FOREX DATA")
print("="*60)
print("\nDefault currency pairs tracked:")
for pair in ForexService.DEFAULT_PAIRS:
    print(f"  - {pair['from']}/{pair['to']}")

print("\nTo collect 2 currency pairs (takes ~25 seconds):")
print("  results = collector.collect(currency_pairs=[{'from': 'EUR', 'to': 'USD'}, {'from': 'GBP', 'to': 'USD'}])")
print("\nOr collect all 7 default pairs (~90 seconds):")
print("  results = collector.collect()")
print("\nCollector is working!")
