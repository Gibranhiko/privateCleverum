"""
Document processor factory for creating appropriate processors.

This module provides a factory class that automatically selects
the correct processor for a given file type.
"""

from pathlib import Path
from typing import List
from .base import DocumentProcessor
from .pdf_processor import PDFProcessor
from .text_processor import TextProcessor


class DocumentProcessorFactory:
    """Factory for creating appropriate document processors."""
    
    def __init__(self, custom_processors: List[DocumentProcessor] = None):
        """
        Initialize the factory with available processors.
        
        Args:
            custom_processors: Optional list of additional processors to register
        """
        # Default processors
        self.processors = [
            PDFProcessor(),
            TextProcessor(),
        ]
        
        # Add any custom processors
        if custom_processors:
            self.processors.extend(custom_processors)
    
    def get_processor(self, file_path: Path) -> DocumentProcessor:
        """
        Get the appropriate processor for a file.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            DocumentProcessor: The processor that can handle this file type
            
        Raises:
            ValueError: If no processor can handle the file type
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor
        
        # No processor found
        supported_types = []
        for processor in self.processors:
            # Try to get supported extensions (this is a simple heuristic)
            if hasattr(processor, 'can_process'):
                # This is a basic way to show what types are supported
                # In a real implementation, you might want processors to expose their supported types
                pass
        
        raise ValueError(
            f"No processor available for file type: {file_path.suffix}. "
            f"Supported types: .pdf, .txt"
        )
    
    def add_processor(self, processor: DocumentProcessor) -> None:
        """
        Add a new processor to the factory.
        
        Args:
            processor: The processor to add
        """
        if not isinstance(processor, DocumentProcessor):
            raise TypeError("Processor must inherit from DocumentProcessor")
        
        self.processors.append(processor)
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List[str]: List of supported extensions (e.g., ['.pdf', '.txt'])
        """
        # This is a simple implementation - in practice you might want
        # processors to expose their supported extensions more explicitly
        extensions = []
        test_files = ['.pdf', '.txt', '.doc', '.docx', '.html', '.md']
        
        for ext in test_files:
            test_path = Path(f"test{ext}")
            for processor in self.processors:
                if processor.can_process(test_path):
                    if ext not in extensions:
                        extensions.append(ext)
                    break
        
        return extensions