"""
News Data Collector
Fetches latest news articles from various free news APIs
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

class NewsDataCollector:
    """Collector for news articles from multiple sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        # NewsAPI - Free tier available (requires API key)
        self.newsapi_url = "https://newsapi.org/v2"
        self.api_key = api_key or os.environ.get('NEWSAPI_KEY')
        
        # Hacker News API (no key required)
        self.hackernews_url = "https://hacker-news.firebaseio.com/v0"
        
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_newsapi_headlines(self, 
                                category: str = 'general',
                                country: str = 'us') -> Optional[List[Dict[str, Any]]]:
        """
        Fetch top headlines from NewsAPI
        
        Args:
            category: News category (business, technology, sports, etc.)
            country: Country code (us, gb, ca, etc.)
            
        Returns:
            List of news articles or None if failed
        """
        if not self.api_key:
            logger.warning("NewsAPI key not provided, skipping NewsAPI headlines")
            return None
        
        endpoint = f"{self.newsapi_url}/top-headlines"
        params = {
            'category': category,
            'country': country,
            'apiKey': self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching NewsAPI headlines for {category}/{country} "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') != 'ok':
                    logger.error(f"NewsAPI returned error: {data.get('message', 'Unknown')}")
                    return None
                
                articles = data.get('articles', [])
                logger.info(f"Successfully fetched {len(articles)} NewsAPI headlines")
                
                return articles
                
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
                        time.sleep(self.retry_delay * 5)
                elif e.response.status_code == 401:
                    logger.error("Invalid API key")
                    return None
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
    
    def fetch_hackernews_top(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch top stories from Hacker News
        
        Args:
            limit: Number of stories to fetch (max 30)
            
        Returns:
            List of news stories or None if failed
        """
        limit = min(limit, 30)  # Cap at 30
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching Hacker News top {limit} stories "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                # Get top story IDs
                response = requests.get(
                    f"{self.hackernews_url}/topstories.json",
                    timeout=self.timeout
                )
                response.raise_for_status()
                story_ids = response.json()[:limit]
                
                # Fetch individual stories
                stories = []
                for story_id in story_ids:
                    try:
                        story_response = requests.get(
                            f"{self.hackernews_url}/item/{story_id}.json",
                            timeout=self.timeout
                        )
                        story_response.raise_for_status()
                        story = story_response.json()
                        
                        if story:
                            stories.append({
                                'title': story.get('title'),
                                'url': story.get('url'),
                                'score': story.get('score'),
                                'author': story.get('by'),
                                'time': story.get('time'),
                                'comments': story.get('descendants', 0),
                                'type': story.get('type')
                            })
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch story {story_id}: {e}")
                        continue
                
                logger.info(f"Successfully fetched {len(stories)} Hacker News stories")
                return stories
                
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
    
    def fetch_data(self, 
                   newsapi_category: str = 'technology',
                   hn_limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive news data from multiple sources
        
        Args:
            newsapi_category: Category for NewsAPI
            hn_limit: Number of Hacker News stories to fetch
            
        Returns:
            Dictionary containing all news data or None if failed
        """
        logger.info("Starting comprehensive news data collection")
        
        # Fetch NewsAPI headlines (if key available)
        newsapi_articles = self.fetch_newsapi_headlines(category=newsapi_category)
        
        # Fetch Hacker News stories
        hn_stories = self.fetch_hackernews_top(limit=hn_limit)
        
        # If both failed, return None
        if newsapi_articles is None and hn_stories is None:
            logger.error("All news data collection failed")
            return None
        
        # Process and enrich the data
        enriched_data = self._enrich_data(
            newsapi_articles or [],
            hn_stories or [],
            newsapi_category
        )
        
        return enriched_data
    
    def _enrich_data(self, 
                     newsapi_articles: List[Dict],
                     hn_stories: List[Dict],
                     category: str) -> Dict[str, Any]:
        """Process and enrich news data"""
        
        # Process NewsAPI articles
        processed_newsapi = []
        for article in newsapi_articles[:10]:  # Limit to top 10
            processed_newsapi.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'source': article.get('source', {}).get('name'),
                'published_at': article.get('publishedAt'),
                'author': article.get('author')
            })
        
        # Calculate some stats
        total_articles = len(processed_newsapi) + len(hn_stories)
        
        # Get unique sources
        sources = set()
        if processed_newsapi:
            sources.update([a.get('source') for a in processed_newsapi if a.get('source')])
        if hn_stories:
            sources.add('Hacker News')
        
        return {
            'total_articles': total_articles,
            'newsapi_count': len(processed_newsapi),
            'hackernews_count': len(hn_stories),
            'category': category,
            'sources': list(sources),
            'newsapi_articles': processed_newsapi,
            'hackernews_stories': hn_stories,
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success'
        }

def main():
    """Main execution function"""
    # You can set NEWSAPI_KEY environment variable for NewsAPI access
    # Otherwise, it will only fetch Hacker News
    collector = NewsDataCollector()
    
    logger.info("Starting news data collection")
    data = collector.fetch_data(newsapi_category='technology', hn_limit=10)
    
    if data:
        logger.info("News data collection successful")
        print("\n=== News Data Collection ===")
        print(f"Total Articles: {data['total_articles']}")
        print(f"NewsAPI Articles: {data['newsapi_count']}")
        print(f"Hacker News Stories: {data['hackernews_count']}")
        print(f"Sources: {', '.join(data['sources'])}")
        
        if data['newsapi_articles']:
            print("\n📰 Top NewsAPI Headlines:")
            for i, article in enumerate(data['newsapi_articles'][:3], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                if article['description']:
                    print(f"   {article['description'][:100]}...")
        
        if data['hackernews_stories']:
            print("\n🔥 Top Hacker News Stories:")
            for i, story in enumerate(data['hackernews_stories'][:3], 1):
                print(f"\n{i}. {story['title']}")
                print(f"   Score: {story['score']} | Comments: {story['comments']} | By: {story['author']}")
        
        print(f"\nCollection Time: {data['collection_time']}")
        
        return data
    else:
        logger.error("News data collection failed")
        return None

if __name__ == "__main__":
    main()
