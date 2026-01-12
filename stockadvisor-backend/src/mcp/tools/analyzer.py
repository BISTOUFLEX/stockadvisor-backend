"""
Analysis tools for MCP.

Provides technical analysis, sentiment analysis, and data processing capabilities.
"""

from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from src.utils.logger import app_logger


class TechnicalAnalyzer:
    """
    Technical analysis tool for stock data.
    
    Calculates technical indicators and identifies trends.
    """
    
    @staticmethod
    def calculate_moving_average(prices: List[float], period: int = 20) -> List[float]:
        """
        Calculate simple moving average.
        
        Args:
            prices: List of prices
            period: Period for moving average
        
        Returns:
            List of moving average values
        """
        if len(prices) < period:
            return []
        
        ma = []
        for i in range(len(prices) - period + 1):
            ma.append(np.mean(prices[i:i + period]))
        
        return ma
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of prices
            period: Period for RSI calculation
        
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 0.0
        
        deltas = np.diff(prices)
        seed = deltas[:period + 1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        # Handle edge cases: no down moves means strong uptrend -> RSI ~100
        if down == 0:
            if up == 0:
                return 50.0
            return 100.0

        if up == 0:
            return 0.0

        rs = up / down
        rsi = 100 - (100 / (1 + rs))

        return float(rsi)
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: List of prices
        
        Returns:
            Dictionary with MACD, signal line, and histogram
        """
        if len(prices) < 26:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        ema_12 = TechnicalAnalyzer._calculate_ema(prices, 12)
        ema_26 = TechnicalAnalyzer._calculate_ema(prices, 26)
        
        macd = ema_12 - ema_26
        signal = TechnicalAnalyzer._calculate_ema([macd], 9)
        histogram = macd - signal
        
        return {
            "macd": float(macd),
            "signal": float(signal),
            "histogram": float(histogram)
        }
    
    @staticmethod
    def _calculate_ema(prices: List[float], period: int) -> float:
        """
        Calculate Exponential Moving Average.
        
        Args:
            prices: List of prices
            period: Period for EMA
        
        Returns:
            EMA value
        """
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    @staticmethod
    def analyze_trend(prices: List[float]) -> Dict[str, Any]:
        """
        Analyze price trend.
        
        Args:
            prices: List of prices
        
        Returns:
            Dictionary with trend analysis
        """
        if len(prices) < 2:
            return {"trend": "unknown", "strength": 0.0}
        
        # Calculate percentage change
        pct_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] != 0 else 0
        
        # Determine trend
        if pct_change > 5:
            trend = "bullish"
        elif pct_change < -5:
            trend = "bearish"
        else:
            trend = "neutral"
        
        # Calculate trend strength (0-100)
        strength = min(abs(pct_change) * 10, 100)
        
        return {
            "trend": trend,
            "strength": float(strength),
            "pct_change": float(pct_change)
        }


class SentimentAnalyzer:
    """
    Sentiment analysis tool for news and text.
    
    Analyzes sentiment of financial news and text content.
    """
    
    # Sentiment keywords
    POSITIVE_KEYWORDS = {
        "surge", "rally", "gain", "up", "rise", "bull", "strong", "outperform",
        "beat", "growth", "profit", "earnings", "success", "positive", "good",
        "excellent", "outstanding", "record", "high", "boost", "jump"
    }
    
    NEGATIVE_KEYWORDS = {
        "plunge", "crash", "fall", "down", "bear", "weak", "underperform",
        "miss", "loss", "decline", "negative", "bad", "poor", "worst", "low",
        "drop", "tumble", "slump", "sell-off", "concern", "risk"
    }
    
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment analysis
        """
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for keyword in SentimentAnalyzer.POSITIVE_KEYWORDS 
                           if keyword in text_lower)
        negative_count = sum(1 for keyword in SentimentAnalyzer.NEGATIVE_KEYWORDS 
                           if keyword in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total
        
        # Determine sentiment label
        if sentiment_score > 0.2:
            sentiment = "positive"
        elif sentiment_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "score": float(sentiment_score),
            "positive_keywords": positive_count,
            "negative_keywords": negative_count
        }
    
    @staticmethod
    def analyze_news_sentiment(articles: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze overall sentiment of news articles.
        
        Args:
            articles: List of article dictionaries with 'title' and 'summary'
        
        Returns:
            Dictionary with overall sentiment analysis
        """
        if not articles:
            return {
                "overall_sentiment": "neutral",
                "average_score": 0.0,
                "article_sentiments": []
            }
        
        article_sentiments = []
        scores = []
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            sentiment_data = SentimentAnalyzer.analyze_text(text)
            
            article_sentiments.append({
                "title": article.get("title", ""),
                "sentiment": sentiment_data["sentiment"],
                "score": sentiment_data["score"]
            })
            
            scores.append(sentiment_data["score"])
        
        # Calculate average sentiment
        average_score = np.mean(scores) if scores else 0.0
        
        if average_score > 0.2:
            overall_sentiment = "positive"
        elif average_score < -0.2:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "overall_sentiment": overall_sentiment,
            "average_score": float(average_score),
            "article_sentiments": article_sentiments
        }
