# components/header.py
import streamlit as st

def display_header(title="CleverumGPT", subtitle=None):
    """
    Display the main application header with customizable title and subtitle.
    
    Args:
        title (str): Main title of the application
        subtitle (str): Subtitle/description text
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {title}</h1>
    </div>
    """, unsafe_allow_html=True)

def display_page_header(page_title, icon="📄"):
    """
    Display a smaller header for individual pages/sections.
    
    Args:
        page_title (str): Title of the current page/section
        icon (str): Emoji icon to display
    """
    st.markdown(f"""
    <div style="text-align: left; padding: 1rem 0; margin-bottom: 1rem;">
        <h2>{icon} {page_title}</h2>
    </div>
    """, unsafe_allow_html=True)

def display_welcome_message():
    """Mensaje de bienvenida minimal para MVP."""
    # Removido: explicación larga y bullets para mantener MVP limpio
    return