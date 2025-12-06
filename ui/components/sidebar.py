# components/sidebar.py
import streamlit as st

def display_system_status(private_gpt_instance):
    """
    Mostrar el estado del sistema en la barra lateral.
    
    Args:
        private_gpt_instance: Instancia de la clase PrivateGPT
    """
    st.sidebar.title("📊 Estado del sistema")
    
    if not private_gpt_instance:
        st.sidebar.error("❌ System not initialized")
        return False
    
    try:
        status = private_gpt_instance.get_system_status()
        
        # Ollama status
        ollama_status = "🟢 En línea" if status['ollama_available'] else "🔴 Fuera de línea"
        st.sidebar.markdown(f"""
        <div class="status-card">
            <strong>Estado de Ollama:</strong> {ollama_status}
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics in columns
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Documentos", status['total_documents'])
        with col2:
            st.metric("Fragmentos", status['total_chunks'])
        
        # Additional info
        st.sidebar.markdown(f"**Modelo de embeddings:** {status['embedding_model']}")
        
        # Status indicators
        if status['total_documents'] == 0:
            st.sidebar.warning("📝 No hay documentos cargados")
        else:
            efficiency = status['total_chunks'] / status['total_documents']
            st.sidebar.success(f"⚡ Promedio {efficiency:.1f} fragmentos/doc")
        
        # Refresh button
        if st.sidebar.button("🔄 Actualizar estado"):
            st.rerun()
        
        return True
        
    except Exception as e:
        st.sidebar.error(f"Error getting status: {str(e)}")
        return False

def display_model_settings():
    """Mostrar configuración del modelo en la barra lateral."""
    st.sidebar.title("⚙️ Configuración")
    
    # Model selection
    available_models = ["llama3.2", "llama2", "codellama", "mistral", "phi"]
    selected_model = st.sidebar.selectbox(
        "Modelo de IA", 
        available_models, 
        help="Selecciona el modelo de IA para las respuestas"
    )
    
    # Retrieval settings
    max_chunks = st.sidebar.slider(
        "Máx. fuentes", 
        min_value=1, 
        max_value=10, 
        value=3,
        help="Número máximo de fragmentos de documento como contexto"
    )
    
    # Temperature setting
    temperature = st.sidebar.slider(
        "Creatividad de la respuesta",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Valores altos hacen respuestas más creativas pero menos enfocadas"
    )
    
    return {
        'model': selected_model,
        'max_chunks': max_chunks,
        'temperature': temperature
    }

def display_navigation_menu():
    """Mostrar navegación en la barra lateral con enlaces simples."""
    st.sidebar.title("🧭 Navegación")

    nav_order = [
        ("📁 Documentos", "documents"),
        ("💬 Chat", "chat"),
        ("📈 Estadísticas", "statistics"),
        ("⚙️ Configuración", "settings"),
    ]

    if 'current_nav' not in st.session_state:
        st.session_state.current_nav = "documents"

    for label, key in nav_order:
        clicked = st.sidebar.button(label, use_container_width=True, key=f"nav_{key}")
        if clicked:
            st.session_state.current_nav = key
            st.rerun()

    return st.session_state.current_nav

def display_help_section():
    """Mostrar ayuda y enlaces de documentación."""
    st.sidebar.title("❓ Ayuda e información")
    
    with st.sidebar.expander("📖 Guía rápida"):
        st.markdown("""
        1. **Cargar documentos**: Ve a la pestaña Documentos y sube tus archivos
        2. **Espera el procesamiento**: Serán procesados e indexados
        3. **Comienza a chatear**: Ve a la pestaña Chat y pregunta
        4. **Monitorea**: Revisa Estadísticas para información del sistema
        """)
    
    with st.sidebar.expander("🔧 Resolución de problemas"):
        st.markdown("""
        **Problemas comunes:**
        - Si Ollama está offline, inícialo con `ollama serve`
        - Formatos soportados: PDF, TXT, DOCX, MD
        - Archivos grandes tardan en procesar
        - Limpia la caché del navegador si la UI se bloquea
        """)
    
    # Links
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Recursos:**")
    st.sidebar.markdown("• [Documentación](https://github.com/your-repo)")
    st.sidebar.markdown("• [Reportar issues](https://github.com/your-repo/issues)")
    st.sidebar.markdown("• [Configuración de Ollama](https://ollama.ai)")

def display_danger_zone():
    """Mostrar acciones peligrosas con advertencias."""
    with st.sidebar.expander("⚠️ Zona de peligro", expanded=False):
        st.warning("¡Estas acciones no se pueden deshacer!")
        
        if st.button("🗑️ Borrar todos los datos", type="secondary"):
            return "clear_all"
        
        if st.button("🔄 Reiniciar sistema", type="secondary"):
            return "reset_system"
    
    return None