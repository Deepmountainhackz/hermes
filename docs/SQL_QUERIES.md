# SQL Query Examples for Hermes Database

This file contains useful SQL queries for analyzing data in the Hermes database.

---

## Basic Queries

### Count Records in Each Table

```sql
SELECT 'stocks' as table_name, COUNT(*) as count FROM stocks
UNION ALL
SELECT 'iss_positions', COUNT(*) FROM iss_positions
UNION ALL
SELECT 'near_earth_objects', COUNT(*) FROM near_earth_objects
UNION ALL
SELECT 'solar_flares', COUNT(*) FROM solar_flares
UNION ALL
SELECT 'weather', COUNT(*) FROM weather
UNION ALL
SELECT 'news', COUNT(*) FROM news;
```

### View All Table Names

```sql
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
```

### Check Database Size

```sql
SELECT page_count * page_size as size_bytes 
FROM pragma_page_count(), pragma_page_size();
```

---

## Stock Market Queries

### Latest Stock Prices

```sql
SELECT symbol, date, close as price, volume
FROM stocks
WHERE date = (SELECT MAX(date) FROM stocks)
ORDER BY symbol;
```

### Stock Price Trends (Last 30 Days)

```sql
SELECT symbol, date, close
FROM stocks
WHERE date >= date('now', '-30 days')
ORDER BY symbol, date;
```

### Daily Price Changes

```sql
SELECT 
    symbol,
    date,
    close,
    ROUND(((close - open) / open * 100), 2) as daily_change_pct
FROM stocks
WHERE date = (SELECT MAX(date) FROM stocks)
ORDER BY daily_change_pct DESC;
```

### Best Performing Stock (All Time)

```sql
SELECT 
    symbol,
    ROUND(((MAX(close) - MIN(close)) / MIN(close) * 100), 2) as total_gain_pct
FROM stocks
GROUP BY symbol
ORDER BY total_gain_pct DESC;
```

### Average Volume by Stock

```sql
SELECT 
    symbol,
    AVG(volume) as avg_volume,
    MIN(volume) as min_volume,
    MAX(volume) as max_volume
FROM stocks
GROUP BY symbol;
```

---

## Space Queries

### Latest ISS Position

```sql
SELECT latitude, longitude, altitude_km, speed_kmh, timestamp
FROM iss_positions
ORDER BY timestamp DESC
LIMIT 1;
```

### ISS Track History (Last 24 Hours)

```sql
SELECT latitude, longitude, timestamp
FROM iss_positions
WHERE timestamp >= datetime('now', '-1 day')
ORDER BY timestamp DESC;
```

### Hazardous Near-Earth Objects

```sql
SELECT name, date, diameter_max_m, velocity_kmh, miss_distance_km
FROM near_earth_objects
WHERE is_hazardous = 1
ORDER BY date;
```

### Largest Near-Earth Objects

```sql
SELECT name, date, diameter_max_m, velocity_kmh, is_hazardous
FROM near_earth_objects
ORDER BY diameter_max_m DESC
LIMIT 10;
```

### Closest Near-Earth Objects

```sql
SELECT name, date, miss_distance_km, velocity_kmh, is_hazardous
FROM near_earth_objects
ORDER BY miss_distance_km ASC
LIMIT 10;
```

### Upcoming NEOs (Next 7 Days)

```sql
SELECT name, date, diameter_max_m, miss_distance_km, is_hazardous
FROM near_earth_objects
WHERE date BETWEEN date('now') AND date('now', '+7 days')
ORDER BY date;
```

### Solar Flare Activity (Last 30 Days)

```sql
SELECT class_type, begin_time, peak_time, source_location
FROM solar_flares
WHERE begin_time >= datetime('now', '-30 days')
ORDER BY begin_time DESC;
```

---

## Weather Queries

### Current Weather (All Cities)

```sql
SELECT city, temperature_c, humidity_percent, weather_description
FROM weather
WHERE timestamp = (SELECT MAX(timestamp) FROM weather)
ORDER BY city;
```

### Temperature Trends by City

```sql
SELECT 
    city,
    AVG(temperature_c) as avg_temp,
    MIN(temperature_c) as min_temp,
    MAX(temperature_c) as max_temp
FROM weather
GROUP BY city
ORDER BY avg_temp DESC;
```

### Hottest and Coldest Cities

```sql
-- Hottest
SELECT city, temperature_c, timestamp
FROM weather
ORDER BY temperature_c DESC
LIMIT 1;

-- Coldest
SELECT city, temperature_c, timestamp
FROM weather
ORDER BY temperature_c ASC
LIMIT 1;
```

### Humidity Comparison

```sql
SELECT city, AVG(humidity_percent) as avg_humidity
FROM weather
GROUP BY city
ORDER BY avg_humidity DESC;
```

---

## News Queries

### Latest Headlines (All Sources)

```sql
SELECT source, title, published
FROM news
ORDER BY published DESC
LIMIT 20;
```

### News by Source

```sql
SELECT source, COUNT(*) as article_count
FROM news
GROUP BY source
ORDER BY article_count DESC;
```

### Recent News from Specific Source

```sql
SELECT title, published, link
FROM news
WHERE source = 'BBC News'
ORDER BY published DESC
LIMIT 10;
```

### News from Today

```sql
SELECT source, title, published
FROM news
WHERE date(published) = date('now')
ORDER BY published DESC;
```

---

## Cross-Layer Analysis

### Collection Activity by Layer

```sql
SELECT 
    layer,
    COUNT(*) as collections,
    SUM(records_collected) as total_records,
    MAX(timestamp) as last_collection
FROM collection_metadata
GROUP BY layer
ORDER BY total_records DESC;
```

### Collection Success Rate

```sql
SELECT 
    layer,
    collector,
    COUNT(*) as total_runs,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
    ROUND(SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as success_rate_pct
FROM collection_metadata
GROUP BY layer, collector
ORDER BY success_rate_pct DESC;
```

### Data Freshness Check

```sql
SELECT 
    'stocks' as data_source,
    MAX(date) as latest_data,
    JULIANDAY('now') - JULIANDAY(MAX(date)) as days_old
FROM stocks
UNION ALL
SELECT 
    'iss_positions',
    MAX(timestamp),
    JULIANDAY('now') - JULIANDAY(MAX(timestamp))
FROM iss_positions
UNION ALL
SELECT 
    'weather',
    MAX(timestamp),
    JULIANDAY('now') - JULIANDAY(MAX(timestamp))
FROM weather
UNION ALL
SELECT 
    'news',
    MAX(published),
    JULIANDAY('now') - JULIANDAY(MAX(published))
FROM news;
```

---

## Advanced Analytics

### Stock Volatility Analysis

```sql
SELECT 
    symbol,
    ROUND(AVG(high - low), 2) as avg_daily_range,
    ROUND(MAX(high - low), 2) as max_daily_range,
    ROUND(MIN(high - low), 2) as min_daily_range
FROM stocks
GROUP BY symbol
ORDER BY avg_daily_range DESC;
```

### Weather Extremes

```sql
SELECT 
    city,
    MAX(temperature_c) as highest_temp,
    MIN(temperature_c) as lowest_temp,
    MAX(temperature_c) - MIN(temperature_c) as temp_range
FROM weather
GROUP BY city
ORDER BY temp_range DESC;
```

### NEO Threat Assessment

```sql
SELECT 
    COUNT(*) as total_neos,
    SUM(CASE WHEN is_hazardous = 1 THEN 1 ELSE 0 END) as hazardous_count,
    ROUND(AVG(diameter_max_m), 2) as avg_diameter_m,
    ROUND(MIN(miss_distance_km), 2) as closest_approach_km
FROM near_earth_objects
WHERE date >= date('now');
```

---

## Maintenance Queries

### Delete Old Data (Older than 90 Days)

```sql
-- Weather data
DELETE FROM weather 
WHERE timestamp < datetime('now', '-90 days');

-- ISS positions
DELETE FROM iss_positions 
WHERE timestamp < datetime('now', '-90 days');

-- Old news
DELETE FROM news 
WHERE published < datetime('now', '-90 days');
```

### Vacuum Database (Optimize)

```sql
VACUUM;
```

### Check for Duplicates

```sql
-- Stocks duplicates
SELECT date, symbol, COUNT(*)
FROM stocks
GROUP BY date, symbol
HAVING COUNT(*) > 1;

-- News duplicates
SELECT link, COUNT(*)
FROM news
GROUP BY link
HAVING COUNT(*) > 1;
```

---

## How to Run These Queries

### Option 1: Using Python

```python
import sqlite3

conn = sqlite3.connect('hermes.db')
cursor = conn.cursor()

# Run your query
cursor.execute("YOUR SQL QUERY HERE")
results = cursor.fetchall()

for row in results:
    print(row)

conn.close()
```

### Option 2: Using SQLite Command Line

```bash
sqlite3 hermes.db "YOUR SQL QUERY HERE"
```

### Option 3: Using query_hermes.py

Modify the `query_hermes.py` script to include your custom query.

---

## Tips

1. **Always backup before running DELETE queries:**
   ```bash
   cp hermes.db hermes_backup.db
   ```

2. **Use LIMIT when testing:**
   ```sql
   SELECT * FROM stocks LIMIT 10;
   ```

3. **Format dates consistently:**
   ```sql
   date('now')  -- Today
   datetime('now', '-7 days')  -- 7 days ago
   ```

4. **Use EXPLAIN QUERY PLAN for optimization:**
   ```sql
   EXPLAIN QUERY PLAN SELECT * FROM stocks WHERE symbol = 'AAPL';
   ```

---

**Happy Querying! 📊**
