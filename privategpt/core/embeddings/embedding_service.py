# embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingService:
    """Handles text embedding generation."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts).tolist()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.model.encode([text])[0].tolist()
