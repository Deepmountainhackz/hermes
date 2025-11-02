import sqlite3

conn = sqlite3.connect('hermes.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("DATABASE SCHEMA:\n")
for table in tables:
    table_name = table[0]
    print(f"\n{'='*60}")
    print(f"TABLE: {table_name}")
    print('='*60)
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
