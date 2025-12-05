"""
Embedding services for converting text to vector representations.

Currently supports sentence-transformers models with plans for
additional embedding providers.
"""

from .embedding_service import EmbeddingService

__all__ = ["EmbeddingService"]