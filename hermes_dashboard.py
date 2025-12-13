"""
Hermes Intelligence Platform Dashboard v4.3
Custom query interface, portfolio views, mobile-responsive, LLM classification
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
import numpy as np

# Load environment variables (for local development)
load_dotenv()

# City coordinates for weather visualization
CITY_COORDS = {
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Toronto': {'lat': 43.6532, 'lon': -79.3832},
    'Mexico City': {'lat': 19.4326, 'lon': -99.1332},
    'Miami': {'lat': 25.7617, 'lon': -80.1918},
    'Vancouver': {'lat': 49.2827, 'lon': -123.1207},
    'San Francisco': {'lat': 37.7749, 'lon': -122.4194},
    'São Paulo': {'lat': -23.5505, 'lon': -46.6333},
    'Rio de Janeiro': {'lat': -22.9068, 'lon': -43.1729},
    'Buenos Aires': {'lat': -34.6037, 'lon': -58.3816},
    'Lima': {'lat': -12.0464, 'lon': -77.0428},
    'Bogotá': {'lat': 4.7110, 'lon': -74.0721},
    'Santiago': {'lat': -33.4489, 'lon': -70.6693},
    'London': {'lat': 51.5074, 'lon': -0.1278},
    'Paris': {'lat': 48.8566, 'lon': 2.3522},
    'Berlin': {'lat': 52.5200, 'lon': 13.4050},
    'Madrid': {'lat': 40.4168, 'lon': -3.7038},
    'Rome': {'lat': 41.9028, 'lon': 12.4964},
    'Amsterdam': {'lat': 52.3676, 'lon': 4.9041},
    'Moscow': {'lat': 55.7558, 'lon': 37.6173},
    'Istanbul': {'lat': 41.0082, 'lon': 28.9784},
    'Athens': {'lat': 37.9838, 'lon': 23.7275},
    'Stockholm': {'lat': 59.3293, 'lon': 18.0686},
    'Dubai': {'lat': 25.2048, 'lon': 55.2708},
    'Cairo': {'lat': 30.0444, 'lon': 31.2357},
    'Tel Aviv': {'lat': 32.0853, 'lon': 34.7818},
    'Riyadh': {'lat': 24.7136, 'lon': 46.6753},
    'Johannesburg': {'lat': -26.2041, 'lon': 28.0473},
    'Cape Town': {'lat': -33.9249, 'lon': 18.4241},
    'Nairobi': {'lat': -1.2921, 'lon': 36.8219},
    'Lagos': {'lat': 6.5244, 'lon': 3.3792},
    'Tokyo': {'lat': 35.6762, 'lon': 139.6503},
    'Beijing': {'lat': 39.9042, 'lon': 116.4074},
    'Shanghai': {'lat': 31.2304, 'lon': 121.4737},
    'Hong Kong': {'lat': 22.3193, 'lon': 114.1694},
    'Singapore': {'lat': 1.3521, 'lon': 103.8198},
    'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
    'Delhi': {'lat': 28.7041, 'lon': 77.1025},
    'Bangkok': {'lat': 13.7563, 'lon': 100.5018},
    'Seoul': {'lat': 37.5665, 'lon': 126.9780},
    'Jakarta': {'lat': -6.2088, 'lon': 106.8456},
    'Manila': {'lat': 14.5995, 'lon': 120.9842},
    'Kuala Lumpur': {'lat': 3.1390, 'lon': 101.6869},
    'Taipei': {'lat': 25.0330, 'lon': 121.5654},
    'Sydney': {'lat': -33.8688, 'lon': 151.2093},
    'Melbourne': {'lat': -37.8136, 'lon': 144.9631},
    'Auckland': {'lat': -36.8485, 'lon': 174.7633},
    'Perth': {'lat': -31.9505, 'lon': 115.8605},
    'Brisbane': {'lat': -27.4698, 'lon': 153.0251}
}


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

def get_db_config():
    """Get database configuration from Streamlit secrets or environment variables."""
    if hasattr(st, 'secrets') and 'database' in st.secrets:
        return {
            'host': st.secrets.database.host,
            'port': st.secrets.database.port,
            'dbname': st.secrets.database.name,
            'user': st.secrets.database.user,
            'password': st.secrets.database.password,
        }
    return {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': os.getenv('DATABASE_PORT', '5432'),
        'dbname': os.getenv('DATABASE_NAME', 'hermes'),
        'user': os.getenv('DATABASE_USER', 'postgres'),
        'password': os.getenv('DATABASE_PASSWORD', ''),
    }


def get_db_connection():
    """Get a database connection using psycopg3."""
    config = get_db_config()
    return psycopg.connect(
        host=config['host'],
        port=config['port'],
        dbname=config['dbname'],
        user=config['user'],
        password=config['password'],
        row_factory=dict_row
    )


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Hermes Intelligence Platform",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
CUSTOM_CSS = """
<style>
    /* Color classes for change values */
    .positive { color: #00c853; font-weight: 600; }
    .negative { color: #ff1744; font-weight: 600; }
    .neutral { color: #757575; }

    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }

    /* Alert boxes */
    .alert-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }

    /* Data freshness indicator */
    .freshness-good { color: #4caf50; }
    .freshness-warning { color: #ff9800; }
    .freshness-stale { color: #f44336; }

    /* Tooltip styling */
    .tooltip-icon {
        color: #9e9e9e;
        cursor: help;
        font-size: 0.8rem;
    }

    /* Market status */
    .market-open { background-color: #e8f5e9; color: #2e7d32; padding: 0.25rem 0.75rem; border-radius: 1rem; font-weight: 600; }
    .market-closed { background-color: #ffebee; color: #c62828; padding: 0.25rem 0.75rem; border-radius: 1rem; font-weight: 600; }

    /* Portfolio card */
    .portfolio-card {
        background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
    }
    .portfolio-card h3 { margin: 0 0 0.5rem 0; }
    .portfolio-card .value { font-size: 2rem; font-weight: 700; }

    /* Query builder */
    .query-result {
        background-color: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: monospace;
        overflow-x: auto;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .stMetric { padding: 0.5rem !important; }
        .stMetric label { font-size: 0.75rem !important; }
        .stMetric [data-testid="stMetricValue"] { font-size: 1.25rem !important; }
        .stDataFrame { font-size: 0.75rem !important; }
        [data-testid="stSidebar"] { min-width: 200px !important; }
        .stTabs [data-baseweb="tab"] { padding: 0.5rem !important; font-size: 0.8rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1rem !important; }
    }

    /* Tablet responsive */
    @media (max-width: 1024px) and (min-width: 769px) {
        .stMetric [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
        h1 { font-size: 1.75rem !important; }
    }

    /* LLM classification badge */
    .llm-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .llm-badge.bullish { background-color: #e8f5e9; color: #2e7d32; }
    .llm-badge.bearish { background-color: #ffebee; color: #c62828; }
    .llm-badge.neutral { background-color: #f5f5f5; color: #616161; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=60)
def load_data(query):
    """Load data from PostgreSQL database"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                if not rows:
                    return pd.DataFrame()
                return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


def get_count(table):
    """Safely get count from a table"""
    try:
        df = load_data(f'SELECT COUNT(*) as c FROM {table}')
        if df.empty:
            return 0
        return int(df['c'].iloc[0]) if 'c' in df.columns else int(df.iloc[0, 0])
    except Exception:
        return 0


def table_exists(table_name):
    """Check if a table exists in the database"""
    try:
        df = load_data(f"SELECT 1 FROM {table_name} LIMIT 1")
        return True
    except Exception:
        return False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_change(value):
    """Format a change value with color"""
    if value is None:
        return "N/A"
    return f"+{value:.2f}%" if value > 0 else f"{value:.2f}%"


def format_large_number(value):
    """Format large numbers with K, M, B suffixes"""
    if value is None:
        return "N/A"
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    if value >= 1e6:
        return f"${value/1e6:.2f}M"
    if value >= 1e3:
        return f"${value/1e3:.2f}K"
    return f"${value:.2f}"


def export_csv(df, filename):
    """Create CSV download button"""
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def get_clean_plotly_layout():
    """Standard clean layout for Plotly charts (light mode)"""
    return dict(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#333'),
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)', zerolinecolor='rgba(0,0,0,0.2)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)', zerolinecolor='rgba(0,0,0,0.2)')
    )


def get_data_freshness(table_name):
    """Get data freshness status for a table"""
    try:
        df = load_data(f"SELECT MAX(timestamp) as latest FROM {table_name}")
        if df.empty or df['latest'].iloc[0] is None:
            return None, "stale", "No data"
        latest = pd.to_datetime(df['latest'].iloc[0])
        age = datetime.now() - latest.replace(tzinfo=None)
        hours = age.total_seconds() / 3600

        if hours < 1:
            return latest, "good", f"{int(age.total_seconds() / 60)}m ago"
        elif hours < 6:
            return latest, "good", f"{hours:.1f}h ago"
        elif hours < 24:
            return latest, "warning", f"{hours:.1f}h ago"
        else:
            return latest, "stale", f"{hours / 24:.1f}d ago"
    except Exception:
        return None, "stale", "Error"


def is_market_open():
    """Check if US stock market is open (simplified)"""
    now = datetime.now()
    # NYSE hours: 9:30 AM - 4:00 PM ET, Mon-Fri
    # Simplified: assume ET timezone
    weekday = now.weekday()
    hour = now.hour

    if weekday >= 5:  # Weekend
        return False, "Weekend"
    if hour < 9 or (hour == 9 and now.minute < 30):
        return False, "Pre-market"
    if hour >= 16:
        return False, "After hours"
    return True, "Open"


def create_sparkline(data, color='#1976d2'):
    """Create a mini sparkline chart"""
    if len(data) < 2:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=1.5),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}'
    ))
    fig.update_layout(
        height=40,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False
    )
    return fig


def create_gauge_chart(value, title, min_val=0, max_val=100):
    """Create a gauge chart for sentiment indicators"""
    # Determine color based on value
    if value <= 25:
        color = "#f44336"  # Red - Extreme Fear
    elif value <= 45:
        color = "#ff9800"  # Orange - Fear
    elif value <= 55:
        color = "#9e9e9e"  # Gray - Neutral
    elif value <= 75:
        color = "#8bc34a"  # Light Green - Greed
    else:
        color = "#4caf50"  # Green - Extreme Greed

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 14}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e0e0e0",
            'steps': [
                {'range': [0, 25], 'color': '#ffebee'},
                {'range': [25, 45], 'color': '#fff3e0'},
                {'range': [45, 55], 'color': '#fafafa'},
                {'range': [55, 75], 'color': '#f1f8e9'},
                {'range': [75, 100], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 2},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def info_tooltip(text):
    """Create an info tooltip icon with hover text"""
    return f' <span class="tooltip-icon" title="{text}">ⓘ</span>'


def classify_event_sentiment(title, description=""):
    """
    Simple keyword-based event classification.
    Can be upgraded to use Claude/OpenAI API for more accurate classification.

    Returns: (sentiment, confidence, keywords_found)
    sentiment: 'bullish', 'bearish', or 'neutral'
    """
    text = f"{title} {description}".lower()

    bullish_keywords = [
        'growth', 'surge', 'rally', 'gain', 'profit', 'beat', 'exceed',
        'strong', 'boom', 'record high', 'bullish', 'upturn', 'recovery',
        'expansion', 'hire', 'hiring', 'invest', 'investment', 'deal',
        'partnership', 'breakthrough', 'innovation', 'launch', 'success'
    ]

    bearish_keywords = [
        'fall', 'drop', 'decline', 'loss', 'crash', 'recession', 'bearish',
        'downturn', 'layoff', 'layoffs', 'cut', 'miss', 'disappoint',
        'weak', 'slump', 'fear', 'crisis', 'default', 'bankruptcy',
        'inflation', 'tariff', 'war', 'conflict', 'shutdown', 'risk'
    ]

    bullish_count = sum(1 for kw in bullish_keywords if kw in text)
    bearish_count = sum(1 for kw in bearish_keywords if kw in text)

    bullish_found = [kw for kw in bullish_keywords if kw in text]
    bearish_found = [kw for kw in bearish_keywords if kw in text]

    total = bullish_count + bearish_count
    if total == 0:
        return 'neutral', 0.5, []

    if bullish_count > bearish_count:
        confidence = min(0.5 + (bullish_count - bearish_count) * 0.1, 0.95)
        return 'bullish', confidence, bullish_found[:3]
    elif bearish_count > bullish_count:
        confidence = min(0.5 + (bearish_count - bullish_count) * 0.1, 0.95)
        return 'bearish', confidence, bearish_found[:3]
    else:
        return 'neutral', 0.5, []


def get_sentiment_badge(sentiment):
    """Return HTML badge for sentiment classification"""
    return f'<span class="llm-badge {sentiment}">{sentiment.upper()}</span>'


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("Hermes Intelligence")

# Market Status Banner
market_open, market_status = is_market_open()
status_class = "market-open" if market_open else "market-closed"
st.sidebar.markdown(f'<p><span class="{status_class}">US Markets: {market_status}</span></p>', unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["Overview", "Markets", "Crypto", "Economic Indicators",
     "Market Sentiment", "Weather & Globe", "Space", "Global Events", "News",
     "Time Series", "Portfolio", "Query Builder", "Alerts & Export"]
)

st.sidebar.markdown("---")

# Data Freshness Indicators
st.sidebar.markdown("**Data Freshness**")
freshness_tables = ['stocks', 'crypto', 'weather', 'news']
for table in freshness_tables:
    _, status, age_str = get_data_freshness(table)
    icon = "🟢" if status == "good" else "🟡" if status == "warning" else "🔴"
    st.sidebar.caption(f"{icon} {table.title()}: {age_str}")

st.sidebar.markdown("---")

if st.sidebar.button("Refresh Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.sidebar.caption("v4.3 - Query & Portfolio")


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "Overview":
    st.title("Hermes Intelligence Platform")
    st.markdown("### Real-time Multi-Layer Intelligence Dashboard")

    # Key Highlights Section
    st.markdown("---")
    st.subheader("Key Highlights")

    highlights = []

    # Get key data for highlights
    stocks_df = load_data("""
        SELECT symbol, price, change_percent
        FROM stocks WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
        ORDER BY ABS(change_percent) DESC NULLS LAST LIMIT 1
    """)
    if not stocks_df.empty:
        row = stocks_df.iloc[0]
        change = row.get('change_percent', 0) or 0
        direction = "up" if change > 0 else "down"
        highlights.append(f"**{row['symbol']}** {direction} **{abs(change):.1f}%** at ${row['price']:.2f}")

    crypto_df = load_data("""
        SELECT symbol, price, change_percent_24h
        FROM crypto WHERE timestamp = (SELECT MAX(timestamp) FROM crypto)
        ORDER BY ABS(change_percent_24h) DESC NULLS LAST LIMIT 1
    """)
    if not crypto_df.empty:
        row = crypto_df.iloc[0]
        change = row.get('change_percent_24h', 0) or 0
        direction = "up" if change > 0 else "down"
        highlights.append(f"**{row['symbol']}** {direction} **{abs(change):.1f}%** (24h)")

    # VIX from economics
    vix_df = load_data("""
        SELECT value FROM economic_indicators
        WHERE indicator = 'VIXCLS' AND country = 'USA'
        ORDER BY timestamp DESC LIMIT 1
    """)
    if not vix_df.empty and vix_df['value'].iloc[0]:
        vix = float(vix_df['value'].iloc[0])
        vix_status = "elevated" if vix > 20 else "low" if vix < 15 else "normal"
        highlights.append(f"**VIX** at **{vix:.1f}** ({vix_status} volatility)")

    # Crypto Fear & Greed (quick fetch)
    try:
        import requests
        fng_resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        if fng_resp.status_code == 200:
            fng_data = fng_resp.json()
            if 'data' in fng_data and fng_data['data']:
                fng_val = fng_data['data'][0]['value']
                fng_class = fng_data['data'][0]['value_classification']
                highlights.append(f"Crypto sentiment: **{fng_class}** ({fng_val})")
    except Exception:
        pass

    if highlights:
        cols = st.columns(len(highlights))
        for i, highlight in enumerate(highlights):
            with cols[i]:
                st.info(highlight)
    else:
        st.info("Run collectors to see key highlights")

    st.markdown("---")

    # System Stats
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Stocks", f"{get_count('stocks'):,}")
    with col2:
        st.metric("Crypto", f"{get_count('crypto'):,}")
    with col3:
        st.metric("Forex", f"{get_count('forex'):,}")
    with col4:
        st.metric("Weather", f"{get_count('weather'):,}")
    with col5:
        st.metric("News", f"{get_count('news'):,}")

    st.markdown("---")

    # Market Overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Top Stocks")
        stocks = load_data("""
            SELECT symbol, price, change_percent
            FROM stocks
            WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
            ORDER BY symbol LIMIT 8
        """)
        if not stocks.empty:
            for _, row in stocks.iterrows():
                change = row.get('change_percent', 0) or 0
                color = "positive" if change >= 0 else "negative"
                arrow = "+" if change >= 0 else ""
                st.markdown(f"**{row['symbol']}**: ${row['price']:.2f} "
                           f"<span class='{color}'>{arrow}{change:.2f}%</span>",
                           unsafe_allow_html=True)
        else:
            st.info("No stock data yet")

    with col2:
        st.subheader("Top Crypto")
        crypto = load_data("""
            SELECT symbol, price, change_percent_24h
            FROM crypto
            WHERE timestamp = (SELECT MAX(timestamp) FROM crypto)
            ORDER BY market_cap DESC NULLS LAST LIMIT 8
        """)
        if not crypto.empty:
            for _, row in crypto.iterrows():
                change = row.get('change_percent_24h', 0) or 0
                color = "positive" if change >= 0 else "negative"
                arrow = "+" if change >= 0 else ""
                st.markdown(f"**{row['symbol']}**: ${row['price']:,.2f} "
                           f"<span class='{color}'>{arrow}{change:.2f}%</span>",
                           unsafe_allow_html=True)
        else:
            st.info("No crypto data yet")

    with col3:
        st.subheader("Forex Rates")
        forex = load_data("""
            SELECT pair, rate FROM forex
            WHERE timestamp = (SELECT MAX(timestamp) FROM forex)
            ORDER BY pair LIMIT 8
        """)
        if not forex.empty:
            for _, row in forex.iterrows():
                st.write(f"**{row['pair']}**: {row['rate']:.4f}")
        else:
            st.info("No forex data yet")

    st.markdown("---")

    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("ISS Position")
        iss = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 1")
        if not iss.empty:
            latest = iss.iloc[0]
            st.write(f"Lat: {latest['latitude']:.4f}")
            st.write(f"Lon: {latest['longitude']:.4f}")
        else:
            st.info("No ISS data")

    with col2:
        st.subheader("Weather Sample")
        weather = load_data("""
            SELECT city, temperature FROM weather
            WHERE timestamp = (SELECT MAX(timestamp) FROM weather) LIMIT 4
        """)
        if not weather.empty:
            for _, row in weather.iterrows():
                st.write(f"{row['city']}: {row['temperature']:.1f}C")
        else:
            st.info("No weather data")

    with col3:
        st.subheader("Global Events")
        if table_exists('gdelt_events'):
            event_count = get_count('gdelt_events')
            st.metric("Total Events", event_count)
        else:
            st.info("GDELT not active")

    with col4:
        st.subheader("Latest News")
        news = load_data("SELECT source, title FROM news ORDER BY published_at DESC LIMIT 3")
        if not news.empty:
            for _, row in news.iterrows():
                st.caption(f"[{row['source']}] {row['title'][:40]}...")
        else:
            st.info("No news")


# ============================================================================
# PAGE: MARKETS
# ============================================================================

elif page == "Markets":
    st.title("Market Intelligence")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Stocks", "Commodities", "Forex"])

    with tab1:
        st.subheader("Stock Market Overview")
        stocks_df = load_data("""
            SELECT symbol, name, price, change, change_percent, volume, timestamp
            FROM stocks ORDER BY timestamp DESC, symbol
        """)

        if stocks_df.empty:
            st.warning("No stock data available.")
        else:
            stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp'])
            latest_stocks = stocks_df.groupby('symbol').first().reset_index()

            col1, col2, col3, col4 = st.columns(4)
            gainers = latest_stocks[latest_stocks['change_percent'] > 0]
            losers = latest_stocks[latest_stocks['change_percent'] < 0]

            with col1:
                st.metric("Total Stocks", len(latest_stocks))
            with col2:
                st.metric("Gainers", len(gainers))
            with col3:
                st.metric("Losers", len(losers))
            with col4:
                avg = latest_stocks['change_percent'].mean() if not latest_stocks.empty else 0
                st.metric("Avg Change", f"{avg:.2f}%")

            st.markdown("---")
            # View toggle: Table or Heatmap
            view_mode = st.radio("View Mode", ["Table", "Heatmap"], horizontal=True)

            if view_mode == "Table":
                display_df = latest_stocks[['symbol', 'name', 'price', 'change_percent', 'volume']].copy()
                display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x else "N/A")
                display_df['change_percent'] = display_df['change_percent'].apply(format_change)
                display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}" if x else "N/A")
                display_df.columns = ['Symbol', 'Name', 'Price', 'Change %', 'Volume']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                # Treemap heatmap showing stock performance
                heatmap_df = latest_stocks[['symbol', 'name', 'price', 'change_percent', 'volume']].copy()
                heatmap_df['change_percent'] = heatmap_df['change_percent'].fillna(0)
                heatmap_df['volume'] = heatmap_df['volume'].fillna(1)
                heatmap_df['display_text'] = heatmap_df.apply(
                    lambda r: f"{r['symbol']}<br>${r['price']:.2f}<br>{r['change_percent']:+.2f}%", axis=1
                )

                fig = px.treemap(
                    heatmap_df,
                    path=['symbol'],
                    values='volume',
                    color='change_percent',
                    color_continuous_scale='RdYlGn',
                    color_continuous_midpoint=0,
                    custom_data=['name', 'price', 'change_percent']
                )
                fig.update_traces(
                    textinfo='label+text',
                    texttemplate='<b>%{label}</b><br>$%{customdata[1]:.2f}<br>%{customdata[2]:+.2f}%',
                    hovertemplate='<b>%{customdata[0]}</b><br>Symbol: %{label}<br>Price: $%{customdata[1]:.2f}<br>Change: %{customdata[2]:+.2f}%<extra></extra>'
                )
                fig.update_layout(
                    **get_clean_plotly_layout(),
                    height=500,
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Size represents trading volume. Color shows daily change (green=gain, red=loss).")

    with tab2:
        st.subheader("Commodity Prices")
        commodities_df = load_data("""
            SELECT symbol, name, price, change_percent, unit, timestamp
            FROM commodities ORDER BY timestamp DESC, symbol
        """)

        if commodities_df.empty:
            st.warning("No commodity data available.")
        else:
            commodities_df['timestamp'] = pd.to_datetime(commodities_df['timestamp'])
            latest_commodities = commodities_df.groupby('symbol').first().reset_index()

            cols = st.columns(3)
            for idx, (_, row) in enumerate(latest_commodities.iterrows()):
                with cols[idx % 3]:
                    change = row.get('change_percent', 0) or 0
                    st.metric(
                        label=row['name'] or row['symbol'],
                        value=f"${row['price']:.2f}" if row['price'] else "N/A",
                        delta=format_change(change)
                    )

    with tab3:
        st.subheader("Foreign Exchange Rates")
        forex_df = load_data("""
            SELECT pair, rate, bid, ask, timestamp FROM forex
            ORDER BY timestamp DESC, pair
        """)

        if forex_df.empty:
            st.warning("No forex data available.")
        else:
            forex_df['timestamp'] = pd.to_datetime(forex_df['timestamp'])
            latest_forex = forex_df.groupby('pair').first().reset_index()

            display_forex = latest_forex[['pair', 'rate', 'bid', 'ask']].copy()
            display_forex['rate'] = display_forex['rate'].apply(lambda x: f"{x:.4f}" if x else "N/A")
            display_forex['bid'] = display_forex['bid'].apply(lambda x: f"{x:.4f}" if x else "N/A")
            display_forex['ask'] = display_forex['ask'].apply(lambda x: f"{x:.4f}" if x else "N/A")
            display_forex.columns = ['Pair', 'Rate', 'Bid', 'Ask']
            st.dataframe(display_forex, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: CRYPTO
# ============================================================================

elif page == "Crypto":
    st.title("Cryptocurrency Intelligence")
    st.markdown("---")

    crypto_df = load_data("""
        SELECT symbol, name, price, change_24h, change_percent_24h,
               market_cap, volume_24h, timestamp
        FROM crypto ORDER BY timestamp DESC, market_cap DESC NULLS LAST
    """)

    if crypto_df.empty:
        st.warning("No cryptocurrency data available. Run the crypto collector to populate data.")
    else:
        crypto_df['timestamp'] = pd.to_datetime(crypto_df['timestamp'])
        latest_crypto = crypto_df.groupby('symbol').first().reset_index()

        col1, col2, col3, col4 = st.columns(4)
        total_market_cap = latest_crypto['market_cap'].sum() if 'market_cap' in latest_crypto.columns else 0
        gainers = latest_crypto[latest_crypto['change_percent_24h'] > 0] if 'change_percent_24h' in latest_crypto.columns else pd.DataFrame()
        losers = latest_crypto[latest_crypto['change_percent_24h'] < 0] if 'change_percent_24h' in latest_crypto.columns else pd.DataFrame()

        with col1:
            st.metric("Total Coins", len(latest_crypto))
        with col2:
            st.metric("Total Market Cap", format_large_number(total_market_cap))
        with col3:
            st.metric("Gainers (24h)", len(gainers))
        with col4:
            st.metric("Losers (24h)", len(losers))

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Gainers")
            if not gainers.empty and 'change_percent_24h' in gainers.columns:
                top_gainers = gainers.nlargest(5, 'change_percent_24h')
                for _, row in top_gainers.iterrows():
                    st.markdown(f"**{row['symbol']}**: <span class='positive'>+{row['change_percent_24h']:.2f}%</span>",
                               unsafe_allow_html=True)

        with col2:
            st.subheader("Top Losers")
            if not losers.empty and 'change_percent_24h' in losers.columns:
                top_losers = losers.nsmallest(5, 'change_percent_24h')
                for _, row in top_losers.iterrows():
                    st.markdown(f"**{row['symbol']}**: <span class='negative'>{row['change_percent_24h']:.2f}%</span>",
                               unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("All Cryptocurrencies")
        display_crypto = latest_crypto[['symbol', 'name', 'price', 'change_percent_24h', 'market_cap', 'volume_24h']].copy()
        display_crypto['price'] = display_crypto['price'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
        display_crypto['change_percent_24h'] = display_crypto['change_percent_24h'].apply(format_change)
        display_crypto['market_cap'] = display_crypto['market_cap'].apply(format_large_number)
        display_crypto['volume_24h'] = display_crypto['volume_24h'].apply(format_large_number)
        display_crypto.columns = ['Symbol', 'Name', 'Price', '24h Change', 'Market Cap', '24h Volume']
        st.dataframe(display_crypto, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: ECONOMIC INDICATORS
# ============================================================================

elif page == "Economic Indicators":
    st.title("Economic Indicators")
    st.markdown("---")

    econ_df = load_data("""
        SELECT indicator, country, name, value, unit, timestamp
        FROM economic_indicators ORDER BY timestamp DESC, country, indicator
    """)

    if econ_df.empty:
        st.warning("No economic indicator data available.")
    else:
        econ_df['timestamp'] = pd.to_datetime(econ_df['timestamp'])
        countries = sorted(econ_df['country'].unique().tolist())

        selected_country = st.selectbox("Select Country", countries)

        if selected_country:
            country_data = econ_df[econ_df['country'] == selected_country]
            latest_country = country_data.groupby('indicator').first().reset_index()

            st.markdown("---")
            st.subheader(f"{selected_country} Economic Indicators")

            cols = st.columns(min(4, len(latest_country)))
            for idx, (_, row) in enumerate(latest_country.iterrows()):
                with cols[idx % len(cols)]:
                    unit_str = f" {row['unit']}" if row.get('unit') else ""
                    st.metric(
                        label=row['name'] or row['indicator'],
                        value=f"{row['value']:.2f}{unit_str}" if row['value'] else "N/A"
                    )

        # Comparison chart
        st.markdown("---")
        st.subheader("Cross-Country Comparison")

        indicator_options = econ_df['name'].unique().tolist()
        selected_indicator = st.selectbox("Select Indicator for Comparison", indicator_options)

        if selected_indicator:
            comparison_data = econ_df[econ_df['name'] == selected_indicator]
            latest_comparison = comparison_data.groupby('country').first().reset_index()

            if not latest_comparison.empty:
                fig = px.bar(latest_comparison, x='country', y='value',
                            title=f"{selected_indicator} by Country",
                            color='value', color_continuous_scale='Blues')
                fig.update_layout(**get_clean_plotly_layout(), height=400)
                st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: MARKET SENTIMENT
# ============================================================================

elif page == "Market Sentiment":
    st.title("Market Sentiment & Risk Indicators")
    st.markdown("---")

    # Load economic data to get VIX and yield curve
    econ_df = load_data("""
        SELECT indicator, name, value, timestamp
        FROM economic_indicators
        WHERE country = 'USA'
        ORDER BY timestamp DESC
    """)

    # Extract VIX and Yield Curve values
    vix_value = None
    yield_spread = None
    treasury_data = {}

    if not econ_df.empty:
        econ_df['timestamp'] = pd.to_datetime(econ_df['timestamp'])
        latest_econ = econ_df.groupby('indicator').first().reset_index()

        for _, row in latest_econ.iterrows():
            if row['indicator'] == 'VIXCLS':
                vix_value = float(row['value']) if row['value'] else None
            elif row['indicator'] == 'T10Y2Y':
                yield_spread = float(row['value']) if row['value'] else None
            elif row['indicator'] in ['DGS3MO', 'DGS2', 'DGS5', 'DGS10', 'DGS30']:
                treasury_data[row['indicator']] = float(row['value']) if row['value'] else None

    # ---- Fear & Greed Section ----
    st.subheader("Fear & Greed Index")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Crypto Fear & Greed")
        # Fetch crypto fear & greed from API
        try:
            import requests
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
            if fng_response.status_code == 200:
                fng_data = fng_response.json()
                if 'data' in fng_data and fng_data['data']:
                    crypto_fng = int(fng_data['data'][0]['value'])
                    crypto_class = fng_data['data'][0]['value_classification']

                    # Color based on value
                    if crypto_fng <= 25:
                        fng_color = "#ff4757"
                    elif crypto_fng <= 45:
                        fng_color = "#ff6b81"
                    elif crypto_fng <= 55:
                        fng_color = "#ffa502"
                    elif crypto_fng <= 75:
                        fng_color = "#7bed9f"
                    else:
                        fng_color = "#2ed573"

                    st.metric("Crypto F&G Index", crypto_fng, crypto_class)
                    st.progress(crypto_fng / 100)
                else:
                    st.info("Crypto F&G data unavailable")
            else:
                st.info("Crypto F&G API unavailable")
        except Exception:
            st.info("Could not fetch Crypto F&G data")

    with col2:
        st.markdown("##### Stock Market Sentiment")
        if vix_value is not None and yield_spread is not None:
            # Calculate stock fear & greed
            if vix_value <= 12:
                vix_score = 100
            elif vix_value >= 35:
                vix_score = 0
            else:
                vix_score = 100 - ((vix_value - 12) / 23 * 100)

            if yield_spread >= 1.0:
                yield_score = 100
            elif yield_spread <= -0.5:
                yield_score = 0
            else:
                yield_score = ((yield_spread + 0.5) / 1.5) * 100

            stock_fng = int((vix_score * 0.6) + (yield_score * 0.4))
            stock_fng = max(0, min(100, stock_fng))

            if stock_fng <= 25:
                stock_class = "Extreme Fear"
            elif stock_fng <= 45:
                stock_class = "Fear"
            elif stock_fng <= 55:
                stock_class = "Neutral"
            elif stock_fng <= 75:
                stock_class = "Greed"
            else:
                stock_class = "Extreme Greed"

            st.metric("Stock F&G Index", stock_fng, stock_class)
            st.progress(stock_fng / 100)
        else:
            st.info("Waiting for VIX and Yield data (run collector)")

    st.markdown("---")

    # ---- VIX & Yield Curve Section ----
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("VIX Volatility Index")
        if vix_value is not None:
            # VIX interpretation
            if vix_value < 15:
                vix_status = "Low Volatility (Complacency)"
                vix_color = "#2ed573"
            elif vix_value < 20:
                vix_status = "Normal Volatility"
                vix_color = "#7bed9f"
            elif vix_value < 25:
                vix_status = "Elevated Volatility"
                vix_color = "#ffa502"
            elif vix_value < 35:
                vix_status = "High Volatility"
                vix_color = "#ff6b81"
            else:
                vix_status = "Extreme Fear"
                vix_color = "#ff4757"

            st.metric("VIX Level", f"{vix_value:.2f}", vix_status)
        else:
            st.info("VIX data not yet collected")

    with col2:
        st.subheader("Yield Curve (10Y-2Y Spread)")
        if yield_spread is not None:
            if yield_spread > 0.5:
                curve_status = "Steep (Normal)"
                curve_color = "#2ed573"
            elif yield_spread > 0:
                curve_status = "Normal"
                curve_color = "#7bed9f"
            elif yield_spread > -0.25:
                curve_status = "Flat (Caution)"
                curve_color = "#ffa502"
            else:
                curve_status = "Inverted (Recession Signal)"
                curve_color = "#ff4757"

            st.metric("10Y-2Y Spread", f"{yield_spread:.2f}%", curve_status)
        else:
            st.info("Yield curve data not yet collected")

    st.markdown("---")

    # ---- Treasury Yield Curve Chart ----
    st.subheader("Treasury Yield Curve")
    if treasury_data:
        maturities = ['3M', '2Y', '5Y', '10Y', '30Y']
        maturity_map = {'DGS3MO': '3M', 'DGS2': '2Y', 'DGS5': '5Y', 'DGS10': '10Y', 'DGS30': '30Y'}
        yields = []
        labels = []

        for series, label in maturity_map.items():
            if series in treasury_data and treasury_data[series] is not None:
                yields.append(treasury_data[series])
                labels.append(label)

        if yields:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=labels,
                y=yields,
                mode='lines+markers',
                name='Treasury Yields',
                line=dict(color='#3498db', width=3),
                marker=dict(size=10)
            ))
            fig.update_layout(
                title="US Treasury Yield Curve",
                xaxis_title="Maturity",
                yaxis_title="Yield (%)",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Treasury yield data not yet collected. Run the economics collector.")

    st.markdown("---")

    # ---- Cross-Asset Correlation Matrix ----
    st.subheader("Cross-Asset Correlation Matrix")

    # Load various asset data for correlation
    stocks_df = load_data("SELECT symbol, price, timestamp FROM stocks ORDER BY timestamp")
    crypto_df = load_data("SELECT symbol, price, timestamp FROM crypto ORDER BY timestamp")
    commodities_df = load_data("SELECT symbol, price, timestamp FROM commodities ORDER BY timestamp")

    # Build correlation data
    corr_assets = {}

    if not stocks_df.empty:
        stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp']).dt.date
        for symbol in ['AAPL', 'GOOGL', 'MSFT']:
            sym_data = stocks_df[stocks_df['symbol'] == symbol]
            if not sym_data.empty:
                corr_assets[symbol] = sym_data.groupby('timestamp')['price'].first()

    if not crypto_df.empty:
        crypto_df['timestamp'] = pd.to_datetime(crypto_df['timestamp']).dt.date
        for symbol in ['BTC', 'ETH']:
            sym_data = crypto_df[crypto_df['symbol'] == symbol]
            if not sym_data.empty:
                corr_assets[symbol] = sym_data.groupby('timestamp')['price'].first()

    if not commodities_df.empty:
        commodities_df['timestamp'] = pd.to_datetime(commodities_df['timestamp']).dt.date
        for symbol in ['CRUDE_OIL', 'GOLD']:
            sym_data = commodities_df[commodities_df['symbol'] == symbol]
            if not sym_data.empty:
                corr_assets[symbol] = sym_data.groupby('timestamp')['price'].first()

    if len(corr_assets) >= 3:
        corr_df = pd.DataFrame(corr_assets)
        corr_matrix = corr_df.pct_change().dropna().corr()

        if not corr_matrix.empty:
            fig = px.imshow(
                corr_matrix,
                text_auto='.2f',
                color_continuous_scale='RdYlGn',
                zmin=-1, zmax=1,
                title="Asset Correlation Matrix (Price Returns)"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data points for correlation calculation")
    else:
        st.info("Need more asset data for correlation matrix. Run collectors to populate data.")

    st.markdown("---")

    # ---- Central Bank Calendar ----
    st.subheader("Central Bank Meeting Calendar")

    # Central Bank meetings (2024-2025)
    from datetime import timedelta

    central_banks = {
        'Federal Reserve (FOMC)': {
            'country': 'USA', 'currency': 'USD',
            'meetings': ['2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
                        '2025-07-30', '2025-09-17', '2025-11-05', '2025-12-17']
        },
        'European Central Bank (ECB)': {
            'country': 'EU', 'currency': 'EUR',
            'meetings': ['2025-01-30', '2025-03-06', '2025-04-17', '2025-06-05',
                        '2025-07-17', '2025-09-11', '2025-10-30', '2025-12-18']
        },
        'Bank of England (BoE)': {
            'country': 'UK', 'currency': 'GBP',
            'meetings': ['2025-02-06', '2025-03-20', '2025-05-08', '2025-06-19',
                        '2025-08-07', '2025-09-18', '2025-11-06', '2025-12-18']
        },
        'Bank of Japan (BoJ)': {
            'country': 'Japan', 'currency': 'JPY',
            'meetings': ['2025-01-24', '2025-03-14', '2025-05-01', '2025-06-17',
                        '2025-07-31', '2025-09-19', '2025-10-31', '2025-12-19']
        },
        'Bank of Canada (BoC)': {
            'country': 'Canada', 'currency': 'CAD',
            'meetings': ['2025-01-29', '2025-03-12', '2025-04-16', '2025-06-04',
                        '2025-07-30', '2025-09-03', '2025-10-29', '2025-12-10']
        }
    }

    today = datetime.now().date()
    upcoming_meetings = []

    for bank, info in central_banks.items():
        for meeting_str in info['meetings']:
            meeting_date = datetime.strptime(meeting_str, '%Y-%m-%d').date()
            if meeting_date >= today:
                days_until = (meeting_date - today).days
                if days_until <= 60:  # Show next 60 days
                    upcoming_meetings.append({
                        'Bank': bank,
                        'Country': info['country'],
                        'Currency': info['currency'],
                        'Date': meeting_date.strftime('%b %d, %Y'),
                        'Days Until': days_until
                    })

    upcoming_meetings.sort(key=lambda x: x['Days Until'])

    if upcoming_meetings:
        meetings_df = pd.DataFrame(upcoming_meetings[:10])  # Show top 10
        st.dataframe(meetings_df, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming central bank meetings in the next 60 days")


# ============================================================================
# PAGE: WEATHER & 3D GLOBE
# ============================================================================

elif page == "Weather & Globe":
    st.title("Weather & 3D Globe Visualization")
    st.markdown("---")

    weather_df = load_data("""
        SELECT city, country, temperature, feels_like, humidity, description, timestamp
        FROM weather ORDER BY timestamp DESC
    """)

    if weather_df.empty:
        st.warning("No weather data available.")
    else:
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
        weather_df['temperature'] = pd.to_numeric(weather_df['temperature'], errors='coerce')
        latest_weather = weather_df.groupby('city').first().reset_index()
        latest_weather = latest_weather[latest_weather['temperature'].notna()]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cities Tracked", len(latest_weather))
        with col2:
            if not latest_weather.empty:
                hottest = latest_weather.loc[latest_weather['temperature'].idxmax()]
                st.metric("Hottest", f"{hottest['city']}", f"{hottest['temperature']:.1f}C")
        with col3:
            if not latest_weather.empty:
                coldest = latest_weather.loc[latest_weather['temperature'].idxmin()]
                st.metric("Coldest", f"{coldest['city']}", f"{coldest['temperature']:.1f}C")
        with col4:
            avg_temp = latest_weather['temperature'].mean()
            st.metric("Global Average", f"{avg_temp:.1f}C")

        st.markdown("---")

        # Add coordinates
        latest_weather['lat'] = latest_weather['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lat'))
        latest_weather['lon'] = latest_weather['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lon'))
        map_data = latest_weather[latest_weather['lat'].notna()].copy()

        # 3D Globe visualization
        st.subheader("Interactive 3D Globe")

        # Globe controls
        col1, col2 = st.columns(2)
        with col1:
            projection = st.selectbox("Projection", ["orthographic", "natural earth", "equirectangular"])
        with col2:
            rotation = st.slider("Rotation (Longitude)", -180, 180, 0)

        if not map_data.empty:
            fig = go.Figure()

            # Add weather points
            fig.add_trace(go.Scattergeo(
                lon=map_data['lon'],
                lat=map_data['lat'],
                text=map_data.apply(lambda r: f"<b>{r['city']}</b><br>Temp: {r['temperature']:.1f}C<br>{r['description']}", axis=1),
                mode='markers',
                marker=dict(
                    size=map_data['temperature'].apply(lambda x: max(abs(x) / 3 + 8, 6)),
                    color=map_data['temperature'],
                    colorscale='RdYlBu_r',
                    cmin=-10,
                    cmax=40,
                    colorbar=dict(title="Temp (C)", tickfont=dict(color='#333'), titlefont=dict(color='#333')),
                    line=dict(width=1, color='white')
                ),
                hoverinfo='text'
            ))

            # 3D Globe projection (light mode)
            fig.update_geos(
                projection_type=projection.replace(" ", ""),
                projection_rotation_lon=rotation,
                showland=True,
                landcolor='rgb(229, 229, 229)',
                showocean=True,
                oceancolor='rgb(173, 216, 230)',
                showlakes=True,
                lakecolor='rgb(135, 206, 250)',
                showcoastlines=True,
                coastlinecolor='rgb(100, 100, 100)',
                showcountries=True,
                countrycolor='rgb(150, 150, 150)',
                showframe=False,
                bgcolor='white'
            )

            fig.update_layout(
                height=600,
                paper_bgcolor='white',
                geo=dict(bgcolor='white'),
                margin=dict(l=0, r=0, t=0, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: SPACE
# ============================================================================

elif page == "Space":
    st.title("Space Intelligence")
    st.markdown("---")

    st.subheader("International Space Station")
    iss_df = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 50")

    if not iss_df.empty:
        latest = iss_df.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Latitude", f"{latest['latitude']:.4f}")
        with col2:
            st.metric("Longitude", f"{latest['longitude']:.4f}")
        with col3:
            st.metric("Altitude", f"{latest['altitude']:.2f} km")
        with col4:
            st.metric("Velocity", f"{latest['velocity']:,.0f} km/h")

    st.markdown("---")

    st.subheader("Near-Earth Objects")
    neo_df = load_data("""
        SELECT name, date, estimated_diameter_max, relative_velocity,
               miss_distance, is_potentially_hazardous
        FROM near_earth_objects WHERE date >= CURRENT_DATE - 7
        ORDER BY date DESC LIMIT 20
    """)

    if not neo_df.empty:
        neo_df['date'] = pd.to_datetime(neo_df['date'])
        neo_df['estimated_diameter_max'] = pd.to_numeric(neo_df['estimated_diameter_max'], errors='coerce')
        neo_df['relative_velocity'] = pd.to_numeric(neo_df['relative_velocity'], errors='coerce')

        display_neo = neo_df.copy()
        display_neo['Hazardous'] = display_neo['is_potentially_hazardous'].apply(lambda x: 'YES' if x else 'No')
        display_neo['Diameter'] = display_neo['estimated_diameter_max'].apply(lambda x: f"{x:.0f}m" if pd.notna(x) else "N/A")
        display_neo['Velocity'] = display_neo['relative_velocity'].apply(lambda x: f"{x:,.0f} km/h" if pd.notna(x) else "N/A")
        st.dataframe(display_neo[['name', 'date', 'Diameter', 'Velocity', 'Hazardous']],
                    use_container_width=True, hide_index=True)
    else:
        st.info("No NEO data available.")


# ============================================================================
# PAGE: GLOBAL EVENTS (GDELT)
# ============================================================================

elif page == "Global Events":
    st.title("Global Events & Social Unrest")
    st.markdown("*Powered by GDELT Project*")
    st.markdown("---")

    if not table_exists('gdelt_events'):
        st.warning("GDELT events table not yet created. Run the GDELT collector to populate data.")
    else:
        gdelt_df = load_data("""
            SELECT title, url, source, country, event_type, tone, published_at, timestamp
            FROM gdelt_events ORDER BY timestamp DESC LIMIT 200
        """)

        if gdelt_df.empty:
            st.info("No GDELT events collected yet. Run the collector to fetch global events.")
        else:
            gdelt_df['timestamp'] = pd.to_datetime(gdelt_df['timestamp'])
            gdelt_df['tone'] = pd.to_numeric(gdelt_df['tone'], errors='coerce')

            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Events", len(gdelt_df))
            with col2:
                avg_tone = gdelt_df['tone'].mean()
                tone_label = "Negative" if avg_tone < -2 else "Neutral" if avg_tone < 2 else "Positive"
                st.metric("Avg Sentiment", f"{avg_tone:.2f}", tone_label)
            with col3:
                countries = gdelt_df['country'].nunique()
                st.metric("Countries", countries)
            with col4:
                protests = len(gdelt_df[gdelt_df['event_type'].isin(['PROTEST', 'RIOT', 'STRIKE'])])
                st.metric("Unrest Events", protests)

            st.markdown("---")

            # Event type filter
            tab1, tab2, tab3 = st.tabs(["All Events", "By Country", "Sentiment Analysis"])

            with tab1:
                event_types = ['All'] + gdelt_df['event_type'].unique().tolist()
                selected_type = st.selectbox("Filter by Event Type", event_types)

                filtered = gdelt_df if selected_type == 'All' else gdelt_df[gdelt_df['event_type'] == selected_type]

                for _, event in filtered.head(20).iterrows():
                    tone = event.get('tone', 0) or 0
                    tone_color = 'negative' if tone < -2 else 'positive' if tone > 2 else 'neutral'
                    st.markdown(f"""
                    **{event['title'][:100]}...**
                    <span class='{tone_color}'>Tone: {tone:.2f}</span> |
                    {event['country']} | {event['event_type']} | {event['source']}
                    """, unsafe_allow_html=True)
                    st.markdown("---")

            with tab2:
                country_counts = gdelt_df['country'].value_counts().head(15)
                fig = px.bar(x=country_counts.index, y=country_counts.values,
                            title="Events by Country", labels={'x': 'Country', 'y': 'Event Count'})
                fig.update_layout(**get_clean_plotly_layout(), height=400)
                st.plotly_chart(fig, use_container_width=True)

            with tab3:
                # Sentiment by country
                country_tone = gdelt_df.groupby('country')['tone'].mean().sort_values()
                fig = px.bar(x=country_tone.values, y=country_tone.index, orientation='h',
                            title="Average Sentiment by Country (Negative = Unrest)",
                            color=country_tone.values, color_continuous_scale='RdYlGn')
                fig.update_layout(**get_clean_plotly_layout(), height=500)
                st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: NEWS
# ============================================================================

elif page == "News":
    st.title("News Intelligence")
    st.markdown("---")

    news_df = load_data("""
        SELECT title, source, url, description, published_at
        FROM news ORDER BY published_at DESC LIMIT 50
    """)

    if news_df.empty:
        st.warning("No news data available.")
    else:
        col1, col2 = st.columns([2, 1])
        with col1:
            sources = ['All'] + sorted(news_df['source'].dropna().unique().tolist())
            selected_source = st.selectbox("Filter by Source", sources)
        with col2:
            show_sentiment = st.checkbox("Show AI Sentiment", value=True)

        filtered = news_df if selected_source == 'All' else news_df[news_df['source'] == selected_source]

        # Sentiment summary if enabled
        if show_sentiment:
            bullish_count = 0
            bearish_count = 0
            neutral_count = 0
            for _, article in filtered.iterrows():
                sentiment, _, _ = classify_event_sentiment(
                    article.get('title', ''),
                    article.get('description', '')
                )
                if sentiment == 'bullish':
                    bullish_count += 1
                elif sentiment == 'bearish':
                    bearish_count += 1
                else:
                    neutral_count += 1

            scol1, scol2, scol3 = st.columns(3)
            with scol1:
                st.metric("Bullish", bullish_count, delta=None)
            with scol2:
                st.metric("Bearish", bearish_count, delta=None)
            with scol3:
                st.metric("Neutral", neutral_count, delta=None)

        st.write(f"**Showing {len(filtered)} articles**")
        st.markdown("---")

        for _, article in filtered.iterrows():
            title = article['title'] or 'Untitled'

            # Add sentiment badge if enabled
            if show_sentiment:
                sentiment, confidence, keywords = classify_event_sentiment(
                    title,
                    article.get('description', '')
                )
                badge = get_sentiment_badge(sentiment)
                st.markdown(f"### {title} {badge}", unsafe_allow_html=True)
                if keywords:
                    st.caption(f"Keywords: {', '.join(keywords)} ({confidence:.0%} confidence)")
            else:
                st.markdown(f"### {title}")

            if article.get('description'):
                st.write(article['description'][:300] + "..." if len(str(article['description'])) > 300 else article['description'])
            col1, col2 = st.columns([3, 1])
            with col1:
                if article.get('url'):
                    st.markdown(f"[Read full article]({article['url']})")
            with col2:
                st.caption(f"{article['source']} | {str(article['published_at'])[:16]}")
            st.markdown("---")


# ============================================================================
# PAGE: TIME SERIES ANALYSIS
# ============================================================================

elif page == "Time Series":
    st.title("Time Series Analysis")
    st.markdown("*Historical trends and pattern analysis*")
    st.markdown("---")

    analysis_type = st.selectbox("Select Data Type", ["Stocks", "Crypto", "Economic Indicators", "Weather"])

    if analysis_type == "Stocks":
        stocks_df = load_data("""
            SELECT symbol, price, change_percent, timestamp
            FROM stocks ORDER BY timestamp DESC
        """)

        if stocks_df.empty:
            st.warning("No stock data for time series analysis.")
        else:
            stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp'])
            symbols = stocks_df['symbol'].unique().tolist()
            selected_symbol = st.selectbox("Select Stock", symbols)

            if selected_symbol:
                symbol_data = stocks_df[stocks_df['symbol'] == selected_symbol].sort_values('timestamp')

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=symbol_data['timestamp'],
                    y=symbol_data['price'],
                    mode='lines+markers',
                    name=selected_symbol,
                    line=dict(color='#00d26a', width=2)
                ))
                fig.update_layout(
                    title=f"{selected_symbol} Price History",
                    **get_clean_plotly_layout(),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current", f"${symbol_data['price'].iloc[0]:.2f}")
                with col2:
                    st.metric("High", f"${symbol_data['price'].max():.2f}")
                with col3:
                    st.metric("Low", f"${symbol_data['price'].min():.2f}")
                with col4:
                    st.metric("Avg", f"${symbol_data['price'].mean():.2f}")

    elif analysis_type == "Crypto":
        crypto_df = load_data("""
            SELECT symbol, price, change_percent_24h, market_cap, timestamp
            FROM crypto ORDER BY timestamp DESC
        """)

        if crypto_df.empty:
            st.warning("No crypto data for time series analysis.")
        else:
            crypto_df['timestamp'] = pd.to_datetime(crypto_df['timestamp'])
            symbols = crypto_df['symbol'].unique().tolist()
            selected_symbol = st.selectbox("Select Cryptocurrency", symbols)

            if selected_symbol:
                symbol_data = crypto_df[crypto_df['symbol'] == selected_symbol].sort_values('timestamp')

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=symbol_data['timestamp'],
                    y=symbol_data['price'],
                    mode='lines+markers',
                    name=selected_symbol,
                    line=dict(color='#f7931a', width=2)
                ))
                fig.update_layout(
                    title=f"{selected_symbol} Price History",
                    **get_clean_plotly_layout(),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Economic Indicators":
        econ_df = load_data("""
            SELECT country, name, value, timestamp
            FROM economic_indicators ORDER BY timestamp DESC
        """)

        if econ_df.empty:
            st.warning("No economic data for time series analysis.")
        else:
            econ_df['timestamp'] = pd.to_datetime(econ_df['timestamp'])
            indicators = econ_df['name'].unique().tolist()
            selected_indicator = st.selectbox("Select Indicator", indicators)

            if selected_indicator:
                indicator_data = econ_df[econ_df['name'] == selected_indicator]
                countries = indicator_data['country'].unique().tolist()

                fig = go.Figure()
                colors = ['#00d26a', '#ff4757', '#ffa502', '#3498db', '#9b59b6']
                for i, country in enumerate(countries):
                    country_data = indicator_data[indicator_data['country'] == country].sort_values('timestamp')
                    fig.add_trace(go.Scatter(
                        x=country_data['timestamp'],
                        y=country_data['value'],
                        mode='lines+markers',
                        name=country,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))

                fig.update_layout(
                    title=f"{selected_indicator} - Cross Country Comparison",
                    **get_clean_plotly_layout(),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Weather":
        weather_df = load_data("""
            SELECT city, temperature, humidity, timestamp
            FROM weather ORDER BY timestamp DESC
        """)

        if weather_df.empty:
            st.warning("No weather data for time series analysis.")
        else:
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            weather_df['temperature'] = pd.to_numeric(weather_df['temperature'], errors='coerce')
            cities = weather_df['city'].unique().tolist()
            selected_cities = st.multiselect("Select Cities", cities, default=cities[:3])

            if selected_cities:
                fig = go.Figure()
                colors = ['#00d26a', '#ff4757', '#ffa502', '#3498db', '#9b59b6', '#e74c3c', '#2ecc71']
                for i, city in enumerate(selected_cities):
                    city_data = weather_df[weather_df['city'] == city].sort_values('timestamp')
                    fig.add_trace(go.Scatter(
                        x=city_data['timestamp'],
                        y=city_data['temperature'],
                        mode='lines+markers',
                        name=city,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))

                fig.update_layout(
                    title="Temperature Trends",
                    yaxis_title="Temperature (C)",
                    **get_clean_plotly_layout(),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: PORTFOLIO
# ============================================================================

elif page == "Portfolio":
    st.title("Portfolio Correlation Analysis")
    st.markdown("---")

    st.markdown("""
    Build a custom portfolio and analyze correlations between your holdings.
    Select assets from stocks, crypto, and commodities to see how they move together.
    """)

    # Portfolio builder
    st.subheader("Build Your Portfolio")

    col1, col2, col3 = st.columns(3)

    # Get available assets
    stocks_list = load_data("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
    crypto_list = load_data("SELECT DISTINCT symbol FROM crypto ORDER BY symbol")
    commodities_list = load_data("SELECT DISTINCT symbol FROM commodities ORDER BY symbol")

    with col1:
        st.markdown("##### Stocks")
        selected_stocks = st.multiselect(
            "Select stocks",
            stocks_list['symbol'].tolist() if not stocks_list.empty else [],
            default=['AAPL', 'MSFT'] if not stocks_list.empty else []
        )

    with col2:
        st.markdown("##### Crypto")
        selected_crypto = st.multiselect(
            "Select crypto",
            crypto_list['symbol'].tolist() if not crypto_list.empty else [],
            default=['BTC', 'ETH'] if not crypto_list.empty else []
        )

    with col3:
        st.markdown("##### Commodities")
        selected_commodities = st.multiselect(
            "Select commodities",
            commodities_list['symbol'].tolist() if not commodities_list.empty else [],
            default=[]
        )

    all_selected = selected_stocks + selected_crypto + selected_commodities

    if len(all_selected) >= 2:
        st.markdown("---")
        st.subheader("Portfolio Correlation Matrix")

        # Build portfolio data
        portfolio_data = {}

        # Load stock prices
        if selected_stocks:
            stocks_df = load_data(f"""
                SELECT symbol, price, timestamp FROM stocks
                WHERE symbol IN ({','.join([f"'{s}'" for s in selected_stocks])})
                ORDER BY timestamp
            """)
            if not stocks_df.empty:
                stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp']).dt.date
                for symbol in selected_stocks:
                    sym_data = stocks_df[stocks_df['symbol'] == symbol]
                    if not sym_data.empty:
                        portfolio_data[symbol] = sym_data.groupby('timestamp')['price'].first()

        # Load crypto prices
        if selected_crypto:
            crypto_df = load_data(f"""
                SELECT symbol, price, timestamp FROM crypto
                WHERE symbol IN ({','.join([f"'{s}'" for s in selected_crypto])})
                ORDER BY timestamp
            """)
            if not crypto_df.empty:
                crypto_df['timestamp'] = pd.to_datetime(crypto_df['timestamp']).dt.date
                for symbol in selected_crypto:
                    sym_data = crypto_df[crypto_df['symbol'] == symbol]
                    if not sym_data.empty:
                        portfolio_data[symbol] = sym_data.groupby('timestamp')['price'].first()

        # Load commodity prices
        if selected_commodities:
            commodities_df = load_data(f"""
                SELECT symbol, price, timestamp FROM commodities
                WHERE symbol IN ({','.join([f"'{s}'" for s in selected_commodities])})
                ORDER BY timestamp
            """)
            if not commodities_df.empty:
                commodities_df['timestamp'] = pd.to_datetime(commodities_df['timestamp']).dt.date
                for symbol in selected_commodities:
                    sym_data = commodities_df[commodities_df['symbol'] == symbol]
                    if not sym_data.empty:
                        portfolio_data[symbol] = sym_data.groupby('timestamp')['price'].first()

        if len(portfolio_data) >= 2:
            # Calculate correlations
            portfolio_df = pd.DataFrame(portfolio_data)
            returns_df = portfolio_df.pct_change().dropna()

            if len(returns_df) >= 5:
                corr_matrix = returns_df.corr()

                # Correlation heatmap
                fig = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    color_continuous_scale='RdYlGn',
                    zmin=-1, zmax=1,
                    title="Portfolio Correlation Matrix (Daily Returns)"
                )
                fig.update_layout(**get_clean_plotly_layout(), height=500)
                st.plotly_chart(fig, use_container_width=True)

                # Portfolio statistics
                st.markdown("---")
                st.subheader("Portfolio Statistics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
                    st.metric("Average Correlation", f"{avg_corr:.2f}")
                    if avg_corr > 0.7:
                        st.warning("High correlation - limited diversification")
                    elif avg_corr < 0.3:
                        st.success("Low correlation - good diversification")

                with col2:
                    # Find highest correlation pair
                    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
                    max_corr_idx = np.unravel_index(np.argmax(corr_matrix.where(mask).values), corr_matrix.shape)
                    max_corr = corr_matrix.iloc[max_corr_idx]
                    pair_names = f"{corr_matrix.index[max_corr_idx[0]]} & {corr_matrix.columns[max_corr_idx[1]]}"
                    st.metric("Highest Correlation", f"{max_corr:.2f}")
                    st.caption(pair_names)

                with col3:
                    # Find lowest correlation pair
                    min_corr_idx = np.unravel_index(np.argmin(corr_matrix.where(mask).values), corr_matrix.shape)
                    min_corr = corr_matrix.iloc[min_corr_idx]
                    pair_names = f"{corr_matrix.index[min_corr_idx[0]]} & {corr_matrix.columns[min_corr_idx[1]]}"
                    st.metric("Lowest Correlation", f"{min_corr:.2f}")
                    st.caption(pair_names)

                # Price performance chart
                st.markdown("---")
                st.subheader("Normalized Price Performance")

                normalized_df = portfolio_df.div(portfolio_df.iloc[0]) * 100

                fig = go.Figure()
                colors = px.colors.qualitative.Set2
                for i, col in enumerate(normalized_df.columns):
                    fig.add_trace(go.Scatter(
                        x=normalized_df.index,
                        y=normalized_df[col],
                        mode='lines',
                        name=col,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))

                fig.update_layout(
                    title="Portfolio Performance (Indexed to 100)",
                    yaxis_title="Value (Base = 100)",
                    **get_clean_plotly_layout(),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 5 data points for correlation analysis. Run collectors to gather more data.")
        else:
            st.warning("Need price data for at least 2 assets. Run collectors first.")
    else:
        st.info("Select at least 2 assets to analyze portfolio correlations.")


# ============================================================================
# PAGE: QUERY BUILDER
# ============================================================================

elif page == "Query Builder":
    st.title("Custom Query Builder")
    st.markdown("---")

    st.markdown("""
    Build custom queries to explore your data. Select a table, choose columns,
    add filters, and export results.
    """)

    # Available tables
    available_tables = {
        'stocks': ['symbol', 'name', 'price', 'change', 'change_percent', 'volume', 'timestamp'],
        'crypto': ['symbol', 'name', 'price', 'change_24h', 'change_percent_24h', 'market_cap', 'volume_24h', 'timestamp'],
        'forex': ['pair', 'rate', 'bid', 'ask', 'timestamp'],
        'commodities': ['symbol', 'name', 'price', 'change_percent', 'unit', 'timestamp'],
        'economic_indicators': ['country', 'indicator', 'name', 'value', 'unit', 'timestamp'],
        'weather': ['city', 'temperature', 'humidity', 'description', 'wind_speed', 'timestamp'],
        'news': ['title', 'source', 'url', 'published_at', 'description'],
        'earthquakes': ['location', 'magnitude', 'depth', 'latitude', 'longitude', 'timestamp'],
        'near_earth_objects': ['name', 'date', 'estimated_diameter_max', 'relative_velocity', 'miss_distance', 'is_potentially_hazardous'],
    }

    # Check if GDELT exists
    if table_exists('gdelt_events'):
        available_tables['gdelt_events'] = ['country', 'title', 'event_type', 'tone', 'source', 'url', 'timestamp']

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Query Options")

        selected_table = st.selectbox("Select Table", list(available_tables.keys()))
        available_columns = available_tables[selected_table]

        selected_columns = st.multiselect(
            "Select Columns",
            available_columns,
            default=available_columns[:4]
        )

        # Filters
        st.markdown("**Filters**")

        # Time filter for tables with timestamp
        if 'timestamp' in available_columns or 'published_at' in available_columns or 'date' in available_columns:
            time_col = 'timestamp' if 'timestamp' in available_columns else ('published_at' if 'published_at' in available_columns else 'date')
            time_filter = st.selectbox(
                "Time Range",
                ["All Time", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
            )
        else:
            time_filter = "All Time"
            time_col = None

        # Limit
        limit = st.slider("Row Limit", 10, 1000, 100)

        # Order
        order_col = st.selectbox("Order By", selected_columns if selected_columns else available_columns[:1])
        order_dir = st.radio("Order Direction", ["DESC", "ASC"], horizontal=True)

    with col2:
        st.subheader("Results")

        # Build query
        if selected_columns:
            columns_str = ", ".join(selected_columns)
            query = f"SELECT {columns_str} FROM {selected_table}"

            # Add time filter
            if time_filter != "All Time" and time_col:
                if time_filter == "Last 24 Hours":
                    query += f" WHERE {time_col} >= NOW() - INTERVAL '24 hours'"
                elif time_filter == "Last 7 Days":
                    query += f" WHERE {time_col} >= NOW() - INTERVAL '7 days'"
                elif time_filter == "Last 30 Days":
                    query += f" WHERE {time_col} >= NOW() - INTERVAL '30 days'"
                elif time_filter == "Last 90 Days":
                    query += f" WHERE {time_col} >= NOW() - INTERVAL '90 days'"

            query += f" ORDER BY {order_col} {order_dir} LIMIT {limit}"

            # Show query
            st.markdown("**Generated Query:**")
            st.code(query, language="sql")

            if st.button("Run Query", type="primary"):
                with st.spinner("Executing query..."):
                    try:
                        result_df = load_data(query)
                        if not result_df.empty:
                            st.success(f"Returned {len(result_df)} rows")
                            st.dataframe(result_df, use_container_width=True, hide_index=True)

                            # Export option
                            export_csv(result_df, f"query_{selected_table}")

                            # Basic stats for numeric columns
                            numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
                            if numeric_cols:
                                st.markdown("**Quick Stats:**")
                                st.dataframe(result_df[numeric_cols].describe(), use_container_width=True)
                        else:
                            st.warning("Query returned no results")
                    except Exception as e:
                        st.error(f"Query error: {str(e)}")
        else:
            st.info("Select at least one column to build a query")

    # Quick query templates
    st.markdown("---")
    st.subheader("Quick Query Templates")

    templates = {
        "Top Movers Today": """SELECT symbol, name, price, change_percent
FROM stocks
WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
ORDER BY ABS(change_percent) DESC NULLS LAST
LIMIT 10""",
        "Crypto 24h Volatility": """SELECT symbol, name, price, change_percent_24h, market_cap
FROM crypto
WHERE timestamp = (SELECT MAX(timestamp) FROM crypto)
ORDER BY ABS(change_percent_24h) DESC NULLS LAST
LIMIT 15""",
        "Economic Indicators by Country": """SELECT country, name, value, unit, timestamp
FROM economic_indicators
WHERE country = 'USA'
ORDER BY timestamp DESC
LIMIT 20""",
        "Recent Earthquakes M5+": """SELECT location, magnitude, depth, timestamp
FROM earthquakes
WHERE magnitude >= 5.0
ORDER BY timestamp DESC
LIMIT 10""",
        "Hazardous NEOs": """SELECT name, date, estimated_diameter_max, miss_distance
FROM near_earth_objects
WHERE is_potentially_hazardous = true
ORDER BY date DESC
LIMIT 10"""
    }

    selected_template = st.selectbox("Select Template", ["-- Choose --"] + list(templates.keys()))

    if selected_template != "-- Choose --":
        template_query = templates[selected_template]
        st.code(template_query, language="sql")

        if st.button("Run Template Query"):
            with st.spinner("Executing..."):
                try:
                    result_df = load_data(template_query)
                    if not result_df.empty:
                        st.success(f"Returned {len(result_df)} rows")
                        st.dataframe(result_df, use_container_width=True, hide_index=True)
                        export_csv(result_df, f"template_{selected_template.lower().replace(' ', '_')}")
                    else:
                        st.warning("No results")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


# ============================================================================
# PAGE: ALERTS & EXPORT
# ============================================================================

elif page == "Alerts & Export":
    st.title("Alerts & Data Export")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Alerts", "Export Data"])

    with tab1:
        st.subheader("Active Alerts")

        # Stock alerts
        stocks_df = load_data("SELECT * FROM stocks ORDER BY timestamp DESC")
        if not stocks_df.empty:
            stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp'])
            latest_stocks = stocks_df.groupby('symbol').first().reset_index()
            big_movers = latest_stocks[abs(latest_stocks['change_percent']) > 5]
            if not big_movers.empty:
                st.markdown("#### Stock Alerts (>5% change)")
                for _, row in big_movers.iterrows():
                    change = row.get('change_percent', 0)
                    color = "success-box" if change > 0 else "alert-box"
                    st.markdown(f"""<div class='{color}'>
                        <strong>{row['symbol']}</strong>: {format_change(change)} (${row['price']:.2f})
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No significant stock movements (>5%)")

        # Crypto alerts
        crypto_df = load_data("SELECT * FROM crypto ORDER BY timestamp DESC")
        if not crypto_df.empty:
            crypto_df['timestamp'] = pd.to_datetime(crypto_df['timestamp'])
            latest_crypto = crypto_df.groupby('symbol').first().reset_index()
            big_crypto = latest_crypto[abs(latest_crypto['change_percent_24h']) > 10]
            if not big_crypto.empty:
                st.markdown("#### Crypto Alerts (>10% change)")
                for _, row in big_crypto.iterrows():
                    change = row.get('change_percent_24h', 0)
                    color = "success-box" if change > 0 else "alert-box"
                    st.markdown(f"""<div class='{color}'>
                        <strong>{row['symbol']}</strong>: {format_change(change)} (${row['price']:,.2f})
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No significant crypto movements (>10%)")

        # NEO alerts
        neo_df = load_data("""
            SELECT * FROM near_earth_objects
            WHERE is_potentially_hazardous = true AND date >= CURRENT_DATE
        """)
        if not neo_df.empty:
            st.markdown("#### Hazardous NEO Alerts")
            for _, row in neo_df.iterrows():
                st.markdown(f"""<div class='alert-box'>
                    <strong>{row['name']}</strong> - Potentially Hazardous
                    <br>Approach Date: {row['date']}
                </div>""", unsafe_allow_html=True)

        # GDELT unrest alerts
        if table_exists('gdelt_events'):
            unrest_df = load_data("""
                SELECT * FROM gdelt_events
                WHERE event_type IN ('PROTEST', 'RIOT', 'STRIKE') AND tone < -5
                ORDER BY timestamp DESC LIMIT 5
            """)
            if not unrest_df.empty:
                st.markdown("#### Social Unrest Alerts")
                for _, row in unrest_df.iterrows():
                    st.markdown(f"""<div class='warning-box'>
                        <strong>{row['country']}</strong>: {row['title'][:80]}...
                        <br>Tone: {row['tone']:.2f} | Type: {row['event_type']}
                    </div>""", unsafe_allow_html=True)

    with tab2:
        st.subheader("Export Data")

        export_options = {
            "Stocks": "SELECT * FROM stocks ORDER BY timestamp DESC LIMIT 1000",
            "Crypto": "SELECT * FROM crypto ORDER BY timestamp DESC LIMIT 1000",
            "Forex": "SELECT * FROM forex ORDER BY timestamp DESC LIMIT 1000",
            "Commodities": "SELECT * FROM commodities ORDER BY timestamp DESC LIMIT 1000",
            "Weather": "SELECT * FROM weather ORDER BY timestamp DESC LIMIT 1000",
            "News": "SELECT * FROM news ORDER BY published_at DESC LIMIT 500",
            "Economic Indicators": "SELECT * FROM economic_indicators ORDER BY timestamp DESC LIMIT 500",
            "Near-Earth Objects": "SELECT * FROM near_earth_objects ORDER BY date DESC LIMIT 500",
        }

        # Add GDELT if table exists
        if table_exists('gdelt_events'):
            export_options["GDELT Events"] = "SELECT * FROM gdelt_events ORDER BY timestamp DESC LIMIT 1000"

        selected_export = st.selectbox("Select data to export", list(export_options.keys()))

        if st.button("Generate Export"):
            with st.spinner("Loading data..."):
                export_df = load_data(export_options[selected_export])
                if not export_df.empty:
                    st.success(f"Loaded {len(export_df)} records")
                    export_csv(export_df, selected_export.lower().replace(" ", "_"))
                    st.dataframe(export_df.head(10), use_container_width=True)
                else:
                    st.warning("No data available for export")


# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("**Hermes Intelligence Platform**")
st.sidebar.caption("Multi-layer investment intelligence")
