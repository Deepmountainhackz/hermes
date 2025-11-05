# 🌐 Hermes Intelligence Platform

**Personal investment intelligence system for global data monitoring and analysis**

![Status](https://img.shields.io/badge/status-active-success)
![Automation](https://img.shields.io/badge/automation-enabled-blue)
![Deployment](https://img.shields.io/badge/deployment-live-green)

**Live Dashboard:** [hermes-intelligence.streamlit.app](https://hermes-intelligence.streamlit.app)

---

## 📊 Overview

Hermes is an automated intelligence platform that aggregates global data for investment research and decision-making. It collects data from multiple sources every hour and presents it through an interactive dashboard with real-time visualizations.

**Purpose:** Long-term research tool for understanding market dynamics, geopolitical trends, and environmental factors affecting investment decisions.

---

## ✅ Current Capabilities

### **Data Collection (Automated Hourly)**

| Category | Data Sources | Status |
|----------|-------------|--------|
| 📈 **Markets** | 3 major stocks (AAPL, GOOGL, MSFT) | ✅ Live |
| ☄️ **Space** | Near-Earth Objects, Solar Flares, ISS Position | ✅ Live |
| 🌍 **Geography** | 20 country profiles with demographics | ✅ Live |
| 🌦️ **Weather** | 50 global cities with temperature data | ✅ Live |
| 📰 **News** | Bloomberg, Reuters, BBC, Financial Times | ✅ Live |

### **Visualization**
- Interactive 3D globe for weather and geography
- Candlestick charts for market data
- Real-time ISS tracking map
- Country demographic comparisons
- News aggregation dashboard

### **Infrastructure**
- ✅ SQLite database with 8 tables
- ✅ Automated data collection via GitHub Actions
- ✅ Cloud deployment on Streamlit
- ✅ CI/CD pipeline (auto-deploy on push)
- ✅ 7 production-grade collectors with error handling

---

## 🚀 Roadmap

### **Phase 1: Financial Markets Expansion** (Next 1-2 weeks)
**Goal:** Comprehensive market coverage

- [ ] Expand to 30+ major stocks
- [ ] Add commodities (Gold, Silver, Oil, Copper, Wheat)
- [ ] Add forex pairs (EUR/USD, GBP/USD, USD/JPY)
- [ ] Add market indices (S&P 500, NASDAQ, Dow)
- [ ] Create custom watchlist feature
- [ ] Add technical indicators (MA, RSI, MACD)

**Why:** Core investment data, highest ROI

---

### **Phase 2: Country Economic Intelligence** (Weeks 3-4)
**Goal:** Macro economic framework

- [ ] GDP data (World Bank API)
- [ ] Inflation rates by country
- [ ] Unemployment statistics
- [ ] Interest rates
- [ ] Debt-to-GDP ratios
- [ ] Trade balances
- [ ] Country comparison tools
- [ ] Historical trend analysis

**Why:** Essential for macro investing decisions

---

### **Phase 3: Shipping & Marine Intelligence** (Weeks 5-6)
**Goal:** Track weather impacts on trade routes

- [ ] Hurricane tracking with forecast paths
- [ ] Active storm systems monitoring
- [ ] Wind speed heat maps
- [ ] Major shipping route overlays
- [ ] Storm severity indicators
- [ ] Port weather conditions
- [ ] Dedicated marine weather page

**Why:** Unique edge for commodity/shipping analysis

**Future Enhancement:** Advanced wind vectors, wave heights, ocean currents (pending budget)

---

### **Phase 4: Intelligence Layer** (Month 3+)
**Goal:** Automated analysis and alerts

- [ ] Custom alerts (price thresholds, weather events, news keywords)
- [ ] Pattern recognition across data layers
- [ ] Correlation analysis (weather → commodity prices)
- [ ] Daily summary reports
- [ ] Investment opportunity scanner
- [ ] Risk monitoring dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub Actions                      │
│              (Runs every hour, 24/7)                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ├──► ISS Collector
                       ├──► NEO Collector
                       ├──► Solar Flares Collector
                       ├──► Markets Collector
                       ├──► News Collector
                       ├──► Weather Collector
                       └──► Country Collector
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   SQLite Database                       │
│        (hermes.db - Stores all collected data)          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit Dashboard (Cloud)                │
│         hermes-intelligence.streamlit.app               │
│                                                         │
│  ├── Overview Page (Summary metrics)                   │
│  ├── Markets Page (Stock charts)                       │
│  ├── Space Page (ISS, NEO, Solar)                      │
│  ├── Geography Page (Country profiles)                 │
│  ├── Environment Page (3D weather globe)               │
│  └── News Page (Latest headlines)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- SQLite (database)
- Requests (API calls)
- Pandas (data processing)

**Frontend:**
- Streamlit (dashboard framework)
- Plotly (interactive visualizations)
- H3 (geospatial indexing)
- Pydeck (3D mapping)

**DevOps:**
- GitHub Actions (automation)
- Streamlit Cloud (deployment)
- Git (version control)

**Data Sources:**
- NASA APIs (space data)
- OpenWeather API (weather)
- NewsAPI (news aggregation)
- Alpha Vantage (market data)
- REST Countries API (geography)

---

## 📈 Data Update Frequency

| Data Type | Update Frequency | Source |
|-----------|-----------------|---------|
| Stock Prices | Every hour | Alpha Vantage |
| Weather | Every hour | OpenWeather |
| ISS Position | Every hour | Open Notify |
| News | Every hour | NewsAPI |
| NEO/Solar | Daily | NASA |
| Countries | Weekly | REST Countries |

---

## 💰 Operating Costs

**Current (Free Tier):**
- APIs: $0/month (free tier limits)
- Hosting: $0/month (Streamlit Community)
- GitHub Actions: $0/month (2,000 minutes free)
- **Total: $0/month**

**With Planned Expansions:**
- Market data API: $15-50/month (for 30+ stocks)
- Enhanced weather: $20-50/month (marine data)
- Country data: Free (World Bank/IMF)
- **Estimated: $35-100/month**

---

## 🚀 Quick Start

### View Dashboard
Visit: [hermes-intelligence.streamlit.app](https://hermes-intelligence.streamlit.app)

### Run Locally
```bash
# Clone repository
git clone https://github.com/DeepmountainHackz/hermes.git
cd hermes

# Install dependencies
pip install -r requirements.txt

# Set up API keys in .env file
cp .env.example .env
# Edit .env with your API keys

# Run dashboard
streamlit run hermes_dashboard.py
```

### Manual Data Collection
```bash
# Run all collectors
python scripts/test_all_collectors.py

# Or run individually
python services/space/fetch_iss_data.py
python services/markets/fetch_market_data.py
# etc.
```

---

## 🔑 API Keys Required

1. **NASA API** (free): https://api.nasa.gov
2. **OpenWeather API** (free): https://openweathermap.org/api
3. **NewsAPI** (free): https://newsapi.org
4. **Alpha Vantage** (free): https://www.alphavantage.co

Add to `.env` file:
```bash
NASA_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
ALPHA_VANTAGE_KEY=your_key_here
```

---

## 📊 Data Storage

**Database:** SQLite (`hermes.db`)

**Tables:**
- `stocks` - Market data
- `iss_positions` - ISS tracking
- `near_earth_objects` - NEO data
- `solar_flares` - Solar activity
- `weather` - Global weather
- `news` - News articles
- `countries` - Country profiles

**Size:** ~10MB (grows with historical data)

---

## 🤝 Development Philosophy

**Principles:**
1. **Automation First** - No manual data collection
2. **Stability Over Features** - Working system beats fancy features
3. **Data Quality** - Reliable sources, validated data
4. **Pragmatic Tools** - AI-augmented development, modern workflows
5. **Real Use Case** - Built for actual investment research

**Approach:**
- Start simple, scale intelligently
- Prove value before investing in complexity
- Free tier until limits require upgrade
- Iterate based on actual usage

---

## 🎯 Success Metrics

**Current:**
- ✅ 7 data sources integrated
- ✅ 100% automation (no manual collection)
- ✅ 99%+ uptime
- ✅ Hourly data refresh
- ✅ 600+ data records collected

**Target (3 months):**
- 15+ data sources
- 30+ stocks tracked
- 50+ countries profiled
- Hurricane tracking operational
- Custom alert system

---

## 📝 Notes

**What this is:**
- Personal investment research tool
- Multi-source data aggregation platform
- Automated intelligence collection system

**What this is NOT:**
- Trading bot (no automated trades)
- Financial advice platform
- Production-grade enterprise system
- Replacement for Bloomberg Terminal

**Development:**
- Built with AI assistance (Claude)
- AI-augmented development approach
- Focus on practical functionality over perfect code

---

## 📜 License

MIT License - See LICENSE file

---

## 🔗 Links

- **Live Dashboard:** https://hermes-intelligence.streamlit.app
- **Repository:** https://github.com/DeepmountainHackz/hermes
- **Issues:** https://github.com/DeepmountainHackz/hermes/issues

---

**Built for investment intelligence. Automated for reliability. Deployed for accessibility.**

*Last Updated: November 2025*
