"""
GDELT Service
Fetches global events and social unrest data from GDELT Project API.
"""
import requests
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from core.config import Config
from core.exceptions import APIError
from repositories.gdelt_repository import GdeltRepository

logger = logging.getLogger(__name__)


class GdeltService:
    """Service for GDELT global events data."""

    # Event categories of interest for investment intelligence
    EVENT_CATEGORIES = {
        'PROTEST': 'Civil Unrest/Protests',
        'RIOT': 'Riots/Violence',
        'STRIKE': 'Labor Strikes',
        'COERCE': 'Coercion/Threats',
        'ASSAULT': 'Armed Conflict',
        'SANCTION': 'Economic Sanctions',
        'MOBILIZE': 'Military Mobilization',
    }

    # Key countries to monitor
    MONITORED_COUNTRIES = [
        'US', 'GB', 'DE', 'FR', 'JP', 'CN', 'RU', 'IN', 'BR', 'MX',
        'AU', 'CA', 'IT', 'ES', 'KR', 'SA', 'ZA', 'TR', 'AR', 'ID'
    ]

    def __init__(self, config: Config, repository: GdeltRepository):
        """Initialize the service."""
        self.config = config
        self.repository = repository
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.timeout = config.API_TIMEOUT
        self.rate_limit_delay = config.DEFAULT_RATE_LIMIT_DELAY

    def _make_api_request(self, query: str, mode: str = "artlist") -> Dict[str, Any]:
        """Make a request to GDELT API."""
        params = {
            'query': query,
            'mode': mode,
            'maxrecords': 50,
            'format': 'json',
            'sort': 'datedesc'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GDELT API request failed: {e}")
            raise APIError(f"Failed to fetch from GDELT: {e}")

    def fetch_unrest_events(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch civil unrest and protest events."""
        results = []

        # Search terms for civil unrest
        search_terms = [
            'protest OR demonstration OR riot',
            'strike OR labor dispute',
            'civil unrest OR social unrest',
            'political tension OR political crisis'
        ]

        for term in search_terms:
            try:
                query = term
                if country:
                    query = f"({term}) sourcecountry:{country}"

                data = self._make_api_request(query)

                if 'articles' in data:
                    for article in data['articles'][:10]:  # Limit per category
                        event = {
                            'title': article.get('title', '')[:500],
                            'url': article.get('url', ''),
                            'source': article.get('domain', ''),
                            'country': article.get('sourcecountry', country or 'Unknown'),
                            'event_type': self._classify_event(article.get('title', '')),
                            'tone': article.get('tone', 0),
                            'published_at': self._parse_date(article.get('seendate')),
                            'timestamp': datetime.now()
                        }
                        results.append(event)

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.warning(f"Error fetching unrest events for '{term}': {e}")
                continue

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for event in results:
            if event['url'] not in seen_urls:
                seen_urls.add(event['url'])
                unique_results.append(event)

        return unique_results

    def fetch_geopolitical_events(self) -> List[Dict[str, Any]]:
        """Fetch geopolitical events (sanctions, military, diplomatic)."""
        results = []

        search_terms = [
            'economic sanctions OR trade war',
            'military deployment OR troop movement',
            'diplomatic crisis OR embassy',
            'coup OR government overthrow'
        ]

        for term in search_terms:
            try:
                data = self._make_api_request(term)

                if 'articles' in data:
                    for article in data['articles'][:10]:
                        event = {
                            'title': article.get('title', '')[:500],
                            'url': article.get('url', ''),
                            'source': article.get('domain', ''),
                            'country': article.get('sourcecountry', 'Unknown'),
                            'event_type': 'GEOPOLITICAL',
                            'tone': article.get('tone', 0),
                            'published_at': self._parse_date(article.get('seendate')),
                            'timestamp': datetime.now()
                        }
                        results.append(event)

                time.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.warning(f"Error fetching geopolitical events: {e}")
                continue

        return results

    def collect_and_store_data(self) -> Dict[str, Any]:
        """Collect GDELT events and store in database."""
        logger.info("Starting GDELT data collection")
        start_time = datetime.now()

        all_events = []

        # Fetch unrest events for monitored countries
        for country in self.MONITORED_COUNTRIES[:10]:  # Limit to avoid rate limits
            try:
                events = self.fetch_unrest_events(country)
                all_events.extend(events)
                time.sleep(self.rate_limit_delay)
            except Exception as e:
                logger.warning(f"Failed to fetch events for {country}: {e}")

        # Fetch geopolitical events
        try:
            geo_events = self.fetch_geopolitical_events()
            all_events.extend(geo_events)
        except Exception as e:
            logger.warning(f"Failed to fetch geopolitical events: {e}")

        # Store in database
        successful = 0
        if all_events:
            try:
                successful = self.repository.insert_bulk_events(all_events)
            except Exception as e:
                logger.error(f"Error storing GDELT events: {e}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        results = {
            'total_events': len(all_events),
            'successful': successful,
            'failed': len(all_events) - successful,
            'duration_seconds': duration,
            'timestamp': end_time
        }

        logger.info(f"GDELT collection completed: {successful} events stored")
        return results

    def get_latest_events(self, event_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest events from database."""
        try:
            return self.repository.get_latest_events(event_type=event_type, limit=limit)
        except Exception as e:
            logger.error(f"Error getting latest events: {e}")
            return []

    def get_events_by_country(self, country: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get events for a specific country."""
        try:
            return self.repository.get_events_by_country(country, limit)
        except Exception as e:
            logger.error(f"Error getting events for {country}: {e}")
            return []

    def _classify_event(self, title: str) -> str:
        """Classify event type based on title."""
        title_lower = title.lower()

        if any(word in title_lower for word in ['protest', 'demonstration', 'march']):
            return 'PROTEST'
        elif any(word in title_lower for word in ['riot', 'violence', 'clash']):
            return 'RIOT'
        elif any(word in title_lower for word in ['strike', 'walkout', 'labor']):
            return 'STRIKE'
        elif any(word in title_lower for word in ['sanction', 'tariff', 'trade war']):
            return 'SANCTION'
        elif any(word in title_lower for word in ['military', 'troop', 'armed']):
            return 'MOBILIZE'
        else:
            return 'UNREST'

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse GDELT date format."""
        if not date_str:
            return None
        try:
            # GDELT format: YYYYMMDDHHmmSS
            return datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
        except (ValueError, TypeError):
            return None
