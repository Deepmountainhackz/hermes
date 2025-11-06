"""
Near-Earth Objects (NEO) Data Collector
Fetches asteroid data from NASA API and saves to PostgreSQL
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
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

class NEODataCollector:
    """Collector for Near-Earth Objects data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('NASA_API_KEY')
        self.base_url = "https://api.nasa.gov/neo/rest/v1/feed"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("NASA_API_KEY not found in environment!")
    
    def fetch_data(self, days: int = 1) -> Optional[Dict[str, Any]]:
        """
        Fetch NEO data for the specified number of days
        
        Args:
            days: Number of days to fetch (default: 1)
            
        Returns:
            Dictionary containing NEO data or None if failed
        """
        if not self.api_key:
            logger.error("NASA API key not provided")
            return None
        
        # Get date range
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days-1)
        
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'api_key': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching NEO data (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"Successfully fetched NEO data")
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
    
    def save_to_database(self, data: Dict[str, Any]) -> int:
        """
        Save NEO data to PostgreSQL database
        
        Args:
            data: NEO data from NASA API
            
        Returns:
            Number of NEOs saved
        """
        saved_count = 0
        
        try:
            near_earth_objects = data.get('near_earth_objects', {})
            
            for date_str, neos in near_earth_objects.items():
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                for neo in neos:
                    try:
                        # Extract data
                        neo_data = {
                            'neo_id': neo['id'],
                            'name': neo['name'],
                            'date': date,
                            'diameter_min': float(neo['estimated_diameter']['kilometers']['estimated_diameter_min']),
                            'diameter_max': float(neo['estimated_diameter']['kilometers']['estimated_diameter_max']),
                            'velocity': float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']),
                            'miss_distance': float(neo['close_approach_data'][0]['miss_distance']['kilometers']),
                            'hazardous': neo['is_potentially_hazardous_asteroid']
                        }
                        
                        # Insert into database
                        with get_db_connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO near_earth_objects 
                                    (neo_id, name, date, estimated_diameter_min, estimated_diameter_max,
                                     relative_velocity, miss_distance, is_potentially_hazardous)
                                    VALUES (%(neo_id)s, %(name)s, %(date)s, %(diameter_min)s, %(diameter_max)s,
                                            %(velocity)s, %(miss_distance)s, %(hazardous)s)
                                    ON CONFLICT (neo_id, date) DO UPDATE SET
                                        name = EXCLUDED.name,
                                        estimated_diameter_min = EXCLUDED.estimated_diameter_min,
                                        estimated_diameter_max = EXCLUDED.estimated_diameter_max,
                                        relative_velocity = EXCLUDED.relative_velocity,
                                        miss_distance = EXCLUDED.miss_distance,
                                        is_potentially_hazardous = EXCLUDED.is_potentially_hazardous,
                                        collected_at = CURRENT_TIMESTAMP
                                """, neo_data)
                        
                        saved_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to save NEO {neo.get('id')}: {e}")
                        continue
            
            logger.info(f"✓ Saved {saved_count} NEO records to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process NEO data: {e}")
            return saved_count

def main():
    """Main execution function"""
    collector = NEODataCollector()
    
    logger.info("Starting NEO data collection")
    data = collector.fetch_data(days=1)
    
    if data:
        logger.info("NEO data collection successful")
        
        # Save to database
        saved = collector.save_to_database(data)
        
        print(f"\n=== NEO Data Collection ===")
        print(f"Total NEOs: {data.get('element_count', 0)}")
        print(f"Saved to database: {saved}")
        
        return data
    else:
        logger.error("NEO data collection failed")
        return None

if __name__ == "__main__":
    main()
