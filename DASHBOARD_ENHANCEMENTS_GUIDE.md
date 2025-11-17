# Dashboard Enhancements Implementation Guide

## Overview

Four major enhancement modules have been created for your IRAQAF dashboard:

1. **Alerts System** (`alerts.py`) - Real-time alerts and notifications
2. **Export Manager** (`exports.py`) - PDF and CSV export functionality  
3. **Authentication** (`authentication.py`) - User authentication and RBAC
4. **Domain Dashboards** (`domain_dashboards.py`) - Regulatory domain-specific views
5. **Integration Module** (`enhancements.py`) - Central integration point

## Quick Start

### 1. Alerts System

```python
from alerts import AlertManager

alerts = AlertManager()

# Create an alert
alert_id = alerts.create_alert(
    alert_type="regulatory_change",
    severity="high",
    title="FDA Guidance Update",
    description="New FDA guidance on Quality by Design released",
    domain="FDA"
)

# Retrieve alerts
recent_alerts = alerts.get_alerts(hours=24, unread_only=False)

# Mark as read
alerts.mark_as_read(alert_id)

# Display in Streamlit
for alert in recent_alerts:
    alerts.display_alert_toast(alert)
```

**Severity Levels:** `critical`, `high`, `medium`, `low`

**Alert Types:** `regulatory_change`, `compliance_issue`, `threshold_breach`, `audit_event`

### 2. Export Manager

```python
from exports import ExportManager
import pandas as pd

exporter = ExportManager()

# Create sample data
data = pd.DataFrame({
    "Domain": ["FDA", "EPA"],
    "Score": [92, 88]
})

# Export to CSV
csv_bytes = exporter.export_to_csv(data, filename="report.csv")

# Export to Excel with multiple sheets
excel_bytes = exporter.export_to_excel({
    "Summary": data,
    "Details": other_data
})

# Create PDF report
pdf_bytes = exporter.generate_compliance_report_pdf(
    title="Compliance Report",
    executive_summary="Annual compliance assessment",
    sections=[
        {"heading": "Overview", "content": "..."},
        {"heading": "Findings", "content": data}
    ]
)

# Streamlit download buttons
exporter.create_streamlit_download_buttons(data, "compliance")
```

### 3. Authentication System

```python
from authentication import (
    AuthenticationManager,
    User,
    check_authentication,
    require_permission
)

auth = AuthenticationManager()

# Create user
auth.create_user(
    username="analyst1",
    password="secure_pass",
    role="analyst",
    display_name="Jane Smith",
    domain="FDA"
)

# Authenticate
success, user = auth.authenticate("analyst1", "secure_pass")
if success:
    session_id = auth.create_session("analyst1")
    print(f"Session created: {session_id}")

# Validate session
if auth.validate_session(session_id):
    user = auth.get_session_user(session_id)
    print(f"Authenticated as: {user['display_name']}")

# Check permissions
roles = User.ROLE_DEFINITIONS
permissions = roles["analyst"]["permissions"]
# Output: ['view_all_reports', 'export_data', 'create_alerts', ...]
```

**Available Roles:**
- **admin** - Full system access, user management, settings
- **analyst** - Reporting, export, alert creation, audit logs
- **viewer** - Dashboard and report viewing only

### 4. Domain Dashboards

```python
from domain_dashboards import DomainDashboard, RegulatoryDomain

# Available domains
domains = RegulatoryDomain.DOMAINS  # FDA, EPA, SEC, ISO, GDPR

# Create domain dashboard
fda_dashboard = DomainDashboard("FDA")

# Display components
fda_dashboard.display_domain_overview()
fda_dashboard.display_regulations()
fda_dashboard.display_metrics()
fda_dashboard.display_audit_readiness()
fda_dashboard.display_recent_findings()
fda_dashboard.display_compliance_timeline()

# Export domain report
pdf_bytes = fda_dashboard.export_domain_report()
```

**Supported Domains:**
- **FDA** - Food and Drug Administration (Quality, GMP, Validation)
- **EPA** - Environmental Protection Agency (Emissions, Water, Waste)
- **SEC** - Securities and Exchange Commission (Financial, Governance)
- **ISO** - International Standards (Quality, Environment, Security)
- **GDPR** - Data Protection (Privacy, Data Rights, Breach Response)

### 5. Integration in Main App

```python
import streamlit as st
from enhancements import (
    initialize_dashboard,
    render_dashboard_header,
    render_quick_stats
)

# Initialize all enhancements
enhancements = initialize_dashboard()

# Check authentication
if not enhancements.render_authentication_ui():
    st.stop()

# Render UI components
enhancements.render_user_menu()
enhancements.render_admin_panel()
enhancements.render_sidebar_alerts()

# Main content
render_dashboard_header()
render_quick_stats()

# Your dashboard tabs and content here...
```

## Data Storage

Files are stored in the following directories:

```
project_root/
├── data/
│   ├── alerts/
│   │   └── active_alerts.json
│   ├── auth/
│   │   ├── users.json
│   │   └── sessions.json
│   └── domain_dashboards/
│       └── (domain-specific data)
└── exports/
    └── (exported reports)
```

## Default User

**Username:** `admin`  
**Password:** `admin_default_123`  
**Role:** `admin`

⚠️ **Important:** Change the default admin password immediately in production!

## Feature Comparison

| Feature | Analyst | Viewer | Admin |
|---------|---------|--------|-------|
| View Dashboards | ✓ | ✓ | ✓ |
| Export Data | ✓ | ✗ | ✓ |
| Create Alerts | ✓ | ✗ | ✓ |
| Manage Users | ✗ | ✗ | ✓ |
| Audit Logs | ✓ | ✗ | ✓ |
| System Settings | ✗ | ✗ | ✓ |

## Integration Steps

### Step 1: Add to requirements.txt
```
reportlab>=4.0.0
fpdf2>=2.7.0
streamlit-authenticator>=0.2.0
openpyxl>=3.1.0
```

### Step 2: Import in your app

```python
from alerts import AlertManager
from exports import ExportManager
from authentication import AuthenticationManager
from domain_dashboards import DomainDashboard
from enhancements import initialize_dashboard
```

### Step 3: Use in Streamlit pages

See `example_integrated_app.py` for complete working example.

### Step 4: Run the dashboard

```bash
streamlit run example_integrated_app.py
```

## API Reference

### AlertManager
- `create_alert()` - Create new alert
- `get_alerts()` - Retrieve filtered alerts
- `mark_as_read()` - Mark alert as read
- `delete_alert()` - Delete alert
- `get_stats()` - Get alert statistics

### ExportManager
- `export_to_csv()` - Export DataFrame to CSV
- `export_to_excel()` - Export multiple sheets to Excel
- `generate_compliance_report_pdf()` - Create PDF report
- `create_streamlit_download_buttons()` - Add download UI

### AuthenticationManager
- `create_user()` - Create new user account
- `authenticate()` - Verify username/password
- `create_session()` - Create user session
- `validate_session()` - Check session validity
- `list_users()` - Get all users
- `deactivate_user()` - Disable account
- `update_user_role()` - Change user role

### DomainDashboard
- `display_domain_overview()` - Show domain metrics
- `display_regulations()` - List regulations
- `display_metrics()` - Show compliance metrics
- `display_audit_readiness()` - Audit readiness scorecard
- `display_recent_findings()` - Show audit findings
- `export_domain_report()` - Generate PDF report

## Customization

### Adding New Domains

Edit `domain_dashboards.py` and add to `RegulatoryDomain.DOMAINS`:

```python
DOMAINS = {
    "CUSTOM": {
        "name": "Custom Domain",
        "color": "#hexcolor",
        "icon": "emoji",
        "key_regulations": [...],
        "metrics": [...]
    }
}
```

### Adding New Roles

Edit `authentication.py` and add to `User.ROLE_DEFINITIONS`:

```python
ROLE_DEFINITIONS = {
    "custom_role": {
        "display_name": "Custom Role",
        "permissions": [...]
    }
}
```

### Styling Alerts

Modify colors in `enhancements.py` CSS section:

```python
<style>
.alert-critical { color: #d62728; }
/* Update as needed */
</style>
```

## Troubleshooting

**Issue:** Import errors for enhancement modules
**Solution:** Ensure all files are in the `dashboard/` directory

**Issue:** Authentication not persisting
**Solution:** Check that `data/auth/` directory has write permissions

**Issue:** PDF export fails
**Solution:** Verify reportlab is installed: `pip install reportlab`

**Issue:** Alerts not showing
**Solution:** Initialize AlertManager after Streamlit app starts

## Next Steps

1. ✅ Integrate all modules into `app.py`
2. ✅ Add real-time alert monitoring
3. ✅ Set up automated report generation
4. ✅ Configure email notifications
5. ✅ Add API endpoints for alerts
6. ✅ Implement audit logging
7. ✅ Set up dashboard caching

## Support

For issues or questions about the enhancements, refer to:
- Module docstrings for detailed API docs
- `example_integrated_app.py` for usage examples
- Individual module files for implementation details
