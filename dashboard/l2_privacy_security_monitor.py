"""
L2 Privacy/Security Monitoring Dashboard
Real-time security and privacy monitoring for frameworks and applications
Uses shared authentication with example_integrated_app.py
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Import shared modules
from authentication import AuthenticationManager
from security_monitor import SecurityMonitor

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="L2 Privacy/Security Monitor",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = AuthenticationManager()

if "security_monitor" not in st.session_state:
    st.session_state.security_monitor = SecurityMonitor()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ============================================================================
# AUTHENTICATION LAYER
# ============================================================================
def show_login():
    """Display login form"""
    st.markdown("# 🔒 L2 Privacy/Security Monitoring")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login to Dashboard")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_login, col_register = st.columns(2)
        
        with col_login:
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                auth_manager = st.session_state.auth_manager
                
                success, user = auth_manager.authenticate(username, password)
                if success:
                    st.session_state.current_user = user
                    st.session_state.logged_in = True
                    st.success(f"✅ Welcome, {user['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Try again.")
        
        with col_register:
            if st.button("📝 Create Account", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
    
    # Display default credentials
    st.markdown("---")
    with st.expander("📖 Default Credentials (Demo)"):
        st.info("""
        **Admin Account:**
        - Username: `admin`
        - Password: `admin_default_123`
        
        **For Testing:**
        You can create new accounts after logging in.
        """)


def show_register():
    """Display registration form"""
    st.markdown("# 🔒 L2 Privacy/Security Monitoring - Register")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Create New Account")
        
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
        new_role = st.selectbox("Role", ["viewer", "analyst", "admin"], key="register_role")
        
        col_create, col_back = st.columns(2)
        
        with col_create:
            if st.button("✅ Create Account", use_container_width=True, type="primary"):
                auth_manager = st.session_state.auth_manager
                
                if auth_manager.create_user(new_username, new_password, new_role):
                    st.success(f"✅ Account created! You can now login.")
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error("❌ Username already exists.")
        
        with col_back:
            if st.button("⬅️ Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()


# ============================================================================
# MAIN DASHBOARD
# ============================================================================
def show_dashboard():
    """Display main security monitoring dashboard"""
    
    auth_manager = st.session_state.auth_manager
    security_monitor = st.session_state.security_monitor
    current_user = st.session_state.current_user
    
    # Sidebar user info
    with st.sidebar:
        st.markdown(f"👤 **{current_user['username']}**")
        st.caption(f"Role: {current_user['role']}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()
        
        st.divider()
    
    # Main header
    st.markdown("# 🔒 L2 Privacy/Security Monitoring Dashboard")
    st.markdown("Real-time security and privacy assessment for frameworks and applications")
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🔍 Run Scan",
        "📋 Scan History",
        "⚠️ Vulnerabilities",
        "📋 Policies"
    ])
    
    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        st.markdown("## Security Summary")
        
        summary = security_monitor.get_security_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Scans",
                summary.get("total_scans", 0),
                delta="0" if summary.get("total_scans", 0) == 0 else "+1"
            )
        
        with col2:
            st.metric(
                "Frameworks Scanned",
                summary.get("frameworks_scanned", 0)
            )
        
        with col3:
            avg_score = summary.get("average_score", 0)
            st.metric(
                "Average Security Score",
                f"{avg_score}/100",
                delta=f"{'🔴 Low' if avg_score < 60 else '🟡 Medium' if avg_score < 80 else '🟢 High'}"
            )
        
        with col4:
            last_scan = summary.get("last_scan", "Never")
            st.metric("Last Scan", last_scan if last_scan != "Never" else "No scans yet")
        
        st.divider()
        
        # Framework statistics
        if summary.get("framework_stats"):
            st.markdown("### Framework Security Status")
            
            framework_data = []
            for fw in summary.get("framework_stats", []):
                framework_data.append({
                    "Framework": fw["framework"],
                    "Score": fw["average_score"],
                    "Scans": fw["total_scans"],
                    "Last Scan": fw["last_scan"]
                })
            
            if framework_data:
                df = pd.DataFrame(framework_data)
                
                # Color code by score
                def score_color(score):
                    if score >= 90:
                        return "🟢 Excellent"
                    elif score >= 75:
                        return "🟡 Good"
                    elif score >= 60:
                        return "🟠 Fair"
                    else:
                        return "🔴 Poor"
                
                df["Status"] = df["Score"].apply(score_color)
                
                st.dataframe(df, use_container_width=True)
                
                # Chart
                fig = px.bar(
                    df,
                    x="Framework",
                    y="Score",
                    color="Score",
                    color_continuous_scale="RdYlGn",
                    range_color=[0, 100],
                    title="Security Score by Framework"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ========== TAB 2: RUN SCAN ==========
    with tab2:
        st.markdown("## Run Security Scan")
        
        # Check user permissions
        if current_user["role"] not in ["analyst", "admin"]:
            st.warning("⚠️ You need analyst or admin role to run scans.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                framework_name = st.text_input(
                    "Framework/Application Name",
                    placeholder="e.g., API Server, Database, Web App"
                )
                scan_type = st.selectbox("Scan Type", ["full", "partial", "quick"])
            
            with col2:
                st.empty()
                st.empty()
            
            if st.button("🔍 Start Scan", use_container_width=True, type="primary"):
                if not framework_name:
                    st.error("Please enter a framework name.")
                else:
                    with st.spinner(f"Scanning {framework_name}..."):
                        scan = security_monitor.start_scan(framework_name, scan_type)
                        
                        st.success(f"✅ Scan completed: {scan.scan_id}")
                        
                        # Display results
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Overall Score", f"{scan.overall_score}/100")
                        
                        with col2:
                            status = "🟢 Pass" if scan.overall_score >= 80 else "🟡 Warning" if scan.overall_score >= 60 else "🔴 Fail"
                            st.metric("Status", status)
                        
                        with col3:
                            st.metric("Issues Found", len(scan.recommendations))
                        
                        st.divider()
                        
                        # Detailed results
                        st.markdown("### Scan Results")
                        
                        for category, result in scan.results.items():
                            with st.expander(f"{category.replace('_', ' ').title()} - {result.get('score', 0)}/100"):
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    status_badge = "✅" if result.get("status") == "passed" else "⚠️" if result.get("status") == "warning" else "❌"
                                    st.markdown(f"**Status:** {status_badge} {result.get('status').upper()}")
                                    st.markdown(f"**Score:** {result.get('score')}/100")
                                
                                with col2:
                                    st.markdown("**Details:**")
                                    details = result.get("details", {})
                                    for key, value in details.items():
                                        st.caption(f"• {key}: {value}")
    
    # ========== TAB 3: SCAN HISTORY ==========
    with tab3:
        st.markdown("## Scan History")
        
        recent_scans = security_monitor.get_recent_scans(limit=20)
        
        if not recent_scans:
            st.info("No scans yet. Run your first scan in the 'Run Scan' tab.")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                selected_framework = st.selectbox(
                    "Filter by Framework",
                    ["All"] + list(set(s["framework"] for s in recent_scans))
                )
            
            with col2:
                score_threshold = st.slider("Score Threshold", 0, 100, 0)
            
            # Filter scans
            filtered_scans = recent_scans
            if selected_framework != "All":
                filtered_scans = [s for s in filtered_scans if s["framework"] == selected_framework]
            
            filtered_scans = [s for s in filtered_scans if s.get("overall_score", 0) >= score_threshold]
            
            # Display scans
            for scan in filtered_scans:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{scan['framework']}**")
                        st.caption(f"ID: {scan['scan_id']}")
                    
                    with col2:
                        score = scan.get("overall_score", 0)
                        st.metric("Score", f"{score}/100")
                    
                    with col3:
                        st.metric("Type", scan.get("scan_type", "unknown"))
                    
                    with col4:
                        timestamp = scan.get("timestamp", "Unknown")
                        st.caption(timestamp)
                    
                    if st.button("📄 View Report", key=f"report_{scan['scan_id']}"):
                        report = security_monitor.generate_report(scan["scan_id"])
                        if report:
                            st.json(report)
    
    # ========== TAB 4: VULNERABILITIES ==========
    with tab4:
        st.markdown("## Known Vulnerabilities")
        
        vulnerabilities = security_monitor.vulnerabilities.get("vulnerabilities", [])
        
        if not vulnerabilities:
            st.info("No vulnerabilities recorded.")
        else:
            # Filter by severity
            severity_filter = st.multiselect(
                "Filter by Severity",
                ["critical", "high", "medium", "low"],
                default=["critical", "high"]
            )
            
            filtered_vulns = [v for v in vulnerabilities if v.get("severity") in severity_filter]
            
            for vuln in filtered_vulns:
                severity = vuln.get("severity", "unknown").upper()
                
                if severity == "CRITICAL":
                    color = "🔴"
                elif severity == "HIGH":
                    color = "🟠"
                elif severity == "MEDIUM":
                    color = "🟡"
                else:
                    color = "🔵"
                
                with st.container(border=True):
                    st.markdown(f"{color} **{severity}** - {vuln.get('framework', 'Unknown')}")
                    st.markdown(f"**Description:** {vuln.get('description', 'N/A')}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"CVE: {vuln.get('cve', 'N/A')}")
                    with col2:
                        st.caption(f"Discovered: {vuln.get('discovered_date', 'N/A')[:10]}")
                    with col3:
                        st.caption(f"Status: {vuln.get('status', 'open')}")
    
    # ========== TAB 5: POLICIES ==========
    with tab5:
        st.markdown("## Security Policies & Frameworks")
        
        # Get all policies
        all_policies = security_monitor.get_policies()
        
        if not all_policies:
            st.info("No policies configured.")
        else:
            # Filter by category
            categories = list(set(p.get("category", "general") for p in all_policies))
            selected_category = st.selectbox("Filter by Category", ["All"] + categories)
            
            displayed_policies = all_policies
            if selected_category != "All":
                displayed_policies = [p for p in all_policies if p.get("category") == selected_category]
            
            # Display policies
            for policy in displayed_policies:
                with st.expander(f"📋 {policy.get('name', 'Unknown Policy')}"):
                    st.markdown(f"**ID:** {policy.get('id')}")
                    st.markdown(f"**Category:** {policy.get('category', 'N/A')}")
                    st.markdown("**Requirements:**")
                    for req in policy.get("requirements", []):
                        st.markdown(f"- {req}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Main application flow"""
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        if st.session_state.get("show_register", False):
            show_register()
        else:
            show_login()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
