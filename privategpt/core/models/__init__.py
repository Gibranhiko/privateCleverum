"""
Data models and schemas used throughout the PrivateGPT system.

Provides type-safe data structures for documents, search results,
and API responses.
"""

from .document import (
    DocumentInfo,
    SearchResult, 
    QueryResponse,
    ChunkInfo,
    SystemStatus
)

__all__ = [
    "DocumentInfo",
    "SearchResult",
    "QueryResponse", 
    "ChunkInfo",
    "SystemStatus"
]