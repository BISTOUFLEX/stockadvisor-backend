"""
MCP Server for StockAdvisor+ Bot.

Orchestrates all tools and exposes them through a unified interface.
"""

from typing import Dict, Any, List
from src.utils.logger import app_logger
from src.mcp.tools import (
    StockScraper,
    NewsScraper,
    TechnicalAnalyzer,
    SentimentAnalyzer,
    ReportGenerator
)


class MCPServer:
    """
    Model Context Protocol Server.
    
    Manages all available tools and their execution.
    """
    
    def __init__(self):
        """Initialize the MCP server with all tools."""
        self.stock_scraper = StockScraper()
        self.news_scraper = NewsScraper()
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.report_generator = ReportGenerator()
        
        app_logger.info("MCP Server initialized")
    
    async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Perform complete stock analysis.
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Complete analysis report
        """
        try:
            app_logger.info(f"Starting analysis for {symbol}")
            
            # Get stock data
            stock_data = await self.stock_scraper.get_stock_data(symbol)
            
            # Get historical data for technical analysis
            historical_data = await self.stock_scraper.get_historical_data(symbol, "1y")
            prices = [dp["close"] for dp in historical_data["data_points"] if dp["close"]]
            
            # Perform technical analysis
            technical_analysis = {
                "trend": self.technical_analyzer.analyze_trend(prices),
                "rsi": self.technical_analyzer.calculate_rsi(prices),
                "macd": self.technical_analyzer.calculate_macd(prices),
                "moving_average_20": self.technical_analyzer.calculate_moving_average(prices, 20)
            }
            
            # Get news
            news_data = await self.news_scraper.get_news_for_symbol(symbol, limit=10)
            
            # Analyze sentiment
            news_sentiment = self.sentiment_analyzer.analyze_news_sentiment(
                news_data["articles"]
            )
            
            # Generate report
            report = self.report_generator.generate_stock_analysis_report(
                symbol,
                stock_data,
                technical_analysis,
                news_sentiment
            )
            
            app_logger.info(f"Analysis completed for {symbol}")
            
            return {
                "success": True,
                "symbol": symbol,
                "report": report,
                "news": news_data["articles"][:5],  # Top 5 articles
                "historical_data": historical_data
            }
        
        except Exception as e:
            app_logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {
                "success": False,
                "symbol": symbol,
                "error": str(e)
            }
    
    async def compare_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Compare multiple stocks.
        
        Args:
            symbols: List of stock ticker symbols
        
        Returns:
            Comparison report
        """
        try:
            app_logger.info(f"Starting comparison for {symbols}")
            
            analyses = {}
            
            for symbol in symbols:
                try:
                    result = await self.analyze_stock(symbol)
                    if result["success"]:
                        analyses[symbol] = result["report"]
                except Exception as e:
                    app_logger.warning(f"Error analyzing {symbol}: {str(e)}")
            
            # Generate comparison
            comparison = self.report_generator.generate_comparison_report(
                symbols,
                analyses
            )
            
            app_logger.info(f"Comparison completed for {symbols}")
            
            return {
                "success": True,
                "comparison": comparison,
                "analyses": analyses
            }
        
        except Exception as e:
            app_logger.error(f"Error comparing stocks: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_market_news(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get general market news.
        
        Args:
            limit: Maximum number of articles
        
        Returns:
            Market news with sentiment analysis
        """
        try:
            app_logger.info("Fetching market news")
            
            news_data = await self.news_scraper.get_market_news(limit)
            sentiment = self.sentiment_analyzer.analyze_news_sentiment(
                news_data["articles"]
            )
            
            return {
                "success": True,
                "articles": news_data["articles"],
                "sentiment": sentiment
            }
        
        except Exception as e:
            app_logger.error(f"Error fetching market news: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of available tools.
        
        Returns:
            List of tool descriptions
        """
        return [
            {
                "name": "analyze_stock",
                "description": "Perform complete analysis of a stock (technical + sentiment)",
                "parameters": {
                    "symbol": "Stock ticker symbol (e.g., 'AAPL', 'MSFT')"
                }
            },
            {
                "name": "compare_stocks",
                "description": "Compare multiple stocks side by side",
                "parameters": {
                    "symbols": "List of stock ticker symbols"
                }
            },
            {
                "name": "get_market_news",
                "description": "Get general market news and sentiment",
                "parameters": {
                    "limit": "Maximum number of articles (default: 20)"
                }
            }
        ]
    
    def close(self):
        """Close all resources."""
        self.stock_scraper.close()
        self.news_scraper.close()
        app_logger.info("MCP Server closed")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
