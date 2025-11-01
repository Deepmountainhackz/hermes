import feedparser
import pandas as pd
from datetime import datetime

def fetch_rss_feed(feed_url, source_name):
    """
    Fetch and parse an RSS feed.
    """
    try:
        print(f"📰 Fetching {source_name}...")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:  # Feed parsing error
            print(f"   ⚠️  Warning: Feed may have issues")
        
        articles = []
        
        for entry in feed.entries[:10]:  # Get top 10 articles
            articles.append({
                'source': source_name,
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', 'No link'),
                'published': entry.get('published', 'Unknown date'),
                'summary': entry.get('summary', 'No summary')[:200] + '...'  # Truncate
            })
        
        print(f"   ✅ Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"   ❌ Error fetching {source_name}: {e}")
        return []

def fetch_news_feeds():
    """
    Fetch news from multiple RSS feeds.
    """
    print("=" * 70)
    print("HERMES Social Intelligence - News Monitor")
    print("=" * 70)
    print()
    
    # RSS feeds to monitor
    feeds = {
        'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
        'Reuters': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'TechCrunch': 'https://techcrunch.com/feed/',
        'Hacker News': 'https://news.ycombinator.com/rss',
        'NPR': 'https://feeds.npr.org/1001/rss.xml',
        'The Guardian': 'https://www.theguardian.com/world/rss'
    }
    
    all_articles = []
    
    for source, url in feeds.items():
        articles = fetch_rss_feed(url, source)
        all_articles.extend(articles)
        print()
    
    if not all_articles:
        print("❌ No news articles collected")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_articles)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data_NEWS_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    print("=" * 70)
    print(f"✅ Saved {len(df)} news articles to {filename}")
    print("=" * 70)
    print()
    
    # Show recent headlines
    print("📰 Latest Headlines:")
    print()
    
    # Group by source and show top headline from each
    for source in df['source'].unique():
        source_articles = df[df['source'] == source]
        top_article = source_articles.iloc[0]
        print(f"   [{source}]")
        print(f"   {top_article['title']}")
        print(f"   {top_article['link']}")
        print()
    
    return df

def main():
    """Main function"""
    fetch_news_feeds()

if __name__ == "__main__":
    main()