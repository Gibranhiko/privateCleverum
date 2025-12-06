from pathlib import Path
from typing import Dict, List, Optional
from privategpt.core.ai.ollama_service import OllamaService
from privategpt.core.management.document_manager import DocumentManager
from privategpt.core.processors.factory import DocumentProcessorFactory
from privategpt.core.embeddings.embedding_service import EmbeddingService
from privategpt.core.chunking.text_chunker import TextChunker
from privategpt.core.storage.chroma_store import ChromaVectorStore
from privategpt.core.utils.helpers import normalize_text
import logging

class PrivateGPT:
    """
    Main orchestrator for the private document AI system.
    Coordinates between different components.
    """
    
    def __init__(self, data_dir: str = "data", index_dir: str = "index", 
                 ollama_url: str = "http://localhost:11434"):
        """Initialize the PrivateGPT system."""
        self.data_dir = Path(data_dir)
        self.index_dir = Path(index_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.index_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.document_processor_factory = DocumentProcessorFactory()
        self.text_chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = ChromaVectorStore(self.index_dir)
        self.ai_service = OllamaService(ollama_url)
        self.document_manager = DocumentManager(self.index_dir)
    
    def get_system_status(self) -> Dict[str, any]:
        """Get current system status."""
        return {
            'ollama_available': self.ai_service.available,
            'total_documents': len(self.document_manager.get_all_documents()),
            'total_chunks': self.vector_store.count(),
            'embedding_model': self.embedding_service.model_name
        }
    
    def add_document(self, file_path: str, filename: Optional[str] = None) -> Dict[str, any]:
        """Add a document to the knowledge base."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {
                    'success': False,
                    'message': f"File {file_path} not found!",
                    'doc_info': None
                }
            
            # Process document
            processor = self.document_processor_factory.get_processor(file_path)
            text = processor.extract_text(file_path)
            
            if not text.strip():
                return {
                    'success': False,
                    'message': "No text could be extracted from the file. It may be a scanned image or an unsupported format.",
                    'doc_info': None
                }
            
            # Chunk text
            doc_chunks = self.text_chunker.chunk_text(text)
            
            # Add to document manager
            display_name = filename or file_path.name
            doc_id = self.document_manager.add_document(
                display_name, str(file_path), len(doc_chunks), 
                file_path.stat().st_size
            )
            
            # Generate embeddings for chunks
            embeddings = []
            for chunk in doc_chunks:
                embedding = self.embedding_service.get_embedding(chunk)
                embeddings.append(embedding)
            
            # Prepare data for vector store
            documents = []
            current_patient_name = None
            for i, (chunk, embedding) in enumerate(zip(doc_chunks, embeddings)):
                chunk_id = f"{doc_id}_{i}"
                # Extract simple metadata
                patient_name = None
                if "- Paciente:" in chunk:
                    try:
                        patient_name = chunk.split("- Paciente:",1)[1].split("(")[0].strip()
                        current_patient_name = patient_name if patient_name else current_patient_name
                    except Exception:
                        patient_name = None
                # Propagate patient context: if this chunk lacks explicit patient, use last seen
                if not patient_name and current_patient_name:
                    patient_name = current_patient_name
                # Infer topic from chunk content
                lower_chunk = chunk.lower()
                inferred_topic = 'general'
                if patient_name:
                    inferred_topic = 'patients'
                if any(k in lower_chunk for k in [
                    "cita", "próxima cita", "proxima cita", "agenda", "programación", "programacion",
                    "confirmación", "confirmacion", "reprogramación", "reprogramacion", "turno", "recordatorio"
                ]):
                    inferred_topic = 'appointments'
                if any(k in lower_chunk for k in ["tratamiento", "procedimiento", "ortodoncia", "endodoncia", "extracción", "extraccion"]):
                    inferred_topic = 'treatments'
                # Build metadata and remove None values to satisfy ChromaDB
                metadata = {
                    'filename': display_name,
                    'doc_id': doc_id,
                    'chunk_id': i,
                    'file_path': str(file_path),
                    'patient_name': patient_name,
                    'normalized_name': normalize_text(patient_name) if patient_name else None,
                    'topic': inferred_topic
                }
                metadata = {k: v for k, v in metadata.items() if v is not None}

                documents.append({
                    'id': chunk_id,
                    'text': chunk,
                    'embedding': embedding,
                    'metadata': metadata
                })
            
            # Add to vector store
            self.vector_store.add_documents(documents)  # Fixed: Pass proper document format
            
            return {
                'success': True,
                'message': f"Successfully processed {display_name} ({len(doc_chunks)} chunks)",
                'doc_info': {
                    'doc_id': doc_id,
                    'filename': display_name,
                    'num_chunks': len(doc_chunks)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing document: {str(e)}",
                'doc_info': None
            }
    
    def search(self, query: str, k: int = 8) -> List[Dict]:
        """Search for relevant chunks using embeddings only (MVP)."""
        query_embedding = self.embedding_service.get_embedding(query)
        results = self.vector_store.search(query_embedding, k, where=None)
        # Minimal MVP: rely on vector store scoring; sort by relevance_score if present
        results.sort(key=lambda x: x.get('relevance_score') or 0, reverse=True)
        return results
    
    def generate_answer(self, question: str, model: str = "llama3.2", 
                       max_chunks: int = 5) -> Dict[str, any]:
        """Generate an AI answer based on relevant document chunks (MVP)."""
        search_results = self.search(question, max_chunks)
        if not search_results:
            return {
                'answer': "No encontré información relevante en tus documentos para responder esta pregunta.",
                'sources': [],
                'has_sources': False,
                'ollama_used': False
            }
        
        # Generate context string
        context_parts = []
        for result in search_results:
            # Fixed: Access metadata properly
            filename = result.get('metadata', {}).get('filename', 'Unknown')
            text = result.get('text', result.get('document', ''))
            context_parts.append(f"[Source: {filename}]\n{text}")
        context = "\n\n---\n\n".join(context_parts)
        # Debug: log composed context and filters for LLM
        logging.info("[PrivateGPT] Question=%s", question)
        logging.info("[PrivateGPT] Context preview (first 500 chars)=%s", context[:500])
        
        # Basic metrics (minimal)
        metrics = {
            'top_k': len(search_results),
            'avg_score': round(sum([(r.get('relevance_score') or 0) for r in search_results]) / max(len(search_results),1), 3),
        }

        # Build unique sources by filename to avoid duplicates in UI
        unique_sources: Dict[str, Dict[str, any]] = {}
        for r in search_results:
            meta = r.get('metadata', {})
            fname = meta.get('filename', 'Unknown')
            score = r.get('relevance_score') or 0
            # Keep the best scoring chunk per filename
            existing = unique_sources.get(fname)
            if not existing or score > (existing.get('score') or 0):
                unique_sources[fname] = {
                    'filename': fname,
                    'page': meta.get('page'),
                    'score': score,
                    'content': r.get('text', r.get('document', '')),
                }
        deduped_sources = list(unique_sources.values())

        # Generate answer using AI service if available
        if self.ai_service.available:
            try:
                answer = self.ai_service.generate_answer(context, question, model)
                return {
                    'answer': answer,
                    'sources': deduped_sources,
                    'has_sources': True,
                    'ollama_used': True,
                    'context': context,
                    'metrics': metrics,
                }
            except Exception as e:
                return {
                    'answer': f"Error generating AI response: {str(e)}",
                    'sources': deduped_sources,
                    'has_sources': True,
                    'ollama_used': False,
                    'context': context,
                    'metrics': metrics,
                }
        else:
            return {
                'answer': "No hay modelo AI disponible. Pasajes relevantes:",
                'sources': deduped_sources,
                'has_sources': True,
                'ollama_used': False,
                'context': context,
                'metrics': metrics,
            }
    
    def get_documents(self) -> List[Dict]:
        """Get list of all documents."""
        return self.document_manager.get_all_documents()
    
    def remove_document(self, doc_id: str) -> Dict[str, any]:
        """Remove a document from the knowledge base."""
        try:
            doc_info = self.document_manager.remove_document(doc_id)
            if not doc_info:
                return {
                    'success': False,
                    'message': 'Document not found'
                }
            
            self.vector_store.delete_by_doc_id(doc_id)
            
            return {
                'success': True,
                'message': f"Successfully removed {doc_info['filename']}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error removing document: {str(e)}"
            }
    
    def clear_all_documents(self) -> Dict[str, any]:
        """Clear the entire knowledge base."""
        try:
            self.vector_store.clear_all()
            self.document_manager.clear_all()
            
            return {
                'success': True,
                'message': 'Knowledge base cleared successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Error clearing knowledge base: {str(e)}"
            }
    
    def get_document_stats(self) -> Dict[str, any]:
        """Get detailed statistics about the knowledge base."""
        documents = self.document_manager.get_all_documents()
        total_chunks = self.vector_store.count()
        total_docs = len(documents)
        
        if documents:
            avg_chunks = total_chunks / total_docs
            total_size = sum(doc.get('file_size', 0) for doc in documents)
        else:
            avg_chunks = 0
            total_size = 0
        
        return {
            'total_documents': total_docs,
            'total_chunks': total_chunks,
            'average_chunks_per_doc': round(avg_chunks, 1),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'ollama_available': self.ai_service.available
        }