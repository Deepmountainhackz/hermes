import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv('ALPHA_VANTAGE_KEY')

# Configuration
SYMBOL = 'AAPL'  # Apple stock
URL = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&apikey={API_KEY}'

print(f"Fetching market data for {SYMBOL}...")

# Fetch the data
response = requests.get(URL)
data = response.json()

# Check if we got data
if 'Time Series (Daily)' in data:
    # Convert to a readable format
    time_series = data['Time Series (Daily)']
    
    # Get the 5 most recent days
    recent_days = list(time_series.items())[:5]
    
    print(f"\n✅ Success! Latest {SYMBOL} stock prices:\n")
    
    for date, prices in recent_days:
        open_price = prices['1. open']
        close_price = prices['4. close']
        print(f"Date: {date}")
        print(f"  Open:  ${open_price}")
        print(f"  Close: ${close_price}")
        print()
    
    print("🎉 Your first market data fetch complete!")
else:
    print("❌ Error fetching data. Response:")
    print(data)
    