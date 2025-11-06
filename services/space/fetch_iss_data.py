"""
ISS Position Data Collector
Fetches real-time International Space Station position data and saves to PostgreSQL
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import time
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from database import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ISSDataCollector:
    """Collector for International Space Station position data"""
    
    def __init__(self):
        self.base_url = "http://api.open-notify.org/iss-now.json"
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current ISS position data
        
        Returns:
            Dictionary containing ISS data or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching ISS position data (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response structure
                if not self._validate_response(data):
                    logger.error("Invalid response structure from ISS API")
                    return None
                
                # Enrich data with timestamp
                enriched_data = self._enrich_data(data)
                
                logger.info(f"Successfully fetched ISS position: "
                          f"Lat {enriched_data['latitude']}, "
                          f"Lon {enriched_data['longitude']}")
                
                return enriched_data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate ISS API response structure"""
        try:
            return (
                'message' in data and
                data['message'] == 'success' and
                'iss_position' in data and
                'latitude' in data['iss_position'] and
                'longitude' in data['iss_position'] and
                'timestamp' in data
            )
        except Exception:
            return False
    
    def _enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich ISS data with additional metadata"""
        position = data['iss_position']
        
        return {
            'latitude': float(position['latitude']),
            'longitude': float(position['longitude']),
            'timestamp': data['timestamp'],
            'timestamp_readable': datetime.fromtimestamp(data['timestamp']).isoformat(),
            'collection_time': datetime.utcnow().isoformat(),
            'altitude': 408.0,  # Average ISS altitude in km
            'velocity': 27600.0,  # Average ISS velocity in km/h
            'status': 'success'
        }
    
    def save_to_database(self, data: Dict[str, Any]) -> bool:
        """
        Save ISS position data to PostgreSQL database
        
        Args:
            data: ISS position data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data for database
            timestamp = datetime.fromtimestamp(data['timestamp'])
            
            iss_data = {
                'timestamp': timestamp,
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'altitude': data['altitude'],
                'velocity': data['velocity']
            }
            
            # Insert into database
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO iss_positions 
                        (timestamp, latitude, longitude, altitude, velocity)
                        VALUES (%(timestamp)s, %(latitude)s, %(longitude)s, 
                                %(altitude)s, %(velocity)s)
                        ON CONFLICT (timestamp) DO UPDATE SET
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            altitude = EXCLUDED.altitude,
                            velocity = EXCLUDED.velocity,
                            collected_at = CURRENT_TIMESTAMP
                    """, iss_data)
            
            logger.info(f"✓ Saved ISS position to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save ISS data to database: {e}")
            return False

def main():
    """Main execution function"""
    collector = ISSDataCollector()
    
    logger.info("Starting ISS position data collection")
    data = collector.fetch_data()
    
    if data:
        logger.info("ISS data collection successful")
        
        # Save to database
        if collector.save_to_database(data):
            logger.info("✓ ISS data saved to database")
        else:
            logger.error("✗ Failed to save ISS data to database")
        
        print("\n=== ISS Position Data ===")
        print(f"Latitude: {data['latitude']}")
        print(f"Longitude: {data['longitude']}")
        print(f"Altitude: {data['altitude']} km")
        print(f"Velocity: {data['velocity']} km/h")
        print(f"Timestamp: {data['timestamp_readable']}")
        print(f"Collection Time: {data['collection_time']}")
        return data
    else:
        logger.error("ISS data collection failed")
        return None

if __name__ == "__main__":
    main()
