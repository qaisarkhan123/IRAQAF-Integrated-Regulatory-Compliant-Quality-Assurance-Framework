"""
IRAQAF Dashboard Sidebar Component
Handles hub navigation, user info, and sidebar controls
"""

import streamlit as st
from typing import Optional

def render_sidebar_header():
    """Render the main IRAQAF header in sidebar"""
    st.markdown("""
        <div class="sidebar-container">
            <div class="header-card">
                <h2>🛡️ IRAQAF</h2>
                <p>Integrated Regulatory Compliance Framework</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_hub_navigation():
    """Render the hub navigation buttons"""
    st.markdown("""
        <div class="section-title">
            <span>🚀 HUB NAVIGATION</span>
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <!-- 1. L1 – Regulations & Governance Hub -->
            <a href="http://localhost:8504" target="_blank" class="hub-button l1">
                <span class="hub-button-icon">⚖️</span>
                <span class="hub-button-text">L1 Regulations & Governance</span>
                <span class="hub-button-arrow">→</span>
            </a>
            <!-- 2. L2 – Privacy & Security Hub -->
            <a href="http://localhost:8502" target="_blank" class="hub-button l2">
                <span class="hub-button-icon">🔐</span>
                <span class="hub-button-text">L2 Privacy & Security</span>
                <span class="hub-button-arrow">→</span>
            </a>
            <!-- 3. L3 – Fairness & Ethics Hub -->
            <a href="http://localhost:8506" target="_blank" class="hub-button l3-fairness">
                <span class="hub-button-icon">⚖️</span>
                <span class="hub-button-text">L3 Fairness & Ethics</span>
                <span class="hub-button-arrow">→</span>
            </a>
            <!-- 4. L4 – Explainability & Transparency Hub -->
            <a href="http://localhost:5000" target="_blank" class="hub-button l4">
                <span class="hub-button-icon">🔍</span>
                <span class="hub-button-text">L4 Explainability & Transparency</span>
                <span class="hub-button-arrow">→</span>
            </a>
            <!-- 5. System Operations & QA Monitor (SOQM) -->
            <a href="http://localhost:8503" target="_blank" class="hub-button l3">
                <span class="hub-button-icon">⚙️</span>
                <span class="hub-button-text">System Operations & QA Monitor (SOQM)</span>
                <span class="hub-button-arrow">→</span>
            </a>
            <!-- 6. Unified QA Orchestrator (UQO) -->
            <a href="http://localhost:8507" target="_blank" class="hub-button m5-hub">
                <span class="hub-button-icon">📊</span>
                <span class="hub-button-text">Unified QA Orchestrator<br><small style="font-size: 11px; opacity: 0.8;">(UQO)</small></span>
                <span class="hub-button-arrow">→</span>
            </a>
            <!-- 7. Continuous Assurance Engine (CAE) -->
            <a href="http://localhost:8508" target="_blank" class="hub-button m5-core">
                <span class="hub-button-icon">🤖</span>
                <span class="hub-button-text">Continuous Assurance Engine<br><small style="font-size: 11px; opacity: 0.8;">(CAE)</small></span>
                <span class="hub-button-arrow">→</span>
            </a>
        </div>
        
        <div class="tip-box">
            💡 <b>Quick Tip:</b> Click any hub to access specialized assessment tools in a new tab
        </div>
    """, unsafe_allow_html=True)

def render_sidebar(auth_available: bool = False, ux_available: bool = False):
    """
    Render the complete sidebar with all components
    
    Args:
        auth_available: Whether authentication UI is available
        ux_available: Whether UX enhancements are available
    """
    with st.sidebar:
        # Load CSS styles
        try:
            from css_loader import load_main_styles
            load_main_styles()
        except ImportError:
            pass
        
        # Header
        render_sidebar_header()
        
        # User Section
        if auth_available:
            try:
                from auth_ui import render_user_info
                render_user_info()
                st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
            except ImportError:
                pass
        
        # Hub Navigation
        render_hub_navigation()
        
        # Session Info
        if ux_available:
            try:
                from ux_enhancements import render_session_info
                render_session_info()
            except ImportError:
                pass

def get_hub_status() -> dict:
    """
    Check the status of all hubs
    
    Returns:
        Dictionary with hub status information
    """
    import requests
    
    hubs = {
        'L1 Regulations': 'http://localhost:8504/health',
        'L2 Privacy & Security': 'http://localhost:8502/health', 
        'L3 Fairness & Ethics': 'http://localhost:8506/health',
        'L4 Explainability': 'http://localhost:5000/health',
        'SOQM': 'http://localhost:8503/health',
        'UQO': 'http://localhost:8507/health',
        'CAE': 'http://localhost:8508/health'
    }
    
    status = {}
    for name, url in hubs.items():
        try:
            response = requests.get(url, timeout=2)
            status[name] = {
                'online': response.status_code == 200,
                'response_time': response.elapsed.total_seconds() * 1000
            }
        except:
            status[name] = {
                'online': False,
                'response_time': None
            }
    
    return status

def render_hub_status_indicator():
    """Render a compact hub status indicator in sidebar"""
    status = get_hub_status()
    online_count = sum(1 for hub in status.values() if hub['online'])
    total_count = len(status)
    
    if online_count == total_count:
        color = "🟢"
        text = f"All {total_count} hubs online"
    elif online_count > 0:
        color = "🟡" 
        text = f"{online_count}/{total_count} hubs online"
    else:
        color = "🔴"
        text = "No hubs online"
    
    st.markdown(f"""
        <div style="
            background: rgba(0,0,0,0.1); 
            padding: 8px 12px; 
            border-radius: 6px; 
            margin: 10px 0;
            font-size: 12px;
        ">
            {color} {text}
        </div>
    """, unsafe_allow_html=True)
