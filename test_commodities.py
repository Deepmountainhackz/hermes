"""
Simple test for Commodities Collector
Run from hermes root directory.
"""
import sys
sys.path.insert(0, '.')

print("Testing commodities collector imports...")

try:
    from core.config import Config
    print("✓ Core config imported")
except Exception as e:
    print(f"✗ Core config failed: {e}")
    sys.exit(1)

try:
    from repositories.commodities_repository import CommoditiesRepository
    print("✓ Commodities repository imported")
except Exception as e:
    print(f"✗ Commodities repository failed: {e}")
    sys.exit(1)

try:
    from services.commodities_service import CommoditiesService
    print("✓ Commodities service imported")
except Exception as e:
    print(f"✗ Commodities service failed: {e}")
    sys.exit(1)

try:
    from collectors.commodities_collector import CommoditiesCollector
    print("✓ Commodities collector imported")
except Exception as e:
    print(f"✗ Commodities collector failed: {e}")
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
collector = CommoditiesCollector(config)
print("✓ Collector initialized")

# Test database setup
collector.setup()
print("✓ Database tables created")

print("\n" + "="*60)
print("READY TO COLLECT COMMODITIES DATA")
print("="*60)
print("\nDefault commodities tracked:")
for symbol, info in CommoditiesService.DEFAULT_COMMODITIES.items():
    print(f"  - {symbol}: {info['name']} ({info['unit']})")

print("\nTo collect 2 commodities (takes ~25 seconds):")
print("  results = collector.collect(commodities=['WTI', 'BRENT'])")
print("\nOr collect all 6 default commodities (~80 seconds):")
print("  results = collector.collect()")
print("\nCollector is working!")
