# Hermes - Global Systems Intelligence Platform

A modular data intelligence system that unifies financial, environmental, social, and demographic data into one transparent framework.

## Overview

Hermes is designed to surface actionable signals, track long-term structural trends, and visualize real-time disruptions across global systems.

## Current Features

### Market Data Layer ✅
- Automated fetching of stock market data (AAPL, MSFT, GOOGL)
- Daily price tracking (Open, High, Low, Close, Volume)
- CSV export for historical analysis
- Error handling and rate limit management

## Installation

### Prerequisites
- Python 3.12+
- Alpha Vantage API key (free at https://www.alphavantage.co)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/DeepmountainHackz/hermes.git
cd hermes
```

2. Install dependencies:
```bash
pip install requests pandas python-dotenv
```

3. Create a `.env` file with your API key:
```
ALPHA_VANTAGE_KEY=your_key_here
```

4. Run the market data fetcher:
```bash
python fetch_market_data.py
```

## Project Architecture
```
hermes/
├── fetch_market_data.py    # Market data ingestion
├── .env                     # API keys (not committed)
├── .gitignore              # Security configuration
└── data_*.csv              # Generated data files
```

## Planned Features

### 🔜 Coming Soon
- **Environment Tracker**: Real-time wildfire, seismic, weather data
- **Social & Unrest Layer**: GDELT, RSS feeds, sentiment analysis
- **Demographics & Health**: UN, World Bank, WHO datasets
- **Dalio-Style Cycle Analysis**: Country-level macro indicators
- **Geo-News Map**: Interactive country-specific news aggregation
- **LLM Intelligence Layer**: Entity extraction and causal modeling
- **Streamlit Dashboard**: Interactive visualization and alerts

## Data Sources

- **Alpha Vantage**: Stock market data
- More sources coming soon...

## Security

- API keys stored in `.env` (never committed to Git)
- Rate limiting and error handling built-in
- All sensitive data excluded via `.gitignore`

## Tech Stack

- **Language**: Python 3.12
- **Data Processing**: Pandas
- **API Requests**: Requests library
- **Environment Management**: python-dotenv
- **Version Control**: Git/GitHub

## Roadmap

**Phase 1: Foundation** ✅
- [x] Basic market data fetching
- [x] CSV export functionality
- [x] Error handling
- [x] Security setup

**Phase 2: Multi-Source Integration** (In Progress)
- [ ] Weather API integration
- [ ] News API integration
- [ ] Database setup (PostgreSQL/TimescaleDB)

**Phase 3: Intelligence Layer** (Planned)
- [ ] LLM-based event classification
- [ ] Causal relationship modeling
- [ ] Predictive analytics

**Phase 4: Visualization** (Planned)
- [ ] Streamlit dashboard
- [ ] Interactive maps (Pydeck)
- [ ] Real-time alerts

## Contributing

This is a personal learning project, but suggestions and feedback are welcome!

## License

MIT License - Feel free to use and modify as needed.

## Author

Built by DeepmountainHackz as a comprehensive learning project in data engineering and systems integration.

---

**Status**: 🚧 Active Development | **Last Updated**: October 2025