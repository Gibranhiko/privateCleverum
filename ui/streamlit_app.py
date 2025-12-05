import sys
import pathlib

# Add project root to PYTHONPATH so `import privategpt` works
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from privategpt.main import PrivateGPT

# UI components
from ui.components.styles import apply_custom_css
from ui.components.header import display_header, display_welcome_message
from ui.components.sidebar import (
    display_system_status, display_navigation_menu, display_help_section, display_danger_zone
)
from ui.components.chat import ChatInterface
from ui.components.document_uploader import DocumentManager

# --- App Initialization ---
st.set_page_config(
    page_title="PrivateGPT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# --- Instantiate Core Logic ---
if 'private_gpt' not in st.session_state:
    st.session_state.private_gpt = PrivateGPT()
private_gpt = st.session_state.private_gpt

# --- Sidebar ---
system_ok = display_system_status(private_gpt)
nav = display_navigation_menu()
danger_action = display_danger_zone()
display_help_section()

# --- Handle Danger Zone Actions ---
if danger_action == "clear_all":
    result = private_gpt.clear_all_documents()
    if result['success']:
        st.sidebar.success("✅ All data cleared!")
        st.experimental_rerun()
    else:
        st.sidebar.error(f"Error: {result['message']}")
elif danger_action == "reset_system":
    # For now, just clear all documents (extend as needed)
    result = private_gpt.clear_all_documents()
    if result['success']:
        st.sidebar.success("✅ System reset!")
        st.experimental_rerun()
    else:
        st.sidebar.error(f"Error: {result['message']}")

# --- Main Area ---
display_header()

if nav == "documents":
    display_welcome_message()
    doc_manager = DocumentManager(private_gpt)
    doc_manager.display_upload_section()
    doc_manager.display_document_list()
    # Optionally: doc_manager.display_bulk_actions() / doc_manager.display_danger_zone()
elif nav == "chat":
    chat = ChatInterface(private_gpt)
    chat.display_chat_interface()
elif nav == "statistics":
    st.subheader("📈 System Statistics")
    stats = private_gpt.get_document_stats() if hasattr(private_gpt, 'get_document_stats') else {}
    if stats:
        st.json(stats)
    else:
        st.info("Statistics functionality coming soon!")
elif nav == "settings":
    st.subheader("⚙️ Settings")
    st.info("Settings page coming soon!")
else:
    st.info("Select a page from the sidebar.")
