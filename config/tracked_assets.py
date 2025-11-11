TRACKED_STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'JPM', 'GS', 
    'CVX', 'JNJ', 'UNH', 'PG', 'V', 'WMT', 'XOM'
]

TRACKED_COMMODITIES = [
    {'symbol': 'CL=F', 'name': 'WTI Crude Oil'},
    {'symbol': 'BZ=F', 'name': 'Brent Crude Oil'},
    {'symbol': 'NG=F', 'name': 'Natural Gas'},
    {'symbol': 'GC=F', 'name': 'Gold'},
    {'symbol': 'SI=F', 'name': 'Silver'},
    {'symbol': 'HG=F', 'name': 'Copper'},
]

TRACKED_FOREX_PAIRS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 
    'AUDUSD=X', 'USDCAD=X'
]

TRACKED_ECONOMIC_INDICATORS = {
    'US': ['GDP', 'UNRATE', 'CPIAUCSL', 'FEDFUNDS', 'INDPRO']
}

TRACKED_WEATHER_CITIES = [
    {'name': 'New York', 'country': 'US', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'London', 'country': 'GB', 'lat': 51.5074, 'lon': -0.1278},
    {'name': 'Tokyo', 'country': 'JP', 'lat': 35.6762, 'lon': 139.6503},
]

TRACKED_CROPS = ['CORN', 'SOYBEANS', 'WHEAT', 'COTTON', 'RICE']

MAJOR_AG_REGIONS = {
    'US_Corn_Belt': {'lat': 41.5, 'lon': -93.5, 'name': 'US Corn Belt'},
    'Brazil_Cerrado': {'lat': -15.8, 'lon': -47.9, 'name': 'Brazilian Cerrado'},
}
