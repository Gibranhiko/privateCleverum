# components/document_manager.py
import streamlit as st
import os
import tempfile
import time
from pathlib import Path

class DocumentManager:
    """Handles document upload, processing, and management."""
    
    def __init__(self, private_gpt_instance):
        self.private_gpt = private_gpt_instance
    
    def display_upload_section(self):
        """Display the document upload interface."""
        st.subheader("📤 Upload Documents")
        
        if not self.private_gpt:
            st.error("System not initialized. Please check your setup.")
            return
        
        # Initialize session state for tracking uploaded file names
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = set()
        
        # File upload widget
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'docx', 'md'],
            help="Select one or more documents to add to your knowledge base"
        )
        
        if uploaded_files:
            # Filter out already processed files
            new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]
            
            if new_files:
                self._process_uploaded_files(new_files)
                # Mark files as processed
                for f in new_files:
                    st.session_state.processed_files.add(f.name)
            elif uploaded_files:
                st.info("✅ All selected files have already been processed.")
    
    def _process_uploaded_files(self, uploaded_files):
        """Process and add uploaded files to the system."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        successful_count = 0
        errors = []
        
        for idx, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (idx + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Process individual file
            success, error_msg = self._process_single_file(uploaded_file)
            if success:
                successful_count += 1
            elif error_msg:
                errors.append(f"**{uploaded_file.name}**: {error_msg}")
        
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Show results
        if successful_count > 0:
            st.success(f"✅ Successfully processed {successful_count} file(s)!")
            if errors:
                with st.expander(f"⚠️ {len(errors)} file(s) failed (click to see details)"):
                    for error in errors:
                        st.markdown(error)
        elif len(uploaded_files) > 0:
            st.error(f"❌ Could not process any of the {len(uploaded_files)} file(s):")
            for error in errors:
                st.markdown(f"• {error}")
    
    def _process_single_file(self, uploaded_file):
        """Process a single uploaded file. Returns (success, error_msg)."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        try:
            result = self.private_gpt.add_document(tmp_path, uploaded_file.name)
            
            if result['success']:
                # Show success details in expander
                with st.expander(f"✅ {uploaded_file.name} processed successfully"):
                    if result['doc_info']:
                        st.write(f"**Document ID:** {result['doc_info']['doc_id']}")
                        st.write(f"**Chunks created:** {result['doc_info']['num_chunks']}")
                        st.write(f"**File size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
                return True, None
            else:
                return False, result['message']
                
        except Exception as e:
            return False, str(e)
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def display_document_list(self):
        """Display the list of current documents."""
        st.subheader("📋 Current Documents")
        
        try:
            documents = self.private_gpt.get_documents()
            
            if not documents:
                st.info("📝 No documents uploaded yet. Upload some documents to get started!")
                return
            
            # Search and filter
            search_term = st.text_input("🔍 Search documents", placeholder="Enter filename or keywords...")
            
            # Filter documents based on search
            if search_term:
                documents = [doc for doc in documents 
                           if search_term.lower() in doc.get('filename', '').lower()]
            
            # Sort options
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{len(documents)} document(s) found**")
            with col2:
                sort_by = st.selectbox("Sort by", ["filename", "size", "chunks"], label_visibility="collapsed")
            
            # Sort documents
            if sort_by == "size":
                documents.sort(key=lambda x: x.get('file_size', 0), reverse=True)
            elif sort_by == "chunks":
                documents.sort(key=lambda x: x.get('num_chunks', 0), reverse=True)
            else:
                documents.sort(key=lambda x: x.get('filename', '').lower())
            
            # Display documents
            for doc in documents:
                self._display_document_card(doc)
        
        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")
    
    def _display_document_card(self, doc):
        """Display a single document card."""
        with st.container():
            st.markdown('<div class="document-card">', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(f"📄 **{doc.get('filename', 'Unknown')}**")
                st.caption(f"ID: {doc.get('doc_id', 'N/A')}")
            
            with col2:
                chunks = doc.get('num_chunks', 0)
                st.metric("Chunks", chunks)
            
            with col3:
                size_bytes = doc.get('file_size', 0)
                size_mb = size_bytes / (1024 * 1024) if size_bytes else 0
                st.metric("Size", f"{size_mb:.1f}MB")
            
            with col4:
                # Document actions
                if st.button("📖 View", key=f"view_{doc.get('doc_id')}", help="View document details"):
                    self._show_document_details(doc)
            
            with col5:
                if st.button("🗑️ Delete", key=f"delete_{doc.get('doc_id')}", 
                           help="Delete document", type="secondary"):
                    self._delete_document(doc)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _show_document_details(self, doc):
        """Show detailed information about a document."""
        with st.modal(f"Document Details: {doc.get('filename', 'Unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information:**")
                st.write(f"• **Filename:** {doc.get('filename', 'N/A')}")
                st.write(f"• **Document ID:** {doc.get('doc_id', 'N/A')}")
                st.write(f"• **File Size:** {doc.get('file_size', 0):,} bytes")
                st.write(f"• **Number of Chunks:** {doc.get('num_chunks', 0)}")
            
            with col2:
                st.write("**Processing Statistics:**")
                if doc.get('num_chunks', 0) > 0:
                    avg_chunk_size = doc.get('file_size', 0) / doc.get('num_chunks', 1)
                    st.write(f"• **Avg Chunk Size:** {avg_chunk_size:.0f} bytes")
                
                # Additional metadata if available
                if 'created_at' in doc:
                    st.write(f"• **Added:** {doc['created_at']}")
                if 'file_type' in doc:
                    st.write(f"• **Type:** {doc['file_type']}")
    
    def _delete_document(self, doc):
        """Delete a document after confirmation."""
        doc_id = doc.get('doc_id')
        filename = doc.get('filename', 'Unknown')
        
        # Confirmation in session state
        confirm_key = f"confirm_delete_{doc_id}"
        
        if st.session_state.get(confirm_key, False):
            with st.spinner(f"Deleting {filename}..."):
                result = self.private_gpt.remove_document(doc_id)
            
            if result['success']:
                st.success(f"✅ {filename} deleted successfully!")
                st.session_state[confirm_key] = False
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Failed to delete {filename}: {result['message']}")
        else:
            st.session_state[confirm_key] = True
            st.warning(f"⚠️ Click delete again to confirm removal of {filename}")
            st.rerun()
    
    def display_bulk_actions(self):
        """Display bulk action controls."""
        st.subheader("🔧 Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Reindex All Documents", help="Rebuild the search index"):
                self._reindex_all_documents()
        
        with col2:
            if st.button("🧹 Clear Empty Entries", help="Remove orphaned entries"):
                self._cleanup_database()
    
    def display_danger_zone(self):
        """Display dangerous actions with appropriate warnings."""
        st.subheader("⚠️ Danger Zone")
        
        st.markdown('<div class="danger-zone">', unsafe_allow_html=True)
        st.warning("**Warning:** These actions cannot be undone!")
        
        confirm_key = "confirm_clear_all"
        
        if st.session_state.get(confirm_key, False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete Everything", type="primary"):
                    self._clear_all_documents()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state[confirm_key] = False
                    st.rerun()
        else:
            if st.button("🗑️ Clear All Documents", type="secondary"):
                st.session_state[confirm_key] = True
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _clear_all_documents(self):
        """Clear all documents from the system."""
        with st.spinner("Clearing all documents..."):
            result = self.private_gpt.clear_all_documents()
        
        if result['success']:
            # Also clear chat history
            if 'chat_history' in st.session_state:
                st.session_state.chat_history = []
            
            st.success("✅ All documents cleared successfully!")
            st.session_state['confirm_clear_all'] = False
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ Failed to clear documents: {result['message']}")
    
    def _reindex_all_documents(self):
        """Reindex all documents."""
        with st.spinner("Reindexing documents..."):
            # This would need to be implemented in your PrivateGPT class
            # result = self.private_gpt.reindex_all_documents()
            st.info("Reindexing functionality would be implemented here")
    
    def _cleanup_database(self):
        """Clean up orphaned database entries."""
        with st.spinner("Cleaning up database..."):
            # This would need to be implemented in your PrivateGPT class
            # result = self.private_gpt.cleanup_database()
            st.info("Database cleanup functionality would be implemented here")