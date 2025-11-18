#  Quick Reference - IRAQAF Commands

##  Dashboard

### Start Main Dashboard (Port 8501)
\\\ash
streamlit run dashboard/app.py --server.port 8501
\\\

### Start Privacy & Security Hub (Port 8502)
\\\ash
streamlit run dashboard/privacy_security_hub.py --server.port 8502
\\\

### Start Dashboard on Different Port
\\\ash
streamlit run dashboard/app.py --server.port=8503
\\\

### Debug Mode
\\\ash
streamlit run dashboard/app.py --logger.level=debug
\\\

### Kill All Streamlit Processes
\\\powershell
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force
\\\

##  Modules

### L1 - Governance & Regulatory
\\\ash
python -m cli.iraqaf_cli run --module L1 --config configs/governance.yaml
\\\

### L2 - Privacy & Security
\\\ash
python -m cli.iraqaf_cli run --module L2 --config configs/security.yaml
\\\
**Note**: L2 assessments also available in Privacy & Security Hub with L2 Historical Metrics tab

### L3 - Fairness
\\\ash
python -m cli.iraqaf_cli run --module L3 --config configs/fairness.yaml
\\\

### L4 - Explainability
\\\ash
python -m cli.iraqaf_cli run --module L4 --config configs/explainability.yaml
\\\

### L5 - Operations
\\\ash
python -m cli.iraqaf_cli run --module L5 --config configs/operations.yaml
\\\

### Run All Modules
\\\ash
python -m cli.iraqaf_cli run-all --config configs/project.yaml
\\\

##  Data & Reports

### Generate Evidence Report
\\\ash
# Via Dashboard:
# Evidence Management  Sync & Export  Select format (CSV/PDF/JSON/Word)  Download
\\\

### Access Reports Directory
\\\ash
# Reports are saved in:
ls reports/

# Filter by date:
ls reports/L1-*.json
\\\

### Export Formats

| Format | Usage | Where |
|--------|-------|-------|
| **CSV** | Tabular data | Dashboard or CLI |
| **PDF** | Professional reports | Dashboard |
| **JSON** | Machine-readable | CLI or Dashboard |
| **Word** | Formatted documents | Dashboard |

##  Installation & Setup

### Install Dependencies
\\\ash
pip install -r requirements.txt
\\\

### Verify Installation
\\\ash
python -c "import streamlit; print(' Setup complete')"
\\\

### Update Dependencies
\\\ash
pip install -r requirements.txt --upgrade
\\\

##  Testing

### Run Unit Tests
\\\ash
pytest tests/ -v
\\\

### Test Specific Module
\\\ash
pytest tests/test_l2_security.py -v
\\\

### Run with Coverage
\\\ash
pytest tests/ --cov=dashboard --cov-report=html
\\\

##  Database

### Reset Database
\\\ash
rm iraqaf_compliance.db
\\\

### Backup Database
\\\ash
cp iraqaf_compliance.db iraqaf_compliance.db.backup
\\\

### Check Database Status
\\\ash
# In dashboard: Evidence Management  Database Insights
\\\

##  Configuration

### Edit Configuration
\\\ash
# Windows
notepad configs/project.yaml

# Linux/Mac
nano configs/project.yaml
\\\

### Supported Frameworks
- GDPR
- HIPAA
- PCI-DSS
- ISO 27001:2022
- NIST Cybersecurity Framework 2.0

### Add Custom Policy
Edit \configs/policies.yaml\ and add your policy rules.

##  Troubleshooting

### Clear Streamlit Cache
\\\ash
streamlit cache clear
\\\

### Stop Streamlit Process
\\\powershell
# Windows
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force

# Linux/Mac
pkill -f streamlit
\\\

### Check Logs
\\\ash
tail -f logs/app.log
\\\

### Verify Python Version
\\\ash
python --version  # Should be 3.8+
\\\

### Port Already in Use
\\\ash
# Main dashboard uses 8501, Hub uses 8502
# Use different port:
streamlit run dashboard/app.py --server.port=8503
\\\

### Privacy & Security Hub Not Accessible
\\\ash
# Verify port 8502 is available
netstat -ano | findstr :8502

# Launch the hub
streamlit run dashboard/privacy_security_hub.py --server.port 8502
\\\

##  Common Issues

| Issue | Solution |
|-------|----------|
| Port 8501 already in use | Use \--server.port=8503\ |
| Port 8502 already in use | Kill process: \Get-Process streamlit \| Stop-Process -Force\ |
| Module not found | Run \pip install -r requirements.txt\ |
| Session timeout | Log back in (8-hour default) |
| Upload fails | Check disk space and permissions in \data/uploads/\ |
| Report generation slow | Reduce date range or file count |
| Hub not loading | Ensure both dashboards are running on 8501 & 8502 |

##  Performance Tips

- Limit file uploads to <100MB per session
- Export reports in batches for large datasets
- Clear cache regularly with \streamlit cache clear\
- Close unused browser tabs to reduce memory usage
- Run Hub separately if only accessing security modules

##  API Reference

### Authentication
\\\python
from dashboard.auth_ui import verify_credentials
auth = verify_credentials(username, password)
\\\

### Export Manager
\\\python
from dashboard.export_alerts_rbac import ExportManager
manager = ExportManager()
manager.export_to_csv(data, filename)
\\\

### RBAC
\\\python
from dashboard.export_alerts_rbac import RBACManager
rbac = RBACManager()
rbac.check_permission(user_role, action)
\\\

### L2 Integration
\\\python
from dashboard.l2_monitor_integration import get_l2_metrics
metrics = get_l2_metrics()
\\\

##  Resources

- [README.md](./README.md) - Full documentation
- [00_START_HERE.md](./00_START_HERE.md) - Getting started guide
- [GitHub Repository](https://github.com/qaisarkhan123/IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework)
- Support via GitHub Issues

---

**Last Updated**: November 2025
**Version**: 2.0 (with Privacy & Security Hub)
