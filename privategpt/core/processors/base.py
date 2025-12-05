"""
Abstract base class for document processors.

This module defines the interface that all document processors must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class DocumentProcessor(ABC):
    """Abstract base class for document processors."""
    
    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle the file type.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if this processor can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from the document.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            str: Extracted text content
            
        Raises:
            ValueError: If the file cannot be processed or text cannot be extracted
        """
        pass