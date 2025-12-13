# 🌍 Hermes Intelligence Platform

> **Global Systems Intelligence for Investment Research**

A comprehensive, automated data collection and analysis platform that integrates financial markets, cryptocurrency, economic indicators, environmental data, space events, and news intelligence to support macro investment decision-making.

**Live Dashboard:** [hermes-intelligence.streamlit.app](https://hermes-intelligence.streamlit.app)

---

## ✨ What's New in v4.2

### UX Improvements
- **🎨 Light Mode Theme** - Clean, professional light mode styling throughout
- **📊 Stock Heatmap** - Treemap visualization showing performance by volume
- **🔄 Data Freshness Indicators** - Real-time status of data collection
- **🕐 Market Status Banner** - Live US market open/closed status
- **💡 Key Highlights** - Auto-generated insights on Overview page
- **📈 Gauge Charts** - Visual Fear & Greed gauges
- **✨ Sparklines** - Mini trend charts for tables
- **ℹ️ Tooltip Explainers** - Contextual help icons
- **🌍 Improved Globe** - Light mode globe with better country visibility

### v4.1 Features
- **📊 Market Sentiment Dashboard** - Fear & Greed Index for crypto and stocks
- **📈 Treasury Yield Curve** - 3M, 2Y, 5Y, 10Y, 30Y yields with curve visualization
- **📉 VIX Volatility Index** - Real-time market fear gauge with interpretation
- **🏦 Central Bank Calendar** - Fed, ECB, BoE, BoJ, BoC meeting schedules
- **🔗 Cross-Asset Correlation Matrix** - Visual correlations across stocks, crypto, commodities
- **🌐 3D Interactive Globe** - Rotating Earth visualization with weather data overlay
- **📊 Time Series Analysis** - Historical trends for stocks, crypto, economics, and weather
- **🔥 GDELT Integration** - Global events and social unrest tracking with sentiment analysis
- **📈 Enhanced Economics** - 32+ indicators including PMI, Consumer Sentiment, Retail Sales
- **₿ Cryptocurrency Tracking** - Top 15 cryptos with real-time prices and 24h changes
- **📥 Data Export** - Download any dataset as CSV with one click
- **🚨 Smart Alerts** - Stock moves, crypto volatility, hazardous NEOs, and social unrest

---

## 🎯 Overview

Hermes is a multi-dimensional intelligence platform designed for serious macro investing. It automatically collects, stores, and visualizes data from multiple global sources every 6 hours, providing a comprehensive view of:

- **Financial Markets** - Stocks, commodities, and forex rates
- **Cryptocurrency** - Top 15 cryptos by market cap with price tracking
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

### **Cryptocurrency Intelligence**
- **15 Top Cryptos** by market cap via CoinGecko API
  - Bitcoin, Ethereum, Tether, BNB, Solana
  - XRP, Cardano, Dogecoin, Polkadot, Avalanche
  - Chainlink, Polygon, Litecoin, Uniswap, Stellar
- **Real-time Data:** Price, 24h change, market cap, volume
- **Alerts:** Automatic detection of >10% price moves

### **Economic Indicators**
- **32+ Key Indicators** across 5 major economies
  - United States: GDP, Unemployment, Inflation, Interest Rate, PMI, Consumer Sentiment, Retail Sales, Industrial Production
  - Eurozone: GDP, Unemployment, Inflation, Consumer Confidence, Industrial Production
  - United Kingdom: GDP, Unemployment, Inflation, Consumer Confidence, Retail Sales
  - Japan: GDP, Unemployment, Inflation, Consumer Confidence, Industrial Production
  - China: GDP, Inflation, Industrial Production

### **Market Sentiment & Risk**
- **Treasury Yields** - 3-Month, 2-Year, 5-Year, 10-Year, 30-Year
- **Yield Curve Spread** - 10Y-2Y spread (recession indicator)
- **VIX Volatility Index** - Market fear gauge
- **Fear & Greed Index** - Crypto (via Alternative.me) and Stock (calculated)
- **Cross-Asset Correlations** - Stocks, crypto, commodities relationships
- **Central Bank Calendar** - 8 major central banks with 2025 meeting dates

### **Global Events (GDELT)**
- **Social Unrest Tracking** - Protests, riots, strikes worldwide
- **Geopolitical Events** - Sanctions, military movements, diplomatic crises
- **Sentiment Analysis** - Tone scoring for event severity
- **20 Countries Monitored** - Major economies and emerging markets

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

**Frequency:** Every 6 hours via GitHub Actions
**Total Collectors:** 11 independent data collectors
**Database:** PostgreSQL (hosted on Railway)
**Storage:** 16 normalized tables with proper indexing

### Collection Schedule
```
0 */6 * * * - Runs at: 12:00 AM, 6:00 AM, 12:00 PM, 6:00 PM (4 times daily)
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
2. **CoinGecko** - Cryptocurrency data (free, no key required)
3. **FRED (Federal Reserve)** - Economic indicators
4. **USGS** - Earthquake data
5. **NASA EONET** - Wildfires and storms
6. **NASA APIs** - NEO, solar activity, ISS tracking
7. **OpenWeatherMap** - Global weather data
8. **NewsAPI** - Premium news sources

---

## 📁 Project Structure

```
hermes/
├── core/                  # Core infrastructure
│   ├── config.py         # Configuration management
│   ├── database.py       # Database connection manager
│   └── exceptions.py     # Custom exceptions
├── services/              # Business logic layer
│   ├── markets_service.py    # Stocks data
│   ├── forex_service.py      # Currency exchange
│   ├── commodities_service.py # Commodities
│   ├── crypto_service.py     # Cryptocurrency (NEW)
│   ├── economics_service.py  # Economic indicators
│   ├── weather_service.py    # Weather data
│   ├── space_service.py      # Space events
│   ├── disasters_service.py  # Earthquakes, wildfires, storms
│   └── news_service.py       # News aggregation
├── repositories/          # Database operations
├── collectors/            # Data collection orchestrators
├── .github/
│   └── workflows/        # GitHub Actions automation
├── hermes_dashboard.py   # Streamlit web interface (dark mode)
└── requirements.txt      # Python dependencies
```

---

## 🎨 Dashboard Features

The interactive Streamlit dashboard provides a sleek dark-mode interface:

### **🌙 Dark Mode UI**
- Professional dark theme throughout
- Optimized chart colors for readability
- Custom CSS styling for all components

### **📈 Markets Overview**
- Real-time stock prices with interactive charts
- Commodities and forex tracking
- Sector performance with visual indicators

### **₿ Cryptocurrency**
- Top 15 cryptos by market cap
- Price, 24h change, market cap, volume
- Visual price change indicators (green/red)

### **🌍 Weather & Environment**
- 50 cities with live weather data
- Temperature, humidity, wind conditions
- Global coverage across all continents

### **☄️ Space Events**
- ISS position tracking
- Near-Earth Object monitoring with hazard alerts
- Solar flare activity timeline

### **📰 News Feed**
- Latest articles from premium sources
- Source filtering and time-sorted updates

### **🚨 Alerts & Export**
- **Stock Alerts:** >5% daily price moves
- **Crypto Alerts:** >10% 24h price changes
- **Space Alerts:** Potentially hazardous asteroids
- **CSV Export:** Download any dataset with one click

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

### **Crypto Analysis**
- Monitor market cap shifts across top cryptos
- Track 24h volatility for trading opportunities
- Correlation with risk-on/risk-off sentiment
- Alerts for significant price movements

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
- `near_earth_objects` - Near-Earth Objects
- `solar_flares` - Solar activity
- `news` - Article aggregation
- `crypto` - Cryptocurrency prices and market data

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

### **Phase 1: Core Expansion** ✅ Complete
- ✅ Multi-sector stock coverage
- ✅ Commodity and forex tracking
- ✅ Economic indicators (5 countries)
- ✅ Natural disaster monitoring
- ✅ Automated collection pipeline

### **Phase 2: Enhanced Intelligence** ✅ Complete
- ✅ Cryptocurrency tracking (15 top cryptos)
- ✅ Alert system for significant events
- ✅ CSV data export
- ✅ Additional economic indicators (PMI, confidence indexes)

### **Phase 3: Advanced Analysis** ✅ Complete
- ✅ GDELT social unrest integration
- ✅ Cross-layer correlation analysis
- ✅ Treasury yields and yield curve tracking
- ✅ VIX volatility index
- ✅ Fear & Greed Index (crypto + stock)
- [ ] LLM-powered event classification
- [ ] Custom query interface

### **Phase 4: Visualization & UI** ✅ Complete
- ✅ 3D interactive globe visualization
- ✅ Time-series analysis tools
- ✅ Cross-asset correlation matrix
- ✅ Central bank meeting calendar
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
- CoinGecko - Cryptocurrency data
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
