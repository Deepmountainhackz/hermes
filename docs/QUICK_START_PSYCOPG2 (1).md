# 💰 Financial Expansion - Quick Start (psycopg2)

## 📦 Download These 3 Files:

1. **initialize_database_psycopg2.py** → Rename to `initialize_database.py`
2. **fetch_market_data_psycopg2.py** → Rename to `fetch_market_data.py` in `services/markets/`
3. **fetch_commodity_data_psycopg2.py** → Rename to `fetch_commodity_data.py` in `services/markets/`

---

## 🚀 Installation (3 Steps)

### **Step 1: Update Database**

```bash
python initialize_database.py
```

**You should see:**
```
Creating table: commodities
✓ Table commodities created successfully
```

---

### **Step 2: Test Stock Collector (12 stocks)**

```bash
python services\markets\fetch_market_data.py
```

**Expected: 12 stocks collected**
- Tech: AAPL, GOOGL, MSFT
- Finance: JPM, GS, V
- Energy: XOM, CVX
- Healthcare: JNJ, UNH
- Consumer: WMT, PG

**Takes ~2.5 minutes** (12 second delay between each)

---

### **Step 3: Test Commodity Collector**

```bash
python services\markets\fetch_commodity_data.py
```

**Expected: 5 commodities collected**
- WTI (Crude Oil)
- NATURAL_GAS
- COPPER
- WHEAT
- CORN

**Takes ~1 minute** (12 second delay between each)

---

## ✅ Success Checklist

- [ ] Commodities table created in database
- [ ] 12 stocks collected successfully
- [ ] 5 commodities collected successfully
- [ ] All data visible in Railway database

---

## 🎯 Once Both Work:

Update your GitHub Actions workflow to include commodity collection, then push everything!

**Show me the output when you run each collector!** 🚀
