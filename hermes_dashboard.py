import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import h3
from config_cities import CITY_COORDS  # Move city data to separate file
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables (for local development)
load_dotenv()


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
# CONFIGURATION & SETUP
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
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# DATABASE & HELPER FUNCTIONS
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
                # dict_row returns list of dicts
                return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def render_metric_row(metrics_data, columns=4):
    """Render a row of metrics with consistent styling"""
    cols = st.columns(columns)
    for col, (label, value, delta) in zip(cols, metrics_data):
        with col:
            st.metric(label, value, delta if delta else None)

def create_comparison_chart(df, date_col, value_col, group_col, title, normalize=False):
    """Create a line chart comparing multiple series"""
    pivot_df = df.pivot(index=date_col, columns=group_col, values=value_col)
    if normalize:
        pivot_df = (pivot_df / pivot_df.iloc[0] * 100)
    
    fig = go.Figure()
    for col in pivot_df.columns:
        fig.add_trace(go.Scatter(
            x=pivot_df.index, y=pivot_df[col],
            name=col, mode='lines'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=date_col.title(),
        yaxis_title="Normalized Price" if normalize else value_col.title(),
        height=500,
        hovermode='x unified'
    )
    return fig

def create_globe_map(df, lat_col, lon_col, color_col, text_col, title):
    """Create a 3D globe visualization"""
    fig = go.Figure(go.Scattergeo(
        lon=df[lon_col],
        lat=df[lat_col],
        text=df[text_col],
        mode='markers+text',
        marker=dict(
            size=df[color_col].apply(lambda x: abs(x) + 10),
            color=df[color_col],
            colorscale=[[0, 'rgb(0,0,255)'], [0.5, 'rgb(128,0,128)'], [1, 'rgb(255,0,0)']],
            cmin=-20, cmax=50,
            colorbar=dict(title="Temperature (°C)", thickness=15, len=0.7),
            line=dict(width=1, color='white')
        ),
        textfont=dict(size=10, color='white'),
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>%{marker.color:.1f}°C<extra></extra>'
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
        title=title, height=700,
        paper_bgcolor='rgb(0,0,0)', plot_bgcolor='rgb(0,0,0)',
        font=dict(color='white'), geo=dict(bgcolor='rgb(0,0,0)'),
        dragmode='pan'
    )
    return fig

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("🌐 Hermes Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Overview", "📈 Markets", "🛰️ Space", "🌍 Geography", "🌦️ Environment", "📰 News"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "🏠 Overview":
    st.title("🌐 Hermes Intelligence Platform")
    st.markdown("### Real-time Multi-Layer Intelligence Dashboard")
    st.markdown("---")
    
    # System metrics - helper function to safely get count
    def get_count(table):
        try:
            df = load_data(f'SELECT COUNT(*) as c FROM {table}')
            if df.empty:
                return 0
            # Handle different return formats from psycopg3/pandas
            if 'c' in df.columns:
                return int(df['c'].iloc[0])
            # Fallback: get first column, first row
            return int(df.iloc[0, 0])
        except Exception:
            return 0

    metrics = [
        ("📈 Stock Records", f"{get_count('stocks'):,}", None),
        ("☄️ NEO Records", f"{get_count('near_earth_objects'):,}", None),
        ("🌦️ Weather Records", f"{get_count('weather'):,}", None),
        ("📰 News Articles", f"{get_count('news'):,}", None)
    ]
    render_metric_row(metrics)
    
    st.markdown("---")
    
    # Latest stock prices
    st.subheader("📈 Latest Stock Prices")
    stocks = load_data("""
        SELECT symbol, price, change_percent as change
        FROM stocks WHERE timestamp = (SELECT MAX(timestamp) FROM stocks)
        ORDER BY symbol
    """)
    
    if not stocks.empty:
        stock_metrics = [(row['symbol'], f"${row['price']:.2f}", f"{row['change']:+.2f}%") 
                        for _, row in stocks.iterrows()]
        render_metric_row(stock_metrics, len(stocks))
    
    st.markdown("---")
    
    # ISS & Weather side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛰️ ISS Position")
        iss = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 1")
        if not iss.empty:
            st.write(f"**📍 Location:** {iss['latitude'][0]:.4f}°, {iss['longitude'][0]:.4f}°")
            st.write(f"**🚀 Altitude:** {iss['altitude'][0]:.2f} km")
            st.write(f"**⚡ Speed:** {iss['velocity'][0]:,.2f} km/h")
    
    with col2:
        st.subheader("🌦️ Weather Snapshot")
        weather = load_data("""
            SELECT city, temperature, description
            FROM weather WHERE timestamp = (SELECT MAX(timestamp) FROM weather)
            LIMIT 3
        """)
        for _, row in weather.iterrows():
            st.write(f"**{row['city']}:** {row['temperature']:.1f}°C - {row['description']}")
    
    st.markdown("---")
    
    # Latest news
    st.subheader("📰 Latest Headlines")
    news = load_data("SELECT source, title, published_at FROM news ORDER BY published_at DESC LIMIT 5")
    for _, row in news.iterrows():
        st.write(f"**[{row['source']}]** {row['title']}")
        st.caption(str(row['published_at']))

# ============================================================================
# PAGE: MARKETS
# ============================================================================

elif page == "📈 Markets":
    st.title("📈 Stock Market Analysis")
    st.markdown("---")

    stocks_df = load_data("SELECT * FROM stocks ORDER BY timestamp, symbol")

    if stocks_df.empty:
        st.warning("No stock data available")
    else:
        stocks_df['timestamp'] = pd.to_datetime(stocks_df['timestamp'])
        selected_symbol = st.selectbox("Select Stock:", stocks_df['symbol'].unique())
        symbol_df = stocks_df[stocks_df['symbol'] == selected_symbol].copy()

        # Metrics
        latest = symbol_df.iloc[-1]
        prev = symbol_df.iloc[-2] if len(symbol_df) > 1 else latest
        change = latest.get('change_percent', 0) or 0

        metrics = [
            ("Current Price", f"${latest['price']:.2f}" if latest['price'] else "N/A", f"{change:+.2f}%"),
            ("Change", f"${latest.get('change', 0) or 0:.2f}", None),
            ("Volume", f"{latest.get('volume', 0) or 0:,.0f}", None),
            ("Avg Volume", f"{symbol_df['volume'].mean():,.0f}" if symbol_df['volume'].notna().any() else "N/A", None)
        ]
        render_metric_row(metrics)

        st.markdown("---")

        # Price history line chart (replacing candlestick since we don't have OHLC data)
        st.subheader(f"{selected_symbol} Price History")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=symbol_df['timestamp'],
            y=symbol_df['price'],
            mode='lines+markers',
            name=selected_symbol
        ))
        fig.update_layout(xaxis_title="Date", yaxis_title="Price (USD)", height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Volume
        if symbol_df['volume'].notna().any():
            st.subheader("Trading Volume")
            fig_vol = px.bar(symbol_df, x='timestamp', y='volume')
            fig_vol.update_layout(height=300)
            st.plotly_chart(fig_vol, use_container_width=True)

        # Comparison
        st.markdown("---")
        st.subheader("Compare All Stocks")
        fig_comp = create_comparison_chart(
            stocks_df, 'timestamp', 'price', 'symbol',
            "Normalized Stock Performance (Base 100)", normalize=True
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ============================================================================
# PAGE: SPACE
# ============================================================================

elif page == "🛰️ Space":
    st.title("🛰️ Space Intelligence")
    st.markdown("---")
    
    # ISS Tracker
    st.subheader("International Space Station")
    iss_df = load_data("SELECT * FROM iss_positions ORDER BY timestamp DESC LIMIT 100")
    
    if not iss_df.empty:
        latest = iss_df.iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure(go.Scattergeo(
                lon=[latest['longitude']], lat=[latest['latitude']],
                mode='markers+text', marker=dict(size=15, color='red'),
                text=['ISS'], textposition="top center"
            ))
            fig.update_layout(
                title="Current ISS Position",
                geo=dict(projection_type='natural earth', showland=True, 
                        landcolor='lightgreen', showocean=True, oceancolor='lightblue'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            metrics = [
                ("📍 Latitude", f"{latest['latitude']:.4f}°", None),
                ("📍 Longitude", f"{latest['longitude']:.4f}°", None),
                ("🚀 Altitude", f"{latest['altitude']:.2f} km", None),
                ("⚡ Speed", f"{latest['velocity']:,.0f} km/h", None)
            ]
            for label, value, _ in metrics:
                st.metric(label, value)
            st.caption(f"Updated: {latest['timestamp']}")
    
    st.markdown("---")
    
    # Near-Earth Objects
    st.subheader("☄️ Near-Earth Objects")
    neo_df = load_data("""
        SELECT name, 
               ROUND((estimated_diameter_max/1000.0)::numeric, 3) as max_diameter_km,
               ROUND(relative_velocity::numeric, 0) as velocity_kmh,
               ROUND(miss_distance::numeric, 0) as miss_distance_km,
               is_potentially_hazardous, date
        FROM near_earth_objects
        WHERE date >= CURRENT_DATE
        ORDER BY date LIMIT 20
    """)
    
    if not neo_df.empty:
        neo_df['is_potentially_hazardous'] = neo_df['is_potentially_hazardous'].apply(lambda x: '⚠️ YES' if x else '✅ No')
        st.dataframe(neo_df, use_container_width=True, hide_index=True)
        
        fig = px.scatter(neo_df, x='date', y='max_diameter_km', size='max_diameter_km',
                        color='is_potentially_hazardous', hover_data=['name', 'velocity_kmh'],
                        title="Upcoming Near-Earth Objects")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No upcoming NEO data")
    
    st.markdown("---")
    
    # Solar Activity
    st.subheader("☀️ Solar Activity")
    solar_df = load_data("""
        SELECT class_type, begin_time, peak_time, source_location
        FROM solar_flares
        WHERE begin_time >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY begin_time DESC
    """)
    
    if not solar_df.empty:
        st.dataframe(solar_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent solar activity")

# ============================================================================
# PAGE: GEOGRAPHY
# ============================================================================

elif page == "🌍 Geography":
    st.title("🌍 Country Intelligence")
    st.markdown("---")
    
    try:
        countries_df = load_data("""
            SELECT name, code, region, subregion, population, area,
                   capital, languages, currencies,
                   latitude, longitude
            FROM countries ORDER BY population DESC
        """)
        
        if countries_df.empty:
            st.warning("No country data. Run: `python services/geography/fetch_country_data.py`")
        else:
            # Stats
            metrics = [
                ("🗺️ Countries", f"{len(countries_df):,}", None),
                ("👥 Total Population", f"{countries_df['population'].sum():,.0f}", None),
                ("📊 Avg Area", f"{countries_df['area'].mean():,.0f} km²", None),
                ("🌍 Regions", f"{countries_df['region'].nunique()}", None)
            ]
            render_metric_row(metrics)
            
            st.markdown("---")
            
            # Filter
            regions = ['All'] + sorted(countries_df['region'].dropna().unique().tolist())
            selected_region = st.selectbox("Region:", regions)
            filtered = countries_df if selected_region == 'All' else countries_df[countries_df['region'] == selected_region]
            
            st.markdown("---")
            
            # Map
            st.subheader("🌐 Country Map")
            map_data = filtered[['name', 'latitude', 'longitude', 'population']].dropna(subset=['latitude', 'longitude'])
            
            if not map_data.empty:
                fig = go.Figure(go.Scattergeo(
                    lon=map_data['longitude'], lat=map_data['latitude'],
                    text=map_data['name'], mode='markers',
                    marker=dict(
                        size=map_data['population'].apply(lambda x: min(max(x/5_000_000, 5), 30)),
                        color=map_data['population'], colorscale='Viridis',
                        showscale=True, colorbar=dict(title="Population")
                    ),
                    hovertemplate='<b>%{text}</b><br>Pop: %{marker.color:,.0f}<extra></extra>'
                ))
                fig.update_geos(projection_type='natural earth', showcountries=True, 
                               showland=True, landcolor='white', showocean=True, oceancolor='lightblue')
                fig.update_layout(title='Countries by Population', height=600)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Top charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 Top by Population")
                top_pop = filtered.nlargest(10, 'population')
                fig = px.bar(top_pop, x='name', y='population', color='population', 
                            color_continuous_scale='Blues')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Top by Area")
                top_area = filtered.nlargest(10, 'area')
                fig = px.bar(top_area, x='name', y='area', 
                            color='area', color_continuous_scale='Greens')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Country profile
            st.subheader("🗂️ Country Profile")
            selected = st.selectbox("Select country:", sorted(filtered['name'].tolist()))
            
            if selected:
                country = filtered[filtered['name'] == selected].iloc[0]
                
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.markdown(f"### {country['name']}")
                    st.caption(country['code'])
                
                with col2:
                    st.write(f"**Region:** {country['region']} - {country['subregion']}")
                    st.write(f"**Capital:** {country['capital']}")
                
                with col3:
                    st.metric("Population", f"{country['population']:,.0f}")
                    st.metric("Area", f"{country['area']:,.0f} km²")
    
    except Exception as e:
        st.error(f"Error: {e}")

# ============================================================================
# PAGE: ENVIRONMENT
# ============================================================================

elif page == "🌦️ Environment":
    st.title("🌦️ Environmental Monitoring")
    st.markdown("---")
    
    weather_df = load_data("SELECT * FROM weather ORDER BY timestamp DESC")
    
    if weather_df.empty:
        st.warning("No weather data")
    else:
        # Add coordinates
        weather_df['lat'] = weather_df['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lat', 0))
        weather_df['lon'] = weather_df['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lon', 0))
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'], errors='coerce', utc=True)
        
        latest = weather_df.groupby('city').first().reset_index()
        latest['h3'] = latest.apply(
            lambda row: h3.latlng_to_cell(row['lat'], row['lon'], 4) if row['lat'] != 0 else None, 
            axis=1
        )
        latest = latest[latest['h3'].notna()]
        
        # City selector
        selected_cities = st.multiselect("Cities:", latest['city'].tolist(), 
                                        default=latest['city'].tolist()[:10])  # Default to first 10
        filtered = latest[latest['city'].isin(selected_cities)]
        
        if not filtered.empty:
            st.markdown("---")
            
            # 3D Globe
            st.subheader("🌐 Weather Globe")
            fig = create_globe_map(filtered, 'lat', 'lon', 'temperature', 'city',
                                  '🌍 Global Weather - 3D Sphere View')
            st.plotly_chart(fig, use_container_width=True)
            st.info("🌍 **Controls:** Drag to rotate | Scroll to zoom")
            
            st.markdown("---")
            
            # Weather cards
            st.subheader("📊 Current Conditions")
            cols = st.columns(min(3, len(filtered)))
            for idx, (col, (_, row)) in enumerate(zip(cols * 10, filtered.iterrows())):
                with col:
                    st.markdown(f"### {row['city']}")
                    st.metric("Temperature", f"{row['temperature']:.1f}°C")
                    st.write(f"**Feels like:** {row['feels_like']:.1f}°C")
                    st.write(f"**Conditions:** {row['description']}")
                    st.write(f"**Humidity:** {row['humidity']}%")
            
            st.markdown("---")
            
            # Temperature trends
            st.subheader("📈 Temperature Trends")
            fig = go.Figure()
            for city in selected_cities:
                city_data = weather_df[weather_df['city'] == city]
                fig.add_trace(go.Scatter(x=city_data['timestamp'], 
                                        y=city_data['temperature'],
                                        name=city, mode='lines+markers'))
            fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)", 
                            height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: NEWS
# ============================================================================

elif page == "📰 News":
    st.title("📰 News Intelligence")
    st.markdown("---")
    
    news_df = load_data("SELECT * FROM news ORDER BY published_at DESC")
    
    if news_df.empty:
        st.warning("No news data")
    else:
        # Filter
        sources = ['All'] + sorted(news_df['source'].unique().tolist())
        selected_source = st.selectbox("Source:", sources)
        filtered = news_df if selected_source == 'All' else news_df[news_df['source'] == selected_source]
        
        st.write(f"**{len(filtered)} articles**")
        st.markdown("---")
        
        # Articles
        for _, article in filtered.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(article['title'])
                if pd.notna(article['description']) and article['description']:
                    st.write(article['description'])
                st.markdown(f"[Read more →]({article['url']})")
            with col2:
                st.write(f"**{article['source']}**")
                st.caption(str(article['published_at']))
            st.markdown("---")
        
        # Distribution
        st.subheader("Articles by Source")
        source_counts = news_df['source'].value_counts().reset_index()
        source_counts.columns = ['source', 'count']
        fig = px.bar(source_counts, x='source', y='count')
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Hermes Intelligence Platform**")
st.sidebar.caption("Multi-layer intelligence system")
