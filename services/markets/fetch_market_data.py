import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv('ALPHA_VANTAGE_KEY')

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
        response.raise_for_status()  # Raises error for bad status codes
        data = response.json()
        
        # Check if we got valid data
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

def save_to_csv(symbol, time_series):
    """
    Save stock data to a CSV file.
    """
    # Convert to DataFrame (like an Excel table)
    df = pd.DataFrame.from_dict(time_series, orient='index')
    
    # Rename columns to be more readable
    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # Add symbol column
    df['Symbol'] = symbol
    
    # Sort by date (most recent first)
    df = df.sort_index(ascending=False)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data_{symbol}_{timestamp}.csv"
    
    # Save to CSV
    df.to_csv(filename, index_label='Date')
    print(f"✅ Saved {len(df)} days of data to {filename}")
    
    return df

def main():
    """
    Main function - orchestrates everything.
    """
    print("=" * 50)
    print("HERMES Market Data Fetcher")
    print("=" * 50)
    print()
    
    all_data = {}
    
    # Fetch data for each symbol
    for symbol in SYMBOLS:
        time_series = fetch_stock_data(symbol)
        
        if time_series:
            # Save to CSV
            df = save_to_csv(symbol, time_series)
            all_data[symbol] = df
            
            # Show preview of latest data
            print(f"\n📊 Latest prices for {symbol}:")
            latest_date = df.index[0]
            latest = df.iloc[0]
            print(f"   Date:  {latest_date}")
            print(f"   Open:  ${latest['Open']}")
            print(f"   Close: ${latest['Close']}")
            print()
        else:
            print(f"⚠️  Skipping {symbol} due to errors\n")
    
    # Summary
    print("=" * 50)
    print(f"✅ Successfully fetched data for {len(all_data)}/{len(SYMBOLS)} symbols")
    print("=" * 50)

# Run the script
if __name__ == "__main__":
    main()