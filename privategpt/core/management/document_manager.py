# document_manager.py
import pickle
import uuid
from pathlib import Path
from typing import List, Dict, Optional


class DocumentManager:
    """Manages document metadata and persistence."""
    
    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.documents = []
        self._load_metadata()
    
    def add_document(self, filename: str, file_path: str, 
                    num_chunks: int, file_size: int) -> str:
        """Add document metadata and return document ID."""
        doc_id = str(uuid.uuid4())
        doc_info = {
            'doc_id': doc_id,
            'filename': filename,
            'path': file_path,
            'num_chunks': num_chunks,
            'file_size': file_size
        }
        self.documents.append(doc_info)
        self._save_metadata()
        return doc_id
    
    def remove_document(self, doc_id: str) -> Optional[Dict]:
        """Remove document metadata."""
        doc_to_remove = None
        for doc in self.documents:
            if doc['doc_id'] == doc_id:
                doc_to_remove = doc
                break
        
        if doc_to_remove:
            self.documents = [doc for doc in self.documents if doc['doc_id'] != doc_id]
            self._save_metadata()
        
        return doc_to_remove
    
    def get_all_documents(self) -> List[Dict]:
        """Get all document metadata."""
        return self.documents.copy()
    
    def clear_all(self) -> None:
        """Clear all document metadata."""
        self.documents = []
        docs_file = self.index_dir / "documents.pkl"
        if docs_file.exists():
            docs_file.unlink()
    
    def _save_metadata(self) -> None:
        """Save metadata to disk."""
        try:
            with open(self.index_dir / "documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
        except Exception as e:
            print(f"Error saving documents metadata: {e}")
    
    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        docs_file = self.index_dir / "documents.pkl"
        if docs_file.exists():
            try:
                with open(docs_file, 'rb') as f:
                    self.documents = pickle.load(f)
            except Exception as e:
                print(f"Error loading documents metadata: {e}")
                self.documents = []
