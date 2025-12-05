"""Extended document models for the examples above."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class DocumentInfo:
    """Document metadata."""
    doc_id: str
    filename: str
    path: str
    num_chunks: int
    file_size: int


@dataclass
class SearchResult:
    """Search result from vector store."""
    text: str
    filename: str
    doc_id: str
    chunk_id: int
    relevance_score: float


@dataclass
class QueryResponse:
    """Response from AI query."""
    answer: str
    sources: List[SearchResult]
    has_sources: bool
    ollama_used: bool
    context: Optional[str] = None


@dataclass
class ChunkInfo:
    """Information about a text chunk."""
    chunk_id: str
    text: str
    doc_id: str
    chunk_index: int
    metadata: Dict[str, any]


@dataclass  
class SystemStatus:
    """Current system status information."""
    ollama_available: bool
    total_documents: int
    total_chunks: int
    embedding_model: str
    version: str