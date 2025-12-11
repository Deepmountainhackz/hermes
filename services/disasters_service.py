"""Disasters Service - USGS Earthquake API."""
import requests, logging
from typing import List, Dict
from datetime import datetime
from core.config import Config
from repositories.disasters_repository import DisastersRepository

logger = logging.getLogger(__name__)

class DisastersService:
    def __init__(self, config: Config, repository: DisastersRepository):
        self.config = config
        self.repository = repository
        self.usgs_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    
    def fetch_earthquakes(self) -> List[Dict]:
        try:
            response = requests.get(self.usgs_url, timeout=10)
            data = response.json()
            
            results = []
            for feature in data['features'][:10]:  # Top 10
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                results.append({
                    'disaster_type': 'EARTHQUAKE',
                    'location': props.get('place', 'Unknown'),
                    'magnitude': props.get('mag'),
                    'description': f"Magnitude {props.get('mag')} at {props.get('place')}",
                    'timestamp': datetime.now()
                })
            return results
        except Exception as e:
            logger.error(f"Error fetching earthquakes: {e}")
            return []
    
    def collect_and_store_data(self) -> Dict:
        results = self.fetch_earthquakes()
        successful = 0
        if results:
            successful = self.repository.insert_bulk_disaster_data(results)
        
        return {
            'total_events': len(results),
            'successful': successful,
            'failed': 0,
            'timestamp': datetime.now()
        }
