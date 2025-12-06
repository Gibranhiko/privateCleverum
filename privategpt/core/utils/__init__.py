"""
Utility functions and shared components.

Contains common helpers, custom exceptions, and utility functions
used across the PrivateGPT system.
"""

try:
    from .exceptions import (
        PrivateGPTError,
        DocumentProcessingError,
        EmbeddingError,
        VectorStoreError,
        AIServiceError,
        UnsupportedFileTypeError,
    )
except Exception:
    # Fallback lightweight exception types to prevent import-time failures
    class PrivateGPTError(Exception):
        pass
    class DocumentProcessingError(PrivateGPTError):
        pass
    class EmbeddingError(PrivateGPTError):
        pass
    class VectorStoreError(PrivateGPTError):
        pass
    class AIServiceError(PrivateGPTError):
        pass
    class UnsupportedFileTypeError(PrivateGPTError):
        pass

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