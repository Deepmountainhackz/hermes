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

### Space & Astronomical Events Layer ✅
- **ISS Tracker**: Real-time International Space Station position monitoring
- **NEO Monitor**: Near-Earth Object (asteroid) detection and tracking
- **Solar Activity**: Solar flare detection and geomagnetic storm alerts
- Risk assessment for space weather impacts on infrastructure
- CSV export for all space data sources

### Environment Layer ✅
- **Weather Monitor**: Multi-city weather tracking with real-time conditions
- Temperature, humidity, wind speed, and atmospheric pressure
- Support for any city worldwide
- Weather comparison across multiple locations

### Social Intelligence Layer ✅
- **News Aggregator**: RSS feed monitoring from major news sources
- Real-time headlines from BBC, Reuters, TechCrunch, Hacker News, NPR, The Guardian
- Automated news collection and archiving
- Topic tracking across multiple sources

### Master Control System ✅
- **Unified Interface**: Single command to run all data collectors
- Interactive menu with individual or batch collection options
- Error tracking and success reporting
- Automated data collection cycles

## Installation

### Prerequisites
- Python 3.12+
- API Keys:
  - Alpha Vantage (free at https://www.alphavantage.co)
  - NASA API (free at https://api.nasa.gov)
  - OpenWeatherMap (free at https://openweathermap.org/api)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/DeepmountainHackz/hermes.git
cd hermes
```

2. Install dependencies:
```bash
pip install requests pandas python-dotenv feedparser
```

3. Create a `.env` file with your API keys:
```
ALPHA_VANTAGE_KEY=your_key_here
NASA_API_KEY=your_key_here
OPENWEATHER_KEY=your_key_here
```

4. Run the master control:
```bash
python run_hermes.py
```

Or run individual collectors:
```bash
python services/markets/fetch_market_data.py
python services/space/fetch_iss_data.py
python services/space/fetch_neo_data.py
python services/space/fetch_solar_data.py
python services/environment/fetch_weather_data.py
python services/social/fetch_news_data.py
```

## Project Architecture
```
hermes/
├── services/
│   ├── markets/
│   │   └── fetch_market_data.py      # Stock market data collector
│   ├── space/
│   │   ├── fetch_iss_data.py         # ISS position tracker
│   │   ├── fetch_neo_data.py         # Asteroid monitor
│   │   └── fetch_solar_data.py       # Solar flare detector
│   ├── environment/
│   │   └── fetch_weather_data.py     # Weather monitor
│   └── social/
│       └── fetch_news_data.py        # RSS news aggregator
├── run_hermes.py                      # Master control interface
├── .env                               # API keys (not committed)
├── .gitignore                         # Security configuration
└── README.md                          # This file
```

## Data Layers

### 📈 Markets
- Real-time and historical stock data
- Multiple symbols with configurable watchlists
- Price trends and volume analysis

### 🛰️ Space
- ISS orbital tracking with position updates
- Near-Earth Object approach monitoring
- Solar flare activity and geomagnetic storm alerts
- Space weather risk assessment

### 🌦️ Environment
- Current weather conditions for any city
- Multi-city comparison
- Temperature, humidity, pressure, wind data
- Weather description and cloud coverage

### 📰 Social Intelligence
- Multi-source news aggregation
- Real-time headline monitoring
- Topic tracking across sources
- Automated news archiving

## Planned Features

### 🔜 Phase 3: Advanced Intelligence
- **Wildfire Tracking**: NASA FIRMS real-time wildfire monitoring
- **Seismic Activity**: USGS earthquake detection and alerts
- **Demographics**: UN, World Bank, WHO datasets
- **Dalio Cycles**: Country-level macro indicator tracking
- **LLM Processing**: Entity extraction and causal modeling
- **Correlation Analysis**: Cross-layer event relationships

### 🔜 Phase 4: Visualization & Alerts
- **Streamlit Dashboard**: Interactive multi-layer visualization
- **Pydeck Maps**: Geographic overlay of all data sources
- **Real-time Alerts**: Configurable thresholds and notifications
- **Trend Analysis**: Historical pattern detection
- **Risk Scoring**: Composite risk assessment across layers

## Data Sources

- **Alpha Vantage**: Stock market data
- **NASA NEO API**: Near-Earth Object tracking
- **NASA DONKI**: Solar flare and space weather monitoring
- **Open Notify**: ISS real-time position
- **OpenWeatherMap**: Global weather data
- **RSS Feeds**: BBC, Reuters, TechCrunch, Hacker News, NPR, The Guardian
- More sources coming soon...

## Security

- API keys stored in `.env` (never committed to Git)
- Rate limiting and error handling built-in
- All sensitive data excluded via `.gitignore`
- Secure credential management with python-dotenv

## Tech Stack

- **Language**: Python 3.12
- **Data Processing**: Pandas
- **API Requests**: Requests library
- **RSS Parsing**: Feedparser
- **Environment Management**: python-dotenv
- **Version Control**: Git/GitHub

## Roadmap

**Phase 1: Foundation** ✅ COMPLETE
- [x] Development environment setup
- [x] API integration framework
- [x] Error handling and logging
- [x] CSV data export
- [x] Security configuration

**Phase 2: Core Data Layers** ✅ COMPLETE
- [x] Markets data collection
- [x] ISS real-time tracking
- [x] NEO asteroid monitoring
- [x] Solar flare detection
- [x] Weather monitoring
- [x] News aggregation
- [x] Master control system
- [x] Professional code organization

**Phase 3: Intelligence & Analysis** (In Progress)
- [ ] Database integration (PostgreSQL/TimescaleDB)
- [ ] Wildfire tracking (NASA FIRMS)
- [ ] Seismic monitoring (USGS)
- [ ] LLM-based event classification
- [ ] Cross-layer correlation analysis
- [ ] Automated insights generation

**Phase 4: Visualization & Access** (Planned)
- [ ] Streamlit dashboard
- [ ] Interactive map layers
- [ ] Real-time alert system
- [ ] API endpoints for data access
- [ ] Historical trend visualization
- [ ] Risk assessment interface

## Usage Examples

### Fetch All Data
```bash
python run_hermes.py
# Select option 7: Run ALL Collectors
```

### Check Latest Stock Prices
```bash
python run_hermes.py
# Select option 1: Markets Layer
```

### Monitor Space Weather
```bash
python run_hermes.py
# Select option 3: NEO Monitor
# Select option 4: Solar Activity
```

### Get Current News Headlines
```bash
python run_hermes.py
# Select option 6: News Monitor
```

## Contributing

This is a personal learning project, but suggestions and feedback are welcome! Feel free to open issues or submit pull requests.

## License

MIT License - Feel free to use and modify as needed.

## Author

Built by DeepmountainHackz as a comprehensive learning project in data engineering, API integration, and systems intelligence.

## Acknowledgments

- NASA for open space data APIs
- OpenWeatherMap for weather data access
- Alpha Vantage for financial market data
- All RSS feed providers for open news access

---

**Status**: 🚀 Active Development  
**Last Updated**: November 2025  
**Current Version**: v0.2 - Multi-Layer Intelligence Platform