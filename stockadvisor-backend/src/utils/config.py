"""
Configuration module for StockAdvisor+ Bot backend.

This module loads environment variables and provides configuration
settings for the entire application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration class.
    
    Loads all configuration from environment variables with sensible defaults.
    """
    
    # Backend Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Ollama Settings
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stockadvisor.db")
    
    # Scraping Configuration
    SCRAPING_DELAY: int = int(os.getenv("SCRAPING_DELAY", "2"))
    SCRAPING_TIMEOUT: int = int(os.getenv("SCRAPING_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # News Sources
    NEWS_SOURCES: list = os.getenv("NEWS_SOURCES", "reuters,bloomberg,cnbc").split(",")
    
    # API Keys
    ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")
    FINNHUB_KEY: str = os.getenv("FINNHUB_KEY", "")


# Create a global config instance
config = Config()
