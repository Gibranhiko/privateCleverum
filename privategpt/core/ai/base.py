"""
Abstract base class for AI service providers.

Defines the interface that all AI service implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIService(ABC):
    """Abstract base class for AI service providers."""
    
    def __init__(self, **kwargs):
        """Initialize the AI service with provider-specific configuration."""
        self.available = False
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """
        Check if the AI service is available and responsive.
        
        Returns:
            bool: True if service is available, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_answer(self, context: str, question: str, 
                       model: Optional[str] = None, 
                       **kwargs) -> str:
        """
        Generate an answer using the AI model.
        
        Args:
            context: The document context to base the answer on
            question: The question to answer
            model: Optional model name/identifier
            **kwargs: Additional provider-specific parameters
            
        Returns:
            str: The generated answer
            
        Raises:
            RuntimeError: If the service is unavailable or API call fails
        """
        pass
    
    @property
    def is_available(self) -> bool:
        """Check if the service is currently available."""
        return self.available
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models from the service.
        
        Returns:
            Dict containing model information
        """
        return {}