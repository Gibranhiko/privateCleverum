"""
AI service providers for generating responses to user queries.

Supports multiple AI backends with Ollama as the primary implementation.
Easily extensible for OpenAI, Anthropic, or other providers.
"""

from .base import AIService
from .ollama_service import OllamaService

__all__ = [
    "AIService",      # Abstract interface
    "OllamaService"   # Default implementation
]