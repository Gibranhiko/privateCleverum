"""
PDF document processor implementation.

This module provides PDF processing capabilities using PyPDF2.
"""

from pathlib import Path
import PyPDF2
from .base import DocumentProcessor


class PDFProcessor(DocumentProcessor):
    """Processes PDF documents using PyPDF2."""
    
    def can_process(self, file_path: Path) -> bool:
        """
        Check if this processor can handle PDF files.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if file has .pdf extension, False otherwise
        """
        return file_path.suffix.lower() == '.pdf'
    
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from a PDF document.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            str: Extracted text with page separators
            
        Raises:
            ValueError: If PDF cannot be read or no text is extracted
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add pages with content
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as page_error:
                        # Log page-specific errors but continue processing
                        print(f"Warning: Could not extract text from page {page_num + 1}: {page_error}")
                        continue
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Error reading PDF {file_path.name}: {e}")