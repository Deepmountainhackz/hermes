# 🔧 Fix: Python 3.13 Compatibility Issue

## ❌ Problem

Streamlit Cloud is using **Python 3.13.9**, but `psycopg2-binary==2.9.9` doesn't support it yet.

Error: `pg_config executable not found`

---

## ✅ Solution: Migrate to psycopg (Version 3)

`psycopg` (version 3) is the modern replacement for `psycopg2` and fully supports Python 3.13.

---

## 📦 Files to Replace

Download these 3 files from outputs folder:

1. **requirements_psycopg3.txt** → Rename to `requirements.txt`
2. **database_psycopg3.py** → Rename to `database.py`
3. **initialize_database_psycopg3.py** → Rename to `initialize_database.py`

---

## 🚀 Deployment Steps

### **Step 1: Replace Files Locally**

```bash
# In your Hermes project folder
# Replace these 3 files with the new versions
```

### **Step 2: Test Locally**

```bash
# Test one collector
python services/markets/fetch_market_data.py

# Should still work!
```

### **Step 3: Push to GitHub**

```bash
git add requirements.txt database.py initialize_database.py
git commit -m "Migrate to psycopg3 for Python 3.13 compatibility"
git push origin master
```

### **Step 4: Reboot Streamlit**

1. Go to https://share.streamlit.io/
2. Find your Hermes app
3. Click **⋮** (three dots)
4. Click **Reboot app**

---

## ⚙️ What Changed?

**requirements.txt:**
```diff
- psycopg2-binary==2.9.9
+ psycopg[binary]==3.1.18
```

**database.py:**
```diff
- import psycopg2
- from psycopg2.extras import RealDictCursor
+ import psycopg
+ from psycopg.rows import dict_row

- conn = psycopg2.connect(db_url)
+ conn = psycopg.connect(db_url, row_factory=dict_row, autocommit=True)
```

**initialize_database.py:**
```diff
- import psycopg2
+ import psycopg

- conn = psycopg2.connect(db_url)
+ conn = psycopg.connect(db_url, autocommit=True)
```

---

## 🎯 Expected Result

After deployment:
- ✅ Streamlit Cloud installs psycopg successfully
- ✅ Dashboard loads without errors
- ✅ All collectors continue working
- ✅ GitHub Actions runs hourly
- ✅ Data accumulates in PostgreSQL

---

## 📊 About Data

Your PostgreSQL database is **brand new**, so:
- Limited historical data (only from local tests)
- GitHub Actions will populate more data hourly
- After a few days, you'll have rich historical data

**Don't worry** - the system is working, it just needs time to collect data!

---

## 🐛 Troubleshooting

**If collectors fail after update:**
```bash
# Reinstall locally
pip uninstall psycopg2-binary
pip install psycopg[binary]==3.1.18

# Test again
python services/markets/fetch_market_data.py
```

**If Streamlit still fails:**
- Check Streamlit Cloud logs
- Verify DATABASE_URL is in secrets
- Try manual reboot again

---

**Replace the 3 files and push to GitHub!** 🚀
