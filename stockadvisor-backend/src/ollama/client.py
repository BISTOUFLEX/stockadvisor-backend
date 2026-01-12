"""
Ollama client module for StockAdvisor+ Bot.

Handles communication with the local Ollama LLM service.
"""

import json
from typing import Optional, Dict, Any
import httpx
from src.utils.logger import app_logger
from src.utils.config import config


class OllamaClient:
    """
    Client for interacting with Ollama LLM service.
    
    Provides methods to generate text completions and manage conversations.
    """
    
    def __init__(self, host: str = None, model: str = None):
        """
        Initialize the Ollama client.
        
        Args:
            host: Ollama service host URL (default from config)
            model: Model name to use (default from config)
        """
        self.host = host or config.OLLAMA_HOST
        self.model = model or config.OLLAMA_MODEL
        self.client = httpx.Client(timeout=30.0)
        app_logger.info(f"Ollama client initialized: {self.host} with model {self.model}")
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate text completion using Ollama.
        
        Args:
            prompt: The user prompt
            system: System message to set context
            temperature: Sampling temperature (0-1)
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        
        Raises:
            Exception: If Ollama service is unavailable
        """
        try:
            messages = []
            
            if system:
                messages.append({
                    "role": "system",
                    "content": system
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            url = f"{self.host}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False,
                "options": {
                    "num_predict": max_tokens
                }
            }
            
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
        
        except httpx.ConnectError:
            app_logger.error(f"Failed to connect to Ollama at {self.host}")
            raise Exception("Ollama service is not available")
        except Exception as e:
            app_logger.error(f"Error generating text: {str(e)}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Generate text completion with streaming response.
        
        Args:
            prompt: The user prompt
            system: System message to set context
            temperature: Sampling temperature
        
        Yields:
            Text chunks as they are generated
        """
        try:
            messages = []
            
            if system:
                messages.append({
                    "role": "system",
                    "content": system
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            url = f"{self.host}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }
            
            with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
        
        except Exception as e:
            app_logger.error(f"Error in streaming generation: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            url = f"{self.host}/api/tags"
            response = self.client.get(url, timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            app_logger.warning(f"Ollama health check failed: {str(e)}")
            return False
    
    def close(self):
        """Close the HTTP client connection."""
        self.client.close()
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
