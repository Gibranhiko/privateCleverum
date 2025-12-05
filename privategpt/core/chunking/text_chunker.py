from typing import List


class TextChunker:
    """Handles text chunking with smart boundary detection."""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with smart boundaries."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence or word boundaries
            if end < len(text):
                last_period = chunk.rfind('.')
                last_space = chunk.rfind(' ')
                
                if last_period > self.chunk_size // 2:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1
                elif last_space > self.chunk_size // 2:
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - self.overlap
            
        return chunks
