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
    """Mostrar navegación con botones y resaltar el activo."""
    nav_order = [
        ("📁 Documentos", "documents"),
        ("💬 Chat", "chat"),
        ("📈 Estadísticas", "statistics"),
    ]

    # Default selection: Chat
    if 'current_nav' not in st.session_state:
        st.session_state.current_nav = "chat"

    for label, key in nav_order:
        if st.session_state.current_nav == key:
            # Active item: show highlighted label instead of a clickable button
            st.sidebar.markdown(f"**{label}** ✅")
        else:
            # Ensure left alignment: avoid full-width buttons
            clicked = st.sidebar.button(label, key=f"nav_{key}")
            if clicked:
                st.session_state.current_nav = key
                st.rerun()

    return st.session_state.current_nav

def display_help_section():
    """Sección de ayuda/recursos deshabilitada para MVP."""
    return

def display_danger_zone():
    """Mostrar acciones peligrosas dentro de un ítem expandible, estilo enlaces."""
    with st.sidebar.expander("⚠️ Zona de peligro", expanded=False):
        # Texto de advertencia breve
        st.caption("Estas acciones no se pueden deshacer.")
        # Sub-opciones estilo enlace (botones con CSS de enlace)
        if st.button("🗑️ Borrar todos los datos", key="dz_clear_all"):
            return "clear_all"
    return None