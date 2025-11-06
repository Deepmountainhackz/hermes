# 🌍 Add Natural Disaster Tracking - Earthquakes & Storms

## 🎯 What You're Adding

### **Earthquakes 🌍**
- Recent significant earthquakes (M4.5+)
- Global coverage via USGS
- Magnitude, location, depth, tsunami warnings
- **FREE - No API key needed!**

### **Severe Storms 🌪️**
- Active hurricanes, typhoons, cyclones
- Severe weather events
- Global coverage via NASA EONET
- **FREE - No API key needed!**

---

## 💡 Investment Intelligence Value

**Earthquakes:**
- Infrastructure damage assessment
- Supply chain disruptions
- Construction/materials sector opportunities
- Insurance sector impacts
- Regional economic impacts

**Storms:**
- Shipping route disruptions
- Agriculture/crop damage
- Energy infrastructure (offshore platforms, refineries)
- Insurance claims spikes
- Supply chain delays

---

## 📦 Files to Install

Download these 3 files:

1. **fetch_earthquake_data.py** → New file in `services/environment/`
2. **fetch_storm_data.py** → New file in `services/environment/`
3. **initialize_database_with_disasters.py** → Rename to `initialize_database.py`

---

## 🚀 Installation Steps

### **Step 1: Add Database Tables**

```bash
python initialize_database.py
```

**Expected output:**
```
Creating table: earthquakes
✓ Table earthquakes created successfully
Creating table: storms
✓ Table storms created successfully
```

---

### **Step 2: Test Earthquake Collector**

```bash
python services\environment\fetch_earthquake_data.py
```

**Expected output:**
```
Collecting earthquakes (magnitude 4.5+) from past 7 days

=== Earthquake Data Collection ===
Total earthquakes found: 23
Saved to database: 23

🌍 Recent Significant Earthquakes:
  🔴 M6.2 - 42 km NW of Hualien, Taiwan
  🟡 M5.8 - Kermadec Islands, New Zealand
  🟡 M5.3 - South of Fiji
  🟢 M4.9 - Near the coast of central Chile
  🟢 M4.7 - Southern Iran
```

**Legend:**
- 🔴 = Major (M6.0+)
- 🟡 = Strong (M5.0-5.9)
- 🟢 = Moderate (M4.5-4.9)

---

### **Step 3: Test Storm Collector**

```bash
python services\environment\fetch_storm_data.py
```

**Expected output:**
```
Collecting active storms and severe weather events

=== Storm Data Collection ===
Total active storms found: 3
Saved to database: 3

🌪️ Active Storms and Severe Weather:
  🌀 Hurricane Rafael
     Location: 24.50°, -85.20°
     Last updated: 2024-11-06T12:00:00Z
  🌀 Tropical Storm Sara
     Location: 15.80°, -80.50°
     Last updated: 2024-11-06T11:30:00Z
```

---

### **Step 4: View on Your Globe Map**

Your existing dashboard already has the 3D globe! The earthquake and storm data will automatically appear as points on the map.

**Run dashboard:**
```bash
streamlit run hermes_dashboard.py
```

Go to **🌦️ Environment** tab → You'll see the globe with:
- 🌦️ Weather (50 cities)
- 🌍 Earthquakes (red markers)
- 🌀 Storms (storm markers)

---

## 📊 Data Updates

**How often to collect:**

**Earthquakes:**
- Update: Every 1-2 hours
- Frequency: Earthquakes happen constantly, but significant ones (M4.5+) are rare
- Cost: FREE, no limits

**Storms:**
- Update: Every 2-4 hours  
- Frequency: Storms are tracked continuously
- Cost: FREE, no limits

**Both are FREE with no API limits!**

---

## 🎯 GitHub Actions Integration

Add to your `.github/workflows/collect_data.yml`:

```yaml
- name: Run Earthquake Collector
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    python services/environment/fetch_earthquake_data.py

- name: Run Storm Collector
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    python services/environment/fetch_storm_data.py
```

---

## 📈 Query Examples

**Recent major earthquakes:**
```sql
SELECT magnitude, place, timestamp, latitude, longitude, tsunami
FROM earthquakes
WHERE magnitude >= 5.0
ORDER BY timestamp DESC
LIMIT 10;
```

**Active storms near shipping routes:**
```sql
SELECT title, latitude, longitude, timestamp, status
FROM storms
WHERE status = 'active'
ORDER BY timestamp DESC;
```

**Earthquakes with tsunami warnings:**
```sql
SELECT magnitude, place, timestamp, url
FROM earthquakes
WHERE tsunami = TRUE
ORDER BY timestamp DESC;
```

---

## 🎯 Investment Use Cases

### **Earthquake Impact Analysis**
1. Check recent earthquakes > M5.5
2. Identify affected regions
3. Assess:
   - Infrastructure companies in region
   - Supply chain disruptions
   - Construction/materials opportunities
   - Insurance exposure

### **Storm Impact Analysis**
1. Track active hurricanes/typhoons
2. Identify paths and projected impacts
3. Assess:
   - Shipping delays (ports, routes)
   - Energy infrastructure risk
   - Agriculture damage potential
   - Insurance claims spikes

### **Combined Analysis**
- Cross-reference weather + earthquakes + storms
- Identify compound risks
- Regional stability assessment
- Supply chain vulnerability mapping

---

## 🐛 Troubleshooting

**No earthquakes showing:**
- Reduce min_magnitude to 4.0 to see more
- Increase days lookback to 14 or 30
- USGS API is very reliable, check internet connection

**No storms showing:**
- Storms are seasonal and variable
- Try increasing days to 60
- Check NASA EONET status

**Both collectors work offline (no API keys needed!)**

---

## 🚀 Next Steps

Once these work:
1. Add wildfire tracking (also NASA EONET)
2. Add volcanic activity
3. Set up alerts for significant events
4. Correlate with your stock portfolio exposure

---

**Install the files and test both collectors!** Show me those earthquakes and storms. 🌍🌪️
