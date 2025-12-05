"""
Utility functions and shared components.

Contains common helpers, custom exceptions, and utility functions
used across the PrivateGPT system.
"""

from .exceptions import (
    PrivateGPTError,
    DocumentProcessingError,
    EmbeddingError,
    VectorStoreError,
    AIServiceError,
    UnsupportedFileTypeError
)

from .helpers import (
    validate_file_path,
    get_file_size_mb,
    sanitize_filename,
    ensure_directory_exists
)

__all__ = [
    # Exceptions
    "PrivateGPTError",
    "DocumentProcessingError",
    "EmbeddingError", 
    "VectorStoreError",
    "AIServiceError",
    "UnsupportedFileTypeError",
    
    # Helper functions
    "validate_file_path",
    "get_file_size_mb",
    "sanitize_filename",
    "ensure_directory_exists"
]