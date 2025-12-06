"""
ChromaDB implementation of vector storage.

This module provides a ChromaDB-based implementation of the VectorStore interface.
ChromaDB handles automatic text embedding generation and vector similarity search.
"""

import chromadb
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
        except Exception:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "hnsw:space": "cosine",  # Use cosine similarity
                    "description": "Document chunks for semantic search"
                }
            )
    
    def add_documents(self, chunk_ids: List[str] = None, texts: List[str] = None,
                      metadatas: List[Dict] = None, documents: List[Dict] = None) -> None:
        """
        Add documents to ChromaDB collection.

        Supports two calling styles for backward compatibility:
        - add_documents(chunk_ids, texts, metadatas)
        - add_documents(documents=[{ 'id', 'text', 'embedding'(opt), 'metadata' }, ...])

        If embeddings are provided in the document dicts they will be passed to Chroma.
        """
        # Normalize inputs to lists of ids, texts, metadatas, and optional embeddings
        ids = []
        docs = []
        metas = []
        embeddings = None

        # If caller passed a list of document dicts
        if documents is None and isinstance(chunk_ids, list) and chunk_ids and isinstance(chunk_ids[0], dict):
            documents = chunk_ids

        if documents:
            for d in documents:
                ids.append(d.get('id'))
                docs.append(d.get('text') or d.get('document') or '')
                metas.append(d.get('metadata') or d.get('metadatas') or {})
                if 'embedding' in d:
                    if embeddings is None:
                        embeddings = []
                    embeddings.append(d.get('embedding'))
        else:
            # Fallback to old signature
            if not (chunk_ids and texts and metadatas):
                # Nothing to add
                return
            if not (len(chunk_ids) == len(texts) == len(metadatas)):
                raise ValueError('All input lists must have the same length')
            ids = chunk_ids
            docs = texts
            metas = metadatas

        if not ids:
            return

        try:
            add_kwargs = {
                'ids': ids,
                'documents': docs,
                'metadatas': metas
            }
            if embeddings is not None:
                add_kwargs['embeddings'] = embeddings

            self.collection.add(**add_kwargs)
        except Exception as e:
            raise ValueError(f"Failed to add documents to ChromaDB: {e}")
    
    def search(self, query, k: int = 5, where: Dict = None, where_document: Dict = None) -> List[Dict]:
        """
        Search for semantically similar documents.

        `query` may be either a text string or an embedding vector (list of floats).
        """
        # Empty query handling
        if query is None:
            return []

        # If collection empty
        try:
            total = self.collection.count()
        except Exception:
            total = 0

        if total == 0:
            return []

        try:
            # Limit k to available documents
            k = min(k, total)

            # Detect whether query is embedding vector or text
            if isinstance(query, (list, tuple)):
                # Avoid passing empty filter dicts which some Chroma versions reject
                effective_where = where if where else None
                effective_where_doc = where_document if where_document else None
                results = self.collection.query(
                    query_embeddings=[list(query)],
                    n_results=k,
                    where=effective_where,
                    where_document=effective_where_doc
                )
            else:
                if not str(query).strip():
                    return []
                effective_where = where if where else None
                effective_where_doc = where_document if where_document else None
                results = self.collection.query(
                    query_texts=[str(query)],
                    n_results=k,
                    where=effective_where,
                    where_document=effective_where_doc
                )

            search_results = []

            # Normalize result structure
            docs_list = results.get('documents', [])
            metas_list = results.get('metadatas', [])
            dists_list = results.get('distances', [])

            if docs_list and metas_list:
                docs = docs_list[0] if isinstance(docs_list[0], list) else docs_list
                metas = metas_list[0] if isinstance(metas_list[0], list) else metas_list
                dists = dists_list[0] if dists_list and isinstance(dists_list[0], list) else (dists_list or [None]*len(docs))

                for doc, metadata, distance in zip(docs, metas, dists):
                    search_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'filename': metadata.get('filename', 'unknown'),
                        'doc_id': metadata.get('doc_id', 'unknown'),
                        'chunk_id': metadata.get('chunk_id', 'unknown'),
                        'relevance_score': round(1 - distance, 3) if distance is not None else None
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