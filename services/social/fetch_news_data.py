import feedparser
import pandas as pd
import sqlite3
from datetime import datetime

DATABASE_PATH = 'hermes.db'

def fetch_rss_feed(feed_url, source_name):
    """
    Fetch and parse an RSS feed.
    """
    try:
        print(f"📰 Fetching {source_name}...")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"   ⚠️  Warning: Feed may have issues")
        
        articles = []
        
        for entry in feed.entries[:10]:
            articles.append({
                'timestamp': datetime.now().isoformat(),
                'source': source_name,
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', 'No link'),
                'published': entry.get('published', 'Unknown date'),
                'summary': entry.get('summary', 'No summary')[:200] + '...'
            })
        
        print(f"   ✅ Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"   ❌ Error fetching {source_name}: {e}")
        return []

def save_to_database(articles):
    """
    Save news articles to database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.DataFrame(articles)
    
    try:
        df.to_sql('news', conn, if_exists='append', index=False)
        print(f"✅ Saved {len(df)} news articles to database")
        return len(df)
    except sqlite3.IntegrityError:
        print(f"⚠️  Some articles already exist in database (skipped duplicates)")
        return 0
    except Exception as e:
        print(f"❌ Database error: {e}")
        return 0
    finally:
        conn.close()

def fetch_news_feeds():
    """
    Fetch news from multiple RSS feeds.
    """
    print("=" * 70)
    print("HERMES Social Intelligence - News Monitor (Database Mode)")
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
    
    # Save to database
    saved_count = save_to_database(all_articles)
    
    print("=" * 70)
    print(f"📊 Collection Summary:")
    print(f"   Total articles: {len(all_articles)}")
    print(f"   Saved to database: {saved_count}")
    print(f"   Sources: {len(feeds)}")
    print("=" * 70)
    print()
    
    # Show recent headlines
    print("📰 Latest Headlines:")
    print()
    
    df = pd.DataFrame(all_articles)
    
    for source in df['source'].unique():
        source_articles = df[df['source'] == source]
        top_article = source_articles.iloc[0]
        print(f"   [{source}]")
        print(f"   {top_article['title']}")
        print()
    
    return df

def main():
    """Main function"""
    fetch_news_feeds()

if __name__ == "__main__":
    main()