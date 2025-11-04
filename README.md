# Production-Ready Data Collectors

All 5 data collectors are now complete with comprehensive error handling, logging, and retry logic! 🚀

## 📦 Files Created

1. **fetch_iss_data.py** - ISS Position Tracker
2. **fetch_neo_data.py** - Near Earth Objects (Asteroids)
3. **fetch_solar_data.py** - Solar Flares & Space Weather
4. **fetch_market_data.py** - Financial Markets (Crypto)
5. **fetch_news_data.py** - News Articles

---

## 🎯 Features (All Collectors)

✅ **Comprehensive Error Handling**
- Timeout handling
- Connection error recovery
- HTTP error management
- Rate limit detection
- JSON parsing validation

✅ **Retry Logic**
- 3 retry attempts with exponential backoff
- Configurable retry delays
- Smart rate limit handling

✅ **Professional Logging**
- INFO, WARNING, and ERROR levels
- Detailed execution traces
- Timestamp tracking

✅ **Data Enrichment**
- Additional metadata
- Timestamp normalization
- Statistical summaries

---

## 📋 Quick Start Guide

### 1. ISS Position Tracker

**API:** Open Notify (No key required)

```python
from fetch_iss_data import ISSDataCollector

collector = ISSDataCollector()
data = collector.fetch_data()

print(f"ISS Location: {data['latitude']}, {data['longitude']}")
```

**Returns:**
- Current latitude/longitude
- Timestamp (Unix & ISO format)
- Collection metadata

---

### 2. Near Earth Objects (NEO)

**API:** NASA NEO (DEMO_KEY included, get your own for higher limits)

```python
from fetch_neo_data import NEODataCollector

collector = NEODataCollector(api_key="YOUR_NASA_API_KEY")  # Optional
data = collector.fetch_data(days=1)

print(f"Total Objects: {data['total_objects']}")
print(f"Potentially Hazardous: {data['potentially_hazardous_count']}")
```

**Returns:**
- All NEO objects
- Potentially hazardous asteroids
- Size, velocity, and miss distance data
- Date range coverage

**Get NASA API Key:**
https://api.nasa.gov/ (Free, instant approval)

---

### 3. Solar Activity Tracker

**API:** NASA DONKI (DEMO_KEY included)

```python
from fetch_solar_data import SolarDataCollector

collector = SolarDataCollector(api_key="YOUR_NASA_API_KEY")  # Optional
data = collector.fetch_data(days_back=7)

print(f"X-Class Flares: {data['flare_breakdown']['X_class']}")
print(f"Total CME Events: {data['total_cme']}")
```

**Returns:**
- Solar flares (categorized by class: X, M, C, B, A)
- Coronal Mass Ejections (CME)
- 7-day activity summary

---

### 4. Financial Markets (Crypto)

**API:** CoinGecko (No key required)

```python
from fetch_market_data import MarketsDataCollector

collector = MarketsDataCollector()
coins = ['bitcoin', 'ethereum', 'cardano', 'solana']
data = collector.fetch_data(coins)

print(f"Global Market Cap: ${data['global_market_cap_usd']:,.0f}")
print(f"Bitcoin: ${data['cryptocurrencies'][0]['price_usd']}")
```

**Returns:**
- Individual coin prices & 24h changes
- Global market statistics
- Bitcoin dominance
- Market cap & volume data

---

### 5. News Aggregator

**APIs:** NewsAPI + Hacker News

```python
from fetch_news_data import NewsDataCollector

# NewsAPI key optional - will use Hacker News if not provided
collector = NewsDataCollector(api_key="YOUR_NEWSAPI_KEY")
data = collector.fetch_data(newsapi_category='technology', hn_limit=10)

print(f"Total Articles: {data['total_articles']}")
```

**Returns:**
- NewsAPI headlines (if key provided)
- Hacker News top stories (always available)
- Article metadata (title, source, URL, etc.)

**Get NewsAPI Key:**
https://newsapi.org/ (Free tier: 100 requests/day)

---

## 🔧 Installation

```bash
# Install required packages
pip install requests --break-system-packages
```

---

## 🎯 Usage Patterns

### Simple One-Shot Collection

```python
from fetch_iss_data import ISSDataCollector

collector = ISSDataCollector()
data = collector.fetch_data()

if data:
    print(f"Success! ISS at {data['latitude']}, {data['longitude']}")
else:
    print("Collection failed - check logs")
```

### Scheduled Collection Loop

```python
import time
from fetch_market_data import MarketsDataCollector

collector = MarketsDataCollector()

while True:
    data = collector.fetch_data()
    if data:
        print(f"BTC: ${data['cryptocurrencies'][0]['price_usd']}")
    time.sleep(300)  # Update every 5 minutes
```

### Error Handling Example

```python
from fetch_neo_data import NEODataCollector
import logging

logging.basicConfig(level=logging.INFO)

collector = NEODataCollector()
data = collector.fetch_data(days=7)

if data:
    hazardous = data['potentially_hazardous']
    if hazardous:
        print(f"⚠️  {len(hazardous)} potentially hazardous objects!")
        for neo in hazardous[:3]:
            print(f"  - {neo['name']}: {neo['diameter_max_km']:.2f} km")
else:
    print("Failed to collect NEO data")
```

---

## 📊 Data Structures

### ISS Data
```python
{
    'latitude': 45.2,
    'longitude': -122.5,
    'timestamp': 1699123456,
    'timestamp_readable': '2024-11-04T12:30:56',
    'collection_time': '2024-11-04T12:30:57.123456',
    'status': 'success'
}
```

### NEO Data
```python
{
    'total_objects': 15,
    'potentially_hazardous_count': 2,
    'start_date': '2024-11-04',
    'end_date': '2024-11-04',
    'all_objects': [...],
    'potentially_hazardous': [...],
    'status': 'success'
}
```

### Solar Data
```python
{
    'total_flares': 23,
    'total_cme': 5,
    'flare_breakdown': {
        'X_class': 1,
        'M_class': 5,
        'C_class': 15,
        'B_class': 2,
        'A_class': 0
    },
    'x_class_flares': [...],
    'all_cme': [...],
    'status': 'success'
}
```

### Market Data
```python
{
    'cryptocurrencies': [
        {
            'id': 'bitcoin',
            'name': 'Bitcoin',
            'price_usd': 35000.50,
            'change_24h': 2.5,
            'market_cap': 680000000000,
            'volume_24h': 25000000000
        }
    ],
    'global_market_cap_usd': 1200000000000,
    'bitcoin_dominance_percent': 56.7,
    'status': 'success'
}
```

### News Data
```python
{
    'total_articles': 20,
    'newsapi_count': 10,
    'hackernews_count': 10,
    'newsapi_articles': [...],
    'hackernews_stories': [...],
    'sources': ['TechCrunch', 'Hacker News', ...],
    'status': 'success'
}
```

---

## 🚨 Error Handling

All collectors implement:

1. **Network Errors**: Automatic retry with backoff
2. **Timeouts**: 10-15 second timeouts with retry
3. **Rate Limits**: Detection and extended backoff
4. **API Errors**: Graceful handling with logging
5. **Validation**: Response structure checking
6. **Fallbacks**: Partial data return when possible

---

## 📝 Logging Examples

```
2024-11-04 12:30:45 - fetch_iss_data - INFO - Fetching ISS position data (attempt 1/3)
2024-11-04 12:30:46 - fetch_iss_data - INFO - Successfully fetched ISS position: Lat 45.2, Lon -122.5
2024-11-04 12:30:46 - fetch_iss_data - INFO - ISS data collection successful
```

```
2024-11-04 12:31:15 - fetch_market_data - WARNING - Rate limit hit, waiting longer
2024-11-04 12:31:25 - fetch_market_data - INFO - Fetching crypto data (attempt 2/3)
2024-11-04 12:31:26 - fetch_market_data - INFO - Successfully fetched crypto data for 5 coins
```

---

## 🔑 API Keys Summary

| Collector | API Key Required? | Get Key From | Free Tier |
|-----------|------------------|--------------|-----------|
| ISS | ❌ No | N/A | Unlimited |
| NEO | ⚠️ Optional | https://api.nasa.gov/ | 1000/hour |
| Solar | ⚠️ Optional | https://api.nasa.gov/ | 1000/hour |
| Markets | ❌ No | N/A | Rate limited |
| News (HN) | ❌ No | N/A | Rate limited |
| News (API) | ✅ Yes | https://newsapi.org/ | 100/day |

**Note:** DEMO_KEY works for NASA APIs but has lower rate limits. Get your own key for production use!

---

## 🎨 Customization

### Adjust Retry Settings

```python
collector = ISSDataCollector()
collector.max_retries = 5
collector.retry_delay = 3
collector.timeout = 20
```

### Custom Logging Level

```python
import logging

logging.basicConfig(level=logging.DEBUG)  # More verbose
# or
logging.basicConfig(level=logging.ERROR)  # Only errors
```

---

## 🧪 Testing

Run each collector individually:

```bash
python fetch_iss_data.py
python fetch_neo_data.py
python fetch_solar_data.py
python fetch_market_data.py
python fetch_news_data.py
```

---

## 🚀 Next Steps

1. **Set Environment Variables** (optional but recommended):
   ```bash
   export NASA_API_KEY="your_key_here"
   export NEWSAPI_KEY="your_key_here"
   ```

2. **Test Each Collector**:
   Run the scripts to verify they work

3. **Integrate Into Your App**:
   Import and use the collectors in your main application

4. **Add Database Storage**:
   Save collected data to MongoDB, PostgreSQL, etc.

5. **Create Scheduled Jobs**:
   Use cron, celery, or APScheduler for automated collection

---

## 💡 Pro Tips

- **Rate Limiting**: Use delays between repeated calls
- **Caching**: Store data temporarily to reduce API calls
- **Monitoring**: Log all collections for debugging
- **Fallbacks**: Handle partial failures gracefully
- **Keys**: Use environment variables for API keys

---

## ✅ What's Done

All 5 collectors are production-ready with:
- ✅ Error handling
- ✅ Retry logic
- ✅ Logging
- ✅ Data validation
- ✅ Enrichment
- ✅ Documentation

Ready to deploy! 🎉
