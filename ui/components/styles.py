# components/styles.py
import streamlit as st

def apply_custom_css():
    """Apply custom CSS styles to the Streamlit app."""
    st.markdown("""
    <style>
        .main-header {
            text-align: left;
            padding: 0.5rem 0;
            color: black;
            margin-bottom: 1rem;
        }
        
        .status-card {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 0.5rem 0;
        }
        
        .metric-card {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: left;
            margin: 0.2rem;
        }
        
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .user-message {
            background: #e3f2fd;
            border-left-color: #2196f3;
        }
        
        .ai-message {
            background: #f3e5f5;
            border-left-color: #9c27b0;
        }
        
        .source-tag {
            background: #667eea;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin: 0.2rem;
            display: inline-block;
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 0.75rem;
            border-radius: 5px;
            border: 1px solid #c3e6cb;
            margin: 0.5rem 0;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
            margin: 0.5rem 0;
        }
        
        .document-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            text-align: left;
        }
        
        .document-card:hover {
            background: #e9ecef;
            transition: background-color 0.3s ease;
        }
        
        .danger-zone {
            border: 2px dashed #dc3545;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            background: #fff5f5;
        }
        
        .stats-container {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            text-align: left;
        }

        /* Make sidebar navigation buttons look like links */
        section[data-testid="stSidebar"] .stButton > button {
            background: none !important;
            border: none !important;
            color: #0a66c2 !important; /* link color */
            text-align: left !important;
            padding: 0.25rem 0 !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            text-decoration: underline;
            background: transparent !important;
        }
        /* Radio to look like plain links (if used) */
        section[data-testid="stSidebar"] .stRadio > div { gap: 0.25rem; }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { font-weight: 400; }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] svg { display: none; }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { text-decoration: underline; }
        /* Highlight current selection via caption style */
        section[data-testid="stSidebar"] .st-emotion-cache-1jicfl2 { color: #0a66c2; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)