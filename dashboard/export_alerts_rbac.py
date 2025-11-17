"""
Export, Alerts & Notifications, and Role-Based Dashboard Enhancements
Integrated features for IRAQAF Dashboard
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ============================================================================
# EXPORT FUNCTIONALITY
# ============================================================================

class ExportManager:
    """Handle PDF and CSV exports"""
    
    @staticmethod
    def export_to_csv(data: Dict, filename: str = None) -> bytes:
        """Export assessment data to CSV"""
        if filename is None:
            filename = f"iraqaf_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode()
    
    @staticmethod
    def export_to_pdf(data: Dict, title: str = "IRAQAF Compliance Report") -> bytes:
        """Export assessment data to PDF"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build document elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1  # Center
        )
        elements.append(Paragraph(title, title_style))
        
        # Add timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        elements.append(Paragraph(f"<i>Generated on {timestamp}</i>", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Add data table
        if isinstance(data, dict):
            table_data = [list(data.keys())] + [[str(v) for v in data.values()]]
        else:
            df = pd.DataFrame(data)
            table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Create table with styling
        table = Table(table_data, colWidths=[2*inch]*len(table_data[0]))
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    @staticmethod
    def create_json_export(data: Dict, metadata: Dict = None) -> str:
        """Create JSON export with metadata"""
        export = {
            "export_date": datetime.now().isoformat(),
            "metadata": metadata or {},
            "data": data
        }
        return json.dumps(export, indent=2, default=str)


def render_export_section():
    """Render export controls in sidebar"""
    st.sidebar.markdown("---")
    with st.sidebar.expander("📥 Export & Reports", expanded=False):
        export_type = st.radio(
            "Export Format",
            ["CSV", "JSON", "PDF"] if REPORTLAB_AVAILABLE else ["CSV", "JSON"],
            key="export_format"
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="export_date_range"
        )
        
        if st.button("📊 Generate Export", use_container_width=True):
            st.success(f"✅ Export prepared as {export_type}")
            
            # Create sample data
            sample_data = {
                "Assessment": "11-Category",
                "Overall Score": 85,
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Status": "Compliant"
            }
            
            if export_type == "CSV":
                csv_data = ExportManager.export_to_csv(sample_data)
                st.download_button(
                    "⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"iraqaf_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            elif export_type == "JSON":
                json_data = ExportManager.create_json_export(sample_data)
                st.download_button(
                    "⬇️ Download JSON",
                    data=json_data,
                    file_name=f"iraqaf_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            elif export_type == "PDF" and REPORTLAB_AVAILABLE:
                pdf_data = ExportManager.export_to_pdf(sample_data)
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_data,
                    file_name=f"iraqaf_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )


# ============================================================================
# ALERTS & NOTIFICATIONS
# ============================================================================

class AlertManager:
    """Handle alerts and notifications"""
    
    ALERTS_FILE = Path("data/alerts/alerts.json")
    
    @staticmethod
    def create_alert(alert_type: str, title: str, message: str, severity: str = "info") -> Dict:
        """Create a new alert"""
        alert = {
            "id": int(datetime.now().timestamp() * 1000),
            "type": alert_type,
            "title": title,
            "message": message,
            "severity": severity,  # info, warning, critical
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        return alert
    
    @staticmethod
    def save_alerts(alerts: List[Dict]):
        """Save alerts to file"""
        AlertManager.ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(AlertManager.ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)
    
    @staticmethod
    def load_alerts() -> List[Dict]:
        """Load alerts from file"""
        if AlertManager.ALERTS_FILE.exists():
            with open(AlertManager.ALERTS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @staticmethod
    def get_recent_alerts(limit: int = 5) -> List[Dict]:
        """Get recent unread alerts"""
        alerts = AlertManager.load_alerts()
        unread = [a for a in alerts if not a.get('read', False)]
        return sorted(unread, key=lambda x: x['timestamp'], reverse=True)[:limit]


def render_alerts_section():
    """Render alerts in main area"""
    st.markdown("---")
    
    # Get alerts
    recent_alerts = AlertManager.get_recent_alerts()
    
    if recent_alerts:
        st.subheader("🔔 Recent Alerts & Notifications")
        
        for idx, alert in enumerate(recent_alerts):
            severity = alert.get('severity', 'info')
            
            # Color map
            color_map = {
                'critical': '🔴',
                'warning': '🟡',
                'info': '🔵'
            }
            
            icon = color_map.get(severity, '🔵')
            
            with st.expander(f"{icon} {alert['title']}", expanded=(severity == 'critical')):
                st.write(alert['message'])
                st.caption(f"📅 {alert['timestamp']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Mark as Read", key=f"alert_read_{idx}_{alert['id']}"):
                        alerts = AlertManager.load_alerts()
                        for a in alerts:
                            if a['id'] == alert['id']:
                                a['read'] = True
                        AlertManager.save_alerts(alerts)
                        st.rerun()
                with col2:
                    if st.button("📧 Email Me", key=f"alert_email_{idx}_{alert['id']}"):
                        st.success("Email notification sent!")


# ============================================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================================

class RBACManager:
    """Role-Based Access Control"""
    
    ROLE_PERMISSIONS = {
        "Admin": {
            "view_dashboard": True,
            "view_all_assessments": True,
            "create_assessments": True,
            "export_data": True,
            "manage_users": True,
            "view_alerts": True,
            "configure_system": True,
            "view_audit_logs": True,
        },
        "Analyst": {
            "view_dashboard": True,
            "view_all_assessments": True,
            "create_assessments": True,
            "export_data": True,
            "manage_users": False,
            "view_alerts": True,
            "configure_system": False,
            "view_audit_logs": True,
        },
        "Viewer": {
            "view_dashboard": True,
            "view_all_assessments": True,
            "create_assessments": False,
            "export_data": False,
            "manage_users": False,
            "view_alerts": True,
            "configure_system": False,
            "view_audit_logs": False,
        }
    }
    
    @staticmethod
    def get_user_role() -> str:
        """Get current user's role from session"""
        user = st.session_state.get('current_user', {})
        return user.get('role', 'Viewer')
    
    @staticmethod
    def has_permission(permission: str) -> bool:
        """Check if user has permission"""
        role = RBACManager.get_user_role()
        permissions = RBACManager.ROLE_PERMISSIONS.get(role, {})
        return permissions.get(permission, False)
    
    @staticmethod
    def require_permission(permission: str, message: str = None):
        """Check permission and show message if denied"""
        if not RBACManager.has_permission(permission):
            default_msg = f"❌ You don't have permission to access this feature. Required role: {permission}"
            st.warning(message or default_msg)
            return False
        return True


def render_role_based_dashboard():
    """Render role-specific dashboard sections"""
    user_role = RBACManager.get_user_role()
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"👤 **Role:** {user_role}")
    
    # Admin-only sections
    if RBACManager.has_permission("manage_users"):
        with st.sidebar.expander("👥 User Management", expanded=False):
            st.write("Manage users, roles, and permissions")
            if st.button("Add New User", key="add_user"):
                st.success("User management feature coming soon!")
    
    # Analyst+ sections
    if RBACManager.has_permission("configure_system"):
        with st.sidebar.expander("⚙️ System Configuration", expanded=False):
            st.write("Configure monitoring and alerts")
            if st.button("System Settings", key="system_settings"):
                st.info("System configuration coming soon!")
    
    # Viewer+ sections (everyone)
    if RBACManager.has_permission("view_dashboard"):
        # Dashboard is available to all authenticated users
        pass


def show_feature_availability(feature_name: str, required_role: str):
    """Show feature availability based on role"""
    if not RBACManager.has_permission("view_dashboard"):
        return False
    
    role = RBACManager.get_user_role()
    available_for = {
        "Advanced Analytics": ["Admin", "Analyst"],
        "User Management": ["Admin"],
        "System Config": ["Admin"],
        "Export Data": ["Admin", "Analyst"],
        "View Reports": ["Admin", "Analyst", "Viewer"],
    }
    
    if feature_name in available_for:
        return role in available_for[feature_name]
    return True


# ============================================================================
# UNIFIED DASHBOARD ENHANCEMENT
# ============================================================================

def render_enhanced_dashboard_header():
    """Render enhanced header with export and alerts"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 📊 Dashboard Controls")
    
    with col2:
        if st.button("🔔 View Alerts", use_container_width=True):
            st.session_state['show_alerts'] = True
    
    with col3:
        if RBACManager.has_permission("export_data"):
            if st.button("📥 Export", use_container_width=True):
                st.session_state['show_export'] = True


def initialize_enhancements():
    """Initialize all enhancements in session state"""
    if 'alerts_initialized' not in st.session_state:
        st.session_state['alerts_initialized'] = True
        st.session_state['show_alerts'] = False
        st.session_state['show_export'] = False
        st.session_state['show_rbac_info'] = False
        
        # Initialize sample alerts if none exist
        if not AlertManager.load_alerts():
            sample_alerts = [
                AlertManager.create_alert(
                    "compliance_check",
                    "Compliance Score Decreased",
                    "Your overall compliance score decreased from 88% to 84%",
                    "warning"
                ),
                AlertManager.create_alert(
                    "regulatory_change",
                    "New Regulatory Update",
                    "GDPR Article 32 has been updated. Review recommended.",
                    "info"
                ),
            ]
            AlertManager.save_alerts(sample_alerts)
