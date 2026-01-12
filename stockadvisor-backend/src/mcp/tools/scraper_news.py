"""
Financial news scraper tool for MCP.

Retrieves financial news and market updates from public sources.
"""

from typing import Dict, Any, List
from datetime import datetime
import feedparser
import httpx
from bs4 import BeautifulSoup
from src.utils.logger import app_logger
from src.utils.config import config


class NewsScraper:
    """
    Scraper for financial news and market updates.
    
    Retrieves news from RSS feeds and public financial news sources.
    """
    
    def __init__(self):
        """Initialize the news scraper."""
        self.client = httpx.Client(timeout=config.SCRAPING_TIMEOUT)
        
        # RSS feeds for financial news
        self.rss_feeds = {
            "reuters": "https://feeds.reuters.com/reuters/businessNews",
            "bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
            "cnbc": "https://feeds.cnbc.com/cnbc/financialnews",
            "marketwatch": "https://feeds.marketwatch.com/marketwatch/topstories/"
        }
    
    async def get_news_for_symbol(
        self,
        symbol: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get recent news for a specific stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of news articles to retrieve
        
        Returns:
            Dictionary containing news articles
        """
        try:
            articles = []
            
            # Search for news mentioning the symbol
            search_url = "https://feeds.bloomberg.com/markets/news.rss"
            
            for source_name, feed_url in self.rss_feeds.items():
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:limit]:
                        # Check if symbol is mentioned in title or summary
                        title = entry.get("title", "").upper()
                        summary = entry.get("summary", "").upper()
                        
                        if symbol.upper() in title or symbol.upper() in summary:
                            articles.append({
                                "source": source_name,
                                "title": entry.get("title", ""),
                                "summary": entry.get("summary", "")[:500],
                                "link": entry.get("link", ""),
                                "published": entry.get("published", ""),
                                "author": entry.get("author", "")
                            })
                
                except Exception as e:
                    app_logger.warning(f"Error fetching from {source_name}: {str(e)}")
                    continue
            
            return {
                "symbol": symbol,
                "articles": articles[:limit],
                "count": len(articles),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            app_logger.error(f"Error scraping news for {symbol}: {str(e)}")
            raise
    
    async def get_market_news(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get general market news.
        
        Args:
            limit: Maximum number of articles to retrieve
        
        Returns:
            Dictionary containing market news articles
        """
        try:
            articles = []
            
            for source_name, feed_url in self.rss_feeds.items():
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:limit]:
                        articles.append({
                            "source": source_name,
                            "title": entry.get("title", ""),
                            "summary": entry.get("summary", "")[:500],
                            "link": entry.get("link", ""),
                            "published": entry.get("published", ""),
                            "author": entry.get("author", "")
                        })
                
                except Exception as e:
                    app_logger.warning(f"Error fetching from {source_name}: {str(e)}")
                    continue
            
            return {
                "articles": articles[:limit],
                "count": len(articles),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            app_logger.error(f"Error scraping market news: {str(e)}")
            raise
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
