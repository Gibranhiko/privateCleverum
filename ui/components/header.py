# components/header.py
import streamlit as st

def display_header(title="CleverumGPT", subtitle="Your Personal Document AI Assistant"):
    """
    Display the main application header with customizable title and subtitle.
    
    Args:
        title (str): Main title of the application
        subtitle (str): Subtitle/description text
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {title}</h1>
        <p>{subtitle}</p>
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
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <h2>{icon} {page_title}</h2>
    </div>
    """, unsafe_allow_html=True)

def display_welcome_message():
    """Display a welcome message for new users."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
        <p>Upload your documents and start chatting with your personal AI assistant. 
           Your data stays private and secure on your local machine.</p>
        <ul>
            <li>📁 Upload documents (PDF, TXT, DOCX, MD)</li>
            <li>💬 Chat with your documents using AI</li>
            <li>📊 Monitor system statistics and performance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)