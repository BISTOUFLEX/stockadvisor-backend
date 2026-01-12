"""
FastAPI routes for StockAdvisor+ Bot backend.

Defines all API endpoints for the application.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from src.utils.logger import app_logger
from src.api.schemas import (
    MessageRequest,
    MessageResponse,
    AnalysisRequest,
    AnalysisResponse,
    ComparisonRequest,
    ComparisonResponse,
    HealthResponse,
    ToolsResponse
)

# This will be injected by the main app
router = APIRouter()
agent_orchestrator = None
mcp_server = None
ollama_client = None


def setup_routes(orchestrator, mcp, ollama):
    """
    Setup routes with dependencies.
    
    Args:
        orchestrator: Agent orchestrator instance
        mcp: MCP server instance
        ollama: Ollama client instance
    """
    global agent_orchestrator, mcp_server, ollama_client
    agent_orchestrator = orchestrator
    mcp_server = mcp
    ollama_client = ollama


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status of the service
    """
    try:
        ollama_available = ollama_client.health_check() if ollama_client else False
        mcp_available = mcp_server is not None
        
        return HealthResponse(
            status="healthy" if (ollama_available and mcp_available) else "degraded",
            ollama_available=ollama_available,
            mcp_available=mcp_available,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        app_logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """
    Process chat message.
    
    Args:
        request: Message request
    
    Returns:
        Chat response with analysis
    """
    try:
        if not agent_orchestrator:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        result = await agent_orchestrator.process_message(
            request.user_id,
            request.message
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return MessageResponse(
            success=True,
            user_id=request.user_id,
            response=result["response"],
            analysis=result.get("analysis"),
            tools_used=result.get("tools_used", [])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock.
    
    Args:
        request: Analysis request with stock symbol
    
    Returns:
        Stock analysis report
    """
    try:
        if not mcp_server:
            raise HTTPException(status_code=503, detail="MCP server not initialized")
        
        result = await mcp_server.analyze_stock(request.symbol)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return AnalysisResponse(
            success=True,
            symbol=request.symbol,
            report=result["report"],
            news=result.get("news")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error analyzing stock: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_stocks(request: ComparisonRequest):
    """
    Compare multiple stocks.
    
    Args:
        request: Comparison request with stock symbols
    
    Returns:
        Stock comparison report
    """
    try:
        if not mcp_server:
            raise HTTPException(status_code=503, detail="MCP server not initialized")
        
        if len(request.symbols) < 2:
            raise HTTPException(status_code=400, detail="At least 2 symbols required")
        
        result = await mcp_server.compare_stocks(request.symbols)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ComparisonResponse(
            success=True,
            comparison=result["comparison"],
            analyses=result.get("analyses")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error comparing stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news")
async def get_market_news(limit: int = 20):
    """
    Get market news.
    
    Args:
        limit: Maximum number of articles
    
    Returns:
        Market news with sentiment analysis
    """
    try:
        if not mcp_server:
            raise HTTPException(status_code=503, detail="MCP server not initialized")
        
        result = await mcp_server.get_market_news(limit)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools", response_model=ToolsResponse)
async def get_tools():
    """
    Get available tools.
    
    Returns:
        List of available MCP tools
    """
    try:
        if not mcp_server:
            raise HTTPException(status_code=503, detail="MCP server not initialized")
        
        tools = mcp_server.get_available_tools()
        
        return ToolsResponse(
            tools=tools,
            count=len(tools)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error fetching tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/context/{user_id}")
async def clear_context(user_id: str):
    """
    Clear conversation context for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        Success message
    """
    try:
        if not agent_orchestrator:
            raise HTTPException(status_code=503, detail="Agent not initialized")
        
        agent_orchestrator.clear_context(user_id)
        
        return {"success": True, "message": f"Context cleared for user {user_id}"}
    
    except Exception as e:
        app_logger.error(f"Error clearing context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
