"""
Abstract base class for vector storage backends.

This module defines the interface that all vector store implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path


class VectorStore(ABC):
    """Abstract base class for vector storage backends."""
    
    def __init__(self, index_dir: Path, collection_name: str = "documents"):
        """
        Initialize the vector store.
        
        Args:
            index_dir: Directory where the vector index will be stored
            collection_name: Name of the collection/index
        """
        self.index_dir = index_dir
        self.collection_name = collection_name
    
    @abstractmethod
    def add_documents(self, chunk_ids: List[str], texts: List[str], 
                     metadatas: List[Dict]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            chunk_ids: Unique identifiers for each text chunk
            texts: List of text content to store
            metadatas: List of metadata dicts for each chunk
        """
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List[Dict]: Search results with text, metadata, and relevance scores
        """
        pass
    
    @abstractmethod
    def delete_by_doc_id(self, doc_id: str) -> None:
        """
        Delete all chunks for a specific document.
        
        Args:
            doc_id: Document ID to delete
        """
        pass
    
    @abstractmethod
    def clear_all(self) -> None:
        """Clear all documents from the store."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Get total number of chunks in the store.
        
        Returns:
            int: Total number of stored chunks
        """
        pass
    
    def get_collection_info(self) -> Dict:
        """
        Get information about the current collection.
        
        Returns:
            Dict: Collection metadata and statistics
        """
        return {
            "collection_name": self.collection_name,
            "index_dir": str(self.index_dir),
            "total_chunks": self.count()
        }