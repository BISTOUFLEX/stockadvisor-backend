"""
Pydantic schemas for API validation.

Defines request and response models for the FastAPI endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    """Request model for chat messages."""
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User message")


class MessageResponse(BaseModel):
    """Response model for chat messages."""
    success: bool
    user_id: str
    response: str
    analysis: Optional[Dict[str, Any]] = None
    tools_used: List[str] = []


class AnalysisRequest(BaseModel):
    """Request model for stock analysis."""
    symbol: str = Field(..., description="Stock ticker symbol")


class StockDataResponse(BaseModel):
    """Response model for stock data."""
    symbol: str
    price: float
    currency: str
    market_cap: float
    pe_ratio: float
    dividend_yield: float
    timestamp: str


class AnalysisResponse(BaseModel):
    """Response model for stock analysis."""
    success: bool
    symbol: str
    report: Optional[Dict[str, Any]] = None
    news: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class ComparisonRequest(BaseModel):
    """Request model for stock comparison."""
    symbols: List[str] = Field(..., description="List of stock ticker symbols")


class ComparisonResponse(BaseModel):
    """Response model for stock comparison."""
    success: bool
    comparison: Optional[Dict[str, Any]] = None
    analyses: Optional[Dict[str, Dict[str, Any]]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    ollama_available: bool
    mcp_available: bool
    timestamp: str


class ToolsResponse(BaseModel):
    """Response model for available tools."""
    tools: List[Dict[str, Any]]
    count: int
