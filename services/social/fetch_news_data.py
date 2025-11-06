"""
News Data Collector
Fetches latest news articles from NewsAPI and saves to PostgreSQL
"""

import requests
import logging
from datetime import datetime
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

class NewsDataCollector:
    """Collector for news articles"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('NEWSAPI_KEY')
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.api_key:
            logger.error("NEWSAPI_KEY not found in environment!")
    
    def fetch_headlines(self, category: str = 'business') -> Optional[List[Dict[str, Any]]]:
        """
        Fetch top headlines from NewsAPI
        
        Args:
            category: News category (business, technology, general, etc.)
            
        Returns:
            List of news articles or None if failed
        """
        if not self.api_key:
            logger.error("NewsAPI key not provided")
            return None
        
        params = {
            'category': category,
            'language': 'en',
            'pageSize': 50,
            'apiKey': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {category} news (attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') != 'ok':
                    logger.error(f"NewsAPI error: {data.get('message', 'Unknown')}")
                    return None
                
                articles = data.get('articles', [])
                logger.info(f"✓ Fetched {len(articles)} {category} articles")
                return articles
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def save_to_database(self, articles: List[Dict[str, Any]], category: str) -> int:
        """
        Save news articles to PostgreSQL database
        
        Args:
            articles: List of news articles
            category: News category
            
        Returns:
            Number of articles saved
        """
        saved_count = 0
        
        try:
            for article in articles:
                try:
                    # Skip if missing required fields
                    if not article.get('title') or not article.get('source'):
                        continue
                    
                    # Parse published date
                    published_at = None
                    if article.get('publishedAt'):
                        try:
                            published_at = datetime.fromisoformat(
                                article['publishedAt'].replace('Z', '+00:00')
                            )
                        except:
                            pass
                    
                    article_data = {
                        'title': article['title'][:500],  # Limit length
                        'description': article.get('description', '')[:1000] if article.get('description') else None,
                        'url': article.get('url', '')[:500],
                        'source': article['source'].get('name', 'Unknown')[:255],
                        'published_at': published_at,
                        'author': article.get('author', '')[:255] if article.get('author') else None,
                        'category': category
                    }
                    
                    # Insert into database
                    with get_db_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO news 
                                (title, description, url, source, published_at, author, category)
                                VALUES (%(title)s, %(description)s, %(url)s, %(source)s,
                                        %(published_at)s, %(author)s, %(category)s)
                                ON CONFLICT (title, source) DO UPDATE SET
                                    description = EXCLUDED.description,
                                    url = EXCLUDED.url,
                                    published_at = EXCLUDED.published_at,
                                    author = EXCLUDED.author,
                                    collected_at = CURRENT_TIMESTAMP
                            """, article_data)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to save article: {e}")
                    continue
            
            logger.info(f"✓ Saved {saved_count} news articles to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Failed to process news data: {e}")
            return saved_count
    
    def collect_all_categories(self) -> Dict[str, Any]:
        """
        Collect news from multiple categories
        
        Returns:
            Collection results
        """
        categories = ['business', 'technology']
        results = {
            'total_articles': 0,
            'saved': 0,
            'categories': {}
        }
        
        for category in categories:
            articles = self.fetch_headlines(category)
            
            if articles:
                saved = self.save_to_database(articles, category)
                results['categories'][category] = {
                    'fetched': len(articles),
                    'saved': saved
                }
                results['total_articles'] += len(articles)
                results['saved'] += saved
                
                # Rate limiting
                time.sleep(2)
        
        return results

def main():
    """Main execution function"""
    collector = NewsDataCollector()
    
    logger.info("Starting news data collection")
    results = collector.collect_all_categories()
    
    print(f"\n=== News Data Collection ===")
    print(f"Total articles fetched: {results['total_articles']}")
    print(f"Total saved to database: {results['saved']}")
    
    for category, stats in results['categories'].items():
        print(f"\n{category.capitalize()}:")
        print(f"  Fetched: {stats['fetched']}")
        print(f"  Saved: {stats['saved']}")
    
    return results

if __name__ == "__main__":
    main()
