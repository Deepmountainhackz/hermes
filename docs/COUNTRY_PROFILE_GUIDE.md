# 🌍 Country Profile Data Collector

Comprehensive collector for country demographics, languages, and statistics using the REST Countries API (free, no key required!)

## 📊 Data Collected

### Demographics
- **Population**: Total population count
- **Population Density**: People per km²
- **Area**: Total area in km²
- **Gini Coefficient**: Income inequality measure

### Languages
- All official languages spoken
- Native language names
- Total language count

### Geographic
- **Region & Subregion**: Europe, Asia, Africa, Americas, Oceania
- **Continent(s)**: Full continent list
- **Capital**: Capital city/cities
- **Coordinates**: Latitude & Longitude
- **Landlocked**: Whether country has ocean access
- **Borders**: Neighboring countries (ISO codes)
- **Border Count**: Number of neighboring countries

### Political & Administrative
- **Independence Status**: Whether country is independent
- **UN Membership**: United Nations member status
- **Status**: Official recognition status
- **ISO Codes**: cca2, cca3, ccn3 codes
- **CIOC Code**: International Olympic Committee code

### Economic
- **Currencies**: Name, code, symbol
- **Gini Index**: Income distribution data

### Cultural & Communication
- **Flag Emoji**: 🇩🇪 🇯🇵 🇧🇷
- **Coat of Arms**: Official emblem
- **Timezones**: All timezones in country
- **Calling Codes**: International dialing codes
- **TLD**: Internet domain (.de, .jp, .br)
- **Start of Week**: Monday/Sunday

### Sports & Organizations
- **FIFA Code**: Football/soccer organization code

### Additional
- **Google Maps Link**: Direct link to country
- **OpenStreetMap Link**: Alternative map link

---

## 🚀 Usage

### Basic Usage - Fetch by Name

```python
from fetch_country_data import CountryProfileCollector

collector = CountryProfileCollector()

# Fetch Germany
germany = collector.fetch_data('Germany')

if germany:
    print(f"Country: {germany['name']}")
    print(f"Population: {germany['population']:,}")
    print(f"Languages: {', '.join(germany['languages'])}")
    print(f"Capital: {', '.join(germany['capital'])}")
    print(f"Density: {germany['population_density']:.2f} people/km²")
```

### Fetch by ISO Code

```python
# Fetch Japan by code
japan = collector.fetch_data('JP', by_code=True)

# Works with both alpha-2 and alpha-3
usa = collector.fetch_data('USA', by_code=True)
uk = collector.fetch_data('GB', by_code=True)
```

### Fetch Multiple Countries

```python
countries = ['Germany', 'France', 'Italy', 'Spain']

for country_name in countries:
    country = collector.fetch_data(country_name)
    if country:
        print(f"{country['flag_emoji']} {country['name']}: "
              f"{country['population']:,} people, "
              f"{', '.join(country['languages'])}")
```

### Fetch by Region

```python
# Get all countries in Europe
europe = collector.fetch_countries_by_region('Europe')

print(f"Found {len(europe)} countries in Europe")
for country in europe[:5]:  # Show first 5
    print(f"{country['name']}: {country['population']:,}")
```

**Available Regions:**
- Europe
- Asia
- Africa
- Americas
- Oceania
- Antarctic (for research stations)

---

## 📋 Complete Data Structure

```python
{
    # Basic Info
    'name': 'Germany',
    'official_name': 'Federal Republic of Germany',
    'native_names': {...},
    
    # Codes
    'cca2': 'DE',
    'cca3': 'DEU',
    'ccn3': '276',
    'cioc': 'GER',
    
    # Demographics
    'population': 83240525,
    'area_km2': 357114.0,
    'population_density': 233.07,
    
    # Languages
    'languages': ['German'],
    'total_languages': 1,
    
    # Geographic
    'region': 'Europe',
    'subregion': 'Western Europe',
    'continents': ['Europe'],
    'capital': ['Berlin'],
    'latitude': 51.0,
    'longitude': 9.0,
    'landlocked': False,
    'borders': ['AUT', 'BEL', 'CZE', 'DNK', 'FRA', 'LUX', 'NLD', 'POL', 'CHE'],
    'border_count': 9,
    
    # Economic
    'currencies': [
        {
            'code': 'EUR',
            'name': 'Euro',
            'symbol': '€'
        }
    ],
    'gini': {'2016': 31.9},
    
    # Political
    'independent': True,
    'un_member': True,
    'status': 'officially-assigned',
    
    # Time & Communication
    'timezones': ['UTC+01:00'],
    'timezone_count': 1,
    'tld': ['.de'],
    'calling_codes': '+49',
    
    # Cultural
    'flag_emoji': '🇩🇪',
    'coat_of_arms': 'https://...',
    'start_of_week': 'monday',
    
    # Additional
    'maps': {
        'google': 'https://goo.gl/maps/...',
        'openstreetmap': 'https://www.openstreetmap.org/...'
    },
    'fifa': 'GER',
    
    # Metadata
    'collection_time': '2025-11-04T14:10:27.123456',
    'status': 'success'
}
```

---

## 💡 Use Cases

### 1. Demographic Research
```python
# Compare population densities
countries = ['Netherlands', 'Belgium', 'Bangladesh', 'Mongolia']
for name in countries:
    c = collector.fetch_data(name)
    print(f"{c['name']}: {c['population_density']:.1f} people/km²")
```

### 2. Language Analysis
```python
# Find multilingual countries
country = collector.fetch_data('Switzerland')
print(f"{country['name']} speaks {country['total_languages']} languages:")
print(', '.join(country['languages']))
```

### 3. Regional Statistics
```python
# Get all Asian countries
asia = collector.fetch_countries_by_region('Asia')
total_pop = sum(c['population'] for c in asia)
print(f"Asia total population: {total_pop:,}")
```

### 4. Border Analysis
```python
# Countries with most borders
country = collector.fetch_data('China')
print(f"{country['name']} borders {country['border_count']} countries:")
print(', '.join(country['borders']))
```

### 5. Economic Comparison
```python
# Compare currencies
countries = ['Japan', 'UK', 'USA', 'Switzerland']
for name in countries:
    c = collector.fetch_data(name)
    curr = c['currencies'][0]
    print(f"{c['flag_emoji']} {c['name']}: {curr['name']} ({curr['symbol']})")
```

---

## 🎯 Integration with Your Project

### Project Structure
```
HERMES/
├── services/
│   ├── geography/              ← NEW FOLDER
│   │   ├── __init__.py
│   │   └── fetch_country_data.py
│   ├── space/
│   ├── markets/
│   ├── social/
│   └── environment/
```

### Create Geography Service

**1. Create folder:**
```bash
mkdir services/geography
```

**2. Add `__init__.py`:**
```python
"""
Geography and country data collection services
"""

from .fetch_country_data import CountryProfileCollector

__all__ = ['CountryProfileCollector']
```

**3. Copy collector:**
```bash
cp fetch_country_data.py services/geography/
```

---

## 🧪 Testing

### Run Standalone
```bash
python fetch_country_data.py
```

### Add to Test Suite

Update `test_all_collectors.py`:

```python
def test_countries():
    """Test Country Profile Collector"""
    print("\n" + "="*60)
    print("🌍 TESTING COUNTRY PROFILE COLLECTOR")
    print("="*60)
    
    try:
        from services.geography.fetch_country_data import CountryProfileCollector
        collector = CountryProfileCollector()
        data = collector.fetch_data('Japan')
        
        if data:
            print(f"✅ SUCCESS!")
            print(f"   Country: {data['name']}")
            print(f"   Population: {data['population']:,}")
            print(f"   Languages: {', '.join(data['languages'])}")
            print(f"   Density: {data['population_density']:.2f} people/km²")
            return True
        else:
            print("❌ FAILED!")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

# Add to results
results = {
    'ISS': test_iss(),
    'NEO': test_neo(),
    'Solar': test_solar(),
    'Markets': test_markets(),
    'News': test_news(),
    'Countries': test_countries(),  # ADD THIS
    'Weather': test_weather()
}
```

---

## 🔑 API Details

**API:** REST Countries API v3.1
- **URL:** https://restcountries.com
- **Cost:** FREE
- **Rate Limits:** None (reasonable use)
- **Authentication:** No API key required! ✨
- **Data Source:** Multiple authoritative sources (UN, CIA World Factbook, etc.)

---

## 📈 Advanced Features

### Filter by Population
```python
# Get large countries only
asia = collector.fetch_countries_by_region('Asia')
large_countries = [c for c in asia if c['population'] > 50_000_000]

for country in sorted(large_countries, key=lambda x: x['population'], reverse=True):
    print(f"{country['name']}: {country['population']:,}")
```

### Language Statistics
```python
# Count total languages in region
europe = collector.fetch_countries_by_region('Europe')
all_languages = set()
for country in europe:
    all_languages.update(country['languages'])

print(f"Europe has {len(all_languages)} unique languages")
```

### UN Member Analysis
```python
# Count UN members
all_countries = []
for region in ['Europe', 'Asia', 'Africa', 'Americas', 'Oceania']:
    countries = collector.fetch_countries_by_region(region)
    all_countries.extend(countries)

un_members = [c for c in all_countries if c['un_member']]
print(f"UN has {len(un_members)} member states")
```

---

## 🎨 Sample Output

```
🇩🇪 Germany (Federal Republic of Germany)
   Region: Europe - Western Europe
   Population: 83,240,525 people
   Area: 357,114.00 km²
   Density: 233.07 people/km²
   Capital: Berlin
   Languages: German
   Currencies: Euro
   Bordering Countries: 9 (AUT, BEL, CZE, DNK, FRA, LUX, NLD, POL, CHE)
   Timezones: UTC+01:00
   UN Member: Yes
   Flag: 🇩🇪

🇯🇵 Japan
   Population: 125,836,021
   Languages: Japanese
   Density: 334.49 people/km²
```

---

## ✨ Key Features

✅ **No API Key Required** - Works immediately  
✅ **Comprehensive Data** - 30+ data points per country  
✅ **Error Handling** - Retry logic and validation  
✅ **Multiple Search Methods** - By name, code, or region  
✅ **Professional Logging** - Track all operations  
✅ **Rich Demographics** - Population, density, languages  
✅ **Geographic Details** - Borders, coordinates, timezones  
✅ **Economic Data** - Currencies, Gini coefficient  
✅ **Cultural Info** - Flags, languages, start of week  

---

## 🚀 Ready to Use!

The collector is production-ready and needs **zero configuration**. Just copy it to your project and start collecting country data!

```python
from services.geography.fetch_country_data import CountryProfileCollector

collector = CountryProfileCollector()
data = collector.fetch_data('Brazil')

print(f"{data['flag_emoji']} {data['name']}")
print(f"Population: {data['population']:,}")
print(f"Languages: {', '.join(data['languages'])}")
```

That's it! 🎉
