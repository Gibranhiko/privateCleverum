# components/sidebar.py
import streamlit as st

def display_system_status(private_gpt_instance):
    """
    Display system status information in the sidebar.
    
    Args:
        private_gpt_instance: Instance of PrivateGPT class
    """
    st.sidebar.title("📊 System Status")
    
    if not private_gpt_instance:
        st.sidebar.error("❌ System not initialized")
        return False
    
    try:
        status = private_gpt_instance.get_system_status()
        
        # Ollama status
        ollama_status = "🟢 Online" if status['ollama_available'] else "🔴 Offline"
        st.sidebar.markdown(f"""
        <div class="status-card">
            <strong>Ollama Status:</strong> {ollama_status}
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics in columns
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Documents", status['total_documents'])
        with col2:
            st.metric("Chunks", status['total_chunks'])
        
        # Additional info
        st.sidebar.markdown(f"**Embedding Model:** {status['embedding_model']}")
        
        # Status indicators
        if status['total_documents'] == 0:
            st.sidebar.warning("📝 No documents uploaded")
        else:
            efficiency = status['total_chunks'] / status['total_documents']
            st.sidebar.success(f"⚡ Avg {efficiency:.1f} chunks/doc")
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Status"):
            st.rerun()
        
        return True
        
    except Exception as e:
        st.sidebar.error(f"Error getting status: {str(e)}")
        return False

def display_model_settings():
    """Display model and configuration settings in sidebar."""
    st.sidebar.title("⚙️ Settings")
    
    # Model selection
    available_models = ["llama3.2", "llama2", "codellama", "mistral", "phi"]
    selected_model = st.sidebar.selectbox(
        "AI Model", 
        available_models, 
        help="Select the AI model for responses"
    )
    
    # Retrieval settings
    max_chunks = st.sidebar.slider(
        "Max Sources", 
        min_value=1, 
        max_value=10, 
        value=3,
        help="Maximum number of document chunks to use as context"
    )
    
    # Temperature setting
    temperature = st.sidebar.slider(
        "Response Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make responses more creative but less focused"
    )
    
    return {
        'model': selected_model,
        'max_chunks': max_chunks,
        'temperature': temperature
    }

def display_navigation_menu():
    """Display navigation menu in sidebar."""
    st.sidebar.title("🧭 Navigation")
    
    # Navigation options
    nav_options = {
        "📁 Documents": "documents",
        "💬 Chat": "chat", 
        "📈 Statistics": "statistics",
        "⚙️ Settings": "settings"
    }
    
    selected_nav = st.sidebar.radio(
        "Go to:",
        list(nav_options.keys()),
        label_visibility="collapsed"
    )
    
    return nav_options[selected_nav]

def display_help_section():
    """Display help and documentation links."""
    st.sidebar.title("❓ Help & Info")
    
    with st.sidebar.expander("📖 Quick Start Guide"):
        st.markdown("""
        1. **Upload Documents**: Go to Documents tab and upload your files
        2. **Wait for Processing**: Documents will be processed and indexed
        3. **Start Chatting**: Go to Chat tab and ask questions
        4. **Monitor Stats**: Check Statistics tab for system info
        """)
    
    with st.sidebar.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        - If Ollama is offline, start it with `ollama serve`
        - Supported formats: PDF, TXT, DOCX, MD
        - Large files may take time to process
        - Clear browser cache if UI seems stuck
        """)
    
    # Links
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Resources:**")
    st.sidebar.markdown("• [Documentation](https://github.com/your-repo)")
    st.sidebar.markdown("• [Report Issues](https://github.com/your-repo/issues)")
    st.sidebar.markdown("• [Ollama Setup](https://ollama.ai)")

def display_danger_zone():
    """Display dangerous actions with warnings."""
    with st.sidebar.expander("⚠️ Danger Zone", expanded=False):
        st.warning("These actions cannot be undone!")
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            return "clear_all"
        
        if st.button("🔄 Reset System", type="secondary"):
            return "reset_system"
    
    return None