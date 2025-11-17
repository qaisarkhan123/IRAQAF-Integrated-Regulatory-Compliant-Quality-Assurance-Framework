# Quick Start Guide - New Regulatory Features

## Installation & Setup

### 1. Install Required Dependencies

```bash
pip install -r requirements-regulatory.txt
```

Or manually install:
```bash
pip install streamlit plotly pandas numpy python-dateutil
```

### 2. Run Quick Validation

```bash
python tests/test_regulatory_features.py
```

This validates all new features are working correctly.

## Basic Usage Examples

### Example 1: Track Regulatory Changes

```python
from scripts.regulatory_features_api import get_api

api = get_api()

# Track a new regulatory change
api.track_regulatory_change(
    source="Federal Register",
    regulation_id="FR-2024-001",
    regulation_name="Enhanced Security Requirements",
    change_type="requirement_update",
    description="New MFA requirements for all systems",
    impact_level="high",
    affected_systems=["auth_service", "api_gateway"],
    implementation_deadline="2024-12-31"
)

# Get recent changes (last 30 days)
recent = api.get_recent_changes(days=30)

# Get all critical changes
critical = api.get_critical_changes()
```

### Example 2: Monitor Compliance Scores

```python
# Record compliance scores
api.record_compliance_score("GDPR", 92.5)
api.record_compliance_score("HIPAA", 87.3)
api.record_compliance_score("SOC2", 94.1)

# Analyze trends
gdpr_trend = api.get_compliance_trend_analysis("GDPR")
print(f"Current GDPR Score: {gdpr_trend['current_score']}%")
print(f"Trend: {gdpr_trend['trend_direction']}")
print(f"7-Day Forecast: {gdpr_trend['forecast_7d']}%")

# Get all trends
all_trends = api.get_all_trends()
```

### Example 3: Automated Alerting

```python
# Generate custom alert
api.generate_alert(
    alert_type="compliance_threshold_breach",
    affected_regulation="HIPAA",
    message="HIPAA compliance score dropped to 75%",
    recommended_action="Review and remediate non-compliant controls",
    risk_level="high"
)

# Get all open alerts
alerts = api.get_open_alerts()
for alert in alerts:
    print(f"[{alert['risk_level']}] {alert['alert_type']}: {alert['message']}")

# Get critical alerts
critical_alerts = api.get_critical_alerts()

# Acknowledge an alert
api.acknowledge_alert(alert_id)
```

### Example 4: Validate System Compliance

```python
# Validate single framework
result = api.validate_system_compliance(
    system_name="authentication_service",
    framework="GDPR",
    controls={
        "lawful_basis": "compliant",
        "data_protection": "compliant",
        "privacy_by_design": "partial",
        "data_subject_rights": "compliant",
        "dpia": "non_compliant",
        "security_measures": "compliant"
    }
)

print(f"Compliance: {result['compliance_percentage']:.1f}%")
print(f"Status: {result['compliance_level']}")
print(f"Non-compliant: {result['non_compliant_controls']}")

# Validate across multiple frameworks
cross_result = api.validate_cross_framework(
    system_name="data_storage",
    frameworks=["GDPR", "HIPAA", "SOC2"],
    controls={
        "GDPR": {"data_protection": "compliant", "encryption": "compliant"},
        "HIPAA": {"access_controls": "compliant", "audit": "partial"},
        "SOC2": {"availability": "compliant", "processing": "compliant"}
    }
)

print(f"Overall Compliance: {cross_result['overall_compliance_percentage']:.1f}%")
```

### Example 5: Gap Analysis & Remediation

```python
# Identify compliance gaps
gaps = api.identify_compliance_gaps(
    framework="GDPR",
    current_state={
        "data_protection": "partial",
        "dpia": "none",
        "incident_response": "non_compliant"
    },
    required_state={
        "data_protection": "compliant",
        "dpia": "compliant",
        "incident_response": "compliant"
    }
)

print(f"Found {len(gaps)} compliance gaps")

# Get critical gaps
critical_gaps = api.get_critical_gaps()
for gap in critical_gaps:
    print(f"[CRITICAL] {gap['requirement']}: {gap['current_status']} → {gap['required_status']}")

# Create remediation actions
for gap in gaps:
    action = api.create_remediation_action(
        gap_id=gap['gap_id'],
        action_title=f"Fix: {gap['requirement']}",
        description=f"Remediate {gap['requirement']} gap",
        assigned_to="security_team",
        due_date="2024-06-30"
    )

# Track progress
progress = api.get_remediation_progress()
print(f"Remediation: {progress['completed']}/{progress['total']} complete ({progress['completion_percentage']:.0f}%)")

# Update remediation status
api.update_remediation_status(
    action_id="action_001",
    status="in_progress",
    completion_percentage=75.0
)
```

### Example 6: Regulatory Impact Assessment

```python
# Assess impact of a regulatory change
assessment = api.assess_regulatory_impact(
    regulation_id="REG-2024-001",
    regulation_name="AI Governance Framework",
    affected_systems=["ml_inference", "model_training", "monitoring"],
    change_description="New requirements for model transparency and explainability",
    current_compliance_status="partially_compliant"
)

print(f"Impact Score: {assessment['impact_score']}/10")
print(f"Priority: {assessment['priority_level']}")
print(f"Estimated Effort: {assessment['effort_estimate_hours']} hours")
print(f"Timeline: {assessment['recommended_timeline_days']} days")
```

### Example 7: Dashboard Integration

```python
import streamlit as st
from scripts.regulatory_features_api import get_api
from dashboard.enhanced_ui_components import (
    render_metric_card,
    render_compliance_gauge,
    render_alert_panel,
    render_regulatory_timeline,
    render_compliance_trend_chart
)

api = get_api()

st.set_page_config(page_title="Regulatory Dashboard", layout="wide")
st.title("Regulatory Compliance Dashboard")

# Display key metrics
col1, col2, col3 = st.columns(3)

gdpr_trend = api.get_compliance_trend_analysis("GDPR")
with col1:
    render_metric_card(
        title="GDPR Compliance",
        value=gdpr_trend['current_score'],
        unit="%",
        status="good" if gdpr_trend['current_score'] >= 80 else "warning",
        trend=f"{gdpr_trend['trend_direction']}"
    )

hipaa_trend = api.get_compliance_trend_analysis("HIPAA")
with col2:
    render_compliance_gauge(
        value=hipaa_trend['current_score'],
        title="HIPAA Compliance",
        threshold=80.0
    )

soc2_trend = api.get_compliance_trend_analysis("SOC2")
with col3:
    render_metric_card(
        title="SOC2 Compliance",
        value=soc2_trend['current_score'],
        unit="%"
    )

# Display alerts
st.subheader("Active Alerts")
render_alert_panel(api.get_open_alerts())

# Display timeline
st.subheader("Recent Changes")
changes = api.get_recent_changes(days=30)
render_regulatory_timeline(changes)

# Display trends
st.subheader("Compliance Trends")
col1, col2 = st.columns(2)

with col1:
    render_compliance_trend_chart(
        [api.get_compliance_trend_analysis("GDPR")],
        metric_name="GDPR"
    )

with col2:
    render_compliance_trend_chart(
        [api.get_compliance_trend_analysis("HIPAA")],
        metric_name="HIPAA"
    )
```

### Example 8: Generate Reports

```python
# Generate comprehensive compliance report
report = api.generate_compliance_report("authentication_service")

print(f"Report Generated: {report['timestamp']}")
print(f"System: {report['system_name']}")
print(f"Compliance Trends: {len(report['compliance_trends'])}")
print(f"Open Alerts: {len(report['open_alerts'])}")
print(f"Critical Gaps: {len(report['critical_gaps'])}")
print(f"Remediation Progress: {report['remediation_progress']['completion_percentage']:.0f}%")

# Export data
json_export = api.export_data(format="json", data_type="all")
with open("compliance_export.json", "w") as f:
    f.write(json_export)
```

### Example 9: System Status Check

```python
# Get overall system status
status = api.get_system_status()

print("System Status:")
print(f"  Open Alerts: {status['open_alerts']}")
print(f"  Critical Alerts: {status['critical_alerts']}")
print(f"  Total Changes: {status['total_changes']}")
print(f"  Remediation Progress: {status['remediation_progress']['completion_percentage']:.0f}%")
print(f"  Cache Size: {status['cache_status']['memory_cache_size']} entries")
```

## Common Workflows

### Workflow 1: Initial Setup & Configuration

1. Initialize API
2. Configure frameworks and controls
3. Validate baseline compliance
4. Identify gaps
5. Create remediation plan

### Workflow 2: Ongoing Monitoring

1. Record compliance scores daily/weekly
2. Monitor compliance trends
3. Generate alerts for threshold breaches
4. Review and acknowledge alerts
5. Update remediation progress

### Workflow 3: Regulatory Change Management

1. Track new regulatory changes
2. Assess impact on systems
3. Identify affected controls
4. Create remediation actions
5. Monitor implementation progress

### Workflow 4: Compliance Reporting

1. Collect compliance data
2. Analyze trends
3. Generate comprehensive report
4. Export for audit/compliance team
5. Track remediation items

## Troubleshooting

### Issue: API not available
- Ensure all dependencies are installed
- Check that advanced modules are in scripts directory
- Verify Python path is correct

### Issue: Cache not working
- Check cache directory permissions
- Verify disk space available
- Clear expired cache: `api.cleanup()`

### Issue: Alerts not generating
- Verify compliance scores are being recorded
- Check alert thresholds and rules
- Review alert configuration in API

### Issue: Performance issues
- Clear expired cache entries
- Reduce cache TTL for high-volume data
- Use data filtering and pagination

## Next Steps

1. **Integrate with existing dashboard**: Add new components to your dashboard app
2. **Set up scheduled tasks**: Use cron/scheduler for regular compliance checks
3. **Configure alerts**: Set up email/Slack notifications for critical alerts
4. **Automate reporting**: Generate and distribute compliance reports
5. **Enable audit logging**: Track all compliance-related activities

## Support

For issues or questions:
1. Check REGULATORY_FEATURES_GUIDE.md for detailed documentation
2. Review test cases in tests/test_regulatory_features.py
3. Check module docstrings for function details
4. Review logs for error messages
