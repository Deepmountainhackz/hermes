"""
Storm and Severe Weather Data Collector with NOAA + JTWC Cross-Referencing
Fetches active storms from NASA EONET and cross-references with:
- NOAA NHC (Atlantic & Eastern Pacific)
- JTWC (Western Pacific, Indian Ocean, Southern Hemisphere)
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
import re
import xml.etree.ElementTree as ET

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

class StormDataCollector:
    """Collector for storm and severe weather data with multi-source cross-referencing"""
    
    def __init__(self):
        # NASA EONET API - FREE, no key needed!
        self.eonet_url = "https://eonet.gsfc.nasa.gov/api/v3/events"
        
        # NOAA National Hurricane Center - Atlantic & E. Pacific
        self.noaa_url = "https://www.nhc.noaa.gov/CurrentStorms.json"
        
        # JTWC (Joint Typhoon Warning Center) - W. Pacific, Indian Ocean
        self.jtwc_rss_url = "https://www.metoc.navy.mil/jtwc/rss/jtwc.rss"
        
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_noaa_active_storms(self) -> List[Dict[str, Any]]:
        """
        Fetch active storms from NOAA National Hurricane Center
        
        Returns:
            List of active storms with coordinates
        """
        try:
            logger.info("Fetching active storms from NOAA NHC (Atlantic/E. Pacific)...")
            
            response = requests.get(self.noaa_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            active_storms = data.get('activeStorms', [])
            
            logger.info(f"✓ Found {len(active_storms)} active storms in NOAA data")
            
            return active_storms
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch NOAA data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching NOAA data: {e}")
            return []
    
    def fetch_jtwc_active_storms(self) -> List[Dict[str, Any]]:
        """
        Fetch active storms from JTWC via RSS feed
        
        Returns:
            List of active storms with coordinates
        """
        try:
            logger.info("Fetching active storms from JTWC (W. Pacific/Indian Ocean)...")
            
            response = requests.get(self.jtwc_rss_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse RSS/XML
            root = ET.fromstring(response.content)
            
            storms = []
            
            # RSS structure: <rss><channel><item>...</item></channel></rss>
            for item in root.findall('.//item'):
                try:
                    title = item.find('title').text if item.find('title') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    
                    # Extract storm information from title/description
                    # JTWC format varies, but usually includes coordinates in description
                    
                    # Try to extract coordinates from description
                    # Format example: "15.8N 120.5E" or "15.8°N 120.5°E"
                    coords = self.extract_coordinates_from_text(description)
                    
                    if coords and title:
                        storm_data = {
                            'name': title,
                            'latitude': coords[0],
                            'longitude': coords[1],
                            'description': description
                        }
                        storms.append(storm_data)
                        
                except Exception as e:
                    logger.warning(f"Error parsing JTWC storm item: {e}")
                    continue
            
            logger.info(f"✓ Found {len(storms)} active storms in JTWC data")
            
            return storms
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch JTWC data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching JTWC data: {e}")
            return []
    
    def extract_coordinates_from_text(self, text: str) -> Optional[tuple]:
        """
        Extract latitude/longitude from text description
        
        Examples:
        "15.8N 120.5E" → (15.8, 120.5)
        "15.8°N 120.5°E" → (15.8, 120.5)
        "Located at 15.8N, 120.5E" → (15.8, 120.5)
        
        Args:
            text: Text containing coordinates
            
        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # Pattern: decimal number followed by N/S, then decimal number followed by E/W
            # Matches: "15.8N 120.5E", "15.8°N 120.5°E", etc.
            pattern = r'(\d+\.?\d*)\s*°?\s*([NS])\s*,?\s*(\d+\.?\d*)\s*°?\s*([EW])'
            
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match:
                lat = float(match.group(1))
                lat_dir = match.group(2).upper()
                lon = float(match.group(3))
                lon_dir = match.group(4).upper()
                
                # Convert to signed coordinates
                if lat_dir == 'S':
                    lat = -lat
                if lon_dir == 'W':
                    lon = -lon
                
                logger.info(f"Extracted coordinates from text: ({lat}, {lon})")
                return (lat, lon)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting coordinates: {e}")
            return None
    
    def extract_storm_name(self, title: str) -> str:
        """
        Extract storm name from title
        
        Examples:
        "Tropical Storm Melissa" → "melissa"
        "Hurricane Rafael" → "rafael"
        "Typhoon Kalmaegi" → "kalmaegi"
        "TS 15W (Fung-Wong)" → "fung-wong"
        
        Args:
            title: Full storm title
            
        Returns:
            Cleaned storm name in lowercase
        """
        title_lower = title.lower()
        
        # Remove common prefixes
        prefixes = ['tropical storm', 'hurricane', 'typhoon', 'tropical depression', 
                   'cyclone', 'super typhoon', 'ts', 'ty', 'tc']
        
        for prefix in prefixes:
            if title_lower.startswith(prefix):
                title_lower = title_lower.replace(prefix, '').strip()
        
        # Remove storm numbers like "15W" or "(15W)"
        title_lower = re.sub(r'\d+[EW]', '', title_lower)
        title_lower = re.sub(r'[\(\)]', '', title_lower)
        
        # Clean up
        title_lower = title_lower.strip()
        
        logger.info(f"Extracted storm name: '{title_lower}' from '{title}'")
        return title_lower
    
    def find_storm_in_sources(self, storm_name: str, noaa_storms: List[Dict], jtwc_storms: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Find matching storm in NOAA or JTWC data
        
        Args:
            storm_name: Storm name to search for
            noaa_storms: List of NOAA storm data
            jtwc_storms: List of JTWC storm data
            
        Returns:
            Matching storm data with source or None
        """
        storm_name = storm_name.lower().strip()
        
        # Try NOAA first (Atlantic/E. Pacific)
        for noaa_storm in noaa_storms:
            noaa_name = noaa_storm.get('name', '').lower().strip()
            
            if storm_name in noaa_name or noaa_name in storm_name:
                logger.info(f"✓ Found match in NOAA: '{noaa_storm.get('name')}'")
                return {
                    'source': 'NOAA',
                    'data': noaa_storm,
                    'lat': noaa_storm.get('latitudeNumeric'),
                    'lon': noaa_storm.get('longitudeNumeric')
                }
        
        # Try JTWC (W. Pacific/Indian Ocean)
        for jtwc_storm in jtwc_storms:
            jtwc_name = jtwc_storm.get('name', '').lower().strip()
            
            if storm_name in jtwc_name or jtwc_name in storm_name:
                logger.info(f"✓ Found match in JTWC: '{jtwc_storm.get('name')}'")
                return {
                    'source': 'JTWC',
                    'data': jtwc_storm,
                    'lat': jtwc_storm.get('latitude'),
                    'lon': jtwc_storm.get('longitude')
                }
        
        logger.warning(f"No match found in NOAA or JTWC for: '{storm_name}'")
        return None
    
    def fetch_active_storms(self, days: int = 60) -> Optional[Dict[str, Any]]:
        """
        Fetch active storms from NASA EONET
        
        Args:
            days: Number of days to look back (default: 60)
            
        Returns:
            Dictionary containing storm data or None if failed
        """
        params = {
            'category': 'severeStorms',
            'status': 'open',
            'days': days
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching active storms from NASA EONET (last {days} days)")
                
                response = requests.get(
                    self.eonet_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                storm_count = len(data.get('events', []))
                logger.info(f"✓ Found {storm_count} storms in NASA EONET")
                
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
    
    def save_to_database(self, storms_data: Dict[str, Any]) -> int:
        """
        Save storm data to PostgreSQL database with multi-source cross-referencing
        
        Args:
            storms_data: Event data from NASA EONET
            
        Returns:
            Number of storms saved
        """
        saved_count = 0
        
        # Fetch active storms from both sources
        logger.info("\nFetching data from multiple storm tracking sources...")
        noaa_storms = self.fetch_noaa_active_storms()
        jtwc_storms = self.fetch_jtwc_active_storms()
        
        total_external_storms = len(noaa_storms) + len(jtwc_storms)
        logger.info(f"Total storms found in external sources: {total_external_storms}")
        
        try:
            events = storms_data.get('events', [])
            
            for event in events:
                try:
                    storm_id = event.get('id')
                    title = event.get('title', 'Unknown Storm')
                    
                    logger.info(f"\nProcessing storm: {title} (ID: {storm_id})")
                    
                    latitude = None
                    longitude = None
                    source_used = "NASA EONET"
                    
                    # Step 1: Try to get coordinates from NASA EONET
                    geometries = event.get('geometries', [])
                    if geometries:
                        latest_geometry = geometries[-1]
                        coordinates = latest_geometry.get('coordinates', [])
                        
                        if len(coordinates) >= 2:
                            latitude = float(coordinates[1])
                            longitude = float(coordinates[0])
                            logger.info(f"Using NASA EONET coordinates: ({latitude}, {longitude})")
                    
                    # Step 2: If no NASA coordinates, try NOAA + JTWC cross-reference
                    if latitude is None or longitude is None:
                        logger.info(f"No NASA coordinates, trying NOAA + JTWC cross-reference...")
                        
                        # Extract storm name
                        storm_name = self.extract_storm_name(title)
                        
                        # Find in external sources
                        match = self.find_storm_in_sources(storm_name, noaa_storms, jtwc_storms)
                        
                        if match:
                            latitude = match['lat']
                            longitude = match['lon']
                            source_used = match['source']
                            logger.info(f"✓ Using {source_used} coordinates: ({latitude}, {longitude})")
                    
                    # If still no coordinates, skip
                    if latitude is None or longitude is None:
                        logger.warning(f"❌ No coordinates available for {title} - skipping")
                        continue
                    
                    # Parse date
                    date_str = ''
                    if geometries:
                        date_str = geometries[-1].get('date', '')
                    
                    try:
                        timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else datetime.utcnow()
                    except Exception:
                        timestamp = datetime.utcnow()
                    
                    # Get sources
                    sources = event.get('sources', [])
                    source_url = sources[0].get('url', '') if sources else ''
                    
                    storm_data = {
                        'storm_id': str(storm_id),
                        'title': title[:500],
                        'timestamp': timestamp,
                        'latitude': latitude,
                        'longitude': longitude,
                        'status': 'active',
                        'category': f'Severe Storm ({source_used})',
                        'source_url': source_url[:1000] if source_url else ''
                    }
                    
                    logger.info(f"Saving storm: {title} at ({latitude:.2f}, {longitude:.2f})")
                    
                    # Insert into database
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO storms 
                                (storm_id, title, timestamp, latitude, longitude, 
                                 status, category, source_url)
                                VALUES (%(storm_id)s, %(title)s, %(timestamp)s, %(latitude)s,
                                        %(longitude)s, %(status)s, %(category)s, %(source_url)s)
                                ON CONFLICT (storm_id) DO UPDATE SET
                                    title = EXCLUDED.title,
                                    timestamp = EXCLUDED.timestamp,
                                    latitude = EXCLUDED.latitude,
                                    longitude = EXCLUDED.longitude,
                                    status = EXCLUDED.status,
                                    category = EXCLUDED.category,
                                    collected_at = CURRENT_TIMESTAMP
                            """, storm_data)
                    
                    logger.info(f"✓ Successfully saved storm {storm_id}")
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save storm {event.get('id')}: {e}", exc_info=True)
                    continue
            
            logger.info(f"\n✓ Saved {saved_count} storm records to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process storm data: {e}", exc_info=True)
            return saved_count

def main():
    """Main execution function"""
    logger.info("=== Storm Data Collection with NOAA + JTWC Cross-Referencing ===\n")
    
    collector = StormDataCollector()
    
    # Fetch active storms from NASA EONET
    logger.info("Step 1: Fetching storms from NASA EONET")
    data = collector.fetch_active_storms(days=60)
    
    if data:
        logger.info("Storm data collection successful")
        
        # Save to database (will cross-reference with NOAA + JTWC)
        logger.info("\nStep 2: Cross-referencing with NOAA + JTWC and saving to database")
        saved = collector.save_to_database(data)
        
        # Display results
        events = data.get('events', [])
        
        print(f"\n{'='*80}")
        print(f"=== Storm Data Collection Complete ===")
        print(f"{'='*80}")
        print(f"Total storms from NASA EONET: {len(events)}")
        print(f"Saved to database: {saved}")
        
        if saved > 0:
            print(f"\n🌪️ Active Storms:")
            
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT title, latitude, longitude, timestamp, category
                        FROM storms
                        WHERE status = 'active'
                        ORDER BY timestamp DESC
                        LIMIT 10
                    """)
                    
                    storms = cur.fetchall()
                    
                    for storm in storms:
                        title, lat, lon, ts, category = storm
                        print(f"\n  🌀 {title}")
                        print(f"     Location: {lat:.2f}°N, {lon:.2f}°E")
                        print(f"     Source: {category}")
                        print(f"     Last updated: {ts}")
        else:
            print(f"\n⚠️ No storms could be saved (no coordinates available from any source)")
        
        return data
    else:
        logger.error("Storm data collection failed")
        return None

if __name__ == "__main__":
    main()
