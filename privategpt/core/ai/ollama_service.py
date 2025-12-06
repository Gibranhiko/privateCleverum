"""
Ollama AI service implementation.

Provides integration with Ollama local AI models.
"""

import requests
from typing import Dict, List, Optional, Any
from .base import AIService
import logging


class OllamaService(AIService):
    """Ollama AI service implementation."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", 
                 default_model: str = "llama3.2", **kwargs):
        """
        Initialize Ollama service.
        
        Args:
            ollama_url: URL of the Ollama server
            default_model: Default model to use for generation
        """
        super().__init__(**kwargs)
        self.ollama_url = ollama_url.rstrip('/')
        self.default_model = default_model
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags", 
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_answer(self, context: str, question: str, 
                       model: Optional[str] = None, 
                       temperature: float = 0.1,
                       max_tokens: int = 500,
                       **kwargs) -> str:
        """
        Generate an answer using Ollama model.
        
        Args:
            context: Document context for the answer
            question: Question to answer
            model: Model to use (defaults to instance default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Ollama-specific options
            
        Returns:
            str: Generated answer
            
        Raises:
            RuntimeError: If service unavailable or API error
        """
        if not self.available:
            raise RuntimeError("Ollama service is not available")
        
        model_name = model or self.default_model
        
        prompt = f"""Basándote en el siguiente contexto de documentos, responde la pregunta de manera precisa y concisa en ESPAÑOL. Si el contexto no contiene suficiente información, indícalo claramente.

Contexto:
{context}

Pregunta: {question}

Respuesta:"""
        # Debug: log prompt preview to terminal for inspection
        try:
            preview = prompt[:500]
            logging.info("[OllamaService] Prompt preview (first 500 chars)=%s", preview)
        except Exception:
            pass
        
        # Merge additional options
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": options
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
            else:
                raise RuntimeError(
                    f"Ollama API error: {response.status_code} - {response.text}"
                )
                
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama: {str(e)}")
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available Ollama models.
        
        Returns:
            Dict containing model information
        """
        if not self.available:
            return {}
        
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry.
        
        Args:
            model_name: Name of the model to pull
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                timeout=300  # Model pulling can take time
            )
            return response.status_code == 200
        except Exception:
            return False