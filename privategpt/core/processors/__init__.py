"""
Document processors for handling different file types.

This module provides extensible document processing capabilities through
an abstract base class and concrete implementations for various formats.
"""

from .base import DocumentProcessor
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor
from .factory import DocumentProcessorFactory

# For easy extension - users can import these to create custom processors
__all__ = [
    "DocumentProcessor",      # Abstract base - for custom processors
    "PDFProcessor",
    "TextProcessor", 
    "DocumentProcessorFactory"  # Main entry point
]