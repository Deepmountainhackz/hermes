# 💱 Add Forex (Currency Exchange Rates)

## 🎯 What You're Adding

**7 Major Currency Pairs (relative to USD):**
- EUR/USD - Euro
- GBP/USD - British Pound
- JPY/USD - Japanese Yen
- CHF/USD - Swiss Franc
- AUD/USD - Australian Dollar
- CAD/USD - Canadian Dollar
- CNY/USD - Chinese Yuan

---

## 📦 Files to Install

Download these 2 files:

1. **fetch_forex_data.py** → New file in `services/markets/`
2. **initialize_database_with_forex.py** → Rename to `initialize_database.py` (replace current one)

---

## 🚀 Quick Install

### **Step 1: Add Forex Table**

```bash
python initialize_database.py
```

**Expected output:**
```
Creating table: forex
✓ Table forex created successfully
```

---

### **Step 2: Add Forex Collector**

1. Download `fetch_forex_data.py`
2. Put it in `services/markets/`

---

### **Step 3: Test It**

```bash
python services\markets\fetch_forex_data.py
```

**Expected output:**
```
Collecting rates for 7 currency pairs

=== Collection Complete ===
Total: 7
Successful: 7
Failed: 0

💱 Exchange Rates (to USD):
  EUR/USD: 1.0542
  GBP/USD: 1.2673
  JPY/USD: 0.0066
  CHF/USD: 1.1234
  AUD/USD: 0.6512
  CAD/USD: 0.7189
  CNY/USD: 0.1389
```

**Takes ~1.5 minutes** (12 second delay between each)

---

### **Step 4: Update GitHub Actions**

Open `.github/workflows/collect_data.yml` and add after commodity collector:

```yaml
- name: Run Forex Collector
  env:
    ALPHA_VANTAGE_KEY: ${{ secrets.ALPHA_VANTAGE_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    python services/markets/fetch_forex_data.py
```

---

### **Step 5: Push to GitHub**

```bash
git add services/markets/fetch_forex_data.py
git add initialize_database.py
git add .github/workflows/collect_data.yml
git commit -m "Add forex currency exchange rates"
git push origin master
```

---

## 📊 What This Gives You

### **Investment Intelligence:**
- **Currency exposure analysis** - How forex affects your international holdings
- **Hedging opportunities** - When to hedge currency risk
- **Economic indicators** - Strong/weak currencies signal economic health
- **Correlation analysis** - Currency movements vs stock sectors

### **Example Insights:**
- Strong USD → Foreign stocks underperform in USD terms
- Weak EUR → European exports become competitive
- Strong JPY → Japanese exporters struggle
- Commodity currencies (AUD, CAD) → Track with commodity prices

---

## 🎯 Rate Limits

**Current API usage per hour:**
- 12 stocks = 12 calls
- 5 commodities = 5 calls
- 7 forex pairs = 7 calls
- **Total: 24 calls/hour**

**Daily: 24 × 24 = 576 calls**

**Alpha Vantage free tier: 500 calls/day** ⚠️

**Solution:** You're slightly over. Options:
1. Reduce hourly collections to every 2 hours
2. Upgrade Alpha Vantage plan ($50/month for 75 calls/min)
3. Remove some less important pairs

For now, you might hit the limit late in the day. GitHub Actions will just fail gracefully and retry next hour.

---

## 🐛 Troubleshooting

**"Rate limit exceeded":**
- You've hit your 500 calls/day limit
- Wait until tomorrow (resets at midnight UTC)
- Or upgrade Alpha Vantage

**"Failed to fetch forex":**
- Check API key is correct
- Verify internet connection
- Check Alpha Vantage status

---

**Test the forex collector and show me the output!** 💱
