"""
Context management for the conversational agent.

Maintains conversation history and user context.
"""

from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import app_logger


class ConversationContext:
    """
    Manages conversation context and history.
    
    Maintains messages, user preferences, and conversation state.
    """
    
    def __init__(self, user_id: str, max_history: int = 50):
        """
        Initialize conversation context.
        
        Args:
            user_id: Unique user identifier
            max_history: Maximum number of messages to keep
        """
        self.user_id = user_id
        self.max_history = max_history
        self.messages: List[Dict[str, Any]] = []
        self.user_preferences: Dict[str, Any] = {}
        self.watched_stocks: List[str] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata about the message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        
        app_logger.debug(f"Message added for user {self.user_id}: {role}")
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of messages to return
        
        Returns:
            List of messages
        """
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_system_prompt(self) -> str:
        """
        Generate system prompt for the AI agent.
        
        Returns:
            System prompt with context
        """
        watched_stocks_str = ", ".join(self.watched_stocks) if self.watched_stocks else "None"
        
        prompt = f"""You are StockAdvisor+, an intelligent financial advisor chatbot.

Your role is to:
1. Analyze stock market data and provide investment insights
2. Retrieve and analyze financial news
3. Generate recommendations based on technical and sentiment analysis
4. Maintain a conversational and helpful tone

User Profile:
- User ID: {self.user_id}
- Watched Stocks: {watched_stocks_str}
- Preferences: {self.user_preferences}

Available Tools:
- analyze_stock(symbol): Get complete analysis of a stock
- compare_stocks(symbols): Compare multiple stocks
- get_market_news(limit): Get market news and sentiment

Guidelines:
- Always provide data-driven recommendations
- Explain your analysis in simple terms
- Ask clarifying questions if needed
- Remind users that this is not financial advice
- Be honest about limitations and uncertainties

Current Date/Time: {datetime.now().isoformat()}
"""
        return prompt
    
    def add_watched_stock(self, symbol: str):
        """
        Add a stock to user's watched list.
        
        Args:
            symbol: Stock ticker symbol
        """
        if symbol.upper() not in self.watched_stocks:
            self.watched_stocks.append(symbol.upper())
            app_logger.info(f"Added {symbol} to watched stocks for user {self.user_id}")
    
    def remove_watched_stock(self, symbol: str):
        """
        Remove a stock from user's watched list.
        
        Args:
            symbol: Stock ticker symbol
        """
        if symbol.upper() in self.watched_stocks:
            self.watched_stocks.remove(symbol.upper())
            app_logger.info(f"Removed {symbol} from watched stocks for user {self.user_id}")
    
    def set_preference(self, key: str, value: Any):
        """
        Set user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.user_preferences[key] = value
        app_logger.debug(f"Set preference {key}={value} for user {self.user_id}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get user preference.
        
        Args:
            key: Preference key
            default: Default value if not found
        
        Returns:
            Preference value or default
        """
        return self.user_preferences.get(key, default)
    
    def clear_history(self):
        """Clear conversation history."""
        self.messages = []
        app_logger.info(f"Cleared conversation history for user {self.user_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.
        
        Returns:
            Dictionary representation of context
        """
        return {
            "user_id": self.user_id,
            "messages": self.messages,
            "user_preferences": self.user_preferences,
            "watched_stocks": self.watched_stocks,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }
