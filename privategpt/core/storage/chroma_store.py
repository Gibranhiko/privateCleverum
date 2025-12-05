"""
ChromaDB implementation of vector storage.

This module provides a ChromaDB-based implementation of the VectorStore interface.
ChromaDB handles automatic text embedding generation and vector similarity search.
"""

import chromadb
from chromadb.errors import InvalidCollectionException
from typing import List, Dict
from pathlib import Path
from .base import VectorStore


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of vector storage."""
    
    def __init__(self, index_dir: Path, collection_name: str = "documents"):
        """
        Initialize ChromaDB vector store.
        
        Args:
            index_dir: Directory where ChromaDB will store its data
            collection_name: Name of the ChromaDB collection
        """
        super().__init__(index_dir, collection_name)
        
        # Ensure index directory exists
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=str(index_dir))
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get existing ChromaDB collection."""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(self.collection_name)
        except (ValueError, InvalidCollectionException):
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",  # Use cosine similarity
                    "description": "Document chunks for semantic search"
                }
            )
    
    def add_documents(self, chunk_ids: List[str], texts: List[str], 
                     metadatas: List[Dict]) -> None:
        """
        Add documents to ChromaDB collection.
        
        Args:
            chunk_ids: Unique identifiers for each text chunk
            texts: List of text content to store
            metadatas: List of metadata dicts for each chunk
            
        Raises:
            ValueError: If input lists have different lengths
        """
        if not (len(chunk_ids) == len(texts) == len(metadatas)):
            raise ValueError("All input lists must have the same length")
        
        if not chunk_ids:  # Empty input
            return
        
        try:
            self.collection.add(
                ids=chunk_ids,
                documents=texts,
                metadatas=metadatas
            )
        except Exception as e:
            raise ValueError(f"Failed to add documents to ChromaDB: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for semantically similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List[Dict]: Search results with text, metadata, and relevance scores
        """
        if not query.strip():
            return []
        
        if self.collection.count() == 0:
            return []
        
        try:
            # Limit k to available documents
            k = min(k, self.collection.count())
            
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            search_results = []
            
            # Check if we got results
            if (results['documents'] and results['documents'][0] and
                results['metadatas'] and results['metadatas'][0] and
                results['distances'] and results['distances'][0]):
                
                for doc, metadata, distance in zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                ):
                    search_results.append({
                        'text': doc,
                        'filename': metadata.get('filename', 'unknown'),
                        'doc_id': metadata.get('doc_id', 'unknown'),
                        'chunk_id': metadata.get('chunk_id', 'unknown'),
                        'relevance_score': round(1 - distance, 3)  # Convert distance to similarity
                    })
            
            return search_results
            
        except Exception as e:
            print(f"ChromaDB search error: {e}")
            return []
    
    def delete_by_doc_id(self, doc_id: str) -> None:
        """
        Delete all chunks for a specific document.
        
        Args:
            doc_id: Document ID to delete
        """
        try:
            # Find all chunks with this doc_id
            results = self.collection.get(where={"doc_id": doc_id})
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} chunks for document {doc_id}")
            else:
                print(f"No chunks found for document {doc_id}")
                
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
    
    def clear_all(self) -> None:
        """Clear all documents from the ChromaDB collection."""
        try:
            # Delete the entire collection and recreate it
            self.client.delete_collection(self.collection_name)
            self._initialize_collection()
            print(f"Cleared all documents from collection '{self.collection_name}'")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def count(self) -> int:
        """
        Get total number of chunks in the collection.
        
        Returns:
            int: Total number of stored chunks
        """
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error getting collection count: {e}")
            return 0
    
    def get_collection_info(self) -> Dict:
        """
        Get detailed information about the ChromaDB collection.
        
        Returns:
            Dict: Collection metadata and statistics
        """
        info = super().get_collection_info()
        
        try:
            # Add ChromaDB-specific info
            info.update({
                "backend": "ChromaDB",
                "similarity_metric": "cosine",
                "client_type": "PersistentClient"
            })
            
            # Get collection metadata if available
            if hasattr(self.collection, 'metadata') and self.collection.metadata:
                info["collection_metadata"] = self.collection.metadata
                
        except Exception as e:
            info["error"] = f"Could not retrieve full collection info: {e}"
        
        return info
    
    def get_document_chunks(self, doc_id: str) -> List[Dict]:
        """
        Get all chunks for a specific document.
        
        Args:
            doc_id: Document ID to retrieve chunks for
            
        Returns:
            List[Dict]: List of chunks with their content and metadata
        """
        try:
            results = self.collection.get(
                where={"doc_id": doc_id},
                include=["documents", "metadatas", "ids"]
            )
            
            chunks = []
            if results['documents']:
                for doc, metadata, chunk_id in zip(
                    results['documents'],
                    results['metadatas'],
                    results['ids']
                ):
                    chunks.append({
                        'chunk_id': chunk_id,
                        'text': doc,
                        'metadata': metadata
                    })
            
            return chunks
            
        except Exception as e:
            print(f"Error retrieving chunks for document {doc_id}: {e}")
            return []