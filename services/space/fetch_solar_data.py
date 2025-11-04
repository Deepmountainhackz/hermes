"""
Solar Activity Data Collector
Fetches solar flare and space weather data from NASA's DONKI API
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

class SolarDataCollector:
    """Collector for Solar activity and space weather data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.nasa.gov/DONKI"
        self.api_key = api_key or os.environ.get('NASA_API_KEY', 'DEMO_KEY')
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_solar_flares(self, days_back: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch solar flare data
        
        Args:
            days_back: Number of days to look back (default 7)
            
        Returns:
            List of solar flare events or None if failed
        """
        start_date = (datetime.now() - timedelta(days=days_back)).date()
        end_date = datetime.now().date()
        
        params = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'api_key': self.api_key
        }
        
        endpoint = f"{self.base_url}/FLR"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching solar flare data from {start_date} to {end_date} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
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
    
    def fetch_cme(self, days_back: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch Coronal Mass Ejection (CME) data
        
        Args:
            days_back: Number of days to look back (default 7)
            
        Returns:
            List of CME events or None if failed
        """
        start_date = (datetime.now() - timedelta(days=days_back)).date()
        end_date = datetime.now().date()
        
        params = {
            'startDate': start_date.isoformat(),
            'endDate': end_date.isoformat(),
            'api_key': self.api_key
        }
        
        endpoint = f"{self.base_url}/CME"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching CME data from {start_date} to {end_date} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"Successfully fetched {len(data)} CME events")
                
                return data
                
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
    
    def fetch_data(self, days_back: int = 7) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive solar activity data
        
        Args:
            days_back: Number of days to look back (default 7)
            
        Returns:
            Dictionary containing all solar activity data or None if failed
        """
        logger.info("Starting comprehensive solar data collection")
        
        # Fetch solar flares
        flares = self.fetch_solar_flares(days_back)
        
        # Fetch CME data
        cme_data = self.fetch_cme(days_back)
        
        # If both failed, return None
        if flares is None and cme_data is None:
            logger.error("All solar data collection failed")
            return None
        
        # Process and enrich the data
        enriched_data = self._enrich_data(flares or [], cme_data or [], days_back)
        
        return enriched_data
    
    def _enrich_data(self, flares: List[Dict], cme_data: List[Dict], days_back: int) -> Dict[str, Any]:
        """Process and enrich solar activity data"""
        
        # Categorize flares by class
        flare_classes = {'X': [], 'M': [], 'C': [], 'B': [], 'A': []}
        
        for flare in flares:
            class_type = flare.get('classType', 'Unknown')
            if class_type and len(class_type) > 0:
                first_char = class_type[0].upper()
                if first_char in flare_classes:
                    flare_classes[first_char].append(flare)
        
        return {
            'total_flares': len(flares),
            'total_cme': len(cme_data),
            'flare_breakdown': {
                'X_class': len(flare_classes['X']),  # Most intense
                'M_class': len(flare_classes['M']),
                'C_class': len(flare_classes['C']),
                'B_class': len(flare_classes['B']),
                'A_class': len(flare_classes['A'])   # Weakest
            },
            'x_class_flares': flare_classes['X'],
            'm_class_flares': flare_classes['M'],
            'all_flares': flares,
            'all_cme': cme_data,
            'days_covered': days_back,
            'start_date': (datetime.now() - timedelta(days=days_back)).date().isoformat(),
            'end_date': datetime.now().date().isoformat(),
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success'
        }

def main():
    """Main execution function"""
    # You can set NASA_API_KEY environment variable or it will use DEMO_KEY
    collector = SolarDataCollector()
    
    logger.info("Starting solar activity data collection")
    data = collector.fetch_data(days_back=7)
    
    if data:
        logger.info("Solar data collection successful")
        print("\n=== Solar Activity Data ===")
        print(f"Total Solar Flares: {data['total_flares']}")
        print(f"Total CME Events: {data['total_cme']}")
        print(f"Date Range: {data['start_date']} to {data['end_date']}")
        print(f"\nFlare Breakdown:")
        print(f"  X-Class (Most Intense): {data['flare_breakdown']['X_class']}")
        print(f"  M-Class: {data['flare_breakdown']['M_class']}")
        print(f"  C-Class: {data['flare_breakdown']['C_class']}")
        print(f"  B-Class: {data['flare_breakdown']['B_class']}")
        print(f"  A-Class (Weakest): {data['flare_breakdown']['A_class']}")
        print(f"\nCollection Time: {data['collection_time']}")
        
        if data['x_class_flares']:
            print("\n⚠️  X-Class Flares (Major Events):")
            for flare in data['x_class_flares'][:3]:  # Show first 3
                print(f"  - {flare.get('classType', 'Unknown')}: {flare.get('beginTime', 'Unknown time')}")
        
        return data
    else:
        logger.error("Solar data collection failed")
        return None

if __name__ == "__main__":
    main()
