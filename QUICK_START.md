#  Quick Start Guide - IRAQAF

## Dashboard Launch

### Automated Dual Dashboard (Recommended)
\\\ash
python launch_dual_dashboards.py
\\\

### Manual Launch

**Terminal 1 - Main Dashboard (Port 8501)**
\\\ash
streamlit run dashboard/app.py --server.port 8501
\\\

**Terminal 2 - Security Hub (Port 8502)**
\\\ash
python dashboard/hub_flask_app.py
\\\

## Access Dashboard

- **Main Dashboard**: http://localhost:8501
- **Security Hub**: http://localhost:8502
- **Login**: admin / admin_default_123

## Process Management

### Kill All Python Processes
\\\powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
\\\

### Kill Specific Port
\\\powershell
netstat -ano | findstr :8501
taskkill /PID <PID> /F
\\\

## CLI Modules

### L1 - Governance & Regulatory
\\\ash
python -m cli.iraqaf_cli run --module L1 --config configs/governance.yaml
\\\

### L2 - Privacy & Security
\\\ash
python -m cli.iraqaf_cli run --module L2 --config configs/security.yaml
\\\

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

## Data & Reports

### Generate Evidence Report
1. Dashboard  Evidence Management  Sync & Export
2. Select format (CSV/PDF/JSON/Word)
3. Download report

### Access Reports Directory
\\\ash
ls reports/
ls reports/L1-*.json
\\\

## Installation & Setup

### Install Dependencies
\\\ash
pip install -r requirements.txt
\\\

### Update Dependencies
\\\ash
pip install -r requirements.txt --upgrade
\\\

## Testing

### Run Unit Tests
\\\ash
pytest tests/ -v
\\\

### Run with Coverage
\\\ash
pytest tests/ --cov=dashboard --cov-report=html
\\\

## Database

### Reset Database
\\\ash
rm iraqaf_compliance.db
\\\

### Backup Database
\\\ash
cp iraqaf_compliance.db iraqaf_compliance.db.backup
\\\

## Troubleshooting

### Port Already in Use
\\\powershell
streamlit run dashboard/app.py --server.port=8503
\\\

### Security Hub Not Accessible (Port 8502)
\\\powershell
# Install Flask if needed
pip install flask

# Launch the hub
python dashboard/hub_flask_app.py
\\\

### Clear Streamlit Cache
\\\ash
streamlit cache clear
\\\

## Common Issues

| Issue | Solution |
|-------|----------|
| Port 8501 in use | Use \--server.port=8503\ |
| Port 8502 in use | Kill with \Get-Process python \| Stop-Process -Force\ |
| Module not found | Run \pip install -r requirements.txt\ |
| Session timeout | Log back in (8-hour default) |
| Upload fails | Check disk space in \data/uploads/\ |
| Flask hub crashes | Install Flask: \pip install flask\ |

## Performance Tips

- Limit file uploads to <100MB per session
- Export reports in batches
- Clear cache: \streamlit cache clear\
- Close unused tabs to reduce memory
- Run Hub on separate terminal

## Security Hub API Endpoints

\\\ash
# Get dashboard
curl http://localhost:8502/

# Get module data
curl http://localhost:8502/api/module/PII_Detection

# Health check
curl http://localhost:8502/health

# Analytics data
curl http://localhost:8502/api/analytics
\\\

---

**Last Updated**: November 2025  
**Status**:  Production Ready  
**Version**: 2.1 (Flask Hub)
