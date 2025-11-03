import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import h3
import pydeck as pdk

# Page config
st.set_page_config(
    page_title="Hermes Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('hermes.db', check_same_thread=False)

def load_data(query):
    conn = get_connection()
    df = pd.read_sql_query(query, conn)
    return df

# City coordinates (add these to your database eventually)
CITY_COORDS = {
    'Dubai': {'lat': 25.2048, 'lon': 55.2708},
    'London': {'lat': 51.5074, 'lon': -0.1278},
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Tokyo': {'lat': 35.6762, 'lon': 139.6503},
    'Sydney': {'lat': -33.8688, 'lon': 151.2093},
    'Paris': {'lat': 48.8566, 'lon': 2.3522},
    'Berlin': {'lat': 52.5200, 'lon': 13.4050},
    'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
    'Singapore': {'lat': 1.3521, 'lon': 103.8198},
    'São Paulo': {'lat': -23.5505, 'lon': -46.6333}
}

# Sidebar
st.sidebar.title("🌐 Hermes Intelligence")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["🏠 Overview", "📈 Markets", "🛰️ Space", "🌦️ Environment", "📰 News"]
)

st.sidebar.markdown("---")
st.sidebar.info("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ============================================================================
# OVERVIEW PAGE
# ============================================================================
if page == "🏠 Overview":
    st.title("🌐 Hermes Intelligence Platform")
    st.markdown("### Real-time Multi-Layer Intelligence Dashboard")
    st.markdown("---")
    
    # Database stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stock_count = load_data("SELECT COUNT(*) as count FROM stocks")['count'][0]
        st.metric("📈 Stock Records", f"{stock_count:,}")
    
    with col2:
        neo_count = load_data("SELECT COUNT(*) as count FROM near_earth_objects")['count'][0]
        st.metric("☄️ NEO Records", f"{neo_count:,}")
    
    with col3:
        weather_count = load_data("SELECT COUNT(*) as count FROM weather")['count'][0]
        st.metric("🌦️ Weather Records", f"{weather_count:,}")
    
    with col4:
        news_count = load_data("SELECT COUNT(*) as count FROM news")['count'][0]
        st.metric("📰 News Articles", f"{news_count:,}")
    
    st.markdown("---")
    
    # Latest Stock Prices
    st.subheader("📈 Latest Stock Prices")
    stocks_query = """
    SELECT 
        symbol,
        date,
        close as price,
        ROUND(((close - open) / open * 100), 2) as daily_change
    FROM stocks
    WHERE date = (SELECT MAX(date) FROM stocks)
    ORDER BY symbol
    """
    stocks_df = load_data(stocks_query)
    
    if not stocks_df.empty:
        cols = st.columns(len(stocks_df))
        for idx, (col, row) in enumerate(zip(cols, stocks_df.iterrows())):
            with col:
                change = row[1]['daily_change']
                st.metric(
                    row[1]['symbol'],
                    f"${row[1]['price']:.2f}",
                    f"{change:+.2f}%"
                )
    
    st.markdown("---")
    
    # ISS Position
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🛰️ ISS Current Position")
        iss_query = """
        SELECT latitude, longitude, altitude_km, speed_kmh, timestamp
        FROM iss_positions
        ORDER BY timestamp DESC
        LIMIT 1
        """
        iss_df = load_data(iss_query)
        
        if not iss_df.empty:
            st.write(f"**📍 Coordinates:** {iss_df['latitude'][0]:.4f}°, {iss_df['longitude'][0]:.4f}°")
            st.write(f"**🚀 Altitude:** {iss_df['altitude_km'][0]:.2f} km")
            st.write(f"**⚡ Speed:** {iss_df['speed_kmh'][0]:,.2f} km/h")
            st.write(f"**🕐 Updated:** {iss_df['timestamp'][0]}")
    
    with col2:
        st.subheader("🌦️ Current Weather")
        weather_query = """
        SELECT city, temperature_c, weather_description
        FROM weather
        WHERE timestamp = (SELECT MAX(timestamp) FROM weather)
        ORDER BY city
        LIMIT 3
        """
        weather_df = load_data(weather_query)
        
        if not weather_df.empty:
            for _, row in weather_df.iterrows():
                st.write(f"**{row['city']}:** {row['temperature_c']:.1f}°C - {row['weather_description']}")
    
    st.markdown("---")
    
    # Latest News
    st.subheader("📰 Latest Headlines")
    news_query = """
    SELECT source, title, published
    FROM news
    ORDER BY published DESC
    LIMIT 5
    """
    news_df = load_data(news_query)
    
    if not news_df.empty:
        for _, row in news_df.iterrows():
            st.write(f"**[{row['source']}]** {row['title']}")
            st.caption(row['published'])

# ============================================================================
# MARKETS PAGE
# ============================================================================
elif page == "📈 Markets":
    st.title("📈 Stock Market Analysis")
    st.markdown("---")
    
    # Get all stock data
    stocks_query = """
    SELECT symbol, date, open, high, low, close, volume
    FROM stocks
    ORDER BY date, symbol
    """
    stocks_df = load_data(stocks_query)
    stocks_df['date'] = pd.to_datetime(stocks_df['date'])
    
    if stocks_df.empty:
        st.warning("No stock data available")
    else:
        # Stock selector
        symbols = stocks_df['symbol'].unique()
        selected_symbol = st.selectbox("Select Stock:", symbols)
        
        # Filter data for selected stock
        symbol_df = stocks_df[stocks_df['symbol'] == selected_symbol].copy()
        
        # Calculate metrics
        latest_price = symbol_df.iloc[-1]['close']
        prev_price = symbol_df.iloc[-2]['close'] if len(symbol_df) > 1 else latest_price
        price_change = latest_price - prev_price
        price_change_pct = (price_change / prev_price * 100) if prev_price != 0 else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${latest_price:.2f}", f"{price_change_pct:+.2f}%")
        with col2:
            st.metric("High", f"${symbol_df['high'].max():.2f}")
        with col3:
            st.metric("Low", f"${symbol_df['low'].min():.2f}")
        with col4:
            st.metric("Avg Volume", f"{symbol_df['volume'].mean():,.0f}")
        
        st.markdown("---")
        
        # Price chart
        st.subheader(f"{selected_symbol} Price History")
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=symbol_df['date'],
            open=symbol_df['open'],
            high=symbol_df['high'],
            low=symbol_df['low'],
            close=symbol_df['close'],
            name=selected_symbol
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        st.subheader("Trading Volume")
        fig_volume = px.bar(
            symbol_df,
            x='date',
            y='volume',
            title=f"{selected_symbol} Trading Volume"
        )
        fig_volume.update_layout(height=300)
        st.plotly_chart(fig_volume, use_container_width=True)
        
        # Comparison chart
        st.markdown("---")
        st.subheader("Compare All Stocks")
        
        # Normalize prices to show percentage change
        comparison_df = stocks_df.pivot(index='date', columns='symbol', values='close')
        comparison_df_norm = (comparison_df / comparison_df.iloc[0] * 100)
        
        fig_comparison = go.Figure()
        for symbol in symbols:
            fig_comparison.add_trace(go.Scatter(
                x=comparison_df_norm.index,
                y=comparison_df_norm[symbol],
                name=symbol,
                mode='lines'
            ))
        
        fig_comparison.update_layout(
            title="Normalized Stock Performance (Base 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)

# ============================================================================
# SPACE PAGE
# ============================================================================
elif page == "🛰️ Space":
    st.title("🛰️ Space Intelligence")
    st.markdown("---")
    
    # ISS Tracker
    st.subheader("International Space Station Tracker")
    
    iss_query = """
    SELECT latitude, longitude, altitude_km, speed_kmh, timestamp
    FROM iss_positions
    ORDER BY timestamp DESC
    LIMIT 100
    """
    iss_df = load_data(iss_query)
    
    if not iss_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Map
            latest_iss = iss_df.iloc[0]
            
            fig_map = go.Figure(go.Scattergeo(
                lon=[latest_iss['longitude']],
                lat=[latest_iss['latitude']],
                mode='markers+text',
                marker=dict(size=15, color='red'),
                text=['ISS'],
                textposition="top center"
            ))
            
            fig_map.update_layout(
                title="Current ISS Position",
                geo=dict(
                    projection_type='natural earth',
                    showland=True,
                    landcolor='lightgreen',
                    showocean=True,
                    oceancolor='lightblue'
                ),
                height=400
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
        
        with col2:
            st.metric("📍 Latitude", f"{latest_iss['latitude']:.4f}°")
            st.metric("📍 Longitude", f"{latest_iss['longitude']:.4f}°")
            st.metric("🚀 Altitude", f"{latest_iss['altitude_km']:.2f} km")
            st.metric("⚡ Speed", f"{latest_iss['speed_kmh']:,.2f} km/h")
            st.caption(f"Updated: {latest_iss['timestamp']}")
    
    st.markdown("---")
    
    # Near-Earth Objects
    st.subheader("☄️ Near-Earth Objects")
    
    neo_query = """
    SELECT 
        name,
        ROUND(diameter_min_m / 1000.0, 3) as min_diameter_km,
        ROUND(diameter_max_m / 1000.0, 3) as max_diameter_km,
        ROUND(velocity_kmh, 0) as velocity_kmh,
        ROUND(miss_distance_km, 0) as miss_distance_km,
        is_hazardous,
        date
    FROM near_earth_objects
    WHERE date(date) >= date('now')
    ORDER BY date ASC
    LIMIT 20
    """
    neo_df = load_data(neo_query)
    
    if not neo_df.empty:
        neo_df['is_hazardous'] = neo_df['is_hazardous'].apply(lambda x: '⚠️ YES' if x == 1 else '✅ No')
        st.dataframe(neo_df, use_container_width=True, hide_index=True)
        
        # NEO size distribution
        st.subheader("NEO Size Distribution")
        fig_neo = px.scatter(
            neo_df,
            x='date',
            y='max_diameter_km',
            size='max_diameter_km',
            color='is_hazardous',
            hover_data=['name', 'velocity_kmh', 'miss_distance_km'],
            title="Upcoming Near-Earth Objects"
        )
        st.plotly_chart(fig_neo, use_container_width=True)
    else:
        st.info("No upcoming NEO data available")
    
    st.markdown("---")
    
    # Solar Flares
    st.subheader("☀️ Solar Activity")
    
    solar_query = """
    SELECT class_type, begin_time, peak_time, source_location
    FROM solar_flares
    WHERE date(begin_time) >= date('now', '-30 days')
    ORDER BY begin_time DESC
    """
    solar_df = load_data(solar_query)
    
    if not solar_df.empty:
        st.dataframe(solar_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent solar flare activity detected (this is normal!)")

# ============================================================================
# ENVIRONMENT PAGE WITH H3 HEXAGONS
# ============================================================================
elif page == "🌦️ Environment":
    st.title("🌦️ Environmental Monitoring")
    st.markdown("### Interactive Global Weather Grid")
    st.markdown("---")
    
    weather_query = """
    SELECT 
        city,
        temperature_c,
        feels_like_c,
        temp_min_c,
        temp_max_c,
        humidity_percent,
        weather_main,
        weather_description,
        wind_speed_ms,
        clouds_percent,
        timestamp
    FROM weather
    ORDER BY timestamp DESC
    """
    weather_df = load_data(weather_query)
    
    if weather_df.empty:
        st.warning("No weather data available")
    else:
        # Add coordinates to weather data
        weather_df['lat'] = weather_df['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lat', 0))
        weather_df['lon'] = weather_df['city'].map(lambda x: CITY_COORDS.get(x, {}).get('lon', 0))
        
        # Fix datetime parsing
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'], errors='coerce', utc=True)
        
        # Get latest weather for each city
        latest_weather = weather_df.groupby('city').first().reset_index()
        
        # Convert to H3 hexagons (resolution 4 = ~22km edge)
        # Using h3 v4.x API (latlng_to_cell is the new function name)
        # H3 Resolution Guide:
        # - 0: ~1,107 km (continents)
        # - 4: ~22 km (cities) ← WE'RE HERE
        # - 6: ~3.2 km (neighborhoods)
        # - 8: ~461 m (blocks)
        latest_weather['h3'] = latest_weather.apply(
            lambda row: h3.latlng_to_cell(row['lat'], row['lon'], 4) if row['lat'] != 0 else None,
            axis=1
        )
        
        # Remove any rows where H3 conversion failed
        latest_weather = latest_weather[latest_weather['h3'].notna()]
        
        # Region selector
        st.subheader("🗺️ Select Regions to Display")
        all_cities = latest_weather['city'].tolist()
        selected_cities = st.multiselect(
            "Choose cities:",
            options=all_cities,
            default=all_cities
        )
        
        # Filter data
        filtered_weather = latest_weather[latest_weather['city'].isin(selected_cities)]
        
        if not filtered_weather.empty:
            st.markdown("---")
            
            # Create H3 Hexagon Map
            st.subheader("🌐 Interactive Weather Grid (H3 Hexagons)")
            
            # Prepare data for H3HexagonLayer (for globe view)
            hex_layer_data = []
            for _, row in filtered_weather.iterrows():
                # Normalize temperature for color (0-50°C range)
                temp_norm = min(max(row['temperature_c'], -20), 50)
                # Red for hot, blue for cold
                red = int(255 * ((temp_norm + 20) / 70))
                blue = int(255 * (1 - (temp_norm + 20) / 70))
                
                hex_layer_data.append({
                    'hex': row['h3'],
                    'temperature': row['temperature_c'],
                    'city': row['city'],
                    'humidity': row['humidity_percent'],
                    'description': row['weather_description'],
                    'count': 1,
                    'color': [red, 150, blue, 200]
                })
            
            hex_layer_df = pd.DataFrame(hex_layer_data)
            
            # Create H3HexagonLayer for proper globe rendering
            layer = pdk.Layer(
                'H3HexagonLayer',
                hex_layer_df,
                get_hexagon='hex',
                get_fill_color='color',
                get_line_color=[255, 255, 255, 100],
                line_width_min_pixels=1,
                pickable=True,
                auto_highlight=True,
                elevation_scale=50000,
                extruded=True,
                coverage=1,
                get_elevation='temperature * 1000'
            )
            
            # Set view state for GLOBE perspective
            view_state = pdk.ViewState(
                latitude=30,
                longitude=0,
                zoom=0.8,  # Zoomed out to see full globe
                pitch=0,    # Top-down view initially
                bearing=0,
                min_zoom=0,
                max_zoom=10
            )
            
            # Create deck with GLOBE view (single world, no wrapping)
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={
                    'html': '<b>{city}</b><br/>🌡️ {temperature}°C<br/>💧 {humidity}%<br/>{description}',
                    'style': {
                        'backgroundColor': 'rgba(0, 0, 0, 0.8)',
                        'color': 'white',
                        'fontSize': '14px',
                        'padding': '10px'
                    }
                },
                map_style='https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json',
                parameters={
                    'renderWorldCopies': False  # Don't repeat the world!
                }
            )
            
            st.pydeck_chart(deck)
            
            st.info("🌍 **Globe Controls:** Click and drag to rotate | Scroll to zoom | Shift+drag to tilt | Red = hot, Blue = cold")

            
            st.markdown("---")
            
            # Weather Cards
            st.subheader("📊 Current Conditions")
            
            cols = st.columns(min(3, len(filtered_weather)))
            for idx, (col, (_, row)) in enumerate(zip(cols * 10, filtered_weather.iterrows())):
                with col:
                    st.markdown(f"### {row['city']}")
                    st.metric("Temperature", f"{row['temperature_c']:.1f}°C")
                    st.write(f"**Feels like:** {row['feels_like_c']:.1f}°C")
                    st.write(f"**Conditions:** {row['weather_description']}")
                    st.write(f"**Humidity:** {row['humidity_percent']}%")
                    st.write(f"**Wind:** {row['wind_speed_ms']} m/s")
                    st.caption(f"H3: {row['h3'][:8]}...")
            
            st.markdown("---")
            
            # Temperature Trends
            st.subheader("📈 Temperature Trends")
            
            fig_temp = go.Figure()
            
            for city in selected_cities:
                city_data = weather_df[weather_df['city'] == city]
                fig_temp.add_trace(go.Scatter(
                    x=city_data['timestamp'],
                    y=city_data['temperature_c'],
                    name=city,
                    mode='lines+markers'
                ))
            
            fig_temp.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Humidity comparison
            st.subheader("💧 Humidity Comparison")
            
            fig_humidity = px.bar(
                filtered_weather,
                x='city',
                y='humidity_percent',
                title="Current Humidity by City",
                labels={'humidity_percent': 'Humidity (%)'},
                color='humidity_percent',
                color_continuous_scale='Blues'
            )
            fig_humidity.update_layout(height=300)
            st.plotly_chart(fig_humidity, use_container_width=True)
            
        else:
            st.warning("Please select at least one city to display data.")

# ============================================================================
# NEWS PAGE
# ============================================================================
elif page == "📰 News":
    st.title("📰 News Intelligence")
    st.markdown("---")
    
    news_query = """
    SELECT source, title, summary, link, published
    FROM news
    ORDER BY published DESC
    """
    news_df = load_data(news_query)
    
    if news_df.empty:
        st.warning("No news data available")
    else:
        # Source filter
        sources = ['All'] + sorted(news_df['source'].unique().tolist())
        selected_source = st.selectbox("Filter by Source:", sources)
        
        if selected_source != 'All':
            filtered_news = news_df[news_df['source'] == selected_source]
        else:
            filtered_news = news_df
        
        st.write(f"**Showing {len(filtered_news)} articles**")
        st.markdown("---")
        
        # Display news articles
        for _, article in filtered_news.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.subheader(article['title'])
                    if pd.notna(article['summary']) and article['summary']:
                        st.write(article['summary'])
                    st.markdown(f"[Read more →]({article['link']})")
                
                with col2:
                    st.write(f"**{article['source']}**")
                    st.caption(article['published'])
                
                st.markdown("---")
        
        # News distribution by source
        st.subheader("Articles by Source")
        source_counts = news_df['source'].value_counts().reset_index()
        source_counts.columns = ['source', 'count']
        
        fig_sources = px.bar(
            source_counts,
            x='source',
            y='count',
            title="Article Distribution by News Source"
        )
        st.plotly_chart(fig_sources, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Hermes Intelligence Platform**")
st.sidebar.caption("Multi-layer data collection and analysis")
