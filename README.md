# Hermes Intelligence Platform

Multi-layer intelligence platform collecting and analyzing data from multiple sources.

## Quick Start

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

## Project Structure

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

## Features

- Markets - Real-time stock data
- Space - ISS tracking, NEO monitoring, solar flares
- Geography - Country profiles and analytics
- Environment - Global weather with 3D globe
- News - Latest headlines from multiple sources

## Documentation

See the docs/ directory for detailed documentation:

- Migration Guide (docs/MIGRATION_GUIDE.md)
- Error Handling Guide (docs/ERROR_HANDLING_GUIDE.md)
- Contributing (docs/CONTRIBUTING.md)
- Roadmap (docs/HERMES_ROADMAP.md)

## Development

```bash
# Run tests
python -m pytest tests/

# Run specific collector
python scripts/collect_weather_50cities.py

# Check database schema
python scripts/check_schema.py
```

## Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- H3-py
- API keys (see .env.example)

## Contributing

See CONTRIBUTING.md in docs/ for guidelines.

## License

MIT License - See LICENSE file for details.

---

Built for intelligence gathering and analysis
