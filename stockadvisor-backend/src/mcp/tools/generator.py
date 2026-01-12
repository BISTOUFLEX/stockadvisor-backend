"""
Report generation tools for MCP.

Generates analysis reports and recommendations.
"""

from typing import Dict, Any
from datetime import datetime
from src.utils.logger import app_logger


class ReportGenerator:
    """
    Generator for analysis reports and recommendations.
    
    Creates formatted reports combining technical and sentiment analysis.
    """
    
    @staticmethod
    def generate_stock_analysis_report(
        symbol: str,
        stock_data: Dict[str, Any],
        technical_analysis: Dict[str, Any],
        news_sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive stock analysis report.
        
        Args:
            symbol: Stock ticker symbol
            stock_data: Current stock data
            technical_analysis: Technical analysis results
            news_sentiment: News sentiment analysis
        
        Returns:
            Dictionary containing the analysis report
        """
        try:
            # Generate recommendation based on analysis
            recommendation = ReportGenerator._generate_recommendation(
                technical_analysis,
                news_sentiment
            )
            
            # Generate summary
            summary = ReportGenerator._generate_summary(
                symbol,
                technical_analysis,
                news_sentiment
            )
            
            report = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "current_price": stock_data.get("price", 0),
                "currency": stock_data.get("currency", "USD"),
                
                # Technical Analysis
                "technical_analysis": {
                    "trend": technical_analysis.get("trend", {}).get("trend", "unknown"),
                    "trend_strength": technical_analysis.get("trend", {}).get("strength", 0),
                    "rsi": technical_analysis.get("rsi", 0),
                    "macd": technical_analysis.get("macd", {})
                },
                
                # News Sentiment
                "news_sentiment": {
                    "overall_sentiment": news_sentiment.get("overall_sentiment", "neutral"),
                    "average_score": news_sentiment.get("average_score", 0),
                    "article_count": len(news_sentiment.get("article_sentiments", []))
                },
                
                # Recommendation
                "recommendation": recommendation["action"],
                "confidence": recommendation["confidence"],
                "rationale": recommendation["rationale"],
                
                # Summary
                "summary": summary,
                
                # Key Metrics
                "metrics": {
                    "market_cap": stock_data.get("market_cap", 0),
                    "pe_ratio": stock_data.get("pe_ratio", 0),
                    "dividend_yield": stock_data.get("dividend_yield", 0),
                    "52_week_high": stock_data.get("fifty_two_week_high", 0),
                    "52_week_low": stock_data.get("fifty_two_week_low", 0)
                }
            }
            
            return report
        
        except Exception as e:
            app_logger.error(f"Error generating report for {symbol}: {str(e)}")
            raise
    
    @staticmethod
    def _generate_recommendation(
        technical_analysis: Dict[str, Any],
        news_sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate investment recommendation.
        
        Args:
            technical_analysis: Technical analysis data
            news_sentiment: News sentiment data
        
        Returns:
            Dictionary with recommendation details
        """
        trend = technical_analysis.get("trend", {}).get("trend", "neutral")
        trend_strength = technical_analysis.get("trend", {}).get("strength", 0)
        rsi = technical_analysis.get("rsi", 50)
        sentiment = news_sentiment.get("overall_sentiment", "neutral")
        sentiment_score = news_sentiment.get("average_score", 0)
        
        # Calculate recommendation score
        score = 0
        
        # Technical analysis contribution
        if trend == "bullish":
            score += trend_strength / 100 * 40
        elif trend == "bearish":
            score -= trend_strength / 100 * 40
        
        if rsi < 30:
            score += 15  # Oversold
        elif rsi > 70:
            score -= 15  # Overbought
        
        # Sentiment contribution
        if sentiment == "positive":
            score += abs(sentiment_score) * 30
        elif sentiment == "negative":
            score -= abs(sentiment_score) * 30
        
        # Determine action and confidence
        if score > 20:
            action = "BUY"
            confidence = min(abs(score) / 100, 1.0)
        elif score < -20:
            action = "SELL"
            confidence = min(abs(score) / 100, 1.0)
        else:
            action = "HOLD"
            confidence = 0.5
        
        # Generate rationale
        rationale_parts = []
        
        if trend == "bullish":
            rationale_parts.append(f"Strong {trend} trend ({trend_strength:.1f}% strength)")
        elif trend == "bearish":
            rationale_parts.append(f"Strong {trend} trend ({trend_strength:.1f}% strength)")
        
        if rsi < 30:
            rationale_parts.append("Stock is oversold (RSI < 30)")
        elif rsi > 70:
            rationale_parts.append("Stock is overbought (RSI > 70)")
        
        if sentiment == "positive":
            rationale_parts.append(f"Positive news sentiment ({sentiment_score:.2f})")
        elif sentiment == "negative":
            rationale_parts.append(f"Negative news sentiment ({sentiment_score:.2f})")
        
        rationale = "; ".join(rationale_parts) if rationale_parts else "Mixed signals"
        
        return {
            "action": action,
            "confidence": float(confidence),
            "score": float(score),
            "rationale": rationale
        }
    
    @staticmethod
    def _generate_summary(
        symbol: str,
        technical_analysis: Dict[str, Any],
        news_sentiment: Dict[str, Any]
    ) -> str:
        """
        Generate text summary of analysis.
        
        Args:
            symbol: Stock symbol
            technical_analysis: Technical analysis data
            news_sentiment: News sentiment data
        
        Returns:
            Text summary
        """
        trend = technical_analysis.get("trend", {}).get("trend", "unknown")
        sentiment = news_sentiment.get("overall_sentiment", "neutral")
        
        summary = f"Stock {symbol} is showing a {trend} technical trend with {sentiment} news sentiment. "
        
        if trend == "bullish" and sentiment == "positive":
            summary += "Both technical and fundamental indicators are positive."
        elif trend == "bearish" and sentiment == "negative":
            summary += "Both technical and fundamental indicators are negative."
        else:
            summary += "Technical and fundamental indicators are mixed."
        
        return summary
    
    @staticmethod
    def generate_comparison_report(
        symbols: list,
        analyses: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comparison report for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            analyses: Dictionary of analyses for each symbol
        
        Returns:
            Comparison report
        """
        try:
            comparison = {
                "timestamp": datetime.now().isoformat(),
                "symbols": symbols,
                "stocks": []
            }
            
            for symbol in symbols:
                if symbol in analyses:
                    analysis = analyses[symbol]
                    comparison["stocks"].append({
                        "symbol": symbol,
                        "price": analysis.get("current_price", 0),
                        "recommendation": analysis.get("recommendation", "HOLD"),
                        "confidence": analysis.get("confidence", 0),
                        "trend": analysis.get("technical_analysis", {}).get("trend", "unknown"),
                        "sentiment": analysis.get("news_sentiment", {}).get("overall_sentiment", "neutral")
                    })
            
            return comparison
        
        except Exception as e:
            app_logger.error(f"Error generating comparison report: {str(e)}")
            raise
