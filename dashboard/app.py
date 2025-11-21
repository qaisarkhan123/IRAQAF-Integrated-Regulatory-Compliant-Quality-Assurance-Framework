"""
IRAQAF Dashboard - Enhanced Modular Version
Preserves all original functionality while improving structure and performance
"""

import streamlit as st
import logging
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="IRAQAF Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def setup_paths():
    """Setup project paths for imports"""
    try:
        # Get current file directory
        current_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
        
        # Find project root (directory containing dashboard/)
        project_root = current_dir.parent if current_dir.name == 'dashboard' else current_dir
        
        # Add paths to sys.path if not already there
        paths_to_add = [str(project_root), str(current_dir)]
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        return project_root, current_dir
    except Exception as e:
        logger.error(f"Path setup failed: {e}")
        return Path.cwd(), Path.cwd()

def check_dependencies():
    """Check if required modules are available"""
    dependencies = {}
    
    # Authentication - Try enhanced version first
    try:
        from auth_ui_enhanced import check_enhanced_authentication
        dependencies['auth'] = True
        dependencies['auth_enhanced'] = True
    except ImportError:
        try:
            from auth_ui import check_authentication
            dependencies['auth'] = True
            dependencies['auth_enhanced'] = False
        except ImportError:
            dependencies['auth'] = False
            dependencies['auth_enhanced'] = False
            logger.warning("Authentication module not available")
    
    # UX Enhancements
    try:
        from ux_enhancements import initialize_ux_enhancements
        dependencies['ux'] = True
    except ImportError:
        dependencies['ux'] = False
        logger.warning("UX enhancements module not available")
    
    # CSS Loader
    try:
        from css_loader import load_main_styles
        dependencies['css'] = True
    except ImportError:
        dependencies['css'] = False
        logger.warning("CSS loader not available")
    
    return dependencies

def initialize_app():
    """Initialize the application"""
    # Setup paths first
    project_root, dashboard_dir = setup_paths()
    
    # Check dependencies
    deps = check_dependencies()
    
    # Initialize UX enhancements if available
    if deps['ux']:
        try:
            from ux_enhancements import initialize_ux_enhancements
            initialize_ux_enhancements()
        except Exception as e:
            logger.error(f"Failed to initialize UX enhancements: {e}")
    
    return deps, project_root, dashboard_dir

def handle_authentication(deps):
    """Handle user authentication"""
    if deps['auth']:
        try:
            # Use enhanced authentication if available
            if deps.get('auth_enhanced', False):
                from auth_ui_enhanced import check_enhanced_authentication
                if not check_enhanced_authentication():
                    st.stop()
            else:
                from auth_ui import check_authentication
                if not check_authentication():
                    st.stop()
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            logger.error(f"Authentication failed: {e}")
            st.stop()
    else:
        # Show warning if auth is not available in development
        if st.session_state.get('show_dev_warning', True):
            st.warning("⚠️ Authentication module not loaded. Running in development mode.")
            if st.button("Hide this warning"):
                st.session_state.show_dev_warning = False
                st.rerun()

def render_sidebar(deps):
    """Render the sidebar with navigation and user info"""
    with st.sidebar:
        # Load CSS if available
        if deps['css']:
            try:
                from css_loader import load_main_styles
                load_main_styles()
            except Exception as e:
                logger.error(f"Failed to load CSS: {e}")
        
        # Enhanced Premium Header with Modern Design
        st.markdown("""
            <div class="sidebar-container">
                <div class="header-card">
                    <h2>🛡️ IRAQAF</h2>
                    <p>Integrated Regulatory Compliance Framework</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # User Section
        if deps['auth']:
            try:
                # Use enhanced user info if available
                if deps.get('auth_enhanced', False):
                    from auth_ui_enhanced import render_enhanced_user_info
                    render_enhanced_user_info()
                else:
                    from auth_ui import render_user_info
                    render_user_info()
                st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
            except ImportError:
                pass
        
        # Hub Navigation Section
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
        
        # Session Info
        if deps['ux']:
            try:
                from ux_enhancements import render_session_info
                render_session_info()
            except ImportError:
                pass

def render_main_content():
    """Render the main dashboard content"""
    
    # Dashboard Header
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
    
    # Welcome message for new users
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
        4. Use the Reports & Analysis tab to view detailed module reports
        """)
        
        if st.button("Got it! Don't show this again"):
            st.session_state.first_visit = False
            st.rerun()
    
    # Quick metrics
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
    
    st.markdown("---")
    
    # Create tabs for different dashboard sections
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Hub Overview", "📊 Reports & Analysis", "🔍 Search & Tools", "⚙️ System Health"])
    
    with tab1:
        render_hub_overview_tab()
    
    with tab2:
        render_reports_tab()
    
    with tab3:
        render_search_tab()
    
    with tab4:
        render_system_health_tab()

def render_hub_overview_tab():
    """Render the hub overview tab"""
    st.markdown("### 🎯 Hub Status Overview")
    
    # Hub status cards
    hubs_info = [
        ("L1 Regulations & Governance", "8504", "⚖️"),
        ("L2 Privacy & Security", "8502", "🔐"),
        ("L3 Fairness & Ethics", "8506", "⚖️"),
        ("L4 Explainability & Transparency", "5000", "🔍"),
        ("SOQM", "8503", "⚙️"),
        ("UQO", "8507", "📊"),
        ("CAE", "8508", "🤖")
    ]
    
    col1, col2 = st.columns(2)
    
    for i, (name, port, icon) in enumerate(hubs_info):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            # Check hub status
            try:
                import requests
                # Try /health first, then fallback to root /
                try:
                    response = requests.get(f"http://localhost:{port}/health", timeout=5)
                except:
                    response = requests.get(f"http://localhost:{port}/", timeout=5)
                
                online = response.status_code == 200
                response_time = response.elapsed.total_seconds() * 1000
            except:
                online = False
                response_time = None
            
            status_color = "🟢" if online else "🔴"
            status_text = "Online" if online else "Offline"
            
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
                        {f" | Response: {response_time:.0f}ms" if response_time else ""}
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_reports_tab():
    """Render the reports and analysis tab"""
    try:
        from components.reports_manager import render_reports_manager
        render_reports_manager()
    except ImportError as e:
        st.error(f"Reports manager not available: {e}")
        
        # Fallback basic reports functionality
        st.markdown("### 📊 Reports Overview")
        
        import glob
        report_files = glob.glob("reports/*.json") + glob.glob("./reports/*.json")
        
        if not report_files:
            st.info("""
            📭 **No reports found**
            
            Run the CLI to generate JSON reports in ./reports:
            
            ```bash
            python -m cli.iraqaf_cli run --module ALL --config configs/project.example.yaml --out reports
            ```
            
            Or use the hub-specific dashboards available in the sidebar navigation.
            """)
        else:
            st.success(f"Found {len(report_files)} report files")
            
            # Show report files
            for report_file in report_files[:10]:  # Show first 10
                st.markdown(f"- `{os.path.basename(report_file)}`")
            
            if len(report_files) > 10:
                st.markdown(f"... and {len(report_files) - 10} more files")

def render_search_tab():
    """Render the search and tools tab"""
    st.markdown("### 🔍 Global Search")
    
    # Search interface
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
            ["Modules", "Evidence", "Hubs", "Reports"],
            default=["Modules"],
            key="search_scope"
        )
    
    if search_query:
        st.markdown(f"### 🔍 Search Results for '{search_query}'")
        
        results = []
        
        # Search in hubs
        if "Hubs" in search_in:
            hub_names = [
                "L1 Regulations & Governance",
                "L2 Privacy & Security", 
                "L3 Fairness & Ethics",
                "L4 Explainability & Transparency",
                "SOQM",
                "UQO", 
                "CAE"
            ]
            
            for hub_name in hub_names:
                if search_query.lower() in hub_name.lower():
                    results.append({
                        "Type": "Hub",
                        "Location": hub_name,
                        "Match": f"Hub name contains '{search_query}'"
                    })
        
        if results:
            import pandas as pd
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("No results found. Try different keywords or check the Reports tab for detailed analysis.")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Data", help="Clear cache and reload"):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with col2:
        if st.button("📊 Hub Status", help="Check all hub status"):
            st.info("Hub status shown in Hub Overview tab")
    
    with col3:
        if st.button("🧭 Navigation Help", help="Show navigation tips"):
            st.info("""
            **Quick Navigation:**
            - L1: Governance & Regulations
            - L2: Privacy & Security  
            - L3: Fairness & Ethics
            - L4: Explainability & Transparency
            - SOQM: System Operations
            - UQO: Unified QA Orchestrator
            - CAE: Continuous Assurance Engine
            """)
    
    with col4:
        if st.button("📖 Documentation", help="Open documentation"):
            st.markdown("[📖 View Comprehensive Guide](./IRAQAF_HUBS_COMPREHENSIVE_GUIDE.md)")

def render_system_health_tab():
    """Render the system health tab"""
    st.markdown("### 📊 System Health & Performance")
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Hub Response Times**")
        # Mock data for demonstration
        import pandas as pd
        import numpy as np
        
        response_data = pd.DataFrame({
            'Hub': ['L1', 'L2', 'L3F', 'L4', 'SOQM', 'UQO', 'CAE'],
            'Response Time (ms)': np.random.randint(20, 100, 7)
        })
        st.bar_chart(response_data.set_index('Hub'))
    
    with col2:
        st.markdown("**System Resources**")
        resource_data = pd.DataFrame({
            'Component': ['CPU', 'Memory', 'Disk', 'Network'],
            'Usage (%)': np.random.randint(10, 80, 4)
        })
        st.bar_chart(resource_data.set_index('Component'))
    
    with col3:
        st.markdown("**Active Connections**")
        st.metric("Current Users", "12", "2")
        st.metric("Hub Connections", "7/7", "0")
        st.metric("API Calls/min", "45", "8")
    
    st.markdown("---")
    
    # Recent Activity
    st.markdown("### 📈 Recent Activity")
    
    activities = [
        {"time": "2 min ago", "level": "ℹ️", "message": "L4 Hub: Transparency score updated (85.2%)"},
        {"time": "5 min ago", "level": "✅", "message": "L2 Hub: Security scan completed successfully"},
        {"time": "12 min ago", "level": "⚠️", "message": "L3 Fairness: Score below threshold (89.1%)"},
        {"time": "1 hour ago", "level": "🔄", "message": "System: Automatic cache refresh completed"}
    ]
    
    for activity in activities:
        st.markdown(f"""
            <div style="
                border-left: 3px solid #E5E7EB;
                padding: 8px 12px;
                margin: 8px 0;
                background: #F9FAFB;
            ">
                <div style="font-size: 0.9em; color: #6B7280;">{activity['time']}</div>
                <div>{activity['level']} {activity['message']}</div>
            </div>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    try:
        # Initialize application
        deps, project_root, dashboard_dir = initialize_app()
        
        # Handle authentication
        handle_authentication(deps)
        
        # Render sidebar
        render_sidebar(deps)
        
        # Render main content
        render_main_content()
        
    except Exception as e:
        st.error("An unexpected error occurred. Please check the logs.")
        logger.error(f"Application error: {e}", exc_info=True)
        
        # Show basic fallback interface
        st.title("🛡️ IRAQAF Dashboard")
        st.error("Dashboard components are not fully available. Please check the installation.")
        
        # Basic hub links
        st.markdown("### Hub Access")
        hubs = [
            ("L1 Regulations & Governance", "8504"),
            ("L2 Privacy & Security", "8502"),
            ("L3 Fairness & Ethics", "8506"),
            ("L4 Explainability & Transparency", "5000"),
            ("SOQM", "8503"),
            ("UQO", "8507"),
            ("CAE", "8508")
        ]
        
        for name, port in hubs:
            st.markdown(f"- [{name}](http://localhost:{port})")

# Run the application
if __name__ == "__main__":
    main()
else:
    # When imported as module, run main automatically
    main()