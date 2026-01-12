"""
Main entry point for StockAdvisor+ Bot backend.

Initializes FastAPI application with all components.
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.logger import app_logger
from src.utils.config import config
from src.ollama.client import OllamaClient
from src.mcp.server import MCPServer
from src.agent.orchestrator import AgentOrchestrator
from src.api import router, setup_routes


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="StockAdvisor+ Bot API",
        description="Conversational AI agent for stock market analysis",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize components
    app_logger.info("Initializing StockAdvisor+ Bot backend...")
    
    try:
        # Initialize Ollama client
        ollama_client = OllamaClient()
        
        # Check Ollama availability
        if not ollama_client.health_check():
            app_logger.warning("Ollama service is not available. Some features may not work.")
        else:
            app_logger.info("Ollama service is available")
        
        # Initialize MCP server
        mcp_server = MCPServer()
        app_logger.info("MCP server initialized")
        
        # Initialize agent orchestrator
        agent_orchestrator = AgentOrchestrator(ollama_client, mcp_server)
        app_logger.info("Agent orchestrator initialized")
        
        # Setup routes with dependencies
        setup_routes(agent_orchestrator, mcp_server, ollama_client)
        
        # Include routes
        app.include_router(router, prefix="/api")
        
        # Store components in app state for cleanup
        app.state.ollama_client = ollama_client
        app.state.mcp_server = mcp_server
        app.state.agent_orchestrator = agent_orchestrator
        
        app_logger.info("Backend initialized successfully")
    
    except Exception as e:
        app_logger.error(f"Error initializing backend: {str(e)}")
        raise
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        app_logger.info("Shutting down backend...")
        
        if hasattr(app.state, "ollama_client"):
            app.state.ollama_client.close()
        
        if hasattr(app.state, "mcp_server"):
            app.state.mcp_server.close()
        
        app_logger.info("Backend shutdown complete")
    
    return app


# Create the app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to StockAdvisor+ Bot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=config.DEBUG,
        log_level="info"
    )
