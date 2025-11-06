"""
Solar Flares Data Collector
Fetches solar flare data from NASA DONKI API and saves to PostgreSQL
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

class SolarFlareCollector:
    """Collector for solar flare data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('NASA_API_KEY')
        self.base_url = "https://api.nasa.gov/DONKI/FLR"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("NASA_API_KEY not found in environment!")
    
    def fetch_data(self, days: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch solar flare data for the past N days
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            List of solar flare events or None if failed
        """
        if not self.api_key:
            logger.error("NASA API key not provided")
            return None
        
        # Get date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'api_key': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching solar flare data (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"Successfully fetched {len(data)} solar flare events")
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
    
    def save_to_database(self, flares: List[Dict[str, Any]]) -> int:
        """
        Save solar flare data to PostgreSQL database
        
        Args:
            flares: List of solar flare events
            
        Returns:
            Number of flares saved
        """
        saved_count = 0
        
        try:
            for flare in flares:
                try:
                    # Create unique flare ID
                    flare_id = flare.get('flrID', '')
                    if not flare_id:
                        continue
                    
                    # Parse timestamps
                    begin_time = None
                    if flare.get('beginTime'):
                        begin_time = datetime.fromisoformat(flare['beginTime'].replace('Z', '+00:00'))
                    
                    peak_time = None
                    if flare.get('peakTime'):
                        peak_time = datetime.fromisoformat(flare['peakTime'].replace('Z', '+00:00'))
                    
                    end_time = None
                    if flare.get('endTime'):
                        end_time = datetime.fromisoformat(flare['endTime'].replace('Z', '+00:00'))
                    
                    flare_data = {
                        'flare_id': flare_id,
                        'begin_time': begin_time,
                        'peak_time': peak_time,
                        'end_time': end_time,
                        'class_type': flare.get('classType', ''),
                        'source_location': flare.get('sourceLocation', ''),
                        'active_region': flare.get('activeRegionNum', '')
                    }
                    
                    # Insert into database
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO solar_flares 
                                (flare_id, begin_time, peak_time, end_time, class_type, 
                                 source_location, active_region_num)
                                VALUES (%(flare_id)s, %(begin_time)s, %(peak_time)s, %(end_time)s,
                                        %(class_type)s, %(source_location)s, %(active_region)s)
                                ON CONFLICT (flare_id) DO UPDATE SET
                                    begin_time = EXCLUDED.begin_time,
                                    peak_time = EXCLUDED.peak_time,
                                    end_time = EXCLUDED.end_time,
                                    class_type = EXCLUDED.class_type,
                                    source_location = EXCLUDED.source_location,
                                    active_region_num = EXCLUDED.active_region_num,
                                    collected_at = CURRENT_TIMESTAMP
                            """, flare_data)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save flare {flare.get('flrID')}: {e}")
                    continue
            
            logger.info(f"✓ Saved {saved_count} solar flare records to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process solar flare data: {e}")
            return saved_count

def main():
    """Main execution function"""
    collector = SolarFlareCollector()
    
    logger.info("Starting solar flare data collection")
    data = collector.fetch_data(days=7)
    
    if data:
        logger.info("Solar flare data collection successful")
        
        # Save to database
        saved = collector.save_to_database(data)
        
        print(f"\n=== Solar Flare Data Collection ===")
        print(f"Total flares found: {len(data)}")
        print(f"Saved to database: {saved}")
        
        if data:
            print(f"\nRecent flares:")
            for flare in data[:3]:
                print(f"  {flare.get('classType', 'Unknown')} - {flare.get('beginTime', 'N/A')}")
        
        return data
    else:
        logger.error("Solar flare data collection failed")
        return None

if __name__ == "__main__":
    main()
