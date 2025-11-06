"""
Earthquake Data Collector
Fetches recent earthquake data from USGS and saves to PostgreSQL
No API key required!
"""

import requests
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for database import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EarthquakeDataCollector:
    """Collector for earthquake data from USGS"""
    
    def __init__(self):
        # USGS Earthquake API - FREE, no key needed!
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_recent_earthquakes(self, 
                                 min_magnitude: float = 4.5,
                                 days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Fetch recent significant earthquakes
        
        Args:
            min_magnitude: Minimum earthquake magnitude (default: 4.5)
            days: Number of days to look back (default: 7)
            
        Returns:
            Dictionary containing earthquake data or None if failed
        """
        # Calculate date range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%d'),
            'endtime': end_time.strftime('%Y-%m-%d'),
            'minmagnitude': min_magnitude,
            'orderby': 'time'
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching earthquakes >= {min_magnitude} magnitude "
                          f"from last {days} days (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                earthquake_count = len(data.get('features', []))
                logger.info(f"✓ Successfully fetched {earthquake_count} earthquakes")
                
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def save_to_database(self, earthquakes_data: Dict[str, Any]) -> int:
        """
        Save earthquake data to PostgreSQL database
        
        Args:
            earthquakes_data: GeoJSON data from USGS
            
        Returns:
            Number of earthquakes saved
        """
        saved_count = 0
        
        try:
            features = earthquakes_data.get('features', [])
            
            for feature in features:
                try:
                    properties = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    coordinates = geometry.get('coordinates', [])
                    
                    if len(coordinates) < 3:
                        continue
                    
                    # Extract data
                    earthquake_id = feature.get('id')
                    
                    # Parse timestamp (milliseconds since epoch)
                    timestamp_ms = properties.get('time')
                    timestamp = datetime.fromtimestamp(timestamp_ms / 1000.0) if timestamp_ms else None
                    
                    earthquake_data = {
                        'earthquake_id': earthquake_id,
                        'magnitude': float(properties.get('mag', 0)),
                        'place': properties.get('place', 'Unknown'),
                        'timestamp': timestamp,
                        'latitude': float(coordinates[1]),
                        'longitude': float(coordinates[0]),
                        'depth_km': float(coordinates[2]),
                        'magnitude_type': properties.get('magType', 'Unknown'),
                        'event_type': properties.get('type', 'earthquake'),
                        'tsunami': properties.get('tsunami', 0) == 1,
                        'significance': int(properties.get('sig', 0)),
                        'url': properties.get('url', '')
                    }
                    
                    # Insert into database
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO earthquakes 
                                (earthquake_id, magnitude, place, timestamp, latitude, longitude,
                                 depth_km, magnitude_type, event_type, tsunami, significance, url)
                                VALUES (%(earthquake_id)s, %(magnitude)s, %(place)s, %(timestamp)s,
                                        %(latitude)s, %(longitude)s, %(depth_km)s, %(magnitude_type)s,
                                        %(event_type)s, %(tsunami)s, %(significance)s, %(url)s)
                                ON CONFLICT (earthquake_id) DO UPDATE SET
                                    magnitude = EXCLUDED.magnitude,
                                    place = EXCLUDED.place,
                                    timestamp = EXCLUDED.timestamp,
                                    latitude = EXCLUDED.latitude,
                                    longitude = EXCLUDED.longitude,
                                    depth_km = EXCLUDED.depth_km,
                                    significance = EXCLUDED.significance,
                                    collected_at = CURRENT_TIMESTAMP
                            """, earthquake_data)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save earthquake {feature.get('id')}: {e}")
                    continue
            
            logger.info(f"✓ Saved {saved_count} earthquake records to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process earthquake data: {e}")
            return saved_count

def main():
    """Main execution function"""
    logger.info("=== Earthquake Data Collection ===\n")
    
    collector = EarthquakeDataCollector()
    
    # Fetch significant earthquakes from past 7 days (magnitude 4.5+)
    logger.info("Collecting earthquakes (magnitude 4.5+) from past 7 days")
    data = collector.fetch_recent_earthquakes(min_magnitude=4.5, days=7)
    
    if data:
        logger.info("Earthquake data collection successful")
        
        # Save to database
        saved = collector.save_to_database(data)
        
        # Display results
        features = data.get('features', [])
        
        print(f"\n=== Earthquake Data Collection ===")
        print(f"Total earthquakes found: {len(features)}")
        print(f"Saved to database: {saved}")
        
        if features:
            print(f"\n🌍 Recent Significant Earthquakes:")
            
            # Sort by magnitude (descending)
            sorted_features = sorted(features, 
                                    key=lambda x: x['properties'].get('mag', 0), 
                                    reverse=True)
            
            for feature in sorted_features[:10]:  # Show top 10
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                mag = props.get('mag', 0)
                place = props.get('place', 'Unknown')
                tsunami_warning = " 🌊 TSUNAMI" if props.get('tsunami') == 1 else ""
                
                print(f"  {'🔴' if mag >= 6.0 else '🟡' if mag >= 5.0 else '🟢'} "
                      f"M{mag:.1f} - {place}{tsunami_warning}")
        
        return data
    else:
        logger.error("Earthquake data collection failed")
        return None

if __name__ == "__main__":
    main()
