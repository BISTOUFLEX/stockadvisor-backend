"""
Stock data scraper tool for MCP.

Retrieves stock price data, historical information, and basic metrics
from public financial data sources.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx
from src.utils.logger import app_logger
from src.utils.config import config


class StockScraper:
    """
    Scraper for stock market data.
    
    Retrieves price data, historical information, and basic metrics
    for stocks from public sources.
    """
    
    def __init__(self):
        """Initialize the stock scraper."""
        self.client = httpx.Client(timeout=config.SCRAPING_TIMEOUT)
        self.base_url = "https://query1.finance.yahoo.com"
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock data for a symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        
        Returns:
            Dictionary containing stock data
        """
        try:
            # Using Yahoo Finance API (public endpoint)
            url = f"{self.base_url}/v10/finance/quoteSummary/{symbol}"
            params = {
                "modules": "price,summaryDetail,financialData"
            }
            
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "quoteSummary" not in data or "result" not in data["quoteSummary"]:
                raise ValueError(f"No data found for symbol {symbol}")
            
            result = data["quoteSummary"]["result"][0]
            
            return {
                "symbol": symbol,
                "price": result.get("price", {}).get("regularMarketPrice", {}).get("raw", 0),
                "currency": result.get("price", {}).get("currency", "USD"),
                "market_cap": result.get("summaryDetail", {}).get("marketCap", {}).get("raw", 0),
                "pe_ratio": result.get("summaryDetail", {}).get("trailingPE", {}).get("raw", 0),
                "dividend_yield": result.get("summaryDetail", {}).get("dividendYield", {}).get("raw", 0),
                "fifty_two_week_high": result.get("summaryDetail", {}).get("fiftyTwoWeekHigh", {}).get("raw", 0),
                "fifty_two_week_low": result.get("summaryDetail", {}).get("fiftyTwoWeekLow", {}).get("raw", 0),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            app_logger.error(f"Error scraping stock data for {symbol}: {str(e)}")
            raise
    
    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        Get historical stock data.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y')
        
        Returns:
            Dictionary containing historical data
        """
        try:
            url = f"{self.base_url}/v7/finance/download/{symbol}"
            
            # Map period to interval
            period_map = {
                "1d": ("1d", "1m"),
                "5d": ("5d", "15m"),
                "1mo": ("1mo", "1d"),
                "3mo": ("3mo", "1d"),
                "6mo": ("6mo", "1d"),
                "1y": ("1y", "1d"),
                "2y": ("2y", "1wk"),
                "5y": ("5y", "1wk"),
                "10y": ("10y", "1mo")
            }
            
            period_val, interval = period_map.get(period, ("1y", "1d"))
            
            params = {
                "period1": int((datetime.now() - timedelta(days=365)).timestamp()),
                "period2": int(datetime.now().timestamp()),
                "interval": interval,
                "events": "history"
            }
            
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            # Parse CSV response
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                raise ValueError(f"No historical data found for {symbol}")
            
            headers = lines[0].split(',')
            data_points = []
            
            for line in lines[1:]:
                values = line.split(',')
                data_points.append({
                    "date": values[0],
                    "open": float(values[1]) if values[1] != "null" else None,
                    "high": float(values[2]) if values[2] != "null" else None,
                    "low": float(values[3]) if values[3] != "null" else None,
                    "close": float(values[4]) if values[4] != "null" else None,
                    "volume": int(values[5]) if values[5] != "null" else 0,
                    "adj_close": float(values[6]) if values[6] != "null" else None
                })
            
            return {
                "symbol": symbol,
                "period": period,
                "data_points": data_points,
                "count": len(data_points),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            app_logger.error(f"Error scraping historical data for {symbol}: {str(e)}")
            raise
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
