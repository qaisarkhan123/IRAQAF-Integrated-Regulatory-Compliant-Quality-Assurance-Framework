"""
Dashboard Enhancements Integration Module
Integrates alerts, exports, authentication, and domain dashboards into the main app.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DashboardEnhancements:
    """Centralized management of all dashboard enhancements."""
    
    def __init__(self):
        """Initialize all enhancement systems."""
        self.alerts = None
        self.exporter = None
        self.auth_manager = None
        self.initialized = False
    
    def initialize(self):
        """Initialize all enhancement systems."""
        try:
            from alerts import AlertManager
            from exports import ExportManager
            from authentication import AuthenticationManager
            
            self.alerts = AlertManager()
            self.exporter = ExportManager()
            self.auth_manager = AuthenticationManager()
            self.initialized = True
            logger.info("All dashboard enhancements initialized")
        except ImportError as e:
            logger.error(f"Failed to initialize enhancements: {e}")
            self.initialized = False
    
    def setup_streamlit_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="IRAQAF - Compliance Dashboard",
            page_icon="🔐",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        st.markdown("""
        <style>
        /* Alert badges */
        .alert-critical { color: #d62728; }
        .alert-high { color: #ff7f0e; }
        .alert-medium { color: #ffd700; }
        .alert-low { color: #2ca02c; }
        
        /* Dashboard sections */
        .dashboard-section { padding: 15px; border-radius: 8px; }
        
        /* Domain indicators */
        .domain-fda { background-color: #1f77b4; }
        .domain-epa { background-color: #2ca02c; }
        .domain-sec { background-color: #ff7f0e; }
        .domain-iso { background-color: #d62728; }
        .domain-gdpr { background-color: #9467bd; }
        </style>
        """, unsafe_allow_html=True)
    
    def render_sidebar_alerts(self):
        """Render alerts in sidebar."""
        if not self.alerts:
            return
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔔 Recent Alerts")
        
        recent_alerts = self.alerts.get_alerts(hours=24, unread_only=False)[:5]
        
        if recent_alerts:
            for alert in recent_alerts[:5]:
                severity_icon = {
                    "critical": "🚨",
                    "high": "⚠️",
                    "medium": "ℹ️",
                    "low": "📌"
                }.get(alert["severity"], "📢")
                
                read_status = "✓" if alert["read"] else "●"
                st.sidebar.markdown(
                    f"{severity_icon} {alert['title']} {read_status}\n"
                    f"*{alert['domain']}* | {alert['created_at'][:10]}"
                )
                
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("Read", key=f"read_{alert['id']}", help="Mark as read"):
                        self.alerts.mark_as_read(alert["id"])
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"del_{alert['id']}", help="Delete alert"):
                        self.alerts.delete_alert(alert["id"])
                        st.rerun()
        else:
            st.sidebar.info("No recent alerts")
        
        # Alert statistics
        stats = self.alerts.get_stats(hours=24)
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            st.sidebar.metric("Total", stats["total"])
        with col2:
            st.sidebar.metric("Unread", stats["unread"])
        with col3:
            st.sidebar.metric("Critical", stats["critical"])
    
    def render_authentication_ui(self):
        """Render authentication UI and manage session."""
        if "session_id" not in st.session_state:
            from authentication import render_login_form
            
            login_result = render_login_form()
            if login_result:
                username, password = login_result
                success, user = self.auth_manager.authenticate(username, password)
                
                if success:
                    session_id = self.auth_manager.create_session(username)
                    st.session_state.session_id = session_id
                    st.session_state.user = user
                    st.success(f"Welcome, {user.get('display_name', username)}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            return False
        
        return True
    
    def render_user_menu(self):
        """Render user menu in sidebar."""
        if "user" in st.session_state:
            user = st.session_state.user
            st.sidebar.markdown("---")
            st.sidebar.subheader(f"👤 {user.get('display_name', user.get('username', 'User'))}")
            
            role_display = {
                "admin": "👑 Administrator",
                "analyst": "📊 Analyst",
                "viewer": "👁️ Viewer"
            }
            
            st.sidebar.caption(role_display.get(user.get("role", "viewer"), user.get("role")))
            
            if user.get("domain"):
                st.sidebar.caption(f"Domain: {user.get('domain')}")
            
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                if "session_id" in st.session_state:
                    self.auth_manager.end_session(st.session_state.session_id)
                del st.session_state.session_id
                del st.session_state.user
                st.rerun()
    
    def render_admin_panel(self):
        """Render admin control panel for user management."""
        from authentication import User
        
        if "user" not in st.session_state:
            return
        
        user = st.session_state.user
        if user.get("role") != "admin":
            return
        
        with st.sidebar.expander("⚙️ Admin Controls"):
            admin_option = st.radio(
                "Admin Panel",
                ["View Users", "Create User", "Manage Alerts"],
                label_visibility="collapsed"
            )
            
            if admin_option == "View Users":
                st.markdown("### User Management")
                users = self.auth_manager.list_users()
                user_data = []
                for u in users:
                    user_data.append({
                        "Username": u["username"],
                        "Role": u["role"],
                        "Display Name": u.get("display_name", "N/A"),
                        "Active": "✓" if u.get("is_active", False) else "✗",
                        "Created": u.get("created_at", "N/A")[:10]
                    })
                
                import pandas as pd
                st.dataframe(pd.DataFrame(user_data), use_container_width=True)
            
            elif admin_option == "Create User":
                st.markdown("### Create New User")
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")
                new_display_name = st.text_input("Display Name")
                new_role = st.selectbox("Role", list(User.ROLE_DEFINITIONS.keys()))
                new_domain = st.text_input("Domain (optional)")
                
                if st.button("Create User"):
                    success = self.auth_manager.create_user(
                        username=new_username,
                        password=new_password,
                        role=new_role,
                        display_name=new_display_name,
                        domain=new_domain if new_domain else None
                    )
                    if success:
                        st.success(f"User {new_username} created successfully")
                    else:
                        st.error("Failed to create user")
            
            elif admin_option == "Manage Alerts":
                st.markdown("### Alert Management")
                alert_stats = self.alerts.get_stats(hours=0)
                st.metric("Total Alerts", alert_stats["total"])
                
                if st.button("Clear All Alerts"):
                    self.alerts.alerts = []
                    self.alerts._save_alerts()
                    st.success("All alerts cleared")
    
    def create_test_alerts(self):
        """Create sample alerts for testing."""
        if not hasattr(self, '_test_alerts_created'):
            self.alerts.create_alert(
                alert_type="regulatory_change",
                severity="high",
                title="FDA Guidance Update",
                description="New FDA guidance on Quality by Design has been released",
                domain="FDA"
            )
            self.alerts.create_alert(
                alert_type="compliance_issue",
                severity="medium",
                title="Training Compliance Gap",
                description="3 employees have overdue annual compliance training",
                domain="General"
            )
            self.alerts.create_alert(
                alert_type="threshold_breach",
                severity="critical",
                title="Audit Deadline Approaching",
                description="Annual compliance audit is due in 2 days",
                domain="ISO"
            )
            self._test_alerts_created = True


def initialize_dashboard():
    """Initialize all dashboard enhancements."""
    if "enhancements" not in st.session_state:
        enhancements = DashboardEnhancements()
        enhancements.initialize()
        enhancements.setup_streamlit_page()
        st.session_state.enhancements = enhancements
    
    return st.session_state.enhancements


def render_dashboard_header():
    """Render main dashboard header."""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🔐 IRAQAF Compliance Dashboard")
        st.caption("Integrated Regulatory-Compliant Quality Assurance Framework")
    
    with col3:
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")


def render_quick_stats():
    """Render quick statistics cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Compliance Score", "92%", "+2%")
    with col2:
        st.metric("Active Alerts", "3", "1 new")
    with col3:
        st.metric("Audit Ready", "✓", "All domains")
    with col4:
        st.metric("Last Sync", "2 mins ago", "Active")
