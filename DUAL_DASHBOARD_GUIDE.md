# Running Both Dashboards: Quick Start Guide

## Option 1: Automated Launch (Recommended)

Run both dashboards with a single command:

```bash
python launch_dual_dashboards.py
```

This will:
- ✓ Clear any existing processes on ports 8501 and 8502
- ✓ Start Main Dashboard (Streamlit) on port 8501
- ✓ Start Privacy & Security Hub (Flask) on port 8502
- ✓ Display URLs and login credentials

**Close the terminal window to stop both apps.**

---

## Option 2: Manual Launch

### Start Main Dashboard (Streamlit)

```bash
# From project root
venv\Scripts\streamlit.exe run dashboard/app.py --server.port=8501
```

In a separate terminal, start the Security Hub:

```bash
# From project root
venv\Scripts\python.exe dashboard/hub_flask_app.py
```

---

## Accessing the Dashboards

### Main Dashboard
- **URL**: http://localhost:8501
- **Login**: admin / admin_default_123
- **Features**:
  - L1-L5 Assessment Modules
  - GQAS Aggregate Scoring
  - Evidence Management & Upload
  - Export (CSV, PDF, JSON, Word)
  - Role-based Access Control

### Privacy & Security Hub
- **URL**: http://localhost:8502
- **Features** (10 Modules):
  - Dashboard Overview
  - PII Detection & Anonymization
  - Encryption Validator
  - Model Integrity Checker
  - Adversarial Test Suite
  - GDPR Rights Management
  - L2 Historical Metrics
  - MFA Configuration
  - Data Retention Policy
  - Quick Assessment Tool

---

## Architecture

| Component | Framework | Port | Status |
|-----------|-----------|------|--------|
| Main Dashboard | Streamlit | 8501 | ✅ Production Ready |
| Security Hub | Flask | 8502 | ✅ Production Ready |

---

## Troubleshooting

### Port Already in Use
The launcher automatically clears ports 8501 and 8502 before starting. If you still see port errors:

```bash
# Kill processes on specific ports (Windows)
taskkill /F /IM streamlit.exe
taskkill /F /IM python.exe
```

Then try again.

### Flask App Won't Start
Ensure Flask is installed:

```bash
venv\Scripts\pip.exe install flask
```

### Can't See Security Hub Module Options
The Flask hub renders using embedded HTML/JavaScript. Make sure JavaScript is enabled in your browser.

---

## API Endpoints

### Security Hub (Flask)

- `GET /` - Main hub page with all modules
- `GET /api/module/<module_name>` - Get specific module data
- `GET /health` - Health check endpoint

Example:
```bash
curl http://localhost:8502/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Privacy & Security Hub",
  "port": 8502,
  "modules": 10,
  "timestamp": "2025-11-19T00:02:00"
}
```

---

## Notes

- Both apps run independently and can be stopped without affecting the other
- The main dashboard includes a link back to the hub in the sidebar
- All data is in-memory for this demo; production deployments should use persistent storage
- The Flask hub uses embedded HTML templates and doesn't require additional static files
