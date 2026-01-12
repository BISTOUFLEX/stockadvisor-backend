"""
Agent orchestrator for StockAdvisor+ Bot.

Manages the AI agent logic and tool execution.
"""

import json
import re
from typing import Dict, Any, Optional
from src.utils.logger import app_logger
from src.ollama.client import OllamaClient
from src.mcp.server import MCPServer
from src.agent.context import ConversationContext


class AgentOrchestrator:
    """
    Orchestrates the AI agent.
    
    Manages conversation flow, tool calling, and response generation.
    """
    
    def __init__(self, ollama_client: OllamaClient, mcp_server: MCPServer):
        """
        Initialize the agent orchestrator.
        
        Args:
            ollama_client: Ollama LLM client
            mcp_server: MCP server with tools
        """
        self.ollama = ollama_client
        self.mcp = mcp_server
        self.contexts: Dict[str, ConversationContext] = {}
    
    def get_or_create_context(self, user_id: str) -> ConversationContext:
        """
        Get or create conversation context for user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Conversation context
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = ConversationContext(user_id)
            app_logger.info(f"Created new context for user {user_id}")
        
        return self.contexts[user_id]
    
    async def process_message(
        self,
        user_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Process user message and generate response.
        
        Args:
            user_id: User identifier
            message: User message
        
        Returns:
            Response with analysis and recommendations
        """
        try:
            context = self.get_or_create_context(user_id)
            
            # Add user message to history
            context.add_message("user", message)
            
            app_logger.info(f"Processing message from user {user_id}: {message[:50]}...")
            
            # Get system prompt with context
            system_prompt = context.get_system_prompt()
            
            # Get conversation history for context
            history = context.get_conversation_history(limit=10)
            
            # Format conversation for Ollama
            messages_text = self._format_messages_for_llm(history)
            
            # Generate response with tool calling
            response = await self._generate_response_with_tools(
                system_prompt,
                messages_text,
                message
            )
            
            # Add assistant response to history
            context.add_message("assistant", response["text"], response.get("metadata"))
            
            return {
                "success": True,
                "user_id": user_id,
                "response": response["text"],
                "analysis": response.get("analysis"),
                "tools_used": response.get("tools_used", [])
            }
        
        except Exception as e:
            app_logger.error(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_response_with_tools(
        self,
        system_prompt: str,
        messages_text: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Generate response with tool calling capability.
        
        Args:
            system_prompt: System prompt for the agent
            messages_text: Formatted conversation history
            user_message: Current user message
        
        Returns:
            Response with analysis
        """
        # First, let the LLM decide what tools to use
        tool_decision_prompt = f"""{system_prompt}

Conversation History:
{messages_text}

User: {user_message}

Based on the user's message, decide which tools to use (if any):
1. analyze_stock(symbol) - for analyzing a specific stock
2. compare_stocks(symbols) - for comparing multiple stocks
3. get_market_news(limit) - for getting market news

Respond with a JSON object containing:
{{"tools": ["tool_name(param)"], "reasoning": "why you chose these tools"}}

If no tools are needed, respond with: {{"tools": [], "reasoning": "reason"}}
"""
        
        try:
            # Get tool decision from LLM
            tool_response = await self.ollama.generate(
                tool_decision_prompt,
                temperature=0.3
            )
            
            # Parse tool decision
            tools_to_use = self._parse_tool_decision(tool_response)
            
            # Execute tools
            analysis_results = {}
            if tools_to_use:
                analysis_results = await self._execute_tools(tools_to_use)
            
            # Generate final response
            final_prompt = f"""{system_prompt}

Conversation History:
{messages_text}

User: {user_message}

{f'Analysis Results: {json.dumps(analysis_results, indent=2)}' if analysis_results else ''}

Generate a helpful response to the user based on the above information. Be conversational and provide actionable insights.
"""
            
            final_response = await self.ollama.generate(
                final_prompt,
                temperature=0.7
            )
            
            return {
                "text": final_response,
                "analysis": analysis_results,
                "tools_used": tools_to_use,
                "metadata": {
                    "tool_count": len(tools_to_use),
                    "has_analysis": bool(analysis_results)
                }
            }
        
        except Exception as e:
            app_logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _parse_tool_decision(self, response: str) -> list:
        """
        Parse tool decision from LLM response.
        
        Args:
            response: LLM response
        
        Returns:
            List of tools to execute
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\\{.*\\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("tools", [])
        except Exception as e:
            app_logger.warning(f"Error parsing tool decision: {str(e)}")
        
        return []
    
    async def _execute_tools(self, tools: list) -> Dict[str, Any]:
        """
        Execute requested tools.
        
        Args:
            tools: List of tools to execute
        
        Returns:
            Results from tool execution
        """
        results = {}
        
        for tool in tools:
            try:
                if "analyze_stock" in tool:
                    # Extract symbol from tool call
                    symbol_match = re.search(r'analyze_stock\\((.*?)\\)', tool)
                    if symbol_match:
                        symbol = symbol_match.group(1).strip().strip('"').strip("'").strip('\\')
                        result = await self.mcp.analyze_stock(symbol)
                        results[f"analyze_stock_{symbol}"] = result
                
                elif "compare_stocks" in tool:
                    # Extract symbols from tool call
                    symbols_match = re.search(r'compare_stocks\\(\\[(.*?)\\]\\)', tool)
                    if symbols_match:
                        symbols_str = symbols_match.group(1)
                        symbols = [s.strip().strip('"').strip("'").strip('\\') for s in symbols_str.split(",")]
                        result = await self.mcp.compare_stocks(symbols)
                        results["compare_stocks"] = result
                
                elif "get_market_news" in tool:
                    result = await self.mcp.get_market_news()
                    results["market_news"] = result
            
            except Exception as e:
                app_logger.error(f"Error executing tool {tool}: {str(e)}")
                results[tool] = {"error": str(e)}
        
        return results
    
    def _format_messages_for_llm(self, messages: list) -> str:
        """
        Format conversation messages for LLM.
        
        Args:
            messages: List of messages
        
        Returns:
            Formatted message string
        """
        formatted = []
        
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted.append(f"{role}: {content}")
        
        return "\\n".join(formatted)
    
    def clear_context(self, user_id: str):
        """
        Clear conversation context for user.
        
        Args:
            user_id: User identifier
        """
        if user_id in self.contexts:
            del self.contexts[user_id]
            app_logger.info(f"Cleared context for user {user_id}")
