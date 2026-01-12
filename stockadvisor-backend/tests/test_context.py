"""
Unit tests for the conversation context module.

Tests context management and conversation history.
"""

import pytest
from src.agent.context import ConversationContext


class TestConversationContext:
    """Tests for ConversationContext."""
    
    @pytest.fixture
    def context(self):
        """Create a context instance for testing."""
        return ConversationContext("test_user")
    
    def test_context_initialization(self, context):
        """Test context initialization."""
        assert context.user_id == "test_user"
        assert len(context.messages) == 0
        assert len(context.watched_stocks) == 0
        assert isinstance(context.user_preferences, dict)
    
    def test_add_message(self, context):
        """Test adding messages to context."""
        context.add_message("user", "Hello")
        
        assert len(context.messages) == 1
        assert context.messages[0]["role"] == "user"
        assert context.messages[0]["content"] == "Hello"
    
    def test_add_multiple_messages(self, context):
        """Test adding multiple messages."""
        context.add_message("user", "Hello")
        context.add_message("assistant", "Hi there")
        context.add_message("user", "How are you?")
        
        assert len(context.messages) == 3
        assert context.messages[0]["role"] == "user"
        assert context.messages[1]["role"] == "assistant"
        assert context.messages[2]["role"] == "user"
    
    def test_get_conversation_history(self, context):
        """Test retrieving conversation history."""
        context.add_message("user", "Message 1")
        context.add_message("assistant", "Response 1")
        
        history = context.get_conversation_history()
        
        assert len(history) == 2
        assert history[0]["content"] == "Message 1"
        assert history[1]["content"] == "Response 1"
    
    def test_get_conversation_history_with_limit(self, context):
        """Test retrieving conversation history with limit."""
        for i in range(5):
            context.add_message("user", f"Message {i}")
        
        history = context.get_conversation_history(limit=2)
        
        assert len(history) == 2
        assert history[0]["content"] == "Message 3"
        assert history[1]["content"] == "Message 4"
    
    def test_add_watched_stock(self, context):
        """Test adding watched stocks."""
        context.add_watched_stock("AAPL")
        context.add_watched_stock("MSFT")
        
        assert "AAPL" in context.watched_stocks
        assert "MSFT" in context.watched_stocks
        assert len(context.watched_stocks) == 2
    
    def test_add_watched_stock_duplicate(self, context):
        """Test adding duplicate watched stocks."""
        context.add_watched_stock("AAPL")
        context.add_watched_stock("AAPL")
        
        assert context.watched_stocks.count("AAPL") == 1
    
    def test_remove_watched_stock(self, context):
        """Test removing watched stocks."""
        context.add_watched_stock("AAPL")
        context.add_watched_stock("MSFT")
        context.remove_watched_stock("AAPL")
        
        assert "AAPL" not in context.watched_stocks
        assert "MSFT" in context.watched_stocks
    
    def test_set_preference(self, context):
        """Test setting user preferences."""
        context.set_preference("risk_level", "high")
        context.set_preference("currency", "USD")
        
        assert context.user_preferences["risk_level"] == "high"
        assert context.user_preferences["currency"] == "USD"
    
    def test_get_preference(self, context):
        """Test getting user preferences."""
        context.set_preference("risk_level", "medium")
        
        value = context.get_preference("risk_level")
        
        assert value == "medium"
    
    def test_get_preference_default(self, context):
        """Test getting non-existent preference with default."""
        value = context.get_preference("nonexistent", "default_value")
        
        assert value == "default_value"
    
    def test_clear_history(self, context):
        """Test clearing conversation history."""
        context.add_message("user", "Hello")
        context.add_message("assistant", "Hi")
        
        context.clear_history()
        
        assert len(context.messages) == 0
    
    def test_get_system_prompt(self, context):
        """Test system prompt generation."""
        context.add_watched_stock("AAPL")
        context.set_preference("risk_level", "high")
        
        prompt = context.get_system_prompt()
        
        assert "StockAdvisor+" in prompt
        assert "AAPL" in prompt
        assert "test_user" in prompt
    
    def test_max_history_limit(self):
        """Test maximum history limit."""
        context = ConversationContext("test_user", max_history=5)
        
        for i in range(10):
            context.add_message("user", f"Message {i}")
        
        assert len(context.messages) <= 5
    
    def test_context_to_dict(self, context):
        """Test converting context to dictionary."""
        context.add_message("user", "Hello")
        context.add_watched_stock("AAPL")
        context.set_preference("risk_level", "high")
        
        context_dict = context.to_dict()
        
        assert context_dict["user_id"] == "test_user"
        assert len(context_dict["messages"]) == 1
        assert "AAPL" in context_dict["watched_stocks"]
        assert context_dict["user_preferences"]["risk_level"] == "high"