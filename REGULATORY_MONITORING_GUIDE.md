# Real-Time Regulatory Monitoring System

## Overview

This system continuously monitors healthcare regulations (GDPR, HIPAA, EU AI Act, etc.) for real-time changes and automatically updates your IRAQAF compliance assessment. It uses:

- **Web Scraping**: Extract regulation text from official sources
- **RSS/API Integration**: Fetch updates from regulatory databases
- **NLP-Based Change Detection**: Identify meaningful changes semantically
- **IRAQAF Sync**: Automatically update compliance traces and trigger re-evaluations
- **Background Scheduling**: Continuous monitoring (hourly, daily, weekly)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Regulatory Sources                        │
│  GDPR EU Journal │ HIPAA HHS.gov │ EU AI Act Portal        │
└────────────┬────────────────────┬──────────────┬────────────┘
             │                    │              │
             ▼                    ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│              Monitoring Layer (Background Task)              │
│  • Web Scraper (BeautifulSoup/Selenium)                     │
│  • API Integrations (Federal Register, EUR-Lex)             │
│  • RSS/Atom Feed Parsers                                    │
│  • NLP Change Detector (spaCy/Transformers)                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│         Change Detection & Version Control                   │
│  • Diff algorithm (clause-by-clause comparison)             │
│  • Semantic similarity (embeddings)                         │
│  • Version tracking (Git-like for regulations)              │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│              IRAQAF Integration Layer                        │
│  • Update trace_map.yaml automatically                      │
│  • Trigger re-evaluation of affected modules                │
│  • Generate compliance delta reports                        │
│  • Alert dashboard users                                    │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements-regulatory.txt
```

### 2. Configure Monitoring Sources

Edit `configs/regulatory_sources.yaml`:

```yaml
monitoring_schedule:
  type: daily
  hour: 2  # 2 AM UTC

regulatory_sources:
  gdpr:
    enabled: true
    type: rss
    url: "https://eur-lex.europa.eu/rss/oj-l-all.xml"
  
  hipaa:
    enabled: true
    type: api
    url: "https://www.hhs.gov/hipaa/"
```

### 3. Start Monitoring Service

**Option A: Scheduled Background Service**
```bash
python scripts/regulatory_scheduler.py --schedule daily --hour 2
```

**Option B: One-Time Manual Check**
```bash
python scripts/regulatory_monitor.py
```

**Option C: Local Testing**
```bash
python scripts/regulatory_monitor.py --test --sources GDPR,HIPAA
```

### 4. Monitor for Changes

Changes are automatically:
- ✅ Detected using NLP semantic similarity
- ✅ Saved to `regulatory_data/detected_changes.json`
- ✅ Synced to IRAQAF trace_map
- ✅ Displayed in Streamlit dashboard
- ✅ Exported as compliance delta reports

## Components

### 1. Regulatory Monitor (`scripts/regulatory_monitor.py`)

Fetches regulation updates from multiple sources:

- **RegulatorySource**: Base class for data sources
- **WebScraperSource**: HTML scraping with BeautifulSoup
- **APISource**: Structured API endpoints
- **RSSSource**: RSS/Atom feed parsing
- **RegulatoryMonitor**: Main orchestrator

**Usage:**
```python
from regulatory_monitor import RegulatoryMonitor, RSSSource

monitor = RegulatoryMonitor()
monitor.register_source(RSSSource('GDPR', 'https://eur-lex.europa.eu/rss/oj-l-all.xml'))

documents = monitor.fetch_all()
changes = monitor.detect_changes()
```

### 2. NLP Change Detector (`scripts/nlp_change_detector.py`)

Analyzes semantic changes using TF-IDF and cosine similarity:

- **NLPChangeDetector**: Detect clause-level changes
- **ChangeTracker**: Historical change tracking
- **Severity Classification**: CRITICAL/HIGH/MEDIUM/LOW

**Usage:**
```python
from nlp_change_detector import NLPChangeDetector

detector = NLPChangeDetector(similarity_threshold=0.75)

changes = detector.detect_clause_changes(old_text, new_text)
severity = detector.classify_severity(changes)
summary = detector.generate_summary(regulation, changes)
```

### 3. IRAQAF Sync (`scripts/iraqaf_regulatory_sync.py`)

Automatically updates IRAQAF trace_map based on regulatory changes:

- **IRQAFRegulatorySync**: Sync to trace_map.yaml
- **RegulatoryComplianceDelta**: Generate impact reports
- **Module Mapping**: Link regulations to L1-L5 modules

**Usage:**
```python
from iraqaf_regulatory_sync import IRQAFRegulatorySync

sync = IRQAFRegulatorySync()
sync.update_module_due_to_regulation('GDPR', changes)
report = sync.generate_sync_report(changes)
```

### 4. Regulatory Scheduler (`scripts/regulatory_scheduler.py`)

Background task scheduler using APScheduler:

- **Hourly checks**: Run every hour
- **Daily checks**: Run at specified time (e.g., 2 AM UTC)
- **Weekly checks**: Run on specific day/time
- **Custom cron**: Custom schedule expressions

**Usage:**
```python
from regulatory_scheduler import RegulatoryMonitoringScheduler

scheduler = RegulatoryMonitoringScheduler()
scheduler.schedule_daily_check(hour=2)
scheduler.schedule_weekly_check('monday', hour=9)
scheduler.start()
```

## Configuration

### `configs/regulatory_sources.yaml`

Main configuration file:

```yaml
# Monitoring schedule
monitoring_schedule:
  type: daily
  hour: 2
  timezone: UTC

# Registered data sources
regulatory_sources:
  gdpr:
    enabled: true
    type: rss
    url: "..."
    mapping:
      modules: ["L1-Governance", "L2-Privacy"]

# NLP settings
nlp_settings:
  similarity_threshold: 0.75
  severity_thresholds:
    critical: 0.50
    high: 0.70
    medium: 0.85

# IRAQAF sync settings
iraqaf_sync:
  auto_update_trace_map: true
  generate_impact_reports: true
  dashboard_alerts: true

# Notifications
notifications:
  alert_on_new: true
  min_severity: "MEDIUM"
  methods:
    dashboard: true
    slack:
      enabled: false
    email:
      enabled: false
```

## Monitoring Workflows

### Workflow 1: Automated Hourly Monitoring

```bash
# Start continuous monitoring every hour
python scripts/regulatory_scheduler.py --schedule hourly

# Monitoring automatically:
# 1. Fetches updates from all sources
# 2. Detects changes using NLP
# 3. Syncs to IRAQAF trace_map
# 4. Generates delta reports
# 5. Alerts dashboard
```

### Workflow 2: Manual Compliance Review

```bash
# One-time check
python scripts/regulatory_monitor.py

# Outputs:
# • regulatory_data/regulations_cache.json
# • regulatory_data/detected_changes.json
# • regulatory_data/change_history.json
# • regulatory_data/impact_*.txt
```

### Workflow 3: Change Analysis Only

```python
from nlp_change_detector import NLPChangeDetector

detector = NLPChangeDetector()

# Detect clause-level changes
changes = detector.detect_clause_changes(old_gdpr_text, new_gdpr_text)

# Generate summary
summary = detector.generate_summary({'title': 'GDPR Article 4'}, changes)

# Get severity
severity = detector.classify_severity(changes)
# Output: CRITICAL, HIGH, MEDIUM, or LOW
```

## Supported Regulatory Sources

### GDPR (EU General Data Protection Regulation)
- **Source**: EU Official Journal (EUR-Lex)
- **Type**: RSS Feed
- **Update Frequency**: Daily
- **Maps to**: L1-Governance, L2-Privacy

### HIPAA (Health Insurance Portability and Accountability Act)
- **Source**: HHS.gov
- **Type**: Web Scraping / API
- **Update Frequency**: 48 hours
- **Maps to**: L2-Privacy, L5-Operations

### EU AI Act
- **Source**: EUR-Lex
- **Type**: RSS Feed
- **Update Frequency**: 48 hours
- **Maps to**: L3-Fairness, L4-Explainability, L1-Governance

### SOC2 (Service Organization Control)
- **Source**: AICPA-CIMA
- **Type**: Web Scraping
- **Update Frequency**: Weekly
- **Maps to**: L1-Governance, L5-Operations

### CCPA (California Consumer Privacy Act)
- **Source**: California Attorney General
- **Type**: RSS Feed
- **Update Frequency**: Weekly
- **Maps to**: L1-Governance, L2-Privacy

## Alert Severity Levels

### 🔴 CRITICAL
- Similarity < 50%
- Major structural changes
- New compliance requirements added
- **Action**: Immediate review and assessment required

### 🟠 HIGH
- Similarity < 70%
- Significant clause modifications
- Multiple affected modules
- **Action**: Review and update within 48 hours

### 🟡 MEDIUM
- Similarity < 85%
- 2-3 modified clauses
- Minor requirement changes
- **Action**: Review and plan updates within 1 week

### 🟢 LOW
- Similarity < 95%
- Editorial or clarification changes
- 1 modified clause
- **Action**: Document and include in next review cycle

## Output Files

### `regulatory_data/regulations_cache.json`
```json
{
  "timestamp": "2025-11-16T02:00:00",
  "documents": {
    "GDPR-Official": [
      {
        "title": "GDPR Article Update",
        "date": "2025-11-16",
        "content": "Updated requirements...",
        "url": "https://...",
        "source": "GDPR-Official"
      }
    ]
  }
}
```

### `regulatory_data/detected_changes.json`
```json
{
  "timestamp": "2025-11-16T02:00:00",
  "new_regulations": [],
  "updated_regulations": [
    {
      "doc": {...},
      "previous_content": "...",
      "new_content": "..."
    }
  ],
  "affected_modules": ["L1-Governance", "L2-Privacy"]
}
```

### `regulatory_data/change_history.json`
```json
{
  "GDPR-Article-4": [
    {
      "timestamp": "2025-11-16T02:00:00",
      "similarity_score": 0.92,
      "added_clauses": [...],
      "modified_clauses": [...]
    }
  ]
}
```

### `regulatory_data/impact_*.txt`
```
╔════════════════════════════════════════════════════════════════════╗
║    COMPLIANCE IMPACT REPORT: GDPR
╚════════════════════════════════════════════════════════════════════╝

📅 Generated: 2025-11-16T02:00:00
🏛️  REGULATION: GDPR
📊 CHANGE SEVERITY: 🟡 MEDIUM

AFFECTED MODULES:
  • L1-Governance
  • L2-Privacy

⚠️  NEW REQUIREMENTS:
      Your organization may need to implement new controls to meet:
      • Enhanced data minimization requirements
      • Biometric data protection measures

ACTION ITEMS:
  1. Review the full regulation text
  2. Assess current compliance controls
  ...
```

## Integration with Dashboard

Add to `app.py` to show regulatory alerts:

```python
import streamlit as st
import json
from pathlib import Path

# Load regulatory alerts
alerts_file = Path('regulatory_data/detected_changes.json')
if alerts_file.exists():
    with open(alerts_file) as f:
        alerts = json.load(f)
    
    if alerts['new_regulations'] or alerts['updated_regulations']:
        st.warning("⚠️ Regulatory Changes Detected")
        st.expander("📋 View Regulatory Updates").write(alerts)
```

## Troubleshooting

### Problem: "SSL: Certificate Verify Failed"

```bash
# Disable SSL verification (development only):
export PYTHONHTTPSVERIFY=0
```

Or in Python:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

### Problem: "Rate Limited"

Adjust in `regulatory_sources.yaml`:
```yaml
rate_limiting:
  request_delay: 5  # Increase delay
  max_concurrent: 1  # Reduce parallel requests
```

### Problem: "No Changes Detected"

1. Check `regulatory_data/regulations_cache.json` exists
2. Compare similarity threshold: lower = more sensitive
3. Check NLP detector is working:
   ```bash
   python scripts/nlp_change_detector.py
   ```

### Problem: IRAQAF Not Updated

1. Verify `trace_map.yaml` path in `iraqaf_regulatory_sync.py`
2. Check trace_map permissions (must be writable)
3. Enable auto-update in config:
   ```yaml
   iraqaf_sync:
     auto_update_trace_map: true
   ```

## Best Practices

### ✅ DO:
- Run hourly or daily checks (depending on risk tolerance)
- Review alerts at specified severity levels
- Track compliance deltas automatically
- Archive historical changes for audit trail
- Test new regulations in staging before production

### ❌ DON'T:
- Skip manual review of CRITICAL changes
- Auto-apply changes without validation
- Disable alerts permanently
- Store API credentials in config files (use env vars)
- Monitor too frequently (hourly max recommended)

## Advanced Usage

### Custom Regulatory Source

```python
from regulatory_monitor import RegulatorySource

class CustomAPISource(RegulatorySource):
    def __init__(self, name: str, api_url: str):
        super().__init__(name, 'api', api_url)
    
    def fetch(self) -> str:
        # Custom fetch logic
        return api_response_text
    
    def parse(self, content: str) -> List[Dict]:
        # Custom parsing logic
        return parsed_documents

# Register and use
monitor.register_source(CustomAPISource('MySource', 'https://api.example.com'))
```

### Custom Change Detector

```python
from nlp_change_detector import NLPChangeDetector

class CustomDetector(NLPChangeDetector):
    def classify_severity(self, changes: Dict) -> str:
        # Custom severity logic
        return 'CRITICAL'
```

## Resources

- [GDPR EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- [HIPAA HHS](https://www.hhs.gov/hipaa/)
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [SOC2 Standards](https://www.aicpa-cima.com/topic/service-organization-control-soc-2)
- [CCPA California](https://oag.ca.gov/privacy/ccpa)

---

**Created**: November 16, 2025  
**Status**: Production Ready  
**Maintenance**: Ongoing
