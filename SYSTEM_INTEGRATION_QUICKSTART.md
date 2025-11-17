# System Integration Quick Start

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install sqlalchemy
```

### Step 2: Initialize System

```python
from scripts.system_integration import initialize_coordinator

# Initialize with SQLite (automatic setup)
coordinator = initialize_coordinator(
    db_url="sqlite:///compliance.db",
    monitor_interval=60,  # Check every minute
    start_monitoring=True,
)

print("✓ System initialized and monitoring started")
```

### Step 3: Start Using

```python
from datetime import datetime, timedelta

# Track a regulatory change
coordinator.track_regulatory_change(
    source="Federal Register",
    regulation_id="FR-2024-001",
    regulation_name="Data Protection Rules",
    change_type="new_requirement",
    description="New data minimization requirements",
    impact_level="high",
    affected_systems=["database", "api"],
    implementation_deadline=datetime.utcnow() + timedelta(days=90),
)

# Record compliance scores
coordinator.record_compliance_score(
    framework="GDPR",
    system_name="all_systems",
    score=92.5,
)

# Get open alerts
alerts = coordinator.get_open_alerts()
print(f"Open alerts: {len(alerts)}")

# Get system status
status = coordinator.get_system_status()
print(f"System status: {status}")
```

## Common Tasks

### Task 1: Track Regulatory Changes

```python
coordinator.track_regulatory_change(
    source="NIST",
    regulation_id="NIST-SP-800-171",
    regulation_name="Cybersecurity Maturity Model",
    change_type="update",
    description="Updated security controls for federal contractors",
    impact_level="high",
    affected_systems=["all"],
    implementation_deadline=datetime.utcnow() + timedelta(days=180),
)

# View recent changes
changes = coordinator.get_recent_changes(days=30)
for change in changes:
    print(f"- {change['regulation_name']}: {change['impact_level']}")
```

### Task 2: Monitor Compliance Scores

```python
# Record daily compliance checks
frameworks = {
    "GDPR": 92.5,
    "HIPAA": 87.3,
    "SOC2": 94.1,
    "ISO27001": 89.0,
}

for framework, score in frameworks.items():
    coordinator.record_compliance_score(
        framework=framework,
        system_name="all_systems",
        score=score,
    )

# Get score history
scores = coordinator.get_compliance_scores("GDPR", days=30)
print(f"GDPR scores (last 30 days): {len(scores)} records")
```

### Task 3: Manage Alerts

```python
# Generate an alert
alert = coordinator.generate_alert(
    alert_type="compliance_threshold_breach",
    message="HIPAA compliance dropped below 90%",
    risk_level="high",
    affected_regulation="HIPAA",
    recommended_action="Review access controls",
)
print(f"Alert created: {alert['id']}")

# Get open alerts
open_alerts = coordinator.get_open_alerts()
print(f"Open alerts: {len(open_alerts)}")

# Acknowledge alert
coordinator.acknowledge_alert(alert['id'])

# Resolve alert
coordinator.resolve_alert(alert['id'])
```

### Task 4: Track Remediation

```python
# Create remediation action
action = coordinator.create_remediation_action(
    gap_id="GAP-001",
    action_title="Implement MFA for Admin Access",
    description="Deploy multi-factor authentication for all admin accounts",
    assigned_to="security_team",
    due_date=datetime.utcnow() + timedelta(days=30),
    priority=9,
)
print(f"Action created: {action['id']}")

# Update progress
coordinator.update_remediation_status(
    action_id=action['id'],
    status="in_progress",
    completion_percentage=25.0,
)

# View pending actions
pending = coordinator.get_pending_remediation()
print(f"Pending remediation: {len(pending)} actions")

# View overdue actions
overdue = coordinator.get_overdue_actions()
print(f"Overdue actions: {len(overdue)}")
```

### Task 5: Generate Reports

```python
# Get compliance report
report = coordinator.get_compliance_report(system_name="authentication_system")

print(f"Report generated: {report['generated_at']}")
print(f"Recent changes: {len(report['changes'])}")
print(f"Open alerts: {len(report['alerts']['open'])}")
print(f"Critical alerts: {len(report['alerts']['critical'])}")
print(f"Pending remediations: {len(report['remediation']['pending'])}")
print(f"Overdue actions: {len(report['remediation']['overdue'])}")

# Export data
json_data = coordinator.export_compliance_data(format="json")
with open("compliance_export.json", "w") as f:
    f.write(json_data)
```

### Task 6: Real-Time Monitoring

```python
# Get recent events
recent_events = coordinator.get_recent_events(count=10)
for event in recent_events:
    print(f"Event: {event['event_type']} - {event['timestamp']}")

# Get event history for specific type
alert_events = coordinator.get_event_history(event_type="alert_triggered")
print(f"Alert events: {len(alert_events)}")

# Register for real-time alerts
def on_critical_alert(event):
    print(f"⚠️ CRITICAL ALERT: {event['data']}")

coordinator.register_event_callback("alert_triggered", on_critical_alert)
```

### Task 7: System Status

```python
# Get current system status
status = coordinator.get_system_status()

print(f"Total regulatory changes: {status['total_changes']}")
print(f"Total alerts: {status['total_alerts']}")
print(f"Critical alerts: {status['critical_alerts']}")
print(f"Open alerts: {status['open_alerts']}")
print(f"Total remediation actions: {status['total_remediation_actions']}")
print(f"Completed actions: {status['completed_actions']}")
print(f"Pending actions: {status['pending_actions']}")

# Monitor service health
print(f"System initialized: {status['initialized']}")
print(f"Monitoring active: {status['monitoring']}")
```

## Integration with Dashboard

```python
import streamlit as st
from scripts.system_integration import get_coordinator
from dashboard.enhanced_ui_components import (
    render_metric_card,
    render_alert_panel,
    render_compliance_gauge,
)

# Initialize coordinator
@st.cache_resource
def get_system():
    return get_coordinator()

coordinator = get_system()

# Display metrics
st.title("🔍 Regulatory Compliance Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    status = coordinator.get_system_status()
    render_metric_card(
        title="Active Alerts",
        value=status["open_alerts"],
        unit="alerts",
    )

with col2:
    render_metric_card(
        title="Critical Issues",
        value=status["critical_alerts"],
        unit="critical",
    )

with col3:
    render_metric_card(
        title="Pending Actions",
        value=status["pending_actions"],
        unit="actions",
    )

with col4:
    render_metric_card(
        title="Recent Changes",
        value=status["total_changes"],
        unit="changes",
    )

# Display alerts
st.subheader("Open Alerts")
alerts = coordinator.get_open_alerts()
render_alert_panel(alerts)

# Display recent events
st.subheader("Recent Events")
events = coordinator.get_recent_events(10)
for event in events:
    st.write(f"**{event['event_type']}** - {event['timestamp']}")
```

## Scheduled Monitoring

```python
import schedule
import time
from scripts.system_integration import get_coordinator

coordinator = get_coordinator()

def daily_check():
    """Run daily compliance check."""
    print("Running daily compliance check...")
    
    # Record compliance scores
    scores = {
        "GDPR": 92.5,
        "HIPAA": 87.3,
        "SOC2": 94.1,
    }
    
    for framework, score in scores.items():
        coordinator.record_compliance_score(framework, "all_systems", score)
    
    print("✓ Daily check complete")

def weekly_report():
    """Generate weekly report."""
    print("Generating weekly report...")
    report = coordinator.get_compliance_report()
    
    # Save report
    import json
    with open(f"report_{datetime.now().date()}.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("✓ Report generated")

# Schedule tasks
schedule.every().day.at("02:00").do(daily_check)
schedule.every().monday.at("09:00").do(weekly_report)

# Run scheduler
print("Starting scheduler...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Environment Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///compliance.db

# Monitoring
MONITOR_INTERVAL=60
MONITOR_ENABLED=true

# Thresholds
COMPLIANCE_THRESHOLD_WARNING=80
COMPLIANCE_THRESHOLD_CRITICAL=70
```

Load configuration:

```python
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///compliance.db")
monitor_interval = int(os.getenv("MONITOR_INTERVAL", "60"))

coordinator = initialize_coordinator(
    db_url=db_url,
    monitor_interval=monitor_interval,
    start_monitoring=True,
)
```

## Troubleshooting

### Issue: "Database not initialized"

```python
# Make sure to initialize first
from scripts.system_integration import initialize_coordinator

coordinator = initialize_coordinator()  # Initialize first
coordinator.track_regulatory_change(...)  # Then use
```

### Issue: Monitoring not detecting changes

```python
# Check monitoring status
status = coordinator.get_system_status()
print(f"Monitoring: {status['monitoring']}")

# Restart if needed
coordinator.stop_monitoring()
coordinator.start_monitoring()
```

### Issue: No events in history

```python
# Events are only generated when changes occur
# Make sure you're generating data first
coordinator.record_compliance_score("GDPR", "system1", 90.0)

# Then check events
events = coordinator.get_recent_events()
print(f"Events: {len(events)}")
```

## Performance Tips

1. **Increase monitoring interval** for large systems:
   ```python
   coordinator.monitor_interval = 300  # Check every 5 minutes
   ```

2. **Limit event history** to reduce memory:
   ```python
   coordinator.monitor.event_history = deque(maxlen=500)  # Reduce from 1000
   ```

3. **Use PostgreSQL** for production instead of SQLite:
   ```python
   coordinator = initialize_coordinator(
       db_url="postgresql://user:password@localhost/compliance"
   )
   ```

4. **Archive old data** regularly:
   ```python
   # Delete records older than 1 year
   cutoff = datetime.utcnow() - timedelta(days=365)
   session.query(ComplianceScore).filter(ComplianceScore.recorded_at < cutoff).delete()
   ```

## Next Steps

1. Set up PostgreSQL for production
2. Configure alert notifications (email/Slack)
3. Create dashboard pages for each component
4. Schedule daily/weekly compliance checks
5. Integrate with existing audit logging
6. Set up database backups
7. Create API endpoints for external access

## Support

For detailed information:
- See `SYSTEM_INTEGRATION_GUIDE.md` for architecture
- See module docstrings for API details
- See `test_system_integration.py` for usage examples
