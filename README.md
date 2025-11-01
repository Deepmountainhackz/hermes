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

### Space & Astronomical Events Layer ✅ NEW!
- **ISS Tracker**: Real-time International Space Station position monitoring
- **NEO Monitor**: Near-Earth Object (asteroid) detection and tracking
- **Solar Activity**: Solar flare detection and geomagnetic storm alerts
- Risk assessment for space weather impacts on infrastructure
- CSV export for all space data sources

## Installation

### Prerequisites
- Python 3.12+
- Alpha Vantage API key (free at https://www.alphavantage.co)
- NASA API key (free at https://api.nasa.gov)

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

3. Create a `.env` file with your API keys:
```
ALPHA_VANTAGE_KEY=your_key_here
NASA_API_KEY=your_key_here
```

4. Run any data fetcher:
```bash
python fetch_market_data.py    # Stock market data
python fetch_iss_data.py        # ISS position tracking
python fetch_neo_data.py        # Asteroid monitoring
python fetch_solar_data.py      # Solar flare detection
```

## Project Architecture
```
hermes/
├── fetch_market_data.py    # Market data ingestion
├── fetch_iss_data.py       # ISS position tracker
├── fetch_neo_data.py       # Near-Earth Object monitor
├── fetch_solar_data.py     # Solar flare detector
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
- **NASA NEO API**: Near-Earth Object tracking
- **NASA DONKI**: Solar flare and space weather monitoring
- **Open Notify**: ISS real-time position
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
- [x] ISS real-time tracking
- [x] NEO asteroid monitoring
- [x] Solar flare detection

**Phase 2: Multi-Source Integration** (In Progress)
- [ ] Weather API integration
- [ ] News API integration
- [ ] Database setup (PostgreSQL/TimescaleDB)

**Phase 3: Intelligence Layer** (Planned)
- [ ] LLM-based event classification
- [ ] Causal relationship modeling
- [ ] Predictive analytics
- [ ] Space-financial correlation analysis

**Phase 4: Visualization** (Planned)
- [ ] Streamlit dashboard
- [ ] Interactive maps (Pydeck)
- [ ] Real-time alerts
- [ ] ISS tracking map
- [ ] NEO trajectory visualization

## Contributing

This is a personal learning project, but suggestions and feedback are welcome!

## License

MIT License - Feel free to use and modify as needed.

## Author

Built by DeepmountainHackz as a comprehensive learning project in data engineering and systems integration.

---

**Status**: 🚧 Active Development | **Last Updated**: November 2025