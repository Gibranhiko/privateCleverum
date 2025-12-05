"""
Vector storage backends for document embeddings and metadata.

Provides abstraction layer for different vector databases with
ChromaDB as the default implementation.
"""

from .base import VectorStore
from .chroma_store import ChromaVectorStore

__all__ = [
    "VectorStore",        # Abstract interface
    "ChromaVectorStore"   # Default implementation
]