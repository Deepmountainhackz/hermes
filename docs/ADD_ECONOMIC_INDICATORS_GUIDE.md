# 📊 Add Economic Indicators - The Macro Dashboard

## 🎯 What You're Building

**Track key economic indicators for 5 major economies:**

### **United States**
- GDP Growth Rate
- Unemployment Rate  
- Inflation (CPI)
- Federal Funds Rate

### **Eurozone**
- GDP Growth
- Unemployment
- Inflation (HICP)

### **China**
- GDP Growth
- Unemployment

### **Japan**
- GDP Growth
- Unemployment
- Inflation (CPI)

### **United Kingdom**
- GDP Growth
- Unemployment
- Inflation (CPI)

**Total: 17 economic indicators across the world's major economies**

---

## 🔑 Step 1: Get FRED API Key (FREE)

**1. Go to:** https://fred.stlouisfed.org/docs/api/api_key.html

**2. Click "Request API Key"**

**3. Sign up** (takes 1 minute, free forever)

**4. Copy your API key**

**5. Add to your `.env` file:**
```
FRED_API_KEY=your_key_here_32_character_string
```

**Note:** FRED = Federal Reserve Economic Data (St. Louis Fed)

---

## 📦 Step 2: Install Files

Download these 2 files:

1. **fetch_economic_data.py** → New file in `services/markets/`
2. **initialize_database_with_economic.py** → Rename to `initialize_database.py`

---

## 🚀 Step 3: Setup & Test

### **Add the table:**
```bash
python initialize_database.py
```

**Expected:**
```
Creating table: economic_indicators
✓ Table economic_indicators created successfully
```

---

### **Test the collector:**
```bash
python services\markets\fetch_economic_data.py
```

**Expected output:**
```
=== Collection Complete ===
Total indicators: 17
Successful: 15-17
Failed: 0-2

📊 Latest Economic Indicators:

  United States:
    GDP: $28,781B
    Unemployment: 4.1%
    Inflation: 315.2
    Interest Rate: 4.75%

  Eurozone:
    GDP: €15,234B
    Unemployment: 6.3%
    Inflation: 112.5

  China:
    GDP: $18,532B
    Unemployment: 5.0%

  Japan:
    GDP: $4,234B
    Unemployment: 2.5%
    Inflation: 108.2

  United Kingdom:
    GDP: $3,495B
    Unemployment: 4.2%
    Inflation: 132.4
```

---

## 💡 Investment Intelligence Value

### **This Changes Everything**

**Cross-Country Analysis:**
- Compare US vs EU growth rates
- Spot economic divergences
- Predict currency movements
- Identify sector opportunities

**Example Insights:**

**1. Growth Divergence**
```
US GDP: +3.2% YoY
EU GDP: +0.5% YoY
China GDP: +4.8% YoY
→ Bullish USD, allocate to US equities
```

**2. Unemployment Trends**
```
US Unemployment rising: 3.8% → 4.1%
→ Fed may cut rates, bonds become attractive
```

**3. Inflation Watch**
```
US Inflation: 3.2%
EU Inflation: 2.1%
→ Fed stays hawkish longer, EUR/USD weakness
```

**4. Interest Rate Differential**
```
US Rates: 4.75%
EU Rates: 3.50%
→ Capital flows to USD, carry trade opportunities
```

---

## 📊 Key Queries

### **Economic Dashboard:**
```sql
SELECT country, indicator_type, value, unit, timestamp
FROM economic_indicators
ORDER BY country, indicator_type;
```

### **Track Changes Over Time:**
```sql
SELECT country, indicator_type, value, timestamp
FROM economic_indicators
WHERE indicator_type = 'Unemployment'
ORDER BY country, timestamp DESC;
```

### **Compare Regions:**
```sql
SELECT country, 
       MAX(CASE WHEN indicator_type = 'GDP' THEN value END) as gdp,
       MAX(CASE WHEN indicator_type = 'Unemployment' THEN value END) as unemployment,
       MAX(CASE WHEN indicator_type = 'Inflation' THEN value END) as inflation
FROM economic_indicators
WHERE timestamp = (SELECT MAX(timestamp) FROM economic_indicators)
GROUP BY country;
```

---

## 🎯 Collection Frequency

**How often to update:**
- **GDP:** Updated quarterly → Collect weekly
- **Unemployment:** Updated monthly → Collect weekly
- **Inflation:** Updated monthly → Collect weekly
- **Interest Rates:** Updated as changed → Collect daily

**Recommendation:** Run daily or weekly. Economic data doesn't change often.

---

## 🚀 GitHub Actions

Add to `.github/workflows/collect_data.yml`:

```yaml
- name: Run Economic Indicators Collector
  env:
    FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    python services/markets/fetch_economic_data.py
```

**Don't forget:** Add `FRED_API_KEY` to GitHub Secrets!

---

## 📈 Investment Strategies You Can Build

### **1. Macro Rotation Strategy**
- Strong GDP → Cyclical stocks (XLF, XLE)
- Weak GDP → Defensive stocks (XLP, XLV)
- Rising unemployment → Bonds
- Falling unemployment → Equities

### **2. Currency Trading**
- Interest rate differential → Forex positions
- Growth divergence → Currency pairs
- Inflation divergence → FX hedges

### **3. Geographic Allocation**
- Compare regional growth
- Allocate capital to strongest economies
- Hedge exposure to weak regions

### **4. Recession Signals**
- Inverted yield curves + rising unemployment
- GDP deceleration + falling confidence
- Early warning system for downturns

---

## 🎯 What You Now Have

**Complete Investment Intelligence Platform:**

**Financial Markets:**
- 12 stocks across 5 sectors
- 5 commodities
- 6 forex pairs
- **17 economic indicators (NEW!)**

**Global Monitoring:**
- Earthquakes
- Weather (50 cities)
- Space events
- News feeds

**This is professional-grade macro analysis infrastructure.** 🏆

---

## 🐛 Troubleshooting

**"FRED_API_KEY not found":**
- Make sure it's in your `.env` file
- Restart terminal after adding it
- Check for typos

**Some indicators failing:**
- FRED series IDs occasionally change
- Some data may have delays
- 15-17 out of 17 working is normal

**Rate limits:**
- FRED free tier: 120 requests/minute
- You're using ~17 requests per run
- No problem at all!

---

**Get your FRED API key and test it!** This is the big one. 📊
