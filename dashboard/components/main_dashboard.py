"""
IRAQAF Main Dashboard Component
Core dashboard content and metrics display
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

def render_dashboard_header():
    """Render the main dashboard header with key metrics"""
    st.markdown("""
        <div style="margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; color: #1F2937;">
                🛡️ IRAQAF Dashboard
            </h1>
            <p style="margin: 8px 0 0 0; font-size: 1.1rem; color: #6B7280;">
                Integrated Regulatory Compliance & Quality Assurance Framework
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_quick_metrics():
    """Render quick metrics cards at the top of dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏛️ Compliance Score",
            value="87.5%",
            delta="2.3%",
            help="Overall regulatory compliance across all frameworks"
        )
    
    with col2:
        st.metric(
            label="🔐 Security Index", 
            value="84.1%",
            delta="1.2%",
            help="Privacy and security assessment score"
        )
    
    with col3:
        st.metric(
            label="⚖️ Fairness Index",
            value="92.3%", 
            delta="-0.5%",
            help="Algorithmic fairness and bias assessment"
        )
    
    with col4:
        st.metric(
            label="🔍 Transparency Score",
            value="85.0%",
            delta="3.1%", 
            help="AI explainability and transparency metrics"
        )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_hub_data() -> Dict[str, Any]:
    """Load data from all hubs with caching"""
    import requests
    
    hub_data = {}
    hubs = {
        'l1': 'http://localhost:8504/api/summary',
        'l2': 'http://localhost:8502/api/metrics',
        'l3_fairness': 'http://localhost:8506/api/summary',
        'l4': 'http://localhost:5000/api/explainability-metrics',
        'soqm': 'http://localhost:8503/api/status',
        'uqo': 'http://localhost:8507/api/qa-overview',
        'cae': 'http://localhost:8508/api/internal-cqs'
    }
    
    for hub_name, url in hubs.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                hub_data[hub_name] = response.json()
            else:
                hub_data[hub_name] = {'error': f'HTTP {response.status_code}'}
        except Exception as e:
            hub_data[hub_name] = {'error': str(e)}
    
    return hub_data

def render_hub_overview():
    """Render overview of all hub statuses"""
    st.markdown("### 🎯 Hub Overview")
    
    hub_data = load_hub_data()
    
    # Create columns for hub cards
    col1, col2 = st.columns(2)
    
    hubs_info = [
        ("L1 Regulations & Governance", "l1", "⚖️", "8504"),
        ("L2 Privacy & Security", "l2", "🔐", "8502"),
        ("L3 Fairness & Ethics", "l3_fairness", "⚖️", "8506"),
        ("L4 Explainability & Transparency", "l4", "🔍", "5000"),
        ("SOQM", "soqm", "⚙️", "8503"),
        ("UQO", "uqo", "📊", "8507"),
        ("CAE", "cae", "🤖", "8508")
    ]
    
    for i, (name, key, icon, port) in enumerate(hubs_info):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            data = hub_data.get(key, {})
            has_error = 'error' in data
            
            # Determine status
            if has_error:
                status_color = "🔴"
                status_text = "Offline"
            else:
                status_color = "🟢"
                status_text = "Online"
            
            # Create hub card
            st.markdown(f"""
                <div style="
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                    background: white;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 1.2em; margin-right: 8px;">{icon}</span>
                        <strong>{name}</strong>
                        <span style="margin-left: auto;">{status_color} {status_text}</span>
                    </div>
                    <div style="font-size: 0.9em; color: #6B7280;">
                        Port: {port} | 
                        <a href="http://localhost:{port}" target="_blank">Open Hub</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_system_health():
    """Render system health and performance metrics"""
    st.markdown("### 📊 System Health")
    
    # Create tabs for different health aspects
    health_tabs = st.tabs(["🔄 Performance", "📈 Trends", "⚠️ Alerts"])
    
    with health_tabs[0]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Response Times**")
            # Mock data - replace with actual hub response times
            response_data = pd.DataFrame({
                'Hub': ['L1', 'L2', 'L3F', 'L4', 'SOQM', 'UQO', 'CAE'],
                'Response Time (ms)': [45, 32, 28, 67, 41, 55, 38]
            })
            st.bar_chart(response_data.set_index('Hub'))
        
        with col2:
            st.markdown("**Memory Usage**")
            # Mock memory usage data
            memory_data = pd.DataFrame({
                'Component': ['Dashboard', 'Hubs', 'Database', 'Cache'],
                'Usage (MB)': [156, 423, 89, 67]
            })
            st.bar_chart(memory_data.set_index('Component'))
        
        with col3:
            st.markdown("**Active Connections**")
            st.metric("Current Users", "12", "2")
            st.metric("Hub Connections", "7/7", "0")
            st.metric("API Calls/min", "45", "8")
    
    with health_tabs[1]:
        st.markdown("**7-Day Trends**")
        
        # Generate mock trend data
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Compliance Score': np.random.normal(87, 2, 7),
            'Security Index': np.random.normal(84, 1.5, 7),
            'Fairness Index': np.random.normal(92, 1, 7),
            'Transparency Score': np.random.normal(85, 2.5, 7)
        })
        
        st.line_chart(trend_data.set_index('Date'))
    
    with health_tabs[2]:
        st.markdown("**Recent Alerts**")
        
        # Mock alerts data
        alerts = [
            {"time": "2 hours ago", "level": "⚠️", "message": "L3 Fairness score below threshold (89.2%)"},
            {"time": "5 hours ago", "level": "ℹ️", "message": "Scheduled maintenance completed successfully"},
            {"time": "1 day ago", "level": "🔴", "message": "L2 Security scan detected 3 medium-risk items"},
            {"time": "2 days ago", "level": "✅", "message": "All compliance frameworks updated"}
        ]
        
        for alert in alerts:
            st.markdown(f"""
                <div style="
                    border-left: 3px solid #E5E7EB;
                    padding: 8px 12px;
                    margin: 8px 0;
                    background: #F9FAFB;
                ">
                    <div style="font-size: 0.9em; color: #6B7280;">{alert['time']}</div>
                    <div>{alert['level']} {alert['message']}</div>
                </div>
            """, unsafe_allow_html=True)

def render_search_functionality():
    """Render the global search functionality"""
    st.markdown("---")
    
    # Search section
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input(
            "🔍 Search across all modules",
            placeholder="Search for metrics, clauses, or evidence...",
            key="global_search",
            help="Press Ctrl+K to focus"
        )
    
    with search_col2:
        search_in = st.multiselect(
            "Search in",
            ["Modules", "Evidence", "Clauses", "Metrics"],
            default=["Modules"],
            key="search_scope"
        )
    
    if search_query:
        st.markdown(f"### 🔍 Search Results for '{search_query}'")
        
        results = []
        
        # Load hub data for searching
        hub_data = load_hub_data()
        
        # Search in modules
        if "Modules" in search_in:
            for hub_name, data in hub_data.items():
                if data and 'error' not in data:
                    if search_query.lower() in str(data).lower():
                        results.append({
                            "Type": "Module",
                            "Location": hub_name.replace('_', ' ').title(),
                            "Match": f"Found in {hub_name} data"
                        })
        
        # Search in evidence (placeholder - would need evidence index)
        if "Evidence" in search_in:
            # This would require loading the evidence index
            # For now, show a placeholder
            results.append({
                "Type": "Evidence",
                "Location": "Evidence System",
                "Match": "Evidence search requires evidence index"
            })
        
        # Search in clauses (placeholder)
        if "Clauses" in search_in:
            results.append({
                "Type": "Clauses",
                "Location": "Regulatory Framework",
                "Match": "Clause search requires regulatory data"
            })
        
        # Search in metrics
        if "Metrics" in search_in:
            for hub_name, data in hub_data.items():
                if data and 'error' not in data:
                    # Search in metric names and values
                    for key, value in data.items():
                        if search_query.lower() in key.lower():
                            results.append({
                                "Type": "Metric",
                                "Location": hub_name.replace('_', ' ').title(),
                                "Match": f"{key}: {value}"
                            })
        
        if results:
            import pandas as pd
            st.dataframe(pd.DataFrame(results), width="stretch")
        else:
            st.info("No results found. Try different keywords.")

def check_reports_availability():
    """Check if reports are available and show appropriate message"""
    import glob
    import os
    
    # Check for reports in common locations
    report_paths = [
        "reports/*.json",
        "./reports/*.json", 
        "../reports/*.json"
    ]
    
    reports_found = False
    for pattern in report_paths:
        if glob.glob(pattern):
            reports_found = True
            break
    
    if not reports_found:
        st.info("""
        📭 **No reports found**
        
        Run the CLI to generate JSON reports in ./reports:
        
        ```bash
        python -m cli.iraqaf_cli run --module ALL --config configs/project.example.yaml --out reports
        ```
        
        Or use the hub-specific dashboards available in the sidebar navigation.
        """)
        return False
    return True

def render_main_dashboard():
    """Render the complete main dashboard"""
    # Header
    render_dashboard_header()
    
    # Quick metrics
    render_quick_metrics()
    
    st.markdown("---")
    
    # Create tabs for different dashboard sections
    tab1, tab2, tab3 = st.tabs(["🏠 Hub Overview", "📊 Reports & Analysis", "🔍 Search & Tools"])
    
    with tab1:
        # Hub overview and system health in columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            render_hub_overview()
        
        with col2:
            render_system_health()
    
    with tab2:
        # Reports management section
        try:
            from components.reports_manager import render_reports_manager
            render_reports_manager()
        except ImportError as e:
            st.error(f"Reports manager not available: {e}")
            # Fallback to basic reports check
            check_reports_availability()
    
    with tab3:
        # Search functionality
        render_search_functionality()

def render_welcome_message():
    """Render welcome message for new users"""
    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    
    if st.session_state.first_visit:
        st.info("""
        👋 **Welcome to IRAQAF!** 
        
        This is your central dashboard for AI governance and compliance. 
        Use the sidebar to navigate between specialized hubs, each focusing on different aspects of AI quality assurance.
        
        **Quick Start:**
        1. Check hub status in the overview below
        2. Click any hub button in the sidebar to access detailed assessments
        3. Monitor overall compliance metrics on this dashboard
        """)
        
        if st.button("Got it! Don't show this again"):
            st.session_state.first_visit = False
            st.rerun()
