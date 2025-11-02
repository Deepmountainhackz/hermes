# 🌐 Hermes Intelligence Platform

A multi-layer data intelligence platform that automatically collects, stores, and visualizes real-time data from multiple sources including financial markets, space activity, environmental conditions, and news feeds.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## 🎯 Overview

Hermes is an automated intelligence gathering platform that collects data from 5+ APIs across 4 distinct layers:

- **📈 Markets Layer** - Stock market data and trends
- **🛰️ Space Layer** - ISS tracking, near-earth objects, solar activity
- **🌦️ Environment Layer** - Multi-city weather monitoring
- **📰 Social Layer** - Real-time news aggregation

All data is stored in a SQLite database, queryable via command-line tools, and visualized through an interactive web dashboard.

---

## ✨ Features

### Data Collection
- ✅ **6 Automated Collectors** - Markets, ISS, NEO, Solar Flares, Weather, News
- ✅ **5+ API Integrations** - Alpha Vantage, NASA, OpenWeatherMap, RSS feeds
- ✅ **Duplicate Prevention** - Smart database constraints prevent redundant data
- ✅ **Error Handling** - Collectors continue even if individual sources fail

### Data Storage
- ✅ **SQLite Database** - Professional schema with 8 tables
- ✅ **300+ Records** - Growing automatically with each collection
- ✅ **Normalized Structure** - Efficient data storage and retrieval
- ✅ **Metadata Tracking** - Collection timestamps and status monitoring

### Data Access
- ✅ **Query Tool** - Command-line data explorer with formatted tables
- ✅ **Interactive Dashboard** - 5-page Streamlit web application
- ✅ **Real-time Visualization** - Charts, maps, and analytics
- ✅ **Multi-page Interface** - Overview, Markets, Space, Environment, News

### Automation
- ✅ **GitHub Actions** - Fully automated daily data collection
- ✅ **Scheduled Runs** - Runs every day at 6:00 AM UTC
- ✅ **Manual Triggers** - Run on-demand from GitHub UI
- ✅ **Auto-commit** - Database updates pushed automatically

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.11+
Git
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/hermes.git
cd hermes
```

2. **Install dependencies**
```bash
pip install requests pandas python-dotenv feedparser streamlit plotly
```

3. **Set up API keys**

Create a `.env` file in the project root:
```env
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
NASA_API_KEY=your_nasa_api_key
OPENWEATHER_KEY=your_openweather_key
```

Get your free API keys:
- Alpha Vantage: https://www.alphavantage.co/support/#api-key
- NASA: https://api.nasa.gov/
- OpenWeatherMap: https://openweathermap.org/api

4. **Initialize the database**
```bash
python database/setup_database.py
```

---

## 💻 Usage

### Collect Data

**Run all collectors:**
```bash
python run_hermes.py
# Select option 7: Run all collectors
```

**Run individual collectors:**
```bash
python services/markets/fetch_market_data.py
python services/space/fetch_iss_data.py
python services/space/fetch_neo_data.py
python services/space/fetch_solar_data.py
python services/environment/fetch_weather_data.py
python services/social/fetch_news_data.py
```

### Query Data

**Explore all data with formatted tables:**
```bash
python query_hermes.py
```

This displays:
- 📊 Database statistics
- 📈 Latest stock prices
- 🛰️ Current ISS position
- ☄️ Upcoming near-earth objects
- ☀️ Recent solar flares
- 🌦️ Current weather
- 📰 Latest news headlines

### Visualize Data

**Launch the interactive dashboard:**
```bash
streamlit run hermes_dashboard.py
```

Then open your browser to `http://localhost:8501`

**Dashboard Pages:**
- 🏠 **Overview** - All data at a glance
- 📈 **Markets** - Stock charts, candlesticks, comparisons
- 🛰️ **Space** - ISS map, NEO tracker, solar activity
- 🌦️ **Environment** - Weather cards and trends
- 📰 **News** - Feed with source filtering

---

## 🤖 Automation

### GitHub Actions Setup

The platform runs automatically every day using GitHub Actions.

**To enable automation:**

1. **Add secrets to GitHub:**
   - Go to: Settings → Secrets and variables → Actions
   - Add: `ALPHA_VANTAGE_KEY`, `NASA_API_KEY`, `OPENWEATHER_KEY`

2. **Workflow runs automatically:**
   - Daily at 6:00 AM UTC
   - Can be triggered manually from Actions tab

3. **Monitor runs:**
   - Check the Actions tab in your repository
   - View logs and collection summaries

**See [AUTOMATION_SETUP.md](AUTOMATION_SETUP.md) for detailed instructions.**

---

## 📁 Project Structure

```
hermes/
├── .github/
│   └── workflows/
│       └── hermes_workflow.yml      # GitHub Actions automation
├── database/
│   └── setup_database.py            # Database initialization
├── services/
│   ├── markets/
│   │   └── fetch_market_data.py     # Stock data collector
│   ├── space/
│   │   ├── fetch_iss_data.py        # ISS tracker
│   │   ├── fetch_neo_data.py        # Near-earth objects
│   │   └── fetch_solar_data.py      # Solar flare monitor
│   ├── environment/
│   │   └── fetch_weather_data.py    # Weather collector
│   └── social/
│       └── fetch_news_data.py       # News aggregator
├── hermes.db                         # SQLite database
├── run_hermes.py                     # Master control system
├── query_hermes.py                   # Data query tool
├── hermes_dashboard.py               # Streamlit dashboard
├── check_schema.py                   # Database schema viewer
├── .env                              # API keys (not in Git)
├── .gitignore                        # Git exclusions
└── README.md                         # This file
```

---

## 🗄️ Database Schema

**8 Tables:**

1. **stocks** - Stock market data
   - Date, symbol, open, high, low, close, volume
   - UNIQUE constraint on (date, symbol)

2. **iss_positions** - ISS tracking data
   - Timestamp, latitude, longitude, altitude, speed

3. **near_earth_objects** - Asteroid data
   - NEO ID, name, diameter, velocity, miss distance, hazard status
   - UNIQUE constraint on (neo_id, date)

4. **solar_flares** - Solar activity
   - Class type, begin/peak/end times, source location
   - UNIQUE constraint on (begin_time, class_type)

5. **weather** - Weather observations
   - City, temperature, humidity, conditions, wind speed

6. **news** - News articles
   - Source, title, summary, link, published date
   - UNIQUE constraint on link

7. **collection_metadata** - System tracking
   - Layer, collector, status, records collected, errors

8. **sqlite_sequence** - Auto-increment tracking

---

## 📊 Data Sources

| Layer | Source | API | Data Type |
|-------|--------|-----|-----------|
| Markets | Alpha Vantage | REST | Stock prices (AAPL, MSFT, GOOGL) |
| Space | NASA ISS | REST | Real-time ISS position |
| Space | NASA NEO | REST | Near-earth object tracking |
| Space | NASA DONKI | REST | Solar flare detection |
| Environment | OpenWeatherMap | REST | Multi-city weather (5 cities) |
| Social | RSS Feeds | RSS | News from 6 sources |

---

## 🎨 Dashboard Preview

**Overview Page:**
- Database statistics
- Latest stock prices
- ISS position
- Current weather
- Recent headlines

**Markets Page:**
- Interactive candlestick charts
- Volume analysis
- Multi-stock comparison
- Normalized performance tracking

**Space Page:**
- Live ISS position map
- Near-earth object table
- NEO size distribution chart
- Solar flare history

**Environment Page:**
- Weather cards for all cities
- Temperature trend charts
- Humidity comparisons
- Real-time conditions

**News Page:**
- Full news feed
- Source filtering
- Article distribution chart
- Direct links to sources

---

## 🔧 Configuration

### Modify Collection Schedule

Edit `.github/workflows/hermes_workflow.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # Daily at 6:00 AM UTC
```

**Examples:**
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * *'` - Daily at midnight
- `'0 12 * * 1'` - Weekly on Mondays at noon

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Add More Stocks

Edit `services/markets/fetch_market_data.py`:

```python
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']  # Add more
```

### Add More Cities

Edit `services/environment/fetch_weather_data.py`:

```python
cities = ['New York', 'London', 'Tokyo', 'Sydney', 'Paris']  # Add more
```

### Add More News Sources

Edit `services/social/fetch_news_data.py`:

```python
rss_feeds = {
    'Source Name': 'https://example.com/rss',
    # Add more RSS feeds
}
```

---

## 📈 Stats

- **Total Code:** 2,500+ lines
- **Python Files:** 10+
- **APIs Integrated:** 5
- **Database Tables:** 8
- **Data Records:** 300+
- **Dashboard Pages:** 5
- **Automated:** ✅ Yes

---

## 🛠️ Development

### Run Tests
```bash
python test_database.py
```

### Check Database Schema
```bash
python check_schema.py
```

### View Database Records
```bash
python query_hermes.py
```

### Manual Data Collection
```bash
python run_hermes.py
```

---

## 🚧 Roadmap

### Completed ✅
- [x] Multi-layer data collection
- [x] SQLite database integration
- [x] Query tool
- [x] Interactive dashboard
- [x] GitHub Actions automation
- [x] Duplicate prevention
- [x] Error handling

### Planned 🔜
- [ ] PostgreSQL migration (production)
- [ ] Email notifications
- [ ] Deploy dashboard to Streamlit Cloud
- [ ] Add more data sources
- [ ] Cross-layer correlation analysis
- [ ] REST API endpoints
- [ ] Unit tests
- [ ] Data export (Excel/PDF)

---

## 🐛 Troubleshooting

**Problem: API key errors**
- Solution: Check `.env` file has all three keys
- Verify keys are valid at provider websites

**Problem: Database locked**
- Solution: Close any programs accessing `hermes.db`
- Restart the dashboard

**Problem: Workflow not appearing**
- Solution: Check `.github/workflows/hermes_workflow.yml` exists
- Verify YAML syntax is correct
- Wait 1 minute and refresh

**Problem: No data collected**
- Solution: Check API keys in GitHub Secrets
- View workflow logs for error messages
- Verify internet connectivity

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Alpha Vantage** - Stock market data
- **NASA** - Space data (ISS, NEO, Solar)
- **OpenWeatherMap** - Weather data
- **RSS Feeds** - News sources

---

## 📧 Contact

Created by [@DeepmountainHackz](https://github.com/DeepmountainHackz)

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you learn about data collection, APIs, and automation!

---

**Built with Python, SQLite, Streamlit, and GitHub Actions** 🚀
