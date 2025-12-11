"""News Service - NewsAPI integration."""
import requests, logging
from typing import List, Dict
from datetime import datetime
from core.config import Config
from repositories.news_repository import NewsRepository

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self, config: Config, repository: NewsRepository):
        self.config = config
        self.repository = repository
        self.api_key = getattr(config, 'NEWS_API_KEY', None)
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.timeout = config.API_TIMEOUT
    
    def fetch_news(self) -> List[Dict]:
        if not self.api_key:
            logger.warning("NEWS_API_KEY not configured")
            return []
        
        try:
            params = {
                'apiKey': self.api_key,
                'category': 'business',
                'pageSize': 10,
                'language': 'en'
            }
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            data = response.json()
            
            results = []
            for article in data.get('articles', []):
                results.append({
                    'title': article.get('title'),
                    'source': article.get('source', {}).get('name'),
                    'url': article.get('url'),
                    'description': article.get('description'),
                    'published_at': article.get('publishedAt'),
                    'timestamp': datetime.now()
                })
            return results
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def collect_and_store_data(self) -> Dict:
        results = self.fetch_news()
        successful = 0
        if results:
            successful = self.repository.insert_bulk_news_data(results)
        
        return {
            'total_articles': len(results),
            'successful': successful,
            'failed': 0,
            'timestamp': datetime.now()
        }
