# System Integration Deployment & Configuration

## Pre-Deployment Checklist

- [ ] Database selected (SQLite or PostgreSQL)
- [ ] Dependencies installed (sqlalchemy, etc.)
- [ ] Environment variables configured
- [ ] Dashboard app.py updated with imports
- [ ] Real-time monitoring intervals configured
- [ ] Alert thresholds set appropriately
- [ ] Logging configured
- [ ] Backup strategy planned

## Database Setup

### SQLite (Development/Small Deployments)

No setup required. Database is created automatically:

```python
from scripts.system_integration import initialize_coordinator

coordinator = initialize_coordinator(
    db_url="sqlite:///compliance.db"
)
```

Files created:
- `compliance.db` - Main database file
- `compliance.db-shm` - Shared memory for concurrency
- `compliance.db-wal` - Write-ahead log for durability

### PostgreSQL (Production)

**Installation:**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Or use Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=compliance \
  -e POSTGRES_DB=compliance \
  -p 5432:5432 \
  postgres:15
```

**Setup:**

```bash
# Connect to PostgreSQL
psql -U compliance -d compliance -h localhost

# Create database and user (if not already done)
CREATE USER compliance WITH PASSWORD 'your_secure_password';
CREATE DATABASE compliance OWNER compliance;
```

**Python Configuration:**

```python
from scripts.system_integration import initialize_coordinator

coordinator = initialize_coordinator(
    db_url="postgresql://compliance:password@localhost:5432/compliance"
)
```

**Connection Pool Settings:**

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:password@localhost/compliance",
    pool_size=10,  # Connections to keep in pool
    max_overflow=20,  # Additional connections when pool full
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Test connections before use
)
```

## Environment Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=sqlite:///compliance.db
# or
# DATABASE_URL=postgresql://user:password@localhost:5432/compliance

# Monitoring
MONITOR_INTERVAL=60
MONITOR_ENABLED=true
MONITOR_EVENT_HISTORY_SIZE=1000

# Alert Thresholds
COMPLIANCE_THRESHOLD_WARNING=80
COMPLIANCE_THRESHOLD_CRITICAL=70
MAX_CRITICAL_ALERTS=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/system_integration.log

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Notifications
ENABLE_EMAIL_ALERTS=false
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM_ADDRESS=compliance@company.com

ENABLE_SLACK_ALERTS=false
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Features
FEATURE_REGULATORY_MONITORING=true
FEATURE_COMPLIANCE_CHECKING=true
FEATURE_REMEDIATION_TRACKING=true
FEATURE_REAL_TIME_UPDATES=true
```

Load configuration:

```python
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "database_url": os.getenv("DATABASE_URL", "sqlite:///compliance.db"),
    "monitor_interval": int(os.getenv("MONITOR_INTERVAL", "60")),
    "monitor_enabled": os.getenv("MONITOR_ENABLED", "true").lower() == "true",
    "compliance_threshold_warning": int(os.getenv("COMPLIANCE_THRESHOLD_WARNING", "80")),
    "compliance_threshold_critical": int(os.getenv("COMPLIANCE_THRESHOLD_CRITICAL", "70")),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "log_file": os.getenv("LOG_FILE", "logs/system_integration.log"),
}
```

### YAML Configuration

Create `config/system_integration.yaml`:

```yaml
database:
  url: ${DATABASE_URL}
  echo: false
  pool_size: 5
  max_overflow: 10
  pool_recycle: 3600

monitoring:
  enabled: true
  interval_seconds: 60
  event_history_size: 1000
  
  # State change detection
  detect_changes: true
  
  # Threshold checking
  check_thresholds: true
  
  # Thread settings
  daemon_thread: true

thresholds:
  compliance:
    warning: 80
    critical: 70
  alerts:
    max_critical: 5
    max_open: 50
  
remediation:
  # Auto-create remediations for critical gaps
  auto_create: true
  auto_create_priority: 10
  
  # Check for overdue actions
  check_overdue: true
  overdue_warning_days: 3

logging:
  level: INFO
  file: logs/system_integration.log
  max_bytes: 10485760  # 10MB
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

alerts:
  enabled: true
  
  channels:
    email:
      enabled: false
      smtp_server: smtp.gmail.com
      smtp_port: 587
      from_address: compliance@company.com
    
    slack:
      enabled: false
      webhook_url: ${SLACK_WEBHOOK_URL}
    
    webhook:
      enabled: false
      url: https://api.company.com/alerts
  
  # Alert rules
  rules:
    - event_type: threshold_breach
      channel: email
      severity: high
    
    - event_type: regulatory_change
      channel: slack
      severity: medium
    
    - event_type: alert_triggered
      channel: email
      severity: critical

reporting:
  enabled: true
  
  # Automatic report generation
  schedule: "0 9 * * MON"  # Cron format: Weekly Monday 9am
  
  formats:
    - json
    - csv
    - pdf
  
  # Report recipients
  recipients:
    - compliance-team@company.com
  
  # Report retention
  retention_days: 365

features:
  regulatory_monitoring: true
  compliance_checking: true
  remediation_tracking: true
  real_time_updates: true
  event_streaming: false
```

Load YAML configuration:

```python
import yaml

def load_config(config_file="config/system_integration.yaml"):
    with open(config_file) as f:
        return yaml.safe_load(f)

config = load_config()
```

## Logging Configuration

```python
import logging
import logging.handlers
from pathlib import Path

def setup_logging(config):
    """Set up logging based on configuration."""
    
    # Create logs directory
    log_dir = Path(config['logging']['file']).parent
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("system_integration")
    logger.setLevel(getattr(logging, config['logging']['level']))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        config['logging']['file'],
        maxBytes=config['logging']['max_bytes'],
        backupCount=config['logging']['backup_count'],
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(config['logging']['format'])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## Dashboard Integration

### Update dashboard app.py

Add to imports:

```python
from scripts.system_integration import get_coordinator, initialize_coordinator
from scripts.realtime_monitor import EventType
```

Add initialization:

```python
@st.cache_resource
def init_compliance_system():
    """Initialize compliance system once."""
    coordinator = initialize_coordinator(
        db_url=st.secrets.get("DATABASE_URL", "sqlite:///compliance.db"),
        monitor_interval=60,
        start_monitoring=True,
    )
    return coordinator

# Initialize system
coordinator = init_compliance_system()
```

Add dashboard pages:

```
dashboard/
├── pages/
│   ├── 01_🔍_regulatory_monitoring.py
│   ├── 02_📊_compliance_dashboard.py
│   ├── 03_⚠️_alerts_management.py
│   └── 04_🔧_remediation_tracker.py
```

**Example page: 01_regulatory_monitoring.py**

```python
import streamlit as st
from scripts.system_integration import get_coordinator

st.set_page_config(page_title="Regulatory Monitoring", layout="wide")

coordinator = get_coordinator()

st.title("🔍 Regulatory Change Monitoring")

col1, col2, col3 = st.columns(3)

with col1:
    changes = coordinator.get_recent_changes(days=30)
    st.metric("Recent Changes", len(changes))

with col2:
    critical = coordinator.get_critical_changes()
    st.metric("Critical Changes", len(critical))

with col3:
    status = coordinator.get_system_status()
    st.metric("Last Update", status.get("timestamp", "N/A"))

st.subheader("Recent Regulatory Changes")
for change in coordinator.get_recent_changes(days=30):
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{change['regulation_name']}**")
            st.caption(change['description'])
        with col2:
            st.write(change['impact_level'].upper())
```

## API Server Setup (FastAPI)

Create `scripts/api_server.py`:

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from scripts.system_integration import initialize_coordinator

app = FastAPI(title="Compliance API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize coordinator
coordinator = initialize_coordinator(start_monitoring=True)

@app.get("/status")
def get_status():
    return coordinator.get_system_status()

@app.get("/alerts")
def get_alerts():
    return {
        "open": coordinator.get_open_alerts(),
        "critical": coordinator.get_critical_alerts(),
    }

@app.get("/report")
def get_report(system_name: str = None):
    return coordinator.get_compliance_report(system_name)

@app.on_event("shutdown")
def shutdown():
    coordinator.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run API:

```bash
python scripts/api_server.py
# or
python -m uvicorn scripts.api_server:app --reload --port 8000
```

## Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgresql://user:password@postgres:5432/compliance

# Create logs directory
RUN mkdir -p logs

# Run dashboard
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py"]
```

**docker-compose.yaml:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: compliance
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: compliance
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://compliance:secure_password@postgres:5432/compliance
      MONITOR_INTERVAL: 60
    ports:
      - "8501:8501"
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs

  api:
    build: .
    command: python -m uvicorn scripts.api_server:app --host 0.0.0.0
    environment:
      DATABASE_URL: postgresql://compliance:secure_password@postgres:5432/compliance
    ports:
      - "8000:8000"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
```

## Monitoring & Maintenance

### Health Checks

```python
@app.get("/health")
def health_check():
    coordinator = get_coordinator()
    status = coordinator.get_system_status()
    
    return {
        "status": "healthy" if status["monitoring"] else "degraded",
        "database": "ok",
        "monitor": "ok" if status["monitoring"] else "error",
        "uptime": status.get("monitor_stats", {}).get("uptime_seconds", 0),
    }
```

### Database Maintenance

```python
# Daily cleanup
import schedule

def cleanup_old_data():
    """Remove data older than 1 year."""
    from datetime import timedelta, datetime
    from scripts.database_layer import get_db_session, ComplianceScore
    
    cutoff = datetime.utcnow() - timedelta(days=365)
    
    with get_db_session() as session:
        deleted = session.query(ComplianceScore).filter(
            ComplianceScore.recorded_at < cutoff
        ).delete()
        print(f"Deleted {deleted} old records")

schedule.every().day.at("03:00").do(cleanup_old_data)
```

## Backup Strategy

### Database Backup

```bash
# PostgreSQL backup
pg_dump compliance > backup_$(date +%Y%m%d).sql

# SQLite backup
cp compliance.db compliance_$(date +%Y%m%d).db
```

### Automated Backup

```python
import subprocess
from datetime import datetime

def backup_database(db_type="sqlite"):
    """Backup database based on type."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if db_type == "sqlite":
        subprocess.run([
            "cp",
            "compliance.db",
            f"backups/compliance_{timestamp}.db"
        ])
    
    elif db_type == "postgresql":
        subprocess.run([
            "pg_dump",
            "-U", "compliance",
            "-d", "compliance",
            "-f", f"backups/compliance_{timestamp}.sql"
        ])

schedule.every().day.at("02:00").do(backup_database, db_type="postgresql")
```

## Performance Tuning

### Database Indexes

```python
from sqlalchemy import Index

# Add indexes for common queries
Index('idx_regulatory_change_created', RegulatoryChange.created_at)
Index('idx_compliance_score_framework', ComplianceScore.framework)
Index('idx_alert_status', ComplianceAlert.status)
Index('idx_remediation_status', RemediationAction.status)
```

### Query Optimization

```python
# Use pagination for large result sets
from sqlalchemy import desc

def get_alerts_paginated(page: int = 1, page_size: int = 50):
    with get_db_session() as session:
        return session.query(ComplianceAlert)\
            .order_by(desc(ComplianceAlert.created_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
```

## Scaling Considerations

### For Small Deployments (< 100K records)
- SQLite is sufficient
- Single monitoring thread
- In-memory event cache
- Update interval: 60 seconds

### For Medium Deployments (100K - 1M records)
- PostgreSQL recommended
- Consider connection pooling
- Implement data retention policy
- Update interval: 300 seconds

### For Large Deployments (> 1M records)
- PostgreSQL with replication
- Message queue for events (Redis/RabbitMQ)
- Separate monitoring service
- Time-series database for scores
- Update interval: 600 seconds

## Troubleshooting

### Database Connection Issues

```python
# Test connection
from scripts.database_layer import init_db

try:
    init_db("postgresql://user:password@localhost/compliance")
    print("✓ Connection successful")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Monitoring Not Working

```python
# Check monitoring status
coordinator = get_coordinator()
status = coordinator.get_system_status()
print(f"Monitoring: {status['monitoring']}")

# Restart monitoring
coordinator.stop_monitoring()
coordinator.start_monitoring()
```

### High Memory Usage

```python
# Reduce event history size
coordinator.monitor.event_history = deque(maxlen=100)

# Increase monitoring interval
coordinator.monitor_interval = 600  # 10 minutes
```

## Support & Documentation

- `SYSTEM_INTEGRATION_GUIDE.md` - Architecture and workflows
- `SYSTEM_INTEGRATION_QUICKSTART.md` - Usage examples
- Module docstrings - API reference
- `test_system_integration.py` - Test examples
