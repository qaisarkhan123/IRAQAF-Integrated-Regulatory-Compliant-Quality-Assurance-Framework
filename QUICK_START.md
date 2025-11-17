#  Quick Reference - IRAQAF Commands

## Dashboard

### Start Dashboard
```bash
streamlit run dashboard/app.py
```

### Start on Different Port
```bash
streamlit run dashboard/app.py --server.port=8502
```

### Debug Mode
```bash
streamlit run dashboard/app.py --logger.level=debug
```

## Modules

### L1 - Governance & Regulatory
```bash
python -m cli.iraqaf_cli run --module L1 --config configs/governance.yaml
```

### L2 - Privacy & Security
```bash
python -m cli.iraqaf_cli run --module L2 --config configs/security.yaml
```

### L3 - Fairness
```bash
python -m cli.iraqaf_cli run --module L3 --config configs/fairness.yaml
```

### L4 - Explainability
```bash
python -m cli.iraqaf_cli run --module L4 --config configs/explainability.yaml
```

### L5 - Operations
```bash
python -m cli.iraqaf_cli run --module L5 --config configs/operations.yaml
```

### Run All Modules
```bash
python -m cli.iraqaf_cli run-all --config configs/project.yaml
```

## Data & Reports

### Generate Evidence Report
```bash
# Navigate to dashboard  Evidence Management  Sync & Export
# Select format (CSV/PDF/JSON/Word) and download
```

### Access Reports Directory
```bash
# Reports are saved in:
ls reports/

# Filter by date:
ls reports/L1-*.json
```

### Export Formats

| Format | Usage | Command |
|--------|-------|---------|
| **CSV** | Tabular data | Dashboard or CLI |
| **PDF** | Professional reports | Dashboard |
| **JSON** | Machine-readable | CLI or Dashboard |
| **Word** | Formatted documents | Dashboard |

## Installation & Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python -c "import dashboard; print(' Setup complete')"
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Test Specific Module
```bash
pytest tests/test_l2_security.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=dashboard --cov-report=html
```

## Database

### Reset Database
```bash
rm iraqaf_compliance.db
```

### Backup Database
```bash
cp iraqaf_compliance.db iraqaf_compliance.db.backup
```

### Check Database Status
```bash
# In dashboard: Evidence Management  Database Insights
```

## Configuration

### Edit Configuration
```bash
nano configs/project.yaml
```

### Supported Frameworks
- GDPR
- HIPAA
- PCI-DSS
- ISO 27001:2022
- NIST Cybersecurity Framework 2.0

### Add Custom Policy
Edit `configs/policies.yaml` and add your policy rules.

## Troubleshooting

### Clear Streamlit Cache
```bash
streamlit cache clear
```

### Stop Streamlit Process
```powershell
# Windows
Get-Process streamlit | Stop-Process -Force

# Linux/Mac
pkill -f streamlit
```

### Check Logs
```bash
tail -f logs/app.log
```

### Verify Python Version
```bash
python --version  # Should be 3.8+
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Use `--server.port=8502` |
| Module not found | Run `pip install -r requirements.txt` |
| Session timeout | Log back in (8-hour default) |
| Upload fails | Check disk space and permissions |
| Report generation slow | Reduce date range or file count |

## Performance Tips

-  Limit file uploads to <100MB per session
-  Export reports in batches for large datasets
-  Clear cache regularly with `streamlit cache clear`
-  Close unused browser tabs to reduce memory usage

## API Reference

### Authentication
```python
from dashboard.auth_ui import verify_credentials
auth = verify_credentials(username, password)
```

### Export Manager
```python
from dashboard.export_alerts_rbac import ExportManager
manager = ExportManager()
manager.export_to_csv(data, filename)
```

### RBAC
```python
from dashboard.export_alerts_rbac import RBACManager
rbac = RBACManager()
rbac.check_permission(user_role, action)
```

## Resources

-  [README.md](./README.md) - Full documentation
-  [00_START_HERE.md](./00_START_HERE.md) - Getting started guide
-  [GitHub Repository](https://github.com/qaisarkhan123/IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework)
-  Support via GitHub Issues

---

**Last Updated**: November 2025
