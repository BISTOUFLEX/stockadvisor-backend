"""
Unit tests for the analyzer module.

Tests technical analysis and sentiment analysis functionality.
"""

import pytest
from src.mcp.tools.analyzer import TechnicalAnalyzer, SentimentAnalyzer


class TestTechnicalAnalyzer:
    """Tests for TechnicalAnalyzer."""
    
    def test_calculate_moving_average(self):
        """Test moving average calculation."""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
        ma = TechnicalAnalyzer.calculate_moving_average(prices, period=3)
        
        assert len(ma) > 0
        assert all(isinstance(x, float) for x in ma)
        assert ma[0] == pytest.approx(101.0)  # (100+102+101)/3
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        prices = [100 + i for i in range(30)]  # Uptrend
        rsi = TechnicalAnalyzer.calculate_rsi(prices, period=14)
        
        assert 0 <= rsi <= 100
        assert rsi > 50  # Should be high for uptrend
    
    def test_calculate_rsi_downtrend(self):
        """Test RSI in downtrend."""
        prices = [100 - i for i in range(30)]  # Downtrend
        rsi = TechnicalAnalyzer.calculate_rsi(prices, period=14)
        
        assert 0 <= rsi <= 100
        assert rsi < 50  # Should be low for downtrend
    
    def test_calculate_macd(self):
        """Test MACD calculation."""
        prices = [100 + i for i in range(50)]
        macd = TechnicalAnalyzer.calculate_macd(prices)
        
        assert "macd" in macd
        assert "signal" in macd
        assert "histogram" in macd
        assert isinstance(macd["macd"], float)
    
    def test_analyze_trend_bullish(self):
        """Test trend analysis for bullish trend."""
        prices = [100, 102, 104, 106, 108, 110]
        trend = TechnicalAnalyzer.analyze_trend(prices)
        
        assert trend["trend"] == "bullish"
        assert trend["strength"] > 0
        assert trend["pct_change"] > 0
    
    def test_analyze_trend_bearish(self):
        """Test trend analysis for bearish trend."""
        prices = [110, 108, 106, 104, 102, 100]
        trend = TechnicalAnalyzer.analyze_trend(prices)
        
        assert trend["trend"] == "bearish"
        assert trend["strength"] > 0
        assert trend["pct_change"] < 0
    
    def test_analyze_trend_neutral(self):
        """Test trend analysis for neutral trend."""
        prices = [100, 101, 100, 101, 100, 101]
        trend = TechnicalAnalyzer.analyze_trend(prices)
        
        assert trend["trend"] == "neutral"


class TestSentimentAnalyzer:
    """Tests for SentimentAnalyzer."""
    
    def test_analyze_positive_text(self):
        """Test sentiment analysis for positive text."""
        text = "Stock surge rally gain bull strong outperform"
        sentiment = SentimentAnalyzer.analyze_text(text)
        
        assert sentiment["sentiment"] == "positive"
        assert sentiment["score"] > 0
        assert sentiment["positive_keywords"] > 0
    
    def test_analyze_negative_text(self):
        """Test sentiment analysis for negative text."""
        text = "Stock plunge crash fall bear weak underperform"
        sentiment = SentimentAnalyzer.analyze_text(text)
        
        assert sentiment["sentiment"] == "negative"
        assert sentiment["score"] < 0
        assert sentiment["negative_keywords"] > 0
    
    def test_analyze_neutral_text(self):
        """Test sentiment analysis for neutral text."""
        text = "The stock price is at 100 dollars today"
        sentiment = SentimentAnalyzer.analyze_text(text)
        
        assert sentiment["sentiment"] == "neutral"
        assert sentiment["score"] == 0
    
    def test_analyze_news_sentiment(self):
        """Test sentiment analysis for news articles."""
        articles = [
            {
                "title": "Stock surge on good earnings",
                "summary": "Company outperforms expectations"
            },
            {
                "title": "Stock falls on weak guidance",
                "summary": "Company misses targets"
            }
        ]
        
        sentiment = SentimentAnalyzer.analyze_news_sentiment(articles)
        
        assert "overall_sentiment" in sentiment
        assert "average_score" in sentiment
        assert "article_sentiments" in sentiment
        assert len(sentiment["article_sentiments"]) == 2
    
    def test_analyze_empty_articles(self):
        """Test sentiment analysis with empty articles."""
        sentiment = SentimentAnalyzer.analyze_news_sentiment([])
        
        assert sentiment["overall_sentiment"] == "neutral"
        assert sentiment["average_score"] == 0.0
        assert len(sentiment["article_sentiments"]) == 0