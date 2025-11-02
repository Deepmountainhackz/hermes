import sqlite3
import pandas as pd

conn = sqlite3.connect('hermes.db')

# Query the data
print("📊 Database Contents:\n")

# Count rows in each table
tables = ['stocks', 'iss_positions', 'near_earth_objects', 'solar_flares', 'weather', 'news']

for table in tables:
    count = pd.read_sql(f'SELECT COUNT(*) as count FROM {table}', conn).iloc[0]['count']
    print(f"   {table}: {count} rows")

print("\n" + "="*50)
print("Latest Stock Prices:")
print("="*50 + "\n")

# Show latest stock prices
df = pd.read_sql('''
    SELECT symbol, date, close 
    FROM stocks 
    ORDER BY date DESC, symbol
    LIMIT 10
''', conn)

print(df.to_string(index=False))

conn.close()