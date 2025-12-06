# components/chat_interface.py
import streamlit as st
import time
from datetime import datetime

class ChatInterface:
    """Handles the chat interface and conversation management."""
    
    def __init__(self, private_gpt_instance):
        self.private_gpt = private_gpt_instance
        self.available_models = ["llama3.2", "llama2", "codellama", "mistral", "phi"]
    
    def display_chat_interface(self):
        """Display the main chat interface."""
        st.subheader("💬 Chatea con tus documentos")
        
        if not self.private_gpt:
            st.error("Sistema no inicializado. Por favor, revisa tu configuración.")
            return
        
        # Check if documents exist
        if not self._check_documents_exist():
            st.info("📝 Por favor, sube algunos documentos antes de chatear.")
            return
        
        # Display chat settings
        self._display_chat_settings()
        
        # Display chat history
        self._display_chat_history()
        
        # Chat input
        self._display_chat_input()
        
        # Chat controls
        self._display_chat_controls()
    
    def _check_documents_exist(self):
        """Check if any documents are available for chat."""
        try:
            documents = self.private_gpt.get_documents()
            return len(documents) > 0
        except Exception as e:
            st.error(f"Error checking documents: {str(e)}")
            return False
    
    def _display_chat_settings(self):
        """Display chat settings: only advanced filters for end users."""
        with st.expander("⚙️ Filtros avanzados", expanded=True):
            fcol1, fcol2, fcol3 = st.columns(3)

            with fcol1:
                patient_filter = st.text_input(
                    "Paciente (nombre)",
                    key="filter_patient_name",
                    help="Filtra resultados por nombre del paciente"
                )
            with fcol2:
                # Mostrar en español pero mapear a valores internos
                topic_labels = ["(todos)", "Pacientes", "Citas", "Tratamientos", "Políticas", "FAQs", "General"]
                label_to_value = {
                    "Pacientes": "patients",
                    "Citas": "appointments",
                    "Tratamientos": "treatments",
                    "Políticas": "policies",
                    "FAQs": "faqs",
                    "General": "general",
                }
                topic_label = st.selectbox(
                    "Tema",
                    topic_labels,
                    key="filter_topic",
                    help="Filtra por tema detectado en metadatos"
                )
            with fcol3:
                date_filter = st.text_input(
                    "Fecha contiene (YYYY-MM)",
                    key="filter_date_contains",
                    help="Coincidencia simple en texto de fecha"
                )

            filters = {}
            if patient_filter.strip():
                # Expect normalized_name in metadata
                from privategpt.core.utils.helpers import normalize_text
                filters["normalized_name"] = normalize_text(patient_filter.strip())
            if topic_label and topic_label != "(todos)":
                filters["topic"] = label_to_value.get(topic_label)
            # Note: date filter is simplistic; could be enhanced via where_document
            # Persist filters in session state so submit uses them
            st.session_state['filters'] = filters
            st.session_state['date_contains'] = date_filter.strip()
    
    def _display_chat_history(self):
        """Display the conversation history."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat container with custom styling
        chat_container = st.container()
        
        with chat_container:
            if not st.session_state.chat_history:
                st.info("👋 ¡Comienza una conversación preguntando sobre tus documentos!")
                return
            
            for idx, message in enumerate(st.session_state.chat_history):
                self._display_message(message, idx)
    
    # Suggested questions removed per user request
    
    def _display_message(self, message, message_idx):
        """Display a single chat message."""
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🤖 AI Assistant:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Display sources if available
            if "sources" in message and message["sources"]:
                self._display_sources(message["sources"], message_idx)

            # Metrics panel in an expander similar to sources
            metrics = message.get("metrics")
            if metrics:
                with st.expander("📊 Métricas", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Top K", value=metrics.get("top_k", 0))
                    with col2:
                        st.metric(label="Score promedio", value=metrics.get("avg_score", 0))
                    active_filters = metrics.get("filters", {})
                    if any(v for v in active_filters.values()):
                        st.markdown("**Filtros activos**")
                        st.code(active_filters, language="json")
                    # Debug info
                    if metrics.get("where_clause") is not None:
                        st.markdown("**Where clause**")
                        st.code(metrics.get("where_clause"), language="json")
                    if metrics.get("query_preview"):
                        st.markdown("**Query preview**")
                        st.code(metrics.get("query_preview"))
    
    def _display_sources(self, sources, message_idx):
        """Display source citations for a message."""
        with st.expander(f"📚 Fuentes ({len(sources)} documentos)", expanded=False):
            for i, source in enumerate(sources):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{source.get('filename', 'Desconocido')}**")
                    if 'content' in source:
                        # Show a preview of the content
                        preview = source['content'][:200] + "..." if len(source['content']) > 200 else source['content']
                        st.caption(f"Vista previa: {preview}")
                
                with col2:
                    if 'page' in source:
                        st.caption(f"Página: {source['page']}")
                    if 'score' in source:
                        st.caption(f"Relevancia: {source['score']:.2f}")
        
        # Remove redundant source pills display (now shown only inside expander)
    
    def _display_message_feedback(self, message_idx):
        """Feedback UI removed per user request."""
        return
    
    def _record_feedback(self, message_idx, feedback_type):
        """Record user feedback for improving responses."""
        # Store feedback in session state or database
        if 'message_feedback' not in st.session_state:
            st.session_state.message_feedback = {}
        
        st.session_state.message_feedback[message_idx] = feedback_type
        st.toast(f"¡Gracias por tu retroalimentación! 😊")
    
    def _display_chat_input(self):
        """Display the chat input form."""
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_question = st.text_input(
                    "Pregunta sobre tus documentos:",
                    placeholder="¿Qué te gustaría saber?",
                    label_visibility="collapsed",
                    key="chat_input"
                )
            
            with col2:
                send_button = st.form_submit_button("Enviar 📤", type="primary", use_container_width=True)
        
        # Process input when form is submitted
        if send_button and user_question.strip():
            self._process_user_input(user_question.strip())
    
    def _process_user_input(self, user_question):
        """Process user input and generate AI response."""
        # Get current settings
        settings = {
            'model': st.session_state.get('chat_model_select', self.available_models[0]),
            'max_chunks': st.session_state.get('chat_max_chunks', 3),
            'temperature': st.session_state.get('chat_temperature', 0.7)
        }
        
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate AI response
        with st.spinner("🤔 Pensando..."):
            try:
                # Retrieve filters from session state
                filters = st.session_state.get('filters', {})
                date_contains = st.session_state.get('date_contains')
                if date_contains:
                    filters = dict(filters)
                    filters['date'] = date_contains
                response = self.private_gpt.generate_answer(
                    user_question, 
                    settings['model'], 
                    settings['max_chunks'],
                    filters=filters
                )
                
                # Add AI response to history
                ai_message = {
                    "role": "assistant",
                    "content": response['answer'],
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add sources if available
                if response.get('has_sources') and response.get('sources'):
                    ai_message["sources"] = response['sources']
                
                # Attach basic metrics if provided
                if 'metrics' in response:
                    ai_message['metrics'] = response['metrics']
                st.session_state.chat_history.append(ai_message)
                
            except Exception as e:
                error_message = {
                    "role": "assistant",
                    "content": f"🚨 Lo siento, ocurrió un error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "error": True
                }
                st.session_state.chat_history.append(error_message)
        
        # Refresh to show new messages
        st.rerun()
    
    def _display_chat_controls(self):
        """Display chat control buttons."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🗑️ Limpiar chat", help="Limpiar historial de conversación"):
                self._clear_chat()
        
        with col2:
            if st.button("💾 Exportar chat", help="Exportar conversación como texto"):
                self._export_chat()
        
        with col3:
            if st.button("🔄 Regenerar última", help="Regenerar la última respuesta de IA"):
                self._regenerate_last_response()
        
        with col4:
            # Chat statistics
            total_messages = len(st.session_state.get('chat_history', []))
            st.caption(f"💬 {total_messages} mensajes")
    
    def _clear_chat(self):
        """Clear the chat history after confirmation."""
        if st.session_state.get('confirm_clear_chat', False):
            st.session_state.chat_history = []
            st.session_state.confirm_clear_chat = False
            st.success("✅ ¡Historial del chat limpiado!")
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.confirm_clear_chat = True
            st.warning("⚠️ ¡Haz clic de nuevo para confirmar la limpieza del historial!")
    
    def _export_chat(self):
        """Export chat history as downloadable text."""
        if not st.session_state.get('chat_history'):
            st.warning("¡No hay historial de chat para exportar!")
            return
        
        # Format chat history as text
        chat_text = "# Exportación de chat de PrivateGPT\n\n"
        chat_text += f"Exportado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for message in st.session_state.chat_history:
            role = "Tú" if message["role"] == "user" else "Asistente IA"
            timestamp = message.get("timestamp", "Unknown time")
            chat_text += f"## {role} ({timestamp})\n"
            chat_text += f"{message['content']}\n\n"
            
            if "sources" in message:
                chat_text += "### Fuentes:\n"
                for source in message["sources"]:
                    chat_text += f"- {source.get('filename', 'Desconocido')}\n"
                chat_text += "\n"
        
        # Provide download button
        st.download_button(
            label="📥 Descargar historial de chat",
            data=chat_text,
            file_name=f"privategpt_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    def _regenerate_last_response(self):
        """Regenerate the last AI response."""
        if not st.session_state.get('chat_history'):
            st.warning("¡No hay mensajes para regenerar!")
            return
        
        # Find the last user message
        last_user_message = None
        for message in reversed(st.session_state.chat_history):
            if message["role"] == "user":
                last_user_message = message
                break
        
        if not last_user_message:
            st.warning("No user message found to regenerate response for!")
            return
        
        # Remove the last AI response if it exists
        if (st.session_state.chat_history and 
            st.session_state.chat_history[-1]["role"] == "assistant"):
            st.session_state.chat_history.pop()
        
        # Regenerate response
        self._process_user_input(last_user_message["content"])
    
    def get_chat_statistics(self):
        """Get statistics about the current chat session."""
        if not st.session_state.get('chat_history'):
            return {
                'total_messages': 0,
                'user_messages': 0,
                'ai_messages': 0,
                'sources_used': 0
            }
        
        user_messages = sum(1 for msg in st.session_state.chat_history if msg["role"] == "user")
        ai_messages = sum(1 for msg in st.session_state.chat_history if msg["role"] == "assistant")
        sources_used = sum(len(msg.get("sources", [])) for msg in st.session_state.chat_history)
        
        return {
            'total_messages': len(st.session_state.chat_history),
            'user_messages': user_messages,
            'ai_messages': ai_messages,
            'sources_used': sources_used
        }