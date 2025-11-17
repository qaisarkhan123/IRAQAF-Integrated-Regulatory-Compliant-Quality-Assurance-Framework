# Real-Time Regulatory Monitoring - Quick Start

**5-Minute Setup for Continuous Compliance Monitoring**

## What This Does

Automatically monitors healthcare regulations (GDPR, HIPAA, EU AI Act, etc.) and alerts you instantly when they change. Uses AI to detect meaningful changes and automatically updates your IRAQAF compliance assessment.

```
Regulation Changes Detected
         ↓
NLP Analysis (Semantic Similarity)
         ↓
IRAQAF Trace Map Updated
         ↓
Dashboard Alerts & Reports
         ↓
You Review & Act
```

## Installation (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements-regulatory.txt

# 2. Verify installation
python scripts/regulatory_monitor.py --test
```

## Configuration (1 minute)

Edit `configs/regulatory_sources.yaml`:

```yaml
monitoring_schedule:
  type: daily        # hourly, daily, weekly, or custom_cron
  hour: 2           # 2 AM UTC (change as needed)
  timezone: UTC

regulatory_sources:
  gdpr:
    enabled: true
  hipaa:
    enabled: true
  eu_ai_act:
    enabled: true
```

## Start Monitoring (1 minute)

### Option 1: Background Service (Recommended)
```bash
# Start monitoring scheduler
python scripts/regulatory_scheduler.py --schedule daily --hour 2
```

### Option 2: Manual Check
```bash
# Run once
python scripts/regulatory_monitor.py
```

### Option 3: Test Locally
```bash
# Test without saving
python scripts/regulatory_monitor.py --dry-run
```

## What Happens Automatically

✅ **Every day at 2 AM UTC:**

1. **Monitor Sources**
   - Fetches GDPR updates from EUR-Lex
   - Checks HIPAA updates from HHS
   - Retrieves EU AI Act changes

2. **Detect Changes**
   - Compares old vs new text
   - Uses NLP semantic similarity
   - Classifies severity (CRITICAL/HIGH/MEDIUM/LOW)

3. **Update IRAQAF**
   - Syncs to trace_map.yaml
   - Marks modules for review
   - Triggers compliance assessment

4. **Generate Reports**
   - Impact analysis per regulation
   - Compliance delta reports
   - Historical tracking

5. **Alert You**
   - Dashboard shows alerts
   - Slack notifications (optional)
   - Email summaries (optional)

## View Results

### In Streamlit Dashboard
```python
# Add to app.py:
from scripts.dashboard_regulatory_integration import display_regulatory_alerts

display_regulatory_alerts()
```

### Command Line
```bash
# Check status
python scripts/regulatory_monitor.py --status

# View last changes
cat regulatory_data/detected_changes.json

# View impact reports
cat regulatory_data/impact_*.txt
```

### Files Generated

| File | Purpose |
|------|---------|
| `regulatory_data/regulations_cache.json` | All fetched regulations |
| `regulatory_data/detected_changes.json` | Changes from last run |
| `regulatory_data/change_history.json` | Historical tracking |
| `regulatory_data/impact_*.txt` | Compliance impact reports |
| `regulatory_data/monitoring.log` | Detailed logs |

## Example Outputs

### Change Detection Output
```
🔍 REGULATORY CHANGE DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Regulation: GDPR Article 4 Update
📅 Date: 2025-11-16
🏷️  Severity: MEDIUM
📊 Similarity: 92%

📈 CHANGE SUMMARY:
  • New clauses: 1
  • Removed clauses: 0
  • Modified clauses: 2

➕ NEW CLAUSES:
   • Biometric data protection measures

🔄 MODIFIED CLAUSES:
   • Data minimization requirements → Enhanced data minimization
```

### Impact Report
```
╔════════════════════════════════════════════════════════════╗
║    COMPLIANCE IMPACT REPORT: GDPR
╚════════════════════════════════════════════════════════════╝

AFFECTED MODULES:
  • L1-Governance
  • L2-Privacy

⚠️  NEW REQUIREMENTS:
      • Enhanced biometric data protection
      • Additional consent mechanisms

ACTION ITEMS:
  1. Review regulation changes
  2. Assess current controls
  3. Identify compliance gaps
  4. Update trace_map.yaml
  5. Re-run compliance assessment
```

## Supported Regulations

| Regulation | Region | Type | Update Freq | Maps To |
|-----------|--------|------|-------------|---------|
| GDPR | EU | RSS | Daily | L1, L2 |
| HIPAA | US | API/Web | 48h | L2, L5 |
| EU AI Act | EU | RSS | 48h | L3, L4, L1 |
| SOC2 | US | Web | Weekly | L1, L5 |
| CCPA | US | RSS | Weekly | L1, L2 |

**Add more sources:** Edit `configs/regulatory_sources.yaml` and add custom sources.

## Alert Severity

- 🔴 **CRITICAL**: < 50% similarity (major changes)
- 🟠 **HIGH**: < 70% similarity (significant changes)
- 🟡 **MEDIUM**: < 85% similarity (moderate changes)
- 🟢 **LOW**: < 95% similarity (minor changes)

**Action Required by Severity:**
- CRITICAL: Review within 24 hours
- HIGH: Review within 48 hours
- MEDIUM: Review within 1 week
- LOW: Include in next monthly review

## Advanced Configuration

### Change Monitoring Sensitivity
```yaml
nlp_settings:
  similarity_threshold: 0.75  # Lower = more sensitive (0-1)
  
  severity_thresholds:
    critical: 0.50
    high: 0.70
    medium: 0.85
```

### Notification Methods
```yaml
notifications:
  alert_on_new: true
  min_severity: "MEDIUM"
  
  methods:
    dashboard: true      # Always show in dashboard
    slack:
      enabled: true      # Optional Slack alerts
      webhook_url: "${SLACK_WEBHOOK_URL}"
    email:
      enabled: false     # Optional email alerts
      to_addresses: ["compliance@company.com"]
```

### Custom Schedule
```yaml
monitoring_schedule:
  type: custom_cron
  expression: "0 */6 * * *"  # Every 6 hours
```

## Troubleshooting

### "No changes detected"
1. First run? Wait for next scheduled run
2. Check similarity_threshold in config (lower = more sensitive)
3. Verify sources are enabled
4. Test: `python scripts/regulatory_monitor.py --test`

### "IRAQAF not updating"
1. Check `trace_map.yaml` exists in `configs/`
2. Verify `auto_update_trace_map: true` in config
3. Check file permissions (must be writable)

### "Rate limited"
Adjust in `regulatory_sources.yaml`:
```yaml
rate_limiting:
  request_delay: 5      # Increase delay
  max_concurrent: 1     # Reduce parallel requests
```

### "SSL errors"
```bash
# Development only:
export PYTHONHTTPSVERIFY=0
python scripts/regulatory_monitor.py
```

## Best Practices

✅ **DO:**
- Schedule daily/weekly based on risk
- Review CRITICAL changes within 24 hours
- Keep audit trail (automatic)
- Test in staging first

❌ **DON'T:**
- Skip manual review of changes
- Auto-apply without validation
- Store credentials in config files
- Monitor more than hourly

## Integration Checklist

- [ ] Install dependencies: `pip install -r requirements-regulatory.txt`
- [ ] Configure sources in `configs/regulatory_sources.yaml`
- [ ] Test monitoring: `python scripts/regulatory_monitor.py --test`
- [ ] Set up scheduler: `python scripts/regulatory_scheduler.py`
- [ ] Add to dashboard: Import `display_regulatory_alerts()`
- [ ] Enable Slack (optional): Add webhook to config
- [ ] Set branch protection (optional): Require compliance checks

## Next Steps

1. **Now**: Start monitoring with daily schedule
2. **Today**: Review generated reports
3. **This Week**: Integrate with CI/CD pipeline
4. **This Month**: Set up Slack/email notifications

## Documentation

- **Full Guide**: `REGULATORY_MONITORING_GUIDE.md`
- **API Docs**: See docstrings in `scripts/regulatory_*.py`
- **Configuration**: `configs/regulatory_sources.yaml`
- **Dashboard Code**: `scripts/dashboard_regulatory_integration.py`

## Support

### Getting Help

```bash
# View monitoring status
python scripts/regulatory_scheduler.py --status

# Check logs
tail -f regulatory_data/monitoring.log

# Run test
python scripts/regulatory_monitor.py --test --verbose

# Manual check
python scripts/nlp_change_detector.py
python scripts/iraqaf_regulatory_sync.py
```

## Examples

### Example 1: Daily GDPR Monitoring
```bash
# In regulatory_sources.yaml:
monitoring_schedule:
  type: daily
  hour: 2

regulatory_sources:
  gdpr:
    enabled: true
    type: rss
    url: "https://eur-lex.europa.eu/rss/oj-l-all.xml"

# Start:
python scripts/regulatory_scheduler.py
```

### Example 2: Custom Multi-Source
```python
from regulatory_monitor import RegulatoryMonitor, APISource

monitor = RegulatoryMonitor()
monitor.register_source(APISource('HIPAA', 'https://...'))
monitor.register_source(APISource('CCPA', 'https://...'))

changes = monitor.detect_changes()
```

### Example 3: Manual Change Analysis
```python
from nlp_change_detector import NLPChangeDetector

detector = NLPChangeDetector()
changes = detector.detect_clause_changes(old_text, new_text)
severity = detector.classify_severity(changes)
print(f"Severity: {severity}")
```

---

**Ready to go!** Start with: `python scripts/regulatory_scheduler.py --schedule daily --hour 2`

Questions? Check `REGULATORY_MONITORING_GUIDE.md` for detailed documentation.
