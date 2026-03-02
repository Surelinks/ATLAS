"""
Atlas AI - Streamlit UI
Ops Copilot Interface for SOP Query and Management
"""
import streamlit as st
import requests
import sys
from pathlib import Path
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Atlas AI - Ops Copilot",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .source-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if backend API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def query_sops(question: str, top_k: int = 3):
    """Query SOPs through API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/ops-copilot/query",
            json={
                "question": question,
                "top_k": top_k,
                "include_sources": True
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return None


def upload_document(uploaded_file):
    """Upload document through API"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(
            f"{API_BASE_URL}/api/v1/ops-copilot/ingest",
            files=files,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None


def get_statistics():
    """Get system statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ops-copilot/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None


def list_documents():
    """List all ingested documents"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/ops-copilot/documents", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">🔧 Atlas AI - Ops Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered SOP Enforcement & Operational Intelligence</div>', unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Backend API is not running. Please start the API server: `cd backend && uvicorn app.main:app --reload`")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("📊 System Status")
        
        stats = get_statistics()
        if stats:
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.metric("Total Chunks", stats.get("total_chunks", 0))
        
        st.divider()
        
        st.header("📚 Document Library")
        docs = list_documents()
        if docs and docs.get("documents"):
            st.write(f"**{docs['count']} documents indexed:**")
            for doc_id in docs["documents"]:
                st.text(f"• {doc_id}")
        else:
            st.info("No documents uploaded yet")
        
        st.divider()
        
        st.header("ℹ️ About")
        st.markdown("""
        **Ops Copilot** helps operations teams:
        - Query SOPs instantly
        - Get AI-powered guidance
        - Ensure compliance
        - Reduce errors
        """)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Query SOPs", "📤 Upload Document", "📈 Analytics"])
    
    # Tab 1: Query Interface
    with tab1:
        st.header("Ask Questions About Your SOPs")
        
        # Sample questions
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - What is the power outage response procedure?
            - What safety precautions are required for transformer maintenance?
            - How do I monitor grid stability?
            - What are the steps for incident escalation?
            - What PPE is required for field operations?
            """)
        
        # Query input
        question = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="E.g., What is the transformer maintenance procedure?"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            query_button = st.button("🔍 Search SOPs", type="primary", use_container_width=True)
        with col2:
            top_k = st.number_input("Results", min_value=1, max_value=10, value=3)
        
        if query_button and question:
            with st.spinner("Searching SOPs and generating answer..."):
                result = query_sops(question, top_k)
                
                if result:
                    # Confidence badge
                    confidence = result.get("confidence", "unknown")
                    confidence_color = {
                        "high": "🟢",
                        "medium": "🟡",
                        "low": "🔴",
                        "error": "⚠️"
                    }.get(confidence, "⚪")
                    
                    st.markdown(f"### {confidence_color} Answer (Confidence: {confidence.upper()})")
                    
                    # Answer
                    st.markdown(f"**{result['answer']}**")
                    
                    # Sources
                    if result.get("sources"):
                        st.divider()
                        st.markdown("### 📚 Sources")
                        
                        for source in result["sources"]:
                            with st.container():
                                st.markdown(f"""
                                <div class="source-card">
                                    <strong>[{source['index']}] {source['document']}</strong><br>
                                    <small>Similarity: {source['similarity']:.3f}</small><br>
                                    <em>"{source['excerpt'][:150]}..."</em>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Metadata
                    with st.expander("🔧 Query Details"):
                        st.json(result)
    
    # Tab 2: Document Upload
    with tab2:
        st.header("Upload SOP Documents")
        
        st.info("📄 Supported formats: PDF, DOCX, TXT, MD")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "txt", "md"],
            help="Upload SOP documents to make them searchable"
        )
        
        if uploaded_file:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
            
            if st.button("📤 Upload & Process", type="primary"):
                with st.spinner("Processing document..."):
                    result = upload_document(uploaded_file)
                    
                    if result and result.get("status") == "success":
                        st.success(f"""
                        ✅ **Document processed successfully!**
                        
                        - Document ID: {result.get('document_id')}
                        - Chunks created: {result.get('chunk_count')}
                        - Total tokens: {result.get('total_tokens')}
                        """)
                        st.balloons()
                    elif result:
                        st.error(f"❌ Upload failed: {result.get('message')}")
        
        # Bulk upload info
        with st.expander("📦 Bulk Upload (Advanced)"):
            st.markdown("""
            For bulk uploads, use the API directly:
            
            ```bash
            # Upload via curl
            curl -X POST http://localhost:8000/api/v1/ops-copilot/ingest \\
                 -F "file=@your_document.pdf"
            
            # Or use the Python script
            python ingest_sops.py
            ```
            """)
    
    # Tab 3: Analytics
    with tab3:
        st.header("System Analytics")
        
        stats = get_statistics()
        docs = list_documents()
        
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="📚 Total Documents",
                    value=stats.get("total_documents", 0)
                )
            
            with col2:
                st.metric(
                    label="📄 Total Chunks",
                    value=stats.get("total_chunks", 0)
                )
            
            with col3:
                avg_chunks = (
                    stats.get("total_chunks", 0) / stats.get("total_documents", 1)
                    if stats.get("total_documents", 0) > 0 else 0
                )
                st.metric(
                    label="📊 Avg Chunks/Doc",
                    value=f"{avg_chunks:.1f}"
                )
            
            st.divider()
            
            # Document list
            if docs and docs.get("documents"):
                st.subheader("📑 Indexed Documents")
                
                for i, doc_id in enumerate(docs["documents"], 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>{i}. {doc_id}</strong>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("Unable to fetch statistics")
        
        st.divider()
        
        # API Status
        st.subheader("🔌 API Status")
        if check_api_health():
            st.success("✅ Backend API is running")
            st.code(f"API Base URL: {API_BASE_URL}")
        else:
            st.error("❌ Backend API is not responding")


if __name__ == "__main__":
    main()
