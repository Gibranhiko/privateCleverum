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

# Map Spanish topic labels from UI to internal keys used in metadata
SPANISH_TO_INTERNAL_TOPIC = {
    "citas": "appointments",
    "tratamientos": "treatments",
    "pacientes": "patients",
    "políticas": "policies",
    "politicas": "policies",
    "faq": "faqs",
    "preguntas": "faqs",
    "general": "general",
}

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
            for i, (chunk, embedding) in enumerate(zip(doc_chunks, embeddings)):
                chunk_id = f"{doc_id}_{i}"
                # Extract simple metadata
                patient_name = None
                if "- Paciente:" in chunk:
                    try:
                        patient_name = chunk.split("- Paciente:",1)[1].split("(")[0].strip()
                    except Exception:
                        patient_name = None
                # Infer topic from chunk content
                lower_chunk = chunk.lower()
                inferred_topic = 'general'
                if patient_name:
                    inferred_topic = 'patients'
                if any(k in lower_chunk for k in ["cita", "próxima cita", "proxima cita", "agenda", "programación"]):
                    inferred_topic = 'appointments'
                if any(k in lower_chunk for k in ["tratamiento", "procedimiento", "ortodoncia", "endodoncia", "extracción", "extraccion"]):
                    inferred_topic = 'treatments'
                documents.append({
                    'id': chunk_id,
                    'text': chunk,
                    'embedding': embedding,
                    'metadata': {
                        'filename': display_name,
                        'doc_id': doc_id,
                        'chunk_id': i,
                        'file_path': str(file_path),
                        'patient_name': patient_name,
                        'normalized_name': normalize_text(patient_name) if patient_name else None,
                        'topic': inferred_topic
                    }
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
    
    def search(self, query: str, k: int = 8, filters: Optional[Dict] = None) -> List[Dict]:
        """Search for relevant chunks with optional filters and simple re-ranking."""
        # Try embedding search first
        query_embedding = self.embedding_service.get_embedding(query)
        # Normalize Spanish topic filter to internal key
        if filters and isinstance(filters, dict) and filters.get('topic'):
            t = str(filters.get('topic')).strip().lower()
            filters['topic'] = SPANISH_TO_INTERNAL_TOPIC.get(t, t)

        # Build Chroma-compliant where clause
        where_clause = None
        if filters:
            # Drop null/empty values
            kv = {k: v for k, v in filters.items() if v not in (None, "")}
            if kv:
                if len(kv) == 1:
                    # Single equality
                    where_clause = kv
                else:
                    # Multiple conditions: AND them
                    where_clause = {"$and": [{k: v} for k, v in kv.items()]}
        # Debug: store and log last query info for troubleshooting
        self.last_query_debug = {
            'raw_filters': filters or {},
            'where_clause': where_clause,
            'k': k,
            'query_preview': str(query)[:120]
        }
        logging.info("[PrivateGPT] where_clause=%s filters=%s k=%s", where_clause, filters, k)

        results = self.vector_store.search(query_embedding, k, where=where_clause)
        
        # Simple re-ranking: boost matches on normalized_name if present in query
        qn = normalize_text(query)
        for r in results:
            meta = r.get('metadata', {})
            score = r.get('relevance_score') or 0
            if meta.get('normalized_name') and meta['normalized_name'] in qn:
                r['relevance_score'] = score + 0.1
                r['boost_reason'] = 'name_match'
            # Boost topic if matches filter
            if filters and meta.get('topic') and filters.get('topic') == meta.get('topic'):
                r['relevance_score'] = (r.get('relevance_score') or score) + 0.05
                r['boost_reason'] = (r.get('boost_reason') or '') + '|topic_match'
        results.sort(key=lambda x: x.get('relevance_score') or 0, reverse=True)
        return results
    
    def generate_answer(self, question: str, model: str = "llama3.2", 
                       max_chunks: int = 5, filters: Optional[Dict] = None, **kwargs) -> Dict[str, any]:
        """Generate an AI answer based on relevant document chunks."""
        # Backward-compat for callers passing filters via kwargs
        if filters is None:
            filters = kwargs.get('filters')

        # Get relevant context
        search_results = self.search(question, max_chunks, filters)

        # Strict post-filtering: enforce patient/topic if provided
        if filters and isinstance(filters, dict):
            nn = filters.get('normalized_name')
            tp = filters.get('topic')
            def _strict_match(res):
                meta = res.get('metadata', {})
                ok_nn = True if not nn else (normalize_text(meta.get('normalized_name')) == normalize_text(nn))
                ok_tp = True if not tp else (str(meta.get('topic')).strip().lower() == str(tp).strip().lower())
                return ok_nn and ok_tp
            search_results = [r for r in search_results if _strict_match(r)]

        # Optional simple date filter post-processing
        # If filters include a 'date' string, perform a basic contains match
        # against text and metadata fields to keep chunks likely relevant.
        if filters and isinstance(filters.get('date'), str) and filters.get('date').strip():
            date_str = filters.get('date').strip()
            def _matches_date(res):
                meta = res.get('metadata', {})
                text = res.get('text', '') or res.get('document', '') or ''
                return (date_str in text) or any(
                    (isinstance(v, str) and date_str in v) for v in meta.values()
                )
            search_results = [r for r in search_results if _matches_date(r)]
        
        if not search_results:
            # Fallback: relax filters progressively to help find something
            relaxed_results = []
            if filters:
                relaxed = dict(filters)
                # Try removing topic first
                if relaxed.get('topic'):
                    relaxed.pop('topic')
                    relaxed_results = self.search(question, max_chunks, relaxed)
                    # still enforce normalized_name strictly if present
                    nn_relaxed = relaxed.get('normalized_name')
                    if nn_relaxed:
                        relaxed_results = [r for r in relaxed_results if normalize_text(r.get('metadata', {}).get('normalized_name')) == normalize_text(nn_relaxed)]
                # If still empty, try without any filters
                if not relaxed_results:
                    relaxed_results = self.search(question, max_chunks, None)
                    # enforce normalized_name even when searching without filters
                    nn_only = filters.get('normalized_name')
                    if nn_only:
                        relaxed_results = [r for r in relaxed_results if normalize_text(r.get('metadata', {}).get('normalized_name')) == normalize_text(nn_only)]

            if relaxed_results:
                search_results = relaxed_results
            else:
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
        
        # Basic metrics
        metrics = {
            'top_k': len(search_results),
            'avg_score': round(sum([(r.get('relevance_score') or 0) for r in search_results]) / max(len(search_results),1), 3),
            'filters': filters or {},
            'where_clause': getattr(self, 'last_query_debug', {}).get('where_clause'),
            'query_preview': getattr(self, 'last_query_debug', {}).get('query_preview'),
        }

        # Generate answer using AI service if available
        if self.ai_service.available:
            try:
                answer = self.ai_service.generate_answer(context, question, model)
                return {
                    'answer': answer,
                    'sources': search_results,
                    'has_sources': True,
                    'ollama_used': True,
                    'context': context,
                    'metrics': metrics,
                }
            except Exception as e:
                return {
                    'answer': f"Error generating AI response: {str(e)}",
                    'sources': search_results,
                    'has_sources': True,
                    'ollama_used': False,
                    'context': context,
                    'metrics': metrics,
                }
        else:
            return {
                'answer': "No hay modelo AI disponible. Pasajes relevantes:",
                'sources': search_results,
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