from typing import List


class TextChunker:
    """Handles text chunking with clinical-aware boundary detection."""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 160):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with clinical markers (Paciente:) as boundaries when present."""
        lines = text.splitlines()
        blocks: List[str] = []
        current: List[str] = []
        for line in lines:
            if line.strip().startswith("- Paciente:") and current:
                blocks.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            blocks.append("\n".join(current))

        if not blocks:
            blocks = [text]

        chunks: List[str] = []
        for b in blocks:
            tokens = b.split()
            start = 0
            while start < len(tokens):
                end = min(start + self.chunk_size, len(tokens))
                chunk = " ".join(tokens[start:end])
                if chunk.strip():
                    chunks.append(chunk.strip())
                if end == len(tokens):
                    break
                start = max(end - self.overlap, start + 1)
        return chunks
