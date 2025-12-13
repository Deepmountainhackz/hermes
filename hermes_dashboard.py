"""
Hermes Intelligence Platform Dashboard
Complete multi-layer intelligence visualization
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
    # Try Streamlit secrets first (for Streamlit Cloud)
    if hasattr(st, 'secrets') and 'database' in st.secrets:
        return {
            'host': st.secrets.database.host,
            'port': st.secrets.database.port,
            'dbname': st.secrets.database.name,
            'user': st.secrets.database.user,
            'password': st.secrets.database.password,
        }

    # Fall back to environment variables (for local development)
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
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    .metric-positive { color: #00c853; }
    .metric-negative { color: #ff1744; }
    </style>
    """, unsafe_allow_html=True)


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
        if 'c' in df.columns:
            return int(df['c'].iloc[0])
        return int(df.iloc[0, 0])
    except Exception:
        return 0


def get_latest_timestamp(table, timestamp_col='timestamp'):
    """Get the latest timestamp from a table"""
    try:
        df = load_data(f'SELECT MAX({timestamp_col}) as latest FROM {table}')
        if df.empty or df['latest'].iloc[0] is None:
            return "No data"
        return df['latest'].iloc[0]
    except Exception:
        return "No data"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_change(value):
    """Format a change value with color"""
    if value is None:
        return "N/A"
    if value > 0:
        return f"+{value:.2f}%"
    return f"{value:.2f}%"


def get_change_color(value):
    """Get color based on change value"""
    if value is None:
        return "gray"
    return "green" if value >= 0 else "red"


def create_sparkline(data, height=50):
    """Create a simple sparkline chart"""
    if data.empty or len(data) < 2:
        return None
    fig = go.Figure(go.Scatter(
        y=data, mode='lines',
        line=dict(color='#1f77b4', width=1),
        fill='tozeroy', fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("🌐 Hermes Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Overview", "📈 Markets", "💹 Economic Indicators",
     "🌦️ Weather & Environment", "🛰️ Space", "📰 News"]
)

st.sidebar.markdown("---")

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(f"**Last Refresh:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "🏠 Overview":
    st.title("🌐 Hermes Intelligence Platform")
    st.markdown("### Real-time Multi-Layer Intelligence Dashboard")
    st.markdown("---")

    # System Stats
    st.subheader("📊 System Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📈 Stock Records", f"{get_count('stocks'):,}")
    with col2:
        st.metric("💱 Forex Records", f"{get_count('forex'):,}")
    with col3:
        st.metric("🛢️ Commodity Records", f"{get_count('commodities'):,}")
    with col4:
        st.metric("🌦️ Weather Records", f"{get_count('weather'):,}")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric("☄️ NEO Records", f"{get_count('near_earth_objects'):,}")
    with col6:
        st.metric("🛰️ ISS Positions", f"{get_count('iss_positions'):,}")
    with col7:
        st.metric("📰 News Articles", f"{get_count('news'):,}")
    with col8:
        st.metric("💹 Economic Indicators", f"{get_count('economic_indicators'):,}")

    st.markdown("---")

    # Market Overview
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Latest Stock Prices")
        stocks = load_data("""
            SELECT symbol, price, change_percent
            FROM stocks
            WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
            ORDER BY symbol
            LIMIT 10
        """)

        if not stocks.empty:
            for _, row in stocks.iterrows():
                change = row.get('change_percent', 0) or 0
                color = "🟢" if change >= 0 else "🔴"
                st.write(f"{color} **{row['symbol']}**: ${row['price']:.2f} ({format_change(change)})")
        else:
            st.info("No stock data yet")

    with col2:
        st.subheader("💱 Forex Rates")
        forex = load_data("""
            SELECT pair, rate
            FROM forex
            WHERE timestamp = (SELECT MAX(timestamp) FROM forex)
            ORDER BY pair
            LIMIT 7
        """)

        if not forex.empty:
            for _, row in forex.iterrows():
                st.write(f"**{row['pair']}**: {row['rate']:.4f}")
        else:
            st.info("No forex data yet")

    st.markdown("---")

    # Quick Stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🛰️ ISS Current Position")
        iss = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 1")
        if not iss.empty:
            latest = iss.iloc[0]
            st.write(f"**Latitude:** {latest['latitude']:.4f}°")
            st.write(f"**Longitude:** {latest['longitude']:.4f}°")
            st.write(f"**Altitude:** {latest['altitude']:.2f} km")
            st.write(f"**Velocity:** {latest['velocity']:,.0f} km/h")
        else:
            st.info("No ISS data yet")

    with col2:
        st.subheader("🌦️ Weather Sample")
        weather = load_data("""
            SELECT city, temperature, description
            FROM weather
            WHERE timestamp = (SELECT MAX(timestamp) FROM weather)
            LIMIT 5
        """)
        if not weather.empty:
            for _, row in weather.iterrows():
                temp = row.get('temperature')
                if temp is not None:
                    st.write(f"**{row['city']}**: {temp:.1f}°C - {row['description'] or 'N/A'}")
        else:
            st.info("No weather data yet")

    with col3:
        st.subheader("📰 Latest Headlines")
        news = load_data("SELECT source, title FROM news ORDER BY published_at DESC LIMIT 5")
        if not news.empty:
            for _, row in news.iterrows():
                st.write(f"**[{row['source']}]** {row['title'][:60]}...")
        else:
            st.info("No news data yet")


# ============================================================================
# PAGE: MARKETS
# ============================================================================

elif page == "📈 Markets":
    st.title("📈 Market Intelligence")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Stocks", "🛢️ Commodities", "💱 Forex"])

    # === STOCKS TAB ===
    with tab1:
        st.subheader("Stock Market Overview")

        stocks_df = load_data("""
            SELECT symbol, name, price, change, change_percent, volume, timestamp
            FROM stocks
            ORDER BY timestamp DESC, symbol
        """)

        if stocks_df.empty:
            st.warning("No stock data available. Run the stock collector to populate data.")
        else:
            # Get latest data for each symbol
            stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp'])
            latest_stocks = stocks_df.groupby('symbol').first().reset_index()

            # Metrics row
            col1, col2, col3, col4 = st.columns(4)

            gainers = latest_stocks[latest_stocks['change_percent'] > 0]
            losers = latest_stocks[latest_stocks['change_percent'] < 0]

            with col1:
                st.metric("Total Stocks", len(latest_stocks))
            with col2:
                st.metric("Gainers", len(gainers), delta=f"{len(gainers)}" if len(gainers) > 0 else None)
            with col3:
                st.metric("Losers", len(losers), delta=f"-{len(losers)}" if len(losers) > 0 else None)
            with col4:
                if not latest_stocks.empty and 'change_percent' in latest_stocks.columns:
                    avg_change = latest_stocks['change_percent'].mean()
                    st.metric("Avg Change", f"{avg_change:.2f}%")
                else:
                    st.metric("Avg Change", "N/A")

            st.markdown("---")

            # Stock table with color coding
            st.subheader("📋 All Stocks")

            # Prepare display dataframe
            display_df = latest_stocks[['symbol', 'name', 'price', 'change', 'change_percent', 'volume']].copy()
            display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x else "N/A")
            display_df['change'] = display_df['change'].apply(lambda x: f"${x:.2f}" if x else "N/A")
            display_df['change_percent'] = display_df['change_percent'].apply(format_change)
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,.0f}" if x else "N/A")
            display_df.columns = ['Symbol', 'Name', 'Price', 'Change', 'Change %', 'Volume']

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Individual stock analysis
            st.subheader("📈 Stock Analysis")
            selected_stock = st.selectbox("Select Stock", sorted(latest_stocks['symbol'].unique()))

            if selected_stock:
                stock_history = stocks_df[stocks_df['symbol'] == selected_stock].sort_values('timestamp')

                if len(stock_history) > 1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=stock_history['timestamp'],
                        y=stock_history['price'],
                        mode='lines+markers',
                        name=selected_stock,
                        line=dict(color='#1f77b4', width=2)
                    ))
                    fig.update_layout(
                        title=f"{selected_stock} Price History",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Not enough historical data for {selected_stock} to show chart")

            # Comparison chart
            st.markdown("---")
            st.subheader("📊 Stock Comparison (Normalized)")

            if len(latest_stocks) > 1:
                # Normalize prices to base 100
                fig = go.Figure()
                for symbol in stocks_df['symbol'].unique():
                    symbol_data = stocks_df[stocks_df['symbol'] == symbol].sort_values('timestamp')
                    if len(symbol_data) > 1 and symbol_data['price'].iloc[0] != 0:
                        normalized = (symbol_data['price'] / symbol_data['price'].iloc[0]) * 100
                        fig.add_trace(go.Scatter(
                            x=symbol_data['timestamp'],
                            y=normalized,
                            mode='lines',
                            name=symbol
                        ))

                fig.update_layout(
                    title="Normalized Performance (Base 100)",
                    xaxis_title="Date",
                    yaxis_title="Normalized Price",
                    height=500,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

    # === COMMODITIES TAB ===
    with tab2:
        st.subheader("Commodity Prices")

        commodities_df = load_data("""
            SELECT symbol, name, price, change, change_percent, unit, timestamp
            FROM commodities
            ORDER BY timestamp DESC, symbol
        """)

        if commodities_df.empty:
            st.warning("No commodity data available. Run the commodity collector to populate data.")
        else:
            commodities_df['timestamp'] = pd.to_datetime(commodities_df['timestamp'])
            latest_commodities = commodities_df.groupby('symbol').first().reset_index()

            # Display as cards
            cols = st.columns(3)
            for idx, (_, row) in enumerate(latest_commodities.iterrows()):
                with cols[idx % 3]:
                    change = row.get('change_percent', 0) or 0
                    delta_color = "normal" if change >= 0 else "inverse"

                    st.metric(
                        label=f"{row['name'] or row['symbol']}",
                        value=f"${row['price']:.2f}" if row['price'] else "N/A",
                        delta=format_change(change)
                    )
                    if row.get('unit'):
                        st.caption(f"Unit: {row['unit']}")

            st.markdown("---")

            # Commodity price chart
            st.subheader("📈 Commodity Price History")
            selected_commodity = st.selectbox("Select Commodity", sorted(latest_commodities['symbol'].unique()))

            if selected_commodity:
                commodity_history = commodities_df[commodities_df['symbol'] == selected_commodity].sort_values('timestamp')

                if len(commodity_history) > 1:
                    fig = px.line(commodity_history, x='timestamp', y='price',
                                 title=f"{selected_commodity} Price History")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Not enough historical data for {selected_commodity}")

    # === FOREX TAB ===
    with tab3:
        st.subheader("Foreign Exchange Rates")

        forex_df = load_data("""
            SELECT pair, from_currency, to_currency, rate, bid, ask, timestamp
            FROM forex
            ORDER BY timestamp DESC, pair
        """)

        if forex_df.empty:
            st.warning("No forex data available. Run the forex collector to populate data.")
        else:
            forex_df['timestamp'] = pd.to_datetime(forex_df['timestamp'])
            latest_forex = forex_df.groupby('pair').first().reset_index()

            # Display forex table
            display_forex = latest_forex[['pair', 'rate', 'bid', 'ask']].copy()
            display_forex['rate'] = display_forex['rate'].apply(lambda x: f"{x:.4f}" if x else "N/A")
            display_forex['bid'] = display_forex['bid'].apply(lambda x: f"{x:.4f}" if x else "N/A")
            display_forex['ask'] = display_forex['ask'].apply(lambda x: f"{x:.4f}" if x else "N/A")
            display_forex.columns = ['Pair', 'Rate', 'Bid', 'Ask']

            st.dataframe(display_forex, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Forex rate history
            st.subheader("📈 Forex Rate History")
            selected_pair = st.selectbox("Select Currency Pair", sorted(latest_forex['pair'].unique()))

            if selected_pair:
                pair_history = forex_df[forex_df['pair'] == selected_pair].sort_values('timestamp')

                if len(pair_history) > 1:
                    fig = px.line(pair_history, x='timestamp', y='rate',
                                 title=f"{selected_pair} Exchange Rate History")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Not enough historical data for {selected_pair}")


# ============================================================================
# PAGE: ECONOMIC INDICATORS
# ============================================================================

elif page == "💹 Economic Indicators":
    st.title("💹 Economic Indicators")
    st.markdown("---")

    econ_df = load_data("""
        SELECT indicator, country, name, value, unit, timestamp
        FROM economic_indicators
        ORDER BY timestamp DESC, country, indicator
    """)

    if econ_df.empty:
        st.warning("No economic indicator data available. Run the economics collector to populate data.")
    else:
        econ_df['timestamp'] = pd.to_datetime(econ_df['timestamp'])

        # Get unique countries and indicators
        countries = sorted(econ_df['country'].unique().tolist())
        indicators = sorted(econ_df['indicator'].unique().tolist())

        # Country selector
        st.subheader("🌍 Select Country")
        selected_country = st.selectbox("Country", countries)

        if selected_country:
            country_data = econ_df[econ_df['country'] == selected_country]
            latest_country = country_data.groupby('indicator').first().reset_index()

            st.markdown("---")
            st.subheader(f"📊 {selected_country} Economic Indicators")

            # Display indicators as metrics
            cols = st.columns(min(4, len(latest_country)))
            for idx, (_, row) in enumerate(latest_country.iterrows()):
                with cols[idx % len(cols)]:
                    unit_str = f" {row['unit']}" if row.get('unit') else ""
                    st.metric(
                        label=row['name'] or row['indicator'],
                        value=f"{row['value']:.2f}{unit_str}" if row['value'] else "N/A"
                    )

            st.markdown("---")

            # Historical chart for selected indicator
            st.subheader("📈 Indicator History")
            selected_indicator = st.selectbox("Select Indicator", sorted(latest_country['indicator'].unique()))

            if selected_indicator:
                indicator_history = country_data[country_data['indicator'] == selected_indicator].sort_values('timestamp')

                if len(indicator_history) > 1:
                    fig = px.line(indicator_history, x='timestamp', y='value',
                                 title=f"{selected_indicator} - {selected_country}")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"Not enough historical data for {selected_indicator}")

        st.markdown("---")

        # Country comparison
        st.subheader("🌍 Country Comparison")

        col1, col2 = st.columns(2)
        with col1:
            compare_countries = st.multiselect("Select Countries to Compare", countries, default=countries[:3] if len(countries) >= 3 else countries)
        with col2:
            compare_indicator = st.selectbox("Select Indicator for Comparison", indicators, key="compare_ind")

        if compare_countries and compare_indicator:
            comparison_data = econ_df[
                (econ_df['country'].isin(compare_countries)) &
                (econ_df['indicator'] == compare_indicator)
            ]

            if not comparison_data.empty:
                # Get latest value for each country
                latest_comparison = comparison_data.groupby('country').first().reset_index()

                fig = px.bar(latest_comparison, x='country', y='value',
                            color='country', title=f"{compare_indicator} by Country")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for selected comparison")


# ============================================================================
# PAGE: WEATHER & ENVIRONMENT
# ============================================================================

elif page == "🌦️ Weather & Environment":
    st.title("🌦️ Weather & Environmental Monitoring")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🌡️ Weather", "🌋 Disasters"])

    # === WEATHER TAB ===
    with tab1:
        weather_df = load_data("""
            SELECT city, country, temperature, feels_like, humidity, pressure, wind_speed, description, timestamp
            FROM weather
            ORDER BY timestamp DESC
        """)

        if weather_df.empty:
            st.warning("No weather data available. Run the weather collector to populate data.")
        else:
            weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])
            weather_df['temperature'] = pd.to_numeric(weather_df['temperature'], errors='coerce')
            weather_df['feels_like'] = pd.to_numeric(weather_df['feels_like'], errors='coerce')
            weather_df['humidity'] = pd.to_numeric(weather_df['humidity'], errors='coerce')

            # Get latest weather for each city
            latest_weather = weather_df.groupby('city').first().reset_index()
            latest_weather = latest_weather[latest_weather['temperature'].notna()]

            # Add coordinates
            latest_weather['lat'] = latest_weather['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lat'))
            latest_weather['lon'] = latest_weather['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lon'))

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Cities Tracked", len(latest_weather))
            with col2:
                hottest = latest_weather.loc[latest_weather['temperature'].idxmax()]
                st.metric("Hottest", f"{hottest['city']}", f"{hottest['temperature']:.1f}°C")
            with col3:
                coldest = latest_weather.loc[latest_weather['temperature'].idxmin()]
                st.metric("Coldest", f"{coldest['city']}", f"{coldest['temperature']:.1f}°C")
            with col4:
                avg_temp = latest_weather['temperature'].mean()
                st.metric("Avg Temperature", f"{avg_temp:.1f}°C")

            st.markdown("---")

            # 3D Globe Map
            st.subheader("🌐 Global Weather Map")

            map_data = latest_weather[latest_weather['lat'].notna() & latest_weather['lon'].notna()].copy()

            if not map_data.empty:
                fig = go.Figure(go.Scattergeo(
                    lon=map_data['lon'],
                    lat=map_data['lat'],
                    text=map_data.apply(lambda r: f"{r['city']}: {r['temperature']:.1f}°C", axis=1),
                    mode='markers',
                    marker=dict(
                        size=map_data['temperature'].apply(lambda x: max(abs(x) + 5, 8)),
                        color=map_data['temperature'],
                        colorscale=[[0, 'rgb(0,0,255)'], [0.5, 'rgb(128,0,128)'], [1, 'rgb(255,0,0)']],
                        cmin=-20, cmax=45,
                        colorbar=dict(title="Temp (°C)", thickness=15),
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate='<b>%{text}</b><extra></extra>'
                ))

                fig.update_geos(
                    projection_type='orthographic',
                    showcountries=True, countrycolor='rgba(255,255,255,0.3)',
                    showcoastlines=True, coastlinecolor='rgba(255,255,255,0.5)',
                    showland=True, landcolor='rgb(30,30,30)',
                    showocean=True, oceancolor='rgb(10,10,30)',
                    projection_rotation=dict(lon=0, lat=30, roll=0)
                )

                fig.update_layout(
                    title="🌍 Global Weather - 3D Globe View",
                    height=600,
                    paper_bgcolor='rgb(0,0,0)',
                    plot_bgcolor='rgb(0,0,0)',
                    font=dict(color='white'),
                    geo=dict(bgcolor='rgb(0,0,0)'),
                    dragmode='pan'
                )
                st.plotly_chart(fig, use_container_width=True)
                st.info("🌍 Drag to rotate the globe | Scroll to zoom")

            st.markdown("---")

            # Weather table
            st.subheader("📊 Current Weather Conditions")

            # Sortable table
            sort_col = st.selectbox("Sort by", ["Temperature", "City", "Humidity"], key="weather_sort")
            sort_map = {"Temperature": "temperature", "City": "city", "Humidity": "humidity"}
            sorted_weather = latest_weather.sort_values(sort_map[sort_col], ascending=(sort_col == "City"))

            display_weather = sorted_weather[['city', 'temperature', 'feels_like', 'humidity', 'description']].copy()
            display_weather['temperature'] = display_weather['temperature'].apply(lambda x: f"{x:.1f}°C" if pd.notna(x) else "N/A")
            display_weather['feels_like'] = display_weather['feels_like'].apply(lambda x: f"{x:.1f}°C" if pd.notna(x) else "N/A")
            display_weather['humidity'] = display_weather['humidity'].apply(lambda x: f"{x:.0f}%" if pd.notna(x) else "N/A")
            display_weather.columns = ['City', 'Temperature', 'Feels Like', 'Humidity', 'Conditions']

            st.dataframe(display_weather, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Temperature trends
            st.subheader("📈 Temperature Trends")
            selected_cities = st.multiselect("Select Cities", sorted(weather_df['city'].unique()),
                                            default=sorted(weather_df['city'].unique())[:5])

            if selected_cities:
                fig = go.Figure()
                for city in selected_cities:
                    city_data = weather_df[weather_df['city'] == city].sort_values('timestamp')
                    if not city_data.empty:
                        fig.add_trace(go.Scatter(
                            x=city_data['timestamp'],
                            y=city_data['temperature'],
                            name=city,
                            mode='lines+markers'
                        ))

                fig.update_layout(
                    title="Temperature Over Time",
                    xaxis_title="Time",
                    yaxis_title="Temperature (°C)",
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)

    # === DISASTERS TAB ===
    with tab2:
        st.subheader("🌋 Natural Disasters & Earthquakes")

        disasters_df = load_data("""
            SELECT disaster_type, location, magnitude, description, timestamp
            FROM disasters
            ORDER BY timestamp DESC
            LIMIT 50
        """)

        if disasters_df.empty:
            st.info("No disaster data recorded yet.")
        else:
            disasters_df['timestamp'] = pd.to_datetime(disasters_df['timestamp'])

            # Summary metrics
            col1, col2, col3 = st.columns(3)

            # Last 24 hours
            last_24h = disasters_df[disasters_df['timestamp'] > datetime.now() - timedelta(hours=24)]
            last_7d = disasters_df[disasters_df['timestamp'] > datetime.now() - timedelta(days=7)]

            with col1:
                st.metric("Events (24h)", len(last_24h))
            with col2:
                st.metric("Events (7d)", len(last_7d))
            with col3:
                if not disasters_df.empty and 'magnitude' in disasters_df.columns:
                    max_mag = disasters_df['magnitude'].max()
                    st.metric("Max Magnitude", f"{max_mag:.1f}" if pd.notna(max_mag) else "N/A")
                else:
                    st.metric("Max Magnitude", "N/A")

            st.markdown("---")

            # Recent events list
            st.subheader("📋 Recent Events")

            for _, event in disasters_df.head(20).iterrows():
                mag = event.get('magnitude')
                mag_str = f"M{mag:.1f}" if pd.notna(mag) else ""

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{event['disaster_type'] or 'Event'}** {mag_str}")
                    st.write(f"📍 {event['location'] or 'Unknown location'}")
                    if event.get('description'):
                        st.caption(event['description'][:200])
                with col2:
                    st.caption(str(event['timestamp']))
                st.markdown("---")


# ============================================================================
# PAGE: SPACE
# ============================================================================

elif page == "🛰️ Space":
    st.title("🛰️ Space Intelligence")
    st.markdown("---")

    # === ISS TRACKER ===
    st.subheader("🛰️ International Space Station")

    iss_df = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 100")

    if iss_df.empty:
        st.info("No ISS position data yet. Run the space collector to populate data.")
    else:
        latest = iss_df.iloc[0]

        col1, col2 = st.columns([2, 1])

        with col1:
            # Map showing ISS position and recent path
            fig = go.Figure()

            # Add trail
            if len(iss_df) > 1:
                fig.add_trace(go.Scattergeo(
                    lon=iss_df['longitude'].tolist(),
                    lat=iss_df['latitude'].tolist(),
                    mode='lines',
                    line=dict(color='rgba(255, 0, 0, 0.5)', width=2),
                    name='Recent Path'
                ))

            # Add current position
            fig.add_trace(go.Scattergeo(
                lon=[latest['longitude']],
                lat=[latest['latitude']],
                mode='markers+text',
                marker=dict(size=15, color='red', symbol='star'),
                text=['ISS'],
                textposition="top center",
                name='Current Position'
            ))

            fig.update_layout(
                title="ISS Current Position",
                geo=dict(
                    projection_type='natural earth',
                    showland=True, landcolor='lightgreen',
                    showocean=True, oceancolor='lightblue',
                    showcountries=True
                ),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.metric("📍 Latitude", f"{latest['latitude']:.4f}°")
            st.metric("📍 Longitude", f"{latest['longitude']:.4f}°")
            st.metric("🚀 Altitude", f"{latest['altitude']:.2f} km")
            st.metric("⚡ Velocity", f"{latest['velocity']:,.0f} km/h")
            st.caption(f"Last update: {latest['timestamp']}")

    st.markdown("---")

    # === NEAR-EARTH OBJECTS ===
    st.subheader("☄️ Near-Earth Objects")

    neo_df = load_data("""
        SELECT name, date,
               estimated_diameter_min, estimated_diameter_max,
               relative_velocity, miss_distance, is_potentially_hazardous
        FROM near_earth_objects
        WHERE date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY date DESC
        LIMIT 30
    """)

    if neo_df.empty:
        st.info("No Near-Earth Object data yet. Run the space collector to populate data.")
    else:
        # Convert Decimal types to float for Plotly compatibility
        neo_df['date'] = pd.to_datetime(neo_df['date'])
        neo_df['estimated_diameter_min'] = pd.to_numeric(neo_df['estimated_diameter_min'], errors='coerce')
        neo_df['estimated_diameter_max'] = pd.to_numeric(neo_df['estimated_diameter_max'], errors='coerce')
        neo_df['relative_velocity'] = pd.to_numeric(neo_df['relative_velocity'], errors='coerce')
        neo_df['miss_distance'] = pd.to_numeric(neo_df['miss_distance'], errors='coerce')

        # Summary
        col1, col2, col3 = st.columns(3)

        hazardous_count = neo_df['is_potentially_hazardous'].sum() if 'is_potentially_hazardous' in neo_df.columns else 0

        with col1:
            st.metric("Total NEOs", len(neo_df))
        with col2:
            st.metric("Potentially Hazardous", int(hazardous_count))
        with col3:
            if 'estimated_diameter_max' in neo_df.columns:
                largest = neo_df['estimated_diameter_max'].max()
                st.metric("Largest Diameter", f"{largest:.0f} m" if pd.notna(largest) else "N/A")
            else:
                st.metric("Largest Diameter", "N/A")

        st.markdown("---")

        # NEO Table
        display_neo = neo_df.copy()
        display_neo['Hazardous'] = display_neo['is_potentially_hazardous'].apply(lambda x: 'YES' if x else 'No')
        display_neo['Diameter (m)'] = display_neo.apply(
            lambda r: f"{r['estimated_diameter_min']:.0f} - {r['estimated_diameter_max']:.0f}"
            if pd.notna(r['estimated_diameter_min']) else "N/A", axis=1
        )
        display_neo['Velocity (km/h)'] = display_neo['relative_velocity'].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
        )
        display_neo['Miss Distance (km)'] = display_neo['miss_distance'].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
        )

        st.dataframe(
            display_neo[['name', 'date', 'Diameter (m)', 'Velocity (km/h)', 'Miss Distance (km)', 'Hazardous']],
            use_container_width=True, hide_index=True
        )

        # Size visualization
        if not neo_df.empty and 'estimated_diameter_max' in neo_df.columns:
            st.markdown("---")
            st.subheader("NEO Size Distribution")

            # Filter out rows with missing data for the chart
            chart_df = neo_df.dropna(subset=['date', 'estimated_diameter_max'])
            if not chart_df.empty:
                fig = px.scatter(
                    chart_df, x='date', y='estimated_diameter_max',
                    size='estimated_diameter_max',
                    color='is_potentially_hazardous',
                    hover_data=['name', 'relative_velocity'],
                    title="Near-Earth Objects by Date and Size",
                    labels={'estimated_diameter_max': 'Max Diameter (m)', 'is_potentially_hazardous': 'Hazardous'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data to display chart")

    st.markdown("---")

    # === SOLAR FLARES ===
    st.subheader("☀️ Solar Activity")

    solar_df = load_data("""
        SELECT flare_id, class_type, begin_time, peak_time, source_location
        FROM solar_flares
        ORDER BY begin_time DESC
        LIMIT 20
    """)

    if solar_df.empty:
        st.info("No recent solar flare data. This may indicate a quiet sun or no data collected yet.")
    else:
        # Class type summary
        class_counts = solar_df['class_type'].value_counts()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.write("**Flare Classes:**")
            for cls, count in class_counts.items():
                st.write(f"- {cls}: {count}")

        with col2:
            fig = px.pie(values=class_counts.values, names=class_counts.index,
                        title="Solar Flare Distribution by Class")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Recent flares table
        st.subheader("📋 Recent Solar Flares")
        st.dataframe(solar_df, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE: NEWS
# ============================================================================

elif page == "📰 News":
    st.title("📰 News Intelligence")
    st.markdown("---")

    news_df = load_data("""
        SELECT title, source, url, description, published_at
        FROM news
        ORDER BY published_at DESC
        LIMIT 100
    """)

    if news_df.empty:
        st.warning("No news data available. Run the news collector to populate data.")
    else:
        # Source filter
        sources = ['All'] + sorted(news_df['source'].unique().tolist())
        selected_source = st.selectbox("Filter by Source", sources)

        filtered_news = news_df if selected_source == 'All' else news_df[news_df['source'] == selected_source]

        st.write(f"**Showing {len(filtered_news)} articles**")
        st.markdown("---")

        # News articles
        for _, article in filtered_news.iterrows():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.subheader(article['title'] or "Untitled")
                if article.get('description'):
                    st.write(article['description'][:300] + "..." if len(str(article['description'])) > 300 else article['description'])
                if article.get('url'):
                    st.markdown(f"[Read full article →]({article['url']})")

            with col2:
                st.write(f"**{article['source']}**")
                if article.get('published_at'):
                    st.caption(str(article['published_at'])[:19])

            st.markdown("---")

        # Source distribution
        st.subheader("📊 Articles by Source")
        source_counts = news_df['source'].value_counts().reset_index()
        source_counts.columns = ['Source', 'Count']

        fig = px.bar(source_counts, x='Source', y='Count', color='Source',
                    title="News Distribution by Source")
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.markdown("**Hermes Intelligence Platform**")
st.sidebar.caption("Multi-layer investment intelligence system")
st.sidebar.caption("v2.0 - Complete Dashboard")
