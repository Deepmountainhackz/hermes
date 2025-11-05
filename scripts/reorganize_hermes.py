#!/usr/bin/env python3
"""
Hermes Project Reorganization Script
=====================================
This script will reorganize your messy project structure into a clean,
professional layout following Python best practices.

BEFORE (Clusterfuck):
hermes/
├── [50+ files scattered everywhere]
└── [chaos and confusion]

AFTER (Clean):
hermes/
├── hermes_dashboard.py      # Main dashboard (root for easy access)
├── config_cities.py          # Config (root for imports)
├── run_hermes.py            # Main runner (root for easy access)
├── hermes.db                # Database (root)
├── .env                     # Environment (root)
├── .gitignore              # Git config (root)
├── requirements.txt        # Dependencies (root)
├── README.md              # Main readme (root)
├── services/              # Data collectors (already organized)
├── docs/                  # All documentation
├── scripts/               # Utility scripts
├── tests/                 # Test files
└── backups/               # Old backup files

Run this script to auto-organize everything!
"""

import os
import shutil
from pathlib import Path

class ProjectOrganizer:
    def __init__(self, project_root="."):
        self.root = Path(project_root)
        self.changes = []
        
    def create_directories(self):
        """Create the new directory structure"""
        dirs = ['docs', 'scripts', 'tests', 'backups']
        for dir_name in dirs:
            dir_path = self.root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.changes.append(f"✅ Created directory: {dir_name}/")
    
    def organize_docs(self):
        """Move all markdown documentation to docs/"""
        doc_files = [
            'CLEANUP_SUMMARY.md',
            'COMPARISON_METRICS.md',
            'MIGRATION_GUIDE.md',
            'ERROR_HANDLING_GUIDE.md',
            'CONTRIBUTING.md',
            'SETUP_FIX.md',
            'SQL_QUERIES.md',
            'CHANGELOG.md',
            'HERMES_ROADMAP.md',
            'hermes_project_plan.md',
            'CLEANUP_CHECKLIST.md'
        ]
        
        for doc in doc_files:
            src = self.root / doc
            if src.exists():
                dst = self.root / 'docs' / doc
                shutil.move(str(src), str(dst))
                self.changes.append(f"📄 Moved {doc} → docs/")
    
    def organize_scripts(self):
        """Move utility scripts to scripts/"""
        script_files = [
            'populate_database.py',
            'query_hermes.py',
            'check_schema.py',
            'collect_country_data.py',
            'collect_weather_50cities.py',
            'test_all_collectors.py'
        ]
        
        for script in script_files:
            src = self.root / script
            if src.exists():
                dst = self.root / 'scripts' / script
                shutil.move(str(src), str(dst))
                self.changes.append(f"🔧 Moved {script} → scripts/")
    
    def organize_tests(self):
        """Move test files to tests/"""
        test_files = [
            'test_country.py',
            'test_database.py',
        ]
        
        for test in test_files:
            src = self.root / test
            if src.exists():
                dst = self.root / 'tests' / test
                shutil.move(str(src), str(dst))
                self.changes.append(f"🧪 Moved {test} → tests/")
    
    def organize_backups(self):
        """Move backup files to backups/"""
        backup_files = [
            'hermes_dashboard_backup.py',
            'hermes_scheduler.py'  # If this is old/unused
        ]
        
        for backup in backup_files:
            src = self.root / backup
            if src.exists():
                dst = self.root / 'backups' / backup
                shutil.move(str(src), str(dst))
                self.changes.append(f"💾 Moved {backup} → backups/")
    
    def create_docs_readme(self):
        """Create a README in docs/ to explain the documentation"""
        readme_content = """# Hermes Documentation

This directory contains all project documentation.

## Files

- **CLEANUP_SUMMARY.md** - Dashboard cleanup details
- **COMPARISON_METRICS.md** - Before/after metrics
- **MIGRATION_GUIDE.md** - How to migrate to clean dashboard
- **ERROR_HANDLING_GUIDE.md** - Error handling best practices
- **CONTRIBUTING.md** - Contribution guidelines
- **SETUP_FIX.md** - Setup troubleshooting
- **SQL_QUERIES.md** - Database query reference
- **CHANGELOG.md** - Project changelog
- **HERMES_ROADMAP.md** - Future plans and roadmap
- **hermes_project_plan.md** - Original project plan

## Quick Links

- Main README: `../README.md`
- Setup: See main README
- API Docs: (Coming soon)
"""
        
        readme_path = self.root / 'docs' / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        self.changes.append("📝 Created docs/README.md")
    
    def create_scripts_readme(self):
        """Create a README in scripts/ to explain utilities"""
        readme_content = """# Hermes Utility Scripts

This directory contains utility scripts for database management and data collection.

## Scripts

### Database Management
- **populate_database.py** - Populate database with initial data
- **query_hermes.py** - Query the Hermes database
- **check_schema.py** - Verify database schema

### Data Collection
- **collect_country_data.py** - Fetch country data
- **collect_weather_50cities.py** - Fetch weather for 50 cities
- **test_all_collectors.py** - Test all data collectors

## Usage

Most scripts can be run directly:

```bash
python scripts/populate_database.py
python scripts/query_hermes.py
```

See individual scripts for specific usage.
"""
        
        readme_path = self.root / 'scripts' / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        self.changes.append("📝 Created scripts/README.md")
    
    def create_tests_readme(self):
        """Create a README in tests/"""
        readme_content = """# Hermes Tests

Test suite for the Hermes Intelligence Platform.

## Test Files

- **test_country.py** - Country data tests
- **test_database.py** - Database tests

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_country.py

# With coverage
python -m pytest tests/ --cov=services
```

## Writing Tests

Follow the existing patterns. Each test file should:
1. Import necessary modules
2. Set up test fixtures
3. Write clear, focused test cases
4. Clean up after tests
"""
        
        readme_path = self.root / 'tests' / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        self.changes.append("📝 Created tests/README.md")
    
    def update_main_readme(self):
        """Update the main README with new structure"""
        readme_content = """# 🌐 Hermes Intelligence Platform

Multi-layer intelligence platform collecting and analyzing data from multiple sources.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env  # Then add your API keys

# 3. Run the dashboard
streamlit run hermes_dashboard.py

# Or use the runner script
python run_hermes.py
```

## 📁 Project Structure

```
hermes/
├── hermes_dashboard.py      # Main Streamlit dashboard
├── config_cities.py          # City configuration
├── run_hermes.py            # Main runner script
├── hermes.db                # SQLite database
├── services/                # Data collection services
│   ├── markets/            # Stock market data
│   ├── space/              # Space/ISS data
│   ├── geography/          # Country data
│   ├── environment/        # Weather data
│   └── social/             # News data
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── docs/                    # Documentation
└── backups/                # Backup files
```

## 📊 Features

- 📈 **Markets** - Real-time stock data
- 🛰️ **Space** - ISS tracking, NEO monitoring, solar flares
- 🌍 **Geography** - Country profiles and analytics
- 🌦️ **Environment** - Global weather with 3D globe
- 📰 **News** - Latest headlines from multiple sources

## 📚 Documentation

See the [`docs/`](docs/) directory for detailed documentation:

- [Migration Guide](docs/MIGRATION_GUIDE.md) - Upgrade to clean dashboard
- [Error Handling Guide](docs/ERROR_HANDLING_GUIDE.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Roadmap](docs/HERMES_ROADMAP.md)

## 🛠️ Development

```bash
# Run tests
python -m pytest tests/

# Run specific collector
python scripts/collect_weather_50cities.py

# Check database schema
python scripts/check_schema.py
```

## 📋 Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- H3-py
- API keys (see `.env.example`)

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - See LICENSE file for details.

---

Built with ❤️ for intelligence gathering and analysis
"""
        
        readme_path = self.root / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        self.changes.append("📝 Updated README.md")
    
    def run(self):
        """Execute the full reorganization"""
        print("🧹 Starting Hermes Project Reorganization...")
        print("=" * 60)
        
        self.create_directories()
        self.organize_docs()
        self.organize_scripts()
        self.organize_tests()
        self.organize_backups()
        self.create_docs_readme()
        self.create_scripts_readme()
        self.create_tests_readme()
        self.update_main_readme()
        
        print("\n✨ Reorganization Complete!\n")
        print("Changes made:")
        for change in self.changes:
            print(f"  {change}")
        
        print("\n" + "=" * 60)
        print("🎉 Your project is now clean and organized!")
        print("\nRoot files (what you'll see):")
        print("  ├── hermes_dashboard.py")
        print("  ├── config_cities.py")
        print("  ├── run_hermes.py")
        print("  ├── hermes.db")
        print("  ├── .env")
        print("  ├── requirements.txt")
        print("  ├── README.md")
        print("  ├── services/")
        print("  ├── docs/")
        print("  ├── scripts/")
        print("  ├── tests/")
        print("  └── backups/")
        print("\nMuch better! 🚀")

if __name__ == "__main__":
    organizer = ProjectOrganizer()
    organizer.run()
