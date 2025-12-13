"""
Hermes Intelligence Platform Dashboard v4.0
Multi-layer intelligence with 3D globe, time-series analysis, and GDELT integration
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
# PAGE CONFIGURATION WITH DARK MODE
# ============================================================================

st.set_page_config(
    page_title="Hermes Intelligence Platform",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark mode CSS
DARK_MODE_CSS = """
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stSidebar { background-color: #161b22; }
    .stMetric { background-color: #21262d; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stDataFrame { background-color: #161b22; }
    .metric-card { background: linear-gradient(135deg, #1a1f2e 0%, #2d3548 100%); padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin: 5px 0; }
    .positive { color: #00d26a; }
    .negative { color: #ff4757; }
    .neutral { color: #a0a0a0; }
    h1, h2, h3 { color: #58a6ff; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #21262d; border-radius: 8px; color: #c9d1d9; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #388bfd; color: white; }
    .alert-box { background-color: #2d1f1f; border: 1px solid #ff4757; border-radius: 8px; padding: 15px; margin: 10px 0; }
    .success-box { background-color: #1f2d1f; border: 1px solid #00d26a; border-radius: 8px; padding: 15px; margin: 10px 0; }
    .warning-box { background-color: #2d2d1f; border: 1px solid #ffa502; border-radius: 8px; padding: 15px; margin: 10px 0; }
</style>
"""
st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)


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


def get_dark_plotly_layout():
    """Standard dark theme layout for Plotly charts"""
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)'),
        yaxis=dict(gridcolor='rgba(128,128,128,0.2)', zerolinecolor='rgba(128,128,128,0.2)')
    )


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("Hermes Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["Overview", "Markets", "Crypto", "Economic Indicators",
     "Weather & Globe", "Space", "Global Events", "News",
     "Time Series", "Alerts & Export"]
)

st.sidebar.markdown("---")

if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(f"Last Refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.caption("v4.0 - Globe + Time Series + GDELT")


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "Overview":
    st.title("Hermes Intelligence Platform")
    st.markdown("### Real-time Multi-Layer Intelligence Dashboard")
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
            display_df = latest_stocks[['symbol', 'name', 'price', 'change_percent', 'volume']].copy()
            display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x else "N/A")
            display_df['change_percent'] = display_df['change_percent'].apply(format_change)
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}" if x else "N/A")
            display_df.columns = ['Symbol', 'Name', 'Price', 'Change %', 'Volume']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

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
                fig.update_layout(**get_dark_plotly_layout(), height=400)
                st.plotly_chart(fig, use_container_width=True)


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
                    colorbar=dict(title="Temp (C)", tickfont=dict(color='white')),
                    line=dict(width=1, color='white')
                ),
                hoverinfo='text'
            ))

            # 3D Globe projection
            fig.update_geos(
                projection_type=projection.replace(" ", ""),
                projection_rotation_lon=rotation,
                showland=True,
                landcolor='rgb(40, 40, 40)',
                showocean=True,
                oceancolor='rgb(20, 30, 50)',
                showlakes=True,
                lakecolor='rgb(30, 40, 60)',
                showcoastlines=True,
                coastlinecolor='rgb(80, 80, 80)',
                showframe=False,
                bgcolor='rgba(0,0,0,0)'
            )

            fig.update_layout(
                height=600,
                paper_bgcolor='rgba(0,0,0,0)',
                geo=dict(bgcolor='rgba(0,0,0,0)'),
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
                fig.update_layout(**get_dark_plotly_layout(), height=400)
                st.plotly_chart(fig, use_container_width=True)

            with tab3:
                # Sentiment by country
                country_tone = gdelt_df.groupby('country')['tone'].mean().sort_values()
                fig = px.bar(x=country_tone.values, y=country_tone.index, orientation='h',
                            title="Average Sentiment by Country (Negative = Unrest)",
                            color=country_tone.values, color_continuous_scale='RdYlGn')
                fig.update_layout(**get_dark_plotly_layout(), height=500)
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
        sources = ['All'] + sorted(news_df['source'].dropna().unique().tolist())
        selected_source = st.selectbox("Filter by Source", sources)

        filtered = news_df if selected_source == 'All' else news_df[news_df['source'] == selected_source]

        st.write(f"**Showing {len(filtered)} articles**")
        st.markdown("---")

        for _, article in filtered.iterrows():
            st.markdown(f"### {article['title'] or 'Untitled'}")
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
                    **get_dark_plotly_layout(),
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
                    **get_dark_plotly_layout(),
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
                    **get_dark_plotly_layout(),
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
                    **get_dark_plotly_layout(),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)


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
