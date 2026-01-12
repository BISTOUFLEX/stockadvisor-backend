"""
API package for StockAdvisor+ Bot backend.

Contains FastAPI routes and schemas.
"""

from .routes import router, setup_routes
from .schemas import (
    MessageRequest,
    MessageResponse,
    AnalysisRequest,
    AnalysisResponse
)

__all__ = [
    "router",
    "setup_routes",
    "MessageRequest",
    "MessageResponse",
    "AnalysisRequest",
    "AnalysisResponse"
]
