"""Space Service - NASA API integration for ISS, NEO, and Solar Flares."""
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from core.config import Config
from repositories.space_repository import SpaceRepository

logger = logging.getLogger(__name__)


class SpaceService:
    """Service for collecting space-related data from various APIs."""

    def __init__(self, config: Config, repository: SpaceRepository):
        self.config = config
        self.repository = repository
        self.api_key = getattr(config, 'NASA_API_KEY', 'DEMO_KEY')
        self.timeout = getattr(config, 'API_TIMEOUT', 15)

    def fetch_iss_position(self) -> Optional[Dict[str, Any]]:
        """Fetch current ISS position from Open Notify API."""
        try:
            response = requests.get(
                "http://api.open-notify.org/iss-now.json",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if data.get('message') == 'success':
                pos = data['iss_position']
                return {
                    'latitude': float(pos['latitude']),
                    'longitude': float(pos['longitude']),
                    'altitude': 408.0,  # Average ISS altitude in km
                    'velocity': 27600.0,  # Average ISS velocity in km/h
                    'timestamp': datetime.now()
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching ISS position: {e}")
            return None

    def fetch_neo_data(self) -> List[Dict[str, Any]]:
        """Fetch Near-Earth Objects from NASA NeoWs API."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

            url = "https://api.nasa.gov/neo/rest/v1/feed"
            params = {
                'start_date': today,
                'end_date': end_date,
                'api_key': self.api_key
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            neo_list = []
            for date_str, objects in data.get('near_earth_objects', {}).items():
                for obj in objects:
                    try:
                        close_approach = obj['close_approach_data'][0] if obj.get('close_approach_data') else {}
                        diameter = obj.get('estimated_diameter', {}).get('meters', {})

                        neo_list.append({
                            'neo_id': obj.get('id', ''),
                            'name': obj.get('name', 'Unknown'),
                            'date': datetime.strptime(date_str, '%Y-%m-%d').date(),
                            'estimated_diameter_min': float(diameter.get('estimated_diameter_min', 0)),
                            'estimated_diameter_max': float(diameter.get('estimated_diameter_max', 0)),
                            'relative_velocity': float(close_approach.get('relative_velocity', {}).get('kilometers_per_hour', 0)),
                            'miss_distance': float(close_approach.get('miss_distance', {}).get('kilometers', 0)),
                            'is_potentially_hazardous': obj.get('is_potentially_hazardous_asteroid', False)
                        })
                    except (KeyError, ValueError, TypeError) as e:
                        logger.warning(f"Error parsing NEO object: {e}")
                        continue

            logger.info(f"Fetched {len(neo_list)} NEO objects")
            return neo_list

        except Exception as e:
            logger.error(f"Error fetching NEO data: {e}")
            return []

    def fetch_solar_flares(self) -> List[Dict[str, Any]]:
        """Fetch solar flare data from NASA DONKI API."""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            url = "https://api.nasa.gov/DONKI/FLR"
            params = {
                'startDate': start_date,
                'endDate': end_date,
                'api_key': self.api_key
            }

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                logger.warning("Solar flare API returned unexpected format")
                return []

            flares = []
            for flare in data:
                try:
                    flares.append({
                        'flare_id': flare.get('flrID', f"FLR-{datetime.now().timestamp()}"),
                        'begin_time': datetime.fromisoformat(flare['beginTime'].replace('Z', '+00:00')) if flare.get('beginTime') else None,
                        'peak_time': datetime.fromisoformat(flare['peakTime'].replace('Z', '+00:00')) if flare.get('peakTime') else None,
                        'end_time': datetime.fromisoformat(flare['endTime'].replace('Z', '+00:00')) if flare.get('endTime') else None,
                        'class_type': flare.get('classType', 'Unknown'),
                        'source_location': flare.get('sourceLocation', ''),
                        'active_region_num': str(flare.get('activeRegionNum', ''))
                    })
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Error parsing solar flare: {e}")
                    continue

            logger.info(f"Fetched {len(flares)} solar flares")
            return flares

        except Exception as e:
            logger.error(f"Error fetching solar flare data: {e}")
            return []

    def collect_and_store_data(self) -> Dict[str, Any]:
        """Collect all space data and store in database."""
        results = {
            'iss': {'collected': 0, 'stored': 0},
            'neo': {'collected': 0, 'stored': 0},
            'solar_flares': {'collected': 0, 'stored': 0},
            'timestamp': datetime.now()
        }

        # Collect ISS position
        logger.info("Collecting ISS position...")
        iss_data = self.fetch_iss_position()
        if iss_data:
            results['iss']['collected'] = 1
            try:
                stored = self.repository.insert_iss_position(iss_data)
                results['iss']['stored'] = stored
            except Exception as e:
                logger.error(f"Failed to store ISS data: {e}")

        # Collect NEO data
        logger.info("Collecting NEO data...")
        neo_data = self.fetch_neo_data()
        results['neo']['collected'] = len(neo_data)
        if neo_data:
            try:
                stored = self.repository.insert_neo_data(neo_data)
                results['neo']['stored'] = stored
            except Exception as e:
                logger.error(f"Failed to store NEO data: {e}")

        # Collect Solar Flares
        logger.info("Collecting solar flare data...")
        flare_data = self.fetch_solar_flares()
        results['solar_flares']['collected'] = len(flare_data)
        if flare_data:
            try:
                stored = self.repository.insert_solar_flares(flare_data)
                results['solar_flares']['stored'] = stored
            except Exception as e:
                logger.error(f"Failed to store solar flare data: {e}")

        logger.info(f"Space data collection complete: {results}")
        return results
