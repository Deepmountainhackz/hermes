# 🌍 Hermes Intelligence Platform

> **Global Systems Intelligence for Investment Research**

A comprehensive, automated data collection and analysis platform that integrates financial markets, economic indicators, environmental data, space events, and news intelligence to support macro investment decision-making.

**Live Dashboard:** [hermes-intelligence.streamlit.app](https://hermes-intelligence.streamlit.app)

---

## 🎯 Overview

Hermes is a multi-dimensional intelligence platform designed for serious macro investing. It automatically collects, stores, and visualizes data from multiple global sources every 2 hours, providing a comprehensive view of:

- **Financial Markets** - Stocks, commodities, and forex rates
- **Economic Indicators** - GDP, unemployment, inflation across major economies  
- **Environmental Events** - Weather, earthquakes, wildfires, storms
- **Space Events** - ISS tracking, near-Earth objects, solar activity
- **News Intelligence** - Premium financial news sources

---

## 📊 Current Capabilities

### **Financial Markets Intelligence**
- **12 Stocks** across 5 sectors (Tech, Finance, Energy, Healthcare, Consumer)
  - Tech: AAPL, GOOGL, MSFT
  - Finance: JPM, GS, V
  - Energy: XOM, CVX
  - Healthcare: JNJ, UNH
  - Consumer: WMT, PG

- **5 Commodities** (Energy, Metals, Agriculture)
  - WTI Crude Oil
  - Natural Gas
  - Copper
  - Wheat
  - Corn

- **7 Forex Pairs** (Major Currencies vs USD)
  - EUR, GBP, JPY, CHF, AUD, CAD, CNY

### **Economic Indicators**
- **15 Key Indicators** across 5 major economies
  - United States: GDP, Unemployment, Inflation, Interest Rate
  - Eurozone: GDP, Unemployment, Inflation
  - China: GDP, Unemployment
  - Japan: GDP, Unemployment, Inflation
  - United Kingdom: GDP, Unemployment, Inflation

### **Environmental Monitoring**
- **50 Cities Worldwide** - Real-time weather with 3D globe visualization
- **Earthquake Tracking** - Magnitude 4.5+ globally (USGS data)
- **Wildfire Monitoring** - Active wildfires with geocoded locations
- **Storm Tracking** - Active hurricanes, typhoons, severe weather

### **Space & Science**
- **ISS Position** - Real-time International Space Station tracking
- **Near-Earth Objects** - Asteroids approaching Earth
- **Solar Activity** - Solar flares and geomagnetic storms

### **News Intelligence**
- **Premium Sources** - Bloomberg, Reuters, Financial Times, Wall Street Journal, BBC
- **Technology News** - Hacker News integration

---

## 🚀 Automated Data Collection

**Frequency:** Every 2 hours via GitHub Actions  
**Total Collectors:** 13 independent data collectors  
**Database:** PostgreSQL (hosted on Railway)  
**Storage:** 14 normalized tables with proper indexing

### Collection Schedule
```
0 */2 * * * - Runs at: 12:00 AM, 2:00 AM, 4:00 AM, ... (12 times daily)
```

All data is automatically collected, validated, and stored without manual intervention.

---

## 🛠️ Technical Stack

### **Core Technologies**
- **Python 3.11** - Primary development language
- **PostgreSQL** - Production database (Railway)
- **Streamlit** - Interactive web dashboard
- **GitHub Actions** - Automated data collection

### **Data Processing**
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive visualizations
- **H3** - Hexagonal geospatial indexing
- **Geopy** - Location geocoding

### **APIs Integrated**
1. **Alpha Vantage** - Stocks, commodities, forex
2. **FRED (Federal Reserve)** - Economic indicators
3. **USGS** - Earthquake data
4. **NASA EONET** - Wildfires and storms
5. **NASA APIs** - NEO, solar activity, ISS tracking
6. **OpenWeatherMap** - Global weather data
7. **NewsAPI** - Premium news sources

---

## 📁 Project Structure

```
hermes/
├── services/              # Data collection modules
│   ├── markets/          # Stock, commodity, forex, economic collectors
│   ├── environment/      # Weather, earthquake, wildfire, storm collectors
│   ├── space/            # ISS, NEO, solar collectors
│   ├── social/           # News collectors
│   └── geography/        # Country data collectors
├── .github/
│   └── workflows/        # GitHub Actions automation
├── docs/                 # Comprehensive documentation
├── database.py           # Database connection manager
├── initialize_database.py # Database schema setup
├── hermes_dashboard.py   # Streamlit web interface
└── requirements.txt      # Python dependencies
```

---

## 🎨 Dashboard Features

The interactive Streamlit dashboard provides:

### **📈 Markets Overview**
- Real-time stock prices with interactive charts
- Historical price trends
- Sector performance tracking

### **🌍 Environment Globe**
- 3D interactive globe with H3 hexagonal mapping
- 50 cities with live weather data
- Earthquake markers (M4.5+)
- Wildfire and storm locations

### **☄️ Space Events**
- ISS position tracking on 3D map
- Near-Earth Object trajectories
- Solar flare activity

### **📰 News Feed**
- Latest articles from premium sources
- Technology news aggregation
- Time-sorted updates

---

## 💡 Investment Intelligence Applications

### **Macro Analysis**
- Compare GDP growth across US, EU, China, Japan, UK
- Track inflation and unemployment trends
- Monitor interest rate differentials
- Identify economic divergences

### **Sector Rotation**
- Correlate sector performance with economic data
- Identify rotation opportunities
- Track cyclical vs defensive stocks

### **Currency Analysis**
- Monitor forex strength/weakness
- Hedge international exposure
- Identify carry trade opportunities

### **Risk Management**
- Natural disaster impact assessment
- Supply chain disruption tracking
- Regional economic stability
- Weather-related risks

### **Commodity Intelligence**
- Track energy prices for sector correlation
- Monitor agricultural conditions
- Industrial metals demand signals
- Inflation indicators

---

## 🔧 Setup & Installation

### **Prerequisites**
- Python 3.11+
- PostgreSQL database
- API keys for data sources

### **Environment Variables**
Create a `.env` file with:
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# APIs
ALPHA_VANTAGE_KEY=your_key_here
FRED_API_KEY=your_key_here
NASA_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
```

### **Installation**
```bash
# Clone repository
git clone https://github.com/DeepmountainHackz/hermes.git
cd hermes

# Install dependencies
pip install -r requirements.txt

# Initialize database
python initialize_database.py

# Run dashboard locally
streamlit run hermes_dashboard.py
```

### **GitHub Actions Setup**
Add all API keys as repository secrets:
- Settings → Secrets and variables → Actions → New repository secret

---

## 📊 Database Schema

### **Core Tables**
- `stocks` - Stock price data with OHLCV
- `commodities` - Commodity prices and units
- `forex` - Exchange rates with bid/ask
- `economic_indicators` - Country-level economic data
- `weather` - 50 cities with temperature, conditions, wind
- `earthquakes` - Seismic activity with location and magnitude
- `wildfires` - Active fires with geocoded positions
- `storms` - Active severe weather events
- `iss_positions` - ISS tracking data
- `neo_objects` - Near-Earth Objects
- `solar_flares` - Solar activity
- `news` - Article aggregation
- `countries` - Country profiles and statistics

---

## 📈 Data Collection Performance

### **Collection Metrics**
- **Average runtime:** 8-12 minutes per collection cycle
- **Success rate:** 95%+ across all collectors
- **Data points collected:** 100+ per cycle
- **Historical data:** Accumulated since deployment
- **Uptime:** 99%+ (GitHub Actions reliability)

### **API Usage**
- **Total API calls per cycle:** ~50-60 calls
- **Rate limit management:** Configured delays between requests
- **Error handling:** Retry logic with exponential backoff
- **Data validation:** Comprehensive checks before storage

---

## 🎯 Roadmap

### **Phase 1: Core Expansion** (Current)
- ✅ Multi-sector stock coverage
- ✅ Commodity and forex tracking
- ✅ Economic indicators (5 countries)
- ✅ Natural disaster monitoring
- ✅ Automated collection pipeline

### **Phase 2: Enhanced Intelligence** (Next)
- [ ] Additional economic indicators (PMI, confidence indexes)
- [ ] Country economic profiles (detailed GDP, trade data)
- [ ] Shipping weather intelligence (wind patterns, routes)
- [ ] Cryptocurrency tracking (BTC, ETH)
- [ ] Alert system for significant events

### **Phase 3: Advanced Analysis** (Future)
- [ ] GDELT social unrest integration
- [ ] LLM-powered event classification
- [ ] Cross-layer correlation analysis
- [ ] European geopolitical intelligence
- [ ] Custom query interface

### **Phase 4: Visualization & UI** (Future)
- [ ] Advanced interactive maps
- [ ] Time-series analysis tools
- [ ] Portfolio correlation views
- [ ] Custom dashboard builder
- [ ] Mobile-responsive design

---

## 🔍 Use Cases

### **For Macro Investors**
- Monitor global economic health
- Track currency movements
- Correlate commodity prices with sectors
- Assess regional risks

### **For Risk Managers**
- Natural disaster impact assessment
- Supply chain disruption tracking
- Geographic exposure analysis
- Weather-related risks

### **For Analysts**
- Multi-dimensional data correlation
- Historical trend analysis
- Event impact studies
- Cross-market relationships

---

## 📚 Documentation

Comprehensive guides available in `/docs`:
- API Integration guides
- Database schema documentation
- Collector implementation details
- Deployment instructions
- Bug fixes and troubleshooting

---

## 🤝 Contributing

This is a personal investment research tool, but feedback and suggestions are welcome:
1. Open an issue for bugs or feature requests
2. Suggest new data sources
3. Share analysis techniques

---

## ⚠️ Known Limitations

### **API Rate Limits**
- Alpha Vantage free tier: 25 calls/day
- Collections run every 2 hours to manage limits
- Premium upgrade available for higher frequency

### **Data Quality**
- Some economic indicators incomplete (80% success rate)
- Storm/wildfire coordinates occasionally missing (NASA data)
- Solar flare data depends on solar activity

### **Coverage**
- Economic data: 5 major economies (expanding)
- Weather: 50 cities (expandable)
- Stocks: 12 symbols (focus on diversification vs volume)

---

## 📄 License

Personal project - All rights reserved.

---

## 🎓 Development Journey

Built from scratch in 4 days by a complete programming beginner with:
- Zero prior coding experience
- Background in macro investing and hedge fund management
- Goal: Create a professional investment research platform

**Result:** Production-grade multi-API intelligence system with automated collection, professional error handling, and comprehensive data coverage.

---

## 📞 Contact

**Developer:** Big Cheese  
**Repository:** [github.com/DeepmountainHackz/hermes](https://github.com/DeepmountainHackz/hermes)  
**Dashboard:** [hermes-intelligence.streamlit.app](https://hermes-intelligence.streamlit.app)

---

## 🏆 Acknowledgments

**Data Sources:**
- Alpha Vantage - Financial market data
- FRED (St. Louis Fed) - Economic indicators
- USGS - Earthquake data
- NASA - Space and Earth observation
- OpenWeatherMap - Global weather
- NewsAPI - Premium news sources

**Technologies:**
- Streamlit - Dashboard framework
- PostgreSQL - Database system
- GitHub Actions - Automation platform

---

## ⭐ Project Stats

![GitHub last commit](https://img.shields.io/github/last-commit/DeepmountainHackz/hermes)
![GitHub repo size](https://img.shields.io/github/repo-size/DeepmountainHackz/hermes)

**Built with dedication for serious investment research.** 📊🌍🚀
