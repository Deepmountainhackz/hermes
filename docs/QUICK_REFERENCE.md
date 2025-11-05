# 🚀 Hermes Quick Reference

## One-Command Cleanup

```bash
# Option 1: Python script (automatic)
python reorganize_hermes.py

# Option 2: Bash script (automatic)
bash cleanup.sh

# Done! Your project is now organized! 🎉
```

---

## New Project Structure

```
hermes/
├── 🎯 hermes_dashboard.py          # Main app - run this
├── ⚙️  config_cities.py             # City coordinates
├── 🚀 run_hermes.py                # Alternative runner
├── 💾 hermes.db                    # Database
├── 🔐 .env                         # API keys
├── 📋 requirements.txt             # Dependencies
├── 📖 README.md                    # Start here
│
├── 🔌 services/                    # Data collectors
│   ├── markets/                   # Stocks
│   ├── space/                     # ISS, NEO, solar
│   ├── geography/                 # Countries
│   ├── environment/               # Weather
│   └── social/                    # News
│
├── 📚 docs/                        # All documentation
├── 🔧 scripts/                     # Utilities
├── 🧪 tests/                       # Tests
└── 💾 backups/                     # Old files
```

---

## Common Tasks

### Run the Dashboard
```bash
streamlit run hermes_dashboard.py
```

### Collect Data
```bash
python scripts/collect_weather_50cities.py
python scripts/collect_country_data.py
```

### Query Database
```bash
python scripts/query_hermes.py
```

### Run Tests
```bash
python -m pytest tests/
```

### Check Schema
```bash
python scripts/check_schema.py
```

---

## Where to Find Things

| What                  | Where                           |
|-----------------------|---------------------------------|
| Main dashboard        | `hermes_dashboard.py`          |
| City config           | `config_cities.py`             |
| Documentation         | `docs/`                        |
| Utility scripts       | `scripts/`                     |
| Tests                 | `tests/`                       |
| Old backups           | `backups/`                     |
| Data collectors       | `services/*/`                  |
| SQL queries guide     | `docs/SQL_QUERIES.md`          |
| Setup help            | `docs/SETUP_FIX.md`            |
| Contributing guide    | `docs/CONTRIBUTING.md`         |
| Roadmap               | `docs/HERMES_ROADMAP.md`       |

---

## Before vs After

### Before: 30+ files in root 😵
```
hermes/
├── [50+ scattered files]
└── [chaos everywhere]
```

### After: 8 files + 5 folders ✨
```
hermes/
├── hermes_dashboard.py
├── config_cities.py
├── run_hermes.py
├── services/
├── docs/
├── scripts/
├── tests/
└── backups/
```

---

## Benefits

✅ **73% fewer files in root**  
✅ **Easy to navigate**  
✅ **Professional structure**  
✅ **Nothing breaks**  
✅ **Better collaboration**  

---

## VS Code Tips

### Collapse unused folders:
- Click arrow next to `docs/` to collapse
- Click arrow next to `backups/` to collapse
- Click arrow next to `tests/` to collapse (when not testing)

### Keep expanded:
- `services/` (main work area)
- Root files (dashboard, config)

---

## Quick Commands

```bash
# Start dashboard
streamlit run hermes_dashboard.py

# Collect all data
python run_hermes.py

# Check database
python scripts/check_schema.py

# Run all tests
python -m pytest tests/ -v

# Read docs
cat docs/README.md

# View SQL reference
cat docs/SQL_QUERIES.md
```

---

## File Counts

| Location      | Before | After |
|---------------|--------|-------|
| Root files    | 30+    | 8     |
| Organized     | 0      | 5 dirs|
| Total clutter | 100%   | 10%   |

---

## Status After Cleanup

🎉 **Project is now:**
- ✅ Organized
- ✅ Professional  
- ✅ Maintainable
- ✅ Scalable
- ✅ Collaborative-ready

---

**Save this file for quick reference!** 📌
