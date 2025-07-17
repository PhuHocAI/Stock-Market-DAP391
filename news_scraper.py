import requests
import yfinance as yf
from datetime import datetime
import feedparser
import re

def get_stock_news(symbol):
    """
    Get news articles for a specific stock symbol
    """
    news_articles = []
    
    try:
        # Method 1: Using yfinance news
        stock = yf.Ticker(symbol)
        news = stock.news
        
        for article in news[:10]:  # Get top 10 articles
            news_articles.append({
                'title': article.get('title', 'No title'),
                'summary': clean_text(article.get('summary', 'No summary available')),
                'link': article.get('link', ''),
                'published': format_timestamp(article.get('providerPublishTime', 0)),
                'source': article.get('publisher', 'Unknown'),
                'image': article.get('thumbnail', {}).get('resolutions', [{}])[-1].get('url', '') if article.get('thumbnail') else ''
            })
        
        # Method 2: RSS feeds for additional news
        rss_sources = [
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
            f"https://finance.yahoo.com/rss/headline?s={symbol}"
        ]
        
        for rss_url in rss_sources:
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:5]:  # Get 5 articles from each source
                    news_articles.append({
                        'title': entry.get('title', 'No title'),
                        'summary': clean_text(entry.get('summary', 'No summary available')),
                        'link': entry.get('link', ''),
                        'published': format_rss_date(entry.get('published', '')),
                        'source': 'Yahoo Finance',
                        'image': extract_image_from_content(entry.get('content', []))
                    })
            except:
                continue
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in news_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        return unique_articles[:15]  # Return top 15 unique articles
    
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def clean_text(text):
    """
    Clean and format text content
    """
    if not text:
        return "No content available"
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Limit length
    if len(text) > 300:
        text = text[:300] + "..."
    
    return text

def format_timestamp(timestamp):
    """
    Format Unix timestamp to readable date
    """
    try:
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        return "Unknown date"
    except:
        return "Unknown date"

def format_rss_date(date_str):
    """
    Format RSS date string to readable format
    """
    try:
        if date_str:
            # Parse common RSS date formats
            dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d %H:%M")
        return "Unknown date"
    except:
        try:
            # Try alternative format
            dt = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return "Unknown date"

def extract_image_from_content(content):
    """
    Extract image URL from RSS content
    """
    try:
        if content and isinstance(content, list) and len(content) > 0:
            content_text = content[0].get('value', '')
            # Look for image URLs in content
            img_match = re.search(r'<img[^>]+src="([^"]+)"', content_text)
            if img_match:
                return img_match.group(1)
        return ''
    except:
        return ''

def get_market_news():
    """
    Get general market news
    """
    market_news = []
    
    try:
        # General market RSS feeds
        market_feeds = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US",
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI&region=US&lang=en-US",
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^IXIC&region=US&lang=en-US"
        ]
        
        for feed_url in market_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    market_news.append({
                        'title': entry.get('title', 'No title'),
                        'summary': clean_text(entry.get('summary', 'No summary available')),
                        'link': entry.get('link', ''),
                        'published': format_rss_date(entry.get('published', '')),
                        'source': 'Yahoo Finance',
                        'image': extract_image_from_content(entry.get('content', []))
                    })
            except:
                continue
        
        return market_news[:10]
    
    except Exception as e:
        print(f"Error fetching market news: {e}")
        return []

def search_news_by_keyword(keyword, limit=10):
    """
    Search for news articles by keyword
    """
    try:
        # This is a simplified version - in production, you might want to use
        # news APIs like NewsAPI, Alpha Vantage, or similar services
        
        search_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={keyword}&region=US&lang=en-US"
        feed = feedparser.parse(search_url)
        
        articles = []
        for entry in feed.entries[:limit]:
            articles.append({
                'title': entry.get('title', 'No title'),
                'summary': clean_text(entry.get('summary', 'No summary available')),
                'link': entry.get('link', ''),
                'published': format_rss_date(entry.get('published', '')),
                'source': 'Yahoo Finance',
                'image': extract_image_from_content(entry.get('content', []))
            })
        
        return articles
    
    except Exception as e:
        print(f"Error searching news: {e}")
        return []