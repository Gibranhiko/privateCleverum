"""
Text document processor implementation.

This module provides plain text file processing capabilities.
"""

from pathlib import Path
from .base import DocumentProcessor


class TextProcessor(DocumentProcessor):
    """Processes plain text documents."""
    
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle text files.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file has .txt extension, False otherwise
        """
        return file_path.suffix.lower() == '.txt'
    
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from a plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            str: File contents as string
            
        Raises:
            ValueError: If file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise ValueError("File appears to be empty")
                
            return content
            
        except UnicodeDecodeError as e:
            raise ValueError(f"Could not decode file {file_path.name} as UTF-8: {e}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading text file {file_path.name}: {e}")