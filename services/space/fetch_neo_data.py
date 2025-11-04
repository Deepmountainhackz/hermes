"""
Near Earth Objects (NEO) Data Collector
Fetches asteroid and comet data from NASA's NEO API
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NEODataCollector:
    """Collector for Near Earth Objects data from NASA"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.nasa.gov/neo/rest/v1/feed"
        self.api_key = api_key or os.environ.get('NASA_API_KEY', 'DEMO_KEY')
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_data(self, days: int = 1) -> Optional[Dict[str, Any]]:
        """
        Fetch NEO data for specified number of days
        
        Args:
            days: Number of days to fetch (1-7, default 1)
            
        Returns:
            Dictionary containing NEO data or None if failed
        """
        # Limit days to API constraint
        days = min(max(days, 1), 7)
        
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days-1)
        
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'api_key': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching NEO data for {start_date} to {end_date} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response structure
                if not self._validate_response(data):
                    logger.error("Invalid response structure from NEO API")
                    return None
                
                # Process and enrich data
                enriched_data = self._enrich_data(data)
                
                logger.info(f"Successfully fetched NEO data: "
                          f"{enriched_data['total_objects']} objects, "
                          f"{enriched_data['potentially_hazardous_count']} potentially hazardous")
                
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
                if e.response.status_code == 429:
                    logger.warning("Rate limit hit, waiting longer")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 3)
                else:
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
        """Validate NEO API response structure"""
        try:
            return (
                'element_count' in data and
                'near_earth_objects' in data
            )
        except Exception:
            return False
    
    def _enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enrich NEO data"""
        neo_objects = data['near_earth_objects']
        
        # Collect all NEOs across all dates
        all_neos = []
        potentially_hazardous = []
        
        for date, neos in neo_objects.items():
            for neo in neos:
                neo_info = {
                    'id': neo['id'],
                    'name': neo['name'],
                    'date': date,
                    'diameter_min_km': neo['estimated_diameter']['kilometers']['estimated_diameter_min'],
                    'diameter_max_km': neo['estimated_diameter']['kilometers']['estimated_diameter_max'],
                    'potentially_hazardous': neo['is_potentially_hazardous_asteroid'],
                    'close_approach_date': neo['close_approach_data'][0]['close_approach_date'] if neo['close_approach_data'] else None,
                    'relative_velocity_kmh': float(neo['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']) if neo['close_approach_data'] else None,
                    'miss_distance_km': float(neo['close_approach_data'][0]['miss_distance']['kilometers']) if neo['close_approach_data'] else None
                }
                all_neos.append(neo_info)
                
                if neo['is_potentially_hazardous_asteroid']:
                    potentially_hazardous.append(neo_info)
        
        return {
            'total_objects': data['element_count'],
            'potentially_hazardous_count': len(potentially_hazardous),
            'start_date': list(neo_objects.keys())[0] if neo_objects else None,
            'end_date': list(neo_objects.keys())[-1] if neo_objects else None,
            'all_objects': all_neos,
            'potentially_hazardous': potentially_hazardous,
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success'
        }

def main():
    """Main execution function"""
    # You can set NASA_API_KEY environment variable or it will use DEMO_KEY
    collector = NEODataCollector()
    
    logger.info("Starting NEO data collection")
    data = collector.fetch_data(days=1)
    
    if data:
        logger.info("NEO data collection successful")
        print("\n=== Near Earth Objects Data ===")
        print(f"Total Objects: {data['total_objects']}")
        print(f"Potentially Hazardous: {data['potentially_hazardous_count']}")
        print(f"Date Range: {data['start_date']} to {data['end_date']}")
        print(f"Collection Time: {data['collection_time']}")
        
        if data['potentially_hazardous']:
            print("\nPotentially Hazardous Objects:")
            for neo in data['potentially_hazardous'][:5]:  # Show first 5
                print(f"  - {neo['name']}: {neo['diameter_max_km']:.2f} km diameter, "
                      f"miss distance: {neo['miss_distance_km']:.0f} km")
        
        return data
    else:
        logger.error("NEO data collection failed")
        return None

if __name__ == "__main__":
    main()
