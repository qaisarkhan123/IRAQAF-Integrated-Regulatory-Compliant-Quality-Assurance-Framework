# Deployment & Integration Guide

## Deploying New Regulatory Features

### Step 1: File Placement Verification

Ensure all files are in the correct locations:

```
C:\Users\khan\Downloads\iraqaf_starter_kit\
├── scripts/
│   ├── advanced_regulatory_monitor.py
│   ├── advanced_compliance_checks.py
│   └── regulatory_features_api.py
├── dashboard/
│   └── enhanced_ui_components.py
├── tests/
│   └── test_regulatory_features.py
├── REGULATORY_FEATURES_GUIDE.md
└── REGULATORY_QUICKSTART.md
```

### Step 2: Verify Installation

Run validation to ensure all components work:

```bash
cd C:\Users\khan\Downloads\iraqaf_starter_kit
python tests/test_regulatory_features.py
```

Expected output: All tests pass (18+ test methods)

### Step 3: Dashboard Integration

To integrate new features into your existing Streamlit dashboard:

#### Option A: Add to existing app.py

```python
# At top of dashboard/app.py
from scripts.regulatory_features_api import get_api, initialize_api
from dashboard.enhanced_ui_components import (
    setup_theme,
    render_metric_card,
    render_compliance_gauge,
    render_alert_panel,
    render_regulatory_timeline,
    render_compliance_trend_chart,
    render_risk_heat_map,
    render_remediation_tracker
)

# Initialize API on app startup
@st.cache_resource
def init_regulatory_api():
    return get_api()

api = init_regulatory_api()
setup_theme("light")  # or "dark" or "auto"
```

#### Option B: Create new dashboard pages

```
dashboard/
├── pages/
│   ├── 01_regulatory_monitoring.py
│   ├── 02_compliance_dashboard.py
│   ├── 03_alert_management.py
│   └── 04_remediation_tracker.py
```

**Example: 01_regulatory_monitoring.py**

```python
import streamlit as st
from scripts.regulatory_features_api import get_api
from dashboard.enhanced_ui_components import render_regulatory_timeline, render_metric_card

st.set_page_config(page_title="Regulatory Monitoring", layout="wide")
st.title("🔍 Regulatory Change Monitoring")

api = get_api()

col1, col2, col3 = st.columns(3)

# Get stats
recent = api.get_recent_changes(days=30)
critical = api.get_critical_changes()

with col1:
    render_metric_card("Recent Changes (30 days)", len(recent), "changes")

with col2:
    render_metric_card("Critical Changes", len(critical), "alerts")

with col3:
    trends = api.get_all_trends()
    render_metric_card("Tracked Frameworks", len(trends), "frameworks")

# Display timeline
st.subheader("Regulatory Timeline")
render_regulatory_timeline(recent)

# Display critical changes
if critical:
    st.subheader("⚠️ Critical Changes")
    for change in critical:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{change['regulation_name']}**")
                st.caption(change['description'])
            with col2:
                st.write(change['impact_level'].upper())
            with col3:
                st.write(f"Due: {change['implementation_deadline']}")
```

### Step 4: Configure Compliance Frameworks

Set up which frameworks you want to monitor:

```python
# Create configuration file: compliance_config.json
{
  "frameworks": ["GDPR", "HIPAA", "SOC2", "ISO27001"],
  "alert_thresholds": {
    "critical": 70,
    "warning": 80,
    "healthy": 90
  },
  "cache_ttl_hours": 24,
  "persistence_enabled": true
}
```

### Step 5: Set Up Monitoring Schedule

Create a scheduled task to regularly check compliance:

```python
# scripts/compliance_scheduler.py
import schedule
import time
from scripts.regulatory_features_api import get_api

def check_compliance():
    api = get_api()
    
    # Record compliance scores
    scores = {
        "GDPR": 92.5,
        "HIPAA": 87.3,
        "SOC2": 94.1
    }
    
    for framework, score in scores.items():
        api.record_compliance_score(framework, score)

# Schedule to run daily at 2 AM
schedule.every().day.at("02:00").do(check_compliance)

while True:
    schedule.run_pending()
    time.sleep(60)
```

Or use Windows Task Scheduler:

```batch
# Run daily check
schtasks /create /tn "Daily Compliance Check" /tr "python scripts/compliance_scheduler.py" /sc daily /st 02:00
```

### Step 6: Set Up Alerting

Configure alerts for critical issues:

```python
# scripts/alert_handler.py
from scripts.regulatory_features_api import get_api
import smtplib
from email.mime.text import MIMEText

def send_email_alert(alert, recipient):
    # Send email about critical alert
    msg = MIMEText(f"Alert: {alert['message']}")
    msg['Subject'] = f"[{alert['risk_level']}] Compliance Alert"
    
    with smtplib.SMTP('localhost') as server:
        server.sendmail("alerts@company.com", recipient, msg.as_string())

# Monitor critical alerts
api = get_api()
critical_alerts = api.get_critical_alerts()

for alert in critical_alerts:
    if alert['status'] != 'acknowledged':
        send_email_alert(alert, "compliance-team@company.com")
```

### Step 7: Verify Integration

Test that all features work with your dashboard:

```bash
# Run dashboard with new features
streamlit run dashboard/app.py

# In browser, navigate to dashboard
# http://localhost:8501
```

### Step 8: Monitor Performance

```python
# Check system status
api = get_api()
status = api.get_system_status()

print(f"Cache Status: {status['cache_status']}")
print(f"Memory Usage: {status.get('memory_usage', 'N/A')}")
print(f"Active Alerts: {status['open_alerts']}")
```

## Production Checklist

- [ ] All files placed in correct directories
- [ ] Dependencies installed
- [ ] Tests pass successfully
- [ ] Dashboard imports work without errors
- [ ] Compliance frameworks configured
- [ ] Alerting configured
- [ ] Monitoring schedule set up
- [ ] Email/Slack notifications working
- [ ] Caching is functioning
- [ ] Performance acceptable
- [ ] Data persistence working
- [ ] Backup strategy in place

## Performance Optimization

### Cache Management

```python
# Optimize cache TTL based on data freshness needs
api = get_api()

# Set cache TTL to 4 hours for regulatory data (changes less frequently)
api._cache.ttl_hours = 4

# Cleanup expired entries weekly
import schedule
schedule.every().week.do(api._persistence_manager.cleanup)
```

### Data Filtering

```python
# Don't load all data at once
recent = api.get_recent_changes(days=7)  # Instead of all history
critical = api.get_critical_alerts()  # Filter for critical only
gaps = api.get_critical_gaps()  # Get priority items only
```

## Troubleshooting Deployment

### Issue: Import errors
**Solution:** Verify all files are in correct directories and Python path includes project root

### Issue: UI components not displaying
**Solution:** Ensure Plotly and Streamlit versions are compatible

### Issue: Slow performance
**Solution:** Increase cache TTL, reduce query scope, enable pagination

### Issue: Alerts not triggering
**Solution:** Verify compliance scores are being recorded, check threshold configuration

## Rollback Plan

If issues occur:

1. Stop dashboard: `Ctrl+C`
2. Remove new feature imports from dashboard/app.py
3. Delete cache: `rm -r .cache/`
4. Restart dashboard: `streamlit run dashboard/app.py`
5. Investigate issue in logs

## Support & Documentation

- **Quick Start Guide**: See REGULATORY_QUICKSTART.md
- **Complete Documentation**: See REGULATORY_FEATURES_GUIDE.md
- **Tests & Examples**: See tests/test_regulatory_features.py
- **API Reference**: See docstrings in script files

## Next Steps After Deployment

1. Monitor dashboard performance for 24 hours
2. Collect user feedback on new features
3. Set up compliance trend reporting
4. Configure escalation procedures for critical alerts
5. Plan for advanced features (API endpoints, database persistence)
