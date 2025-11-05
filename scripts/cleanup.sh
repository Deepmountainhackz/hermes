#!/bin/bash

# Hermes Project Cleanup Script
# ==============================
# Organizes your messy project structure into a clean layout

set -e  # Exit on error

echo "🧹 Hermes Project Cleanup Starting..."
echo "======================================"
echo ""

# Create directories
echo "📁 Creating directory structure..."
mkdir -p docs
mkdir -p scripts  
mkdir -p tests
mkdir -p backups
echo "   ✅ Created: docs/, scripts/, tests/, backups/"
echo ""

# Move documentation files
echo "📝 Organizing documentation..."
if [ -f "CLEANUP_SUMMARY.md" ]; then mv CLEANUP_SUMMARY.md docs/; echo "   Moved CLEANUP_SUMMARY.md"; fi
if [ -f "COMPARISON_METRICS.md" ]; then mv COMPARISON_METRICS.md docs/; echo "   Moved COMPARISON_METRICS.md"; fi
if [ -f "MIGRATION_GUIDE.md" ]; then mv MIGRATION_GUIDE.md docs/; echo "   Moved MIGRATION_GUIDE.md"; fi
if [ -f "ERROR_HANDLING_GUIDE.md" ]; then mv ERROR_HANDLING_GUIDE.md docs/; echo "   Moved ERROR_HANDLING_GUIDE.md"; fi
if [ -f "CONTRIBUTING.md" ]; then mv CONTRIBUTING.md docs/; echo "   Moved CONTRIBUTING.md"; fi
if [ -f "SETUP_FIX.md" ]; then mv SETUP_FIX.md docs/; echo "   Moved SETUP_FIX.md"; fi
if [ -f "SQL_QUERIES.md" ]; then mv SQL_QUERIES.md docs/; echo "   Moved SQL_QUERIES.md"; fi
if [ -f "CHANGELOG.md" ]; then mv CHANGELOG.md docs/; echo "   Moved CHANGELOG.md"; fi
if [ -f "HERMES_ROADMAP.md" ]; then mv HERMES_ROADMAP.md docs/; echo "   Moved HERMES_ROADMAP.md"; fi
if [ -f "hermes_project_plan.md" ]; then mv hermes_project_plan.md docs/; echo "   Moved hermes_project_plan.md"; fi
if [ -f "CLEANUP_CHECKLIST.md" ]; then mv CLEANUP_CHECKLIST.md docs/; echo "   Moved CLEANUP_CHECKLIST.md"; fi
echo ""

# Move utility scripts
echo "🔧 Organizing scripts..."
if [ -f "populate_database.py" ]; then mv populate_database.py scripts/; echo "   Moved populate_database.py"; fi
if [ -f "query_hermes.py" ]; then mv query_hermes.py scripts/; echo "   Moved query_hermes.py"; fi
if [ -f "check_schema.py" ]; then mv check_schema.py scripts/; echo "   Moved check_schema.py"; fi
if [ -f "collect_country_data.py" ]; then mv collect_country_data.py scripts/; echo "   Moved collect_country_data.py"; fi
if [ -f "collect_weather_50cities.py" ]; then mv collect_weather_50cities.py scripts/; echo "   Moved collect_weather_50cities.py"; fi
if [ -f "test_all_collectors.py" ]; then mv test_all_collectors.py scripts/; echo "   Moved test_all_collectors.py"; fi
echo ""

# Move test files
echo "🧪 Organizing tests..."
if [ -f "test_country.py" ]; then mv test_country.py tests/; echo "   Moved test_country.py"; fi
if [ -f "test_database.py" ]; then mv test_database.py tests/; echo "   Moved test_database.py"; fi
echo ""

# Move backup files
echo "💾 Organizing backups..."
if [ -f "hermes_dashboard_backup.py" ]; then mv hermes_dashboard_backup.py backups/; echo "   Moved hermes_dashboard_backup.py"; fi
if [ -f "hermes_scheduler.py" ]; then mv hermes_scheduler.py backups/; echo "   Moved hermes_scheduler.py"; fi
echo ""

# Create README files
echo "📝 Creating README files..."

# docs/README.md
cat > docs/README.md << 'EOF'
# Hermes Documentation

All project documentation in one place.

## Files

- **CLEANUP_SUMMARY.md** - Dashboard cleanup details
- **COMPARISON_METRICS.md** - Before/after metrics  
- **MIGRATION_GUIDE.md** - Migration instructions
- **ERROR_HANDLING_GUIDE.md** - Error handling guide
- **CONTRIBUTING.md** - How to contribute
- **SETUP_FIX.md** - Setup troubleshooting
- **SQL_QUERIES.md** - SQL reference
- **CHANGELOG.md** - Version history
- **HERMES_ROADMAP.md** - Future plans

Back to [main README](../README.md)
EOF
echo "   Created docs/README.md"

# scripts/README.md
cat > scripts/README.md << 'EOF'
# Hermes Utility Scripts

Database management and data collection utilities.

## Scripts

- **populate_database.py** - Populate database
- **query_hermes.py** - Query database
- **check_schema.py** - Verify schema
- **collect_country_data.py** - Country data collector
- **collect_weather_50cities.py** - Weather collector
- **test_all_collectors.py** - Test collectors

## Usage

```bash
python scripts/populate_database.py
python scripts/query_hermes.py
```
EOF
echo "   Created scripts/README.md"

# tests/README.md
cat > tests/README.md << 'EOF'
# Hermes Tests

Test suite for the platform.

## Running Tests

```bash
python -m pytest tests/
python -m pytest tests/test_country.py
```

## Files

- **test_country.py** - Country tests
- **test_database.py** - Database tests
EOF
echo "   Created tests/README.md"

echo ""
echo "======================================"
echo "✨ Cleanup Complete!"
echo ""
echo "Your project structure:"
echo "  hermes/"
echo "  ├── hermes_dashboard.py    (main app)"
echo "  ├── config_cities.py       (config)"
echo "  ├── run_hermes.py          (runner)"
echo "  ├── services/              (collectors)"
echo "  ├── docs/                  (all docs)"
echo "  ├── scripts/               (utilities)"
echo "  ├── tests/                 (tests)"
echo "  └── backups/               (old files)"
echo ""
echo "🎉 Much cleaner! Ready to code!"
