class PrivateGPTError(Exception):
	"""Base exception for PrivateGPT-related errors."""
	pass


class DocumentProcessingError(PrivateGPTError):
	"""Raised when a document fails during processing or ingestion."""
	pass


class EmbeddingError(PrivateGPTError):
	"""Raised when there is an issue generating embeddings."""
	pass


class VectorStoreError(PrivateGPTError):
	"""Raised for storage/retrieval issues in the vector store."""
	pass


class AIServiceError(PrivateGPTError):
	"""Raised when the AI service cannot generate a response."""
	pass


class UnsupportedFileTypeError(PrivateGPTError):
	"""Raised when attempting to process an unsupported file type."""
	pass
