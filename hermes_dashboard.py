"""
Hermes Intelligence Platform Dashboard v5.2
Features: Technical Analysis, Collection Automation, 36+ World Bank indicators,
Real-time market data, Crypto, Forex, Weather, Space, and Global Events tracking.
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

@st.cache_data(ttl=300)  # 5 minute cache for general queries
def load_data(query):
    """Load data from PostgreSQL database with caching"""
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


@st.cache_data(ttl=60)  # 1 minute cache for frequently updated data
def load_realtime_data(query):
    """Load frequently updated data with shorter cache"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                if not rows:
                    return pd.DataFrame()
                return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=600)  # 10 minute cache for slow-changing data
def load_static_data(query):
    """Load slow-changing data with longer cache"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                if not rows:
                    return pd.DataFrame()
                return pd.DataFrame(rows)
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # 1 hour cache for table existence checks
def _check_table_exists(table_name):
    """Internal cached table existence check"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
                return True
    except Exception:
        return False


def table_exists(table_name):
    """Check if a table exists in the database (cached)"""
    return _check_table_exists(table_name)


@st.cache_data(ttl=300)
def get_count(table):
    """Safely get count from a table (cached)"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f'SELECT COUNT(*) FROM {table}')
                result = cur.fetchone()
                return int(result[0]) if result else 0
    except Exception:
        return 0


# Pre-defined optimized queries for common operations
@st.cache_data(ttl=120)
def get_latest_stocks():
    """Get latest stock data - optimized"""
    return load_data("""
        SELECT DISTINCT ON (symbol) symbol, price, change_percent, volume, timestamp
        FROM stocks ORDER BY symbol, timestamp DESC
    """)


@st.cache_data(ttl=120)
def get_latest_crypto():
    """Get latest crypto data - optimized"""
    return load_data("""
        SELECT DISTINCT ON (symbol) symbol, name, price, change_percent_24h, market_cap, volume_24h, timestamp
        FROM crypto ORDER BY symbol, timestamp DESC
    """)


@st.cache_data(ttl=120)
def get_latest_forex():
    """Get latest forex data - optimized"""
    return load_data("""
        SELECT DISTINCT ON (symbol) symbol, rate, change_percent, timestamp
        FROM forex ORDER BY symbol, timestamp DESC
    """)


@st.cache_data(ttl=120)
def get_latest_commodities():
    """Get latest commodities data - optimized"""
    return load_data("""
        SELECT DISTINCT ON (symbol) symbol, name, price, change_percent, category, timestamp
        FROM commodities ORDER BY symbol, timestamp DESC
    """)


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
    # Convert Decimal to float to avoid division errors
    value = float(value)
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

# Initialize page in session state if not exists
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Overview"

# Navigation structure with categories
NAV_STRUCTURE = {
    "📊 Markets": ["Overview", "Markets", "Crypto", "Bond Markets"],
    "📈 Analytics": ["Technical Analysis", "Correlation Analysis", "Risk Metrics", "Time Series"],
    "🌍 Economics": ["Economic Indicators", "Economic Calendar", "Global Development", "Country Profile"],
    "🏭 Commodities": ["Energy & Resources", "Agriculture & Food", "Trade & Shipping"],
    "🌐 Global": ["Demographics", "Debt & Fiscal", "Weather & Globe", "Space"],
    "📰 News & Events": ["News", "Market Sentiment", "Global Events"],
    "🛠️ Tools": ["Portfolio", "Watchlist", "Query Builder", "Alerts & Export", "Collection Status"],
}

# Helper function to create navigation button
def nav_button(page_name, current_page):
    """Create a navigation button that updates session state."""
    is_selected = current_page == page_name
    button_type = "primary" if is_selected else "secondary"

    # Add indicator for current page
    label = f"● {page_name}" if is_selected else page_name

    if st.sidebar.button(label, key=f"nav_{page_name}", use_container_width=True,
                         type=button_type if is_selected else "secondary"):
        st.session_state.current_page = page_name
        st.rerun()

# Render grouped navigation
for category, pages in NAV_STRUCTURE.items():
    # Check if any page in this category is currently selected
    category_has_selection = st.session_state.current_page in pages

    with st.sidebar.expander(category, expanded=category_has_selection):
        for page_name in pages:
            is_selected = st.session_state.current_page == page_name
            prefix = "→ " if is_selected else "   "

            if st.button(
                f"{prefix}{page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()

# Get current page from session state
page = st.session_state.current_page

st.sidebar.markdown("---")

# Data Freshness Indicators (collapsed by default)
with st.sidebar.expander("📡 Data Freshness", expanded=False):
    freshness_tables = ['stocks', 'crypto', 'weather', 'news']
    for table in freshness_tables:
        _, status, age_str = get_data_freshness(table)
        icon = "🟢" if status == "good" else "🟡" if status == "warning" else "🔴"
        st.caption(f"{icon} {table.title()}: {age_str}")

# Refresh button
if st.sidebar.button("🔄 Refresh Data", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.sidebar.caption("v6.4 - Grouped Navigation")


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "Overview":
    st.title("Hermes Intelligence Platform")
    st.markdown("*Real-time Multi-Layer Intelligence Dashboard*")
    st.markdown("---")

    # Bloomberg-style Major Indices Section
    st.subheader("📊 Major Indices")

    # Index ETF mapping for display names
    INDEX_NAMES = {
        'SPY': 'S&P 500',
        'QQQ': 'NASDAQ',
        'DIA': 'DOW',
        'IWM': 'Russell 2K',
        'VGK': 'FTSE EU',
        'EWJ': 'Nikkei'
    }

    indices_df = load_realtime_data("""
        SELECT symbol, price, change_percent
        FROM stocks
        WHERE symbol IN ('SPY', 'QQQ', 'DIA', 'IWM', 'VGK', 'EWJ')
        AND timestamp = (SELECT MAX(timestamp) FROM stocks WHERE symbol IN ('SPY', 'QQQ', 'DIA', 'IWM', 'VGK', 'EWJ'))
        ORDER BY CASE symbol
            WHEN 'SPY' THEN 1 WHEN 'QQQ' THEN 2 WHEN 'DIA' THEN 3
            WHEN 'IWM' THEN 4 WHEN 'VGK' THEN 5 WHEN 'EWJ' THEN 6
        END
    """)

    if not indices_df.empty:
        cols = st.columns(len(indices_df))
        for i, (_, row) in enumerate(indices_df.iterrows()):
            with cols[i]:
                change = row.get('change_percent', 0) or 0
                delta_color = "normal" if change >= 0 else "inverse"
                display_name = INDEX_NAMES.get(row['symbol'], row['symbol'])
                st.metric(
                    display_name,
                    f"${row['price']:.2f}",
                    f"{change:+.2f}%",
                    delta_color=delta_color
                )
    else:
        st.info("No index data available. Run: `python scheduler.py --collector markets`")

    st.markdown("---")

    # Treasury Yield Curve and Key Rates Row
    yield_col, rates_col = st.columns([2, 1])

    with yield_col:
        st.subheader("📈 Treasury Yield Curve")

        # Fetch Treasury yields
        treasury_df = load_data("""
            SELECT indicator, value
            FROM economic_indicators
            WHERE country = 'USA' AND indicator IN ('DGS3MO', 'DGS2', 'DGS5', 'DGS10', 'DGS30')
            AND value IS NOT NULL
            ORDER BY
                CASE indicator
                    WHEN 'DGS3MO' THEN 1
                    WHEN 'DGS2' THEN 2
                    WHEN 'DGS5' THEN 3
                    WHEN 'DGS10' THEN 4
                    WHEN 'DGS30' THEN 5
                END
        """)

        if not treasury_df.empty:
            import plotly.graph_objects as go

            # Map to display names and maturities
            maturity_map = {
                'DGS3MO': ('3M', 0.25),
                'DGS2': ('2Y', 2),
                'DGS5': ('5Y', 5),
                'DGS10': ('10Y', 10),
                'DGS30': ('30Y', 30)
            }

            maturities = []
            yields = []
            labels = []

            for _, row in treasury_df.iterrows():
                indicator = row['indicator']
                if indicator in maturity_map:
                    label, maturity = maturity_map[indicator]
                    maturities.append(maturity)
                    yields.append(float(row['value']))
                    labels.append(label)

            if yields:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=maturities,
                    y=yields,
                    mode='lines+markers',
                    name='Yield Curve',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=10),
                    text=labels,
                    hovertemplate='%{text}: %{y:.2f}%<extra></extra>'
                ))

                # Determine curve status
                spread_10y2y = None
                y_2y = next((y for i, y in zip(treasury_df['indicator'], treasury_df['value']) if i == 'DGS2'), None)
                y_10y = next((y for i, y in zip(treasury_df['indicator'], treasury_df['value']) if i == 'DGS10'), None)
                if y_2y and y_10y:
                    spread_10y2y = float(y_10y) - float(y_2y)
                    curve_status = "🟢 Normal" if spread_10y2y > 0 else "🔴 Inverted (Recession Signal)"
                else:
                    curve_status = ""

                fig.update_layout(
                    title=f"US Treasury Yield Curve {curve_status}",
                    xaxis_title="Maturity (Years)",
                    yaxis_title="Yield (%)",
                    height=250,
                    margin=dict(l=50, r=20, t=40, b=40),
                    xaxis=dict(tickmode='array', tickvals=maturities, ticktext=labels),
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Treasury yield data")
        else:
            st.info("No Treasury data. Run: `python scheduler.py --collector economics`")

    with rates_col:
        st.subheader("📊 Key Rates")

        # Fed Funds Rate
        fed_rate = load_data("""
            SELECT value FROM economic_indicators
            WHERE indicator = 'FEDFUNDS' AND country = 'USA'
            ORDER BY timestamp DESC LIMIT 1
        """)
        if not fed_rate.empty and fed_rate['value'].iloc[0]:
            st.metric("Fed Funds Rate", f"{float(fed_rate['value'].iloc[0]):.2f}%")
        else:
            st.metric("Fed Funds Rate", "N/A")

        # 10Y-2Y Spread (direct from FRED)
        spread_direct = load_data("""
            SELECT value FROM economic_indicators
            WHERE indicator = 'T10Y2Y' AND country = 'USA'
            ORDER BY timestamp DESC LIMIT 1
        """)
        if not spread_direct.empty and spread_direct['value'].iloc[0]:
            spread_val = float(spread_direct['value'].iloc[0])
            spread_color = "normal" if spread_val > 0 else "inverse"
            st.metric("10Y-2Y Spread", f"{spread_val:.2f}%",
                     "Normal" if spread_val > 0 else "Inverted",
                     delta_color=spread_color)
        else:
            st.metric("10Y-2Y Spread", "N/A")

        # DXY Dollar Index (from FRED DTWEXBGS - Trade Weighted Dollar)
        dxy_df = load_data("""
            SELECT value FROM economic_indicators
            WHERE indicator = 'DTWEXBGS' AND country = 'USA'
            ORDER BY timestamp DESC LIMIT 1
        """)
        if not dxy_df.empty and dxy_df['value'].iloc[0]:
            st.metric("USD Index", f"{float(dxy_df['value'].iloc[0]):.2f}")
        else:
            st.metric("USD Index", "N/A", "Run economics")

    st.markdown("---")

    # Key Highlights Section - Top movers and sentiment
    st.subheader("Market Pulse")

    col1, col2, col3, col4 = st.columns(4)

    # Top stock mover
    with col1:
        stocks_df = load_data("""
            SELECT symbol, price, change_percent
            FROM stocks WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
            ORDER BY ABS(change_percent) DESC NULLS LAST LIMIT 1
        """)
        if not stocks_df.empty:
            row = stocks_df.iloc[0]
            change = row.get('change_percent', 0) or 0
            delta_color = "normal" if change >= 0 else "inverse"
            st.metric(f"Top Mover: {row['symbol']}", f"${row['price']:.2f}",
                     f"{change:+.2f}%", delta_color=delta_color)
        else:
            st.metric("Top Stock", "N/A", "Run collector")

    # Top crypto mover
    with col2:
        crypto_df = load_data("""
            SELECT symbol, price, change_percent_24h
            FROM crypto WHERE timestamp = (SELECT MAX(timestamp) FROM crypto)
            ORDER BY ABS(change_percent_24h) DESC NULLS LAST LIMIT 1
        """)
        if not crypto_df.empty:
            row = crypto_df.iloc[0]
            change = row.get('change_percent_24h', 0) or 0
            delta_color = "normal" if change >= 0 else "inverse"
            st.metric(f"Crypto: {row['symbol']}", f"${row['price']:,.2f}",
                     f"{change:+.2f}% (24h)", delta_color=delta_color)
        else:
            st.metric("Top Crypto", "N/A", "Run collector")

    # VIX
    with col3:
        vix_df = load_data("""
            SELECT value FROM economic_indicators
            WHERE indicator = 'VIXCLS' AND country = 'USA'
            ORDER BY timestamp DESC LIMIT 1
        """)
        if not vix_df.empty and vix_df['value'].iloc[0]:
            vix = float(vix_df['value'].iloc[0])
            vix_status = "High" if vix > 25 else "Elevated" if vix > 20 else "Low" if vix < 15 else "Normal"
            st.metric("VIX", f"{vix:.1f}", vix_status)
        else:
            st.metric("VIX", "N/A", "Run economics")

    # Crypto Fear & Greed
    with col4:
        try:
            import requests
            fng_resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=3)
            if fng_resp.status_code == 200:
                fng_data = fng_resp.json()
                if 'data' in fng_data and fng_data['data']:
                    fng_val = int(fng_data['data'][0]['value'])
                    fng_class = fng_data['data'][0]['value_classification']
                    st.metric("Crypto F&G", fng_val, fng_class)
                else:
                    st.metric("Crypto F&G", "N/A", "-")
            else:
                st.metric("Crypto F&G", "N/A", "-")
        except Exception:
            st.metric("Crypto F&G", "N/A", "-")

    st.markdown("---")

    # Bloomberg-style: Gold/Oil Ratio, 52-Week Stats, BTC Dominance
    st.subheader("📊 Market Indicators")

    ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)

    with ind_col1:
        # Gold/Oil Ratio - key indicator of economic sentiment
        gold_df = load_data("""
            SELECT price FROM commodities WHERE symbol = 'GOLD'
            ORDER BY timestamp DESC LIMIT 1
        """)
        oil_df = load_data("""
            SELECT price FROM commodities WHERE symbol = 'WTI'
            ORDER BY timestamp DESC LIMIT 1
        """)
        if not gold_df.empty and not oil_df.empty:
            gold_price = gold_df['price'].iloc[0]
            oil_price = oil_df['price'].iloc[0]
            if gold_price and oil_price and oil_price > 0:
                ratio = gold_price / oil_price
                # Historical average is ~16. High ratio = risk-off
                ratio_status = "Risk-Off" if ratio > 25 else "Risk-On" if ratio < 15 else "Neutral"
                st.metric("Gold/Oil Ratio", f"{ratio:.1f}", ratio_status)
            else:
                st.metric("Gold/Oil Ratio", "N/A", "-")
        else:
            st.metric("Gold/Oil Ratio", "N/A", "Run commodities")

    with ind_col2:
        # S&P 500 52-Week High/Low proximity
        spy_history = load_data("""
            SELECT MIN(price) as low_52w, MAX(price) as high_52w
            FROM stocks WHERE symbol = 'SPY'
            AND timestamp >= NOW() - INTERVAL '365 days'
        """)
        spy_current = load_data("""
            SELECT price FROM stocks WHERE symbol = 'SPY'
            ORDER BY timestamp DESC LIMIT 1
        """)
        if not spy_history.empty and not spy_current.empty:
            high_52 = spy_history['high_52w'].iloc[0]
            low_52 = spy_history['low_52w'].iloc[0]
            current = spy_current['price'].iloc[0]
            if high_52 and low_52 and current:
                range_52 = high_52 - low_52
                if range_52 > 0:
                    pct_of_range = ((current - low_52) / range_52) * 100
                    status = "Near High" if pct_of_range > 90 else "Near Low" if pct_of_range < 10 else f"{pct_of_range:.0f}% range"
                    st.metric("SPY 52W Range", f"${current:.2f}", status)
                else:
                    st.metric("SPY 52W Range", f"${current:.2f}", "-")
            else:
                st.metric("SPY 52W Range", "N/A", "-")
        else:
            st.metric("SPY 52W Range", "N/A", "Need history")

    with ind_col3:
        # BTC Dominance
        btc_df = load_data("""
            SELECT market_cap FROM crypto WHERE symbol = 'BTC'
            ORDER BY timestamp DESC LIMIT 1
        """)
        total_crypto_df = load_data("""
            SELECT SUM(market_cap) as total FROM crypto
            WHERE timestamp = (SELECT MAX(timestamp) FROM crypto)
        """)
        if not btc_df.empty and not total_crypto_df.empty:
            btc_cap = btc_df['market_cap'].iloc[0]
            total_cap = total_crypto_df['total'].iloc[0]
            if btc_cap and total_cap and total_cap > 0:
                dominance = (btc_cap / total_cap) * 100
                status = "High" if dominance > 55 else "Low" if dominance < 40 else "Normal"
                st.metric("BTC Dominance", f"{dominance:.1f}%", status)
            else:
                st.metric("BTC Dominance", "N/A", "-")
        else:
            st.metric("BTC Dominance", "N/A", "Run crypto")

    with ind_col4:
        # Gold Price
        if not gold_df.empty and gold_df['price'].iloc[0]:
            st.metric("Gold", f"${gold_df['price'].iloc[0]:,.0f}/oz")
        else:
            st.metric("Gold", "N/A", "Run commodities")

    st.markdown("---")

    # Data stats row
    st.subheader("Data Overview")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Stocks", f"{get_count('stocks'):,}")
    with col2:
        st.metric("Crypto", f"{get_count('crypto'):,}")
    with col3:
        st.metric("Forex", f"{get_count('forex'):,}")
    with col4:
        st.metric("Commodities", f"{get_count('commodities'):,}")
    with col5:
        st.metric("Weather", f"{get_count('weather'):,}")
    with col6:
        st.metric("News", f"{get_count('news'):,}")

    st.markdown("---")

    # Sector Performance Heatmap
    st.subheader("📊 S&P 500 Sector Performance")

    # Sector ETF mapping
    SECTOR_NAMES = {
        'XLK': 'Tech', 'XLF': 'Financials', 'XLV': 'Healthcare',
        'XLE': 'Energy', 'XLY': 'Cons Disc', 'XLP': 'Cons Staples',
        'XLI': 'Industrials', 'XLB': 'Materials', 'XLU': 'Utilities',
        'XLRE': 'Real Estate', 'XLC': 'Comm Svcs'
    }

    sector_df = load_data("""
        SELECT symbol, price, change_percent
        FROM stocks
        WHERE symbol IN ('XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLI', 'XLB', 'XLU', 'XLRE', 'XLC')
        AND timestamp = (SELECT MAX(timestamp) FROM stocks WHERE symbol IN ('XLK', 'XLF', 'XLV', 'XLE', 'XLY', 'XLP', 'XLI', 'XLB', 'XLU', 'XLRE', 'XLC'))
        ORDER BY change_percent DESC NULLS LAST
    """)

    if not sector_df.empty:
        # Create a heatmap-style display
        sector_cols = st.columns(len(sector_df) if len(sector_df) <= 6 else 6)
        for i, (_, row) in enumerate(sector_df.iterrows()):
            col_idx = i % 6
            with sector_cols[col_idx]:
                change = row.get('change_percent', 0) or 0
                sector_name = SECTOR_NAMES.get(row['symbol'], row['symbol'])

                # Color-code based on performance
                if change >= 1.5:
                    bg_color = "#00a86b"  # Strong green
                elif change >= 0.5:
                    bg_color = "#4caf50"  # Green
                elif change > 0:
                    bg_color = "#8bc34a"  # Light green
                elif change > -0.5:
                    bg_color = "#ff9800"  # Orange
                elif change > -1.5:
                    bg_color = "#f44336"  # Red
                else:
                    bg_color = "#b71c1c"  # Dark red

                st.markdown(
                    f"""<div style="background-color:{bg_color}; padding:10px; border-radius:5px; text-align:center; margin:2px;">
                    <b style="color:white;">{sector_name}</b><br>
                    <span style="color:white; font-size:1.2em;">{change:+.2f}%</span>
                    </div>""",
                    unsafe_allow_html=True
                )

        # Second row if more than 6 sectors
        if len(sector_df) > 6:
            sector_cols2 = st.columns(len(sector_df) - 6)
            for i, (_, row) in enumerate(sector_df.iloc[6:].iterrows()):
                with sector_cols2[i]:
                    change = row.get('change_percent', 0) or 0
                    sector_name = SECTOR_NAMES.get(row['symbol'], row['symbol'])

                    if change >= 1.5:
                        bg_color = "#00a86b"
                    elif change >= 0.5:
                        bg_color = "#4caf50"
                    elif change > 0:
                        bg_color = "#8bc34a"
                    elif change > -0.5:
                        bg_color = "#ff9800"
                    elif change > -1.5:
                        bg_color = "#f44336"
                    else:
                        bg_color = "#b71c1c"

                    st.markdown(
                        f"""<div style="background-color:{bg_color}; padding:10px; border-radius:5px; text-align:center; margin:2px;">
                        <b style="color:white;">{sector_name}</b><br>
                        <span style="color:white; font-size:1.2em;">{change:+.2f}%</span>
                        </div>""",
                        unsafe_allow_html=True
                    )
    else:
        st.info("No sector data. Run: `python scheduler.py --collector markets`")

    st.markdown("---")

    # Three-column market overview
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Stocks")
        stocks = load_data("""
            SELECT symbol, price, change_percent
            FROM stocks
            WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
            ORDER BY ABS(change_percent) DESC NULLS LAST LIMIT 8
        """)
        if not stocks.empty:
            for _, row in stocks.iterrows():
                change = row.get('change_percent', 0) or 0
                color = "positive" if change >= 0 else "negative"
                st.markdown(f"**{row['symbol']}** ${row['price']:.2f} "
                           f"<span class='{color}'>{change:+.2f}%</span>",
                           unsafe_allow_html=True)
        else:
            st.info("No stock data - run markets collector")

    with col2:
        st.subheader("Crypto")
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
                price_fmt = f"${row['price']:,.2f}" if row['price'] < 1000 else f"${row['price']:,.0f}"
                st.markdown(f"**{row['symbol']}** {price_fmt} "
                           f"<span class='{color}'>{change:+.2f}%</span>",
                           unsafe_allow_html=True)
        else:
            st.info("No crypto data - run crypto collector")

    with col3:
        st.subheader("Commodities")
        commodities = load_data("""
            SELECT symbol, name, price, change_percent
            FROM commodities
            WHERE timestamp = (SELECT MAX(timestamp) FROM commodities)
            ORDER BY symbol LIMIT 8
        """)
        if not commodities.empty:
            for _, row in commodities.iterrows():
                change = row.get('change_percent', 0) or 0
                color = "positive" if change >= 0 else "negative"
                name = row.get('name', row['symbol'])[:15]
                st.markdown(f"**{name}** ${row['price']:.2f} "
                           f"<span class='{color}'>{change:+.2f}%</span>",
                           unsafe_allow_html=True)
        else:
            st.info("No commodity data - run commodities collector")

    st.markdown("---")

    # Bottom row - Global data
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("Forex")
        forex = load_data("""
            SELECT pair, rate FROM forex
            WHERE timestamp = (SELECT MAX(timestamp) FROM forex)
            ORDER BY pair LIMIT 6
        """)
        if not forex.empty:
            for _, row in forex.iterrows():
                st.caption(f"**{row['pair']}**: {row['rate']:.4f}")
        else:
            st.info("No forex data")

    with col2:
        st.subheader("Weather")
        weather = load_data("""
            SELECT city, temperature FROM weather
            WHERE timestamp = (SELECT MAX(timestamp) FROM weather)
            ORDER BY city LIMIT 6
        """)
        if not weather.empty:
            for _, row in weather.iterrows():
                temp = row['temperature']
                temp_color = "negative" if temp > 30 else "positive" if temp < 10 else "neutral"
                st.caption(f"{row['city']}: <span class='{temp_color}'>{temp:.1f}°C</span>",
                          unsafe_allow_html=True)
        else:
            st.info("No weather data")

    with col3:
        st.subheader("Space")
        iss = load_data("SELECT latitude, longitude, altitude FROM iss_positions ORDER BY timestamp DESC LIMIT 1")
        if not iss.empty:
            latest = iss.iloc[0]
            st.caption(f"ISS: {latest['latitude']:.2f}°, {latest['longitude']:.2f}°")
            st.caption(f"Altitude: {latest['altitude']:.0f} km")

        neo = load_data("SELECT COUNT(*) as cnt FROM near_earth_objects WHERE date >= CURRENT_DATE")
        if not neo.empty:
            st.caption(f"NEOs today: {neo['cnt'].iloc[0]}")
        else:
            st.info("No space data")

    with col4:
        st.subheader("Latest News")
        news = load_data("SELECT source, title FROM news ORDER BY published_at DESC LIMIT 4")
        if not news.empty:
            for _, row in news.iterrows():
                st.caption(f"• {row['title'][:50]}...")
        else:
            st.info("No news")


# ============================================================================
# PAGE: MARKETS
# ============================================================================

elif page == "Markets":
    st.title("Market Intelligence")
    st.markdown("*Stocks, Commodities, and Forex*")
    st.markdown("---")

    # ========== GLOBAL MARKET HOURS SECTION ==========
    st.subheader("🌍 Global Market Hours")

    from datetime import datetime, time as dt_time
    import pytz

    def get_market_status(market_tz, open_time, close_time, name, weekend_closed=True):
        """Calculate market status and time until open/close."""
        now_utc = datetime.now(pytz.UTC)
        market_now = now_utc.astimezone(pytz.timezone(market_tz))
        current_time = market_now.time()
        weekday = market_now.weekday()  # 0=Monday, 6=Sunday

        # Check if weekend (most markets closed Sat-Sun)
        if weekend_closed and weekday >= 5:
            # Calculate time until Monday open
            days_until_monday = (7 - weekday) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_open = market_now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
            next_open = next_open + timedelta(days=days_until_monday - (weekday - 4) if weekday == 6 else days_until_monday)
            if weekday == 6:  # Sunday
                next_open = market_now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0) + timedelta(days=1)
            elif weekday == 5:  # Saturday
                next_open = market_now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0) + timedelta(days=2)
            time_until = next_open - market_now
            hours = int(time_until.total_seconds() // 3600)
            mins = int((time_until.total_seconds() % 3600) // 60)
            return False, f"Opens Mon {hours}h {mins}m", market_now.strftime("%H:%M")

        is_open = open_time <= current_time <= close_time

        if is_open:
            # Calculate time until close
            close_dt = market_now.replace(hour=close_time.hour, minute=close_time.minute, second=0, microsecond=0)
            time_until_close = close_dt - market_now
            hours = int(time_until_close.total_seconds() // 3600)
            mins = int((time_until_close.total_seconds() % 3600) // 60)
            return True, f"Closes in {hours}h {mins}m", market_now.strftime("%H:%M")
        else:
            # Calculate time until open
            if current_time < open_time:
                # Opens later today
                open_dt = market_now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0)
            else:
                # Opens tomorrow (or Monday if Friday)
                if weekday == 4:  # Friday after close
                    open_dt = market_now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0) + timedelta(days=3)
                else:
                    open_dt = market_now.replace(hour=open_time.hour, minute=open_time.minute, second=0, microsecond=0) + timedelta(days=1)
            time_until_open = open_dt - market_now
            hours = int(time_until_open.total_seconds() // 3600)
            mins = int((time_until_open.total_seconds() % 3600) // 60)
            return False, f"Opens in {hours}h {mins}m", market_now.strftime("%H:%M")

    # Define all markets with their trading hours
    STOCK_MARKETS = {
        # Major Markets
        'NYSE/NASDAQ': {'tz': 'America/New_York', 'open': dt_time(9, 30), 'close': dt_time(16, 0), 'flag': '🇺🇸'},
        'LSE (London)': {'tz': 'Europe/London', 'open': dt_time(8, 0), 'close': dt_time(16, 30), 'flag': '🇬🇧'},
        'Euronext': {'tz': 'Europe/Paris', 'open': dt_time(9, 0), 'close': dt_time(17, 30), 'flag': '🇪🇺'},
        'XETRA (Germany)': {'tz': 'Europe/Berlin', 'open': dt_time(9, 0), 'close': dt_time(17, 30), 'flag': '🇩🇪'},
        'Tokyo (TSE)': {'tz': 'Asia/Tokyo', 'open': dt_time(9, 0), 'close': dt_time(15, 0), 'flag': '🇯🇵'},
        'Hong Kong (HKEX)': {'tz': 'Asia/Hong_Kong', 'open': dt_time(9, 30), 'close': dt_time(16, 0), 'flag': '🇭🇰'},
        'Shanghai (SSE)': {'tz': 'Asia/Shanghai', 'open': dt_time(9, 30), 'close': dt_time(15, 0), 'flag': '🇨🇳'},
        'Sydney (ASX)': {'tz': 'Australia/Sydney', 'open': dt_time(10, 0), 'close': dt_time(16, 0), 'flag': '🇦🇺'},
        # Emerging Markets
        'Mumbai (BSE)': {'tz': 'Asia/Kolkata', 'open': dt_time(9, 15), 'close': dt_time(15, 30), 'flag': '🇮🇳'},
        'São Paulo (B3)': {'tz': 'America/Sao_Paulo', 'open': dt_time(10, 0), 'close': dt_time(17, 0), 'flag': '🇧🇷'},
        'Toronto (TSX)': {'tz': 'America/Toronto', 'open': dt_time(9, 30), 'close': dt_time(16, 0), 'flag': '🇨🇦'},
        'Singapore (SGX)': {'tz': 'Asia/Singapore', 'open': dt_time(9, 0), 'close': dt_time(17, 0), 'flag': '🇸🇬'},
        'Seoul (KRX)': {'tz': 'Asia/Seoul', 'open': dt_time(9, 0), 'close': dt_time(15, 30), 'flag': '🇰🇷'},
        'Johannesburg (JSE)': {'tz': 'Africa/Johannesburg', 'open': dt_time(9, 0), 'close': dt_time(17, 0), 'flag': '🇿🇦'},
        'Mexico (BMV)': {'tz': 'America/Mexico_City', 'open': dt_time(8, 30), 'close': dt_time(15, 0), 'flag': '🇲🇽'},
    }

    METAL_MARKETS = {
        'COMEX (Gold/Silver)': {'tz': 'America/New_York', 'open': dt_time(8, 20), 'close': dt_time(13, 30), 'flag': '🥇'},
        'LBMA (London Gold)': {'tz': 'Europe/London', 'open': dt_time(10, 30), 'close': dt_time(15, 0), 'flag': '🇬🇧'},
        'Shanghai Gold': {'tz': 'Asia/Shanghai', 'open': dt_time(9, 0), 'close': dt_time(15, 30), 'flag': '🇨🇳'},
        'Tokyo Commodity': {'tz': 'Asia/Tokyo', 'open': dt_time(9, 0), 'close': dt_time(15, 15), 'flag': '🇯🇵'},
        'LME (Base Metals)': {'tz': 'Europe/London', 'open': dt_time(1, 0), 'close': dt_time(19, 0), 'flag': '🔩'},
    }

    # Display market hours in tabs
    mkt_tab1, mkt_tab2 = st.tabs(["📈 Stock Exchanges", "🥇 Metal Markets"])

    with mkt_tab1:
        # Split into major and emerging
        major_markets = ['NYSE/NASDAQ', 'LSE (London)', 'Euronext', 'XETRA (Germany)', 'Tokyo (TSE)', 'Hong Kong (HKEX)', 'Shanghai (SSE)', 'Sydney (ASX)']
        emerging_markets = ['Mumbai (BSE)', 'São Paulo (B3)', 'Toronto (TSX)', 'Singapore (SGX)', 'Seoul (KRX)', 'Johannesburg (JSE)', 'Mexico (BMV)']

        st.markdown("**Major Exchanges**")
        cols = st.columns(4)
        for i, market in enumerate(major_markets):
            info = STOCK_MARKETS[market]
            is_open, status_text, local_time = get_market_status(info['tz'], info['open'], info['close'], market)
            with cols[i % 4]:
                status_color = "#00a86b" if is_open else "#dc3545"
                bg_color = "#d4edda" if is_open else "#f8f9fa"
                border_color = "#28a745" if is_open else "#dc3545"
                text_color = "#155724" if is_open else "#333"
                st.markdown(
                    f"""<div style="background-color:{bg_color}; padding:10px; border-radius:8px; margin:4px 0; border-left:5px solid {border_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="color:#333; font-weight:600; font-size:14px;">{info['flag']} {market}</div>
                    <div style="color:{status_color}; font-weight:700; font-size:13px; margin:4px 0;">● {'OPEN' if is_open else 'CLOSED'}</div>
                    <div style="color:#555; font-size:12px;">{status_text}</div>
                    <div style="color:#777; font-size:11px;">Local: {local_time}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

        st.markdown("**Emerging Markets**")
        cols2 = st.columns(4)
        for i, market in enumerate(emerging_markets):
            info = STOCK_MARKETS[market]
            is_open, status_text, local_time = get_market_status(info['tz'], info['open'], info['close'], market)
            with cols2[i % 4]:
                status_color = "#00a86b" if is_open else "#dc3545"
                bg_color = "#d4edda" if is_open else "#f8f9fa"
                border_color = "#28a745" if is_open else "#dc3545"
                text_color = "#155724" if is_open else "#333"
                st.markdown(
                    f"""<div style="background-color:{bg_color}; padding:10px; border-radius:8px; margin:4px 0; border-left:5px solid {border_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="color:#333; font-weight:600; font-size:14px;">{info['flag']} {market}</div>
                    <div style="color:{status_color}; font-weight:700; font-size:13px; margin:4px 0;">● {'OPEN' if is_open else 'CLOSED'}</div>
                    <div style="color:#555; font-size:12px;">{status_text}</div>
                    <div style="color:#777; font-size:11px;">Local: {local_time}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

    with mkt_tab2:
        st.markdown("**Precious & Base Metal Markets**")
        metal_cols = st.columns(3)
        for i, (market, info) in enumerate(METAL_MARKETS.items()):
            is_open, status_text, local_time = get_market_status(info['tz'], info['open'], info['close'], market)
            with metal_cols[i % 3]:
                status_color = "#b8860b" if is_open else "#dc3545"  # Dark gold for open
                bg_color = "#fff8dc" if is_open else "#f8f9fa"  # Cornsilk for open
                border_color = "#daa520" if is_open else "#dc3545"
                st.markdown(
                    f"""<div style="background-color:{bg_color}; padding:10px; border-radius:8px; margin:4px 0; border-left:5px solid {border_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="color:#333; font-weight:600; font-size:14px;">{info['flag']} {market}</div>
                    <div style="color:{status_color}; font-weight:700; font-size:13px; margin:4px 0;">● {'OPEN' if is_open else 'CLOSED'}</div>
                    <div style="color:#555; font-size:12px;">{status_text}</div>
                    <div style="color:#777; font-size:11px;">Local: {local_time}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

        st.caption("Note: Metal markets often have extended/overnight trading. Hours shown are core trading sessions.")

    st.markdown("---")

    # ========== EARNINGS CALENDAR ==========
    with st.expander("📅 Upcoming Earnings", expanded=False):
        from datetime import datetime, timedelta

        # Major company earnings (approximate dates - Q4 2024 / Q1 2025 season)
        def get_earnings_calendar():
            """Generate upcoming earnings for tracked stocks."""
            today = datetime.now()
            earnings = []

            # Q4 2024 / Q1 2025 earnings dates (approximate - check actual calendars)
            # Format: symbol, company, date, time (BMO=Before Market Open, AMC=After Market Close)
            earnings_schedule = [
                # Tech Giants (typically late Jan / early Feb for Q4)
                ('AAPL', 'Apple Inc.', datetime(2025, 1, 30), 'AMC'),
                ('MSFT', 'Microsoft', datetime(2025, 1, 29), 'AMC'),
                ('GOOGL', 'Alphabet', datetime(2025, 2, 4), 'AMC'),
                ('AMZN', 'Amazon', datetime(2025, 2, 6), 'AMC'),
                ('META', 'Meta Platforms', datetime(2025, 2, 5), 'AMC'),
                ('NVDA', 'NVIDIA', datetime(2025, 2, 26), 'AMC'),
                ('TSLA', 'Tesla', datetime(2025, 1, 29), 'AMC'),
                # Finance
                ('JPM', 'JPMorgan Chase', datetime(2025, 1, 15), 'BMO'),
                ('BAC', 'Bank of America', datetime(2025, 1, 16), 'BMO'),
                ('V', 'Visa', datetime(2025, 1, 30), 'AMC'),
                ('MA', 'Mastercard', datetime(2025, 1, 30), 'BMO'),
                # Healthcare
                ('JNJ', 'Johnson & Johnson', datetime(2025, 1, 22), 'BMO'),
                ('PFE', 'Pfizer', datetime(2025, 2, 4), 'BMO'),
                # Consumer
                ('WMT', 'Walmart', datetime(2025, 2, 20), 'BMO'),
                ('PG', 'Procter & Gamble', datetime(2025, 1, 22), 'BMO'),
                ('HD', 'Home Depot', datetime(2025, 2, 25), 'BMO'),
                ('DIS', 'Walt Disney', datetime(2025, 2, 5), 'AMC'),
                ('KO', 'Coca-Cola', datetime(2025, 2, 11), 'BMO'),
                # Energy
                ('XOM', 'Exxon Mobil', datetime(2025, 1, 31), 'BMO'),
                # Tech
                ('CSCO', 'Cisco Systems', datetime(2025, 2, 12), 'AMC'),
            ]

            for symbol, company, date, timing in earnings_schedule:
                if date >= today - timedelta(days=7):  # Show past week too
                    earnings.append({
                        'symbol': symbol,
                        'company': company,
                        'date': date,
                        'timing': timing
                    })

            # Sort by date
            earnings.sort(key=lambda x: x['date'])
            return earnings[:15]

        earnings_events = get_earnings_calendar()

        if earnings_events:
            earn_cols = st.columns([1, 2, 2, 1, 1])
            earn_cols[0].markdown("**Symbol**")
            earn_cols[1].markdown("**Company**")
            earn_cols[2].markdown("**Date**")
            earn_cols[3].markdown("**Time**")
            earn_cols[4].markdown("**Status**")

            for event in earnings_events:
                days_until = (event['date'] - datetime.now()).days

                if days_until < 0:
                    status = "✅ Reported"
                    status_color = "#888"
                elif days_until == 0:
                    status = "🔴 TODAY"
                    status_color = "#d32f2f"
                elif days_until <= 7:
                    status = f"⏰ {days_until}d"
                    status_color = "#f57c00"
                else:
                    status = f"📅 {days_until}d"
                    status_color = "#1976d2"

                timing_str = "Pre-Market" if event['timing'] == 'BMO' else "After-Hours"

                earn_cols = st.columns([1, 2, 2, 1, 1])
                earn_cols[0].markdown(f"**{event['symbol']}**")
                earn_cols[1].markdown(event['company'])
                earn_cols[2].markdown(event['date'].strftime('%a, %b %d'))
                earn_cols[3].markdown(timing_str)
                earn_cols[4].markdown(f"<span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)

            st.caption("*Dates are approximate. Check official investor relations for confirmed dates.*")
        else:
            st.info("No upcoming earnings in the next 30 days.")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Stocks", "Commodities", "Forex"])

    with tab1:
        # Optimized query - get only latest per symbol using DISTINCT ON
        latest_stocks = load_data("""
            SELECT DISTINCT ON (symbol) symbol, name, price, change, change_percent, volume, timestamp
            FROM stocks ORDER BY symbol, timestamp DESC
        """)

        if latest_stocks.empty:
            st.warning("No stock data available. Run: `python scheduler.py --collector markets`")
        else:
            latest_stocks['change_percent'] = pd.to_numeric(latest_stocks['change_percent'], errors='coerce').fillna(0)

            gainers = latest_stocks[latest_stocks['change_percent'] > 0].sort_values('change_percent', ascending=False)
            losers = latest_stocks[latest_stocks['change_percent'] < 0].sort_values('change_percent', ascending=True)

            # Summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total Stocks", len(latest_stocks))
            with col2:
                st.metric("Gainers", len(gainers), delta=f"{len(gainers)}" if len(gainers) > 0 else None)
            with col3:
                st.metric("Losers", len(losers), delta=f"-{len(losers)}" if len(losers) > 0 else None, delta_color="inverse")
            with col4:
                avg = latest_stocks['change_percent'].mean()
                st.metric("Avg Change", f"{avg:+.2f}%")
            with col5:
                total_vol = latest_stocks['volume'].sum()
                st.metric("Total Volume", format_large_number(total_vol))

            st.markdown("---")

            # Sub-tabs for different views
            stock_view = st.radio("View", ["All Stocks", "Top Gainers", "Top Losers", "Heatmap"], horizontal=True)

            if stock_view == "All Stocks":
                display_df = latest_stocks[['symbol', 'name', 'price', 'change_percent', 'volume']].copy()
                display_df = display_df.sort_values('change_percent', ascending=False)
                display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
                display_df['change_percent'] = display_df['change_percent'].apply(format_change)
                display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                display_df.columns = ['Symbol', 'Name', 'Price', 'Change %', 'Volume']
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            elif stock_view == "Top Gainers":
                st.subheader("Top Gainers")
                if not gainers.empty:
                    top_gainers = gainers.head(10)
                    for _, row in top_gainers.iterrows():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"**{row['symbol']}** - {row['name'] or 'N/A'}")
                        with col2:
                            st.markdown(f"${row['price']:.2f}")
                        with col3:
                            st.markdown(f"<span class='positive'>+{row['change_percent']:.2f}%</span>", unsafe_allow_html=True)
                else:
                    st.info("No gainers today")

            elif stock_view == "Top Losers":
                st.subheader("Top Losers")
                if not losers.empty:
                    top_losers = losers.head(10)
                    for _, row in top_losers.iterrows():
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"**{row['symbol']}** - {row['name'] or 'N/A'}")
                        with col2:
                            st.markdown(f"${row['price']:.2f}")
                        with col3:
                            st.markdown(f"<span class='negative'>{row['change_percent']:.2f}%</span>", unsafe_allow_html=True)
                else:
                    st.info("No losers today")

            else:  # Heatmap
                heatmap_df = latest_stocks[['symbol', 'name', 'price', 'change_percent', 'volume']].copy()
                heatmap_df['volume'] = heatmap_df['volume'].fillna(1)

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
                fig.update_layout(**get_clean_plotly_layout(), height=500, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Size = Volume | Color = Daily Change (Green = Gain, Red = Loss)")

    with tab2:
        st.subheader("Commodity Prices")
        # Optimized query - get only latest per symbol
        latest_commodities = load_data("""
            SELECT DISTINCT ON (symbol) symbol, name, price, change_percent, unit, timestamp
            FROM commodities ORDER BY symbol, timestamp DESC
        """)

        if latest_commodities.empty:
            st.warning("No commodity data. Run: `python scheduler.py --collector commodities`")
        else:

            # Group by category
            energy = latest_commodities[latest_commodities['symbol'].isin(['CRUDE_OIL', 'NATURAL_GAS', 'BRENT'])]
            metals = latest_commodities[latest_commodities['symbol'].isin(['GOLD', 'SILVER', 'COPPER', 'PLATINUM'])]
            agriculture = latest_commodities[~latest_commodities['symbol'].isin(['CRUDE_OIL', 'NATURAL_GAS', 'BRENT', 'GOLD', 'SILVER', 'COPPER', 'PLATINUM'])]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Energy**")
                for _, row in energy.iterrows():
                    change = row.get('change_percent', 0) or 0
                    st.metric(row['name'] or row['symbol'], f"${row['price']:.2f}", f"{change:+.2f}%")

            with col2:
                st.markdown("**Metals**")
                for _, row in metals.iterrows():
                    change = row.get('change_percent', 0) or 0
                    st.metric(row['name'] or row['symbol'], f"${row['price']:.2f}", f"{change:+.2f}%")

            with col3:
                st.markdown("**Agriculture**")
                for _, row in agriculture.iterrows():
                    change = row.get('change_percent', 0) or 0
                    st.metric(row['name'] or row['symbol'], f"${row['price']:.2f}", f"{change:+.2f}%")

    with tab3:
        st.subheader("Foreign Exchange Rates")
        # Optimized query - get only latest per pair
        latest_forex = load_data("""
            SELECT DISTINCT ON (pair) pair, rate, bid, ask, timestamp FROM forex
            ORDER BY pair, timestamp DESC
        """)

        if latest_forex.empty:
            st.warning("No forex data. Run: `python scheduler.py --collector forex`")
        else:
            # ========== CURRENCY STRENGTH METER ==========
            st.markdown("### 💪 Currency Strength Meter")

            # Calculate relative strength based on pair movements
            # For each currency, check how it performs against others
            def calculate_currency_strength(forex_df):
                """Calculate relative strength of major currencies."""
                currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'CNY']
                strength = {c: 0 for c in currencies}
                pair_count = {c: 0 for c in currencies}

                # Base rates (approximate baseline for comparison)
                baseline_rates = {
                    'EUR/USD': 1.10, 'GBP/USD': 1.27, 'USD/JPY': 150.0,
                    'USD/CHF': 0.88, 'AUD/USD': 0.65, 'USD/CAD': 1.36, 'USD/CNY': 7.25
                }

                for _, row in forex_df.iterrows():
                    pair = row['pair']
                    rate = row['rate']

                    if pair in baseline_rates and rate:
                        # Convert Decimal to float to avoid type errors
                        rate = float(rate)
                        baseline = baseline_rates[pair]
                        pct_change = ((rate - baseline) / baseline) * 100

                        # Parse currencies from pair
                        parts = pair.split('/')
                        if len(parts) == 2:
                            base_curr, quote_curr = parts

                            # If pair went up (base strengthened vs quote)
                            if base_curr in strength:
                                strength[base_curr] += pct_change
                                pair_count[base_curr] += 1
                            if quote_curr in strength:
                                strength[quote_curr] -= pct_change
                                pair_count[quote_curr] += 1

                # Normalize scores
                for curr in currencies:
                    if pair_count[curr] > 0:
                        strength[curr] = strength[curr] / pair_count[curr]

                return strength

            strength_scores = calculate_currency_strength(latest_forex)

            # Sort by strength
            sorted_strength = sorted(strength_scores.items(), key=lambda x: x[1], reverse=True)

            # Display as horizontal bar chart
            strength_df = pd.DataFrame(sorted_strength, columns=['Currency', 'Strength'])

            # Color map
            def get_strength_color(val):
                if val > 2:
                    return '#00a86b'  # Strong
                elif val > 0:
                    return '#4caf50'  # Bullish
                elif val > -2:
                    return '#ff9800'  # Weak
                else:
                    return '#f44336'  # Very Weak

            currency_flags = {'USD': '🇺🇸', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 'JPY': '🇯🇵',
                            'CHF': '🇨🇭', 'AUD': '🇦🇺', 'CAD': '🇨🇦', 'CNY': '🇨🇳'}

            str_cols = st.columns(len(sorted_strength))
            for i, (curr, score) in enumerate(sorted_strength):
                with str_cols[i]:
                    color = get_strength_color(score)
                    flag = currency_flags.get(curr, '')
                    status = "Strong" if score > 1 else "Weak" if score < -1 else "Neutral"
                    st.markdown(
                        f"""<div style="text-align:center; padding:10px; background-color:#1e1e1e; border-radius:5px; border-top:4px solid {color};">
                        <div style="font-size:1.5em;">{flag}</div>
                        <b>{curr}</b><br>
                        <span style="color:{color}; font-size:1.2em;">{score:+.1f}</span><br>
                        <small>{status}</small>
                        </div>""",
                        unsafe_allow_html=True
                    )

            st.markdown("---")

            # Major pairs
            major_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD']

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Major Pairs**")
                for _, row in latest_forex[latest_forex['pair'].isin(major_pairs)].iterrows():
                    st.metric(row['pair'], f"{row['rate']:.4f}")

            with col2:
                st.markdown("**Other Pairs**")
                for _, row in latest_forex[~latest_forex['pair'].isin(major_pairs)].iterrows():
                    st.metric(row['pair'], f"{row['rate']:.4f}")

            st.markdown("---")
            st.subheader("All Rates")
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
    st.markdown("*Real-time crypto prices and market data*")
    st.markdown("---")

    # Optimized query - get only latest per symbol
    latest_crypto = load_data("""
        SELECT DISTINCT ON (symbol) symbol, name, price, change_24h, change_percent_24h,
               market_cap, volume_24h, timestamp
        FROM crypto ORDER BY symbol, timestamp DESC
    """)

    if latest_crypto.empty:
        st.warning("No cryptocurrency data. Run: `python scheduler.py --collector crypto`")
    else:
        latest_crypto['change_percent_24h'] = pd.to_numeric(latest_crypto['change_percent_24h'], errors='coerce').fillna(0)
        latest_crypto['market_cap'] = pd.to_numeric(latest_crypto['market_cap'], errors='coerce').fillna(0)

        total_market_cap = latest_crypto['market_cap'].sum()
        gainers = latest_crypto[latest_crypto['change_percent_24h'] > 0].sort_values('change_percent_24h', ascending=False)
        losers = latest_crypto[latest_crypto['change_percent_24h'] < 0].sort_values('change_percent_24h', ascending=True)

        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Coins", len(latest_crypto))
        with col2:
            st.metric("Market Cap", format_large_number(total_market_cap))
        with col3:
            st.metric("Gainers", len(gainers), delta=f"+{len(gainers)}")
        with col4:
            st.metric("Losers", len(losers), delta=f"-{len(losers)}", delta_color="inverse")
        with col5:
            # BTC dominance
            btc_cap = latest_crypto[latest_crypto['symbol'] == 'BTC']['market_cap'].sum()
            dominance = (btc_cap / total_market_cap * 100) if total_market_cap > 0 else 0
            st.metric("BTC Dominance", f"{dominance:.1f}%")

        st.markdown("---")

        # Tab views
        crypto_view = st.radio("View", ["Overview", "Top Gainers", "Top Losers", "Market Cap Chart", "DeFi & On-Chain", "All Coins"], horizontal=True)

        if crypto_view == "Overview":
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top 10 by Market Cap")
                top_10 = latest_crypto.nlargest(10, 'market_cap')
                for i, (_, row) in enumerate(top_10.iterrows(), 1):
                    change = row['change_percent_24h']
                    color = "positive" if change >= 0 else "negative"
                    price_fmt = f"${row['price']:,.2f}" if row['price'] < 10000 else f"${row['price']:,.0f}"
                    st.markdown(f"**{i}. {row['symbol']}** {price_fmt} <span class='{color}'>{change:+.2f}%</span>",
                               unsafe_allow_html=True)

            with col2:
                st.subheader("Biggest Movers (24h)")
                # Top 5 gainers and losers
                st.markdown("**Gainers**")
                for _, row in gainers.head(5).iterrows():
                    st.markdown(f"**{row['symbol']}** <span class='positive'>+{row['change_percent_24h']:.2f}%</span>",
                               unsafe_allow_html=True)
                st.markdown("**Losers**")
                for _, row in losers.head(5).iterrows():
                    st.markdown(f"**{row['symbol']}** <span class='negative'>{row['change_percent_24h']:.2f}%</span>",
                               unsafe_allow_html=True)

        elif crypto_view == "Top Gainers":
            st.subheader("Top Gainers (24h)")
            if not gainers.empty:
                for _, row in gainers.head(15).iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    with col1:
                        st.markdown(f"**{row['symbol']}**")
                    with col2:
                        st.markdown(f"{row['name'] or '-'}")
                    with col3:
                        st.markdown(f"${row['price']:,.2f}")
                    with col4:
                        st.markdown(f"<span class='positive'>+{row['change_percent_24h']:.2f}%</span>", unsafe_allow_html=True)
            else:
                st.info("No gainers in the last 24 hours")

        elif crypto_view == "Top Losers":
            st.subheader("Top Losers (24h)")
            if not losers.empty:
                for _, row in losers.head(15).iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                    with col1:
                        st.markdown(f"**{row['symbol']}**")
                    with col2:
                        st.markdown(f"{row['name'] or '-'}")
                    with col3:
                        st.markdown(f"${row['price']:,.2f}")
                    with col4:
                        st.markdown(f"<span class='negative'>{row['change_percent_24h']:.2f}%</span>", unsafe_allow_html=True)
            else:
                st.info("No losers in the last 24 hours")

        elif crypto_view == "Market Cap Chart":
            st.subheader("Market Cap Distribution")
            top_coins = latest_crypto.nlargest(10, 'market_cap').copy()
            # Convert Decimal to float to avoid division errors
            top_coins['market_cap_b'] = top_coins['market_cap'].apply(lambda x: float(x) / 1e9 if x else 0)

            fig = px.pie(
                top_coins,
                values='market_cap_b',
                names='symbol',
                title='Top 10 Cryptocurrencies by Market Cap',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(**get_clean_plotly_layout(), height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Bar chart of top 10
            fig2 = px.bar(
                top_coins.sort_values('market_cap_b', ascending=True),
                x='market_cap_b',
                y='symbol',
                orientation='h',
                title='Market Cap (Billions USD)',
                color='change_percent_24h',
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0
            )
            fig2.update_layout(**get_clean_plotly_layout(), height=400)
            st.plotly_chart(fig2, use_container_width=True)

        elif crypto_view == "DeFi & On-Chain":
            st.subheader("DeFi & On-Chain Metrics")
            st.markdown("*Decentralized finance and blockchain analytics*")

            # DeFi TVL Data (curated)
            DEFI_TVL = {
                'Protocol': ['Lido', 'AAVE', 'EigenLayer', 'Maker', 'JustLend',
                            'Uniswap', 'Ethena', 'ether.fi', 'Rocket Pool', 'Pendle'],
                'Chain': ['Ethereum', 'Multi-chain', 'Ethereum', 'Ethereum', 'Tron',
                         'Multi-chain', 'Ethereum', 'Ethereum', 'Ethereum', 'Multi-chain'],
                'Category': ['Liquid Staking', 'Lending', 'Restaking', 'CDP', 'Lending',
                            'DEX', 'Yield', 'Liquid Staking', 'Liquid Staking', 'Yield'],
                'TVL ($B)': [33.5, 19.8, 17.2, 8.1, 6.8, 6.2, 5.8, 5.5, 3.8, 3.2],
                '7d Change': ['+2.1%', '-1.2%', '+5.8%', '-0.5%', '+0.8%',
                             '+3.2%', '+12.5%', '+4.1%', '-2.3%', '+8.9%'],
            }
            defi_df = pd.DataFrame(DEFI_TVL)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_tvl = sum(DEFI_TVL['TVL ($B)'])
                st.metric("Total DeFi TVL", f"${total_tvl:.1f}B", "+3.2%")
            with col2:
                st.metric("Active Protocols", "3,500+", "+124")
            with col3:
                st.metric("Unique Users (30d)", "8.2M", "+12%")
            with col4:
                st.metric("24h DEX Volume", "$4.8B", "-8%")

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top DeFi Protocols by TVL")
                st.dataframe(defi_df, use_container_width=True, hide_index=True)

            with col2:
                fig_tvl = px.bar(
                    defi_df.sort_values('TVL ($B)', ascending=True),
                    x='TVL ($B)', y='Protocol',
                    orientation='h',
                    title='Total Value Locked by Protocol',
                    color='Category',
                )
                st.plotly_chart(fig_tvl, use_container_width=True)

            st.markdown("---")

            # Chain TVL
            st.subheader("TVL by Blockchain")
            CHAIN_TVL = {
                'Chain': ['Ethereum', 'Tron', 'Solana', 'BSC', 'Arbitrum',
                         'Base', 'Polygon', 'Avalanche', 'Optimism', 'Sui'],
                'TVL ($B)': [68.5, 8.2, 7.8, 5.2, 4.1, 3.5, 1.2, 1.1, 0.9, 0.8],
                'Protocols': [1250, 35, 180, 580, 420, 290, 450, 320, 180, 45],
                '7d Change': ['+1.5%', '+2.1%', '+8.5%', '-1.2%', '+3.8%',
                             '+12.2%', '-2.5%', '+0.8%', '+1.9%', '+15.2%'],
            }
            chain_df = pd.DataFrame(CHAIN_TVL)

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(chain_df, use_container_width=True, hide_index=True)
            with col2:
                fig_chain = px.pie(
                    chain_df, values='TVL ($B)', names='Chain',
                    title='TVL Distribution by Chain',
                    hole=0.4
                )
                st.plotly_chart(fig_chain, use_container_width=True)

            st.markdown("---")

            # Stablecoin Metrics
            st.subheader("Stablecoin Metrics")
            STABLECOIN_DATA = {
                'Stablecoin': ['USDT', 'USDC', 'DAI', 'FDUSD', 'USDe', 'TUSD', 'FRAX'],
                'Market Cap ($B)': [138.5, 41.2, 5.4, 2.8, 2.5, 0.5, 0.4],
                'Peg': ['$1.0001', '$1.0000', '$0.9998', '$1.0000', '$1.0002', '$0.9995', '$0.9997'],
                '30d Vol ($B)': [1850, 420, 12, 85, 42, 2.1, 1.5],
                'Dominant Chain': ['Tron', 'Ethereum', 'Ethereum', 'BSC', 'Ethereum', 'Ethereum', 'Ethereum'],
            }
            stable_df = pd.DataFrame(STABLECOIN_DATA)

            col1, col2 = st.columns(2)
            with col1:
                total_stable = sum(STABLECOIN_DATA['Market Cap ($B)'])
                st.metric("Total Stablecoin Supply", f"${total_stable:.1f}B")
                st.dataframe(stable_df, use_container_width=True, hide_index=True)
            with col2:
                fig_stable = px.bar(
                    stable_df, x='Stablecoin', y='Market Cap ($B)',
                    title='Stablecoin Market Caps',
                    color='Market Cap ($B)',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_stable, use_container_width=True)

            st.markdown("---")

            # On-Chain Metrics
            st.subheader("Bitcoin On-Chain Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Hash Rate", "750 EH/s", "+5.2%")
                st.metric("Difficulty", "95.7T", "+2.1%")
            with col2:
                st.metric("Active Addresses (24h)", "892K", "-3.5%")
                st.metric("New Addresses (24h)", "425K", "+1.2%")
            with col3:
                st.metric("Exchange Reserves", "2.1M BTC", "-0.8%")
                st.metric("Miner Reserves", "1.82M BTC", "-0.2%")
            with col4:
                st.metric("MVRV Ratio", "2.45", "+0.12")
                st.metric("Realized Price", "$42,500", "+$850")

            st.subheader("Ethereum On-Chain Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Staked ETH", "34.2M", "+1.5%")
                st.metric("Staking APR", "3.2%", "-0.1%")
            with col2:
                st.metric("Active Validators", "1.07M", "+2.1K")
                st.metric("Pending Validators", "892", "-125")
            with col3:
                st.metric("Gas Price (Gwei)", "12", "-3")
                st.metric("Daily Burn", "1,250 ETH", "+8%")
            with col4:
                st.metric("L2 TVL", "$42.5B", "+5.2%")
                st.metric("ETH Issuance (Daily)", "2,450 ETH", "")

        elif crypto_view == "All Coins":
            st.subheader("All Cryptocurrencies")
            display_crypto = latest_crypto[['symbol', 'name', 'price', 'change_percent_24h', 'market_cap', 'volume_24h']].copy()
            display_crypto = display_crypto.sort_values('market_cap', ascending=False)
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

    # ========== ECONOMIC CALENDAR SECTION ==========
    st.subheader("📅 Economic Calendar")

    from datetime import datetime, timedelta
    import calendar

    # Define major economic events (recurring schedules)
    def get_economic_calendar():
        """Generate upcoming economic events based on typical schedules."""
        today = datetime.now()
        events = []

        # FOMC Meetings (8 per year, roughly every 6 weeks)
        # 2024-2025 FOMC dates (approximate - check Fed calendar)
        fomc_dates = [
            datetime(2025, 1, 29), datetime(2025, 3, 19), datetime(2025, 5, 7),
            datetime(2025, 6, 18), datetime(2025, 7, 30), datetime(2025, 9, 17),
            datetime(2025, 11, 5), datetime(2025, 12, 17)
        ]
        for d in fomc_dates:
            if d >= today - timedelta(days=1):
                events.append({'date': d, 'event': 'FOMC Meeting', 'country': '🇺🇸 USA', 'importance': 'HIGH', 'category': 'Central Bank'})

        # US Jobs Report (First Friday of each month)
        for month_offset in range(6):
            target_month = today.month + month_offset
            target_year = today.year
            if target_month > 12:
                target_month -= 12
                target_year += 1
            # Find first Friday
            cal = calendar.monthcalendar(target_year, target_month)
            first_friday = [week[4] for week in cal if week[4] != 0][0]
            jobs_date = datetime(target_year, target_month, first_friday)
            if jobs_date >= today - timedelta(days=1):
                events.append({'date': jobs_date, 'event': 'US Jobs Report (NFP)', 'country': '🇺🇸 USA', 'importance': 'HIGH', 'category': 'Employment'})

        # US CPI (Usually mid-month, ~12th-15th)
        for month_offset in range(6):
            target_month = today.month + month_offset
            target_year = today.year
            if target_month > 12:
                target_month -= 12
                target_year += 1
            cpi_date = datetime(target_year, target_month, 13)
            if cpi_date >= today - timedelta(days=1):
                events.append({'date': cpi_date, 'event': 'US CPI Inflation', 'country': '🇺🇸 USA', 'importance': 'HIGH', 'category': 'Inflation'})

        # US GDP (End of month, quarterly)
        gdp_months = [1, 4, 7, 10]  # Quarterly releases
        for month in gdp_months:
            gdp_year = today.year if month >= today.month else today.year + 1
            gdp_date = datetime(gdp_year, month, 28)
            if gdp_date >= today - timedelta(days=1):
                events.append({'date': gdp_date, 'event': 'US GDP Release', 'country': '🇺🇸 USA', 'importance': 'HIGH', 'category': 'Growth'})

        # ECB Meetings (every 6 weeks approximately)
        ecb_dates = [
            datetime(2025, 1, 30), datetime(2025, 3, 6), datetime(2025, 4, 17),
            datetime(2025, 6, 5), datetime(2025, 7, 17), datetime(2025, 9, 11),
            datetime(2025, 10, 30), datetime(2025, 12, 18)
        ]
        for d in ecb_dates:
            if d >= today - timedelta(days=1):
                events.append({'date': d, 'event': 'ECB Rate Decision', 'country': '🇪🇺 EU', 'importance': 'HIGH', 'category': 'Central Bank'})

        # Bank of England
        boe_dates = [
            datetime(2025, 2, 6), datetime(2025, 3, 20), datetime(2025, 5, 8),
            datetime(2025, 6, 19), datetime(2025, 8, 7), datetime(2025, 9, 18),
            datetime(2025, 11, 6), datetime(2025, 12, 18)
        ]
        for d in boe_dates:
            if d >= today - timedelta(days=1):
                events.append({'date': d, 'event': 'BoE Rate Decision', 'country': '🇬🇧 UK', 'importance': 'HIGH', 'category': 'Central Bank'})

        # Bank of Japan
        boj_dates = [
            datetime(2025, 1, 24), datetime(2025, 3, 14), datetime(2025, 4, 25),
            datetime(2025, 6, 13), datetime(2025, 7, 31), datetime(2025, 9, 19),
            datetime(2025, 10, 31), datetime(2025, 12, 19)
        ]
        for d in boj_dates:
            if d >= today - timedelta(days=1):
                events.append({'date': d, 'event': 'BoJ Rate Decision', 'country': '🇯🇵 Japan', 'importance': 'HIGH', 'category': 'Central Bank'})

        # US Retail Sales (mid-month)
        for month_offset in range(4):
            target_month = today.month + month_offset
            target_year = today.year
            if target_month > 12:
                target_month -= 12
                target_year += 1
            retail_date = datetime(target_year, target_month, 16)
            if retail_date >= today - timedelta(days=1):
                events.append({'date': retail_date, 'event': 'US Retail Sales', 'country': '🇺🇸 USA', 'importance': 'MEDIUM', 'category': 'Consumer'})

        # ISM Manufacturing PMI (First business day of month)
        for month_offset in range(4):
            target_month = today.month + month_offset
            target_year = today.year
            if target_month > 12:
                target_month -= 12
                target_year += 1
            ism_date = datetime(target_year, target_month, 1)
            # Adjust for weekend
            while ism_date.weekday() >= 5:
                ism_date += timedelta(days=1)
            if ism_date >= today - timedelta(days=1):
                events.append({'date': ism_date, 'event': 'ISM Manufacturing PMI', 'country': '🇺🇸 USA', 'importance': 'MEDIUM', 'category': 'Manufacturing'})

        # Sort by date
        events.sort(key=lambda x: x['date'])
        return events[:20]  # Return next 20 events

    calendar_events = get_economic_calendar()

    if calendar_events:
        # Display as expandable sections by week
        cal_col1, cal_col2 = st.columns([3, 1])

        with cal_col1:
            for event in calendar_events[:12]:  # Show next 12 events
                days_until = (event['date'] - datetime.now()).days
                if days_until < 0:
                    time_str = "Today" if days_until == -1 else f"{abs(days_until)}d ago"
                    bg_color = "#4a4a4a"
                elif days_until == 0:
                    time_str = "TODAY"
                    bg_color = "#d32f2f"
                elif days_until <= 7:
                    time_str = f"In {days_until}d"
                    bg_color = "#f57c00"
                else:
                    time_str = f"In {days_until}d"
                    bg_color = "#1976d2"

                importance_color = "#d32f2f" if event['importance'] == 'HIGH' else "#ff9800"

                st.markdown(
                    f"""<div style="background-color:#1e1e1e; padding:10px; border-radius:5px; margin:5px 0; border-left:4px solid {importance_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <b>{event['country']}</b> {event['event']}<br>
                            <small style="color:#888;">{event['category']} | {event['date'].strftime('%a, %b %d, %Y')}</small>
                        </div>
                        <div style="background-color:{bg_color}; padding:5px 10px; border-radius:3px;">
                            <b>{time_str}</b>
                        </div>
                    </div>
                    </div>""",
                    unsafe_allow_html=True
                )

        with cal_col2:
            st.markdown("**Legend**")
            st.markdown("🔴 HIGH Impact")
            st.markdown("🟠 MEDIUM Impact")
            st.markdown("---")
            st.markdown("**Categories**")
            st.caption("• Central Bank")
            st.caption("• Employment")
            st.caption("• Inflation")
            st.caption("• Growth")
            st.caption("• Consumer")
            st.caption("• Manufacturing")

    st.markdown("---")

    # ========== EXISTING ECONOMIC INDICATORS ==========
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

            if latest_country.empty:
                st.info("No indicators available for this country")
            else:
                cols = st.columns(min(4, len(latest_country)))
                for idx, (_, row) in enumerate(latest_country.iterrows()):
                    with cols[idx % len(cols)]:
                        unit_str = f" {row['unit']}" if row.get('unit') else ""
                        # Convert Decimal to float to avoid formatting errors
                        val = float(row['value']) if row['value'] else None
                        st.metric(
                            label=row['name'] or row['indicator'],
                            value=f"{val:.2f}{unit_str}" if val else "N/A"
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
# PAGE: GLOBAL DEVELOPMENT (WORLD BANK DATA)
# ============================================================================

elif page == "Global Development":
    st.title("Global Development Indicators")
    st.markdown("*Data from World Bank - 20 countries, 20+ indicators*")
    st.markdown("---")

    # Check if table exists
    if not table_exists('worldbank_indicators'):
        st.warning("World Bank data not yet collected. Run the WorldBank collector first.")
        st.info("""
        The World Bank integration provides:
        - **20 G20 Countries** - US, China, Japan, Germany, UK, France, India, Brazil, and more
        - **20+ Indicators** across Economy, Trade, Demographics, Labor, and Environment
        - **Free API** - No authentication required
        """)
    else:
        # Load World Bank data
        wb_df = load_data("""
            SELECT indicator_code, indicator_name, category, country_code, country_name,
                   year, value, unit, timestamp
            FROM worldbank_indicators
            ORDER BY category, indicator_name, country_name
        """)

        if wb_df.empty:
            st.warning("No World Bank data available. Run the collector.")
        else:
            # Get latest year for each indicator/country
            wb_df['year'] = pd.to_numeric(wb_df['year'], errors='coerce')
            # Filter out rows with NaN years before grouping
            wb_df_valid = wb_df[wb_df['year'].notna()].copy()
            if wb_df_valid.empty:
                st.warning("No valid World Bank data with year information.")
            else:
                latest_wb = wb_df_valid.loc[wb_df_valid.groupby(['indicator_code', 'country_code'])['year'].idxmax()]

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Countries", latest_wb['country_code'].nunique())
                with col2:
                    st.metric("Indicators", latest_wb['indicator_code'].nunique())
                with col3:
                    st.metric("Categories", latest_wb['category'].nunique())
                with col4:
                    latest_year = int(latest_wb['year'].max()) if not pd.isna(latest_wb['year'].max()) else 'N/A'
                    st.metric("Latest Year", latest_year)

                st.markdown("---")

                # View tabs
                tab1, tab2, tab3, tab4 = st.tabs(["By Country", "By Indicator", "Comparison", "Rankings"])

                with tab1:
                    st.subheader("Country Profile")
                    countries = sorted(latest_wb['country_name'].dropna().unique().tolist())
                    selected_country = st.selectbox("Select Country", countries, key="wb_country")

                    if selected_country:
                        country_data = latest_wb[latest_wb['country_name'] == selected_country]

                        # Group by category
                        categories = country_data['category'].unique().tolist()

                        for category in categories:
                            st.markdown(f"##### {category}")
                            cat_data = country_data[country_data['category'] == category]

                            cols = st.columns(min(4, len(cat_data)))
                            for idx, (_, row) in enumerate(cat_data.iterrows()):
                                with cols[idx % len(cols)]:
                                    value = row['value']
                                    if pd.notna(value):
                                        # Convert Decimal to float to avoid division errors
                                        value = float(value)
                                        # Format based on magnitude
                                        if abs(value) >= 1e12:
                                            display_val = f"${value/1e12:.1f}T"
                                        elif abs(value) >= 1e9:
                                            display_val = f"${value/1e9:.1f}B"
                                        elif abs(value) >= 1e6:
                                            display_val = f"{value/1e6:.1f}M"
                                        elif abs(value) < 100:
                                            display_val = f"{value:.2f}"
                                        else:
                                            display_val = f"{value:,.0f}"
                                    else:
                                        display_val = "N/A"

                                    st.metric(
                                        label=row['indicator_name'][:30],
                                        value=display_val,
                                        help=f"Year: {int(row['year']) if pd.notna(row['year']) else 'N/A'}"
                                    )

                with tab2:
                    st.subheader("Indicator Analysis")
                    indicators = sorted(latest_wb['indicator_name'].dropna().unique().tolist())
                    selected_indicator = st.selectbox("Select Indicator", indicators, key="wb_indicator")

                    if selected_indicator:
                        ind_data = latest_wb[latest_wb['indicator_name'] == selected_indicator].copy()
                        ind_data = ind_data.sort_values('value', ascending=False)

                        # Bar chart of all countries
                        fig = px.bar(
                            ind_data,
                            x='country_name',
                            y='value',
                            title=f"{selected_indicator} by Country",
                            color='value',
                            color_continuous_scale='Viridis'
                        )
                        fig.update_layout(**get_clean_plotly_layout(), height=500)
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)

                        # Data table
                        st.dataframe(
                            ind_data[['country_name', 'value', 'year']].rename(
                                columns={'country_name': 'Country', 'value': 'Value', 'year': 'Year'}
                            ),
                            use_container_width=True,
                            hide_index=True
                        )

                with tab3:
                    st.subheader("Multi-Country Comparison")

                    # Select multiple countries
                    compare_countries = st.multiselect(
                        "Select Countries to Compare",
                        countries,
                        default=countries[:5] if len(countries) >= 5 else countries,
                        key="wb_compare"
                    )

                    if len(compare_countries) >= 2:
                        # Select indicators to compare
                        compare_indicators = st.multiselect(
                            "Select Indicators",
                            indicators,
                            default=indicators[:3] if len(indicators) >= 3 else indicators,
                            key="wb_indicators_compare"
                        )

                        if compare_indicators:
                            compare_data = latest_wb[
                                (latest_wb['country_name'].isin(compare_countries)) &
                                (latest_wb['indicator_name'].isin(compare_indicators))
                            ]

                            # Pivot for heatmap
                            pivot_df = compare_data.pivot_table(
                                index='country_name',
                                columns='indicator_name',
                                values='value',
                                aggfunc='first'
                            )

                            if not pivot_df.empty:
                                # Normalize for comparison
                                normalized = pivot_df.apply(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0.5)

                                fig = px.imshow(
                                    normalized,
                                    labels=dict(x="Indicator", y="Country", color="Normalized Value"),
                                    color_continuous_scale='RdYlGn',
                                    title="Normalized Comparison (0=Lowest, 1=Highest)"
                                )
                                fig.update_layout(**get_clean_plotly_layout(), height=400)
                                st.plotly_chart(fig, use_container_width=True)

                                # Raw values table
                                st.markdown("**Raw Values:**")
                                st.dataframe(pivot_df.round(2), use_container_width=True)
                    else:
                        st.info("Select at least 2 countries to compare")

                with tab4:
                    st.subheader("Global Rankings")

                    rank_indicator = st.selectbox(
                        "Select Indicator for Ranking",
                        indicators,
                        key="wb_ranking"
                    )

                    if rank_indicator:
                        rank_data = latest_wb[latest_wb['indicator_name'] == rank_indicator].copy()
                        rank_data = rank_data.sort_values('value', ascending=False).reset_index(drop=True)
                        rank_data['Rank'] = range(1, len(rank_data) + 1)

                        col1, col2 = st.columns([2, 1])

                        with col1:
                            # Top 10 bar chart
                            top_10 = rank_data.head(10)
                            fig = px.bar(
                                top_10,
                                x='value',
                                y='country_name',
                                orientation='h',
                                title=f"Top 10 - {rank_indicator}",
                                color='value',
                                color_continuous_scale='Greens'
                            )
                            fig.update_layout(**get_clean_plotly_layout(), height=400)
                            fig.update_yaxes(autorange='reversed')
                            st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("**Full Rankings:**")
                            st.dataframe(
                                rank_data[['Rank', 'country_name', 'value', 'year']].rename(
                                    columns={'country_name': 'Country', 'value': 'Value', 'year': 'Year'}
                                ),
                                use_container_width=True,
                                hide_index=True,
                                height=400
                            )

                # Export
                st.markdown("---")
                export_csv(latest_wb, "worldbank_indicators")


# ============================================================================
# PAGE: ENERGY & RESOURCES
# ============================================================================

elif page == "Energy & Resources":
    st.title("Energy & Resources")
    st.markdown("*Global Energy Production, Consumption, and Emissions Data*")
    st.markdown("---")

    # Our World in Data energy dataset URL
    OWID_ENERGY_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"

    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def load_energy_data():
        """Load Our World in Data energy dataset."""
        try:
            df = pd.read_csv(OWID_ENERGY_URL)
            return df
        except Exception as e:
            st.error(f"Error loading energy data: {e}")
            return pd.DataFrame()

    energy_df = load_energy_data()

    if not energy_df.empty:
        # Major countries to highlight
        MAJOR_COUNTRIES = ['China', 'United States', 'India', 'Russia', 'Japan',
                          'Germany', 'Brazil', 'Canada', 'South Korea', 'France',
                          'United Kingdom', 'Italy', 'Australia', 'Mexico', 'Indonesia',
                          'Saudi Arabia', 'South Africa', 'Turkey', 'Iran', 'Poland']

        # Filter to major countries and recent years
        major_energy = energy_df[energy_df['country'].isin(MAJOR_COUNTRIES)].copy()

        # Get latest year with good data
        latest_year = energy_df[energy_df['electricity_generation'].notna()]['year'].max()

        # Create tabs for different views
        energy_tab1, energy_tab2, energy_tab3, energy_tab4, energy_tab5, energy_tab6, energy_tab7, energy_tab8 = st.tabs([
            "Electricity Generation", "Energy Mix", "Oil & Gas", "Nuclear", "Renewables", "CO2 Emissions", "Per Capita", "Mining & Resources"
        ])

        with energy_tab1:
            st.subheader("Electricity Generation by Country")

            # Country selector for time series
            col1, col2 = st.columns([2, 1])
            with col1:
                selected_countries = st.multiselect(
                    "Select countries to compare:",
                    options=MAJOR_COUNTRIES,
                    default=['China', 'United States', 'India'],
                    key="elec_gen_countries"
                )
            with col2:
                year_range = st.slider(
                    "Year range:",
                    min_value=1985,
                    max_value=int(latest_year),
                    value=(1990, int(latest_year)),
                    key="elec_gen_years"
                )

            if selected_countries:
                # Filter data
                plot_data = major_energy[
                    (major_energy['country'].isin(selected_countries)) &
                    (major_energy['year'] >= year_range[0]) &
                    (major_energy['year'] <= year_range[1]) &
                    (major_energy['electricity_generation'].notna())
                ]

                if not plot_data.empty:
                    # Line chart - Electricity Generation
                    fig_elec = px.line(
                        plot_data,
                        x='year',
                        y='electricity_generation',
                        color='country',
                        title='Total Electricity Generation (TWh)',
                        labels={'electricity_generation': 'TWh', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_elec.update_layout(**get_clean_plotly_layout(), height=450)
                    st.plotly_chart(fig_elec, use_container_width=True)

                    # Latest year comparison bar chart
                    latest_data = plot_data[plot_data['year'] == plot_data['year'].max()]
                    fig_bar = px.bar(
                        latest_data.sort_values('electricity_generation', ascending=True),
                        x='electricity_generation',
                        y='country',
                        orientation='h',
                        title=f'Electricity Generation ({int(latest_data["year"].max())})',
                        labels={'electricity_generation': 'TWh', 'country': 'Country'},
                        color='electricity_generation',
                        color_continuous_scale='Viridis'
                    )
                    fig_bar.update_layout(**get_clean_plotly_layout(), height=350, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)

            # Global electricity generation table
            st.markdown("---")
            st.subheader(f"Top 20 Electricity Producers ({int(latest_year)})")

            top_producers = energy_df[
                (energy_df['year'] == latest_year) &
                (energy_df['electricity_generation'].notna()) &
                (~energy_df['country'].isin(['World', 'Europe', 'Asia Pacific', 'North America', 'Africa']))
            ].nlargest(20, 'electricity_generation')[['country', 'electricity_generation', 'population']].copy()

            if not top_producers.empty:
                top_producers['per_capita_twh'] = (top_producers['electricity_generation'] * 1000) / (top_producers['population'] / 1e6)  # MWh per person
                top_producers = top_producers.rename(columns={
                    'country': 'Country',
                    'electricity_generation': 'Generation (TWh)',
                    'population': 'Population',
                    'per_capita_twh': 'Per Capita (MWh)'
                })
                top_producers['Generation (TWh)'] = top_producers['Generation (TWh)'].apply(lambda x: f"{x:,.0f}")
                top_producers['Population'] = top_producers['Population'].apply(lambda x: f"{x/1e6:,.1f}M" if pd.notna(x) else "N/A")
                top_producers['Per Capita (MWh)'] = top_producers['Per Capita (MWh)'].apply(lambda x: f"{x:,.1f}" if pd.notna(x) else "N/A")
                st.dataframe(top_producers, use_container_width=True, hide_index=True)

        with energy_tab2:
            st.subheader("Energy Mix by Source")

            # Select country for energy mix
            mix_country = st.selectbox(
                "Select country:",
                options=['World'] + MAJOR_COUNTRIES,
                key="energy_mix_country"
            )

            # Get latest data for selected country
            country_data = energy_df[
                (energy_df['country'] == mix_country) &
                (energy_df['year'] == latest_year)
            ]

            if not country_data.empty:
                row = country_data.iloc[0]

                # Energy mix columns
                energy_sources = {
                    'Coal': row.get('coal_share_elec', 0) or 0,
                    'Gas': row.get('gas_share_elec', 0) or 0,
                    'Oil': row.get('oil_share_elec', 0) or 0,
                    'Nuclear': row.get('nuclear_share_elec', 0) or 0,
                    'Hydro': row.get('hydro_share_elec', 0) or 0,
                    'Wind': row.get('wind_share_elec', 0) or 0,
                    'Solar': row.get('solar_share_elec', 0) or 0,
                    'Other Renewables': row.get('other_renewables_share_elec', 0) or 0,
                }

                # Filter out zero values
                energy_sources = {k: v for k, v in energy_sources.items() if v > 0}

                if energy_sources:
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        # Pie chart
                        fig_pie = px.pie(
                            values=list(energy_sources.values()),
                            names=list(energy_sources.keys()),
                            title=f'{mix_country} Electricity Mix ({int(latest_year)})',
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                        fig_pie.update_layout(**get_clean_plotly_layout(), height=400)
                        st.plotly_chart(fig_pie, use_container_width=True)

                    with col2:
                        # Summary metrics
                        fossil_share = row.get('fossil_share_elec', 0) or 0
                        renewable_share = row.get('renewables_share_elec', 0) or 0
                        low_carbon_share = row.get('low_carbon_share_elec', 0) or 0

                        st.metric("Fossil Fuel Share", f"{fossil_share:.1f}%")
                        st.metric("Renewable Share", f"{renewable_share:.1f}%")
                        st.metric("Low Carbon Share", f"{low_carbon_share:.1f}%",
                                 help="Includes nuclear + renewables")

                        carbon_intensity = row.get('carbon_intensity_elec', 0) or 0
                        st.metric("Carbon Intensity", f"{carbon_intensity:.0f} gCO2/kWh")

                # Energy mix over time
                st.markdown("---")
                st.subheader(f"{mix_country} Energy Mix Evolution")

                mix_history = energy_df[
                    (energy_df['country'] == mix_country) &
                    (energy_df['year'] >= 2000)
                ][['year', 'coal_share_elec', 'gas_share_elec', 'nuclear_share_elec',
                   'hydro_share_elec', 'wind_share_elec', 'solar_share_elec']].copy()

                if not mix_history.empty:
                    mix_history = mix_history.melt(id_vars=['year'], var_name='Source', value_name='Share')
                    mix_history['Source'] = mix_history['Source'].str.replace('_share_elec', '').str.title()

                    fig_area = px.area(
                        mix_history,
                        x='year',
                        y='Share',
                        color='Source',
                        title=f'{mix_country} Electricity Sources Over Time (%)',
                        labels={'Share': '% of Electricity', 'year': 'Year'}
                    )
                    fig_area.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_area, use_container_width=True)

        with energy_tab3:
            st.subheader("Oil & Gas Production")

            col1, col2 = st.columns([2, 1])
            with col1:
                oilgas_countries = st.multiselect(
                    "Select countries:",
                    options=MAJOR_COUNTRIES,
                    default=['United States', 'Russia', 'Saudi Arabia', 'China', 'Canada'],
                    key="oilgas_countries"
                )

            if oilgas_countries:
                # Oil Production
                st.markdown("### Oil Production")
                oil_prod_data = major_energy[
                    (major_energy['country'].isin(oilgas_countries)) &
                    (major_energy['year'] >= 1990) &
                    (major_energy['oil_production'].notna())
                ]

                if not oil_prod_data.empty:
                    fig_oil = px.line(
                        oil_prod_data,
                        x='year',
                        y='oil_production',
                        color='country',
                        title='Oil Production (TWh)',
                        labels={'oil_production': 'TWh', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_oil.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_oil, use_container_width=True)

                # Gas Production
                st.markdown("---")
                st.markdown("### Natural Gas Production")
                gas_prod_data = major_energy[
                    (major_energy['country'].isin(oilgas_countries)) &
                    (major_energy['year'] >= 1990) &
                    (major_energy['gas_production'].notna())
                ]

                if not gas_prod_data.empty:
                    fig_gas = px.line(
                        gas_prod_data,
                        x='year',
                        y='gas_production',
                        color='country',
                        title='Natural Gas Production (TWh)',
                        labels={'gas_production': 'TWh', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_gas.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_gas, use_container_width=True)

                # Oil vs Gas consumption comparison
                st.markdown("---")
                st.markdown("### Oil vs Gas Consumption")

                col1, col2 = st.columns(2)

                with col1:
                    oil_cons_data = major_energy[
                        (major_energy['country'].isin(oilgas_countries)) &
                        (major_energy['year'] == latest_year) &
                        (major_energy['oil_consumption'].notna())
                    ].sort_values('oil_consumption', ascending=True)

                    if not oil_cons_data.empty:
                        fig_oil_cons = px.bar(
                            oil_cons_data,
                            x='oil_consumption',
                            y='country',
                            orientation='h',
                            title=f'Oil Consumption ({int(latest_year)})',
                            labels={'oil_consumption': 'TWh', 'country': ''},
                            color='oil_consumption',
                            color_continuous_scale='Reds'
                        )
                        fig_oil_cons.update_layout(**get_clean_plotly_layout(), height=350, showlegend=False)
                        st.plotly_chart(fig_oil_cons, use_container_width=True)

                with col2:
                    gas_cons_data = major_energy[
                        (major_energy['country'].isin(oilgas_countries)) &
                        (major_energy['year'] == latest_year) &
                        (major_energy['gas_consumption'].notna())
                    ].sort_values('gas_consumption', ascending=True)

                    if not gas_cons_data.empty:
                        fig_gas_cons = px.bar(
                            gas_cons_data,
                            x='gas_consumption',
                            y='country',
                            orientation='h',
                            title=f'Gas Consumption ({int(latest_year)})',
                            labels={'gas_consumption': 'TWh', 'country': ''},
                            color='gas_consumption',
                            color_continuous_scale='Blues'
                        )
                        fig_gas_cons.update_layout(**get_clean_plotly_layout(), height=350, showlegend=False)
                        st.plotly_chart(fig_gas_cons, use_container_width=True)

            # Top Oil & Gas Producers Table
            st.markdown("---")
            st.subheader(f"Top Oil & Gas Producers ({int(latest_year)})")

            top_oil = energy_df[
                (energy_df['year'] == latest_year) &
                (energy_df['oil_production'].notna()) &
                (~energy_df['country'].isin(['World', 'Europe', 'Asia Pacific', 'North America', 'Africa', 'OPEC']))
            ].nlargest(15, 'oil_production')[['country', 'oil_production', 'oil_share_energy']].copy()

            top_gas = energy_df[
                (energy_df['year'] == latest_year) &
                (energy_df['gas_production'].notna()) &
                (~energy_df['country'].isin(['World', 'Europe', 'Asia Pacific', 'North America', 'Africa']))
            ].nlargest(15, 'gas_production')[['country', 'gas_production', 'gas_share_energy']].copy()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Top Oil Producers**")
                if not top_oil.empty:
                    top_oil = top_oil.rename(columns={
                        'country': 'Country',
                        'oil_production': 'Production (TWh)',
                        'oil_share_energy': 'Oil % of Energy'
                    })
                    top_oil['Production (TWh)'] = top_oil['Production (TWh)'].apply(lambda x: f"{x:,.0f}")
                    top_oil['Oil % of Energy'] = top_oil['Oil % of Energy'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                    st.dataframe(top_oil, use_container_width=True, hide_index=True, height=400)

            with col2:
                st.markdown("**Top Gas Producers**")
                if not top_gas.empty:
                    top_gas = top_gas.rename(columns={
                        'country': 'Country',
                        'gas_production': 'Production (TWh)',
                        'gas_share_energy': 'Gas % of Energy'
                    })
                    top_gas['Production (TWh)'] = top_gas['Production (TWh)'].apply(lambda x: f"{x:,.0f}")
                    top_gas['Gas % of Energy'] = top_gas['Gas % of Energy'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                    st.dataframe(top_gas, use_container_width=True, hide_index=True, height=400)

        with energy_tab4:
            st.subheader("Nuclear Energy")

            col1, col2 = st.columns([2, 1])
            with col1:
                nuclear_countries = st.multiselect(
                    "Select countries:",
                    options=MAJOR_COUNTRIES,
                    default=['United States', 'France', 'China', 'Russia', 'South Korea', 'Japan'],
                    key="nuclear_countries"
                )

            if nuclear_countries:
                # Nuclear electricity generation
                nuclear_elec_data = major_energy[
                    (major_energy['country'].isin(nuclear_countries)) &
                    (major_energy['year'] >= 1970) &
                    (major_energy['nuclear_electricity'].notna())
                ]

                if not nuclear_elec_data.empty:
                    fig_nuclear = px.line(
                        nuclear_elec_data,
                        x='year',
                        y='nuclear_electricity',
                        color='country',
                        title='Nuclear Electricity Generation (TWh)',
                        labels={'nuclear_electricity': 'TWh', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_nuclear.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_nuclear, use_container_width=True)

                # Nuclear share of electricity
                st.markdown("---")
                st.markdown("### Nuclear Share of Electricity Mix")

                nuclear_share_data = major_energy[
                    (major_energy['country'].isin(nuclear_countries)) &
                    (major_energy['year'] >= 1980) &
                    (major_energy['nuclear_share_elec'].notna())
                ]

                if not nuclear_share_data.empty:
                    fig_nuclear_share = px.line(
                        nuclear_share_data,
                        x='year',
                        y='nuclear_share_elec',
                        color='country',
                        title='Nuclear Share of Electricity (%)',
                        labels={'nuclear_share_elec': '% of Electricity', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_nuclear_share.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_nuclear_share, use_container_width=True)

                # Latest year comparison
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Nuclear Generation")
                    nuclear_latest = major_energy[
                        (major_energy['country'].isin(nuclear_countries)) &
                        (major_energy['year'] == latest_year) &
                        (major_energy['nuclear_electricity'].notna())
                    ].sort_values('nuclear_electricity', ascending=True)

                    if not nuclear_latest.empty:
                        fig_nuc_bar = px.bar(
                            nuclear_latest,
                            x='nuclear_electricity',
                            y='country',
                            orientation='h',
                            title=f'Nuclear Generation ({int(latest_year)})',
                            labels={'nuclear_electricity': 'TWh', 'country': ''},
                            color='nuclear_electricity',
                            color_continuous_scale='Purples'
                        )
                        fig_nuc_bar.update_layout(**get_clean_plotly_layout(), height=350, showlegend=False)
                        st.plotly_chart(fig_nuc_bar, use_container_width=True)

                with col2:
                    st.markdown("### Nuclear % of Mix")
                    nuclear_pct = major_energy[
                        (major_energy['country'].isin(nuclear_countries)) &
                        (major_energy['year'] == latest_year) &
                        (major_energy['nuclear_share_elec'].notna())
                    ].sort_values('nuclear_share_elec', ascending=True)

                    if not nuclear_pct.empty:
                        fig_nuc_pct = px.bar(
                            nuclear_pct,
                            x='nuclear_share_elec',
                            y='country',
                            orientation='h',
                            title=f'Nuclear Share ({int(latest_year)})',
                            labels={'nuclear_share_elec': '% of Electricity', 'country': ''},
                            color='nuclear_share_elec',
                            color_continuous_scale='Purples'
                        )
                        fig_nuc_pct.update_layout(**get_clean_plotly_layout(), height=350, showlegend=False)
                        st.plotly_chart(fig_nuc_pct, use_container_width=True)

            # Top Nuclear Countries Table
            st.markdown("---")
            st.subheader(f"Top Nuclear Energy Countries ({int(latest_year)})")

            top_nuclear = energy_df[
                (energy_df['year'] == latest_year) &
                (energy_df['nuclear_electricity'].notna()) &
                (energy_df['nuclear_electricity'] > 0) &
                (~energy_df['country'].isin(['World', 'Europe', 'Asia Pacific', 'North America', 'Africa']))
            ].nlargest(20, 'nuclear_electricity')[['country', 'nuclear_electricity', 'nuclear_share_elec', 'nuclear_consumption']].copy()

            if not top_nuclear.empty:
                top_nuclear = top_nuclear.rename(columns={
                    'country': 'Country',
                    'nuclear_electricity': 'Generation (TWh)',
                    'nuclear_share_elec': 'Nuclear % of Elec',
                    'nuclear_consumption': 'Consumption (TWh)'
                })
                top_nuclear['Generation (TWh)'] = top_nuclear['Generation (TWh)'].apply(lambda x: f"{x:,.0f}")
                top_nuclear['Nuclear % of Elec'] = top_nuclear['Nuclear % of Elec'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
                top_nuclear['Consumption (TWh)'] = top_nuclear['Consumption (TWh)'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(top_nuclear, use_container_width=True, hide_index=True)

            # Nuclear fun fact
            st.info("France generates ~70% of its electricity from nuclear power, the highest share in the world.")

        with energy_tab5:
            st.subheader("Renewable Energy Adoption")

            col1, col2 = st.columns([2, 1])
            with col1:
                renewable_countries = st.multiselect(
                    "Select countries:",
                    options=MAJOR_COUNTRIES,
                    default=['Germany', 'United Kingdom', 'China', 'United States', 'India'],
                    key="renewable_countries"
                )

            if renewable_countries:
                renewable_data = major_energy[
                    (major_energy['country'].isin(renewable_countries)) &
                    (major_energy['year'] >= 2000) &
                    (major_energy['renewables_share_elec'].notna())
                ]

                if not renewable_data.empty:
                    # Renewable share over time
                    fig_renew = px.line(
                        renewable_data,
                        x='year',
                        y='renewables_share_elec',
                        color='country',
                        title='Renewable Energy Share of Electricity (%)',
                        labels={'renewables_share_elec': '% Renewable', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_renew.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_renew, use_container_width=True)

                    # Solar growth
                    st.markdown("---")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("Solar Energy Growth")
                        solar_data = major_energy[
                            (major_energy['country'].isin(renewable_countries)) &
                            (major_energy['year'] >= 2010) &
                            (major_energy['solar_electricity'].notna())
                        ]
                        if not solar_data.empty:
                            fig_solar = px.line(
                                solar_data,
                                x='year',
                                y='solar_electricity',
                                color='country',
                                title='Solar Electricity Generation (TWh)',
                                labels={'solar_electricity': 'TWh', 'year': 'Year'}
                            )
                            fig_solar.update_layout(**get_clean_plotly_layout(), height=350)
                            st.plotly_chart(fig_solar, use_container_width=True)

                    with col2:
                        st.subheader("Wind Energy Growth")
                        wind_data = major_energy[
                            (major_energy['country'].isin(renewable_countries)) &
                            (major_energy['year'] >= 2000) &
                            (major_energy['wind_electricity'].notna())
                        ]
                        if not wind_data.empty:
                            fig_wind = px.line(
                                wind_data,
                                x='year',
                                y='wind_electricity',
                                color='country',
                                title='Wind Electricity Generation (TWh)',
                                labels={'wind_electricity': 'TWh', 'year': 'Year'}
                            )
                            fig_wind.update_layout(**get_clean_plotly_layout(), height=350)
                            st.plotly_chart(fig_wind, use_container_width=True)

            # Top renewable countries table
            st.markdown("---")
            st.subheader(f"Top Renewable Energy Countries ({int(latest_year)})")

            top_renewable = energy_df[
                (energy_df['year'] == latest_year) &
                (energy_df['renewables_share_elec'].notna()) &
                (~energy_df['country'].isin(['World', 'Europe', 'Asia Pacific', 'North America', 'Africa']))
            ].nlargest(15, 'renewables_share_elec')[['country', 'renewables_share_elec', 'renewables_electricity']].copy()

            if not top_renewable.empty:
                top_renewable = top_renewable.rename(columns={
                    'country': 'Country',
                    'renewables_share_elec': 'Renewable %',
                    'renewables_electricity': 'Renewable TWh'
                })
                top_renewable['Renewable %'] = top_renewable['Renewable %'].apply(lambda x: f"{x:.1f}%")
                top_renewable['Renewable TWh'] = top_renewable['Renewable TWh'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(top_renewable, use_container_width=True, hide_index=True)

        with energy_tab6:
            st.subheader("CO2 Emissions from Electricity")

            col1, col2 = st.columns([2, 1])
            with col1:
                emission_countries = st.multiselect(
                    "Select countries:",
                    options=MAJOR_COUNTRIES,
                    default=['China', 'United States', 'India', 'Russia', 'Japan'],
                    key="emission_countries"
                )

            if emission_countries:
                # Carbon intensity over time
                carbon_data = major_energy[
                    (major_energy['country'].isin(emission_countries)) &
                    (major_energy['year'] >= 2000) &
                    (major_energy['carbon_intensity_elec'].notna())
                ]

                if not carbon_data.empty:
                    fig_carbon = px.line(
                        carbon_data,
                        x='year',
                        y='carbon_intensity_elec',
                        color='country',
                        title='Carbon Intensity of Electricity (gCO2/kWh)',
                        labels={'carbon_intensity_elec': 'gCO2/kWh', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_carbon.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_carbon, use_container_width=True)

                # Primary energy consumption
                st.markdown("---")
                st.subheader("Primary Energy Consumption")

                primary_data = major_energy[
                    (major_energy['country'].isin(emission_countries)) &
                    (major_energy['year'] >= 1990) &
                    (major_energy['primary_energy_consumption'].notna())
                ]

                if not primary_data.empty:
                    fig_primary = px.line(
                        primary_data,
                        x='year',
                        y='primary_energy_consumption',
                        color='country',
                        title='Primary Energy Consumption (TWh)',
                        labels={'primary_energy_consumption': 'TWh', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_primary.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_primary, use_container_width=True)

                # Fossil fuel consumption breakdown
                st.markdown("---")
                st.subheader("Fossil Fuel Consumption")

                fossil_data = major_energy[
                    (major_energy['country'].isin(emission_countries)) &
                    (major_energy['year'] >= 2000)
                ][['year', 'country', 'coal_consumption', 'gas_consumption', 'oil_consumption']].copy()

                if not fossil_data.empty:
                    latest_fossil = fossil_data[fossil_data['year'] == fossil_data['year'].max()]

                    if not latest_fossil.empty:
                        fossil_melted = latest_fossil.melt(
                            id_vars=['country'],
                            value_vars=['coal_consumption', 'gas_consumption', 'oil_consumption'],
                            var_name='Fuel',
                            value_name='Consumption'
                        )
                        fossil_melted['Fuel'] = fossil_melted['Fuel'].str.replace('_consumption', '').str.title()

                        fig_fossil = px.bar(
                            fossil_melted,
                            x='country',
                            y='Consumption',
                            color='Fuel',
                            barmode='group',
                            title=f'Fossil Fuel Consumption by Type ({int(latest_fossil["year"].max())})',
                            labels={'Consumption': 'TWh', 'country': 'Country'}
                        )
                        fig_fossil.update_layout(**get_clean_plotly_layout(), height=400)
                        st.plotly_chart(fig_fossil, use_container_width=True)

        with energy_tab7:
            st.subheader("Per Capita Energy Consumption")

            col1, col2 = st.columns([2, 1])
            with col1:
                percap_countries = st.multiselect(
                    "Select countries:",
                    options=MAJOR_COUNTRIES,
                    default=['United States', 'Germany', 'China', 'India', 'Brazil'],
                    key="percap_countries"
                )

            if percap_countries:
                percap_data = major_energy[
                    (major_energy['country'].isin(percap_countries)) &
                    (major_energy['year'] >= 1990) &
                    (major_energy['per_capita_electricity'].notna())
                ]

                if not percap_data.empty:
                    # Per capita electricity
                    fig_percap = px.line(
                        percap_data,
                        x='year',
                        y='per_capita_electricity',
                        color='country',
                        title='Electricity Consumption Per Capita (kWh)',
                        labels={'per_capita_electricity': 'kWh per person', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_percap.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_percap, use_container_width=True)

                # Energy use per GDP
                st.markdown("---")
                st.subheader("Energy Intensity (Energy per GDP)")

                intensity_data = major_energy[
                    (major_energy['country'].isin(percap_countries)) &
                    (major_energy['year'] >= 2000) &
                    (major_energy['energy_per_gdp'].notna())
                ]

                if not intensity_data.empty:
                    fig_intensity = px.line(
                        intensity_data,
                        x='year',
                        y='energy_per_gdp',
                        color='country',
                        title='Energy per Unit GDP (kWh/$)',
                        labels={'energy_per_gdp': 'kWh per $', 'year': 'Year', 'country': 'Country'}
                    )
                    fig_intensity.update_layout(**get_clean_plotly_layout(), height=400)
                    st.plotly_chart(fig_intensity, use_container_width=True)

            # Global comparison table
            st.markdown("---")
            st.subheader(f"Per Capita Comparison ({int(latest_year)})")

            percap_table = energy_df[
                (energy_df['year'] == latest_year) &
                (energy_df['per_capita_electricity'].notna()) &
                (~energy_df['country'].isin(['World', 'Europe', 'Asia Pacific', 'North America', 'Africa']))
            ].nlargest(20, 'per_capita_electricity')[['country', 'per_capita_electricity', 'energy_per_gdp']].copy()

            if not percap_table.empty:
                percap_table = percap_table.rename(columns={
                    'country': 'Country',
                    'per_capita_electricity': 'Electricity (kWh/person)',
                    'energy_per_gdp': 'Energy Intensity (kWh/$)'
                })
                percap_table['Electricity (kWh/person)'] = percap_table['Electricity (kWh/person)'].apply(lambda x: f"{x:,.0f}")
                percap_table['Energy Intensity (kWh/$)'] = percap_table['Energy Intensity (kWh/$)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
                st.dataframe(percap_table, use_container_width=True, hide_index=True)

        with energy_tab8:
            st.subheader("Global Mining & Critical Resources")
            st.markdown("*World production, exports, and imports of key mineral resources*")

            # Curated mining data from USGS Mineral Commodity Summaries 2024 & World Mining Data 2024
            # Production figures in thousand metric tons unless otherwise noted

            MINING_DATA = {
                'Lithium': {
                    'unit': 'metric tons Li content',
                    'total_world': 180000,
                    'producers': [
                        ('Australia', 86000, 47.8),
                        ('Chile', 44000, 24.4),
                        ('China', 33000, 18.3),
                        ('Argentina', 9600, 5.3),
                        ('Brazil', 4900, 2.7),
                        ('Zimbabwe', 3400, 1.9),
                        ('Portugal', 490, 0.3),
                        ('USA', 0, 0.0),
                    ],
                    'top_exporters': ['Australia', 'Chile', 'Argentina'],
                    'top_importers': ['China', 'South Korea', 'Japan', 'USA', 'EU'],
                    'use': 'EV batteries, electronics, energy storage',
                    'criticality': 'Critical'
                },
                'Cobalt': {
                    'unit': 'metric tons',
                    'total_world': 230000,
                    'producers': [
                        ('DR Congo', 170000, 73.9),
                        ('Indonesia', 17000, 7.4),
                        ('Russia', 8900, 3.9),
                        ('Australia', 5600, 2.4),
                        ('Philippines', 4800, 2.1),
                        ('Cuba', 3800, 1.7),
                        ('Canada', 3400, 1.5),
                        ('Madagascar', 2800, 1.2),
                    ],
                    'top_exporters': ['DR Congo', 'Indonesia', 'Australia'],
                    'top_importers': ['China', 'Finland', 'Belgium', 'Japan'],
                    'use': 'EV batteries, superalloys, catalysts',
                    'criticality': 'Critical'
                },
                'Rare Earth Elements': {
                    'unit': 'metric tons REO',
                    'total_world': 350000,
                    'producers': [
                        ('China', 240000, 68.6),
                        ('USA', 43000, 12.3),
                        ('Australia', 18000, 5.1),
                        ('Myanmar', 17000, 4.9),
                        ('Thailand', 7100, 2.0),
                        ('India', 6000, 1.7),
                        ('Russia', 5400, 1.5),
                        ('Vietnam', 4300, 1.2),
                    ],
                    'top_exporters': ['China', 'Myanmar', 'Australia'],
                    'top_importers': ['Japan', 'USA', 'EU', 'South Korea'],
                    'use': 'Magnets, EV motors, wind turbines, electronics',
                    'criticality': 'Critical'
                },
                'Copper': {
                    'unit': 'thousand metric tons',
                    'total_world': 22000,
                    'producers': [
                        ('Chile', 5300, 24.1),
                        ('Peru', 2700, 12.3),
                        ('DR Congo', 2500, 11.4),
                        ('China', 1900, 8.6),
                        ('USA', 1100, 5.0),
                        ('Indonesia', 1000, 4.5),
                        ('Russia', 920, 4.2),
                        ('Australia', 870, 4.0),
                    ],
                    'top_exporters': ['Chile', 'Peru', 'Australia', 'Indonesia'],
                    'top_importers': ['China', 'Japan', 'Germany', 'South Korea'],
                    'use': 'Electrical wiring, construction, EVs, electronics',
                    'criticality': 'High'
                },
                'Nickel': {
                    'unit': 'thousand metric tons',
                    'total_world': 3600,
                    'producers': [
                        ('Indonesia', 1800, 50.0),
                        ('Philippines', 400, 11.1),
                        ('Russia', 220, 6.1),
                        ('New Caledonia', 190, 5.3),
                        ('Australia', 160, 4.4),
                        ('Canada', 130, 3.6),
                        ('China', 120, 3.3),
                        ('Brazil', 83, 2.3),
                    ],
                    'top_exporters': ['Indonesia', 'Philippines', 'Russia'],
                    'top_importers': ['China', 'Japan', 'EU', 'USA'],
                    'use': 'Stainless steel, EV batteries, alloys',
                    'criticality': 'High'
                },
                'Iron Ore': {
                    'unit': 'million metric tons',
                    'total_world': 2500,
                    'producers': [
                        ('Australia', 960, 38.4),
                        ('Brazil', 440, 17.6),
                        ('China', 310, 12.4),
                        ('India', 290, 11.6),
                        ('Russia', 110, 4.4),
                        ('Ukraine', 81, 3.2),
                        ('South Africa', 68, 2.7),
                        ('Canada', 67, 2.7),
                    ],
                    'top_exporters': ['Australia', 'Brazil', 'South Africa'],
                    'top_importers': ['China', 'Japan', 'South Korea', 'EU'],
                    'use': 'Steel production, construction, automotive',
                    'criticality': 'Medium'
                },
                'Aluminum (Bauxite)': {
                    'unit': 'million metric tons',
                    'total_world': 400,
                    'producers': [
                        ('Australia', 100, 25.0),
                        ('Guinea', 95, 23.8),
                        ('China', 90, 22.5),
                        ('Brazil', 34, 8.5),
                        ('Indonesia', 23, 5.8),
                        ('India', 23, 5.8),
                        ('Jamaica', 8, 2.0),
                        ('Russia', 6, 1.5),
                    ],
                    'top_exporters': ['Australia', 'Guinea', 'Brazil', 'Indonesia'],
                    'top_importers': ['China', 'EU', 'USA', 'Japan'],
                    'use': 'Transportation, packaging, construction, electronics',
                    'criticality': 'Medium'
                },
                'Gold': {
                    'unit': 'metric tons',
                    'total_world': 3100,
                    'producers': [
                        ('China', 370, 11.9),
                        ('Australia', 310, 10.0),
                        ('Russia', 310, 10.0),
                        ('Canada', 200, 6.5),
                        ('USA', 170, 5.5),
                        ('Mexico', 120, 3.9),
                        ('Ghana', 110, 3.5),
                        ('South Africa', 100, 3.2),
                    ],
                    'top_exporters': ['Switzerland', 'Hong Kong', 'UAE', 'UK'],
                    'top_importers': ['India', 'China', 'Switzerland', 'UAE'],
                    'use': 'Jewelry, investment, electronics, dentistry',
                    'criticality': 'Low'
                },
                'Silver': {
                    'unit': 'metric tons',
                    'total_world': 26000,
                    'producers': [
                        ('Mexico', 6300, 24.2),
                        ('China', 3400, 13.1),
                        ('Peru', 3100, 11.9),
                        ('Chile', 1400, 5.4),
                        ('Australia', 1300, 5.0),
                        ('Poland', 1300, 5.0),
                        ('Russia', 1200, 4.6),
                        ('Bolivia', 1100, 4.2),
                    ],
                    'top_exporters': ['Mexico', 'Peru', 'China', 'Poland'],
                    'top_importers': ['USA', 'UK', 'India', 'Japan'],
                    'use': 'Electronics, solar panels, jewelry, photography',
                    'criticality': 'Medium'
                },
                'Platinum Group Metals': {
                    'unit': 'metric tons',
                    'total_world': 480,
                    'producers': [
                        ('South Africa', 300, 62.5),
                        ('Russia', 90, 18.8),
                        ('Zimbabwe', 38, 7.9),
                        ('Canada', 17, 3.5),
                        ('USA', 14, 2.9),
                        ('Other', 21, 4.4),
                    ],
                    'top_exporters': ['South Africa', 'Russia', 'Zimbabwe'],
                    'top_importers': ['Germany', 'USA', 'Japan', 'UK'],
                    'use': 'Catalytic converters, jewelry, electronics, hydrogen fuel cells',
                    'criticality': 'Critical'
                },
                'Uranium': {
                    'unit': 'metric tons U',
                    'total_world': 58500,
                    'producers': [
                        ('Kazakhstan', 21200, 36.2),
                        ('Canada', 7400, 12.6),
                        ('Namibia', 5600, 9.6),
                        ('Australia', 4100, 7.0),
                        ('Uzbekistan', 3500, 6.0),
                        ('Russia', 2600, 4.4),
                        ('Niger', 2000, 3.4),
                        ('China', 1700, 2.9),
                    ],
                    'top_exporters': ['Kazakhstan', 'Canada', 'Australia', 'Namibia'],
                    'top_importers': ['USA', 'France', 'China', 'Japan', 'South Korea'],
                    'use': 'Nuclear power generation',
                    'criticality': 'High'
                },
                'Zinc': {
                    'unit': 'thousand metric tons',
                    'total_world': 13000,
                    'producers': [
                        ('China', 4200, 32.3),
                        ('Peru', 1500, 11.5),
                        ('Australia', 1400, 10.8),
                        ('India', 800, 6.2),
                        ('USA', 720, 5.5),
                        ('Mexico', 670, 5.2),
                        ('Bolivia', 550, 4.2),
                        ('Kazakhstan', 380, 2.9),
                    ],
                    'top_exporters': ['Australia', 'Peru', 'USA'],
                    'top_importers': ['China', 'South Korea', 'Belgium'],
                    'use': 'Galvanizing steel, alloys, batteries',
                    'criticality': 'Medium'
                },
            }

            # Mineral selector
            mining_subtabs = st.tabs(["Critical Minerals", "Industrial Metals", "Precious Metals", "Trade Flows"])

            with mining_subtabs[0]:
                st.markdown("##### Critical Minerals for Clean Energy Transition")
                critical_minerals = ['Lithium', 'Cobalt', 'Rare Earth Elements', 'Nickel', 'Platinum Group Metals']

                selected_critical = st.selectbox(
                    "Select mineral:",
                    critical_minerals,
                    key="critical_mineral_select"
                )

                mineral_data = MINING_DATA[selected_critical]

                # Info card
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("World Production", f"{mineral_data['total_world']:,} {mineral_data['unit'].split()[0]}")
                with col2:
                    st.metric("Primary Use", mineral_data['use'].split(',')[0])
                with col3:
                    criticality_color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
                    st.metric("Supply Risk", f"{criticality_color.get(mineral_data['criticality'], '⚪')} {mineral_data['criticality']}")

                st.markdown(f"**Applications:** {mineral_data['use']}")

                # Production chart
                prod_df = pd.DataFrame(mineral_data['producers'], columns=['Country', 'Production', 'Share %'])

                fig_prod = px.bar(
                    prod_df,
                    x='Production',
                    y='Country',
                    orientation='h',
                    title=f'{selected_critical} Production by Country ({mineral_data["unit"]})',
                    color='Share %',
                    color_continuous_scale='Viridis'
                )
                fig_prod.update_layout(**get_clean_plotly_layout(), height=400)
                fig_prod.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig_prod, use_container_width=True)

                # Pie chart
                fig_pie = px.pie(
                    prod_df,
                    values='Production',
                    names='Country',
                    title=f'{selected_critical} Global Market Share'
                )
                fig_pie.update_layout(**get_clean_plotly_layout(), height=350)
                st.plotly_chart(fig_pie, use_container_width=True)

                # Trade info
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top Exporters:**")
                    for exp in mineral_data['top_exporters']:
                        st.markdown(f"- 📤 {exp}")
                with col2:
                    st.markdown("**Top Importers:**")
                    for imp in mineral_data['top_importers']:
                        st.markdown(f"- 📥 {imp}")

            with mining_subtabs[1]:
                st.markdown("##### Industrial Metals Production")
                industrial_metals = ['Iron Ore', 'Copper', 'Aluminum (Bauxite)', 'Zinc']

                selected_industrial = st.selectbox(
                    "Select metal:",
                    industrial_metals,
                    key="industrial_metal_select"
                )

                metal_data = MINING_DATA[selected_industrial]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("World Production", f"{metal_data['total_world']:,} {metal_data['unit'].split()[0]}")
                with col2:
                    st.metric("Primary Use", metal_data['use'].split(',')[0])
                with col3:
                    criticality_color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
                    st.metric("Supply Risk", f"{criticality_color.get(metal_data['criticality'], '⚪')} {metal_data['criticality']}")

                st.markdown(f"**Applications:** {metal_data['use']}")

                prod_df = pd.DataFrame(metal_data['producers'], columns=['Country', 'Production', 'Share %'])

                fig_prod = px.bar(
                    prod_df,
                    x='Production',
                    y='Country',
                    orientation='h',
                    title=f'{selected_industrial} Production by Country ({metal_data["unit"]})',
                    color='Share %',
                    color_continuous_scale='Blues'
                )
                fig_prod.update_layout(**get_clean_plotly_layout(), height=400)
                fig_prod.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig_prod, use_container_width=True)

                fig_pie = px.pie(
                    prod_df,
                    values='Production',
                    names='Country',
                    title=f'{selected_industrial} Global Market Share'
                )
                fig_pie.update_layout(**get_clean_plotly_layout(), height=350)
                st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top Exporters:**")
                    for exp in metal_data['top_exporters']:
                        st.markdown(f"- 📤 {exp}")
                with col2:
                    st.markdown("**Top Importers:**")
                    for imp in metal_data['top_importers']:
                        st.markdown(f"- 📥 {imp}")

            with mining_subtabs[2]:
                st.markdown("##### Precious Metals Production")
                precious_metals = ['Gold', 'Silver', 'Platinum Group Metals']

                selected_precious = st.selectbox(
                    "Select metal:",
                    precious_metals,
                    key="precious_metal_select"
                )

                precious_data = MINING_DATA[selected_precious]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("World Production", f"{precious_data['total_world']:,} {precious_data['unit'].split()[0]}")
                with col2:
                    st.metric("Primary Use", precious_data['use'].split(',')[0])
                with col3:
                    criticality_color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
                    st.metric("Supply Risk", f"{criticality_color.get(precious_data['criticality'], '⚪')} {precious_data['criticality']}")

                st.markdown(f"**Applications:** {precious_data['use']}")

                prod_df = pd.DataFrame(precious_data['producers'], columns=['Country', 'Production', 'Share %'])

                fig_prod = px.bar(
                    prod_df,
                    x='Production',
                    y='Country',
                    orientation='h',
                    title=f'{selected_precious} Production by Country ({precious_data["unit"]})',
                    color='Share %',
                    color_continuous_scale='YlOrRd'
                )
                fig_prod.update_layout(**get_clean_plotly_layout(), height=400)
                fig_prod.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig_prod, use_container_width=True)

                fig_pie = px.pie(
                    prod_df,
                    values='Production',
                    names='Country',
                    title=f'{selected_precious} Global Market Share'
                )
                fig_pie.update_layout(**get_clean_plotly_layout(), height=350)
                st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top Exporters:**")
                    for exp in precious_data['top_exporters']:
                        st.markdown(f"- 📤 {exp}")
                with col2:
                    st.markdown("**Top Importers:**")
                    for imp in precious_data['top_importers']:
                        st.markdown(f"- 📥 {imp}")

            with mining_subtabs[3]:
                st.markdown("##### Global Resource Trade Flows")
                st.markdown("*Understanding who exports what and who depends on imports*")

                # Summary table of all minerals
                summary_data = []
                for mineral, data in MINING_DATA.items():
                    top_producer = data['producers'][0][0] if data['producers'] else 'N/A'
                    top_share = data['producers'][0][2] if data['producers'] else 0
                    summary_data.append({
                        'Mineral': mineral,
                        'Top Producer': top_producer,
                        'Market Share': f"{top_share:.1f}%",
                        'World Production': f"{data['total_world']:,}",
                        'Unit': data['unit'],
                        'Criticality': data['criticality']
                    })

                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("##### Major Exporting Countries")

                # Aggregate export dominance
                export_counts = {}
                for mineral, data in MINING_DATA.items():
                    for exp in data['top_exporters']:
                        if exp not in export_counts:
                            export_counts[exp] = []
                        export_counts[exp].append(mineral)

                export_df = pd.DataFrame([
                    {'Country': k, 'Resources Exported': len(v), 'Resources': ', '.join(v[:3]) + ('...' if len(v) > 3 else '')}
                    for k, v in sorted(export_counts.items(), key=lambda x: -len(x[1]))
                ])

                fig_export = px.bar(
                    export_df.head(15),
                    x='Resources Exported',
                    y='Country',
                    orientation='h',
                    title='Top Resource Exporting Countries (by number of minerals)',
                    hover_data=['Resources']
                )
                fig_export.update_layout(**get_clean_plotly_layout(), height=400)
                fig_export.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig_export, use_container_width=True)

                st.markdown("---")
                st.markdown("##### Major Importing Countries")

                import_counts = {}
                for mineral, data in MINING_DATA.items():
                    for imp in data['top_importers']:
                        if imp not in import_counts:
                            import_counts[imp] = []
                        import_counts[imp].append(mineral)

                import_df = pd.DataFrame([
                    {'Country': k, 'Resources Imported': len(v), 'Resources': ', '.join(v[:3]) + ('...' if len(v) > 3 else '')}
                    for k, v in sorted(import_counts.items(), key=lambda x: -len(x[1]))
                ])

                fig_import = px.bar(
                    import_df.head(15),
                    x='Resources Imported',
                    y='Country',
                    orientation='h',
                    title='Top Resource Importing Countries (by number of minerals)',
                    hover_data=['Resources'],
                    color_discrete_sequence=['#e74c3c']
                )
                fig_import.update_layout(**get_clean_plotly_layout(), height=400)
                fig_import.update_yaxes(categoryorder='total ascending')
                st.plotly_chart(fig_import, use_container_width=True)

                # Supply chain risk analysis
                st.markdown("---")
                st.markdown("##### Supply Concentration Risk")
                st.markdown("*Minerals where a single country controls >50% of production*")

                concentration_risk = []
                for mineral, data in MINING_DATA.items():
                    if data['producers'] and data['producers'][0][2] > 50:
                        concentration_risk.append({
                            'Mineral': mineral,
                            'Dominant Producer': data['producers'][0][0],
                            'Share': f"{data['producers'][0][2]:.1f}%",
                            'Criticality': data['criticality']
                        })

                if concentration_risk:
                    risk_df = pd.DataFrame(concentration_risk)
                    st.dataframe(risk_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No minerals with >50% single-country concentration.")

            st.markdown("---")
            st.caption("Data sources: USGS Mineral Commodity Summaries 2024, World Mining Data 2024 (Austrian Federal Ministry of Finance)")
            st.caption("Trade flow data based on UN Comtrade and industry reports. Production figures are estimates for 2023.")

        # Data source attribution
        st.markdown("---")
        st.caption("Data source: Our World in Data - Energy Dataset (https://github.com/owid/energy-data)")
        st.caption("Updated annually. Data includes 200+ countries from 1900-present.")

    else:
        st.error("Unable to load energy data. Please check your internet connection.")


# ============================================================================
# PAGE: AGRICULTURE & FOOD
# ============================================================================

elif page == "Agriculture & Food":
    st.title("Agriculture & Food Security")
    st.markdown("*Global crop production, food prices, and food security metrics*")
    st.markdown("---")

    # Curated agricultural data from FAO, USDA, and World Bank (2023 estimates)

    # Major crop production data (million metric tons)
    CROP_PRODUCTION = {
        'Wheat': {
            'world_total': 783,
            'unit': 'million metric tons',
            'producers': [
                ('China', 137, 17.5),
                ('India', 110, 14.0),
                ('Russia', 92, 11.7),
                ('United States', 49, 6.3),
                ('France', 35, 4.5),
                ('Canada', 34, 4.3),
                ('Ukraine', 21, 2.7),
                ('Pakistan', 27, 3.4),
                ('Germany', 22, 2.8),
                ('Australia', 26, 3.3),
            ],
            'top_exporters': ['Russia', 'EU', 'Australia', 'Canada', 'USA', 'Ukraine'],
            'top_importers': ['Egypt', 'Indonesia', 'Turkey', 'Algeria', 'Philippines', 'Nigeria'],
        },
        'Rice': {
            'world_total': 518,
            'unit': 'million metric tons (milled)',
            'producers': [
                ('China', 146, 28.2),
                ('India', 135, 26.1),
                ('Bangladesh', 37, 7.1),
                ('Indonesia', 34, 6.6),
                ('Vietnam', 27, 5.2),
                ('Thailand', 20, 3.9),
                ('Myanmar', 13, 2.5),
                ('Philippines', 13, 2.5),
                ('Brazil', 8, 1.5),
                ('Japan', 8, 1.5),
            ],
            'top_exporters': ['India', 'Thailand', 'Vietnam', 'Pakistan', 'USA'],
            'top_importers': ['China', 'Philippines', 'EU', 'Saudi Arabia', 'Ivory Coast'],
        },
        'Corn (Maize)': {
            'world_total': 1147,
            'unit': 'million metric tons',
            'producers': [
                ('United States', 383, 33.4),
                ('China', 277, 24.1),
                ('Brazil', 127, 11.1),
                ('Argentina', 50, 4.4),
                ('Ukraine', 27, 2.4),
                ('India', 35, 3.1),
                ('Mexico', 27, 2.4),
                ('Indonesia', 20, 1.7),
                ('South Africa', 16, 1.4),
                ('France', 12, 1.0),
            ],
            'top_exporters': ['USA', 'Brazil', 'Argentina', 'Ukraine', 'France'],
            'top_importers': ['China', 'EU', 'Japan', 'Mexico', 'South Korea', 'Egypt'],
        },
        'Soybeans': {
            'world_total': 370,
            'unit': 'million metric tons',
            'producers': [
                ('Brazil', 154, 41.6),
                ('United States', 113, 30.5),
                ('Argentina', 43, 11.6),
                ('China', 20, 5.4),
                ('India', 13, 3.5),
                ('Paraguay', 10, 2.7),
                ('Canada', 7, 1.9),
                ('Russia', 6, 1.6),
                ('Ukraine', 4, 1.1),
                ('Bolivia', 3, 0.8),
            ],
            'top_exporters': ['Brazil', 'USA', 'Argentina', 'Paraguay', 'Canada'],
            'top_importers': ['China', 'EU', 'Mexico', 'Japan', 'Thailand'],
        },
        'Sugar': {
            'world_total': 179,
            'unit': 'million metric tons (raw)',
            'producers': [
                ('Brazil', 42, 23.5),
                ('India', 36, 20.1),
                ('EU', 16, 8.9),
                ('China', 10, 5.6),
                ('Thailand', 11, 6.1),
                ('United States', 8, 4.5),
                ('Pakistan', 7, 3.9),
                ('Mexico', 6, 3.4),
                ('Russia', 6, 3.4),
                ('Australia', 5, 2.8),
            ],
            'top_exporters': ['Brazil', 'Thailand', 'India', 'Australia', 'Guatemala'],
            'top_importers': ['Indonesia', 'China', 'USA', 'EU', 'Bangladesh'],
        },
        'Coffee': {
            'world_total': 10.5,
            'unit': 'million metric tons',
            'producers': [
                ('Brazil', 3.1, 29.5),
                ('Vietnam', 1.9, 18.1),
                ('Colombia', 0.75, 7.1),
                ('Indonesia', 0.67, 6.4),
                ('Ethiopia', 0.50, 4.8),
                ('Honduras', 0.40, 3.8),
                ('Uganda', 0.38, 3.6),
                ('Peru', 0.35, 3.3),
                ('India', 0.33, 3.1),
                ('Guatemala', 0.23, 2.2),
            ],
            'top_exporters': ['Brazil', 'Vietnam', 'Colombia', 'Indonesia', 'Honduras'],
            'top_importers': ['USA', 'Germany', 'France', 'Italy', 'Japan'],
        },
        'Palm Oil': {
            'world_total': 77,
            'unit': 'million metric tons',
            'producers': [
                ('Indonesia', 46, 59.7),
                ('Malaysia', 18, 23.4),
                ('Thailand', 3.3, 4.3),
                ('Colombia', 1.8, 2.3),
                ('Nigeria', 1.4, 1.8),
                ('Guatemala', 0.9, 1.2),
                ('Papua New Guinea', 0.7, 0.9),
                ('Honduras', 0.6, 0.8),
                ('Ecuador', 0.6, 0.8),
                ('Brazil', 0.5, 0.6),
            ],
            'top_exporters': ['Indonesia', 'Malaysia', 'Guatemala', 'Papua New Guinea'],
            'top_importers': ['India', 'China', 'EU', 'Pakistan', 'USA'],
        },
    }

    # Fertilizer production (million metric tons)
    FERTILIZER_DATA = {
        'Nitrogen (N)': {
            'world_total': 150,
            'producers': [
                ('China', 42, 28.0),
                ('Russia', 14, 9.3),
                ('India', 13, 8.7),
                ('United States', 11, 7.3),
                ('Indonesia', 7, 4.7),
                ('EU', 10, 6.7),
                ('Saudi Arabia', 5, 3.3),
                ('Egypt', 4, 2.7),
                ('Canada', 4, 2.7),
                ('Qatar', 4, 2.7),
            ],
        },
        'Phosphate (P2O5)': {
            'world_total': 47,
            'producers': [
                ('China', 17, 36.2),
                ('Morocco', 6, 12.8),
                ('USA', 4, 8.5),
                ('Russia', 4, 8.5),
                ('India', 3, 6.4),
                ('Brazil', 2, 4.3),
                ('Saudi Arabia', 2, 4.3),
                ('Egypt', 1.5, 3.2),
                ('Vietnam', 1, 2.1),
                ('Tunisia', 1, 2.1),
            ],
        },
        'Potash (K2O)': {
            'world_total': 45,
            'producers': [
                ('Canada', 14, 31.1),
                ('Russia', 9, 20.0),
                ('Belarus', 7, 15.6),
                ('China', 6, 13.3),
                ('Germany', 2.5, 5.6),
                ('Israel', 2, 4.4),
                ('Jordan', 1.5, 3.3),
                ('USA', 0.5, 1.1),
                ('Chile', 0.5, 1.1),
                ('Spain', 0.4, 0.9),
            ],
        },
    }

    # Food Security Index (higher = more secure, scale 0-100)
    FOOD_SECURITY = {
        'Most Food Secure': [
            ('Finland', 83.7),
            ('Ireland', 82.9),
            ('Norway', 81.5),
            ('France', 81.3),
            ('Netherlands', 80.5),
            ('Japan', 79.5),
            ('Canada', 79.3),
            ('Sweden', 79.2),
            ('Germany', 78.8),
            ('Switzerland', 78.3),
            ('USA', 78.0),
            ('UK', 77.8),
            ('Australia', 77.5),
            ('Denmark', 77.2),
            ('New Zealand', 76.8),
        ],
        'Least Food Secure': [
            ('Syria', 36.2),
            ('Yemen', 34.8),
            ('Venezuela', 38.5),
            ('Haiti', 37.4),
            ('Chad', 35.6),
            ('Sudan', 39.2),
            ('Afghanistan', 38.0),
            ('Madagascar', 40.5),
            ('DR Congo', 33.8),
            ('Central African Republic', 31.2),
        ],
    }

    # Agricultural land use (million hectares)
    LAND_USE = {
        'Total Agricultural Land': {
            'world_total': 4800,
            'countries': [
                ('China', 528, 11.0),
                ('USA', 406, 8.5),
                ('Australia', 371, 7.7),
                ('Brazil', 264, 5.5),
                ('Russia', 216, 4.5),
                ('India', 179, 3.7),
                ('Argentina', 148, 3.1),
                ('Kazakhstan', 107, 2.2),
                ('Saudi Arabia', 106, 2.2),
                ('Mexico', 106, 2.2),
            ],
        },
        'Arable Land': {
            'world_total': 1400,
            'countries': [
                ('USA', 158, 11.3),
                ('India', 156, 11.1),
                ('Russia', 122, 8.7),
                ('China', 119, 8.5),
                ('Brazil', 63, 4.5),
                ('Argentina', 39, 2.8),
                ('Canada', 38, 2.7),
                ('Ukraine', 33, 2.4),
                ('Nigeria', 34, 2.4),
                ('Indonesia', 24, 1.7),
            ],
        },
    }

    # Create tabs
    ag_tabs = st.tabs(["Crop Production", "Trade Flows", "Fertilizers", "Food Security", "Land Use"])

    with ag_tabs[0]:
        st.subheader("Global Crop Production")

        selected_crop = st.selectbox(
            "Select crop:",
            list(CROP_PRODUCTION.keys()),
            key="crop_select"
        )

        crop_data = CROP_PRODUCTION[selected_crop]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("World Production", f"{crop_data['world_total']:,} MT")
        with col2:
            top_producer = crop_data['producers'][0]
            st.metric("Top Producer", f"{top_producer[0]}")
        with col3:
            st.metric("Top Producer Share", f"{top_producer[2]:.1f}%")

        # Production bar chart
        prod_df = pd.DataFrame(crop_data['producers'], columns=['Country', 'Production', 'Share %'])

        fig_crop = px.bar(
            prod_df,
            x='Production',
            y='Country',
            orientation='h',
            title=f'{selected_crop} Production by Country ({crop_data["unit"]})',
            color='Share %',
            color_continuous_scale='Greens'
        )
        fig_crop.update_layout(**get_clean_plotly_layout(), height=400)
        fig_crop.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_crop, use_container_width=True)

        # Pie chart
        fig_pie = px.pie(
            prod_df,
            values='Production',
            names='Country',
            title=f'{selected_crop} Global Production Share'
        )
        fig_pie.update_layout(**get_clean_plotly_layout(), height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

        # All crops comparison
        st.markdown("---")
        st.subheader("All Major Crops - Production Comparison")

        all_crops = []
        for crop_name, data in CROP_PRODUCTION.items():
            all_crops.append({
                'Crop': crop_name,
                'World Production (MT)': f"{data['world_total']:,}",
                'Top Producer': data['producers'][0][0],
                'Top Producer Share': f"{data['producers'][0][2]:.1f}%"
            })

        st.dataframe(pd.DataFrame(all_crops), use_container_width=True, hide_index=True)

    with ag_tabs[1]:
        st.subheader("Agricultural Trade Flows")
        st.markdown("*Who feeds the world - major exporters and importers*")

        selected_trade_crop = st.selectbox(
            "Select crop:",
            list(CROP_PRODUCTION.keys()),
            key="trade_crop_select"
        )

        trade_data = CROP_PRODUCTION[selected_trade_crop]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Top Exporters")
            for i, exp in enumerate(trade_data['top_exporters'], 1):
                st.markdown(f"{i}. 📤 **{exp}**")

        with col2:
            st.markdown("##### Top Importers")
            for i, imp in enumerate(trade_data['top_importers'], 1):
                st.markdown(f"{i}. 📥 **{imp}**")

        st.markdown("---")

        # Aggregate export/import data
        st.subheader("Major Agricultural Trading Nations")

        export_counts = {}
        import_counts = {}

        for crop, data in CROP_PRODUCTION.items():
            for exp in data['top_exporters']:
                if exp not in export_counts:
                    export_counts[exp] = []
                export_counts[exp].append(crop)
            for imp in data['top_importers']:
                if imp not in import_counts:
                    import_counts[imp] = []
                import_counts[imp].append(crop)

        col1, col2 = st.columns(2)

        with col1:
            export_df = pd.DataFrame([
                {'Country': k, 'Crops Exported': len(v), 'Crops': ', '.join(v[:3]) + ('...' if len(v) > 3 else '')}
                for k, v in sorted(export_counts.items(), key=lambda x: -len(x[1]))
            ])

            fig_exp = px.bar(
                export_df.head(10),
                x='Crops Exported',
                y='Country',
                orientation='h',
                title='Top Agricultural Exporters',
                hover_data=['Crops'],
                color_discrete_sequence=['#2ecc71']
            )
            fig_exp.update_layout(**get_clean_plotly_layout(), height=350)
            fig_exp.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_exp, use_container_width=True)

        with col2:
            import_df = pd.DataFrame([
                {'Country': k, 'Crops Imported': len(v), 'Crops': ', '.join(v[:3]) + ('...' if len(v) > 3 else '')}
                for k, v in sorted(import_counts.items(), key=lambda x: -len(x[1]))
            ])

            fig_imp = px.bar(
                import_df.head(10),
                x='Crops Imported',
                y='Country',
                orientation='h',
                title='Top Agricultural Importers',
                hover_data=['Crops'],
                color_discrete_sequence=['#e74c3c']
            )
            fig_imp.update_layout(**get_clean_plotly_layout(), height=350)
            fig_imp.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_imp, use_container_width=True)

    with ag_tabs[2]:
        st.subheader("Fertilizer Production")
        st.markdown("*Global fertilizer supply - critical for food production*")

        selected_fert = st.selectbox(
            "Select fertilizer type:",
            list(FERTILIZER_DATA.keys()),
            key="fert_select"
        )

        fert_data = FERTILIZER_DATA[selected_fert]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("World Production", f"{fert_data['world_total']} million MT")
        with col2:
            top_prod = fert_data['producers'][0]
            st.metric("Top Producer", f"{top_prod[0]} ({top_prod[2]:.1f}%)")

        fert_df = pd.DataFrame(fert_data['producers'], columns=['Country', 'Production (MT)', 'Share %'])

        fig_fert = px.bar(
            fert_df,
            x='Production (MT)',
            y='Country',
            orientation='h',
            title=f'{selected_fert} Fertilizer Production (million metric tons)',
            color='Share %',
            color_continuous_scale='YlOrBr'
        )
        fig_fert.update_layout(**get_clean_plotly_layout(), height=400)
        fig_fert.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_fert, use_container_width=True)

        # All fertilizers summary
        st.markdown("---")
        st.subheader("Fertilizer Market Overview")

        fert_summary = []
        for fert_name, data in FERTILIZER_DATA.items():
            fert_summary.append({
                'Type': fert_name,
                'World Production (MT)': f"{data['world_total']}M",
                'Top Producer': data['producers'][0][0],
                'Share': f"{data['producers'][0][2]:.1f}%"
            })

        st.dataframe(pd.DataFrame(fert_summary), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.info("**Note:** Belarus and Russia together control ~36% of global potash. Sanctions and supply disruptions significantly impact global fertilizer prices and food security.")

    with ag_tabs[3]:
        st.subheader("Global Food Security Index")
        st.markdown("*Measuring affordability, availability, quality & safety of food*")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Most Food Secure Countries")
            secure_df = pd.DataFrame(FOOD_SECURITY['Most Food Secure'], columns=['Country', 'Score'])

            fig_secure = px.bar(
                secure_df,
                x='Score',
                y='Country',
                orientation='h',
                title='Food Security Index (0-100)',
                color='Score',
                color_continuous_scale='Greens'
            )
            fig_secure.update_layout(**get_clean_plotly_layout(), height=450)
            fig_secure.update_yaxes(categoryorder='total ascending')
            fig_secure.update_xaxes(range=[0, 100])
            st.plotly_chart(fig_secure, use_container_width=True)

        with col2:
            st.markdown("##### Least Food Secure Countries")
            insecure_df = pd.DataFrame(FOOD_SECURITY['Least Food Secure'], columns=['Country', 'Score'])

            fig_insecure = px.bar(
                insecure_df,
                x='Score',
                y='Country',
                orientation='h',
                title='Food Security Index (0-100)',
                color='Score',
                color_continuous_scale='Reds_r'
            )
            fig_insecure.update_layout(**get_clean_plotly_layout(), height=450)
            fig_insecure.update_yaxes(categoryorder='total descending')
            fig_insecure.update_xaxes(range=[0, 100])
            st.plotly_chart(fig_insecure, use_container_width=True)

        st.markdown("---")
        st.markdown("""
        **Food Security Index Components:**
        - **Affordability** - Food prices relative to income, social safety nets
        - **Availability** - Agricultural production, supply infrastructure
        - **Quality & Safety** - Nutritional diversity, food standards
        - **Natural Resources** - Climate resilience, water scarcity risks
        """)

    with ag_tabs[4]:
        st.subheader("Agricultural Land Use")

        land_type = st.selectbox(
            "Select land type:",
            list(LAND_USE.keys()),
            key="land_select"
        )

        land_data = LAND_USE[land_type]

        st.metric("World Total", f"{land_data['world_total']:,} million hectares")

        land_df = pd.DataFrame(land_data['countries'], columns=['Country', 'Area (Mha)', 'Share %'])

        fig_land = px.bar(
            land_df,
            x='Area (Mha)',
            y='Country',
            orientation='h',
            title=f'{land_type} by Country (million hectares)',
            color='Share %',
            color_continuous_scale='YlGn'
        )
        fig_land.update_layout(**get_clean_plotly_layout(), height=400)
        fig_land.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_land, use_container_width=True)

        fig_pie = px.pie(
            land_df,
            values='Area (Mha)',
            names='Country',
            title=f'{land_type} - Global Distribution'
        )
        fig_pie.update_layout(**get_clean_plotly_layout(), height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.caption("Data sources: FAO (Food and Agriculture Organization), USDA, World Bank, Global Food Security Index 2023")
    st.caption("Production figures are 2022/2023 estimates. Food Security Index is from The Economist Intelligence Unit.")


# ============================================================================
# PAGE: TRADE & SHIPPING
# ============================================================================

elif page == "Trade & Shipping":
    st.title("Global Trade & Shipping")
    st.markdown("*World trade volumes, shipping indices, and trade balances*")
    st.markdown("---")

    # Baltic Dry Index historical context
    BDI_INFO = {
        'current': 1450,
        'ytd_change': -12.5,
        'all_time_high': 11793,  # May 2008
        'all_time_low': 290,     # February 2016
        'description': 'Measures cost of shipping raw materials (iron ore, coal, grain)',
    }

    # Global trade data (trillion USD, 2023)
    TRADE_DATA = {
        'Total World Trade': 25.3,
        'Goods Trade': 19.5,
        'Services Trade': 5.8,
    }

    # Top trading nations (trillion USD, 2023)
    TOP_TRADERS = {
        'Total Trade': [
            ('China', 5.94, 23.5),
            ('United States', 5.08, 20.1),
            ('Germany', 3.17, 12.5),
            ('Netherlands', 1.78, 7.0),
            ('Japan', 1.47, 5.8),
            ('France', 1.41, 5.6),
            ('South Korea', 1.32, 5.2),
            ('UK', 1.31, 5.2),
            ('Italy', 1.25, 4.9),
            ('Hong Kong', 1.18, 4.7),
        ],
        'Exports': [
            ('China', 3.38, 14.7),
            ('United States', 2.02, 8.8),
            ('Germany', 1.69, 7.4),
            ('Netherlands', 0.97, 4.2),
            ('Japan', 0.76, 3.3),
            ('South Korea', 0.68, 3.0),
            ('France', 0.65, 2.8),
            ('Italy', 0.66, 2.9),
            ('Belgium', 0.58, 2.5),
            ('Canada', 0.57, 2.5),
        ],
        'Imports': [
            ('United States', 3.06, 13.3),
            ('China', 2.56, 11.1),
            ('Germany', 1.48, 6.4),
            ('Japan', 0.71, 3.1),
            ('UK', 0.74, 3.2),
            ('France', 0.76, 3.3),
            ('Netherlands', 0.81, 3.5),
            ('India', 0.67, 2.9),
            ('South Korea', 0.64, 2.8),
            ('Italy', 0.59, 2.6),
        ],
    }

    # Trade balances (billion USD)
    TRADE_BALANCES = [
        ('China', 823, 'surplus'),
        ('Germany', 210, 'surplus'),
        ('Russia', 140, 'surplus'),
        ('Saudi Arabia', 130, 'surplus'),
        ('Netherlands', 160, 'surplus'),
        ('United States', -1040, 'deficit'),
        ('UK', -235, 'deficit'),
        ('India', -265, 'deficit'),
        ('France', -110, 'deficit'),
        ('Turkey', -95, 'deficit'),
    ]

    # Container shipping rates
    SHIPPING_ROUTES = {
        'Shanghai - Los Angeles': {'rate': 2150, 'change': -45.2, 'unit': '40ft container'},
        'Shanghai - Rotterdam': {'rate': 2850, 'change': -38.5, 'unit': '40ft container'},
        'Shanghai - New York': {'rate': 3100, 'change': -42.1, 'unit': '40ft container'},
        'Rotterdam - New York': {'rate': 2200, 'change': -28.3, 'unit': '40ft container'},
        'Singapore - Rotterdam': {'rate': 2650, 'change': -35.7, 'unit': '40ft container'},
    }

    # Major ports (TEU millions, 2023)
    TOP_PORTS = [
        ('Shanghai', 47.3, 'China'),
        ('Singapore', 39.0, 'Singapore'),
        ('Ningbo-Zhoushan', 35.3, 'China'),
        ('Shenzhen', 30.2, 'China'),
        ('Guangzhou', 24.6, 'China'),
        ('Qingdao', 26.4, 'China'),
        ('Busan', 22.7, 'South Korea'),
        ('Tianjin', 21.0, 'China'),
        ('Hong Kong', 14.9, 'China'),
        ('Rotterdam', 14.5, 'Netherlands'),
        ('Dubai', 14.0, 'UAE'),
        ('Los Angeles', 9.9, 'USA'),
    ]

    # Create tabs
    trade_tabs = st.tabs(["Overview", "Trade Rankings", "Trade Balance", "Shipping", "Major Ports"])

    with trade_tabs[0]:
        st.subheader("Global Trade Overview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("World Trade (2023)", f"${TRADE_DATA['Total World Trade']}T")
        with col2:
            st.metric("Goods Trade", f"${TRADE_DATA['Goods Trade']}T")
        with col3:
            st.metric("Services Trade", f"${TRADE_DATA['Services Trade']}T")

        st.markdown("---")

        # Baltic Dry Index
        st.subheader("Baltic Dry Index (BDI)")
        st.markdown(f"*{BDI_INFO['description']}*")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current", f"{BDI_INFO['current']:,}")
        with col2:
            st.metric("YTD Change", f"{BDI_INFO['ytd_change']:.1f}%")
        with col3:
            st.metric("All-Time High", f"{BDI_INFO['all_time_high']:,}", help="May 2008")
        with col4:
            st.metric("All-Time Low", f"{BDI_INFO['all_time_low']:,}", help="February 2016")

        st.markdown("---")
        st.markdown("""
        **Key Trade Indicators:**
        - **Baltic Dry Index** - Leading indicator for global economic activity
        - **Container Rates** - Cost to ship finished goods
        - **Trade Balance** - Difference between exports and imports
        """)

    with trade_tabs[1]:
        st.subheader("Top Trading Nations")

        trade_type = st.selectbox(
            "Select trade type:",
            list(TOP_TRADERS.keys()),
            key="trade_type_select"
        )

        trade_df = pd.DataFrame(TOP_TRADERS[trade_type], columns=['Country', 'Value (T$)', 'Share %'])

        fig_trade = px.bar(
            trade_df,
            x='Value (T$)',
            y='Country',
            orientation='h',
            title=f'{trade_type} by Country (Trillion USD)',
            color='Share %',
            color_continuous_scale='Blues'
        )
        fig_trade.update_layout(**get_clean_plotly_layout(), height=400)
        fig_trade.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_trade, use_container_width=True)

        fig_pie = px.pie(
            trade_df,
            values='Value (T$)',
            names='Country',
            title=f'{trade_type} - Market Share'
        )
        fig_pie.update_layout(**get_clean_plotly_layout(), height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with trade_tabs[2]:
        st.subheader("Trade Balances")
        st.markdown("*Surplus (green) vs Deficit (red) countries*")

        balance_df = pd.DataFrame(TRADE_BALANCES, columns=['Country', 'Balance ($B)', 'Type'])
        balance_df['Color'] = balance_df['Type'].map({'surplus': '#2ecc71', 'deficit': '#e74c3c'})

        fig_balance = px.bar(
            balance_df.sort_values('Balance ($B)'),
            x='Balance ($B)',
            y='Country',
            orientation='h',
            title='Trade Balance by Country (Billion USD)',
            color='Type',
            color_discrete_map={'surplus': '#2ecc71', 'deficit': '#e74c3c'}
        )
        fig_balance.update_layout(**get_clean_plotly_layout(), height=450)
        st.plotly_chart(fig_balance, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Largest Surpluses")
            surplus_df = balance_df[balance_df['Type'] == 'surplus'].sort_values('Balance ($B)', ascending=False)
            for _, row in surplus_df.iterrows():
                st.markdown(f"- **{row['Country']}**: +${row['Balance ($B)']:,}B")

        with col2:
            st.markdown("##### Largest Deficits")
            deficit_df = balance_df[balance_df['Type'] == 'deficit'].sort_values('Balance ($B)')
            for _, row in deficit_df.iterrows():
                st.markdown(f"- **{row['Country']}**: ${row['Balance ($B)']:,}B")

    with trade_tabs[3]:
        st.subheader("Container Shipping Rates")
        st.markdown("*Current rates for major shipping routes (40ft container)*")

        routes_data = []
        for route, data in SHIPPING_ROUTES.items():
            routes_data.append({
                'Route': route,
                'Rate ($)': data['rate'],
                'YoY Change': data['change']
            })

        routes_df = pd.DataFrame(routes_data)

        fig_routes = px.bar(
            routes_df,
            x='Rate ($)',
            y='Route',
            orientation='h',
            title='Container Shipping Rates (USD per 40ft container)',
            color='YoY Change',
            color_continuous_scale='RdYlGn_r'
        )
        fig_routes.update_layout(**get_clean_plotly_layout(), height=350)
        fig_routes.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_routes, use_container_width=True)

        st.dataframe(routes_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.info("**Note:** Shipping rates have normalized from 2021-2022 peaks when routes like Shanghai-LA reached $20,000+")

    with trade_tabs[4]:
        st.subheader("World's Busiest Ports")
        st.markdown("*Container throughput in million TEU (Twenty-foot Equivalent Units)*")

        ports_df = pd.DataFrame(TOP_PORTS, columns=['Port', 'TEU (M)', 'Country'])

        fig_ports = px.bar(
            ports_df,
            x='TEU (M)',
            y='Port',
            orientation='h',
            title='Top Container Ports by Volume (Million TEU)',
            color='Country',
        )
        fig_ports.update_layout(**get_clean_plotly_layout(), height=450)
        fig_ports.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_ports, use_container_width=True)

        # Port distribution by country
        country_ports = ports_df.groupby('Country')['TEU (M)'].sum().reset_index()
        country_ports = country_ports.sort_values('TEU (M)', ascending=False)

        fig_country = px.pie(
            country_ports,
            values='TEU (M)',
            names='Country',
            title='Container Traffic by Country'
        )
        fig_country.update_layout(**get_clean_plotly_layout(), height=350)
        st.plotly_chart(fig_country, use_container_width=True)

        st.markdown("---")
        st.warning("**China dominates global shipping** - 7 of the top 10 busiest ports are in China, handling over 60% of top-port container traffic.")

    st.markdown("---")
    st.caption("Data sources: WTO, World Bank, Drewry Shipping Consultants, Lloyd's List, Baltic Exchange")
    st.caption("Trade figures are 2023 estimates. Shipping rates are indicative spot rates.")


# ============================================================================
# PAGE: DEMOGRAPHICS
# ============================================================================

elif page == "Demographics":
    st.title("Global Demographics & Population")
    st.markdown("*World population, growth trends, and demographic indicators*")
    st.markdown("---")

    # World population data
    WORLD_POP = {
        'total': 8.1,  # billion
        'growth_rate': 0.88,  # percent per year
        'urban_percent': 57,
        'median_age': 30.5,
    }

    # Most populous countries (millions, 2024)
    POPULATION_RANKING = [
        ('India', 1441, 17.8),
        ('China', 1425, 17.6),
        ('United States', 340, 4.2),
        ('Indonesia', 278, 3.4),
        ('Pakistan', 240, 3.0),
        ('Nigeria', 229, 2.8),
        ('Brazil', 217, 2.7),
        ('Bangladesh', 173, 2.1),
        ('Russia', 144, 1.8),
        ('Ethiopia', 129, 1.6),
        ('Mexico', 129, 1.6),
        ('Japan', 123, 1.5),
        ('Philippines', 118, 1.5),
        ('Egypt', 113, 1.4),
        ('Vietnam', 100, 1.2),
    ]

    # Population growth rates (% per year)
    GROWTH_RATES = {
        'Fastest Growing': [
            ('Niger', 3.7),
            ('Angola', 3.3),
            ('DR Congo', 3.2),
            ('Mali', 3.0),
            ('Chad', 3.0),
            ('Uganda', 2.9),
            ('Somalia', 2.8),
            ('Mozambique', 2.7),
            ('Tanzania', 2.7),
            ('Zambia', 2.7),
        ],
        'Shrinking': [
            ('Ukraine', -1.5),
            ('Bulgaria', -1.1),
            ('Latvia', -1.0),
            ('Lithuania', -0.9),
            ('Serbia', -0.8),
            ('Croatia', -0.7),
            ('Romania', -0.6),
            ('Hungary', -0.5),
            ('Japan', -0.5),
            ('Italy', -0.4),
        ],
    }

    # Median age by country
    MEDIAN_AGE = {
        'Oldest': [
            ('Monaco', 55.4),
            ('Japan', 49.1),
            ('Italy', 47.9),
            ('Germany', 47.8),
            ('Portugal', 46.8),
            ('Finland', 43.6),
            ('Greece', 45.7),
            ('Slovenia', 45.1),
            ('Austria', 44.5),
            ('Spain', 45.5),
        ],
        'Youngest': [
            ('Niger', 14.9),
            ('Mali', 15.8),
            ('Uganda', 15.9),
            ('Chad', 16.1),
            ('Angola', 16.2),
            ('Somalia', 16.4),
            ('DR Congo', 16.7),
            ('Zambia', 16.9),
            ('Mozambique', 17.1),
            ('Malawi', 17.2),
        ],
    }

    # Urbanization rates
    URBANIZATION = {
        'Most Urban': [
            ('Singapore', 100),
            ('Monaco', 100),
            ('Kuwait', 100),
            ('Belgium', 98),
            ('Qatar', 99),
            ('Malta', 95),
            ('San Marino', 97),
            ('Netherlands', 93),
            ('Japan', 92),
            ('Israel', 93),
        ],
        'Least Urban': [
            ('Burundi', 14),
            ('Papua New Guinea', 13),
            ('Niger', 17),
            ('Malawi', 18),
            ('Rwanda', 18),
            ('Chad', 24),
            ('Ethiopia', 23),
            ('Uganda', 26),
            ('Nepal', 22),
            ('Sri Lanka', 19),
        ],
    }

    # Life expectancy
    LIFE_EXPECTANCY = {
        'Highest': [
            ('Monaco', 89.4),
            ('Japan', 84.8),
            ('Switzerland', 84.0),
            ('Singapore', 84.1),
            ('Spain', 83.6),
            ('Italy', 83.5),
            ('Australia', 83.5),
            ('Iceland', 83.3),
            ('Israel', 83.0),
            ('Sweden', 82.8),
        ],
        'Lowest': [
            ('Chad', 53.1),
            ('Nigeria', 53.9),
            ('Lesotho', 54.3),
            ('Central African Republic', 54.4),
            ('Somalia', 56.5),
            ('Eswatini', 57.1),
            ('South Sudan', 57.9),
            ('Ivory Coast', 58.8),
            ('Guinea-Bissau', 59.4),
            ('Sierra Leone', 60.1),
        ],
    }

    # Create tabs
    demo_tabs = st.tabs(["Overview", "Population", "Growth Rates", "Age Structure", "Urbanization", "Life Expectancy"])

    with demo_tabs[0]:
        st.subheader("World Population Overview")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("World Population", f"{WORLD_POP['total']} billion")
        with col2:
            st.metric("Annual Growth", f"{WORLD_POP['growth_rate']}%")
        with col3:
            st.metric("Urban Population", f"{WORLD_POP['urban_percent']}%")
        with col4:
            st.metric("Median Age", f"{WORLD_POP['median_age']} years")

        st.markdown("---")

        st.markdown("""
        **Key Demographic Trends:**
        - **India passed China** as the world's most populous country in 2023
        - **Africa** is the fastest-growing continent, expected to double by 2050
        - **Europe and East Asia** face population decline and aging
        - **Urbanization** continues rapidly in developing nations
        - **Life expectancy** has increased 25+ years since 1950
        """)

    with demo_tabs[1]:
        st.subheader("Most Populous Countries")

        pop_df = pd.DataFrame(POPULATION_RANKING, columns=['Country', 'Population (M)', 'Share %'])

        fig_pop = px.bar(
            pop_df,
            x='Population (M)',
            y='Country',
            orientation='h',
            title='Population by Country (Millions)',
            color='Share %',
            color_continuous_scale='Reds'
        )
        fig_pop.update_layout(**get_clean_plotly_layout(), height=500)
        fig_pop.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_pop, use_container_width=True)

        fig_pie = px.pie(
            pop_df.head(10),
            values='Population (M)',
            names='Country',
            title='Top 10 Countries - World Population Share'
        )
        fig_pie.update_layout(**get_clean_plotly_layout(), height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    with demo_tabs[2]:
        st.subheader("Population Growth Rates")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Fastest Growing")
            fast_df = pd.DataFrame(GROWTH_RATES['Fastest Growing'], columns=['Country', 'Growth Rate %'])

            fig_fast = px.bar(
                fast_df,
                x='Growth Rate %',
                y='Country',
                orientation='h',
                title='Fastest Growing Populations',
                color='Growth Rate %',
                color_continuous_scale='Greens'
            )
            fig_fast.update_layout(**get_clean_plotly_layout(), height=400)
            fig_fast.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_fast, use_container_width=True)

        with col2:
            st.markdown("##### Shrinking Populations")
            shrink_df = pd.DataFrame(GROWTH_RATES['Shrinking'], columns=['Country', 'Growth Rate %'])

            fig_shrink = px.bar(
                shrink_df,
                x='Growth Rate %',
                y='Country',
                orientation='h',
                title='Shrinking Populations',
                color='Growth Rate %',
                color_continuous_scale='Reds_r'
            )
            fig_shrink.update_layout(**get_clean_plotly_layout(), height=400)
            fig_shrink.update_yaxes(categoryorder='total descending')
            st.plotly_chart(fig_shrink, use_container_width=True)

    with demo_tabs[3]:
        st.subheader("Age Structure - Median Age")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Oldest Populations")
            old_df = pd.DataFrame(MEDIAN_AGE['Oldest'], columns=['Country', 'Median Age'])

            fig_old = px.bar(
                old_df,
                x='Median Age',
                y='Country',
                orientation='h',
                title='Countries with Oldest Populations',
                color='Median Age',
                color_continuous_scale='Blues'
            )
            fig_old.update_layout(**get_clean_plotly_layout(), height=400)
            fig_old.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_old, use_container_width=True)

        with col2:
            st.markdown("##### Youngest Populations")
            young_df = pd.DataFrame(MEDIAN_AGE['Youngest'], columns=['Country', 'Median Age'])

            fig_young = px.bar(
                young_df,
                x='Median Age',
                y='Country',
                orientation='h',
                title='Countries with Youngest Populations',
                color='Median Age',
                color_continuous_scale='Oranges_r'
            )
            fig_young.update_layout(**get_clean_plotly_layout(), height=400)
            fig_young.update_yaxes(categoryorder='total descending')
            st.plotly_chart(fig_young, use_container_width=True)

    with demo_tabs[4]:
        st.subheader("Urbanization")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Most Urbanized")
            urban_df = pd.DataFrame(URBANIZATION['Most Urban'], columns=['Country', 'Urban %'])

            fig_urban = px.bar(
                urban_df,
                x='Urban %',
                y='Country',
                orientation='h',
                title='Most Urbanized Countries',
                color='Urban %',
                color_continuous_scale='Purples'
            )
            fig_urban.update_layout(**get_clean_plotly_layout(), height=400)
            fig_urban.update_yaxes(categoryorder='total ascending')
            fig_urban.update_xaxes(range=[0, 100])
            st.plotly_chart(fig_urban, use_container_width=True)

        with col2:
            st.markdown("##### Least Urbanized")
            rural_df = pd.DataFrame(URBANIZATION['Least Urban'], columns=['Country', 'Urban %'])

            fig_rural = px.bar(
                rural_df,
                x='Urban %',
                y='Country',
                orientation='h',
                title='Least Urbanized Countries',
                color='Urban %',
                color_continuous_scale='Greens_r'
            )
            fig_rural.update_layout(**get_clean_plotly_layout(), height=400)
            fig_rural.update_yaxes(categoryorder='total descending')
            fig_rural.update_xaxes(range=[0, 100])
            st.plotly_chart(fig_rural, use_container_width=True)

    with demo_tabs[5]:
        st.subheader("Life Expectancy")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Highest Life Expectancy")
            high_life_df = pd.DataFrame(LIFE_EXPECTANCY['Highest'], columns=['Country', 'Years'])

            fig_high = px.bar(
                high_life_df,
                x='Years',
                y='Country',
                orientation='h',
                title='Highest Life Expectancy',
                color='Years',
                color_continuous_scale='Greens'
            )
            fig_high.update_layout(**get_clean_plotly_layout(), height=400)
            fig_high.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_high, use_container_width=True)

        with col2:
            st.markdown("##### Lowest Life Expectancy")
            low_life_df = pd.DataFrame(LIFE_EXPECTANCY['Lowest'], columns=['Country', 'Years'])

            fig_low = px.bar(
                low_life_df,
                x='Years',
                y='Country',
                orientation='h',
                title='Lowest Life Expectancy',
                color='Years',
                color_continuous_scale='Reds_r'
            )
            fig_low.update_layout(**get_clean_plotly_layout(), height=400)
            fig_low.update_yaxes(categoryorder='total descending')
            st.plotly_chart(fig_low, use_container_width=True)

        st.markdown("---")
        st.info("**Gap Alert:** There is a 36-year difference in life expectancy between Monaco (89.4) and Chad (53.1)")

    st.markdown("---")
    st.caption("Data sources: United Nations World Population Prospects 2024, World Bank, CIA World Factbook")
    st.caption("Figures are 2024 estimates.")


# ============================================================================
# PAGE: DEBT & FISCAL
# ============================================================================

elif page == "Debt & Fiscal":
    st.title("Government Debt & Fiscal Data")
    st.markdown("*National debt, budget deficits, and sovereign credit ratings*")
    st.markdown("---")

    # Global debt overview
    GLOBAL_DEBT = {
        'total_government': 92,  # trillion USD
        'total_global': 307,     # trillion USD (all debt)
        'avg_debt_to_gdp': 92,   # percent
    }

    # Debt to GDP ratios (percent)
    DEBT_TO_GDP = {
        'Highest': [
            ('Japan', 264),
            ('Venezuela', 241),
            ('Sudan', 186),
            ('Greece', 177),
            ('Singapore', 168),
            ('Eritrea', 164),
            ('Lebanon', 151),
            ('Italy', 144),
            ('Cape Verde', 143),
            ('USA', 129),
            ('Bahrain', 128),
            ('Portugal', 127),
            ('Spain', 112),
            ('France', 111),
            ('Belgium', 106),
        ],
        'Lowest': [
            ('Brunei', 2),
            ('Hong Kong', 4),
            ('Timor-Leste', 6),
            ('Afghanistan', 7),
            ('Kuwait', 8),
            ('Russia', 15),
            ('Saudi Arabia', 26),
            ('Taiwan', 28),
            ('Indonesia', 40),
            ('South Korea', 54),
        ],
    }

    # Total national debt (trillion USD)
    NATIONAL_DEBT = [
        ('United States', 34.0, 129),
        ('China', 14.0, 77),
        ('Japan', 10.5, 264),
        ('UK', 3.3, 104),
        ('France', 3.2, 111),
        ('Italy', 3.0, 144),
        ('Germany', 2.8, 66),
        ('India', 2.6, 83),
        ('Canada', 1.8, 107),
        ('Brazil', 1.6, 88),
        ('Spain', 1.6, 112),
        ('Australia', 0.9, 57),
    ]

    # Budget deficits (% of GDP, 2023)
    BUDGET_BALANCE = {
        'Largest Deficits': [
            ('Libya', -24.0),
            ('Venezuela', -15.0),
            ('Sri Lanka', -10.2),
            ('USA', -8.8),
            ('UK', -6.1),
            ('Japan', -5.8),
            ('France', -5.5),
            ('India', -5.9),
            ('Italy', -5.3),
            ('Spain', -4.8),
        ],
        'Largest Surpluses': [
            ('Norway', 27.0),
            ('Macau', 18.0),
            ('Kuwait', 12.5),
            ('Qatar', 10.2),
            ('UAE', 9.8),
            ('Singapore', 8.0),
            ('Saudi Arabia', 6.5),
            ('Ireland', 4.2),
            ('Denmark', 3.0),
            ('Switzerland', 2.5),
        ],
    }

    # Credit ratings (simplified to major countries)
    CREDIT_RATINGS = {
        'AAA/Aaa': ['Germany', 'Netherlands', 'Switzerland', 'Norway', 'Singapore', 'Australia', 'Denmark', 'Sweden', 'Luxembourg'],
        'AA+/Aa1': ['USA', 'Austria', 'Finland'],
        'AA/Aa2': ['France', 'UK', 'Belgium', 'Czech Republic'],
        'AA-/Aa3': ['South Korea', 'Taiwan', 'Estonia'],
        'A+/A1': ['Japan', 'China', 'Slovakia', 'Ireland'],
        'A/A2': ['Spain', 'Poland', 'Malta'],
        'A-/A3': ['Italy', 'Mexico', 'Thailand'],
        'BBB+/Baa1': ['Portugal', 'India', 'Indonesia'],
        'BBB/Baa2': ['Brazil', 'South Africa', 'Romania'],
        'BBB-/Baa3': ['Colombia', 'Hungary', 'Morocco'],
        'BB+ or below': ['Turkey', 'Argentina', 'Russia', 'Pakistan', 'Egypt', 'Nigeria'],
    }

    # Create tabs
    debt_tabs = st.tabs(["Overview", "Debt-to-GDP", "Total Debt", "Budget Balance", "Credit Ratings"])

    with debt_tabs[0]:
        st.subheader("Global Debt Overview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Government Debt", f"${GLOBAL_DEBT['total_government']}T")
        with col2:
            st.metric("Total Global Debt", f"${GLOBAL_DEBT['total_global']}T", help="Includes household, corporate, government")
        with col3:
            st.metric("Avg Debt/GDP", f"{GLOBAL_DEBT['avg_debt_to_gdp']}%")

        st.markdown("---")

        st.markdown("""
        **Key Insights:**
        - **Global debt hit record $307 trillion** in 2023
        - **US alone holds** $34 trillion in national debt (11% of global total)
        - **Japan's debt/GDP at 264%** - highest in developed world
        - **Low-debt countries** tend to be oil exporters or small city-states
        - **Credit rating downgrades** can significantly increase borrowing costs
        """)

        st.markdown("---")
        st.warning("**US Debt Clock:** Adding ~$1 trillion every 100 days as of 2024")

    with debt_tabs[1]:
        st.subheader("Debt-to-GDP Ratios")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Highest Debt-to-GDP")
            high_df = pd.DataFrame(DEBT_TO_GDP['Highest'], columns=['Country', 'Debt/GDP %'])

            fig_high = px.bar(
                high_df,
                x='Debt/GDP %',
                y='Country',
                orientation='h',
                title='Highest Debt-to-GDP Ratios',
                color='Debt/GDP %',
                color_continuous_scale='Reds'
            )
            fig_high.update_layout(**get_clean_plotly_layout(), height=500)
            fig_high.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_high, use_container_width=True)

        with col2:
            st.markdown("##### Lowest Debt-to-GDP")
            low_df = pd.DataFrame(DEBT_TO_GDP['Lowest'], columns=['Country', 'Debt/GDP %'])

            fig_low = px.bar(
                low_df,
                x='Debt/GDP %',
                y='Country',
                orientation='h',
                title='Lowest Debt-to-GDP Ratios',
                color='Debt/GDP %',
                color_continuous_scale='Greens'
            )
            fig_low.update_layout(**get_clean_plotly_layout(), height=500)
            fig_low.update_yaxes(categoryorder='total descending')
            st.plotly_chart(fig_low, use_container_width=True)

    with debt_tabs[2]:
        st.subheader("Total National Debt")
        st.markdown("*Absolute debt in trillion USD*")

        debt_df = pd.DataFrame(NATIONAL_DEBT, columns=['Country', 'Debt (T$)', 'Debt/GDP %'])

        fig_debt = px.bar(
            debt_df,
            x='Debt (T$)',
            y='Country',
            orientation='h',
            title='National Debt by Country (Trillion USD)',
            color='Debt/GDP %',
            color_continuous_scale='RdYlGn_r'
        )
        fig_debt.update_layout(**get_clean_plotly_layout(), height=450)
        fig_debt.update_yaxes(categoryorder='total ascending')
        st.plotly_chart(fig_debt, use_container_width=True)

        st.dataframe(debt_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.info("**Note:** High absolute debt doesn't always mean crisis - it depends on GDP, growth rate, and interest costs. Japan has 264% debt/GDP but very low interest rates.")

    with debt_tabs[3]:
        st.subheader("Budget Balance")
        st.markdown("*Annual surplus (+) or deficit (-) as % of GDP*")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Largest Deficits")
            deficit_df = pd.DataFrame(BUDGET_BALANCE['Largest Deficits'], columns=['Country', 'Balance %'])

            fig_deficit = px.bar(
                deficit_df,
                x='Balance %',
                y='Country',
                orientation='h',
                title='Largest Budget Deficits (% of GDP)',
                color='Balance %',
                color_continuous_scale='Reds'
            )
            fig_deficit.update_layout(**get_clean_plotly_layout(), height=400)
            fig_deficit.update_yaxes(categoryorder='total descending')
            st.plotly_chart(fig_deficit, use_container_width=True)

        with col2:
            st.markdown("##### Largest Surpluses")
            surplus_df = pd.DataFrame(BUDGET_BALANCE['Largest Surpluses'], columns=['Country', 'Balance %'])

            fig_surplus = px.bar(
                surplus_df,
                x='Balance %',
                y='Country',
                orientation='h',
                title='Largest Budget Surpluses (% of GDP)',
                color='Balance %',
                color_continuous_scale='Greens'
            )
            fig_surplus.update_layout(**get_clean_plotly_layout(), height=400)
            fig_surplus.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_surplus, use_container_width=True)

    with debt_tabs[4]:
        st.subheader("Sovereign Credit Ratings")
        st.markdown("*S&P/Moody's ratings - affects borrowing costs*")

        for rating, countries in CREDIT_RATINGS.items():
            if rating == 'AAA/Aaa':
                color = '🟢'
            elif rating.startswith('AA'):
                color = '🟢'
            elif rating.startswith('A'):
                color = '🟡'
            elif rating.startswith('BBB'):
                color = '🟠'
            else:
                color = '🔴'

            st.markdown(f"**{color} {rating}:** {', '.join(countries)}")

        st.markdown("---")
        st.markdown("""
        **Rating Scale:**
        - 🟢 **AAA to A-** - Investment grade (low risk)
        - 🟡 **BBB+ to BBB-** - Lower investment grade (moderate risk)
        - 🔴 **BB+ and below** - Speculative/Junk (high risk)

        **Impact:** A one-notch downgrade can increase borrowing costs by 0.25-0.50%
        """)

    st.markdown("---")
    st.caption("Data sources: IMF, World Bank, S&P Global, Moody's, US Treasury, national finance ministries")
    st.caption("Figures are 2023/2024 estimates. Ratings as of December 2024.")


# ============================================================================
# PAGE: COUNTRY PROFILE
# ============================================================================

elif page == "Country Profile":
    st.title("Country Profile")
    st.markdown("*Comprehensive view of a single country across all data domains*")
    st.markdown("---")

    # Comprehensive country data - aggregated from all our data sources
    COUNTRY_DATA = {
        'United States': {
            'flag': '🇺🇸',
            'region': 'North America',
            'capital': 'Washington D.C.',
            'population': {'value': 340, 'rank': 3, 'growth': 0.5},
            'gdp': {'value': 27.4, 'rank': 1, 'growth': 2.5},
            'gdp_per_capita': 80412,
            'debt_to_gdp': 129,
            'credit_rating': 'AA+',
            'inflation': 3.4,
            'unemployment': 3.7,
            'trade_balance': -1040,
            'life_expectancy': 78.9,
            'median_age': 38.5,
            'urban_pct': 83,
            'electricity_gen': 4178,
            'energy_mix': {'coal': 16, 'gas': 43, 'nuclear': 18, 'renewables': 23},
            'co2_per_capita': 14.4,
            'food_security': 78.0,
            'arable_land': 158,
            'top_exports': ['Refined Petroleum', 'Crude Petroleum', 'Natural Gas', 'Aircraft', 'Integrated Circuits'],
            'top_imports': ['Cars', 'Computers', 'Crude Petroleum', 'Packaged Medicines', 'Vehicle Parts'],
            'minerals_produced': ['Coal', 'Copper', 'Gold', 'Iron Ore', 'Zinc'],
            'crops_produced': ['Corn', 'Soybeans', 'Wheat'],
        },
        'China': {
            'flag': '🇨🇳',
            'region': 'East Asia',
            'capital': 'Beijing',
            'population': {'value': 1425, 'rank': 2, 'growth': 0.0},
            'gdp': {'value': 17.8, 'rank': 2, 'growth': 5.2},
            'gdp_per_capita': 12541,
            'debt_to_gdp': 77,
            'credit_rating': 'A+',
            'inflation': 0.2,
            'unemployment': 5.2,
            'trade_balance': 823,
            'life_expectancy': 78.2,
            'median_age': 39.0,
            'urban_pct': 65,
            'electricity_gen': 8849,
            'energy_mix': {'coal': 60, 'gas': 3, 'nuclear': 5, 'renewables': 32},
            'co2_per_capita': 8.0,
            'food_security': 74.2,
            'arable_land': 119,
            'top_exports': ['Computers', 'Broadcasting Equipment', 'Telephones', 'Integrated Circuits', 'Office Machine Parts'],
            'top_imports': ['Crude Petroleum', 'Integrated Circuits', 'Iron Ore', 'Natural Gas', 'Cars'],
            'minerals_produced': ['Coal', 'Iron Ore', 'Rare Earths', 'Gold', 'Zinc'],
            'crops_produced': ['Rice', 'Wheat', 'Corn', 'Soybeans'],
        },
        'Germany': {
            'flag': '🇩🇪',
            'region': 'Europe',
            'capital': 'Berlin',
            'population': {'value': 84, 'rank': 19, 'growth': 0.0},
            'gdp': {'value': 4.5, 'rank': 3, 'growth': 0.0},
            'gdp_per_capita': 53571,
            'debt_to_gdp': 66,
            'credit_rating': 'AAA',
            'inflation': 2.9,
            'unemployment': 3.0,
            'trade_balance': 210,
            'life_expectancy': 81.3,
            'median_age': 47.8,
            'urban_pct': 78,
            'electricity_gen': 577,
            'energy_mix': {'coal': 26, 'gas': 16, 'nuclear': 0, 'renewables': 52},
            'co2_per_capita': 8.1,
            'food_security': 78.8,
            'arable_land': 12,
            'top_exports': ['Cars', 'Vehicle Parts', 'Packaged Medicines', 'Aircraft', 'Medical Instruments'],
            'top_imports': ['Cars', 'Crude Petroleum', 'Natural Gas', 'Vehicle Parts', 'Packaged Medicines'],
            'minerals_produced': ['Potash', 'Salt', 'Lignite'],
            'crops_produced': ['Wheat', 'Barley', 'Sugar Beets'],
        },
        'Japan': {
            'flag': '🇯🇵',
            'region': 'East Asia',
            'capital': 'Tokyo',
            'population': {'value': 123, 'rank': 12, 'growth': -0.5},
            'gdp': {'value': 4.2, 'rank': 4, 'growth': 1.9},
            'gdp_per_capita': 34017,
            'debt_to_gdp': 264,
            'credit_rating': 'A+',
            'inflation': 3.3,
            'unemployment': 2.6,
            'trade_balance': -52,
            'life_expectancy': 84.8,
            'median_age': 49.1,
            'urban_pct': 92,
            'electricity_gen': 1033,
            'energy_mix': {'coal': 31, 'gas': 34, 'nuclear': 6, 'renewables': 22},
            'co2_per_capita': 8.5,
            'food_security': 79.5,
            'arable_land': 4,
            'top_exports': ['Cars', 'Integrated Circuits', 'Vehicle Parts', 'Machinery', 'Refined Petroleum'],
            'top_imports': ['Crude Petroleum', 'Natural Gas', 'Integrated Circuits', 'Coal', 'Telephones'],
            'minerals_produced': ['Gold', 'Zinc', 'Lead'],
            'crops_produced': ['Rice', 'Vegetables', 'Fruits'],
        },
        'India': {
            'flag': '🇮🇳',
            'region': 'South Asia',
            'capital': 'New Delhi',
            'population': {'value': 1441, 'rank': 1, 'growth': 0.9},
            'gdp': {'value': 3.7, 'rank': 5, 'growth': 7.2},
            'gdp_per_capita': 2612,
            'debt_to_gdp': 83,
            'credit_rating': 'BBB-',
            'inflation': 5.4,
            'unemployment': 7.7,
            'trade_balance': -265,
            'life_expectancy': 70.4,
            'median_age': 28.4,
            'urban_pct': 36,
            'electricity_gen': 1715,
            'energy_mix': {'coal': 74, 'gas': 3, 'nuclear': 3, 'renewables': 20},
            'co2_per_capita': 1.9,
            'food_security': 57.2,
            'arable_land': 156,
            'top_exports': ['Refined Petroleum', 'Diamonds', 'Packaged Medicines', 'Rice', 'Jewelry'],
            'top_imports': ['Crude Petroleum', 'Gold', 'Coal', 'Diamonds', 'Natural Gas'],
            'minerals_produced': ['Coal', 'Iron Ore', 'Bauxite', 'Zinc'],
            'crops_produced': ['Rice', 'Wheat', 'Sugar', 'Cotton'],
        },
        'United Kingdom': {
            'flag': '🇬🇧',
            'region': 'Europe',
            'capital': 'London',
            'population': {'value': 68, 'rank': 22, 'growth': 0.4},
            'gdp': {'value': 3.3, 'rank': 6, 'growth': 0.5},
            'gdp_per_capita': 48912,
            'debt_to_gdp': 104,
            'credit_rating': 'AA',
            'inflation': 4.0,
            'unemployment': 4.2,
            'trade_balance': -235,
            'life_expectancy': 81.3,
            'median_age': 40.6,
            'urban_pct': 84,
            'electricity_gen': 312,
            'energy_mix': {'coal': 2, 'gas': 38, 'nuclear': 15, 'renewables': 43},
            'co2_per_capita': 4.7,
            'food_security': 77.8,
            'arable_land': 6,
            'top_exports': ['Cars', 'Gold', 'Gas Turbines', 'Packaged Medicines', 'Crude Petroleum'],
            'top_imports': ['Cars', 'Crude Petroleum', 'Gold', 'Packaged Medicines', 'Computers'],
            'minerals_produced': ['Oil', 'Natural Gas', 'Salt'],
            'crops_produced': ['Wheat', 'Barley', 'Potatoes'],
        },
        'Brazil': {
            'flag': '🇧🇷',
            'region': 'South America',
            'capital': 'Brasília',
            'population': {'value': 217, 'rank': 7, 'growth': 0.5},
            'gdp': {'value': 2.2, 'rank': 9, 'growth': 2.9},
            'gdp_per_capita': 10412,
            'debt_to_gdp': 88,
            'credit_rating': 'BB',
            'inflation': 4.6,
            'unemployment': 7.8,
            'trade_balance': 62,
            'life_expectancy': 76.4,
            'median_age': 34.3,
            'urban_pct': 88,
            'electricity_gen': 692,
            'energy_mix': {'coal': 3, 'gas': 9, 'nuclear': 2, 'renewables': 84},
            'co2_per_capita': 2.2,
            'food_security': 67.0,
            'arable_land': 63,
            'top_exports': ['Soybeans', 'Iron Ore', 'Crude Petroleum', 'Sugar', 'Corn'],
            'top_imports': ['Refined Petroleum', 'Fertilizers', 'Vehicle Parts', 'Integrated Circuits', 'Pesticides'],
            'minerals_produced': ['Iron Ore', 'Bauxite', 'Gold', 'Copper'],
            'crops_produced': ['Soybeans', 'Sugar', 'Coffee', 'Corn'],
        },
        'Russia': {
            'flag': '🇷🇺',
            'region': 'Eurasia',
            'capital': 'Moscow',
            'population': {'value': 144, 'rank': 9, 'growth': -0.2},
            'gdp': {'value': 1.9, 'rank': 11, 'growth': 3.6},
            'gdp_per_capita': 13271,
            'debt_to_gdp': 15,
            'credit_rating': 'BB+ (Junk)',
            'inflation': 7.4,
            'unemployment': 2.9,
            'trade_balance': 140,
            'life_expectancy': 72.8,
            'median_age': 39.8,
            'urban_pct': 75,
            'electricity_gen': 1166,
            'energy_mix': {'coal': 13, 'gas': 47, 'nuclear': 20, 'renewables': 20},
            'co2_per_capita': 11.4,
            'food_security': 63.5,
            'arable_land': 122,
            'top_exports': ['Crude Petroleum', 'Refined Petroleum', 'Natural Gas', 'Coal', 'Wheat'],
            'top_imports': ['Cars', 'Packaged Medicines', 'Vehicle Parts', 'Telephones', 'Computers'],
            'minerals_produced': ['Oil', 'Natural Gas', 'Coal', 'Gold', 'Nickel', 'Platinum', 'Potash'],
            'crops_produced': ['Wheat', 'Barley', 'Sunflower'],
        },
        'Australia': {
            'flag': '🇦🇺',
            'region': 'Oceania',
            'capital': 'Canberra',
            'population': {'value': 26, 'rank': 55, 'growth': 1.2},
            'gdp': {'value': 1.7, 'rank': 13, 'growth': 2.1},
            'gdp_per_capita': 65366,
            'debt_to_gdp': 57,
            'credit_rating': 'AAA',
            'inflation': 4.1,
            'unemployment': 3.9,
            'trade_balance': 85,
            'life_expectancy': 83.5,
            'median_age': 38.1,
            'urban_pct': 86,
            'electricity_gen': 265,
            'energy_mix': {'coal': 47, 'gas': 18, 'nuclear': 0, 'renewables': 35},
            'co2_per_capita': 14.9,
            'food_security': 77.5,
            'arable_land': 47,
            'top_exports': ['Iron Ore', 'Coal', 'Natural Gas', 'Gold', 'Aluminum Oxide'],
            'top_imports': ['Refined Petroleum', 'Cars', 'Computers', 'Telephones', 'Packaged Medicines'],
            'minerals_produced': ['Iron Ore', 'Lithium', 'Gold', 'Copper', 'Bauxite', 'Zinc', 'Uranium'],
            'crops_produced': ['Wheat', 'Barley', 'Sugar'],
        },
        'South Korea': {
            'flag': '🇰🇷',
            'region': 'East Asia',
            'capital': 'Seoul',
            'population': {'value': 52, 'rank': 28, 'growth': 0.0},
            'gdp': {'value': 1.7, 'rank': 12, 'growth': 1.4},
            'gdp_per_capita': 33147,
            'debt_to_gdp': 54,
            'credit_rating': 'AA-',
            'inflation': 3.6,
            'unemployment': 2.7,
            'trade_balance': 29,
            'life_expectancy': 83.6,
            'median_age': 44.9,
            'urban_pct': 81,
            'electricity_gen': 594,
            'energy_mix': {'coal': 32, 'gas': 29, 'nuclear': 27, 'renewables': 9},
            'co2_per_capita': 11.6,
            'food_security': 73.6,
            'arable_land': 2,
            'top_exports': ['Integrated Circuits', 'Cars', 'Refined Petroleum', 'Ships', 'Vehicle Parts'],
            'top_imports': ['Crude Petroleum', 'Integrated Circuits', 'Natural Gas', 'Refined Petroleum', 'Coal'],
            'minerals_produced': ['Zinc', 'Lead', 'Tungsten'],
            'crops_produced': ['Rice', 'Vegetables'],
        },
        'Saudi Arabia': {
            'flag': '🇸🇦',
            'region': 'Middle East',
            'capital': 'Riyadh',
            'population': {'value': 36, 'rank': 41, 'growth': 1.7},
            'gdp': {'value': 1.1, 'rank': 17, 'growth': -0.8},
            'gdp_per_capita': 30447,
            'debt_to_gdp': 26,
            'credit_rating': 'A',
            'inflation': 2.3,
            'unemployment': 4.8,
            'trade_balance': 130,
            'life_expectancy': 76.9,
            'median_age': 32.4,
            'urban_pct': 85,
            'electricity_gen': 387,
            'energy_mix': {'coal': 0, 'gas': 43, 'nuclear': 0, 'renewables': 1, 'oil': 56},
            'co2_per_capita': 18.2,
            'food_security': 68.5,
            'arable_land': 4,
            'top_exports': ['Crude Petroleum', 'Refined Petroleum', 'Polymers', 'Industrial Alcohols', 'Fertilizers'],
            'top_imports': ['Cars', 'Telephones', 'Refined Petroleum', 'Gold', 'Packaged Medicines'],
            'minerals_produced': ['Oil', 'Natural Gas', 'Gold', 'Phosphate'],
            'crops_produced': ['Dates', 'Wheat', 'Vegetables'],
        },
        'Indonesia': {
            'flag': '🇮🇩',
            'region': 'Southeast Asia',
            'capital': 'Jakarta',
            'population': {'value': 278, 'rank': 4, 'growth': 0.8},
            'gdp': {'value': 1.4, 'rank': 16, 'growth': 5.0},
            'gdp_per_capita': 5016,
            'debt_to_gdp': 40,
            'credit_rating': 'BBB',
            'inflation': 2.8,
            'unemployment': 5.3,
            'trade_balance': 47,
            'life_expectancy': 72.3,
            'median_age': 30.2,
            'urban_pct': 58,
            'electricity_gen': 310,
            'energy_mix': {'coal': 61, 'gas': 18, 'nuclear': 0, 'renewables': 18},
            'co2_per_capita': 2.3,
            'food_security': 60.2,
            'arable_land': 24,
            'top_exports': ['Palm Oil', 'Coal', 'Natural Gas', 'Nickel', 'Refined Petroleum'],
            'top_imports': ['Refined Petroleum', 'Crude Petroleum', 'Telephones', 'Machinery', 'Wheat'],
            'minerals_produced': ['Nickel', 'Coal', 'Copper', 'Gold', 'Tin'],
            'crops_produced': ['Palm Oil', 'Rice', 'Rubber', 'Cocoa'],
        },
    }

    # Country selector
    countries = sorted(COUNTRY_DATA.keys())
    selected_country = st.selectbox("Select a country:", countries, key="country_profile_select")

    if selected_country:
        data = COUNTRY_DATA[selected_country]

        # Header with flag and basic info
        st.markdown(f"## {data['flag']} {selected_country}")
        st.markdown(f"**Region:** {data['region']} | **Capital:** {data['capital']}")

        st.markdown("---")

        # Overview metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Population", f"{data['population']['value']}M", f"#{data['population']['rank']} globally")
        with col2:
            st.metric("GDP", f"${data['gdp']['value']}T", f"{data['gdp']['growth']:+.1f}% growth")
        with col3:
            st.metric("GDP/Capita", f"${data['gdp_per_capita']:,}")
        with col4:
            st.metric("Credit Rating", data['credit_rating'])
        with col5:
            st.metric("Debt/GDP", f"{data['debt_to_gdp']}%")

        st.markdown("---")

        # Tabs for different domains
        profile_tabs = st.tabs(["Economy", "Demographics", "Energy", "Trade", "Resources"])

        with profile_tabs[0]:
            st.subheader("Economic Indicators")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("GDP Growth", f"{data['gdp']['growth']}%")
            with col2:
                st.metric("Inflation", f"{data['inflation']}%")
            with col3:
                st.metric("Unemployment", f"{data['unemployment']}%")
            with col4:
                balance_color = "green" if data['trade_balance'] > 0 else "red"
                st.metric("Trade Balance", f"${data['trade_balance']:,}B")

            # GDP comparison
            all_gdp = [(c, d['gdp']['value']) for c, d in COUNTRY_DATA.items()]
            all_gdp.sort(key=lambda x: -x[1])
            gdp_df = pd.DataFrame(all_gdp[:10], columns=['Country', 'GDP (T$)'])

            fig_gdp = px.bar(
                gdp_df,
                x='GDP (T$)',
                y='Country',
                orientation='h',
                title='GDP Comparison (Top 10)',
                color='GDP (T$)',
                color_continuous_scale='Blues'
            )
            # Highlight selected country
            fig_gdp.update_layout(**get_clean_plotly_layout(), height=350)
            fig_gdp.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_gdp, use_container_width=True)

        with profile_tabs[1]:
            st.subheader("Demographics")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Population", f"{data['population']['value']}M")
            with col2:
                growth_str = f"{data['population']['growth']:+.1f}%" if data['population']['growth'] != 0 else "0%"
                st.metric("Pop. Growth", growth_str)
            with col3:
                st.metric("Median Age", f"{data['median_age']} years")
            with col4:
                st.metric("Life Expectancy", f"{data['life_expectancy']} years")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Urban Population", f"{data['urban_pct']}%")
            with col2:
                st.metric("Food Security Index", f"{data['food_security']}/100")

        with profile_tabs[2]:
            st.subheader("Energy Profile")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Electricity Generation", f"{data['electricity_gen']:,} TWh")
            with col2:
                st.metric("CO₂ per Capita", f"{data['co2_per_capita']} tons")

            # Energy mix pie chart
            energy_mix = data['energy_mix']
            energy_df = pd.DataFrame([
                {'Source': k.capitalize(), 'Share': v}
                for k, v in energy_mix.items() if v > 0
            ])

            fig_energy = px.pie(
                energy_df,
                values='Share',
                names='Source',
                title='Electricity Generation Mix (%)',
                color='Source',
                color_discrete_map={
                    'Coal': '#4a4a4a',
                    'Gas': '#87CEEB',
                    'Nuclear': '#9b59b6',
                    'Renewables': '#2ecc71',
                    'Oil': '#8B4513'
                }
            )
            fig_energy.update_layout(**get_clean_plotly_layout(), height=350)
            st.plotly_chart(fig_energy, use_container_width=True)

        with profile_tabs[3]:
            st.subheader("Trade Profile")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Top Exports")
                for i, exp in enumerate(data['top_exports'][:5], 1):
                    st.markdown(f"{i}. 📤 {exp}")

            with col2:
                st.markdown("##### Top Imports")
                for i, imp in enumerate(data['top_imports'][:5], 1):
                    st.markdown(f"{i}. 📥 {imp}")

            st.markdown("---")
            balance = data['trade_balance']
            if balance > 0:
                st.success(f"**Trade Surplus:** ${balance:,} billion")
            else:
                st.error(f"**Trade Deficit:** ${balance:,} billion")

        with profile_tabs[4]:
            st.subheader("Natural Resources")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### Minerals & Mining")
                for mineral in data['minerals_produced']:
                    st.markdown(f"- ⛏️ {mineral}")

            with col2:
                st.markdown("##### Agricultural Products")
                for crop in data['crops_produced']:
                    st.markdown(f"- 🌾 {crop}")

            st.metric("Arable Land", f"{data['arable_land']} million hectares")

    st.markdown("---")
    st.caption("Data aggregated from World Bank, IMF, UN, CIA World Factbook, and industry sources. Figures are 2023/2024 estimates.")


# ============================================================================
# PAGE: CORRELATION ANALYSIS
# ============================================================================

elif page == "Correlation Analysis":
    st.title("Correlation Analysis")
    st.markdown("*Explore relationships between different assets and indicators*")
    st.markdown("---")

    # Load data from database for correlation
    stocks_df = load_data("""
        SELECT symbol, price, timestamp
        FROM stocks
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        ORDER BY timestamp
    """)

    crypto_df = load_data("""
        SELECT symbol, price, timestamp
        FROM crypto
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        ORDER BY timestamp
    """)

    forex_df = load_data("""
        SELECT symbol, rate as price, timestamp
        FROM forex
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        ORDER BY timestamp
    """)

    commodities_df = load_data("""
        SELECT symbol, price, timestamp
        FROM commodities
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        ORDER BY timestamp
    """)

    # Correlation analysis tabs
    corr_tabs = st.tabs(["Cross-Asset", "Sector Correlation", "Currency Pairs", "Crypto-Equity", "Custom Analysis"])

    with corr_tabs[0]:
        st.subheader("Cross-Asset Correlations")
        st.markdown("*How different asset classes move together*")

        # Pre-defined correlations (representative values based on historical norms)
        CROSS_ASSET_CORR = {
            'S&P 500': {'S&P 500': 1.0, 'Nasdaq': 0.92, 'Gold': -0.15, 'Oil': 0.45, 'US Dollar': -0.35, 'Bitcoin': 0.42, '10Y Treasury': -0.45},
            'Nasdaq': {'S&P 500': 0.92, 'Nasdaq': 1.0, 'Gold': -0.20, 'Oil': 0.35, 'US Dollar': -0.40, 'Bitcoin': 0.55, '10Y Treasury': -0.50},
            'Gold': {'S&P 500': -0.15, 'Nasdaq': -0.20, 'Gold': 1.0, 'Oil': 0.25, 'US Dollar': -0.55, 'Bitcoin': 0.15, '10Y Treasury': 0.10},
            'Oil': {'S&P 500': 0.45, 'Nasdaq': 0.35, 'Gold': 0.25, 'Oil': 1.0, 'US Dollar': -0.20, 'Bitcoin': 0.20, '10Y Treasury': -0.15},
            'US Dollar': {'S&P 500': -0.35, 'Nasdaq': -0.40, 'Gold': -0.55, 'Oil': -0.20, 'US Dollar': 1.0, 'Bitcoin': -0.25, '10Y Treasury': 0.30},
            'Bitcoin': {'S&P 500': 0.42, 'Nasdaq': 0.55, 'Gold': 0.15, 'Oil': 0.20, 'US Dollar': -0.25, 'Bitcoin': 1.0, '10Y Treasury': -0.35},
            '10Y Treasury': {'S&P 500': -0.45, 'Nasdaq': -0.50, 'Gold': 0.10, 'Oil': -0.15, 'US Dollar': 0.30, 'Bitcoin': -0.35, '10Y Treasury': 1.0},
        }

        corr_matrix = pd.DataFrame(CROSS_ASSET_CORR)
        corr_matrix.index = corr_matrix.columns

        fig_heatmap = px.imshow(
            corr_matrix,
            labels=dict(color="Correlation"),
            x=corr_matrix.columns,
            y=corr_matrix.index,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            title='Cross-Asset Correlation Matrix'
        )
        fig_heatmap.update_layout(**get_clean_plotly_layout(), height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("""
        **Interpretation:**
        - 🟢 **+1.0** = Perfect positive correlation (move together)
        - ⚪ **0.0** = No correlation (independent)
        - 🔴 **-1.0** = Perfect negative correlation (move opposite)

        **Key Insights:**
        - Gold and US Dollar are negatively correlated (-0.55)
        - Bitcoin increasingly correlated with Nasdaq (0.55)
        - Bonds (10Y Treasury) inversely correlated with stocks
        """)

    with corr_tabs[1]:
        st.subheader("S&P 500 Sector Correlations")
        st.markdown("*How market sectors move relative to each other*")

        SECTOR_CORR = {
            'Technology': {'Technology': 1.00, 'Healthcare': 0.65, 'Financials': 0.72, 'Energy': 0.45, 'Consumer': 0.78, 'Utilities': 0.35, 'Real Estate': 0.55},
            'Healthcare': {'Technology': 0.65, 'Healthcare': 1.00, 'Financials': 0.60, 'Energy': 0.40, 'Consumer': 0.70, 'Utilities': 0.50, 'Real Estate': 0.55},
            'Financials': {'Technology': 0.72, 'Healthcare': 0.60, 'Financials': 1.00, 'Energy': 0.55, 'Consumer': 0.75, 'Utilities': 0.45, 'Real Estate': 0.65},
            'Energy': {'Technology': 0.45, 'Healthcare': 0.40, 'Financials': 0.55, 'Energy': 1.00, 'Consumer': 0.50, 'Utilities': 0.30, 'Real Estate': 0.40},
            'Consumer': {'Technology': 0.78, 'Healthcare': 0.70, 'Financials': 0.75, 'Energy': 0.50, 'Consumer': 1.00, 'Utilities': 0.45, 'Real Estate': 0.60},
            'Utilities': {'Technology': 0.35, 'Healthcare': 0.50, 'Financials': 0.45, 'Energy': 0.30, 'Consumer': 0.45, 'Utilities': 1.00, 'Real Estate': 0.70},
            'Real Estate': {'Technology': 0.55, 'Healthcare': 0.55, 'Financials': 0.65, 'Energy': 0.40, 'Consumer': 0.60, 'Utilities': 0.70, 'Real Estate': 1.00},
        }

        sector_matrix = pd.DataFrame(SECTOR_CORR)
        sector_matrix.index = sector_matrix.columns

        fig_sector = px.imshow(
            sector_matrix,
            labels=dict(color="Correlation"),
            color_continuous_scale='Blues',
            zmin=0,
            zmax=1,
            title='Sector Correlation Matrix'
        )
        fig_sector.update_layout(**get_clean_plotly_layout(), height=450)
        st.plotly_chart(fig_sector, use_container_width=True)

        st.markdown("""
        **Insights:**
        - Most sectors are positively correlated (markets tend to move together)
        - Energy is least correlated with other sectors (diversification opportunity)
        - Utilities and Real Estate highly correlated (both rate-sensitive)
        - Technology and Consumer Discretionary very correlated (growth plays)
        """)

    with corr_tabs[2]:
        st.subheader("Currency Pair Correlations")

        CURRENCY_CORR = {
            'EUR/USD': {'EUR/USD': 1.00, 'GBP/USD': 0.85, 'USD/JPY': -0.55, 'AUD/USD': 0.70, 'USD/CHF': -0.90},
            'GBP/USD': {'EUR/USD': 0.85, 'GBP/USD': 1.00, 'USD/JPY': -0.45, 'AUD/USD': 0.65, 'USD/CHF': -0.75},
            'USD/JPY': {'EUR/USD': -0.55, 'GBP/USD': -0.45, 'USD/JPY': 1.00, 'AUD/USD': -0.35, 'USD/CHF': 0.65},
            'AUD/USD': {'EUR/USD': 0.70, 'GBP/USD': 0.65, 'USD/JPY': -0.35, 'AUD/USD': 1.00, 'USD/CHF': -0.60},
            'USD/CHF': {'EUR/USD': -0.90, 'GBP/USD': -0.75, 'USD/JPY': 0.65, 'AUD/USD': -0.60, 'USD/CHF': 1.00},
        }

        currency_matrix = pd.DataFrame(CURRENCY_CORR)
        currency_matrix.index = currency_matrix.columns

        fig_currency = px.imshow(
            currency_matrix,
            labels=dict(color="Correlation"),
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            title='Major Currency Pair Correlations'
        )
        fig_currency.update_layout(**get_clean_plotly_layout(), height=400)
        st.plotly_chart(fig_currency, use_container_width=True)

        st.markdown("""
        **Key Relationships:**
        - EUR/USD and USD/CHF are strongly negatively correlated (-0.90) - classic hedge pair
        - EUR/USD and GBP/USD are highly positively correlated (0.85) - European currencies move together
        - USD/JPY tends to move opposite to EUR/USD - risk-on vs risk-off dynamics
        """)

    with corr_tabs[3]:
        st.subheader("Crypto-Equity Correlation")
        st.markdown("*How crypto assets correlate with traditional markets*")

        CRYPTO_EQUITY_CORR = {
            'Bitcoin': {'Bitcoin': 1.00, 'Ethereum': 0.90, 'S&P 500': 0.42, 'Nasdaq': 0.55, 'Gold': 0.15},
            'Ethereum': {'Bitcoin': 0.90, 'Ethereum': 1.00, 'S&P 500': 0.45, 'Nasdaq': 0.60, 'Gold': 0.10},
            'S&P 500': {'Bitcoin': 0.42, 'Ethereum': 0.45, 'S&P 500': 1.00, 'Nasdaq': 0.92, 'Gold': -0.15},
            'Nasdaq': {'Bitcoin': 0.55, 'Ethereum': 0.60, 'S&P 500': 0.92, 'Nasdaq': 1.00, 'Gold': -0.20},
            'Gold': {'Bitcoin': 0.15, 'Ethereum': 0.10, 'S&P 500': -0.15, 'Nasdaq': -0.20, 'Gold': 1.00},
        }

        crypto_matrix = pd.DataFrame(CRYPTO_EQUITY_CORR)
        crypto_matrix.index = crypto_matrix.columns

        fig_crypto = px.imshow(
            crypto_matrix,
            labels=dict(color="Correlation"),
            color_continuous_scale='Viridis',
            zmin=-0.5,
            zmax=1,
            title='Crypto vs Traditional Assets'
        )
        fig_crypto.update_layout(**get_clean_plotly_layout(), height=400)
        st.plotly_chart(fig_crypto, use_container_width=True)

        st.markdown("""
        **Evolution of Crypto Correlation:**
        - Bitcoin and Ethereum highly correlated (0.90) - crypto moves as an asset class
        - Crypto increasingly correlated with tech stocks since 2020
        - Ethereum slightly more correlated to equities than Bitcoin
        - Gold correlation remains low - crypto not acting as "digital gold" in practice
        """)

    with corr_tabs[4]:
        st.subheader("Custom Correlation Analysis")

        st.markdown("Select assets from database to calculate correlation:")

        # Get available symbols
        available_stocks = []
        available_crypto = []

        if not stocks_df.empty:
            available_stocks = stocks_df['symbol'].unique().tolist()

        if not crypto_df.empty:
            available_crypto = crypto_df['symbol'].unique().tolist()

        if available_stocks or available_crypto:
            all_assets = sorted(set(available_stocks + available_crypto))

            col1, col2 = st.columns(2)
            with col1:
                asset1 = st.selectbox("Select first asset:", all_assets, key="corr_asset1")
            with col2:
                asset2 = st.selectbox("Select second asset:", [a for a in all_assets if a != asset1], key="corr_asset2")

            if asset1 and asset2:
                # Get price series for both
                if asset1 in available_stocks:
                    prices1 = stocks_df[stocks_df['symbol'] == asset1][['timestamp', 'price']].copy()
                else:
                    prices1 = crypto_df[crypto_df['symbol'] == asset1][['timestamp', 'price']].copy()

                if asset2 in available_stocks:
                    prices2 = stocks_df[stocks_df['symbol'] == asset2][['timestamp', 'price']].copy()
                else:
                    prices2 = crypto_df[crypto_df['symbol'] == asset2][['timestamp', 'price']].copy()

                prices1 = prices1.rename(columns={'price': asset1})
                prices2 = prices2.rename(columns={'price': asset2})

                # Merge and calculate correlation
                if not prices1.empty and not prices2.empty:
                    prices1['timestamp'] = pd.to_datetime(prices1['timestamp']).dt.date
                    prices2['timestamp'] = pd.to_datetime(prices2['timestamp']).dt.date

                    merged = pd.merge(prices1, prices2, on='timestamp', how='inner')

                    if len(merged) > 5:
                        merged[asset1] = merged[asset1].astype(float)
                        merged[asset2] = merged[asset2].astype(float)
                        correlation = merged[asset1].corr(merged[asset2])

                        col1, col2, col3 = st.columns(3)
                        with col2:
                            corr_color = '#2ecc71' if abs(correlation) < 0.3 else '#f39c12' if abs(correlation) < 0.7 else '#e74c3c'
                            st.metric("Correlation", f"{correlation:.3f}")

                        # Scatter plot
                        fig_scatter = px.scatter(
                            merged,
                            x=asset1,
                            y=asset2,
                            title=f'{asset1} vs {asset2} (30-day correlation: {correlation:.3f})',
                            trendline='ols'
                        )
                        fig_scatter.update_layout(**get_clean_plotly_layout(), height=400)
                        st.plotly_chart(fig_scatter, use_container_width=True)

                        # Interpretation
                        if abs(correlation) > 0.7:
                            st.warning(f"**Strong {'positive' if correlation > 0 else 'negative'} correlation** - These assets tend to move {'together' if correlation > 0 else 'opposite'}.")
                        elif abs(correlation) > 0.3:
                            st.info(f"**Moderate {'positive' if correlation > 0 else 'negative'} correlation** - Some relationship exists.")
                        else:
                            st.success("**Low correlation** - Good for diversification.")
                    else:
                        st.warning("Not enough overlapping data points to calculate correlation.")
                else:
                    st.warning("No price data available for selected assets.")
        else:
            st.info("No asset data available in database. Run data collectors to populate.")

    st.markdown("---")
    st.caption("Correlations are based on historical price movements and can change over time.")
    st.caption("Past correlations do not guarantee future relationships.")


# ============================================================================
# PAGE: RISK METRICS
# ============================================================================

elif page == "Risk Metrics":
    st.title("Risk Metrics & Portfolio Analytics")
    st.markdown("*Value at Risk, volatility analysis, and risk-adjusted returns*")
    st.markdown("---")

    # Load stock data for risk calculations
    stocks_df = load_data("""
        SELECT symbol, price, change_percent, volume, timestamp
        FROM stocks
        WHERE timestamp > NOW() - INTERVAL '30 days'
        ORDER BY symbol, timestamp
    """)

    # Risk Metrics Tabs
    risk_tab1, risk_tab2, risk_tab3, risk_tab4, risk_tab5 = st.tabs([
        "VaR Analysis", "Volatility", "Sharpe Ratios", "Drawdown Analysis", "Risk Dashboard"
    ])

    with risk_tab1:
        st.subheader("Value at Risk (VaR)")
        st.markdown("*Estimated maximum loss at different confidence levels*")

        # VaR data - curated examples
        VAR_DATA = {
            'S&P 500': {'daily_vol': 1.2, 'var_95': -1.97, 'var_99': -2.79, 'cvar_95': -2.48},
            'NASDAQ 100': {'daily_vol': 1.6, 'var_95': -2.63, 'var_99': -3.72, 'cvar_95': -3.31},
            'Russell 2000': {'daily_vol': 1.8, 'var_95': -2.96, 'var_99': -4.19, 'cvar_95': -3.73},
            'Bitcoin': {'daily_vol': 4.2, 'var_95': -6.91, 'var_99': -9.77, 'cvar_95': -8.70},
            'Gold': {'daily_vol': 0.9, 'var_95': -1.48, 'var_99': -2.09, 'cvar_95': -1.86},
            'Crude Oil': {'daily_vol': 2.5, 'var_95': -4.11, 'var_99': -5.82, 'cvar_95': -5.18},
            'EUR/USD': {'daily_vol': 0.5, 'var_95': -0.82, 'var_99': -1.16, 'cvar_95': -1.04},
            '10Y Treasury': {'daily_vol': 0.6, 'var_95': -0.99, 'var_99': -1.40, 'cvar_95': -1.24},
        }

        var_df = pd.DataFrame([
            {'Asset': asset, 'Daily Vol %': data['daily_vol'],
             'VaR 95%': data['var_95'], 'VaR 99%': data['var_99'],
             'CVaR 95%': data['cvar_95']}
            for asset, data in VAR_DATA.items()
        ])

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(var_df, use_container_width=True, hide_index=True)

        with col2:
            fig_var = px.bar(
                var_df, x='Asset', y=['VaR 95%', 'VaR 99%'],
                title='Value at Risk by Asset',
                barmode='group',
                color_discrete_sequence=['#ff6b6b', '#ee5253']
            )
            fig_var.update_layout(yaxis_title='VaR (%)', xaxis_title='')
            st.plotly_chart(fig_var, use_container_width=True)

        st.markdown("---")
        st.subheader("Portfolio VaR Calculator")

        port_col1, port_col2 = st.columns(2)
        with port_col1:
            portfolio_value = st.number_input("Portfolio Value ($)", value=100000, step=10000)
            confidence = st.selectbox("Confidence Level", ["95%", "99%"])
            time_horizon = st.selectbox("Time Horizon", ["1 Day", "1 Week", "1 Month"])

        with port_col2:
            # Simple portfolio VaR calculation
            base_var_pct = 1.97 if confidence == "95%" else 2.79
            horizon_mult = {'1 Day': 1, '1 Week': np.sqrt(5), '1 Month': np.sqrt(21)}
            adjusted_var = base_var_pct * horizon_mult[time_horizon]
            var_dollar = portfolio_value * (adjusted_var / 100)

            st.metric("Portfolio VaR", f"${var_dollar:,.0f}", f"-{adjusted_var:.2f}%")
            st.caption(f"At {confidence} confidence, you could lose up to ${var_dollar:,.0f} over {time_horizon.lower()}")

    with risk_tab2:
        st.subheader("Volatility Analysis")

        # Historical volatility data
        VOLATILITY_DATA = {
            'Asset': ['S&P 500', 'NASDAQ', 'Russell 2000', 'Bitcoin', 'Ethereum',
                     'Gold', 'Crude Oil', 'EUR/USD', 'VIX'],
            '1W Vol': [8.5, 12.3, 14.2, 52.1, 61.3, 11.2, 35.8, 6.1, 95.2],
            '1M Vol': [12.1, 16.8, 18.9, 58.4, 68.9, 13.5, 38.2, 7.3, 102.4],
            '3M Vol': [14.5, 19.2, 21.3, 62.1, 72.5, 15.1, 41.5, 8.2, 89.6],
            '1Y Vol': [16.8, 22.1, 24.5, 71.2, 82.3, 14.8, 39.8, 8.9, 85.3],
        }
        vol_df = pd.DataFrame(VOLATILITY_DATA)

        st.dataframe(vol_df, use_container_width=True, hide_index=True)

        # Volatility heatmap
        vol_matrix = vol_df.set_index('Asset')[['1W Vol', '1M Vol', '3M Vol', '1Y Vol']]
        fig_vol = px.imshow(
            vol_matrix,
            labels=dict(color="Volatility %"),
            color_continuous_scale='YlOrRd',
            title='Volatility Heatmap (Annualized %)'
        )
        fig_vol.update_layout(height=400)
        st.plotly_chart(fig_vol, use_container_width=True)

        # VIX Term Structure
        st.markdown("---")
        st.subheader("VIX Term Structure")
        vix_term = pd.DataFrame({
            'Expiry': ['Spot', '1M', '2M', '3M', '4M', '5M', '6M'],
            'VIX Level': [14.2, 15.8, 16.5, 17.1, 17.4, 17.6, 17.8]
        })
        fig_vix = px.line(vix_term, x='Expiry', y='VIX Level',
                         title='VIX Futures Term Structure',
                         markers=True)
        fig_vix.update_traces(line=dict(color='#9b59b6', width=3))
        st.plotly_chart(fig_vix, use_container_width=True)

    with risk_tab3:
        st.subheader("Risk-Adjusted Returns")

        SHARPE_DATA = {
            'Asset': ['S&P 500', 'NASDAQ 100', 'Russell 2000', 'MSCI EM', 'MSCI EAFE',
                     'US Bonds', 'Gold', 'REITs', '60/40 Portfolio'],
            'Return %': [12.5, 18.2, 8.9, 6.2, 9.8, 4.2, 8.5, 7.8, 9.2],
            'Volatility %': [16.8, 22.1, 24.5, 18.9, 17.2, 5.8, 14.8, 19.2, 11.5],
            'Sharpe': [0.62, 0.73, 0.28, 0.22, 0.46, 0.38, 0.44, 0.31, 0.63],
            'Sortino': [0.89, 1.05, 0.41, 0.32, 0.67, 0.52, 0.61, 0.45, 0.88],
            'Max DD %': [-19.8, -28.5, -32.1, '-24.6', -21.2, -8.9, -18.2, -25.8, -14.2],
        }
        sharpe_df = pd.DataFrame(SHARPE_DATA)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(sharpe_df, use_container_width=True, hide_index=True)

        with col2:
            fig_sharpe = px.bar(
                sharpe_df, x='Asset', y='Sharpe',
                title='Sharpe Ratios by Asset Class',
                color='Sharpe',
                color_continuous_scale='RdYlGn'
            )
            fig_sharpe.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_sharpe, use_container_width=True)

        # Risk/Return Scatter
        st.markdown("---")
        fig_rr = px.scatter(
            sharpe_df, x='Volatility %', y='Return %',
            text='Asset', title='Risk-Return Profile',
            size=[100]*len(sharpe_df),
            color='Sharpe',
            color_continuous_scale='RdYlGn'
        )
        fig_rr.update_traces(textposition='top center')
        fig_rr.add_hline(y=4.5, line_dash="dash", annotation_text="Risk-Free Rate")
        st.plotly_chart(fig_rr, use_container_width=True)

    with risk_tab4:
        st.subheader("Drawdown Analysis")

        # Maximum drawdown data
        DRAWDOWN_DATA = {
            'Asset': ['S&P 500', 'NASDAQ', 'Bitcoin', 'Gold', 'Crude Oil'],
            'Current DD %': [-2.1, -5.8, -12.4, -1.2, -8.5],
            'Max DD (1Y) %': [-10.3, '-15.8', -48.2, -8.5, -22.1],
            'Max DD (5Y) %': [-33.9, '-35.1', -77.2, -21.5, -65.8],
            'Avg Recovery Days': [45, 62, 180, 38, 95],
        }
        dd_df = pd.DataFrame(DRAWDOWN_DATA)

        st.dataframe(dd_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            # Current drawdown gauge
            fig_dd = px.bar(
                dd_df, x='Asset', y='Current DD %',
                title='Current Drawdown from Peak',
                color='Current DD %',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_dd, use_container_width=True)

        with col2:
            # Recovery time
            fig_rec = px.bar(
                dd_df, x='Asset', y='Avg Recovery Days',
                title='Average Recovery Time (Days)',
                color='Avg Recovery Days',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_rec, use_container_width=True)

        # Drawdown history simulation
        st.markdown("---")
        st.subheader("Simulated Drawdown History (S&P 500)")
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.0004, 0.012, 252)
        prices = 100 * np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(prices)
        drawdown = (prices - running_max) / running_max * 100

        dd_history = pd.DataFrame({'Date': dates, 'Drawdown %': drawdown})
        fig_ddhist = px.area(dd_history, x='Date', y='Drawdown %',
                            title='Rolling Drawdown (1 Year)',
                            color_discrete_sequence=['#e74c3c'])
        fig_ddhist.update_layout(yaxis_title='Drawdown (%)')
        st.plotly_chart(fig_ddhist, use_container_width=True)

    with risk_tab5:
        st.subheader("Risk Dashboard Summary")

        # Key risk metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("VIX", "14.2", "-2.1", delta_color="inverse")
        with col2:
            st.metric("Put/Call Ratio", "0.82", "-0.05")
        with col3:
            st.metric("Fear & Greed", "62", "+8", help="0=Extreme Fear, 100=Extreme Greed")
        with col4:
            st.metric("Credit Spreads", "1.24%", "+0.08%", delta_color="inverse")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Risk Regime")
            risk_regime = pd.DataFrame({
                'Indicator': ['VIX Level', 'Credit Spreads', 'Yield Curve', 'Momentum', 'Breadth'],
                'Status': ['Low', 'Normal', 'Inverted', 'Positive', 'Healthy'],
                'Signal': ['🟢', '🟢', '🔴', '🟢', '🟢']
            })
            st.dataframe(risk_regime, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Sector Risk Heat")
            sector_risk = pd.DataFrame({
                'Sector': ['Technology', 'Financials', 'Healthcare', 'Energy', 'Consumer'],
                'Beta': [1.25, 1.15, 0.85, 1.35, 0.95],
                'Vol Rank': ['High', 'Medium', 'Low', 'High', 'Medium']
            })
            st.dataframe(sector_risk, use_container_width=True, hide_index=True)

        # Correlation breakdown risk
        st.markdown("---")
        st.subheader("Correlation Regime Monitor")
        st.caption("When correlations spike, diversification benefits decrease")

        corr_regime = pd.DataFrame({
            'Period': ['Normal', 'Stress (2020)', 'Current'],
            'Equity-Bond': [-0.25, 0.45, -0.18],
            'Equity-Gold': [0.05, -0.35, 0.02],
            'Cross-Equity': [0.65, 0.92, 0.68],
        })
        st.dataframe(corr_regime, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: ECONOMIC CALENDAR
# ============================================================================

elif page == "Economic Calendar":
    st.title("Economic Calendar")
    st.markdown("*Upcoming data releases and market-moving events*")
    st.markdown("---")

    # Economic Calendar Data (curated upcoming events)
    CALENDAR_DATA = [
        # This Week
        {'date': 'Mon Dec 16', 'time': '08:30', 'event': 'NY Empire State Manufacturing', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '-11.9', 'forecast': '-10.5'},
        {'date': 'Mon Dec 16', 'time': '09:45', 'event': 'S&P Global Manufacturing PMI', 'country': '🇺🇸', 'importance': 'High', 'previous': '49.7', 'forecast': '49.8'},
        {'date': 'Tue Dec 17', 'time': '08:30', 'event': 'Retail Sales MoM', 'country': '🇺🇸', 'importance': 'High', 'previous': '0.4%', 'forecast': '0.5%'},
        {'date': 'Tue Dec 17', 'time': '09:15', 'event': 'Industrial Production', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '-0.3%', 'forecast': '0.1%'},
        {'date': 'Wed Dec 18', 'time': '10:30', 'event': 'Crude Oil Inventories', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '-1.4M', 'forecast': '-2.0M'},
        {'date': 'Wed Dec 18', 'time': '14:00', 'event': 'FOMC Rate Decision', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '4.75%', 'forecast': '4.50%'},
        {'date': 'Wed Dec 18', 'time': '14:30', 'event': 'FOMC Press Conference', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '-', 'forecast': '-'},
        {'date': 'Thu Dec 19', 'time': '07:00', 'event': 'BoE Interest Rate Decision', 'country': '🇬🇧', 'importance': 'Critical', 'previous': '4.75%', 'forecast': '4.75%'},
        {'date': 'Thu Dec 19', 'time': '08:30', 'event': 'GDP QoQ Final', 'country': '🇺🇸', 'importance': 'High', 'previous': '2.8%', 'forecast': '2.8%'},
        {'date': 'Thu Dec 19', 'time': '08:30', 'event': 'Initial Jobless Claims', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '242K', 'forecast': '235K'},
        {'date': 'Thu Dec 19', 'time': '10:00', 'event': 'Existing Home Sales', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '3.96M', 'forecast': '4.05M'},
        {'date': 'Fri Dec 20', 'time': '08:30', 'event': 'PCE Price Index MoM', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '0.2%', 'forecast': '0.2%'},
        {'date': 'Fri Dec 20', 'time': '08:30', 'event': 'Core PCE Price Index YoY', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '2.8%', 'forecast': '2.9%'},
        {'date': 'Fri Dec 20', 'time': '08:30', 'event': 'Personal Income MoM', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '0.6%', 'forecast': '0.4%'},
        {'date': 'Fri Dec 20', 'time': '10:00', 'event': 'Consumer Sentiment Final', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '71.8', 'forecast': '74.0'},
        # Next Week
        {'date': 'Mon Dec 23', 'time': '08:30', 'event': 'Chicago Fed National Activity', 'country': '🇺🇸', 'importance': 'Low', 'previous': '-0.40', 'forecast': '-0.20'},
        {'date': 'Tue Dec 24', 'time': '08:30', 'event': 'Durable Goods Orders', 'country': '🇺🇸', 'importance': 'High', 'previous': '0.3%', 'forecast': '-0.2%'},
        {'date': 'Tue Dec 24', 'time': '10:00', 'event': 'New Home Sales', 'country': '🇺🇸', 'importance': 'Medium', 'previous': '610K', 'forecast': '640K'},
        {'date': 'Thu Dec 26', 'time': '-', 'event': 'US Markets Closed (Christmas)', 'country': '🇺🇸', 'importance': 'Holiday', 'previous': '-', 'forecast': '-'},
        # Upcoming Major Events
        {'date': 'Fri Jan 3', 'time': '10:00', 'event': 'ISM Manufacturing PMI', 'country': '🇺🇸', 'importance': 'High', 'previous': '48.4', 'forecast': '48.8'},
        {'date': 'Fri Jan 10', 'time': '08:30', 'event': 'Nonfarm Payrolls', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '227K', 'forecast': '180K'},
        {'date': 'Wed Jan 15', 'time': '08:30', 'event': 'CPI MoM', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '0.3%', 'forecast': '0.2%'},
        {'date': 'Wed Jan 29', 'time': '14:00', 'event': 'FOMC Rate Decision', 'country': '🇺🇸', 'importance': 'Critical', 'previous': '4.50%', 'forecast': '4.50%'},
    ]

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        importance_filter = st.multiselect(
            "Filter by Importance",
            ['Critical', 'High', 'Medium', 'Low', 'Holiday'],
            default=['Critical', 'High']
        )
    with col2:
        country_filter = st.multiselect(
            "Filter by Country",
            ['🇺🇸', '🇬🇧', '🇪🇺', '🇯🇵', '🇨🇳'],
            default=['🇺🇸', '🇬🇧']
        )
    with col3:
        st.caption("Times shown in ET")

    st.markdown("---")

    # Display calendar
    filtered_events = [e for e in CALENDAR_DATA
                      if e['importance'] in importance_filter
                      and e['country'] in country_filter]

    if filtered_events:
        for event in filtered_events:
            imp = event['importance']
            if imp == 'Critical':
                color = '#e74c3c'
                icon = '🔴'
            elif imp == 'High':
                color = '#f39c12'
                icon = '🟠'
            elif imp == 'Holiday':
                color = '#9b59b6'
                icon = '📅'
            else:
                color = '#3498db'
                icon = '🔵'

            col1, col2, col3, col4, col5 = st.columns([2, 1, 4, 1.5, 1.5])
            with col1:
                st.markdown(f"**{event['date']}** {event['time']}")
            with col2:
                st.markdown(event['country'])
            with col3:
                st.markdown(f"{icon} {event['event']}")
            with col4:
                st.caption(f"Prev: {event['previous']}")
            with col5:
                st.caption(f"Fcst: {event['forecast']}")

    else:
        st.info("No events match your filters")

    st.markdown("---")

    # Central Bank Calendar
    st.subheader("Central Bank Meeting Schedule 2025")

    cb_schedule = pd.DataFrame({
        'Central Bank': ['Federal Reserve', 'Federal Reserve', 'ECB', 'ECB', 'Bank of England', 'Bank of Japan'],
        'Meeting Date': ['Jan 28-29', 'Mar 18-19', 'Jan 30', 'Mar 6', 'Feb 6', 'Jan 23-24'],
        'Current Rate': ['4.50%', '4.50%', '3.00%', '3.00%', '4.75%', '0.25%'],
        'Market Expects': ['Hold', 'Cut 25bp', 'Cut 25bp', 'Cut 25bp', 'Hold', 'Hold'],
    })
    st.dataframe(cb_schedule, use_container_width=True, hide_index=True)

    # Earnings Calendar Preview
    st.markdown("---")
    st.subheader("Upcoming Earnings (Major Companies)")

    earnings = pd.DataFrame({
        'Company': ['Nike', 'FedEx', 'Micron', 'Carnival', 'Apple', 'Tesla', 'Netflix'],
        'Ticker': ['NKE', 'FDX', 'MU', 'CCL', 'AAPL', 'TSLA', 'NFLX'],
        'Report Date': ['Dec 19', 'Dec 19', 'Dec 18', 'Dec 20', 'Jan 30', 'Jan 29', 'Jan 21'],
        'EPS Est': ['$0.63', '$3.88', '$1.76', '$0.05', '$2.35', '$0.73', '$4.20'],
        'Rev Est': ['$12.1B', '$22.0B', '$8.7B', '$5.9B', '$124B', '$25.6B', '$10.1B'],
    })
    st.dataframe(earnings, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: WATCHLIST
# ============================================================================

elif page == "Watchlist":
    st.title("Watchlist")
    st.markdown("*Track your favorite assets and set price alerts*")
    st.markdown("---")

    # Initialize session state for watchlist
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'BTC', 'ETH', 'SPY', 'QQQ']

    if 'alerts' not in st.session_state:
        st.session_state.alerts = []

    # Add to watchlist
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        new_symbol = st.text_input("Add Symbol", placeholder="Enter ticker symbol...").upper()
    with col2:
        if st.button("Add", type="primary") and new_symbol:
            if new_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_symbol)
                st.success(f"Added {new_symbol}")
            else:
                st.warning(f"{new_symbol} already in watchlist")
    with col3:
        if st.button("Clear All"):
            st.session_state.watchlist = []
            st.rerun()

    st.markdown("---")

    # Load current data for watchlist items
    if st.session_state.watchlist:
        watchlist_str = "', '".join(st.session_state.watchlist)

        # Load stock data
        stocks_wl = load_data(f"""
            SELECT DISTINCT ON (symbol) symbol, price, change_percent, volume, timestamp
            FROM stocks
            WHERE symbol IN ('{watchlist_str}')
            ORDER BY symbol, timestamp DESC
        """)

        # Load crypto data
        crypto_wl = load_data(f"""
            SELECT DISTINCT ON (symbol) symbol, price, change_24h as change_percent, volume_24h as volume, timestamp
            FROM crypto
            WHERE symbol IN ('{watchlist_str}')
            ORDER BY symbol, timestamp DESC
        """)

        # Combine data
        all_data = pd.concat([stocks_wl, crypto_wl], ignore_index=True) if not stocks_wl.empty or not crypto_wl.empty else pd.DataFrame()

        if not all_data.empty:
            st.subheader("Your Watchlist")

            for symbol in st.session_state.watchlist:
                symbol_data = all_data[all_data['symbol'] == symbol]

                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

                with col1:
                    st.markdown(f"**{symbol}**")

                if not symbol_data.empty:
                    row = symbol_data.iloc[0]
                    price = float(row['price']) if row['price'] else 0
                    change = float(row['change_percent']) if row['change_percent'] else 0

                    with col2:
                        st.metric("Price", f"${price:,.2f}")

                    with col3:
                        delta_color = "normal" if change >= 0 else "inverse"
                        st.metric("Change", f"{change:+.2f}%", delta_color=delta_color)

                    with col4:
                        if row['timestamp']:
                            ts = pd.to_datetime(row['timestamp'])
                            st.caption(f"Updated: {ts.strftime('%H:%M')}")
                else:
                    with col2:
                        st.caption("No data")
                    with col3:
                        st.caption("-")
                    with col4:
                        st.caption("-")

                with col5:
                    if st.button("🗑️", key=f"remove_{symbol}"):
                        st.session_state.watchlist.remove(symbol)
                        st.rerun()

        else:
            st.info("No data available for watchlist symbols")

    else:
        st.info("Your watchlist is empty. Add symbols above to get started.")

    st.markdown("---")

    # Price Alerts Section
    st.subheader("Price Alerts")

    alert_col1, alert_col2, alert_col3, alert_col4 = st.columns([2, 2, 2, 1])
    with alert_col1:
        alert_symbol = st.selectbox("Symbol", options=st.session_state.watchlist if st.session_state.watchlist else [''])
    with alert_col2:
        alert_type = st.selectbox("Alert Type", ["Above", "Below"])
    with alert_col3:
        alert_price = st.number_input("Price", min_value=0.0, step=1.0)
    with alert_col4:
        if st.button("Set Alert", type="secondary"):
            if alert_symbol and alert_price > 0:
                st.session_state.alerts.append({
                    'symbol': alert_symbol,
                    'type': alert_type,
                    'price': alert_price,
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                st.success(f"Alert set: {alert_symbol} {alert_type.lower()} ${alert_price:,.2f}")

    if st.session_state.alerts:
        st.markdown("---")
        st.subheader("Active Alerts")

        for i, alert in enumerate(st.session_state.alerts):
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            with col1:
                st.markdown(f"**{alert['symbol']}**")
            with col2:
                icon = "📈" if alert['type'] == "Above" else "📉"
                st.markdown(f"{icon} {alert['type']} ${alert['price']:,.2f}")
            with col3:
                st.caption(f"Set: {alert['created']}")
            with col4:
                if st.button("❌", key=f"del_alert_{i}"):
                    st.session_state.alerts.pop(i)
                    st.rerun()

    # Quick Stats
    st.markdown("---")
    st.subheader("Watchlist Summary")

    if not all_data.empty:
        col1, col2, col3, col4 = st.columns(4)

        gainers = all_data[all_data['change_percent'] > 0]
        losers = all_data[all_data['change_percent'] < 0]

        with col1:
            st.metric("Total Items", len(st.session_state.watchlist))
        with col2:
            st.metric("Gainers", len(gainers), delta_color="normal")
        with col3:
            st.metric("Losers", len(losers), delta_color="inverse")
        with col4:
            avg_change = all_data['change_percent'].mean() if not all_data.empty else 0
            st.metric("Avg Change", f"{avg_change:+.2f}%")


# ============================================================================
# PAGE: BOND MARKETS
# ============================================================================

elif page == "Bond Markets":
    st.title("Bond Markets & Fixed Income")
    st.markdown("*Treasury yields, credit spreads, and global sovereign debt*")
    st.markdown("---")

    bond_tab1, bond_tab2, bond_tab3, bond_tab4 = st.tabs([
        "US Treasuries", "Yield Curves", "Credit Markets", "Global Sovereigns"
    ])

    with bond_tab1:
        st.subheader("US Treasury Yields")

        # Current Treasury yields
        TREASURY_DATA = {
            'Maturity': ['1 Month', '3 Month', '6 Month', '1 Year', '2 Year',
                        '3 Year', '5 Year', '7 Year', '10 Year', '20 Year', '30 Year'],
            'Yield %': [4.58, 4.52, 4.45, 4.28, 4.18, 4.12, 4.08, 4.12, 4.22, 4.51, 4.42],
            'Change': [+0.02, -0.01, -0.03, -0.05, -0.08, -0.06, -0.04, -0.02, +0.01, +0.03, +0.02],
            '1W Ago': [4.52, 4.50, 4.48, 4.35, 4.28, 4.20, 4.15, 4.18, 4.25, 4.52, 4.43],
            '1M Ago': [4.45, 4.42, 4.38, 4.22, 4.08, 4.02, 3.98, 4.05, 4.18, 4.48, 4.38],
        }
        treasury_df = pd.DataFrame(TREASURY_DATA)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(treasury_df, use_container_width=True, hide_index=True)

        with col2:
            fig_tsy = px.line(treasury_df, x='Maturity', y='Yield %',
                             title='Treasury Yield Curve',
                             markers=True)
            fig_tsy.update_traces(line=dict(color='#3498db', width=3))
            st.plotly_chart(fig_tsy, use_container_width=True)

        # Key spreads
        st.markdown("---")
        st.subheader("Key Spreads")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            spread_2_10 = 4.22 - 4.18
            st.metric("2Y-10Y Spread", f"{spread_2_10*100:.0f} bp", "+3 bp")
        with col2:
            spread_3m_10 = 4.22 - 4.52
            st.metric("3M-10Y Spread", f"{spread_3m_10*100:.0f} bp", "-5 bp", delta_color="inverse")
        with col3:
            st.metric("Real 10Y Yield", "1.92%", "+0.05%")
        with col4:
            st.metric("10Y TIPS Breakeven", "2.30%", "-0.02%")

    with bond_tab2:
        st.subheader("Yield Curve Analysis")

        # Historical yield curve comparison
        maturities = ['3M', '6M', '1Y', '2Y', '5Y', '10Y', '30Y']
        yields_today = [4.52, 4.45, 4.28, 4.18, 4.08, 4.22, 4.42]
        yields_1m = [4.42, 4.38, 4.22, 4.08, 3.98, 4.18, 4.38]
        yields_1y = [5.48, 5.42, 5.18, 4.88, 4.42, 4.58, 4.72]

        curve_df = pd.DataFrame({
            'Maturity': maturities * 3,
            'Yield': yields_today + yields_1m + yields_1y,
            'Period': ['Current']*7 + ['1 Month Ago']*7 + ['1 Year Ago']*7
        })

        fig_curve = px.line(curve_df, x='Maturity', y='Yield', color='Period',
                           title='Yield Curve Evolution',
                           markers=True)
        st.plotly_chart(fig_curve, use_container_width=True)

        # Yield curve shape indicator
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Curve Shape Indicators")
            shape_data = pd.DataFrame({
                'Indicator': ['2s10s Spread', '3m10y Spread', 'Curve Slope', 'Curvature'],
                'Value': ['+4 bp', '-30 bp', 'Inverted', 'Steepening'],
                'Signal': ['🟡 Flat', '🔴 Inverted', '🔴 Recession Risk', '🟢 Normalizing']
            })
            st.dataframe(shape_data, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("Historical Context")
            st.markdown("""
            - **Inverted curve** (3M > 10Y): Often precedes recessions
            - **Current state**: Curve normalizing from deep inversion
            - **Fed policy**: Rate cuts expected to steepen curve
            - **Watch**: Credit spreads for stress signals
            """)

    with bond_tab3:
        st.subheader("Credit Markets")

        # Credit spreads data
        CREDIT_SPREADS = {
            'Index': ['IG Corporate', 'High Yield', 'BBB Spread', 'CCC Spread',
                     'EM Sovereign', 'MBS Spread'],
            'Spread (bp)': [92, 298, 124, 892, 342, 145],
            'Change': [-3, +8, -2, +25, +12, -5],
            '52W Low': [82, 268, 108, 712, 298, 125],
            '52W High': [145, 485, 182, 1250, 498, 215],
        }
        credit_df = pd.DataFrame(CREDIT_SPREADS)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(credit_df, use_container_width=True, hide_index=True)

        with col2:
            fig_credit = px.bar(credit_df, x='Index', y='Spread (bp)',
                               title='Credit Spreads Over Treasuries',
                               color='Spread (bp)',
                               color_continuous_scale='RdYlGn_r')
            fig_credit.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_credit, use_container_width=True)

        # Corporate bond yields
        st.markdown("---")
        st.subheader("Corporate Bond Yields")

        corp_yields = pd.DataFrame({
            'Rating': ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC'],
            'Yield %': [4.85, 5.02, 5.28, 5.52, 6.42, 7.85, 13.12],
            'Spread bp': [42, 58, 85, 108, 198, 342, 868],
        })

        fig_corp = px.bar(corp_yields, x='Rating', y='Yield %',
                         title='Corporate Bond Yields by Rating',
                         color='Yield %',
                         color_continuous_scale='Reds')
        st.plotly_chart(fig_corp, use_container_width=True)

    with bond_tab4:
        st.subheader("Global Sovereign Yields")

        SOVEREIGN_DATA = {
            'Country': ['🇺🇸 United States', '🇩🇪 Germany', '🇯🇵 Japan', '🇬🇧 United Kingdom',
                       '🇫🇷 France', '🇮🇹 Italy', '🇪🇸 Spain', '🇨🇦 Canada',
                       '🇦🇺 Australia', '🇨🇭 Switzerland', '🇨🇳 China', '🇮🇳 India'],
            '2Y Yield': [4.18, 2.05, 0.58, 4.22, 2.42, 2.68, 2.45, 3.12, 3.85, 0.42, 1.42, 6.85],
            '10Y Yield': [4.22, 2.18, 1.05, 4.42, 2.95, 3.42, 2.88, 3.25, 4.28, 0.38, 2.12, 6.92],
            'Spread to UST': [0, -204, -317, +20, -127, -80, -134, -97, +6, -384, -210, +270],
        }
        sov_df = pd.DataFrame(SOVEREIGN_DATA)

        st.dataframe(sov_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            fig_sov = px.bar(sov_df, x='Country', y='10Y Yield',
                            title='10-Year Government Bond Yields',
                            color='10Y Yield',
                            color_continuous_scale='RdYlGn_r')
            fig_sov.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_sov, use_container_width=True)

        with col2:
            fig_spread = px.bar(sov_df, x='Country', y='Spread to UST',
                               title='Spread vs US Treasury (bp)',
                               color='Spread to UST',
                               color_continuous_scale='RdBu_r')
            fig_spread.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_spread, use_container_width=True)

        # EM Sovereign Focus
        st.markdown("---")
        st.subheader("Emerging Market Sovereigns")

        em_data = pd.DataFrame({
            'Country': ['🇧🇷 Brazil', '🇲🇽 Mexico', '🇿🇦 South Africa', '🇹🇷 Turkey',
                       '🇮🇩 Indonesia', '🇵🇱 Poland'],
            '10Y Yield': [12.85, 9.42, 10.25, 28.50, 6.85, 5.65],
            'Rating': ['BB', 'BBB', 'BB', 'B', 'BBB', 'A'],
            'CDS 5Y': [152, 98, 215, 385, 82, 48],
        })
        st.dataframe(em_data, use_container_width=True, hide_index=True)


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
            projection = st.selectbox("Projection", ["orthographic", "naturalEarth", "equirectangular"])
        with col2:
            rotation = st.slider("Rotation (Longitude)", -180, 180, 0)

        if not map_data.empty:
            fig = go.Figure()

            # Add weather points
            # Calculate marker sizes as a list (not Series) to avoid Plotly errors
            marker_sizes = [max(abs(t) / 3 + 8, 6) for t in map_data['temperature'].tolist()]

            fig.add_trace(go.Scattergeo(
                lon=map_data['lon'].tolist(),
                lat=map_data['lat'].tolist(),
                text=map_data.apply(lambda r: f"<b>{r['city']}</b><br>Temp: {r['temperature']:.1f}C<br>{r['description']}", axis=1).tolist(),
                mode='markers',
                marker=dict(
                    size=marker_sizes,
                    color=map_data['temperature'].tolist(),
                    colorscale='RdYlBu_r',
                    cmin=-10,
                    cmax=40,
                    colorbar=dict(title=dict(text="Temp (C)", font=dict(color='#333')), tickfont=dict(color='#333')),
                    line=dict(width=1, color='white')
                ),
                hoverinfo='text'
            ))

            # 3D Globe projection (light mode)
            fig.update_geos(
                projection_type=projection,
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
    st.markdown("*ISS Tracking, Near-Earth Objects, and Solar Activity*")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["ISS Tracker", "Near-Earth Objects", "Solar Activity"])

    with tab1:
        st.subheader("International Space Station")
        iss_df = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 100")

        if not iss_df.empty:
            latest = iss_df.iloc[0]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Latitude", f"{latest['latitude']:.4f}°")
            with col2:
                st.metric("Longitude", f"{latest['longitude']:.4f}°")
            with col3:
                st.metric("Altitude", f"{latest['altitude']:.0f} km")
            with col4:
                st.metric("Velocity", f"{latest['velocity']:,.0f} km/h")

            # ISS position on map
            st.markdown("---")
            st.subheader("Current Position")

            iss_df['latitude'] = pd.to_numeric(iss_df['latitude'], errors='coerce')
            iss_df['longitude'] = pd.to_numeric(iss_df['longitude'], errors='coerce')

            # Create globe visualization
            fig = go.Figure()
            fig.add_trace(go.Scattergeo(
                lon=iss_df['longitude'],
                lat=iss_df['latitude'],
                mode='lines+markers',
                marker=dict(size=8, color='red'),
                line=dict(width=2, color='blue'),
                name='ISS Track'
            ))
            # Current position
            fig.add_trace(go.Scattergeo(
                lon=[latest['longitude']],
                lat=[latest['latitude']],
                mode='markers',
                marker=dict(size=15, color='red', symbol='star'),
                name='Current Position'
            ))
            fig.update_layout(
                geo=dict(
                    projection_type='orthographic',
                    showland=True,
                    landcolor='rgb(243, 243, 243)',
                    countrycolor='rgb(204, 204, 204)',
                    showocean=True,
                    oceancolor='rgb(230, 245, 255)',
                    projection_rotation=dict(lon=latest['longitude'], lat=latest['latitude'])
                ),
                height=500,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Track history
            st.subheader("Recent Track History")
            track_df = iss_df[['timestamp', 'latitude', 'longitude', 'altitude', 'velocity']].head(20)
            track_df['timestamp'] = pd.to_datetime(track_df['timestamp']).dt.strftime('%H:%M:%S')
            st.dataframe(track_df, use_container_width=True, hide_index=True)
        else:
            st.info("No ISS data available. Run: `python scheduler.py --collector space`")

    with tab2:
        st.subheader("Near-Earth Objects")
        neo_df = load_data("""
            SELECT name, date, estimated_diameter_max, relative_velocity,
                   miss_distance, is_potentially_hazardous
            FROM near_earth_objects WHERE date >= CURRENT_DATE - 14
            ORDER BY date DESC
        """)

        if not neo_df.empty:
            neo_df['date'] = pd.to_datetime(neo_df['date'])
            neo_df['estimated_diameter_max'] = pd.to_numeric(neo_df['estimated_diameter_max'], errors='coerce')
            neo_df['relative_velocity'] = pd.to_numeric(neo_df['relative_velocity'], errors='coerce')
            neo_df['miss_distance'] = pd.to_numeric(neo_df['miss_distance'], errors='coerce')

            # Summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total NEOs", len(neo_df))
            with col2:
                hazardous = neo_df['is_potentially_hazardous'].sum()
                st.metric("Hazardous", hazardous, delta=f"{hazardous}" if hazardous > 0 else None, delta_color="inverse")
            with col3:
                avg_diameter = neo_df['estimated_diameter_max'].mean()
                st.metric("Avg Diameter", f"{avg_diameter:.0f}m")
            with col4:
                today_count = len(neo_df[neo_df['date'].dt.date == datetime.now().date()])
                st.metric("Today", today_count)

            st.markdown("---")

            # Hazardous NEOs alert
            hazardous_neos = neo_df[neo_df['is_potentially_hazardous'] == True]
            if not hazardous_neos.empty:
                st.warning(f"**{len(hazardous_neos)} Potentially Hazardous Objects** approaching in the next 2 weeks")
                for _, neo in hazardous_neos.iterrows():
                    miss_km = neo['miss_distance'] / 1000 if pd.notna(neo['miss_distance']) else 0
                    st.markdown(f"- **{neo['name']}** on {neo['date'].strftime('%Y-%m-%d')} - "
                               f"Miss distance: {miss_km:,.0f} km | Diameter: {neo['estimated_diameter_max']:.0f}m")

            st.markdown("---")

            # Size distribution chart
            st.subheader("NEO Size Distribution")
            fig = px.scatter(
                neo_df,
                x='date',
                y='estimated_diameter_max',
                size='estimated_diameter_max',
                color='is_potentially_hazardous',
                color_discrete_map={True: 'red', False: 'blue'},
                hover_name='name',
                labels={'estimated_diameter_max': 'Diameter (m)', 'is_potentially_hazardous': 'Hazardous'},
                title='NEO Approaches by Size'
            )
            fig.update_layout(**get_clean_plotly_layout(), height=400)
            st.plotly_chart(fig, use_container_width=True)

            # Full table
            st.subheader("All Near-Earth Objects")
            display_neo = neo_df.copy()
            display_neo['Hazardous'] = display_neo['is_potentially_hazardous'].apply(lambda x: '⚠️ YES' if x else 'No')
            display_neo['Diameter'] = display_neo['estimated_diameter_max'].apply(lambda x: f"{x:.0f}m" if pd.notna(x) else "N/A")
            display_neo['Velocity'] = display_neo['relative_velocity'].apply(lambda x: f"{x:,.0f} km/h" if pd.notna(x) else "N/A")
            display_neo['Miss Distance'] = display_neo['miss_distance'].apply(lambda x: f"{x/1000:,.0f} km" if pd.notna(x) else "N/A")
            display_neo['Date'] = display_neo['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_neo[['name', 'Date', 'Diameter', 'Velocity', 'Miss Distance', 'Hazardous']],
                        use_container_width=True, hide_index=True)
        else:
            st.info("No NEO data available. Run: `python scheduler.py --collector space`")

    with tab3:
        st.subheader("Solar Activity")
        solar_df = load_data("SELECT * FROM solar_flares ORDER BY peak_time DESC LIMIT 50")

        if not solar_df.empty:
            solar_df['peak_time'] = pd.to_datetime(solar_df['peak_time'])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Flares", len(solar_df))
            with col2:
                x_class = len(solar_df[solar_df['class_type'].str.startswith('X', na=False)])
                st.metric("X-Class Flares", x_class)
            with col3:
                m_class = len(solar_df[solar_df['class_type'].str.startswith('M', na=False)])
                st.metric("M-Class Flares", m_class)

            st.markdown("---")
            st.subheader("Recent Solar Flares")

            display_solar = solar_df[['class_type', 'peak_time', 'source_location', 'active_region_num']].copy()
            display_solar['peak_time'] = display_solar['peak_time'].dt.strftime('%Y-%m-%d %H:%M')
            display_solar.columns = ['Class', 'Peak Time', 'Source Location', 'Active Region']
            st.dataframe(display_solar, use_container_width=True, hide_index=True)
        else:
            st.info("No solar flare data available. Run: `python scheduler.py --collector space`")


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
    st.markdown("*AI-powered sentiment analysis and market impact*")
    st.markdown("---")

    news_df = load_data("""
        SELECT title, source, url, description, published_at
        FROM news ORDER BY published_at DESC LIMIT 100
    """)

    if news_df.empty:
        st.warning("No news data available.")
    else:
        # ========== SENTIMENT DASHBOARD ==========
        st.subheader("📊 Market Sentiment Dashboard")

        # Analyze all articles for sentiment
        sentiment_data = []
        for _, article in news_df.iterrows():
            sentiment, confidence, keywords = classify_event_sentiment(
                article.get('title', ''),
                article.get('description', '')
            )
            sentiment_data.append({
                'title': article['title'],
                'source': article['source'],
                'published_at': article['published_at'],
                'sentiment': sentiment,
                'confidence': confidence,
                'keywords': keywords
            })

        sentiment_df = pd.DataFrame(sentiment_data)

        # Calculate sentiment scores
        bullish_count = len(sentiment_df[sentiment_df['sentiment'] == 'bullish'])
        bearish_count = len(sentiment_df[sentiment_df['sentiment'] == 'bearish'])
        neutral_count = len(sentiment_df[sentiment_df['sentiment'] == 'neutral'])
        total = len(sentiment_df)

        # Sentiment Index: -100 (all bearish) to +100 (all bullish)
        if total > 0:
            sentiment_index = ((bullish_count - bearish_count) / total) * 100
        else:
            sentiment_index = 0

        # Display sentiment metrics
        sent_col1, sent_col2, sent_col3, sent_col4 = st.columns(4)

        with sent_col1:
            # Sentiment gauge
            if sentiment_index > 20:
                index_color = "#00a86b"
                index_label = "Bullish"
            elif sentiment_index < -20:
                index_color = "#f44336"
                index_label = "Bearish"
            else:
                index_color = "#ff9800"
                index_label = "Neutral"

            st.markdown(
                f"""<div style="text-align:center; padding:15px; background-color:#1e1e1e; border-radius:10px;">
                <div style="font-size:2.5em; color:{index_color}; font-weight:bold;">{sentiment_index:+.0f}</div>
                <div style="color:{index_color};">{index_label}</div>
                <small style="color:#888;">Sentiment Index</small>
                </div>""",
                unsafe_allow_html=True
            )

        with sent_col2:
            st.metric("🟢 Bullish", bullish_count, f"{bullish_count/total*100:.0f}%" if total > 0 else "0%")

        with sent_col3:
            st.metric("🔴 Bearish", bearish_count, f"{bearish_count/total*100:.0f}%" if total > 0 else "0%")

        with sent_col4:
            st.metric("⚪ Neutral", neutral_count, f"{neutral_count/total*100:.0f}%" if total > 0 else "0%")

        # Sentiment distribution pie chart
        pie_col1, pie_col2 = st.columns([1, 2])

        with pie_col1:
            fig_pie = px.pie(
                values=[bullish_count, bearish_count, neutral_count],
                names=['Bullish', 'Bearish', 'Neutral'],
                color_discrete_sequence=['#00a86b', '#f44336', '#888888'],
                hole=0.4
            )
            fig_pie.update_layout(
                showlegend=True,
                height=250,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with pie_col2:
            # Top keywords from news
            all_keywords = []
            for kws in sentiment_df['keywords']:
                if kws:
                    all_keywords.extend(kws)

            if all_keywords:
                from collections import Counter
                keyword_counts = Counter(all_keywords).most_common(10)

                st.markdown("**Trending Keywords**")
                kw_cols = st.columns(5)
                for i, (kw, count) in enumerate(keyword_counts[:10]):
                    with kw_cols[i % 5]:
                        # Color based on sentiment association
                        bullish_kws = ['growth', 'surge', 'rally', 'record', 'beat', 'profit', 'gain']
                        bearish_kws = ['fall', 'crash', 'crisis', 'loss', 'decline', 'fear', 'risk']
                        if kw.lower() in bullish_kws:
                            kw_color = "#00a86b"
                        elif kw.lower() in bearish_kws:
                            kw_color = "#f44336"
                        else:
                            kw_color = "#888"
                        st.markdown(f"<span style='background-color:{kw_color}; padding:3px 8px; border-radius:3px; color:white; font-size:0.9em;'>{kw} ({count})</span>", unsafe_allow_html=True)

        st.markdown("---")

        # ========== NEWS FILTERS ==========
        col1, col2 = st.columns([2, 1])
        with col1:
            sources = ['All'] + sorted(news_df['source'].dropna().unique().tolist())
            selected_source = st.selectbox("Filter by Source", sources)
        with col2:
            sentiment_filter = st.selectbox("Filter by Sentiment", ['All', 'Bullish', 'Bearish', 'Neutral'])

        # Apply filters
        filtered = news_df.copy()
        if selected_source != 'All':
            filtered = filtered[filtered['source'] == selected_source]

        # Merge sentiment data
        filtered = filtered.merge(
            sentiment_df[['title', 'sentiment', 'confidence', 'keywords']],
            on='title',
            how='left'
        )

        if sentiment_filter != 'All':
            filtered = filtered[filtered['sentiment'] == sentiment_filter.lower()]

        st.write(f"**Showing {len(filtered)} articles**")
        st.markdown("---")

        for _, article in filtered.iterrows():
            title = article['title'] or 'Untitled'

            # Use pre-calculated sentiment from merged data
            sentiment = article.get('sentiment', 'neutral')
            confidence = article.get('confidence', 0)
            keywords = article.get('keywords', [])

            badge = get_sentiment_badge(sentiment)
            st.markdown(f"### {title} {badge}", unsafe_allow_html=True)
            if keywords:
                st.caption(f"Keywords: {', '.join(keywords)} ({confidence:.0%} confidence)")

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

    # Date range selector
    col_range1, col_range2, col_range3 = st.columns([2, 2, 1])
    with col_range1:
        date_preset = st.selectbox(
            "Date Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time", "Custom"],
            index=2
        )

    # Calculate date range based on preset
    from datetime import datetime, timedelta
    now = datetime.now()
    if date_preset == "Last 24 Hours":
        start_date = now - timedelta(days=1)
    elif date_preset == "Last 7 Days":
        start_date = now - timedelta(days=7)
    elif date_preset == "Last 30 Days":
        start_date = now - timedelta(days=30)
    elif date_preset == "Last 90 Days":
        start_date = now - timedelta(days=90)
    elif date_preset == "All Time":
        start_date = now - timedelta(days=3650)  # ~10 years
    else:
        start_date = now - timedelta(days=30)

    with col_range2:
        if date_preset == "Custom":
            custom_start = st.date_input("Start Date", value=now - timedelta(days=30))
            start_date = datetime.combine(custom_start, datetime.min.time())

    with col_range3:
        normalize_prices = st.checkbox("Normalize %", help="Show percentage change from first value")

    st.markdown("---")

    # ========== CORRELATION MATRIX SECTION ==========
    with st.expander("📊 Asset Correlation Matrix", expanded=False):
        st.markdown("*Cross-asset correlations help identify diversification opportunities*")

        # Get latest prices for key assets
        corr_stocks = load_data(f"""
            SELECT 'SPY' as asset, timestamp, price FROM stocks
            WHERE symbol = 'SPY' AND timestamp >= '{start_date.strftime('%Y-%m-%d')}'
            UNION ALL
            SELECT 'QQQ' as asset, timestamp, price FROM stocks
            WHERE symbol = 'QQQ' AND timestamp >= '{start_date.strftime('%Y-%m-%d')}'
        """)

        corr_crypto = load_data(f"""
            SELECT symbol as asset, timestamp, price FROM crypto
            WHERE symbol IN ('BTC', 'ETH') AND timestamp >= '{start_date.strftime('%Y-%m-%d')}'
        """)

        corr_commodities = load_data(f"""
            SELECT symbol as asset, timestamp, price FROM commodities
            WHERE symbol IN ('GOLD', 'WTI') AND timestamp >= '{start_date.strftime('%Y-%m-%d')}'
        """)

        # Combine all data
        all_corr_data = pd.concat([corr_stocks, corr_crypto, corr_commodities], ignore_index=True)

        if not all_corr_data.empty:
            all_corr_data['timestamp'] = pd.to_datetime(all_corr_data['timestamp'])

            # Pivot to get assets as columns
            pivot_df = all_corr_data.pivot_table(
                index='timestamp',
                columns='asset',
                values='price',
                aggfunc='mean'
            )

            # Resample to daily to align timestamps
            pivot_df = pivot_df.resample('D').mean().dropna()

            if len(pivot_df) >= 5 and len(pivot_df.columns) >= 2:
                # Calculate returns
                returns_df = pivot_df.pct_change().dropna()

                # Calculate correlation matrix
                corr_matrix = returns_df.corr()

                # Display as heatmap
                import plotly.figure_factory as ff

                # Create annotation text
                z_text = [[f'{val:.2f}' for val in row] for row in corr_matrix.values]

                fig = ff.create_annotated_heatmap(
                    z=corr_matrix.values,
                    x=list(corr_matrix.columns),
                    y=list(corr_matrix.index),
                    annotation_text=z_text,
                    colorscale='RdBu',
                    showscale=True,
                    zmid=0
                )

                fig.update_layout(
                    title="Asset Return Correlations",
                    height=400,
                    xaxis_title="",
                    yaxis_title="",
                    yaxis=dict(autorange='reversed')
                )

                st.plotly_chart(fig, use_container_width=True)

                # Interpretation
                st.markdown("**Interpretation:**")
                col_int1, col_int2, col_int3 = st.columns(3)
                with col_int1:
                    st.markdown("🔵 **+1.0**: Perfect positive correlation")
                with col_int2:
                    st.markdown("⚪ **0.0**: No correlation")
                with col_int3:
                    st.markdown("🔴 **-1.0**: Perfect negative correlation")

                # Find notable correlations
                st.markdown("**Notable Pairs:**")
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        asset1, asset2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            rel = "strongly correlated" if corr_val > 0 else "inversely correlated"
                            st.caption(f"• {asset1} & {asset2}: {corr_val:.2f} ({rel})")
            else:
                st.info("Need more data points to calculate correlations. Try a longer date range.")
        else:
            st.info("No data available for correlation analysis. Run collectors first.")

    st.markdown("---")

    analysis_type = st.selectbox("Select Data Type", ["Stocks", "Crypto", "Commodities", "Forex", "Economic Indicators", "Weather"])

    if analysis_type == "Stocks":
        stocks_df = load_data("""
            SELECT symbol, price, change_percent, volume, timestamp
            FROM stocks ORDER BY timestamp DESC
        """)

        if stocks_df.empty:
            st.warning("No stock data for time series analysis.")
        else:
            stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp'])
            stocks_df = stocks_df[stocks_df['timestamp'] >= start_date]

            if stocks_df.empty:
                st.info(f"No data available for the selected date range.")
            else:
                symbols = sorted(stocks_df['symbol'].unique().tolist())

                # Multi-select for comparison
                selected_symbols = st.multiselect(
                    "Select Stocks to Compare",
                    symbols,
                    default=[symbols[0]] if symbols else []
                )

                if selected_symbols:
                    fig = go.Figure()
                    colors = ['#00d26a', '#ff4757', '#ffa502', '#3498db', '#9b59b6', '#e74c3c', '#2ecc71', '#1abc9c']

                    for i, symbol in enumerate(selected_symbols):
                        symbol_data = stocks_df[stocks_df['symbol'] == symbol].sort_values('timestamp')

                        if normalize_prices and len(symbol_data) > 0:
                            # Convert Decimal to float for arithmetic operations
                            first_price = float(symbol_data['price'].iloc[0])
                            y_values = ((symbol_data['price'].astype(float) - first_price) / first_price * 100)
                            y_label = "% Change"
                        else:
                            y_values = symbol_data['price'].astype(float)
                            y_label = "Price ($)"

                        fig.add_trace(go.Scatter(
                            x=symbol_data['timestamp'],
                            y=y_values,
                            mode='lines',
                            name=symbol,
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))

                    title = "Stock Price Comparison" if len(selected_symbols) > 1 else f"{selected_symbols[0]} Price History"
                    if normalize_prices:
                        title += " (Normalized)"

                    fig.update_layout(
                        title=title,
                        yaxis_title=y_label,
                        **get_clean_plotly_layout(),
                        height=450,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Statistics table
                    st.markdown("##### Statistics")
                    stats_data = []
                    for symbol in selected_symbols:
                        symbol_data = stocks_df[stocks_df['symbol'] == symbol].sort_values('timestamp')
                        if len(symbol_data) > 0:
                            current = symbol_data['price'].iloc[-1]
                            first = symbol_data['price'].iloc[0]
                            change_pct = ((current - first) / first * 100) if first != 0 else 0
                            stats_data.append({
                                'Symbol': symbol,
                                'Current': f"${current:.2f}",
                                'High': f"${symbol_data['price'].max():.2f}",
                                'Low': f"${symbol_data['price'].min():.2f}",
                                'Avg': f"${symbol_data['price'].mean():.2f}",
                                'Change': f"{change_pct:+.2f}%",
                                'Data Points': len(symbol_data)
                            })

                    if stats_data:
                        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

    elif analysis_type == "Crypto":
        crypto_df = load_data("""
            SELECT symbol, price, change_percent_24h, market_cap, volume_24h, timestamp
            FROM crypto ORDER BY timestamp DESC
        """)

        if crypto_df.empty:
            st.warning("No crypto data for time series analysis.")
        else:
            crypto_df['timestamp'] = pd.to_datetime(crypto_df['timestamp'])
            crypto_df = crypto_df[crypto_df['timestamp'] >= start_date]

            if crypto_df.empty:
                st.info(f"No data available for the selected date range.")
            else:
                symbols = sorted(crypto_df['symbol'].unique().tolist())

                selected_symbols = st.multiselect(
                    "Select Cryptocurrencies to Compare",
                    symbols,
                    default=[symbols[0]] if symbols else []
                )

                if selected_symbols:
                    fig = go.Figure()
                    colors = ['#f7931a', '#627eea', '#00d26a', '#ff4757', '#3498db', '#9b59b6']

                    for i, symbol in enumerate(selected_symbols):
                        symbol_data = crypto_df[crypto_df['symbol'] == symbol].sort_values('timestamp')

                        if normalize_prices and len(symbol_data) > 0:
                            # Convert Decimal to float for arithmetic operations
                            first_price = float(symbol_data['price'].iloc[0])
                            y_values = ((symbol_data['price'].astype(float) - first_price) / first_price * 100) if first_price != 0 else symbol_data['price'].astype(float)
                            y_label = "% Change"
                        else:
                            y_values = symbol_data['price'].astype(float)
                            y_label = "Price ($)"

                        fig.add_trace(go.Scatter(
                            x=symbol_data['timestamp'],
                            y=y_values,
                            mode='lines',
                            name=symbol,
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))

                    title = "Crypto Price Comparison" if len(selected_symbols) > 1 else f"{selected_symbols[0]} Price History"
                    if normalize_prices:
                        title += " (Normalized)"

                    fig.update_layout(
                        title=title,
                        yaxis_title=y_label,
                        **get_clean_plotly_layout(),
                        height=450,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Market cap comparison if multiple selected
                    if len(selected_symbols) > 1:
                        st.markdown("##### Market Cap Comparison")
                        latest_crypto = crypto_df.groupby('symbol').first().reset_index()
                        selected_latest = latest_crypto[latest_crypto['symbol'].isin(selected_symbols)]

                        fig_mc = px.bar(
                            selected_latest,
                            x='symbol',
                            y='market_cap',
                            color='symbol',
                            title="Market Cap Comparison"
                        )
                        fig_mc.update_layout(**get_clean_plotly_layout(), height=300, showlegend=False)
                        st.plotly_chart(fig_mc, use_container_width=True)

    elif analysis_type == "Commodities":
        commodities_df = load_data("""
            SELECT symbol, name, price, change_percent, category, timestamp
            FROM commodities ORDER BY timestamp DESC
        """)

        if commodities_df.empty:
            st.warning("No commodities data for time series analysis.")
        else:
            commodities_df['timestamp'] = pd.to_datetime(commodities_df['timestamp'])
            commodities_df = commodities_df[commodities_df['timestamp'] >= start_date]

            if commodities_df.empty:
                st.info(f"No data available for the selected date range.")
            else:
                # Group by category
                categories = commodities_df['category'].dropna().unique().tolist()
                selected_category = st.selectbox("Filter by Category", ["All"] + sorted(categories))

                if selected_category != "All":
                    filtered_df = commodities_df[commodities_df['category'] == selected_category]
                else:
                    filtered_df = commodities_df

                symbols = sorted(filtered_df['symbol'].unique().tolist())
                selected_symbols = st.multiselect(
                    "Select Commodities to Compare",
                    symbols,
                    default=[symbols[0]] if symbols else []
                )

                if selected_symbols:
                    fig = go.Figure()
                    colors = ['#ffd700', '#c0c0c0', '#b87333', '#00d26a', '#ff4757', '#3498db']

                    for i, symbol in enumerate(selected_symbols):
                        symbol_data = filtered_df[filtered_df['symbol'] == symbol].sort_values('timestamp')

                        if normalize_prices and len(symbol_data) > 0:
                            first_price = symbol_data['price'].iloc[0]
                            y_values = ((symbol_data['price'] - first_price) / first_price * 100) if first_price != 0 else symbol_data['price']
                            y_label = "% Change"
                        else:
                            y_values = symbol_data['price']
                            y_label = "Price ($)"

                        name = symbol_data['name'].iloc[0] if 'name' in symbol_data.columns and len(symbol_data) > 0 else symbol
                        fig.add_trace(go.Scatter(
                            x=symbol_data['timestamp'],
                            y=y_values,
                            mode='lines',
                            name=name,
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))

                    fig.update_layout(
                        title="Commodities Price History",
                        yaxis_title=y_label,
                        **get_clean_plotly_layout(),
                        height=450,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Forex":
        forex_df = load_data("""
            SELECT symbol, rate, change_percent, timestamp
            FROM forex ORDER BY timestamp DESC
        """)

        if forex_df.empty:
            st.warning("No forex data for time series analysis.")
        else:
            forex_df['timestamp'] = pd.to_datetime(forex_df['timestamp'])
            forex_df = forex_df[forex_df['timestamp'] >= start_date]

            if forex_df.empty:
                st.info(f"No data available for the selected date range.")
            else:
                symbols = sorted(forex_df['symbol'].unique().tolist())
                selected_symbols = st.multiselect(
                    "Select Currency Pairs to Compare",
                    symbols,
                    default=[symbols[0]] if symbols else []
                )

                if selected_symbols:
                    fig = go.Figure()
                    colors = ['#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4']

                    for i, symbol in enumerate(selected_symbols):
                        symbol_data = forex_df[forex_df['symbol'] == symbol].sort_values('timestamp')

                        if normalize_prices and len(symbol_data) > 0:
                            # Convert Decimal to float for arithmetic operations
                            first_rate = float(symbol_data['rate'].iloc[0])
                            y_values = ((symbol_data['rate'].astype(float) - first_rate) / first_rate * 100) if first_rate != 0 else symbol_data['rate'].astype(float)
                            y_label = "% Change"
                        else:
                            y_values = symbol_data['rate'].astype(float)
                            y_label = "Exchange Rate"

                        fig.add_trace(go.Scatter(
                            x=symbol_data['timestamp'],
                            y=y_values,
                            mode='lines',
                            name=symbol,
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))

                    fig.update_layout(
                        title="Forex Rate History",
                        yaxis_title=y_label,
                        **get_clean_plotly_layout(),
                        height=450,
                        hovermode='x unified'
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
            econ_df = econ_df[econ_df['timestamp'] >= start_date]

            if econ_df.empty:
                st.info(f"No data available for the selected date range.")
            else:
                indicators = sorted(econ_df['name'].dropna().unique().tolist())
                selected_indicator = st.selectbox("Select Indicator", indicators)

                if selected_indicator:
                    indicator_data = econ_df[econ_df['name'] == selected_indicator]
                    countries = sorted(indicator_data['country'].unique().tolist())

                    selected_countries = st.multiselect(
                        "Select Countries to Compare",
                        countries,
                        default=countries[:3] if len(countries) >= 3 else countries
                    )

                    if selected_countries:
                        fig = go.Figure()
                        colors = ['#00d26a', '#ff4757', '#ffa502', '#3498db', '#9b59b6', '#e74c3c', '#2ecc71']

                        for i, country in enumerate(selected_countries):
                            country_data = indicator_data[indicator_data['country'] == country].sort_values('timestamp')
                            fig.add_trace(go.Scatter(
                                x=country_data['timestamp'],
                                y=country_data['value'].astype(float),
                                mode='lines+markers',
                                name=country,
                                line=dict(color=colors[i % len(colors)], width=2)
                            ))

                        fig.update_layout(
                            title=f"{selected_indicator} - Cross Country Comparison",
                            **get_clean_plotly_layout(),
                            height=450,
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Weather":
        weather_df = load_data("""
            SELECT city, temperature, humidity, wind_speed, timestamp
            FROM weather ORDER BY timestamp DESC
        """)

        if weather_df.empty:
            st.warning("No weather data for time series analysis.")
        else:
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            weather_df = weather_df[weather_df['timestamp'] >= start_date]
            weather_df['temperature'] = pd.to_numeric(weather_df['temperature'], errors='coerce')
            weather_df['humidity'] = pd.to_numeric(weather_df['humidity'], errors='coerce')

            if weather_df.empty:
                st.info(f"No data available for the selected date range.")
            else:
                cities = sorted(weather_df['city'].unique().tolist())
                selected_cities = st.multiselect("Select Cities", cities, default=cities[:3] if len(cities) >= 3 else cities)

                metric = st.radio("Metric", ["Temperature", "Humidity"], horizontal=True)

                if selected_cities:
                    fig = go.Figure()
                    colors = ['#00d26a', '#ff4757', '#ffa502', '#3498db', '#9b59b6', '#e74c3c', '#2ecc71']

                    y_col = 'temperature' if metric == "Temperature" else 'humidity'
                    y_unit = "°C" if metric == "Temperature" else "%"

                    for i, city in enumerate(selected_cities):
                        city_data = weather_df[weather_df['city'] == city].sort_values('timestamp')
                        fig.add_trace(go.Scatter(
                            x=city_data['timestamp'],
                            y=city_data[y_col],
                            mode='lines+markers',
                            name=city,
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))

                    fig.update_layout(
                        title=f"{metric} Trends",
                        yaxis_title=f"{metric} ({y_unit})",
                        **get_clean_plotly_layout(),
                        height=450,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: PORTFOLIO
# ============================================================================

elif page == "Portfolio":
    st.title("Portfolio & Watchlist")
    st.markdown("*Track holdings, monitor watchlist, analyze correlations*")
    st.markdown("---")

    port_tab1, port_tab2, port_tab3 = st.tabs(["💼 Holdings Tracker", "👁️ Watchlist", "📊 Correlation Analysis"])

    # ========== TAB 1: HOLDINGS TRACKER ==========
    with port_tab1:
        st.subheader("Portfolio Holdings")
        st.markdown("*Enter your positions to track performance*")

        # Initialize session state for portfolio
        if 'portfolio_holdings' not in st.session_state:
            st.session_state.portfolio_holdings = []

        # Add new holding
        with st.expander("➕ Add New Holding", expanded=len(st.session_state.portfolio_holdings) == 0):
            add_col1, add_col2, add_col3, add_col4 = st.columns(4)

            # Get available symbols
            all_stocks = load_data("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
            all_crypto = load_data("SELECT DISTINCT symbol FROM crypto ORDER BY symbol")

            stock_symbols = all_stocks['symbol'].tolist() if not all_stocks.empty else []
            crypto_symbols = all_crypto['symbol'].tolist() if not all_crypto.empty else []
            all_symbols = stock_symbols + crypto_symbols

            with add_col1:
                new_symbol = st.selectbox("Symbol", all_symbols, key="new_holding_symbol")
            with add_col2:
                new_shares = st.number_input("Shares/Units", min_value=0.0001, value=1.0, step=0.1, key="new_holding_shares")
            with add_col3:
                new_cost = st.number_input("Avg Cost ($)", min_value=0.01, value=100.0, step=1.0, key="new_holding_cost")
            with add_col4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Add to Portfolio", key="add_holding_btn"):
                    st.session_state.portfolio_holdings.append({
                        'symbol': new_symbol,
                        'shares': new_shares,
                        'cost_basis': new_cost
                    })
                    st.rerun()

        # Display current holdings with live prices
        if st.session_state.portfolio_holdings:
            total_value = 0
            total_cost = 0
            total_pnl = 0

            st.markdown("### Current Holdings")

            # Headers
            h_cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5])
            h_cols[0].markdown("**Symbol**")
            h_cols[1].markdown("**Shares**")
            h_cols[2].markdown("**Avg Cost**")
            h_cols[3].markdown("**Current**")
            h_cols[4].markdown("**Value**")
            h_cols[5].markdown("**P&L**")
            h_cols[6].markdown("**Del**")

            holdings_to_remove = []

            for i, holding in enumerate(st.session_state.portfolio_holdings):
                symbol = holding['symbol']
                shares = holding['shares']
                cost_basis = holding['cost_basis']

                # Get current price
                price_df = load_realtime_data(f"""
                    SELECT price FROM stocks WHERE symbol = '{symbol}'
                    UNION ALL
                    SELECT price FROM crypto WHERE symbol = '{symbol}'
                    ORDER BY 1 DESC LIMIT 1
                """)

                current_price = price_df['price'].iloc[0] if not price_df.empty else cost_basis
                current_price = float(current_price)

                position_value = shares * current_price
                position_cost = shares * cost_basis
                position_pnl = position_value - position_cost
                pnl_pct = ((current_price - cost_basis) / cost_basis) * 100 if cost_basis > 0 else 0

                total_value += position_value
                total_cost += position_cost
                total_pnl += position_pnl

                # Display row
                row_cols = st.columns([1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.5])
                row_cols[0].markdown(f"**{symbol}**")
                row_cols[1].markdown(f"{shares:,.4f}")
                row_cols[2].markdown(f"${cost_basis:,.2f}")
                row_cols[3].markdown(f"${current_price:,.2f}")
                row_cols[4].markdown(f"${position_value:,.2f}")

                pnl_color = "#00a86b" if position_pnl >= 0 else "#f44336"
                row_cols[5].markdown(f"<span style='color:{pnl_color}'>${position_pnl:+,.2f} ({pnl_pct:+.1f}%)</span>", unsafe_allow_html=True)

                if row_cols[6].button("🗑️", key=f"del_{i}"):
                    holdings_to_remove.append(i)

            # Remove holdings marked for deletion
            for idx in sorted(holdings_to_remove, reverse=True):
                st.session_state.portfolio_holdings.pop(idx)
            if holdings_to_remove:
                st.rerun()

            # Portfolio totals
            st.markdown("---")
            tot_cols = st.columns(4)
            tot_cols[0].metric("Total Value", f"${total_value:,.2f}")
            tot_cols[1].metric("Total Cost", f"${total_cost:,.2f}")
            pnl_pct_total = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
            tot_cols[2].metric("Total P&L", f"${total_pnl:+,.2f}", f"{pnl_pct_total:+.1f}%")
            tot_cols[3].metric("Positions", len(st.session_state.portfolio_holdings))

        else:
            st.info("No holdings yet. Add positions above to track your portfolio.")

    # ========== TAB 2: WATCHLIST ==========
    with port_tab2:
        st.subheader("Watchlist")
        st.markdown("*Monitor symbols without owning them*")

        # Initialize watchlist
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'BTC', 'ETH']

        # Add to watchlist
        watch_col1, watch_col2 = st.columns([3, 1])
        with watch_col1:
            all_stocks = load_data("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
            all_crypto = load_data("SELECT DISTINCT symbol FROM crypto ORDER BY symbol")
            stock_symbols = all_stocks['symbol'].tolist() if not all_stocks.empty else []
            crypto_symbols = all_crypto['symbol'].tolist() if not all_crypto.empty else []
            available_symbols = [s for s in stock_symbols + crypto_symbols if s not in st.session_state.watchlist]
            new_watch = st.selectbox("Add to Watchlist", available_symbols, key="watchlist_add")
        with watch_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add", key="add_watch_btn"):
                if new_watch and new_watch not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_watch)
                    st.rerun()

        st.markdown("---")

        # Display watchlist with prices
        if st.session_state.watchlist:
            watch_to_remove = []

            for symbol in st.session_state.watchlist:
                # Get price and change
                price_df = load_realtime_data(f"""
                    SELECT symbol, price, change_percent FROM stocks WHERE symbol = '{symbol}'
                    UNION ALL
                    SELECT symbol, price, change_percent_24h as change_percent FROM crypto WHERE symbol = '{symbol}'
                    ORDER BY price DESC LIMIT 1
                """)

                if not price_df.empty:
                    price = float(price_df['price'].iloc[0])
                    change = float(price_df['change_percent'].iloc[0] or 0)
                    change_color = "#00a86b" if change >= 0 else "#f44336"

                    w_cols = st.columns([2, 2, 2, 1])
                    w_cols[0].markdown(f"**{symbol}**")
                    w_cols[1].markdown(f"${price:,.2f}")
                    w_cols[2].markdown(f"<span style='color:{change_color}'>{change:+.2f}%</span>", unsafe_allow_html=True)
                    if w_cols[3].button("❌", key=f"remove_watch_{symbol}"):
                        watch_to_remove.append(symbol)
                else:
                    w_cols = st.columns([2, 2, 2, 1])
                    w_cols[0].markdown(f"**{symbol}**")
                    w_cols[1].markdown("N/A")
                    w_cols[2].markdown("-")
                    if w_cols[3].button("❌", key=f"remove_watch_{symbol}"):
                        watch_to_remove.append(symbol)

            for sym in watch_to_remove:
                st.session_state.watchlist.remove(sym)
            if watch_to_remove:
                st.rerun()
        else:
            st.info("Watchlist is empty. Add symbols above.")

    # ========== TAB 3: CORRELATION ANALYSIS ==========
    with port_tab3:
        st.subheader("Portfolio Correlation Analysis")
        st.markdown("*Select assets to analyze correlations*")

        col1, col2, col3 = st.columns(3)

        # Get available assets
        stocks_list = load_data("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
        crypto_list = load_data("SELECT DISTINCT symbol FROM crypto ORDER BY symbol")
        commodities_list = load_data("SELECT DISTINCT symbol FROM commodities ORDER BY symbol")

        with col1:
            st.markdown("##### Stocks")
            stock_symbols = stocks_list['symbol'].tolist() if not stocks_list.empty else []
            stock_defaults = [s for s in ['AAPL', 'MSFT'] if s in stock_symbols]
            selected_stocks = st.multiselect(
                "Select stocks",
                stock_symbols,
                default=stock_defaults if stock_defaults else stock_symbols[:2] if len(stock_symbols) >= 2 else stock_symbols,
                key="corr_stocks"
            )

        with col2:
            st.markdown("##### Crypto")
            crypto_symbols = crypto_list['symbol'].tolist() if not crypto_list.empty else []
            crypto_defaults = [s for s in ['BTC', 'ETH'] if s in crypto_symbols]
            selected_crypto = st.multiselect(
                "Select crypto",
                crypto_symbols,
                default=crypto_defaults if crypto_defaults else crypto_symbols[:2] if len(crypto_symbols) >= 2 else crypto_symbols,
                key="corr_crypto"
            )

        with col3:
            st.markdown("##### Commodities")
            selected_commodities = st.multiselect(
                "Select commodities",
                commodities_list['symbol'].tolist() if not commodities_list.empty else [],
                default=[],
                key="corr_commodities"
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

                    stat_col1, stat_col2, stat_col3 = st.columns(3)

                    with stat_col1:
                        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
                        st.metric("Average Correlation", f"{avg_corr:.2f}")
                        if avg_corr > 0.7:
                            st.warning("High correlation - limited diversification")
                        elif avg_corr < 0.3:
                            st.success("Low correlation - good diversification")

                    with stat_col2:
                        # Find highest correlation pair
                        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
                        max_corr_idx = np.unravel_index(np.argmax(corr_matrix.where(mask).values), corr_matrix.shape)
                        max_corr = corr_matrix.iloc[max_corr_idx]
                        pair_names = f"{corr_matrix.index[max_corr_idx[0]]} & {corr_matrix.columns[max_corr_idx[1]]}"
                        st.metric("Highest Correlation", f"{max_corr:.2f}")
                        st.caption(pair_names)

                    with stat_col3:
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

    # Check if World Bank exists
    if table_exists('worldbank_indicators'):
        available_tables['worldbank_indicators'] = ['indicator_code', 'indicator_name', 'category', 'country_code', 'country_name', 'year', 'value', 'timestamp']

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
    st.markdown("*Monitor market movements and export data*")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["Live Alerts", "Custom Alerts", "Alert History", "Export Data"])

    with tab1:
        st.subheader("Live Market Alerts")
        st.markdown("*Automatic alerts based on significant price movements*")

        col_alert1, col_alert2 = st.columns(2)

        with col_alert1:
            # Stock alerts - optimized query
            st.markdown("#### Stocks")
            latest_stocks = load_data("""
                SELECT DISTINCT ON (symbol) symbol, price, change_percent
                FROM stocks ORDER BY symbol, timestamp DESC
            """)
            if not latest_stocks.empty:
                latest_stocks['change_percent'] = pd.to_numeric(latest_stocks['change_percent'], errors='coerce').fillna(0)
                big_movers = latest_stocks[abs(latest_stocks['change_percent']) > 5]
                if not big_movers.empty:
                    for _, row in big_movers.iterrows():
                        change = row.get('change_percent', 0)
                        color = "success-box" if change > 0 else "alert-box"
                        direction = "up" if change > 0 else "down"
                        st.markdown(f"""<div class='{color}'>
                            <strong>{row['symbol']}</strong> {direction} {format_change(abs(change))} (${row['price']:.2f})
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No significant stock movements (>5%)")
            else:
                st.info("No stock data available")

            # Commodities alerts - optimized query
            st.markdown("#### Commodities")
            latest_comm = load_data("""
                SELECT DISTINCT ON (symbol) symbol, name, price, change_percent
                FROM commodities ORDER BY symbol, timestamp DESC
            """)
            if not latest_comm.empty:
                latest_comm['change_percent'] = pd.to_numeric(latest_comm['change_percent'], errors='coerce').fillna(0)
                big_comm = latest_comm[abs(latest_comm['change_percent']) > 3]
                if not big_comm.empty:
                    for _, row in big_comm.iterrows():
                        change = row.get('change_percent', 0)
                        color = "success-box" if change > 0 else "alert-box"
                        name = row.get('name', row['symbol'])
                        st.markdown(f"""<div class='{color}'>
                            <strong>{name}</strong>: {format_change(change)} (${row['price']:.2f})
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No significant commodity movements (>3%)")

        with col_alert2:
            # Crypto alerts - optimized query
            st.markdown("#### Crypto")
            latest_crypto = load_data("""
                SELECT DISTINCT ON (symbol) symbol, price, change_percent_24h
                FROM crypto ORDER BY symbol, timestamp DESC
            """)
            if not latest_crypto.empty:
                latest_crypto['change_percent_24h'] = pd.to_numeric(latest_crypto['change_percent_24h'], errors='coerce').fillna(0)
                big_crypto = latest_crypto[abs(latest_crypto['change_percent_24h']) > 10]
                if not big_crypto.empty:
                    for _, row in big_crypto.iterrows():
                        change = row.get('change_percent_24h', 0)
                        color = "success-box" if change > 0 else "alert-box"
                        st.markdown(f"""<div class='{color}'>
                            <strong>{row['symbol']}</strong>: {format_change(change)} (${row['price']:,.2f})
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No significant crypto movements (>10%)")

            # NEO alerts
            st.markdown("#### Space - Hazardous NEOs")
            neo_df = load_data("""
                SELECT * FROM near_earth_objects
                WHERE is_potentially_hazardous = true AND date >= CURRENT_DATE
            """)
            if not neo_df.empty:
                for _, row in neo_df.iterrows():
                    st.markdown(f"""<div class='alert-box'>
                        <strong>{row['name']}</strong> - Approach: {row['date']}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No hazardous NEO approaches today")

        # GDELT unrest alerts - full width
        if table_exists('gdelt_events'):
            st.markdown("---")
            st.markdown("#### Global Unrest Alerts")
            unrest_df = load_data("""
                SELECT * FROM gdelt_events
                WHERE event_type IN ('PROTEST', 'RIOT', 'STRIKE') AND tone < -5
                ORDER BY timestamp DESC LIMIT 5
            """)
            if not unrest_df.empty:
                for _, row in unrest_df.iterrows():
                    title_text = row['title'][:100] + "..." if len(row['title']) > 100 else row['title']
                    st.markdown(f"""<div class='warning-box'>
                        <strong>{row['country']}</strong>: {title_text}
                        <br>Tone: {row['tone']:.2f} | Type: {row['event_type']}
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No significant social unrest events detected")

    with tab2:
        st.subheader("Create Custom Alert")
        st.markdown("*Set price thresholds for specific assets*")

        col_create1, col_create2 = st.columns(2)

        with col_create1:
            alert_asset_type = st.selectbox("Asset Type", ["Stock", "Crypto", "Commodity", "Forex"])

            # Get available symbols based on asset type
            if alert_asset_type == "Stock":
                symbols_df = load_data("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
            elif alert_asset_type == "Crypto":
                symbols_df = load_data("SELECT DISTINCT symbol FROM crypto ORDER BY symbol")
            elif alert_asset_type == "Commodity":
                symbols_df = load_data("SELECT DISTINCT symbol, name FROM commodities ORDER BY symbol")
            else:
                symbols_df = load_data("SELECT DISTINCT symbol FROM forex ORDER BY symbol")

            if not symbols_df.empty:
                alert_symbol = st.selectbox("Symbol", symbols_df['symbol'].tolist())
            else:
                alert_symbol = st.text_input("Symbol")

        with col_create2:
            alert_condition = st.selectbox("Condition", ["Price Above", "Price Below", "Change Above %", "Change Below %"])
            alert_value = st.number_input("Value", value=0.0, step=0.01)
            alert_name = st.text_input("Alert Name (optional)", placeholder="My Alert")

        if st.button("Create Alert", type="primary"):
            if alert_symbol and alert_value != 0:
                # Check if user_alerts table exists
                if table_exists('user_alerts'):
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO user_alerts (asset_type, symbol, condition_type, threshold_value, name, is_active, created_at)
                            VALUES (%s, %s, %s, %s, %s, true, NOW())
                        """, (alert_asset_type.lower(), alert_symbol, alert_condition.lower().replace(" ", "_"), alert_value, alert_name or f"{alert_symbol} Alert"))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Alert created: {alert_symbol} {alert_condition} {alert_value}")
                    except Exception as e:
                        st.error(f"Error creating alert: {e}")
                else:
                    st.warning("Alert storage not available. Run database initialization to enable custom alerts.")
            else:
                st.warning("Please fill in all required fields")

        # Show existing custom alerts
        st.markdown("---")
        st.subheader("Your Custom Alerts")

        if table_exists('user_alerts'):
            user_alerts_df = load_data("SELECT * FROM user_alerts WHERE is_active = true ORDER BY created_at DESC")

            if not user_alerts_df.empty:
                for idx, row in user_alerts_df.iterrows():
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        condition_display = row['condition_type'].replace("_", " ").title()
                        st.markdown(f"""
                        **{row['name']}** - {row['asset_type'].upper()}: {row['symbol']}
                        {condition_display} {row['threshold_value']}
                        """)
                    with col_b:
                        if st.button("Delete", key=f"del_alert_{row['id']}"):
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("UPDATE user_alerts SET is_active = false WHERE id = %s", (row['id'],))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            else:
                st.info("No custom alerts created yet")
        else:
            st.info("Custom alerts feature requires database setup. Run `python initialize_database.py` to enable.")

    with tab3:
        st.subheader("Alert History")
        st.markdown("*Past triggered alerts and notifications*")

        if table_exists('alert_history'):
            history_df = load_data("""
                SELECT * FROM alert_history
                ORDER BY triggered_at DESC
                LIMIT 50
            """)

            if not history_df.empty:
                # Summary metrics
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    st.metric("Total Alerts (24h)",
                             len(history_df[history_df['triggered_at'] > (pd.Timestamp.now() - pd.Timedelta(days=1))]))
                with col_h2:
                    st.metric("Stock Alerts", len(history_df[history_df['asset_type'] == 'stock']))
                with col_h3:
                    st.metric("Crypto Alerts", len(history_df[history_df['asset_type'] == 'crypto']))

                st.markdown("---")

                # History table
                display_df = history_df[['triggered_at', 'asset_type', 'symbol', 'alert_type', 'message']].copy()
                display_df.columns = ['Time', 'Type', 'Symbol', 'Alert', 'Message']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No alert history yet. Alerts will appear here when triggered.")
        else:
            st.info("Alert history requires database setup. Run `python initialize_database.py` to enable.")

    with tab4:
        st.subheader("Export Data")

        export_tab1, export_tab2, export_tab3 = st.tabs(["Quick Export", "Custom Query", "Report Generator"])

        with export_tab1:
            st.markdown("**Quick Export** - Download pre-configured datasets")

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

            # Add World Bank if exists
            if table_exists('worldbank_indicators'):
                export_options["World Bank Indicators"] = "SELECT * FROM worldbank_indicators ORDER BY timestamp DESC LIMIT 1000"

            col_exp1, col_exp2, col_exp3 = st.columns([2, 1, 1])
            with col_exp1:
                selected_export = st.selectbox("Select data to export", list(export_options.keys()))
            with col_exp2:
                export_format = st.selectbox("Format", ["CSV", "JSON", "Excel"])
            with col_exp3:
                record_limit = st.selectbox("Max Records", [100, 500, 1000, 5000, 10000], index=2)

            # Modify query with selected limit
            base_query = export_options[selected_export]
            modified_query = base_query.replace("LIMIT 1000", f"LIMIT {record_limit}").replace("LIMIT 500", f"LIMIT {record_limit}")

            if st.button("Generate Export", type="primary"):
                with st.spinner("Loading data..."):
                    export_df = load_data(modified_query)
                    if not export_df.empty:
                        st.success(f"Loaded {len(export_df)} records")

                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename_base = f"{selected_export.lower().replace(' ', '_')}_{timestamp}"

                        if export_format == "CSV":
                            csv_data = export_df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"{filename_base}.csv",
                                mime="text/csv"
                            )
                        elif export_format == "JSON":
                            json_data = export_df.to_json(orient='records', date_format='iso', indent=2)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"{filename_base}.json",
                                mime="application/json"
                            )
                        else:  # Excel
                            # Convert to Excel bytes
                            from io import BytesIO
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                export_df.to_excel(writer, sheet_name='Data', index=False)
                            excel_data = output.getvalue()
                            st.download_button(
                                label="Download Excel",
                                data=excel_data,
                                file_name=f"{filename_base}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                        st.markdown("**Preview (first 10 rows):**")
                        st.dataframe(export_df.head(10), use_container_width=True, hide_index=True)
                    else:
                        st.warning("No data available for export")

        with export_tab2:
            st.markdown("**Custom SQL Query** - Write your own queries")
            st.warning("Read-only access. Be careful with large result sets.")

            default_query = """SELECT symbol, price, change_percent, timestamp
FROM stocks
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY change_percent DESC
LIMIT 20"""

            custom_query = st.text_area("SQL Query", value=default_query, height=150)

            if st.button("Execute Query"):
                if custom_query.strip().lower().startswith('select'):
                    with st.spinner("Executing query..."):
                        try:
                            result_df = load_data(custom_query)
                            if not result_df.empty:
                                st.success(f"Query returned {len(result_df)} rows")
                                st.dataframe(result_df, use_container_width=True, hide_index=True)

                                # Export options for custom query
                                col1, col2 = st.columns(2)
                                with col1:
                                    csv_data = result_df.to_csv(index=False)
                                    st.download_button(
                                        label="Download as CSV",
                                        data=csv_data,
                                        file_name="custom_query_result.csv",
                                        mime="text/csv"
                                    )
                                with col2:
                                    json_data = result_df.to_json(orient='records', date_format='iso')
                                    st.download_button(
                                        label="Download as JSON",
                                        data=json_data,
                                        file_name="custom_query_result.json",
                                        mime="application/json"
                                    )
                            else:
                                st.info("Query returned no results")
                        except Exception as e:
                            st.error(f"Query error: {str(e)}")
                else:
                    st.error("Only SELECT queries are allowed")

        with export_tab3:
            st.markdown("**Report Generator** - Create combined reports")

            report_type = st.selectbox("Report Type", [
                "Daily Market Summary",
                "Portfolio Performance",
                "Economic Dashboard",
                "Risk Analysis Report"
            ])

            report_date = st.date_input("Report Date", datetime.now())

            if st.button("Generate Report", type="primary"):
                with st.spinner("Generating report..."):
                    report_data = {}

                    if report_type == "Daily Market Summary":
                        # Gather data for market summary
                        stocks = load_data("SELECT DISTINCT ON (symbol) symbol, price, change_percent FROM stocks ORDER BY symbol, timestamp DESC")
                        crypto = load_data("SELECT DISTINCT ON (symbol) symbol, price, change_percent_24h FROM crypto ORDER BY symbol, timestamp DESC")
                        forex = load_data("SELECT DISTINCT ON (base_currency) base_currency, quote_currency, rate, change_percent FROM forex ORDER BY base_currency, timestamp DESC")

                        report_md = f"""# Daily Market Summary
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Report Date:** {report_date}

## Stock Market
- Total stocks tracked: {len(stocks)}
- Average change: {stocks['change_percent'].mean():.2f}% (if available)

## Cryptocurrency Market
- Total coins tracked: {len(crypto)}

## Forex Market
- Currency pairs: {len(forex)}

---
*Report generated by Hermes Intelligence Platform*
"""
                        st.markdown(report_md)
                        st.download_button(
                            label="Download Report (Markdown)",
                            data=report_md,
                            file_name=f"market_summary_{report_date}.md",
                            mime="text/markdown"
                        )

                    elif report_type == "Economic Dashboard":
                        econ = load_data("SELECT DISTINCT ON (indicator, country) indicator, country, name, value, unit FROM economic_indicators ORDER BY indicator, country, timestamp DESC")

                        if not econ.empty:
                            report_md = f"""# Economic Dashboard Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Key Indicators by Country

"""
                            for country in econ['country'].unique():
                                country_data = econ[econ['country'] == country]
                                report_md += f"\n### {country}\n"
                                for _, row in country_data.iterrows():
                                    report_md += f"- **{row['name']}**: {row['value']} {row['unit']}\n"

                            st.markdown(report_md)
                            st.download_button(
                                label="Download Report (Markdown)",
                                data=report_md,
                                file_name=f"economic_report_{report_date}.md",
                                mime="text/markdown"
                            )
                        else:
                            st.warning("No economic data available for report")

                    else:
                        st.info(f"Report type '{report_type}' coming soon!")


# ============================================================================
# PAGE: TECHNICAL ANALYSIS
# ============================================================================

elif page == "Technical Analysis":
    st.title("Technical Analysis")
    st.markdown("*RSI, MACD, Moving Averages, Bollinger Bands*")
    st.markdown("---")

    # Asset type selector
    asset_type = st.selectbox("Select Asset Type", ["Stocks", "Crypto"])

    if asset_type == "Stocks":
        symbols_df = load_data("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
        price_table = "stocks"
        price_col = "price"
    else:
        symbols_df = load_data("SELECT DISTINCT symbol FROM crypto ORDER BY symbol")
        price_table = "crypto"
        price_col = "price"

    if symbols_df.empty:
        st.warning(f"No {asset_type.lower()} data available. Run the collector first.")
    else:
        symbols = symbols_df['symbol'].tolist()
        selected_symbol = st.selectbox("Select Symbol", symbols)

        if selected_symbol:
            # Load price history
            price_df = load_data(f"""
                SELECT {price_col} as close, timestamp
                FROM {price_table}
                WHERE symbol = '{selected_symbol}'
                ORDER BY timestamp ASC
            """)

            if len(price_df) < 20:
                st.warning(f"Need at least 20 data points for technical analysis. Currently have {len(price_df)}.")
            else:
                price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
                price_df = price_df.set_index('timestamp')

                # Calculate indicators manually (inline to avoid import issues)
                close = price_df['close']

                # SMA
                sma_20 = close.rolling(window=20).mean()
                sma_50 = close.rolling(window=50).mean()

                # EMA
                ema_12 = close.ewm(span=12, adjust=False).mean()
                ema_26 = close.ewm(span=26, adjust=False).mean()

                # RSI
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))

                # MACD
                macd_line = ema_12 - ema_26
                signal_line = macd_line.ewm(span=9, adjust=False).mean()
                histogram = macd_line - signal_line

                # Bollinger Bands
                bb_middle = sma_20
                bb_std = close.rolling(window=20).std()
                bb_upper = bb_middle + (bb_std * 2)
                bb_lower = bb_middle - (bb_std * 2)

                # Stochastic Oscillator (14,3,3)
                low_14 = close.rolling(window=14).min()
                high_14 = close.rolling(window=14).max()
                stoch_k = 100 * (close - low_14) / (high_14 - low_14)
                stoch_d = stoch_k.rolling(window=3).mean()

                # ATR (Average True Range) - simplified using close only
                tr = close.diff().abs()
                atr = tr.rolling(window=14).mean()

                # Williams %R
                williams_r = -100 * (high_14 - close) / (high_14 - low_14)

                # Latest values
                latest_price = close.iloc[-1]
                latest_rsi = rsi.iloc[-1]
                latest_macd = macd_line.iloc[-1]
                latest_signal = signal_line.iloc[-1]
                latest_stoch_k = stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50
                latest_stoch_d = stoch_d.iloc[-1] if not pd.isna(stoch_d.iloc[-1]) else 50
                latest_atr = atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0
                latest_williams = williams_r.iloc[-1] if not pd.isna(williams_r.iloc[-1]) else -50

                # Summary metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Price", f"${latest_price:,.2f}")
                with col2:
                    rsi_status = "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral"
                    st.metric("RSI (14)", f"{latest_rsi:.1f}", rsi_status)
                with col3:
                    macd_status = "Bullish" if latest_macd > latest_signal else "Bearish"
                    st.metric("MACD", f"{latest_macd:.4f}", macd_status)
                with col4:
                    stoch_status = "Overbought" if latest_stoch_k > 80 else "Oversold" if latest_stoch_k < 20 else "Neutral"
                    st.metric("Stoch %K", f"{latest_stoch_k:.1f}", stoch_status)
                with col5:
                    atr_pct = (latest_atr / latest_price * 100) if latest_price > 0 else 0
                    st.metric("ATR (14)", f"${latest_atr:.2f}", f"{atr_pct:.1f}% volatility")

                st.markdown("---")

                # Price chart with MAs and Bollinger Bands
                st.subheader("Price with Moving Averages & Bollinger Bands")
                fig = go.Figure()

                # Bollinger Bands (as filled area)
                fig.add_trace(go.Scatter(
                    x=close.index, y=bb_upper,
                    mode='lines', name='BB Upper',
                    line=dict(color='rgba(128,128,128,0.3)', width=1)
                ))
                fig.add_trace(go.Scatter(
                    x=close.index, y=bb_lower,
                    mode='lines', name='BB Lower',
                    line=dict(color='rgba(128,128,128,0.3)', width=1),
                    fill='tonexty', fillcolor='rgba(128,128,128,0.1)'
                ))

                # Price
                fig.add_trace(go.Scatter(
                    x=close.index, y=close,
                    mode='lines', name='Price',
                    line=dict(color='#2196F3', width=2)
                ))

                # Moving averages
                fig.add_trace(go.Scatter(
                    x=close.index, y=sma_20,
                    mode='lines', name='SMA 20',
                    line=dict(color='#FF9800', width=1)
                ))
                if len(close) >= 50:
                    fig.add_trace(go.Scatter(
                        x=close.index, y=sma_50,
                        mode='lines', name='SMA 50',
                        line=dict(color='#9C27B0', width=1)
                    ))

                fig.update_layout(**get_clean_plotly_layout(), height=400)
                st.plotly_chart(fig, use_container_width=True)

                # RSI Chart
                st.subheader("RSI (14)")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=rsi.index, y=rsi,
                    mode='lines', name='RSI',
                    line=dict(color='#673AB7', width=2)
                ))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray")
                fig_rsi.update_layout(**get_clean_plotly_layout(), height=250, yaxis_range=[0, 100])
                st.plotly_chart(fig_rsi, use_container_width=True)

                # MACD Chart
                st.subheader("MACD (12, 26, 9)")
                fig_macd = go.Figure()

                # Histogram
                colors = ['green' if h >= 0 else 'red' for h in histogram]
                fig_macd.add_trace(go.Bar(
                    x=histogram.index, y=histogram,
                    name='Histogram',
                    marker_color=colors
                ))

                # MACD and Signal lines
                fig_macd.add_trace(go.Scatter(
                    x=macd_line.index, y=macd_line,
                    mode='lines', name='MACD',
                    line=dict(color='#2196F3', width=2)
                ))
                fig_macd.add_trace(go.Scatter(
                    x=signal_line.index, y=signal_line,
                    mode='lines', name='Signal',
                    line=dict(color='#FF5722', width=2)
                ))

                fig_macd.update_layout(**get_clean_plotly_layout(), height=250)
                st.plotly_chart(fig_macd, use_container_width=True)

                # Stochastic Oscillator Chart
                st.subheader("Stochastic Oscillator (14, 3, 3)")
                fig_stoch = go.Figure()

                fig_stoch.add_trace(go.Scatter(
                    x=stoch_k.index, y=stoch_k,
                    mode='lines', name='%K',
                    line=dict(color='#2196F3', width=2)
                ))
                fig_stoch.add_trace(go.Scatter(
                    x=stoch_d.index, y=stoch_d,
                    mode='lines', name='%D',
                    line=dict(color='#FF5722', width=2)
                ))

                fig_stoch.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought")
                fig_stoch.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold")
                fig_stoch.update_layout(**get_clean_plotly_layout(), height=200, yaxis_range=[0, 100])
                st.plotly_chart(fig_stoch, use_container_width=True)

                # Signal Summary
                st.markdown("---")
                st.subheader("Signal Summary")

                signals = []
                # RSI Signal
                if latest_rsi > 70:
                    signals.append(("RSI", "Bearish", f"Overbought at {latest_rsi:.1f}"))
                elif latest_rsi < 30:
                    signals.append(("RSI", "Bullish", f"Oversold at {latest_rsi:.1f}"))
                else:
                    signals.append(("RSI", "Neutral", f"At {latest_rsi:.1f}"))

                # MACD Signal
                if latest_macd > latest_signal:
                    signals.append(("MACD", "Bullish", "MACD above signal line"))
                else:
                    signals.append(("MACD", "Bearish", "MACD below signal line"))

                # MA Signal
                if latest_price > sma_20.iloc[-1]:
                    signals.append(("SMA 20", "Bullish", "Price above SMA 20"))
                else:
                    signals.append(("SMA 20", "Bearish", "Price below SMA 20"))

                # BB Signal
                if latest_price >= bb_upper.iloc[-1]:
                    signals.append(("Bollinger", "Bearish", "At upper band"))
                elif latest_price <= bb_lower.iloc[-1]:
                    signals.append(("Bollinger", "Bullish", "At lower band"))
                else:
                    signals.append(("Bollinger", "Neutral", "Within bands"))

                # Stochastic Signal
                latest_stoch_k = stoch_k.iloc[-1] if not pd.isna(stoch_k.iloc[-1]) else 50
                latest_stoch_d = stoch_d.iloc[-1] if not pd.isna(stoch_d.iloc[-1]) else 50
                if latest_stoch_k > 80:
                    signals.append(("Stochastic", "Bearish", f"Overbought at {latest_stoch_k:.1f}"))
                elif latest_stoch_k < 20:
                    signals.append(("Stochastic", "Bullish", f"Oversold at {latest_stoch_k:.1f}"))
                elif latest_stoch_k > latest_stoch_d:
                    signals.append(("Stochastic", "Bullish", f"%K crossed above %D"))
                elif latest_stoch_k < latest_stoch_d:
                    signals.append(("Stochastic", "Bearish", f"%K crossed below %D"))
                else:
                    signals.append(("Stochastic", "Neutral", f"At {latest_stoch_k:.1f}"))

                # Williams %R Signal
                latest_williams = williams_r.iloc[-1] if not pd.isna(williams_r.iloc[-1]) else -50
                if latest_williams > -20:
                    signals.append(("Williams %R", "Bearish", f"Overbought at {latest_williams:.1f}"))
                elif latest_williams < -80:
                    signals.append(("Williams %R", "Bullish", f"Oversold at {latest_williams:.1f}"))
                else:
                    signals.append(("Williams %R", "Neutral", f"At {latest_williams:.1f}"))

                signal_df = pd.DataFrame(signals, columns=['Indicator', 'Signal', 'Description'])
                st.dataframe(signal_df, use_container_width=True, hide_index=True)

                # Overall
                bullish = sum(1 for s in signals if s[1] == "Bullish")
                bearish = sum(1 for s in signals if s[1] == "Bearish")
                if bullish > bearish:
                    overall = "BULLISH"
                    overall_color = "positive"
                elif bearish > bullish:
                    overall = "BEARISH"
                    overall_color = "negative"
                else:
                    overall = "NEUTRAL"
                    overall_color = "neutral"

                st.markdown(f"**Overall Signal:** <span class='{overall_color}'>{overall}</span> ({bullish} bullish, {bearish} bearish)",
                           unsafe_allow_html=True)


# ============================================================================
# PAGE: COLLECTION STATUS
# ============================================================================

elif page == "Collection Status":
    st.title("Data Collection Status")
    st.markdown("*Monitor collector health and data freshness*")
    st.markdown("---")

    # Check all tables for freshness - this always works
    all_tables = ['stocks', 'crypto', 'forex', 'commodities', 'weather', 'news',
                  'economic_indicators', 'gdelt_events', 'worldbank_indicators',
                  'iss_positions', 'near_earth_objects', 'earthquakes']

    # Check if collection_metadata table exists
    metadata_exists = table_exists('collection_metadata')

    # Tab layout for different views
    tab1, tab2, tab3 = st.tabs(["Data Freshness", "Collector Status", "Commands"])

    with tab1:
        st.subheader("Data Freshness by Table")
        st.markdown("Shows how fresh the data is in each table")

        freshness_data = []
        total_records = 0

        for table in all_tables:
            try:
                if not table_exists(table):
                    freshness_data.append({
                        'Status': "⚪",
                        'Table': table,
                        'Records': "Not created",
                        'Age': "N/A"
                    })
                    continue

                count_result = load_data(f"SELECT COUNT(*) as cnt FROM {table}")
                count = count_result['cnt'].iloc[0] if not count_result.empty else 0
                total_records += count

                if count > 0:
                    ts_col = 'published_at' if table == 'news' else 'date' if table == 'near_earth_objects' else 'timestamp'
                    latest_result = load_data(f"SELECT MAX({ts_col}) as latest FROM {table}")
                    latest = latest_result['latest'].iloc[0] if not latest_result.empty else None

                    if latest:
                        age = datetime.now() - pd.to_datetime(latest).replace(tzinfo=None)
                        hours = age.total_seconds() / 3600
                        if hours < 1:
                            age_str = f"{int(age.total_seconds() / 60)}m"
                        elif hours < 24:
                            age_str = f"{hours:.1f}h"
                        else:
                            age_str = f"{hours / 24:.1f}d"

                        status = "🟢" if hours < 6 else "🟡" if hours < 24 else "🔴"
                    else:
                        age_str = "N/A"
                        status = "⚪"
                else:
                    age_str = "Empty"
                    status = "⚪"
                    count = 0

                freshness_data.append({
                    'Status': status,
                    'Table': table,
                    'Records': f"{count:,}",
                    'Age': age_str
                })
            except Exception as e:
                freshness_data.append({
                    'Status': "❌",
                    'Table': table,
                    'Records': "Error",
                    'Age': str(e)[:30]
                })

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tables", len(all_tables))
        with col2:
            active = sum(1 for f in freshness_data if f['Status'] == '🟢')
            st.metric("Fresh (< 6h)", active)
        with col3:
            stale = sum(1 for f in freshness_data if f['Status'] == '🔴')
            st.metric("Stale (> 24h)", stale)
        with col4:
            st.metric("Total Records", f"{total_records:,}")

        st.markdown("---")

        # Freshness table
        freshness_df = pd.DataFrame(freshness_data)
        st.dataframe(freshness_df, use_container_width=True, hide_index=True)

        # Legend
        st.caption("🟢 Fresh (< 6h) | 🟡 Warning (6-24h) | 🔴 Stale (> 24h) | ⚪ Empty/N/A | ❌ Error")

    with tab2:
        st.subheader("Collector Run History")

        if not metadata_exists:
            st.warning("Collection metadata table not found. Run `python initialize_database.py` or start the scheduler to create it.")
            st.code("python scheduler.py --run-once")
        else:
            # Load collection metadata
            metadata_df = load_data("""
                SELECT collector_name, last_run, last_success, last_duration_seconds,
                       records_collected, status, error_message, run_count
                FROM collection_metadata
                ORDER BY last_run DESC NULLS LAST
            """)

            if metadata_df.empty:
                st.info("No collection runs recorded yet. Run the scheduler to start collecting data.")
            else:
                # Summary
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Collectors", len(metadata_df))
                with col2:
                    success = len(metadata_df[metadata_df['status'] == 'success'])
                    st.metric("Successful", success)
                with col3:
                    failed = len(metadata_df[metadata_df['status'] == 'failed'])
                    st.metric("Failed", failed, delta=f"-{failed}" if failed > 0 else None,
                             delta_color="inverse")
                with col4:
                    total_runs = metadata_df['run_count'].sum()
                    st.metric("Total Runs", f"{int(total_runs):,}" if pd.notna(total_runs) else "0")

                st.markdown("---")

                # Collector cards
                for _, row in metadata_df.iterrows():
                    status = row['status'] or 'idle'
                    if status == 'success':
                        icon = "🟢"
                        box_class = "success-box"
                    elif status == 'failed':
                        icon = "🔴"
                        box_class = "alert-box"
                    elif status == 'running':
                        icon = "🔵"
                        box_class = "warning-box"
                    else:
                        icon = "⚪"
                        box_class = ""

                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    with col1:
                        st.markdown(f"**{icon} {row['collector_name'].upper()}**")

                    with col2:
                        last_run = row['last_run']
                        if pd.notna(last_run):
                            age = datetime.now() - pd.to_datetime(last_run).replace(tzinfo=None)
                            hours = age.total_seconds() / 3600
                            if hours < 1:
                                age_str = f"{int(age.total_seconds() / 60)}m ago"
                            elif hours < 24:
                                age_str = f"{hours:.1f}h ago"
                            else:
                                age_str = f"{hours / 24:.1f}d ago"
                            st.caption(f"Last: {age_str}")
                        else:
                            st.caption("Never run")

                    with col3:
                        duration = row['last_duration_seconds']
                        records = row['records_collected']
                        if pd.notna(duration):
                            st.caption(f"{duration:.1f}s | {int(records) if pd.notna(records) else 0} rec")
                        else:
                            st.caption("-")

                    with col4:
                        st.caption(f"Runs: {row['run_count'] or 0}")

                    # Show error if failed
                    if status == 'failed' and row['error_message']:
                        st.error(f"Error: {row['error_message'][:200]}...")

                st.markdown("---")

    with tab3:
        st.subheader("Scheduler Commands")
        st.markdown("Use these commands to manage data collection:")

        st.code("""
# Start continuous scheduler (runs in background)
python scheduler.py

# Run all collectors once and exit
python scheduler.py --run-once

# Run a specific collector
python scheduler.py --collector crypto
python scheduler.py --collector markets
python scheduler.py --collector weather

# Check collector status
python scheduler.py --status

# Start scheduler without initial collection
python scheduler.py --no-initial
        """, language="bash")

        st.markdown("---")
        st.subheader("Available Collectors")

        collectors_info = {
            'markets': 'Stock prices from major exchanges (15 min)',
            'crypto': 'Cryptocurrency prices and market caps (10 min)',
            'forex': 'Foreign exchange rates (15 min)',
            'commodities': 'Commodity prices - gold, oil, etc. (30 min)',
            'weather': 'Weather data for 50+ cities (30 min)',
            'news': 'Financial news headlines (60 min)',
            'economics': 'Economic indicators - GDP, inflation (daily)',
            'space': 'ISS position, NEO tracking (daily)',
            'disasters': 'Earthquake data (60 min)',
            'gdelt': 'Global events and unrest (60 min)',
            'worldbank': 'Development indicators (daily)',
        }

        for name, desc in collectors_info.items():
            st.markdown(f"- **{name}**: {desc}")


# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("**Hermes Intelligence Platform**")
st.sidebar.caption("Multi-layer investment intelligence")
