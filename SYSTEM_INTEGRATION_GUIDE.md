# System Integration & Architecture Guide

## Overview

The integrated regulatory compliance system combines multiple specialized modules into a cohesive workflow with database persistence and real-time monitoring. This guide covers architecture, integration patterns, and workflows.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard/UI Layer                        │
│              (Streamlit + Enhanced Components)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              System Integration Coordinator                   │
│  (Central orchestrator connecting all modules and services)  │
└─────────────────────────────────────────────────────────────┘
        ↓                ↓                ↓                ↓
    ┌────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
    │Database │   │Real-Time  │    │Regulatory  │    │Compliance│
    │Persistence│  │Monitoring │   │Monitoring  │    │Validation│
    │Layer    │   │Service    │   │Features    │    │Features  │
    └────────┘    └──────────┘    └────────────┘    └──────────┘
```

### Module Responsibilities

#### 1. **Database Layer** (`database_layer.py`)
- **Purpose:** Persistent data storage
- **Technology:** SQLAlchemy ORM
- **Databases:** SQLite (default) or PostgreSQL (production)
- **Entities:**
  - RegulatoryChange: Tracks regulatory updates
  - ComplianceScore: Historical compliance data
  - ComplianceAlert: System alerts and incidents
  - RemediationAction: Remediation tracking
  - RegulatoryImpact: Impact assessments
  - SystemHealthLog: Performance metrics

#### 2. **Real-Time Monitor** (`realtime_monitor.py`)
- **Purpose:** Continuous system monitoring and event generation
- **Features:**
  - Background monitoring thread
  - State change detection
  - Threshold checking
  - Event emission to callbacks
  - Event history tracking
  - WebSocket-ready architecture

#### 3. **System Coordinator** (`system_integration.py`)
- **Purpose:** Central orchestration point
- **Responsibilities:**
  - Manages all sub-services
  - Provides unified API
  - Coordinates workflows
  - Handles data persistence
  - Manages real-time monitoring
  - Generates reports

#### 4. **Regulatory Features API** (`regulatory_features_api.py`)
- **Purpose:** Regulatory monitoring and compliance logic
- **Features:**
  - Change tracking and analysis
  - Compliance trend forecasting
  - Alert generation
  - Impact assessment

#### 5. **Enhanced UI Components** (`enhanced_ui_components.py`)
- **Purpose:** Dashboard visualizations
- **Components:**
  - Metric cards with trend indicators
  - Compliance gauges with thresholds
  - Timeline visualizations
  - Risk heat maps
  - Alert panels
  - Progress trackers

## Workflows

### Workflow 1: Regulatory Change Detection & Response

```
1. New Regulatory Change Detected
        ↓
2. SystemCoordinator.track_regulatory_change()
        ↓
3. Save to Database (RegulatoryChange)
        ↓
4. Notify API & Real-Time Monitor
        ↓
5. RealTimeMonitor emits EventType.REGULATORY_CHANGE
        ↓
6. Dashboard receives update in real-time
        ↓
7. Generate compliance alerts if needed
        ↓
8. Create remediation actions for gaps
```

**Usage:**
```python
from scripts.system_integration import get_coordinator

coordinator = get_coordinator()

coordinator.track_regulatory_change(
    source="Federal Register",
    regulation_id="FR-2024-001",
    regulation_name="AI Governance Framework",
    change_type="new_requirement",
    description="New requirements for AI model transparency",
    impact_level="high",
    affected_systems=["ml_inference", "model_training"],
    implementation_deadline=datetime.utcnow() + timedelta(days=180),
)
```

### Workflow 2: Compliance Monitoring & Alerting

```
1. Record Compliance Score
        ↓
2. SystemCoordinator.record_compliance_score()
        ↓
3. Save to Database (ComplianceScore)
        ↓
4. Detect threshold breach (< 80%)
        ↓
5. RealTimeMonitor emits EventType.THRESHOLD_BREACH
        ↓
6. Generate alert if score dropped significantly
        ↓
7. Dashboard shows warning indicator
        ↓
8. Initiate remediation if needed
```

**Usage:**
```python
# Record daily compliance scores
for framework in ["GDPR", "HIPAA", "SOC2"]:
    score = calculate_compliance_score(framework)
    coordinator.record_compliance_score(
        framework=framework,
        system_name="all_systems",
        score=score,
        status="compliant" if score >= 80 else "partial",
    )
```

### Workflow 3: Gap Analysis & Remediation

```
1. Validate System Compliance
        ↓
2. Identify Compliance Gaps
        ↓
3. Create Remediation Actions
        ↓
4. Track Progress & Status
        ↓
5. Update Completion Percentage
        ↓
6. Mark Complete & Archive
        ↓
7. Generate Remediation Report
```

**Usage:**
```python
# Identify gaps
gaps = coordinator.identify_compliance_gaps(
    framework="GDPR",
    current_state={
        "data_protection": "partial",
        "dpia": "none",
        "incident_response": "non_compliant",
    },
    required_state={
        "data_protection": "compliant",
        "dpia": "compliant",
        "incident_response": "compliant",
    },
)

# Automatically creates remediation actions for critical gaps
for gap in gaps:
    if gap["severity"] == "critical":
        action = coordinator.create_remediation_action(
            gap_id=gap["gap_id"],
            action_title=f"Fix: {gap['requirement']}",
            description=gap["recommendation"],
            priority=10,
            due_date=datetime.utcnow() + timedelta(days=90),
        )
        
        # Track progress
        coordinator.update_remediation_status(
            action_id=action["id"],
            status="in_progress",
            completion_percentage=25.0,
        )
```

### Workflow 4: Real-Time Event Processing

```
1. Monitor starts background monitoring thread
        ↓
2. Polls system state every N seconds
        ↓
3. Detects changes (new alerts, score changes, etc.)
        ↓
4. Generates SystemEvent
        ↓
5. Emits to:
   - Event queue (for polling)
   - Registered callbacks (for real-time)
   - Event history (for querying)
        ↓
6. Dashboard polls or listens to WebSocket
        ↓
7. Updates UI in real-time
```

**Usage:**
```python
# Register for real-time events
def on_critical_alert(event):
    print(f"Critical alert: {event.data}")

coordinator.register_event_callback(
    "alert_triggered",
    on_critical_alert,
)

# Get recent events
recent = coordinator.get_recent_events(count=20)
for event in recent:
    print(f"{event.event_type}: {event.data}")

# Get event history
history = coordinator.get_event_history(event_type="threshold_breach")
```

### Workflow 5: Reporting & Compliance Assessment

```
1. Generate Compliance Report
        ↓
2. Collect:
   - Recent regulatory changes
   - Open and critical alerts
   - Pending remediation actions
   - System statistics
        ↓
3. Calculate metrics:
   - Compliance percentage
   - Average framework score
   - Remediation progress
        ↓
4. Export in JSON/PDF
        ↓
5. Distribute to stakeholders
```

**Usage:**
```python
# Generate comprehensive report
report = coordinator.get_compliance_report(system_name="authentication")

print(f"Report generated: {report['generated_at']}")
print(f"Recent changes: {len(report['changes'])}")
print(f"Open alerts: {len(report['alerts']['open'])}")
print(f"Critical alerts: {len(report['alerts']['critical'])}")
print(f"Pending remediations: {len(report['remediation']['pending'])}")
print(f"Overdue actions: {len(report['remediation']['overdue'])}")

# Export data
json_export = coordinator.export_compliance_data(format="json")
with open("compliance_report.json", "w") as f:
    f.write(json_export)
```

## Integration Patterns

### Pattern 1: Standalone Coordinator Usage

```python
from scripts.system_integration import SystemCoordinator

# Initialize
coordinator = SystemCoordinator(
    db_url="sqlite:///compliance.db",
    monitor_interval=60,
)
coordinator.initialize()
coordinator.start_monitoring()

# Use throughout application
coordinator.track_regulatory_change(...)
coordinator.record_compliance_score(...)
coordinator.generate_alert(...)

# Cleanup
coordinator.shutdown()
```

### Pattern 2: Global Coordinator Instance

```python
from scripts.system_integration import get_coordinator, initialize_coordinator

# Initialize once at startup
coordinator = initialize_coordinator(
    db_url="sqlite:///compliance.db",
    monitor_interval=60,
    start_monitoring=True,
)

# Get instance anywhere in code
coordinator = get_coordinator()

# Use normally
coordinator.track_regulatory_change(...)
```

### Pattern 3: Dashboard Integration

```python
import streamlit as st
from scripts.system_integration import get_coordinator
from dashboard.enhanced_ui_components import render_metric_card

@st.cache_resource
def init_system():
    return get_coordinator()

coordinator = init_system()

# Display live metrics
col1, col2, col3 = st.columns(3)

with col1:
    status = coordinator.get_system_status()
    render_metric_card(
        title="Active Alerts",
        value=status["open_alerts"],
        unit="alerts",
    )

# Real-time updates
st.write("### Recent Events")
for event in coordinator.get_recent_events(10):
    st.write(f"**{event['event_type']}** - {event['timestamp']}")

# Refresh automatically
st.session_state.last_update = st.session_state.get('last_update', 0)
if st.session_state.get('auto_refresh', True):
    st.rerun()
```

### Pattern 4: Scheduled Tasks

```python
import schedule
from scripts.system_integration import get_coordinator

coordinator = get_coordinator()

def daily_compliance_check():
    """Run daily compliance check."""
    for framework in ["GDPR", "HIPAA", "SOC2"]:
        score = check_framework_compliance(framework)
        coordinator.record_compliance_score(framework, "all_systems", score)

def weekly_report():
    """Generate weekly compliance report."""
    report = coordinator.get_compliance_report()
    export_report(report, f"report_{datetime.now().date()}.json")

# Schedule tasks
schedule.every().day.at("02:00").do(daily_compliance_check)
schedule.every().monday.at("09:00").do(weekly_report)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Pattern 5: API Integration (FastAPI)

```python
from fastapi import FastAPI
from scripts.system_integration import get_coordinator

app = FastAPI()
coordinator = get_coordinator()

@app.get("/api/status")
def get_status():
    """Get system status."""
    return coordinator.get_system_status()

@app.get("/api/alerts")
def get_alerts():
    """Get open alerts."""
    return {"alerts": coordinator.get_open_alerts()}

@app.get("/api/report")
def get_report():
    """Get compliance report."""
    return coordinator.get_compliance_report()

@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str):
    """Acknowledge an alert."""
    return coordinator.acknowledge_alert(alert_id)
```

## Database Schema

### RegulatoryChange Table
```
- id: UUID (primary key)
- source: String (where the change came from)
- regulation_id: String (unique identifier)
- regulation_name: String
- change_type: Enum (new_requirement, update, deprecation)
- description: Text
- impact_level: Enum (critical, high, medium, low, info)
- affected_systems: JSON list
- implementation_deadline: DateTime
- created_at: DateTime
- updated_at: DateTime
- is_critical: Boolean
```

### ComplianceScore Table
```
- id: UUID
- framework: String (GDPR, HIPAA, SOC2, etc.)
- system_name: String
- score: Float (0-100)
- status: Enum (compliant, partial, non_compliant, unknown)
- recorded_at: DateTime
```

### ComplianceAlert Table
```
- id: UUID
- alert_type: String
- affected_regulation: String
- message: Text
- recommended_action: Text
- risk_level: Enum (critical, high, medium, low, info)
- status: Enum (open, acknowledged, resolved, dismissed)
- regulatory_change_id: FK (RegulatoryChange)
- created_at, acknowledged_at, resolved_at: DateTime
```

### RemediationAction Table
```
- id: UUID
- gap_id: String
- action_title: String
- description: Text
- assigned_to: String
- status: Enum (pending, in_progress, blocked, completed, cancelled)
- priority: Integer (0-10)
- completion_percentage: Float (0-100)
- due_date: DateTime
- started_at, completed_at: DateTime
- created_at, updated_at: DateTime
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///compliance.db
# or PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/compliance

# Monitoring
MONITOR_INTERVAL=60  # seconds between checks
MONITOR_ENABLED=true

# Alert Thresholds
COMPLIANCE_THRESHOLD_WARNING=80
COMPLIANCE_THRESHOLD_CRITICAL=70
MAX_CRITICAL_ALERTS=5

# Persistence
CACHE_TTL_HOURS=24
MAX_EVENT_HISTORY=1000
```

### Configuration File (config.yaml)

```yaml
database:
  url: sqlite:///compliance.db
  echo: false
  pool_size: 5

monitoring:
  enabled: true
  interval_seconds: 60
  event_history_size: 1000

thresholds:
  compliance_warning: 80
  compliance_critical: 70
  critical_alert_count: 5

alerts:
  enabled: true
  channels:
    - email
    - slack
    - webhook

reporting:
  enabled: true
  schedule: "0 9 * * MON"  # Weekly Monday 9am
  formats:
    - json
    - pdf
```

## Deployment

### Development

```bash
# SQLite database (file-based, no setup needed)
python
>>> from scripts.system_integration import initialize_coordinator
>>> coordinator = initialize_coordinator(start_monitoring=True)
>>> coordinator.track_regulatory_change(...)
```

### Production

```bash
# PostgreSQL database (requires PostgreSQL)
export DATABASE_URL="postgresql://user:password@db.example.com/compliance"

# Initialize
python scripts/setup_database.py

# Run coordinator in background
python -m scripts.run_system_integration
```

### Docker

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "scripts.run_system_integration"]
```

## Monitoring & Observability

### Logging

```python
import logging

logger = logging.getLogger("system_integration")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/system_integration.log")
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Metrics

Key metrics to monitor:

1. **Compliance Scores**
   - Current vs. historical
   - Trend direction
   - Forecasted values

2. **Alert Metrics**
   - Total alerts
   - Critical alerts
   - Alert resolution time

3. **Remediation Metrics**
   - Total actions
   - Completion rate
   - Overdue count

4. **System Metrics**
   - Processing time
   - Database size
   - Event queue depth

### Health Checks

```python
# System health endpoint
@app.get("/health")
def health_check():
    coordinator = get_coordinator()
    status = coordinator.get_system_status()
    
    return {
        "status": "healthy" if status["monitoring"] else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "ok",
            "monitor": "ok" if status["monitoring"] else "degraded",
            "api": "ok" if status.get("api") else "error",
        },
    }
```

## Troubleshooting

### Issue: Database Connection Errors

**Symptom:** "database locked" or connection timeouts

**Solution:**
```python
# Use WAL mode for SQLite (supports concurrent access)
DATABASE_URL = "sqlite:///compliance.db?timeout=10&check_same_thread=False&journal_mode=WAL"
```

### Issue: Monitoring Not Detecting Changes

**Symptom:** Real-time events not appearing

**Solution:**
```python
# Check if monitoring is running
coordinator = get_coordinator()
status = coordinator.get_system_status()
print(f"Monitoring: {status['monitoring']}")

# Restart monitoring
coordinator.stop_monitoring()
coordinator.start_monitoring()
```

### Issue: Performance Degradation

**Symptom:** Slow dashboard loads, high CPU

**Solution:**
```python
# Reduce event history
monitor = coordinator.monitor
monitor.event_history = deque(maxlen=100)  # Reduce from 1000

# Increase monitoring interval
coordinator.monitor_interval = 300  # Check every 5 minutes instead of 1
```

## Next Steps

1. **Deploy Database:** Set up persistent database (SQLite or PostgreSQL)
2. **Configure Alerts:** Set up email/Slack notifications
3. **Schedule Tasks:** Configure daily compliance checks
4. **Dashboard Integration:** Add real-time components to dashboard
5. **API Endpoints:** Create REST API for external integrations
6. **Backup Strategy:** Set up database backups
7. **Monitoring:** Deploy monitoring and alerting

## Support & Documentation

- **API Reference:** See docstrings in each module
- **Examples:** See test files for usage patterns
- **Architecture:** See system diagram at top of this guide
- **Workflows:** See workflow sections above
