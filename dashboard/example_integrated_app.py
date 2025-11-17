"""
EXAMPLE: How to integrate dashboard enhancements into your Streamlit app.
This file demonstrates all features and usage patterns.
"""

import streamlit as st
from pathlib import Path
import sys

# Add dashboard to path
sys.path.insert(0, str(Path(__file__).parent))

from alerts import AlertManager
from exports import ExportManager
from authentication import AuthenticationManager, check_authentication, require_permission
from domain_dashboards import DomainDashboard, render_domain_selector, display_all_domains_overview
from enhancements import (
    DashboardEnhancements,
    initialize_dashboard,
    render_dashboard_header,
    render_quick_stats
)
import pandas as pd


def main():
    """Main application with all enhancements integrated."""
    
    # Initialize enhancements
    enhancements = initialize_dashboard()
    
    # Authentication check
    if not enhancements.render_authentication_ui():
        st.stop()
    
    # User menu and admin panel
    enhancements.render_user_menu()
    enhancements.render_admin_panel()
    
    # Sidebar alerts
    enhancements.render_sidebar_alerts()
    
    # Main content
    render_dashboard_header()
    render_quick_stats()
    
    st.markdown("---")
    
    # Main navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "🌐 Domains",
        "📊 Analytics",
        "💾 Export",
        "🔔 Alerts"
    ])
    
    with tab1:
        render_main_dashboard()
    
    with tab2:
        render_domain_dashboards()
    
    with tab3:
        render_analytics()
    
    with tab4:
        render_export_center()
    
    with tab5:
        render_alerts_management()


def render_main_dashboard():
    """Render main compliance dashboard."""
    st.subheader("📊 Compliance Overview")
    
    # Create sample data
    sample_data = pd.DataFrame({
        "Domain": ["FDA", "EPA", "SEC", "ISO", "GDPR"],
        "Compliance Score": [92, 88, 95, 85, 90],
        "Status": ["✓", "⚠️", "✓", "⚠️", "✓"],
        "Last Audit": ["2024-10-15", "2024-09-20", "2024-11-01", "2024-10-30", "2024-11-05"]
    })
    
    st.dataframe(sample_data, use_container_width=True, hide_index=True)
    
    # System health
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("System Health", "Good", "100%")
    with col2:
        st.metric("Last Sync", "1 min ago", "Active")
    with col3:
        st.metric("Avg Response Time", "245ms", "-15ms")


def render_domain_dashboards():
    """Render domain-specific dashboards."""
    st.subheader("🌐 Regulatory Domains")
    
    # Domain overview
    display_all_domains_overview()
    
    st.markdown("---")
    
    # Detailed domain view
    selected_domain = render_domain_selector()
    if selected_domain:
        dashboard = DomainDashboard(selected_domain)
        
        st.subheader(f"{dashboard.domain.get_icon()} {dashboard.domain.get_name()}")
        
        # Create tabs for domain content
        dom_tab1, dom_tab2, dom_tab3, dom_tab4 = st.tabs([
            "Overview",
            "Regulations",
            "Metrics",
            "Audit Status"
        ])
        
        with dom_tab1:
            dashboard.display_domain_overview()
            dashboard.display_compliance_timeline()
        
        with dom_tab2:
            dashboard.display_regulations()
        
        with dom_tab3:
            dashboard.display_metrics()
        
        with dom_tab4:
            dashboard.display_audit_readiness()
            dashboard.display_recent_findings()


def render_analytics():
    """Render analytics and insights."""
    st.subheader("📈 Analytics & Insights")
    
    # Sample analytics data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    compliance_scores = [85, 87, 89, 91, 90, 92]
    
    chart_data = pd.DataFrame({
        "Month": months,
        "Compliance Score": compliance_scores
    })
    
    st.line_chart(chart_data.set_index("Month"), use_container_width=True)
    
    # Finding trends
    st.subheader("Audit Findings Trend")
    findings_data = pd.DataFrame({
        "Month": months,
        "Critical": [2, 1, 1, 0, 0, 0],
        "High": [5, 4, 3, 2, 2, 1],
        "Medium": [8, 7, 6, 5, 4, 3],
        "Low": [12, 11, 10, 8, 7, 6]
    })
    
    st.bar_chart(findings_data.set_index("Month"), use_container_width=True)


def render_export_center():
    """Render data export center."""
    st.subheader("💾 Export Center")
    
    if not require_permission("export_data"):
        st.warning("You don't have permission to export data")
        return
    
    # Create sample data for export
    sample_data = pd.DataFrame({
        "Compliance Domain": ["FDA", "EPA", "SEC", "ISO", "GDPR"],
        "Score": [92, 88, 95, 85, 90],
        "Last Updated": ["2024-11-15", "2024-11-14", "2024-11-15", "2024-11-13", "2024-11-15"],
        "Status": ["Compliant", "At Risk", "Compliant", "At Risk", "Compliant"]
    })
    
    # Export options
    export_type = st.radio(
        "Select Export Format",
        ["CSV", "Excel", "PDF Report"],
        horizontal=True
    )
    
    if export_type == "CSV":
        st.subheader("Export as CSV")
        exporter = ExportManager()
        exporter.create_streamlit_download_buttons(
            data=sample_data,
            filename_base="compliance_report"
        )
    
    elif export_type == "Excel":
        st.subheader("Export as Excel")
        exporter = ExportManager()
        excel_data = {
            "Compliance Summary": sample_data,
            "Metrics": pd.DataFrame({
                "Metric": ["Avg Score", "Domains", "Critical Issues", "Last Sync"],
                "Value": [90, 5, 1, "Active"]
            })
        }
        excel_bytes = exporter.export_to_excel(excel_data)
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_bytes,
            file_name="compliance_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    elif export_type == "PDF Report":
        st.subheader("Generate PDF Report")
        exporter = ExportManager()
        
        sections = [
            {
                "heading": "Executive Summary",
                "content": "This report summarizes compliance across all regulatory domains."
            },
            {
                "heading": "Compliance Scores by Domain",
                "content": sample_data
            },
            {
                "heading": "Key Metrics",
                "content": "Overall compliance average: 90%\nDomains assessed: 5\nCritical issues: 1\nStatus: Active monitoring"
            }
        ]
        
        exporter.create_pdf_download_button(
            title="Compliance Report",
            executive_summary="Comprehensive compliance assessment across all regulatory domains",
            sections=sections,
            filename_base="compliance_report"
        )


def render_alerts_management():
    """Render alert management interface."""
    st.subheader("🔔 Alert Management")
    
    if not require_permission("create_alerts"):
        st.warning("You don't have permission to manage alerts")
        return
    
    alerts = AlertManager()
    
    # Create new alert
    st.subheader("Create New Alert")
    
    col1, col2 = st.columns(2)
    with col1:
        alert_type = st.selectbox(
            "Alert Type",
            ["regulatory_change", "compliance_issue", "threshold_breach", "audit_event"]
        )
        severity = st.selectbox(
            "Severity",
            ["critical", "high", "medium", "low"]
        )
    
    with col2:
        domain = st.selectbox(
            "Domain",
            ["FDA", "EPA", "SEC", "ISO", "GDPR", "General"]
        )
    
    alert_title = st.text_input("Alert Title")
    alert_desc = st.text_area("Alert Description", height=100)
    
    if st.button("Create Alert", use_container_width=True):
        alert_id = alerts.create_alert(
            alert_type=alert_type,
            severity=severity,
            title=alert_title,
            description=alert_desc,
            domain=domain
        )
        st.success(f"Alert created: {alert_id}")
        st.rerun()
    
    st.markdown("---")
    
    # View alerts
    st.subheader("Recent Alerts")
    
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_domain = st.multiselect(
            "Filter by Domain",
            ["FDA", "EPA", "SEC", "ISO", "GDPR", "General"],
            default=["General"]
        )
    
    with filter_col2:
        filter_severity = st.multiselect(
            "Filter by Severity",
            ["critical", "high", "medium", "low"]
        )
    
    # Get filtered alerts
    all_alerts = alerts.get_alerts(hours=0)
    filtered = [
        a for a in all_alerts
        if (not filter_domain or a["domain"] in filter_domain) and
           (not filter_severity or a["severity"] in filter_severity)
    ]
    
    if filtered:
        for alert in filtered:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    severity_icon = {
                        "critical": "🚨",
                        "high": "⚠️",
                        "medium": "ℹ️",
                        "low": "📌"
                    }.get(alert["severity"], "📢")
                    
                    st.markdown(f"### {severity_icon} {alert['title']}")
                    st.markdown(f"**Domain:** {alert['domain']} | **Type:** {alert['type']}")
                    st.markdown(f"**Description:** {alert['description']}")
                    st.caption(f"Created: {alert['created_at']}")
                
                with col2:
                    if st.button("✓ Read", key=f"read_{alert['id']}"):
                        alerts.mark_as_read(alert["id"])
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"del_{alert['id']}"):
                        alerts.delete_alert(alert["id"])
                        st.rerun()
    else:
        st.info("No alerts match the selected filters")


if __name__ == "__main__":
    main()
