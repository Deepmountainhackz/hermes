from core.database import db
from config.settings import settings

print("\n" + "="*60)
print("DATABASE CONNECTION TEST")
print("="*60)

try:
    print(f"Connecting to: {settings.DB_HOST}...")
    
    if db.health_check():
        print("✓ Database connection successful!")
        
        result = db.execute_query("SELECT version()", fetch_one=True)
        print(f"✓ PostgreSQL Version: {result['version'][:50]}...")
        
        print("="*60)
        print("✓ ALL DATABASE TESTS PASSED!")
        print("="*60 + "\n")
    else:
        print("✗ Database health check failed")
        
except Exception as e:
    print(f"✗ Database error: {e}")
    print("\nCheck your .env credentials!")
