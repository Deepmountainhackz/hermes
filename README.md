# Hermes Intelligence Platform

A multi-layer data intelligence platform that collects, stores, and visualizes real-time data from multiple sources including financial markets, space activity, environmental conditions, and news feeds.

[![Live Demo](https://img.shields.io/badge/Live_Demo-View-blue)](https://hermes-intelligence.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Overview

Hermes is an automated intelligence gathering platform that monitors:

- **Weather data** across 50 major cities worldwide
- **Stock market** prices and trends
- **International Space Station** position tracking
- **Near-Earth objects** and asteroid monitoring
- **Solar activity** affecting Earth
- **News aggregation** from multiple sources

All data is collected automatically, stored in a database, and visualized through an interactive web dashboard featuring a 3D globe interface.

**[View Live Demo](https://hermes-intelligence.streamlit.app/)**

---

## Features

### Global Weather Monitoring
- 50 cities across all continents
- Interactive 3D globe visualization with orthographic projection
- Real-time temperature, humidity, and conditions
- Historical trend analysis
- Color-coded temperature mapping

### Financial Markets
- Stock price tracking (AAPL, MSFT, GOOGL)
- Candlestick charts with OHLC data
- Volume analysis
- Multi-stock performance comparison
- Historical price trends

### Space Tracking
- Live ISS position with altitude and velocity
- Near-Earth object detection and tracking
- Solar flare monitoring (X, M, C class events)
- Interactive orbital maps
- Upcoming asteroid flyby data

### News Aggregation
- Multiple RSS feed sources
- Automated article collection
- Source filtering
- Direct article links
- Publication tracking

### Automation
- GitHub Actions workflow
- Scheduled collection every 3 hours
- Automatic database updates
- Error handling and logging
- Manual trigger capability

---

## Global Coverage

### Cities Monitored (50 Total)

**North America** (8)  
New York, Los Angeles, Chicago, Toronto, Mexico City, Miami, Vancouver, San Francisco

**South America** (6)  
São Paulo, Rio de Janeiro, Buenos Aires, Lima, Bogotá, Santiago

**Europe** (10)  
London, Paris, Berlin, Madrid, Rome, Amsterdam, Moscow, Istanbul, Athens, Stockholm

**Middle East & Africa** (8)  
Dubai, Cairo, Tel Aviv, Riyadh, Johannesburg, Cape Town, Nairobi, Lagos

**Asia** (13)  
Tokyo, Beijing, Shanghai, Hong Kong, Singapore, Mumbai, Delhi, Bangkok, Seoul, Jakarta, Manila, Kuala Lumpur, Taipei

**Oceania** (5)  
Sydney, Melbourne, Auckland, Perth, Brisbane

---

## Quick Start

### For Users

Access the live dashboard at: **https://hermes-intelligence.streamlit.app/**

No installation required.

### For Developers

**Prerequisites:**
- Python 3.11 or higher
- Git

**Installation:**

```bash
# Clone repository
git clone https://github.com/DeepmountainHackz/hermes.git
cd hermes

# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Create .env file with:
OPENWEATHER_API_KEY=your_key
ALPHA_VANTAGE_KEY=your_key
NASA_API_KEY=your_key

# Run dashboard
streamlit run hermes_dashboard.py
```

**API Keys (all free):**
- OpenWeather: https://openweathermap.org/api
- Alpha Vantage: https://www.alphavantage.co/support/#api-key
- NASA: https://api.nasa.gov/

---

## Technical Stack

### Core Technologies
- **Python 3.11+** - Primary language
- **Streamlit** - Dashboard framework
- **Plotly** - Data visualization and 3D rendering
- **SQLite** - Database (PostgreSQL migration planned)
- **GitHub Actions** - Automation and CI/CD

### Data Sources
- **OpenWeather API** - Weather data
- **Alpha Vantage** - Stock market data
- **NASA ISS API** - Station position tracking
- **NASA NEO API** - Near-Earth objects
- **NASA DONKI** - Solar activity
- **RSS Feeds** - News sources

### Geospatial Technology
- **H3 Hexagonal Indexing** - Uber's geospatial system (foundation implemented)
- **Orthographic Projection** - True 3D sphere rendering
- **Interactive WebGL** - Hardware-accelerated graphics

---

## Dashboard Interface

### Overview
Database statistics, latest stock prices, ISS position, weather highlights, recent news

### Markets
Interactive candlestick charts, volume analysis, multi-stock comparison, normalized performance tracking

### Space
Live ISS position map, near-Earth object tracking, NEO size distribution, solar flare history

### Environment
Interactive 3D globe with drag-to-rotate functionality, city selection, temperature trends, humidity comparisons

### News
Article feed with source filtering, distribution charts, direct source links

---

## Data Collection

### Automation
Data collection runs automatically via GitHub Actions:
- Schedule: Every 3 hours
- Manual triggers available
- Error handling included
- Database auto-commit

### Collection Process
1. API requests to all configured sources
2. Data validation and cleaning
3. Database insertion with duplicate prevention
4. Metadata logging
5. Auto-commit to repository

### Rate Limiting
All API calls respect free tier limits:
- OpenWeather: 60 calls/minute
- Alpha Vantage: 5 calls/minute
- NASA: 1000 calls/hour

---

## Project Structure

```
hermes/
├── .github/workflows/          # GitHub Actions automation
├── database/                   # Database setup scripts
├── services/                   # Data collection modules
│   ├── markets/               # Stock data
│   ├── space/                 # ISS, NEO, solar
│   ├── environment/           # Weather data
│   └── social/                # News feeds
├── hermes.db                   # SQLite database
├── hermes_dashboard.py         # Streamlit interface
├── collect_weather_50cities.py # Weather collector
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

---

## Database Schema

**8 Tables:**

1. `stocks` - Market data (date, symbol, OHLC, volume)
2. `iss_positions` - ISS tracking (coordinates, altitude, speed)
3. `near_earth_objects` - Asteroid data (ID, diameter, velocity, hazard status)
4. `solar_flares` - Solar activity (class, timing, location)
5. `weather` - Weather observations (city, temperature, conditions)
6. `news` - Articles (source, title, link, published)
7. `collection_metadata` - System tracking
8. `sqlite_sequence` - Auto-increment tracking

Unique constraints prevent duplicate data across all tables.

---

## Configuration

### Update Schedule

Edit `.github/workflows/hermes_workflow.yml`:

```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

### Add Cities

Edit `collect_weather_50cities.py`:

```python
CITIES = [
    'City Name',
    # Add more cities
]
```

### Add Stocks

Edit `services/markets/fetch_market_data.py`:

```python
symbols = ['AAPL', 'MSFT', 'GOOGL']  # Add symbols
```

---

## Statistics

- **Cities monitored:** 50
- **Continents covered:** All 7
- **Data sources:** 6 APIs
- **Update frequency:** Every 3 hours
- **Database records:** Growing continuously
- **Lines of code:** 3000+
- **Operating cost:** $0 (free tier APIs)

---

## Roadmap

### Completed
- Multi-layer data collection
- 50-city global coverage
- Interactive 3D globe visualization
- Automated collection pipeline
- Real-time ISS tracking
- NEO and solar monitoring
- Stock market integration
- News aggregation
- H3 geospatial foundation

### Planned
- Expand to 100+ cities
- GDELT social unrest tracking
- Demographics overlay
- Event summarization with LLMs
- Notification system
- Historical data playback
- Data export functionality
- Public REST API
- PostgreSQL migration
- Mobile application

---

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request

Areas for contribution:
- Additional cities or data sources
- Performance improvements
- Bug fixes
- Documentation
- Testing coverage
- UI/UX enhancements

---

## Use Cases

**Personal:**
- Track weather in cities of interest
- Monitor financial markets
- Follow space events
- Aggregate news sources

**Professional:**
- Portfolio demonstration
- Full-stack development showcase
- Data engineering example
- Automation reference

**Educational:**
- API integration learning
- Data visualization practice
- Automation workflows
- Geospatial systems study

---

## Performance

- Dashboard load time: 1-2 seconds
- Globe rendering: 60 FPS
- Data freshness: Maximum 3 hours
- Concurrent users: Supported
- Mobile responsive: Yes

---

## License

MIT License - See LICENSE file for details.

Free to use for any purpose, including commercial applications.

---

## Acknowledgments

**Data Providers:**
- OpenWeather - Weather data API
- Alpha Vantage - Financial market data
- NASA - Space tracking and monitoring

**Technology:**
- Streamlit - Dashboard framework
- Plotly - Visualization library
- Uber H3 - Geospatial indexing
- GitHub - Hosting and automation

---

## Contact

Created by [@DeepmountainHackz](https://github.com/DeepmountainHackz)

For issues or questions, please use the GitHub issue tracker.

---

**Built with Python, SQLite, Streamlit, and GitHub Actions**
