# ERROR HANDLING & LOGGING - IMPLEMENTATION GUIDE

## What We Upgraded

Your weather collection script has been transformed from **functional** to **production-ready**.

---

## Key Improvements

### 1. **Comprehensive Logging** 📝

**Before:**
```python
print(f"✅ {city} collected")
```

**After:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_collection.log'),  # Saves to file
        logging.StreamHandler()  # Prints to console
    ]
)
logger = logging.getLogger(__name__)
logger.info("Collection started")
```

**Benefits:**
- Every action is logged with timestamp
- Errors saved to `weather_collection.log`
- Can debug issues after the fact
- Professional system administration

---

### 2. **Retry Logic** 🔄

**Before:**
```python
response = requests.get(url)
if response.status_code == 200:
    # success
```

**After:**
```python
def fetch_weather(self, city: str, retry_count: int = 0):
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 429:  # Rate limited
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY * (retry_count + 1))
                return self.fetch_weather(city, retry_count + 1)
    
    except requests.exceptions.Timeout:
        if retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return self.fetch_weather(city, retry_count + 1)
```

**Benefits:**
- Automatically retries failed requests (up to 3 times)
- Handles rate limiting gracefully
- Exponential backoff for retries
- More reliable data collection

---

### 3. **Data Validation** ✅

**Before:**
```python
temp = data['main']['temp']
# Insert directly into database
```

**After:**
```python
class WeatherDataValidator:
    @staticmethod
    def validate_temperature(temp: float) -> bool:
        return -100 <= temp <= 60
    
    @staticmethod
    def validate_humidity(humidity: int) -> bool:
        return 0 <= humidity <= 100

# Use validator
if not self.validator.validate_temperature(parsed['temp']):
    logger.warning(f"Invalid temperature: {parsed['temp']}")
    return None
```

**Benefits:**
- Catches obviously wrong data
- Prevents bad data in database
- Logs anomalies for investigation
- Data quality assurance

---

### 4. **Specific Error Handling** 🛡️

**Before:**
```python
try:
    response = requests.get(url)
except Exception as e:
    print(f"Error: {e}")
```

**After:**
```python
try:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    
except requests.exceptions.Timeout:
    logger.error(f"Timeout fetching weather for {city}")
    # Retry logic

except requests.exceptions.ConnectionError:
    logger.error(f"Connection error for {city}")
    # Retry logic

except requests.exceptions.RequestException as e:
    logger.error(f"Request error for {city}: {str(e)}")

except Exception as e:
    logger.error(f"Unexpected error for {city}: {str(e)}")
```

**Benefits:**
- Different handling for different errors
- Specific error messages
- Retry only when it makes sense
- Better debugging information

---

### 5. **HTTP Status Code Handling** 🔢

**Before:**
```python
if response.status_code == 200:
    # success
else:
    # fail
```

**After:**
```python
if response.status_code == 200:
    return data

elif response.status_code == 401:
    logger.error(f"Invalid API key")
    return None

elif response.status_code == 404:
    logger.warning(f"City not found: {city}")
    return None

elif response.status_code == 429:
    logger.warning(f"Rate limit exceeded")
    # Retry with delay

else:
    logger.error(f"API error: {response.status_code}")
    # Retry
```

**Benefits:**
- Appropriate action for each error type
- No wasted retries on permanent failures
- Clear error messages
- Better API usage

---

### 6. **Object-Oriented Design** 🏗️

**Before:**
```python
def collect_weather():
    # Everything in one function
```

**After:**
```python
class WeatherCollector:
    def __init__(self, api_key: str, db_path: str = 'hermes.db'):
        self.api_key = api_key
        self.db_path = db_path
        self.validator = WeatherDataValidator()
    
    def fetch_weather(self, city: str):
        # Focused functionality
    
    def parse_weather_data(self, data: Dict):
        # Focused functionality
    
    def save_to_database(self, weather_data: Dict):
        # Focused functionality
```

**Benefits:**
- Cleaner code organization
- Easier to test
- Reusable components
- Professional structure

---

### 7. **Type Hints** 🏷️

**Before:**
```python
def fetch_weather(city):
    return data
```

**After:**
```python
def fetch_weather(self, city: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
    """
    Fetch weather data for a city with retry logic
    
    Args:
        city: City name
        retry_count: Current retry attempt
        
    Returns:
        Weather data dict or None if failed
    """
    return data
```

**Benefits:**
- Clear function contracts
- IDE autocomplete support
- Self-documenting code
- Easier to maintain

---

### 8. **Comprehensive Statistics** 📊

**Before:**
```python
print(f"Collected {count} cities")
```

**After:**
```python
stats = {
    'total': len(CITIES),
    'successful': 0,
    'failed': 0,
    'invalid': 0
}

# After collection:
print(f"📊 Collection Summary:")
print(f"   Total cities: {stats['total']}")
print(f"   ✅ Successful: {stats['successful']}")
print(f"   ❌ Failed: {stats['failed']}")
print(f"   ⚠️  Invalid: {stats['invalid']}")
print(f"   Success rate: {stats['successful']/stats['total']*100:.1f}%")
```

**Benefits:**
- Clear success metrics
- Easy to spot issues
- Professional reporting
- Historical tracking

---

### 9. **Exit Codes** 🚪

**Before:**
```python
if __name__ == '__main__':
    collect_weather()
```

**After:**
```python
def main():
    try:
        stats = collector.collect_all()
        
        if stats['successful'] == 0:
            return 1  # Complete failure
        elif stats['successful'] < stats['total'] * 0.5:
            return 1  # Less than 50% success
        else:
            return 0  # Success
    
    except KeyboardInterrupt:
        return 130  # Standard interrupted code
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    exit(main())
```

**Benefits:**
- GitHub Actions can detect failures
- Scripts can chain properly
- Professional Unix/Linux conventions
- Automation-friendly

---

### 10. **Configuration Constants** ⚙️

**Before:**
```python
time.sleep(1.2)
response = requests.get(url)
```

**After:**
```python
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 1.2

# Usage:
time.sleep(RATE_LIMIT_DELAY)
response = requests.get(url, timeout=REQUEST_TIMEOUT)
```

**Benefits:**
- Easy to adjust settings
- Clear what values mean
- Single source of truth
- Professional configuration management

---

## File Generated: `weather_collection.log`

**Example log file:**
```
2025-11-04 10:15:23,451 - __main__ - INFO - WeatherCollector initialized
2025-11-04 10:15:23,452 - __main__ - INFO - Starting weather collection for 50 cities
2025-11-04 10:15:25,612 - __main__ - DEBUG - Successfully fetched weather for New York
2025-11-04 10:15:25,615 - __main__ - DEBUG - Saved weather data for New York
2025-11-04 10:15:28,234 - __main__ - ERROR - Timeout fetching weather for Los Angeles
2025-11-04 10:15:30,442 - __main__ - DEBUG - Successfully fetched weather for Los Angeles
2025-11-04 10:15:30,445 - __main__ - DEBUG - Saved weather data for Los Angeles
...
2025-11-04 10:17:45,123 - __main__ - INFO - Collection complete: 48/50 successful
```

**This log file:**
- Persists across runs
- Shows exactly what happened
- Helps debug failures
- Proves collection worked

---

## Comparison

| Aspect | Before | After |
|--------|--------|-------|
| **Error Handling** | Basic try/except | Specific exception types, retry logic |
| **Logging** | Print statements | Professional logging to file + console |
| **Validation** | None | Temperature, humidity, wind speed checks |
| **Retries** | None | Up to 3 retries with backoff |
| **Status Codes** | 200 vs. other | Handles 401, 404, 429 specifically |
| **Statistics** | Basic count | Comprehensive success/fail/invalid tracking |
| **Code Structure** | Single function | Object-oriented with classes |
| **Type Safety** | None | Type hints throughout |
| **Documentation** | Comments | Docstrings + type hints + logging |
| **Exit Codes** | None | Proper Unix exit codes |

---

## How to Use

### Run with Logging

```bash
python collect_weather_50cities.py
```

**Output:**
- Console shows progress
- Creates `weather_collection.log` file
- Returns exit code (0 = success, 1 = failure)

### Check Logs

```bash
# View full log
cat weather_collection.log

# View recent errors
grep ERROR weather_collection.log

# View last collection
tail -n 100 weather_collection.log
```

### Integration with GitHub Actions

```yaml
- name: Collect Weather Data
  run: python collect_weather_50cities.py
  
- name: Check if collection succeeded
  run: |
    if [ $? -ne 0 ]; then
      echo "Weather collection failed!"
      exit 1
    fi
```

---

## Benefits Summary

### For Development
- Easier to debug problems
- Clear error messages
- Historical log of what happened
- Professional code structure

### For Production
- Handles failures gracefully
- Continues despite individual failures
- Retries transient errors
- Validates data quality

### For Maintenance
- Logs show exactly what went wrong
- Easy to adjust configuration
- Clear code organization
- Type hints prevent bugs

### For Portfolio
- Shows professional coding practices
- Demonstrates error handling skills
- Production-ready code quality
- Industry-standard patterns

---

## Next Steps

1. **Test it:** Run the new script and verify it works
2. **Check logs:** Look at `weather_collection.log`
3. **Monitor:** Watch success rate over time
4. **Apply pattern:** Use same approach for other collectors

---

## Impact

**This single upgrade took your code from:**
- ⭐⭐⭐ "Works for demo" 
- **TO:** ⭐⭐⭐⭐ "Production-ready"

**Employers will see:**
- Professional error handling
- Proper logging
- Data validation
- Retry logic
- OOP design
- Type safety
- Exit codes

**This is the difference between "I can code" and "I can build production systems."**

---

## Files to Replace

1. **Replace:** `collect_weather_50cities.py` with the new version
2. **New file:** `weather_collection.log` (created automatically)
3. **Keep:** All other files unchanged

---

**Ready to deploy this production-ready version!** 🚀
