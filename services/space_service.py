"""Space Service - NASA API integration."""
import requests, json, logging
from typing import List, Dict, Optional
from datetime import datetime
from core.config import Config
from repositories.space_repository import SpaceRepository

logger = logging.getLogger(__name__)

class SpaceService:
    def __init__(self, config: Config, repository: SpaceRepository):
        self.config = config
        self.repository = repository
        self.api_key = getattr(config, 'NASA_API_KEY', 'DEMO_KEY')
        self.timeout = config.API_TIMEOUT
    
    def fetch_iss_position(self) -> Optional[Dict]:
        try:
            response = requests.get("http://api.open-notify.org/iss-now.json", timeout=self.timeout)
            data = response.json()
            return {
                'event_type': 'ISS_POSITION',
                'name': 'ISS Location',
                'description': f"Lat: {data['iss_position']['latitude']}, Lon: {data['iss_position']['longitude']}",
                'data': json.dumps(data),
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching ISS position: {e}")
            return None
    
    def collect_and_store_data(self) -> Dict:
        results = []
        iss_data = self.fetch_iss_position()
        if iss_data:
            results.append(iss_data)
        
        successful = 0
        if results:
            successful = self.repository.insert_bulk_space_data(results)
        
        return {
            'total_events': 1,
            'successful': successful,
            'failed': 1 - len(results),
            'timestamp': datetime.now()
        }
