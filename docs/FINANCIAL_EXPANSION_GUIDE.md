# 💰 Financial Data Expansion - Deployment Guide

## 🎯 What You're Adding

### **Stocks: 3 → 12 symbols**
**Current:** AAPL, GOOGL, MSFT
**New:**
- **Tech:** AAPL, GOOGL, MSFT (keep)
- **Finance:** JPM, GS, V
- **Energy:** XOM, CVX
- **Healthcare:** JNJ, UNH
- **Consumer:** WMT, PG

### **Commodities: NEW!**
- **Energy:** WTI (Crude Oil), NATURAL_GAS
- **Metals:** COPPER
- **Agriculture:** WHEAT, CORN

---

## 📦 Files to Install

Download these 3 files from outputs:

1. **fetch_market_data_12stocks.py** → Replace `services/markets/fetch_market_data.py`
2. **fetch_commodity_data.py** → New file in `services/markets/`
3. **initialize_database_with_commodities.py** → Rename to `initialize_database.py`

---

## 🚀 Installation Steps

### **Step 1: Update Database Schema**

Add the commodities table:

```bash
python initialize_database.py
```

**Expected output:**
```
Creating table: commodities
✓ Table commodities created successfully
```

---

### **Step 2: Replace Stock Collector**

1. Download `fetch_market_data_12stocks.py`
2. Rename to `fetch_market_data.py`
3. Replace in `services/markets/`

---

### **Step 3: Add Commodity Collector**

1. Download `fetch_commodity_data.py`
2. Put in `services/markets/`

---

### **Step 4: Test Locally**

**Test expanded stocks:**
```bash
python services/markets/fetch_market_data.py
```

**Expected output:**
```
Collecting data for 12 stocks: AAPL, GOOGL, MSFT, JPM, GS, V, XOM, CVX, JNJ, UNH, WMT, PG

=== Collection Complete ===
Total: 12
Successful: 12
Failed: 0

📈 Stock Prices:
  📉 AAPL: $270.37 (-2.39%)
  📉 GOOGL: $281.19 (-0.71%)
  ... (all 12 stocks)
```

**Test commodities:**
```bash
python services/markets/fetch_commodity_data.py
```

**Expected output:**
```
Collecting data for 5 commodities: WTI, NATURAL_GAS, COPPER, WHEAT, CORN

=== Collection Complete ===
Total: 5
Successful: 5
Failed: 0

💰 Commodity Prices:
  WTI: $67.89 USD (2024-11-06)
  NATURAL_GAS: $2.45 USD (2024-11-06)
  COPPER: $4.12 USD (2024-11-06)
  WHEAT: $5.67 USD (2024-11-06)
  CORN: $4.23 USD (2024-11-06)
```

---

### **Step 5: Update GitHub Actions Workflow**

Open `.github/workflows/data_collection.yml` and add the commodity collector:

```yaml
- name: Fetch Commodity Data
  run: python services/markets/fetch_commodity_data.py
  env:
    ALPHA_VANTAGE_KEY: ${{ secrets.ALPHA_VANTAGE_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Add it right after the stock collector step.

---

### **Step 6: Push to GitHub**

```bash
# Add all new/updated files
git add services/markets/fetch_market_data.py
git add services/markets/fetch_commodity_data.py
git add initialize_database.py
git add .github/workflows/data_collection.yml

# Commit
git commit -m "Expand financial data: 12 stocks + 5 commodities"

# Push
git push origin master
```

---

## ⏱️ Rate Limit Management

**Alpha Vantage Free Tier:**
- 5 calls per minute
- 500 calls per day

**Current collection time:**
- **12 stocks:** ~2.5 minutes (12 seconds between each)
- **5 commodities:** ~1 minute (12 seconds between each)
- **Total:** ~3.5 minutes per run

**Hourly automation:**
- 24 runs per day
- Total API calls: 17 × 24 = 408 calls/day ✅ Under limit!

---

## 📊 View Your Data

**Query stocks by sector:**
```sql
-- View all tech stocks
SELECT symbol, close, timestamp 
FROM stocks 
WHERE symbol IN ('AAPL', 'GOOGL', 'MSFT')
ORDER BY timestamp DESC;

-- View all commodities
SELECT symbol, price, timestamp 
FROM commodities 
ORDER BY timestamp DESC, symbol;
```

**Run local dashboard:**
```bash
streamlit run hermes_dashboard.py
```

The dashboard will automatically show all 12 stocks in charts!

---

## 🎯 What This Gives You

### **Sector Analysis**
- Track which sectors are performing best
- Identify rotation between sectors
- Correlation analysis across industries

### **Commodity Intelligence**
- Oil prices for energy sector impact
- Agriculture for food supply chains
- Metals for industrial/manufacturing indicators

### **Investment Insights**
- **Energy stocks + Oil prices** → Correlation analysis
- **Healthcare stocks** → Defensive plays
- **Finance stocks** → Economic health indicators
- **Consumer stocks** → Spending trends

---

## 🐛 Troubleshooting

**"Rate limit exceeded":**
- Wait 1 minute and try again
- GitHub Actions will handle this automatically

**"Failed to fetch commodity":**
- Check Alpha Vantage supports that commodity
- Verify API key is correct
- Some commodities may have limited free access

**Database error:**
- Make sure you ran `initialize_database.py` first
- Check DATABASE_URL is set correctly

---

## 📈 Next Expansions (Coming Soon)

Once this is stable:
- **Forex rates** (USD/EUR, USD/JPY, etc.)
- **Crypto prices** (BTC, ETH)
- **Economic indicators** (GDP, unemployment)
- **Sector ETFs** (XLF, XLE, XLV, XLK)

---

**Install the files and test!** Once both collectors work, push to GitHub. 🚀
