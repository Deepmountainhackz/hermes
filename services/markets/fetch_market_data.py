import os
import requests
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from datetime import datetime

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv('ALPHA_VANTAGE_KEY')

# Database path
DATABASE_PATH = 'hermes.db'

# Configuration - Add more stocks here!
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']

def fetch_stock_data(symbol):
    """
    Fetch daily stock data for a given symbol.
    Returns a dictionary with the data, or None if error.
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    
    print(f"Fetching data for {symbol}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            return data['Time Series (Daily)']
        elif 'Note' in data:
            print(f"⚠️  API rate limit hit for {symbol}. Wait a minute and try again.")
            return None
        else:
            print(f"❌ Unexpected response for {symbol}: {data}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout for {symbol}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed for {symbol}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error for {symbol}: {e}")
        return None

def save_to_database(symbol, time_series):
    """
    Save stock data to the database.
    """
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(time_series, orient='index')
    
    # Rename columns to match database schema
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Add metadata columns
    df['symbol'] = symbol
    df['date'] = df.index
    df['timestamp'] = datetime.now().isoformat()
    
    # Reorder columns to match database
    df = df[['timestamp', 'date', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
    
    # Convert data types
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(int)
    
    try:
        # Insert into database (ignore duplicates due to UNIQUE constraint)
        df.to_sql('stocks', conn, if_exists='append', index=False)
        
        print(f"✅ Saved {len(df)} days of data for {symbol} to database")
        
        # Show preview of latest data
        print(f"\n📊 Latest prices for {symbol}:")
        latest = df.iloc[0]
        print(f"   Date:  {latest['date']}")
        print(f"   Open:  ${latest['open']}")
        print(f"   Close: ${latest['close']}")
        print()
        
        return len(df)
        
    except sqlite3.IntegrityError as e:
        # Duplicate data - this is normal if running multiple times same day
        print(f"⚠️  Some {symbol} data already exists in database (skipped duplicates)")
        print()
        return 0
    except Exception as e:
        print(f"❌ Database error for {symbol}: {e}")
        print()
        return 0
    finally:
        conn.close()

def main():
    """
    Main function - orchestrates everything.
    """
    print("=" * 50)
    print("HERMES Market Data Fetcher (Database Mode)")
    print("=" * 50)
    print()
    
    all_data = {}
    total_saved = 0
    
    # Fetch data for each symbol
    for symbol in SYMBOLS:
        time_series = fetch_stock_data(symbol)
        
        if time_series:
            # Save to database
            saved_count = save_to_database(symbol, time_series)
            total_saved += saved_count
            all_data[symbol] = True
        else:
            print(f"⚠️  Skipping {symbol} due to errors\n")
            all_data[symbol] = False
    
    # Summary
    print("=" * 50)
    print(f"✅ Successfully processed {len([v for v in all_data.values() if v])}/{len(SYMBOLS)} symbols")
    print(f"💾 Total records saved to database: {total_saved}")
    print(f"🗄️  Database: {DATABASE_PATH}")
    print("=" * 50)

# Run the script
if __name__ == "__main__":
    main()