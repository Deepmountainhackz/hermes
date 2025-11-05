# City coordinates for weather visualization
# 50 major cities worldwide

CITY_COORDS = {
    # NORTH AMERICA
    'New York': {'lat': 40.7128, 'lon': -74.0060},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298},
    'Toronto': {'lat': 43.6532, 'lon': -79.3832},
    'Mexico City': {'lat': 19.4326, 'lon': -99.1332},
    'Miami': {'lat': 25.7617, 'lon': -80.1918},
    'Vancouver': {'lat': 49.2827, 'lon': -123.1207},
    'San Francisco': {'lat': 37.7749, 'lon': -122.4194},
    
    # SOUTH AMERICA
    'São Paulo': {'lat': -23.5505, 'lon': -46.6333},
    'Rio de Janeiro': {'lat': -22.9068, 'lon': -43.1729},
    'Buenos Aires': {'lat': -34.6037, 'lon': -58.3816},
    'Lima': {'lat': -12.0464, 'lon': -77.0428},
    'Bogotá': {'lat': 4.7110, 'lon': -74.0721},
    'Santiago': {'lat': -33.4489, 'lon': -70.6693},
    
    # EUROPE
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
    
    # MIDDLE EAST & AFRICA
    'Dubai': {'lat': 25.2048, 'lon': 55.2708},
    'Cairo': {'lat': 30.0444, 'lon': 31.2357},
    'Tel Aviv': {'lat': 32.0853, 'lon': 34.7818},
    'Riyadh': {'lat': 24.7136, 'lon': 46.6753},
    'Johannesburg': {'lat': -26.2041, 'lon': 28.0473},
    'Cape Town': {'lat': -33.9249, 'lon': 18.4241},
    'Nairobi': {'lat': -1.2921, 'lon': 36.8219},
    'Lagos': {'lat': 6.5244, 'lon': 3.3792},
    
    # ASIA
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
    
    # OCEANIA
    'Sydney': {'lat': -33.8688, 'lon': 151.2093},
    'Melbourne': {'lat': -37.8136, 'lon': 144.9631},
    'Auckland': {'lat': -36.8485, 'lon': 174.7633},
    'Perth': {'lat': -31.9505, 'lon': 115.8605},
    'Brisbane': {'lat': -27.4698, 'lon': 153.0251}
}

def get_city_coord(city_name, coord_type='lat'):
    """Get latitude or longitude for a city"""
    city = CITY_COORDS.get(city_name, {})
    return city.get(coord_type, 0)

def get_all_cities():
    """Get list of all available cities"""
    return list(CITY_COORDS.keys())

def get_cities_by_region():
    """Get cities grouped by region"""
    return {
        'North America': list(CITY_COORDS.keys())[:8],
        'South America': list(CITY_COORDS.keys())[8:14],
        'Europe': list(CITY_COORDS.keys())[14:24],
        'Middle East & Africa': list(CITY_COORDS.keys())[24:32],
        'Asia': list(CITY_COORDS.keys())[32:45],
        'Oceania': list(CITY_COORDS.keys())[45:50]
    }
