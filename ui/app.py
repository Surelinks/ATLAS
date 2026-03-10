"""
ATLAS AI - Operational Intelligence Platform
Enterprise-Grade UI for 330kV/132kV Substation Operations

Professional interface for power utility operators with:
- Real-time SCADA monitoring
- Incident correlation and root cause analysis
- Operations Copilot (RAG-based SOP assistant)
- Predictive transformer diagnostics (DGA)
"""

import streamlit as st
import httpx
import asyncio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
import sys
from pathlib import Path

# Add backend to path for simulator access
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from app.services.scada_simulator import (
        GridDataSimulator, 
        simulate_historical_incidents, 
        analyze_causal_chain
    )
    SIMULATOR_AVAILABLE = True
except ImportError:
    SIMULATOR_AVAILABLE = False
    print("Warning: SCADA simulator not available")

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="ATLAS AI - Operational Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get API URL from environment variable or use localhost for development
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ==================== ENHANCED STYLING ====================

st.markdown("""
<style>
/* ============================================
   ATLAS AI - DARK ENTERPRISE THEME
   Colors: #0F172A (bg), #F1F5F9 (text), #60A5FA (accent)
   ============================================ */

/* Global Reset & Base Styles */
.stApp {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

.main .block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    color: #F1F5F9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-weight: 600;
}

h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }

p, span, div, label {
    color: #94A3B8;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ============================================
   SIDEBAR STYLING
   ============================================ */
[data-testid="stSidebar"] {
    background: #1E293B !important;
    border-right: 1px solid #334155;
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}

/* Sidebar Logo Area */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #334155;
    margin-bottom: 1.5rem;
}

.sidebar-logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.sidebar-logo-text h1 {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    margin: 0 !important;
    color: #F1F5F9 !important;
}

.sidebar-logo-text p {
    font-size: 0.7rem;
    color: #64748B;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Navigation Section Title */
.nav-section-title {
    font-size: 0.65rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 1.5rem 0 0.75rem 0;
}

/* Status Indicators */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-online {
    background: rgba(52, 211, 153, 0.15);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.3);
    animation: pulse-green 2s infinite;
}

.status-connected {
    background: rgba(52, 211, 153, 0.15);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.3);
    animation: pulse-green 2s infinite;
}

@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
    50% { box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}

/* Quick Stats Grid */
.quick-stat-card {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 0.75rem 0.5rem;
    text-align: center;
}

.quick-stat-card .value {
    font-size: 1.125rem;
    font-weight: 700;
    color: #F1F5F9;
}

.quick-stat-card .label {
    font-size: 0.6rem;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* ============================================
   METRIC CARDS
   ============================================ */
.metric-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-left: 4px solid;
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
}

.metric-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(96, 165, 250, 0.08) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.metric-card:hover::after {
    opacity: 1;
}

.metric-card.normal { border-left-color: #10B981; }
.metric-card.warning { border-left-color: #F59E0B; }
.metric-card.critical { border-left-color: #EF4444; }
.metric-card.info { border-left-color: #60A5FA; }

.metric-card .title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    color: #F1F5F9;
    line-height: 1.2;
}

.metric-card .subtitle {
    font-size: 0.8rem;
    color: #64748B;
    margin-top: 0.25rem;
}

/* ============================================
   CONTENT CARDS
   ============================================ */
.content-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.content-card .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #334155;
}

.content-card .header h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    font-size: 1rem;
}

/* ============================================
   BADGES
   ============================================ */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
    border: 1px solid;
}

.badge-normal {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border-color: rgba(52, 211, 153, 0.3);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border-color: rgba(251, 191, 36, 0.3);
}

.badge-critical {
    background: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border-color: rgba(248, 113, 113, 0.3);
    animation: pulse-red 1.5s infinite;
}

@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
}

.badge-info {
    background: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    border-color: rgba(96, 165, 250, 0.3);
}

/* ============================================
   CHAT INTERFACE
   ============================================ */
.chat-message {
    display: flex;
    gap: 0.875rem;
    margin-bottom: 1.5rem;
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.chat-message.user {
    flex-direction: row-reverse;
}

.chat-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 0.875rem;
}

.chat-avatar.user {
    background: #3B82F6;
}

.chat-avatar.assistant {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
}

.chat-bubble {
    max-width: 80%;
    padding: 0.875rem 1.125rem;
    border-radius: 12px;
    font-size: 0.875rem;
    line-height: 1.6;
}

.chat-message.user .chat-bubble {
    background: #3B82F6;
    color: white;
    border-bottom-right-radius: 4px;
}

.chat-message.assistant .chat-bubble {
    background: #0F172A;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-bottom-left-radius: 4px;
}

/* ============================================
   PROGRESS BARS
   ============================================ */
.progress-container {
    background: #334155;
    border-radius: 9999px;
    height: 8px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    border-radius: 9999px;
    transition: width 0.8s ease;
}

.progress-bar.green {
    background: linear-gradient(90deg, #10B981, #34D399);
}

.progress-bar.amber {
    background: linear-gradient(90deg, #F59E0B, #FBBF24);
}

.progress-bar.red {
    background: linear-gradient(90deg, #EF4444, #F87171);
}

.progress-bar.blue {
    background: linear-gradient(90deg, #3B82F6, #60A5FA);
}

/* ============================================
   INCIDENT CARDS
   ============================================ */
.incident-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.incident-card:hover {
    border-color: #475569;
    transform: translateX(4px);
}

/* ============================================
   FORM ELEMENTS
   ============================================ */
.stTextInput > div > div {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

.stTextInput > div > div:focus-within {
    border-color: #60A5FA !important;
    box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.15) !important;
}

.stTextInput input {
    color: #F1F5F9 !important;
}

.stTextInput input::placeholder {
    color: #64748B !important;
}

.stButton > button {
    background: #3B82F6 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.625rem 1.25rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #2563EB !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* ============================================
   SCROLLBAR
   ============================================ */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0F172A;
}

::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .metric-card {
        margin-bottom: 0.75rem;
    }
    
    [data-testid="column"] {
        width: 100% !important;
        flex: 100% !important;
    }
}

/* Keyboard shortcuts indicator */
.shortcut-hint {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    background-color: #334155;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    color: #94A3B8;
    margin-left: 0.5rem;
}

/* Enhanced loading skeleton */
.skeleton {
    animation: skeleton-loading 1s linear infinite alternate;
    background: linear-gradient(90deg, #1E293B 0%, #334155 50%, #1E293B 100%);
    background-size: 200% 100%;
    border-radius: 0.5rem;
    height: 1.5rem;
    margin: 0.5rem 0;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Export button styling */
.export-btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #1E3A8A;
    color: white;
    border-radius: 0.375rem;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
    border: none;
    cursor: pointer;
}

.export-btn:hover {
    background-color: #1E40AF;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

/* Light theme overrides */
.light-theme .main {
    background-color: #F8FAFC !important;
}

.light-theme .main, .light-theme .main p, .light-theme .main span, 
.light-theme .main div, .light-theme .main label {
    color: #0F172A !important;
}

.light-theme .metric-card {
    background: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.light-theme [data-testid="stSidebar"] {
    background-color: #F1F5F9 !important;
}

/* Hide branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZE STATE ====================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "simulator" not in st.session_state and SIMULATOR_AVAILABLE:
    st.session_state.simulator = GridDataSimulator(station_id="330kV_Station_Alpha")

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True  # Start with demo data

if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # Default to dark theme

if "page_size" not in st.session_state:
    st.session_state.page_size = 15  # Items per page

if "incident_page" not in st.session_state:
    st.session_state.incident_page = 0

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "severity_filter" not in st.session_state:
    st.session_state.severity_filter = "All"

# ==================== API CLIENT ====================

async def call_api(endpoint: str, method: str = "GET", **kwargs) -> Optional[Dict]:
    """Async API client with error handling"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{API_BASE_URL}{endpoint}"
            
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
    except httpx.ConnectError:
        st.error("Cannot connect to backend API. Ensure server is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"API request failed: {str(e)}")
        return None

# ==================== UTILITY FUNCTIONS ====================

def export_to_csv(data: List[Dict], filename: str):
    """Export data to CSV format"""
    if not data:
        st.warning("No data to export")
        return
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Export CSV",
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        width="stretch"
    )

def paginate_data(data: List, page: int, page_size: int) -> tuple:
    """Paginate list data"""
    start = page * page_size
    end = start + page_size
    total_pages = (len(data) + page_size - 1) // page_size
    return data[start:end], total_pages

def filter_incidents(incidents: List[Dict], search: str, severity: str) -> List[Dict]:
    """Filter incidents by search query and severity"""
    filtered = incidents
    
    if search:
        search_lower = search.lower()
        filtered = [
            inc for inc in filtered
            if search_lower in inc.get('description', '').lower() or
               search_lower in inc.get('asset_id', '').lower()
        ]
    
    if severity != "All":
        filtered = [inc for inc in filtered if inc.get('severity', '').lower() == severity.lower()]
    
    return filtered

def show_loading_skeleton(num_lines: int = 3):
    """Display loading skeleton"""
    skeleton_html = ""
    for _ in range(num_lines):
        skeleton_html += '<div class="skeleton"></div>'
    st.markdown(skeleton_html, unsafe_allow_html=True)

def show_keyboard_shortcuts():
    """Display keyboard shortcuts help"""
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        st.markdown("""
        <div style='font-size: 0.9rem;'>
            <p><kbd>Ctrl+K</kbd> - Focus search</p>
            <p><kbd>Ctrl+U</kbd> - Upload document</p>
            <p><kbd>Ctrl+Enter</kbd> - Send message</p>
            <p><kbd>Ctrl+E</kbd> - Export data</p>
            <p><kbd>Esc</kbd> - Clear filters</p>
        </div>
        """, unsafe_allow_html=True)

# ==================== SIDEBAR ====================

with st.sidebar:
    # Enhanced Logo Header
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">⚡</div>
        <div class="sidebar-logo-text">
            <h1>ATLAS AI</h1>
            <p>Operational Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown('<p class="nav-section-title">Navigation</p>', unsafe_allow_html=True)
    
    nav_options = [
        "Dashboard",
        "Operations Copilot",
        "Incident Analyzer",
        "System Analytics"
    ]
    
    selected_module = st.radio(
        "Select Module",
        nav_options,
        label_visibility="collapsed"
    )
    
    # Settings Section
    st.markdown('<p class="nav-section-title">Settings</p>', unsafe_allow_html=True)
    
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("🌙 Dark",
                    disabled=st.session_state.theme == "dark"):
            st.session_state.theme = "dark"
            st.rerun()
    
    with theme_col2:
        if st.button("☀️ Light",
                    disabled=st.session_state.theme == "light"):
            st.session_state.theme = "light"
            st.rerun()
    
    show_keyboard_shortcuts()
    
    # System Status Section
    st.markdown('<p class="nav-section-title">System Status</p>', unsafe_allow_html=True)
    
    # Check API health
    try:
        health_response = asyncio.run(call_api("/health"))
        api_status = "ONLINE" if health_response else "OFFLINE"
        api_class = "status-online" if health_response else "status-offline"
    except:
        api_status = "OFFLINE"
        api_class = "status-offline"
    
    # Status indicators
    status_col1, status_col2 = st.columns([1, 1])
    with status_col1:
        st.markdown('<span style="font-size: 0.8rem; color: #94A3B8;">API Server</span>', unsafe_allow_html=True)
    with status_col2:
        st.markdown(f'<span class="status-badge {api_class}"><span class="status-dot"></span>{api_status}</span>', unsafe_allow_html=True)
    
    scada_col1, scada_col2 = st.columns([1, 1])
    with scada_col1:
        st.markdown('<span style="font-size: 0.8rem; color: #94A3B8;">SCADA Feed</span>', unsafe_allow_html=True)
    with scada_col2:
        scada_status = "CONNECTED" if SIMULATOR_AVAILABLE else "OFFLINE"
        scada_class = "status-connected" if SIMULATOR_AVAILABLE else "status-offline"
        st.markdown(f'<span class="status-badge {scada_class}"><span class="status-dot"></span>{scada_status}</span>', unsafe_allow_html=True)
    
    # Quick Stats Section
    st.markdown('<p class="nav-section-title">Quick Stats</p>', unsafe_allow_html=True)
    
    if SIMULATOR_AVAILABLE:
        incidents = st.session_state.simulator.get_active_incidents()
        st.metric("Active Incidents", len(incidents))
    else:
        st.metric("Active Incidents", "N/A")
    
    # Get document count from API
    try:
        docs_response = asyncio.run(call_api("/api/v1/ops-copilot/documents"))
        if docs_response and "documents" in docs_response:
            doc_count = len(docs_response["documents"])
        else:
            doc_count = 0
    except:
        doc_count = 0
    
    st.metric("SOPs Indexed", doc_count)

# ==================== MAIN CONTENT ====================

# Dashboard Module
if selected_module == "Dashboard":
    st.markdown("""
    <div class="page-header">
        <h1>Operational Dashboard</h1>
        <p>Real-time monitoring for 330kV/132kV Station Alpha</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not SIMULATOR_AVAILABLE:
        st.error("SCADA simulator unavailable. Install backend dependencies.")
    else:
        # Generate fresh telemetry
        scada_data = st.session_state.simulator.generate_scada_telemetry()
        
        # Key metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            incidents = st.session_state.simulator.get_active_incidents()
            critical_count = len([i for i in incidents if i["severity"].value == "Critical"])
            
            st.markdown(f"""
            <div class="metric-card severity-critical">
                <h3>Critical Incidents</h3>
                <p class="value">{critical_count}</p>
                <p class="label">Requires Immediate Action</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            sop_coverage = 92 if doc_count > 0 else 0
            st.markdown(f"""
            <div class="metric-card severity-medium">
                <h3>SOP Coverage</h3>
                <p class="value">{sop_coverage}%</p>
                <p class="label">{doc_count} Procedures Indexed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Get transformer temperature
            t401_temp = scada_data.measurements.get("T-401", {}).get("temperature_c", 0)
            temp_status = "Normal" if t401_temp < 85 else "Warning"
            temp_class = "severity-low" if t401_temp < 85 else "severity-high"
            
            st.markdown(f"""
            <div class="metric-card {temp_class}">
                <h3>Transformer T-401</h3>
                <p class="value">{t401_temp}°C</p>
                <p class="label">{temp_status} Temperature</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            bus_voltage = scada_data.measurements.get("BUS-330", {}).get("voltage_kv", 330)
            voltage_pu = bus_voltage / 330.0
            voltage_status = "Normal" if 0.95 <= voltage_pu <= 1.05 else "Unstable"
            voltage_class = "severity-low" if 0.95 <= voltage_pu <= 1.05 else "severity-high"
            
            st.markdown(f"""
            <div class="metric-card {voltage_class}">
                <h3>330kV Busbar</h3>
                <p class="value">{bus_voltage:.1f} kV</p>
                <p class="label">{voltage_status} ({voltage_pu:.3f} pu)</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Alarms section
        if scada_data.alarms:
            st.markdown("### Active Alarms")
            for alarm in scada_data.alarms:
                st.warning(alarm, icon="⚠️")
        
        st.markdown("---")
        
        # Real-time asset monitoring
        st.markdown("### Asset Telemetry (Live SCADA)")
        
        tab1, tab2, tab3 = st.tabs(["Transformers", "Circuit Breakers", "Busbars"])
        
        with tab1:
            transformer_data = {
                asset_id: data for asset_id, data in scada_data.measurements.items()
                if "T-" in asset_id
            }
            
            if transformer_data:
                df_transformers = pd.DataFrame([
                    {
                        "Asset": asset_id,
                        "Temperature (°C)": data.get("temperature_c", 0),
                        "Load (%)": data.get("load_percent", 0),
                        "Top Oil (°C)": data.get("top_oil_temp_c", 0),
                        "Cooling Fans": data.get("cooling_fans_running", 0),
                        "Status": "Normal" if data.get("temperature_c", 0) < 85 else "Warning"
                    }
                    for asset_id, data in transformer_data.items()
                ])
                
                st.dataframe(
                    df_transformers,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Status",
                            help="Operational status"
                        )
                    }
                )
                
                # Temperature trend chart
                fig_temp = go.Figure()
                for asset_id, data in transformer_data.items():
                    fig_temp.add_trace(go.Bar(
                        x=[asset_id],
                        y=[data.get("temperature_c", 0)],
                        name=asset_id,
                        text=[f"{data.get('temperature_c', 0)}°C"],
                        textposition='auto'
                    ))
                
                fig_temp.add_hline(y=85, line_dash="dash", line_color="red",
                                   annotation_text="Warning Threshold (85°C)")
                
                fig_temp.update_layout(
                    title="Transformer Temperature Monitoring",
                    xaxis_title="Asset",
                    yaxis_title="Temperature (°C)",
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig_temp, width="stretch")
        
        with tab2:
            breaker_data = {
                asset_id: data for asset_id, data in scada_data.measurements.items()
                if "CB-" in asset_id
            }
            
            if breaker_data:
                df_breakers = pd.DataFrame([
                    {
                        "Asset": asset_id,
                        "Status": data.get("status", "UNKNOWN"),
                        "Current (A)": data.get("current_a", 0),
                        "Op. Time (ms)": data.get("operating_time_ms", 0),
                        "Operations": data.get("operations_count", 0)
                    }
                    for asset_id, data in breaker_data.items()
                ])
                
                st.dataframe(df_breakers, hide_index=True)
        
        with tab3:
            busbar_data = {
                asset_id: data for asset_id, data in scada_data.measurements.items()
                if "BUS-" in asset_id
            }
            
            if busbar_data:
                df_busbars = pd.DataFrame([
                    {
                        "Asset": asset_id,
                        "Voltage (kV)": data.get("voltage_kv", 0),
                        "Voltage (pu)": data.get("voltage_pu", 0),
                        "Frequency (Hz)": data.get("frequency_hz", 60.0),
                        "Status": "Normal" if 0.95 <= data.get("voltage_pu", 1.0) <= 1.05 else "Abnormal"
                    }
                    for asset_id, data in busbar_data.items()
                ])
                
                st.dataframe(df_busbars, hide_index=True)
        
        st.markdown("---")
        
        # Recent operational events
        st.markdown("### Recent Operational Events (Last 7 Days)")
        
        historical_incidents = simulate_historical_incidents(days_back=7)
        
        df_incidents = pd.DataFrame(historical_incidents[:15])  # Show latest 15
        df_incidents["timestamp"] = pd.to_datetime(df_incidents["timestamp"])
        df_incidents["date"] = df_incidents["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        
        display_df = df_incidents[["date", "asset_id", "description", "severity", "status", "customers_affected"]]
        display_df.columns = ["Timestamp", "Asset", "Event", "Severity", "Status", "Customers Affected"]
        
        st.dataframe(
            display_df,
            hide_index=True,
            column_config={
                "Severity": st.column_config.SelectboxColumn(
                    "Severity",
                    options=["Low", "Medium", "High", "Critical"]
                )
            }
        )

# Operations Copilot Module  
elif selected_module == "Operations Copilot":
    st.markdown("""
    <div class="page-header">
        <h1>Operations Copilot</h1>
        <p>AI-powered assistant for Standard Operating Procedures and operational guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3-column layout: Upload | Chat | Context
    col_upload, col_chat, col_context = st.columns([1, 2, 1])
    
    with col_upload:
        st.markdown("### Document Management")
        
        # Upload section
        with st.expander("Upload SOPs", expanded=False):
            uploaded_files = st.file_uploader(
                "Upload Standard Operating Procedures",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                label_visibility="collapsed"
            )
            
            if uploaded_files and st.button("Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    for file in uploaded_files:
                        files = {"file": (file.name, file.getvalue(), file.type)}
                        result = asyncio.run(
                            call_api("/api/v1/ops-copilot/ingest", method="POST", files=files)
                        )
                        
                        if result and result.get("status") == "success":
                            chunk_count = result.get("chunk_count", "?")
                            st.success(f"✅ Processed: {file.name} ({chunk_count} chunks)")
                        elif result and result.get("status") == "error":
                            st.error(f"❌ Failed: {file.name} - {result.get('message', 'Unknown error')}")
                        else:
                            st.error(f"❌ Failed: {file.name} - No response from server")
        
        # Document list
        st.markdown("#### Indexed Documents")
        docs_response = asyncio.run(call_api("/api/v1/ops-copilot/documents"))
        
        if docs_response and "documents" in docs_response:
            documents = docs_response["documents"]
            
            for doc in documents:
                # Handle both string (document ID) and dict formats
                if isinstance(doc, str):
                    doc_name = doc
                    doc_id = doc
                    chunk_count = "N/A"
                else:
                    doc_name = doc.get("name", "Unknown")
                    doc_id = doc.get("id", "")
                    chunk_count = doc.get("chunk_count", 0)
                
                with st.container():
                    st.markdown(f"""
                    <div class="content-card" style="margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="color: #F1F5F9;">📄 {doc_name}</strong>
                            <span class="badge-info">{chunk_count} chunks</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No documents indexed yet. Upload SOPs to get started.")
    
    with col_chat:
        st.markdown("### Chat Interface")
        
        # Demo mode toggle
        demo_mode = st.checkbox("Demo Mode (Sample Questions)", value=st.session_state.demo_mode)
        st.session_state.demo_mode = demo_mode
        
        if demo_mode:
            st.markdown("**Quick Questions:**")
            demo_queries = [
                "What is the power outage response procedure?",
                "How do I handle transformer overheating?",
                "What are the steps for grid stability restoration?",
                "Explain the circuit breaker maintenance schedule"
            ]
            
            cols = st.columns(2)
            for idx, query in enumerate(demo_queries):
                with cols[idx % 2]:
                    if st.button(query, key=f"demo_{idx}", width="stretch"):
                        st.session_state.messages.append({"role": "user", "content": query})
        
        # Chat messages
        st.markdown("#### Conversation")
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="chat-avatar user-avatar">👤</div>
                        <div class="chat-bubble user-bubble">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="chat-avatar assistant-avatar">⚡</div>
                        <div class="chat-bubble assistant-bubble">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Ask a question about operational procedures...",
                label_visibility="collapsed",
                placeholder="Type your question here..."
            )
            submit = st.form_submit_button("Send", type="primary", width="stretch")
        
        if submit and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("Searching knowledge base..."):
                response = asyncio.run(
                    call_api("/api/v1/ops-copilot/query", method="POST", json={
                        "question": user_input,
                        "top_k": 3
                    })
                )
                
                if response and "answer" in response:
                    answer = response["answer"]
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    st.error("Failed to get response from API")
    
    with col_context:
        st.markdown("### Retrieved Context")
        
        if st.session_state.messages:
            last_user_msg = next(
                (msg for msg in reversed(st.session_state.messages) if msg["role"] == "user"),
                None
            )
            
            if last_user_msg:
                response = asyncio.run(
                    call_api("/api/v1/ops-copilot/query", method="POST", json={
                        "question": last_user_msg["content"],
                        "top_k": 3
                    })
                )
                
                if response and "sources" in response:
                    st.markdown("#### Source Documents")
                    
                    for idx, source in enumerate(response["sources"][:3]):
                        doc_name = source.get("document_id", "Unknown")
                        similarity = source.get("similarity", 0.0)
                        text = source.get("text", "")[:200]
                        
                        confidence_label = "High" if similarity > 0.7 else "Medium" if similarity > 0.5 else "Low"
                        confidence_class = "badge-success" if similarity > 0.7 else "badge-warning" if similarity > 0.5 else "badge-error"
                        
                        st.markdown(f"""
                        <div class="content-card" style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                <strong style="color: #F1F5F9;">📄 {doc_name}</strong>
                                <span class="{confidence_class}">{confidence_label}</span>
                            </div>
                            <p style="font-size: 0.875rem; color: #94A3B8; margin: 0.5rem 0; line-height: 1.5;">{text}...</p>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                                <span style="font-size: 0.75rem; color: #64748B;">Similarity: {similarity:.1%}</span>
                                <span class="badge-info">Source {idx + 1}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No context retrieved yet. Ask a question to see relevant sources.")
        else:
            st.info("Start a conversation to see retrieved context from SOPs.")

# Incident Analyzer Module
elif selected_module == "Incident Analyzer":
    st.markdown("""
    <div class="page-header">
        <h1>Incident Correlation & Root Cause Analysis</h1>
        <p>Advanced analytics for power system event correlation and fault diagnosis</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not SIMULATOR_AVAILABLE:
        st.error("Simulator unavailable. Install backend dependencies.")
    else:
        # Search and Filter Controls
        col_search, col_severity, col_export = st.columns([2, 1, 1])
        
        with col_search:
            search_query = st.text_input(
                "🔍 Search incidents",
                value=st.session_state.search_query,
                placeholder="Search by description or asset ID...",
                label_visibility="collapsed",
                key="incident_search"
            )
            st.session_state.search_query = search_query
        
        with col_severity:
            severity_filter = st.selectbox(
                "Filter by Severity",
                ["All", "Critical", "High", "Medium", "Low"],
                index=["All", "Critical", "High", "Medium", "Low"].index(st.session_state.severity_filter),
                key="severity_select"
            )
            st.session_state.severity_filter = severity_filter
        
        with col_export:
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("📥 Export CSV", width="stretch", key="export_incidents"):
                historical = simulate_historical_incidents(days_back=7)
                export_to_csv(historical, "incidents")
        
        tab1, tab2, tab3 = st.tabs(["Timeline Analysis", "Root Cause Detection", "DGA Diagnostics"])
        
        with tab1:
            st.markdown("### Incident Timeline & Correlation")
            
            # Get incidents
            historical = simulate_historical_incidents(days_back=7)
            
            # Apply filters
            filtered_incidents = filter_incidents(historical, search_query, severity_filter)
            
            # Pagination
            page_data, total_pages = paginate_data(
                filtered_incidents, 
                st.session_state.incident_page, 
                st.session_state.page_size
            )
            
            st.markdown(f"**Showing {len(page_data)} of {len(filtered_incidents)} incidents**")
            
            # Recent for timeline
            recent_incidents = [i for i in filtered_incidents if i["status"] == "Active" or 
                              (datetime.utcnow() - datetime.fromisoformat(i["timestamp"])).total_seconds() < 3600][:10]
            
            if recent_incidents:
                # Timeline visualization
                fig_timeline = go.Figure()
                
                severity_colors = {
                    "Low": "#10B981",
                    "Medium": "#3B82F6",
                    "High": "#F59E0B",
                    "Critical": "#DC2626"
                }
                
                for inc in recent_incidents:
                    timestamp = datetime.fromisoformat(inc["timestamp"])
                    severity_num = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}[inc["severity"]]
                    
                    fig_timeline.add_trace(go.Scatter(
                        x=[timestamp],
                        y=[severity_num],
                        mode="markers+text",
                        name=inc["asset_id"],
                        text=[inc["asset_id"]],
                        textposition="top center",
                        marker=dict(
                            size=20,
                            color=severity_colors[inc["severity"]],
                            line=dict(width=2, color="white")
                        ),
                        hovertext=inc["description"],
                        hoverinfo="text"
                    ))
                
                fig_timeline.update_layout(
                    title="Incident Timeline - Event Correlation",
                    xaxis_title="Time",
                    yaxis_title="Severity Level",
                    yaxis=dict(
                        tickmode='array',
                        tickvals=[1, 2, 3, 4],
                        ticktext=['Low', 'Medium', 'High', 'Critical']
                    ),
                    height=400,
                    showlegend=False,
                    hovermode='closest',
                    dragmode='pan',  # Enable panning
                    modebar_add=['zoom', 'pan', 'select', 'zoomin', 'zoomout', 'autoscale', 'resetscale']
                )
                
                st.plotly_chart(fig_timeline, config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'incident_timeline',
                        'height': 600,
                        'width': 1200,
                        'scale': 2
                    }
                })
                
                # Incident details table with pagination
                st.markdown("#### Incident Details")
                df_timeline = pd.DataFrame(page_data)
                df_timeline["timestamp"] = pd.to_datetime(df_timeline["timestamp"])
                df_timeline["time"] = df_timeline["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
                
                display = df_timeline[["time", "asset_id", "description", "severity", "status"]]
                display.columns = ["Timestamp", "Asset", "Event Description", "Severity", "Status"]
                
                st.dataframe(display, hide_index=True, width="stretch")
                
                # Pagination controls
                if total_pages > 1:
                    col_prev, col_page, col_next = st.columns([1, 2, 1])
                    
                    with col_prev:
                        if st.button("◀ Previous", disabled=st.session_state.incident_page == 0,
                                   ):
                            st.session_state.incident_page -= 1
                            st.rerun()
                    
                    with col_page:
                        st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.incident_page + 1} of {total_pages}</div>",
                                  unsafe_allow_html=True)
                    
                    with col_next:
                        if st.button("Next ▶", disabled=st.session_state.incident_page >= total_pages - 1,
                                   ):
                            st.session_state.incident_page += 1
                            st.rerun()
                
                display = df_timeline[["time", "asset_id", "description", "severity", "status"]]
                display.columns = ["Time", "Asset", "Event", "Severity", "Status"]

            else:
                st.info("No recent incidents detected. System operating normally.")
        
        with tab2:
            st.markdown("### Root Cause Analysis")
            
            # Get active incidents for correlation
            active_incidents = [i for i in historical if i["status"] == "Active"][:3]
            
            if active_incidents:
                # Perform causal chain analysis
                analysis = analyze_causal_chain(active_incidents)
                
                # Display root cause analysis
                st.markdown(f"""
                <div style="background: #FEF3C7; padding: 1.5rem; border-radius: 6px; 
                     border-left: 4px solid #D97706; margin-bottom: 1.5rem;">
                    <h3 style="margin-top: 0; color: #92400E;">Identified Root Cause</h3>
                    <p style="margin-bottom: 0.5rem;"><strong>Primary Cause:</strong> {analysis['root_cause']}</p>
                    <p style="margin-bottom: 0.5rem;"><strong>Root Asset:</strong> {analysis['root_asset']}</p>
                    <p style="margin-bottom: 0.5rem;"><strong>Confidence Level:</strong> {analysis['confidence'] * 100:.0f}% (High)</p>
                    <p style="margin-bottom: 0;"><strong>Affected Assets:</strong> {analysis['affected_assets']} components</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Causal chain visualization
                st.markdown("#### Causal Chain Sequence")
                
                for idx, step in enumerate(analysis["chain"]):
                    role = step["role"]
                    incident = step["incident"]
                    asset = step["asset"]
                    timestamp = datetime.fromisoformat(step["timestamp"]).strftime("%H:%M:%S")
                    
                    icon = "⚠️ ROOT" if role == "Root Cause" else "🔗 CASCADE"
                    border_class = "incident-card-critical" if idx == 0 else "incident-card-normal"
                    
                    st.markdown(f"""
                    <div class="incident-card {border_class}">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <strong>{icon} Step {idx + 1}: {role}</strong>
                            <span class="badge-info">{timestamp}</span>
                        </div>
                        <div style="color: #94A3B8; margin-bottom: 0.5rem;">{asset}</div>
                        <div>{incident}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Recommendations
                st.markdown("#### Recommended Actions")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info("""
                    **Immediate Actions**
                    - Isolate affected asset
                    - Redirect power flow
                    - Dispatch field crew
                    """)
                
                with col2:
                    st.warning("""
                    **Short-term Response**
                    - Inspect equipment
                    - Run diagnostics
                    - Replace failed components
                    """)
                
                with col3:
                    st.success("""
                    **Long-term Prevention**
                    - Review maintenance schedule
                    - Implement predictive monitoring
                    - Update procedures
                    """)
            else:
                st.success("No active incidents requiring root cause analysis.")
        
        with tab3:
            st.markdown("### Transformer DGA (Dissolved Gas Analysis)")
            
            # Generate DGA for transformers
            transformers = ["T-401", "T-402"]
            
            for transformer_id in transformers:
                dga = st.session_state.simulator.generate_transformer_dga(transformer_id)
                
                # Determine status color
                diagnosis_status = "Normal" if "Normal" in dga.diagnosis else "Fault Detected"
                status_class = "status-online" if "Normal" in dga.diagnosis else "status-error"
                
                with st.expander(f"{transformer_id} - {diagnosis_status}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Gas concentrations chart
                        fig_dga = go.Figure()
                        
                        gases = {
                            "H₂": dga.h2_ppm,
                            "CH₄": dga.ch4_ppm,
                            "C₂H₂": dga.c2h2_ppm,
                            "C₂H₄": dga.c2h4_ppm,
                            "C₂H₆": dga.c2h6_ppm
                        }
                        
                        fig_dga.add_trace(go.Bar(
                            x=list(gases.keys()),
                            y=list(gases.values()),
                            marker_color=['#3B82F6', '#10B981', '#F59E0B', '#DC2626', '#8B5CF6'],
                            text=[f"{v:.1f}" for v in gases.values()],
                            textposition='auto'
                        ))
                        
                        fig_dga.update_layout(
                            title=f"{transformer_id} Gas Concentrations (ppm)",
                            xaxis_title="Gas Type",
                            yaxis_title="Concentration (ppm)",
                            height=300
                        )
                        
                        st.plotly_chart(fig_dga)
                    
                    with col2:
                        confidence_class = "badge-success" if dga.confidence > 0.8 else "badge-warning" if dga.confidence > 0.6 else "badge-error"
                        
                        st.markdown(f"""
                        <div class="content-card">
                            <h4 style="margin-top: 0; color: #F1F5F9;">Diagnosis</h4>
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: #94A3B8;">Result:</strong><br>
                                <span style="color: #F1F5F9;">{dga.diagnosis}</span>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: #94A3B8;">Confidence:</strong><br>
                                <span class="{confidence_class}">{dga.confidence * 100:.0f}%</span>
                            </div>
                            <hr style="border-color: #334155; margin: 1rem 0;">
                            <p style="font-size: 0.8rem; color: #6B7280; margin-bottom: 0;">
                                Analysis based on IEC 60599 standard ratios for transformer fault detection.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

# System Analytics Module
elif selected_module == "System Analytics":
    st.markdown("""
    <div class="page-header">
        <h1>System Analytics & Reports</h1>
        <p>Comprehensive operational metrics and trend analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not SIMULATOR_AVAILABLE:
        st.error("Simulator unavailable.")
    else:
        # Time range selector and export
        col_range, col_export = st.columns([3, 1])
        with col_range:
            time_range = st.selectbox("📊 Time Range", ["Last 7 Days", "Last 30 Days", "Last 90 Days"])
        with col_export:
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("📥 Export Analytics", width="stretch"):
                historical = simulate_historical_incidents(days_back=90)
                export_to_csv(historical, "analytics_report")
        
        st.markdown("### Operational Trends")
        
        days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
        days = days_map[time_range]
        
        historical = simulate_historical_incidents(days_back=days)
        
        # Incidents by severity over time
        df_hist = pd.DataFrame(historical)
        df_hist["timestamp"] = pd.to_datetime(df_hist["timestamp"])
        df_hist["date"] = df_hist["timestamp"].dt.date
        
        # Group by date and severity
        severity_by_date = df_hist.groupby(["date", "severity"]).size().reset_index(name="count")
        
        fig_trend = px.line(
            severity_by_date,
            x="date",
            y="count",
            color="severity",
            title=f"Incident Trends - {time_range}",
            labels={"date": "Date", "count": "Incident Count", "severity": "Severity"},
            color_discrete_map={
                "Low": "#10B981",
                "Medium": "#3B82F6",
                "High": "#F59E0B",
                "Critical": "#DC2626"
            }
        )
        
        fig_trend.update_layout(
            height=400,
            hovermode='x unified',
            dragmode='pan',
            modebar_add=['zoom', 'pan', 'zoomin', 'zoomout', 'autoscale']
        )
        
        st.plotly_chart(fig_trend, config={
            'displayModeBar': True,
            'displaylogo': False,
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'incident_trends',
                'height': 600,
                'width': 1200,
                'scale': 2
            }
        })
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Severity Distribution")
            severity_counts = df_hist["severity"].value_counts()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                marker=dict(colors=["#DC2626", "#F59E0B", "#3B82F6", "#10B981"]),
                textinfo='label+percent',
                hoverinfo='label+value+percent'
            )])
            
            fig_pie.update_layout(
                height=300,
                showlegend=True,
                modebar_add=['toImage']
            )
            st.plotly_chart(fig_pie, config={'displayModeBar': True, 'displaylogo': False})
        
        with col2:
            st.markdown("#### Top Affected Assets")
            asset_counts = df_hist["asset_id"].value_counts().head(5)
            
            fig_assets = go.Figure(data=[go.Bar(
                x=asset_counts.index,
                y=asset_counts.values,
                marker_color="#1E3A8A",
                text=asset_counts.values,
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Incidents: %{y}<extra></extra>'
            )])
            
            fig_assets.update_layout(
                xaxis_title="Asset",
                yaxis_title="Incident Count",
                height=300
            )
            
            st.plotly_chart(fig_assets)
        
        with col3:
            st.markdown("#### Resolution Status")
            status_counts = df_hist["status"].value_counts()
            
            fig_status = go.Figure(data=[go.Bar(
                x=status_counts.index,
                y=status_counts.values,
                marker_color=["#10B981", "#F59E0B", "#3B82F6"]
            )])
            
            fig_status.update_layout(
                xaxis_title="Status",
                yaxis_title="Count",
                height=300
            )
            
            st.plotly_chart(fig_status)
        
        # Detailed incident log
        st.markdown("---")
        st.markdown(f"### Complete Incident Log - {time_range}")
        
        df_display = df_hist[["timestamp", "asset_id", "description", "severity", "status", "duration_minutes", "customers_affected"]]
        df_display.columns = ["Timestamp", "Asset", "Description", "Severity", "Status", "Duration (min)", "Customers Affected"]
        
        st.dataframe(
            df_display.sort_values("Timestamp", ascending=False),
            hide_index=True
        )

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.85rem; padding: 1rem 0;">
    <p><strong>ATLAS AI</strong> - Operational Intelligence Platform v1.0</p>
    <p>MSSE66+ Capstone Project | 330kV/132kV Substation Operations</p>
    <p style="font-size: 0.75rem;">Data Source: Simulated SCADA/EMS | Real-time integration available for production deployment</p>
</div>
""", unsafe_allow_html=True)
