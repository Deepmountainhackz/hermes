# 🚀 PostgreSQL Collectors - Complete Deployment Guide

## ✅ All 6 Collectors Ready!

I've created PostgreSQL versions of all your collectors:

1. ✅ **ISS Position** - `fetch_iss_data.py`
2. ✅ **Near-Earth Objects** - `fetch_neo_data.py`
3. ✅ **Solar Flares** - `fetch_solar_data.py`
4. ✅ **Weather** - `fetch_weather_data.py`
5. ✅ **News** - `fetch_news_data.py`
6. ✅ **Countries** - `fetch_country_data.py`

---

## 📦 Step 1: Replace Your Collectors

### **Backup Your Old Collectors First**

```bash
# Create a backup folder
mkdir services_backup

# Backup current collectors
copy services\space\fetch_iss_data.py services_backup\
copy services\space\fetch_neo_data.py services_backup\
copy services\space\fetch_solar_data.py services_backup\
copy services\environment\fetch_weather_data.py services_backup\
copy services\social\fetch_news_data.py services_backup\
copy services\geography\fetch_country_data.py services_backup\
```

### **Install New Collectors**

Download all 6 files from the outputs folder and place them:

- `fetch_iss_data.py` → `services/space/`
- `fetch_neo_data.py` → `services/space/`
- `fetch_solar_data.py` → `services/space/`
- `fetch_weather_data.py` → `services/environment/`
- `fetch_news_data.py` → `services/social/`
- `fetch_country_data.py` → `services/geography/`

---

## 🧪 Step 2: Test Each Collector Locally

Test them ONE BY ONE to make sure they work:

### **1. ISS Position**
```bash
python services/space/fetch_iss_data.py
```
**Expected output:**
```
✓ Fetched ISS position
✓ Saved ISS position to database
=== ISS Position Data ===
Latitude: -50.6271
Longitude: 84.8139
```

### **2. NEO (Near-Earth Objects)**
```bash
python services/space/fetch_neo_data.py
```
**Expected output:**
```
✓ Fetched NEO data
✓ Saved X NEO records to database
=== NEO Data Collection ===
Total NEOs: X
```

### **3. Solar Flares**
```bash
python services/space/fetch_solar_data.py
```
**Expected output:**
```
✓ Saved X solar flare records to database
=== Solar Flare Data Collection ===
Total flares found: X
```

### **4. Weather**
```bash
python services/environment/fetch_weather_data.py
```
**Expected output:**
```
✓ Fetched weather for London
✓ Fetched weather for New York
...
=== Weather Data Collection ===
Total cities: 50
Successful: 50
```

**⚠️ This one takes ~1 minute** (50 cities with 1 second delay between each)

### **5. News**
```bash
python services/social/fetch_news_data.py
```
**Expected output:**
```
✓ Fetched X business articles
✓ Fetched X technology articles
✓ Saved X news articles to database
```

### **6. Countries**
```bash
python services/geography/fetch_country_data.py
```
**Expected output:**
```
✓ Fetched data for 250 countries
✓ Saved X countries to database
```

---

## ✅ Step 3: Check Your Database

Verify data is actually in PostgreSQL:

Go to Railway → Your Database → Data tab

You should see data in all tables:
- `iss_positions` - Latest ISS location
- `near_earth_objects` - Asteroid data
- `solar_flares` - Solar activity
- `weather` - 50 cities weather
- `news` - Latest articles
- `countries` - Country profiles

---

## 🚀 Step 4: Push to GitHub

Once ALL 6 collectors work locally:

```bash
# Add all updated collectors
git add services/

# Add the database.py module if not already added
git add database.py

# Commit
git commit -m "Migrate all collectors to PostgreSQL"

# Push
git push origin master
```

---

## 🤖 Step 5: GitHub Actions Will Run Automatically

After you push:
1. GitHub Actions detects the changes
2. Runs all collectors hourly
3. Saves to Railway PostgreSQL
4. Your dashboard shows fresh data!

---

## 🎯 Step 6: Update Streamlit Secrets

**Important:** Add DATABASE_URL to Streamlit too!

1. Go to: https://share.streamlit.io/
2. Find your app → Settings → Secrets
3. Make sure you have:
```toml
DATABASE_URL = "your_railway_public_url"
```

4. Save and restart the app

---

## 📊 Step 7: Update Your Dashboard

Your dashboard (`hermes_dashboard.py`) also needs to use PostgreSQL instead of SQLite.

**Key changes needed:**
```python
# OLD (SQLite):
import sqlite3
conn = sqlite3.connect('hermes.db')

# NEW (PostgreSQL):
from database import get_db_connection

with get_db_connection() as conn:
    # your queries
```

**Want me to update your dashboard too?** 
Upload `hermes_dashboard.py` and I'll create the PostgreSQL version!

---

## 🐛 Troubleshooting

### **"DATABASE_URL not set"**
- Check your `.env` file has the PUBLIC url from Railway
- Make sure it starts with `postgresql://` not `postgres://`

### **"Module 'database' not found"**
- Make sure `database.py` is in your project root
- Make sure it has the imports at the top

### **"Connection failed"**
- Verify Railway database is running
- Check you're using the PUBLIC url, not internal
- Test connection: `python initialize_database.py`

### **"Table doesn't exist"**
- Run: `python initialize_database.py`
- Check Railway → Database → Data tab

---

## ✅ Success Checklist

- [ ] All 6 collectors work locally
- [ ] Data appears in Railway database
- [ ] Pushed to GitHub
- [ ] GitHub Actions running successfully
- [ ] Dashboard updated to use PostgreSQL
- [ ] Streamlit Cloud shows fresh data

---

## 🎯 What Happens Next

Once everything is deployed:
1. **GitHub Actions** runs collectors every hour
2. **Railway** stores all the data
3. **Streamlit** displays it on your dashboard
4. **You** just check the dashboard when making decisions!

**No more manual data collection!** 🎉

---

**Ready to test?** Start with collector #1 (ISS) and work through the list!
