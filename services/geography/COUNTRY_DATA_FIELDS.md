# 🌍 Country Profile Data - Quick Reference Card

## All 40+ Data Points Available

### 📊 DEMOGRAPHICS (5 fields)
```
✓ population          - Total population
✓ area_km2           - Total area in km²
✓ population_density  - People per km²
✓ gini               - Income inequality index
✓ independent        - Independence status
```

### 🗣️ LANGUAGES (3 fields)
```
✓ languages          - List of all languages ['German', 'French']
✓ total_languages    - Count of languages
✓ native_names       - Native language name variations
```

### 🌏 GEOGRAPHIC (11 fields)
```
✓ region             - Major region (Europe, Asia, etc.)
✓ subregion          - Detailed region (Western Europe)
✓ continents         - List of continents
✓ capital            - Capital city/cities
✓ latitude           - Latitude coordinate
✓ longitude          - Longitude coordinate
✓ landlocked         - Has ocean access? (bool)
✓ borders            - ISO codes of neighboring countries
✓ border_count       - Number of neighbors
✓ timezones          - All timezones
✓ timezone_count     - Number of timezones
```

### 💰 ECONOMIC (2 fields)
```
✓ currencies         - [{code, name, symbol}]
✓ gini               - Income distribution data
```

### 🏛️ POLITICAL (5 fields)
```
✓ independent        - Independence status (bool)
✓ un_member          - UN membership (bool)
✓ status             - Recognition status
✓ cca2               - ISO 3166-1 alpha-2 code (DE, JP)
✓ cca3               - ISO 3166-1 alpha-3 code (DEU, JPN)
```

### 📱 COMMUNICATION (4 fields)
```
✓ calling_codes      - International dialing codes (+49)
✓ tld                - Internet domains (['.de'])
✓ start_of_week      - Monday or Sunday
✓ timezones          - All timezone strings
```

### 🎨 CULTURAL (4 fields)
```
✓ flag_emoji         - Flag emoji (🇩🇪 🇯🇵)
✓ coat_of_arms       - Official emblem URL
✓ fifa               - FIFA organization code
✓ cioc               - Olympic Committee code
```

### 🗺️ NAVIGATION (2 fields)
```
✓ maps.google        - Google Maps link
✓ maps.openstreetmap - OpenStreetMap link
```

### 📝 IDENTIFIERS (6 fields)
```
✓ name               - Common name
✓ official_name      - Official country name
✓ native_names       - Native name variations
✓ cca2               - 2-letter code
✓ cca3               - 3-letter code
✓ ccn3               - Numeric code
```

### ⏰ METADATA (2 fields)
```
✓ collection_time    - When data was fetched
✓ status             - Success/failure status
```

---

## 🎯 Most Useful Fields

### For Demographics Research:
- `population`
- `area_km2`
- `population_density`
- `gini`

### For Cultural Analysis:
- `languages`
- `flag_emoji`
- `currencies`
- `capital`

### For Geographic Studies:
- `region`
- `subregion`
- `borders`
- `latitude` / `longitude`

### For Economic Analysis:
- `currencies`
- `gini`
- `population`
- `un_member`

---

## 📋 Example Queries

### Get Basic Profile
```python
data = collector.fetch_data('Germany')
print(f"{data['name']}: {data['population']:,} people")
```

### Language Analysis
```python
data = collector.fetch_data('Switzerland')
print(f"Languages: {', '.join(data['languages'])}")
# Output: Languages: French, Swiss German, Italian, Romansh
```

### Economic Data
```python
data = collector.fetch_data('Japan')
for curr in data['currencies']:
    print(f"{curr['name']}: {curr['symbol']}")
# Output: Japanese yen: ¥
```

### Geographic Info
```python
data = collector.fetch_data('Brazil')
print(f"Region: {data['region']}")
print(f"Subregion: {data['subregion']}")
print(f"Borders {data['border_count']} countries")
# Output: Region: Americas
#         Subregion: South America
#         Borders 10 countries
```

### Density Comparison
```python
countries = ['Monaco', 'Singapore', 'Hong Kong', 'Bangladesh']
for name in countries:
    data = collector.fetch_data(name)
    print(f"{data['name']}: {data['population_density']:.0f} people/km²")
```

---

## 🔍 Search Methods

### By Name
```python
collector.fetch_data('Germany')
collector.fetch_data('United States')
```

### By ISO Code (2 or 3 letter)
```python
collector.fetch_data('DE', by_code=True)
collector.fetch_data('USA', by_code=True)
collector.fetch_data('JPN', by_code=True)
```

### By Region
```python
collector.fetch_countries_by_region('Europe')
collector.fetch_countries_by_region('Asia')
collector.fetch_countries_by_region('Africa')
```

---

## ✨ Pro Tips

1. **No API Key Needed** - Works immediately!
2. **Cache Results** - Save frequently accessed countries
3. **Batch Requests** - Small delay between requests
4. **Error Handling** - Always check if data is not None
5. **Rich Data** - 40+ fields per country!

---

## 🌟 Sample Complete Output

```json
{
  "name": "Switzerland",
  "official_name": "Swiss Confederation",
  "population": 8654622,
  "area_km2": 41284,
  "population_density": 209.65,
  "languages": ["French", "Swiss German", "Italian", "Romansh"],
  "total_languages": 4,
  "region": "Europe",
  "subregion": "Western Europe",
  "capital": ["Bern"],
  "currencies": [
    {"code": "CHF", "name": "Swiss franc", "symbol": "Fr."}
  ],
  "borders": ["AUT", "FRA", "ITA", "LIE", "DEU"],
  "border_count": 5,
  "landlocked": true,
  "flag_emoji": "🇨🇭",
  "timezones": ["UTC+01:00"],
  "calling_codes": "+41",
  "un_member": true,
  "independent": true
}
```

---

## 🎉 Ready to Use!

All 40+ data points, zero configuration, no API key required!
