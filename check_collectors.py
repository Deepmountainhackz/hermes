#!/usr/bin/env python3
"""Quick diagnostic script for collectors."""
import sys
sys.path.insert(0, '.')

from core.config import Config
from core.database import DatabasePool
import psycopg

def main():
    config = Config()

    print("=" * 50)
    print("HERMES COLLECTOR DIAGNOSTIC")
    print("=" * 50)

    # Check database connection
    print("\n1. Database Connection:")
    try:
        conn_str = f'host={config.DATABASE_HOST} port={config.DATABASE_PORT} dbname={config.DATABASE_NAME} user={config.DATABASE_USER} password={config.DATABASE_PASSWORD}'
        with psycopg.connect(conn_str) as conn:
            print(f"   Connected to {config.DATABASE_HOST}:{config.DATABASE_PORT}")

            with conn.cursor() as cur:
                # Check tables
                cur.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public' ORDER BY table_name
                """)
                tables = [r[0] for r in cur.fetchall()]
                print(f"   Tables: {len(tables)}")

                # Check data counts
                print("\n2. Data Counts:")
                for table in ['stocks', 'crypto', 'forex', 'commodities', 'economic_indicators', 'weather', 'news']:
                    if table in tables:
                        cur.execute(f'SELECT COUNT(*) FROM {table}')
                        count = cur.fetchone()[0]
                        cur.execute(f'SELECT MAX(timestamp) FROM {table}')
                        last = cur.fetchone()[0]
                        status = "OK" if count > 0 else "EMPTY"
                        print(f"   {table}: {count} rows [{status}] - Last: {last}")
                    else:
                        print(f"   {table}: TABLE MISSING")

    except Exception as e:
        print(f"   ERROR: {e}")
        return

    # Check API keys
    print("\n3. API Keys:")
    keys = [
        ('ALPHA_VANTAGE_API_KEY', config.ALPHA_VANTAGE_API_KEY),
        ('FRED_API_KEY', getattr(config, 'FRED_API_KEY', None)),
        ('NEWS_API_KEY', getattr(config, 'NEWS_API_KEY', None)),
        ('OPENWEATHER_API_KEY', getattr(config, 'OPENWEATHER_API_KEY', None)),
    ]
    for name, value in keys:
        status = "SET" if value else "MISSING"
        print(f"   {name}: {status}")

    # Test a simple API call
    print("\n4. API Tests:")

    # Test CoinGecko (no API key needed)
    try:
        import requests
        resp = requests.get('https://api.coingecko.com/api/v3/ping', timeout=10)
        if resp.status_code == 200:
            print("   CoinGecko API: OK")
        else:
            print(f"   CoinGecko API: ERROR {resp.status_code}")
    except Exception as e:
        print(f"   CoinGecko API: ERROR - {e}")

    # Test Alpha Vantage
    try:
        import requests
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={config.ALPHA_VANTAGE_API_KEY}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        if 'Global Quote' in data:
            print("   Alpha Vantage API: OK")
        elif 'Note' in data:
            print("   Alpha Vantage API: RATE LIMITED")
        elif 'Error Message' in data:
            print(f"   Alpha Vantage API: ERROR - {data['Error Message']}")
        else:
            print(f"   Alpha Vantage API: UNKNOWN - {data}")
    except Exception as e:
        print(f"   Alpha Vantage API: ERROR - {e}")

    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
