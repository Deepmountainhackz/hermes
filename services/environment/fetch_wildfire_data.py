"""
Wildfire Data Collector
Fetches active wildfire data from NASA EONET and saves to PostgreSQL
Uses geocoding to find coordinates when not provided
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
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

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

class WildfireDataCollector:
    """Collector for wildfire data from NASA EONET"""
    
    def __init__(self):
        # NASA EONET API - FREE, no key needed!
        self.base_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        # Initialize geocoder
        self.geocoder = Nominatim(user_agent="hermes-intelligence-platform")
        
    def extract_location_from_title(self, title: str) -> Optional[str]:
        """
        Extract geographic location from wildfire title
        
        Examples:
        "Bear River 9 Rx Prescribed Fire, Box Elder, Utah" → "Box Elder, Utah"
        "Lake Creek Wildfire, Blaine, Idaho" → "Blaine, Idaho"
        "SMR Unit 100/101 Rx 0911 Prescribed Fire, Wakulla, Florida" → "Wakulla, Florida"
        
        Args:
            title: Full wildfire title
            
        Returns:
            Extracted location or None
        """
        # Look for pattern: "Something, City, State"
        # Split by comma and take last 2 parts
        parts = [p.strip() for p in title.split(',')]
        
        if len(parts) >= 2:
            # Take last 2 parts (usually City, State)
            location = f"{parts[-2]}, {parts[-1]}"
            logger.info(f"Extracted location: '{location}' from '{title}'")
            return location
        
        logger.warning(f"Could not extract location from: {title}")
        return None
    
    def geocode_location(self, location_name: str) -> Optional[tuple]:
        """
        Geocode a location name to coordinates
        
        Args:
            location_name: Location name or description
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        try:
            logger.info(f"Geocoding location: {location_name}")
            
            # Try to geocode
            location = self.geocoder.geocode(location_name, timeout=10)
            
            if location:
                logger.info(f"✓ Geocoded to: {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            else:
                logger.warning(f"Could not geocode: {location_name}")
                return None
                
        except GeocoderTimedOut:
            logger.warning(f"Geocoding timeout for: {location_name}")
            return None
        except GeocoderServiceError as e:
            logger.error(f"Geocoding service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected geocoding error: {e}")
            return None
        
    def fetch_active_wildfires(self, days: int = 60) -> Optional[Dict[str, Any]]:
        """
        Fetch active wildfire events
        
        Args:
            days: Number of days to look back (default: 60)
            
        Returns:
            Dictionary containing wildfire data or None if failed
        """
        params = {
            'category': 'wildfires',
            'status': 'open',  # Only active fires
            'days': days
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching active wildfires from last {days} days "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                fire_count = len(data.get('events', []))
                logger.info(f"✓ Successfully fetched {fire_count} active wildfires")
                
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
    
    def save_to_database(self, wildfire_data: Dict[str, Any]) -> int:
        """
        Save wildfire data to PostgreSQL database
        
        Args:
            wildfire_data: Event data from NASA EONET
            
        Returns:
            Number of wildfires saved
        """
        saved_count = 0
        
        try:
            events = wildfire_data.get('events', [])
            
            for event in events:
                try:
                    fire_id = event.get('id')
                    title = event.get('title', 'Unknown Fire')
                    
                    logger.info(f"Processing wildfire: {title} (ID: {fire_id})")
                    
                    # Get latest coordinates
                    geometries = event.get('geometries', [])
                    latitude = None
                    longitude = None
                    
                    if geometries:
                        # Try to get coordinates from NASA data
                        latest_geometry = geometries[-1]
                        coordinates = latest_geometry.get('coordinates', [])
                        
                        if len(coordinates) >= 2:
                            latitude = float(coordinates[1])
                            longitude = float(coordinates[0])
                            logger.info(f"Using NASA coordinates: {latitude}, {longitude}")
                    
                    # If no coordinates from NASA, try geocoding the title
                    if latitude is None or longitude is None:
                        logger.warning(f"No geometries from NASA, attempting geocoding...")
                        
                        # Extract just the location (city, state) from title
                        location = self.extract_location_from_title(title)
                        
                        if location:
                            coords = self.geocode_location(location)
                            if coords:
                                latitude, longitude = coords
                            else:
                                logger.warning(f"Geocoding failed for: {location}")
                                continue
                        else:
                            logger.warning(f"Could not extract location from title")
                            continue
                    
                    # Parse date
                    date_str = ''
                    if geometries:
                        date_str = geometries[-1].get('date', '')
                    
                    try:
                        timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else None
                    except Exception as e:
                        logger.error(f"Date parsing error for {fire_id}: {e}")
                        timestamp = datetime.utcnow()
                    
                    # Get sources
                    sources = event.get('sources', [])
                    source_url = sources[0].get('url', '') if sources else ''
                    
                    # Check if closed
                    closed = event.get('closed')
                    status = 'closed' if closed else 'active'
                    
                    wildfire_data_record = {
                        'fire_id': str(fire_id),
                        'title': title[:500],
                        'timestamp': timestamp,
                        'latitude': latitude,
                        'longitude': longitude,
                        'status': status,
                        'source_url': source_url[:1000] if source_url else ''
                    }
                    
                    logger.info(f"Saving wildfire: {title} at ({latitude:.2f}, {longitude:.2f})")
                    
                    # Insert into database
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO wildfires 
                                (fire_id, title, timestamp, latitude, longitude, 
                                 status, source_url)
                                VALUES (%(fire_id)s, %(title)s, %(timestamp)s, %(latitude)s,
                                        %(longitude)s, %(status)s, %(source_url)s)
                                ON CONFLICT (fire_id) DO UPDATE SET
                                    title = EXCLUDED.title,
                                    timestamp = EXCLUDED.timestamp,
                                    latitude = EXCLUDED.latitude,
                                    longitude = EXCLUDED.longitude,
                                    status = EXCLUDED.status,
                                    collected_at = CURRENT_TIMESTAMP
                            """, wildfire_data_record)
                    
                    logger.info(f"✓ Successfully saved wildfire {fire_id}")
                    saved_count += 1
                    
                    # Rate limiting for geocoding (1 request per second)
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to save wildfire {event.get('id')}: {e}", exc_info=True)
                    continue
            
            logger.info(f"✓ Saved {saved_count} wildfire records to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process wildfire data: {e}", exc_info=True)
            return saved_count

def main():
    """Main execution function"""
    logger.info("=== Wildfire Data Collection ===\n")
    
    collector = WildfireDataCollector()
    
    # Fetch active wildfires from past 60 days
    logger.info("Collecting active wildfires")
    data = collector.fetch_active_wildfires(days=60)
    
    if data:
        logger.info("Wildfire data collection successful")
        
        # Save to database
        saved = collector.save_to_database(data)
        
        # Display results
        events = data.get('events', [])
        
        print(f"\n=== Wildfire Data Collection ===")
        print(f"Total active wildfires found: {len(events)}")
        print(f"Saved to database: {saved}")
        
        if saved > 0:
            print(f"\n🔥 Active Wildfires:")
            
            # Show saved wildfires
            saved_events = [e for e in events if e.get('geometries')]
            
            for event in saved_events[:15]:  # Show up to 15
                title = event.get('title', 'Unknown')
                geometries = event.get('geometries', [])
                
                if geometries:
                    latest = geometries[-1]
                    coords = latest.get('coordinates', [])
                    date = latest.get('date', 'Unknown date')
                    
                    if len(coords) >= 2:
                        print(f"  🔥 {title}")
                        print(f"     Location: {coords[1]:.2f}°N, {coords[0]:.2f}°E")
                        print(f"     Last updated: {date[:10]}")
        
        return data
    else:
        logger.error("Wildfire data collection failed")
        return None

if __name__ == "__main__":
    main()
