# Quick Start Guide - IRAQAF Framework

##  Fastest Way to Start Everything

### Option 1: PowerShell (Recommended for Windows)
```powershell
cd C:\Users\khan\Downloads\iraqaf_starter_kit
.\START_ALL_4_DASHBOARDS.bat
```

### Option 2: Manual (One Command Per Hub)
```powershell
# Terminal 1 - L1 Regulations Hub
python dashboard/l1_regulations_governance_hub.py

# Terminal 2 - L2 Privacy & Security Hub
python dashboard/privacy_security_hub.py

# Terminal 3 - L3 Operations Control Center
python dashboard/l3_operations_control_center.py

# Terminal 4 - L4 Explainability Hub
python dashboard/hub_explainability_app.py
```

---

##  Access URLs

| Hub | URL | Purpose |
|-----|-----|---------|
| **L1** | http://localhost:8504 | Regulations & Governance |
| **L2** | http://localhost:8502 | Privacy & Security |
| **L3** | http://localhost:8503 | Operations Control |
| **L4** | http://localhost:5000 | Explainability |
| **Main** | http://localhost:8501 | Main Dashboard |

---

##  Login Credentials

```
Username: admin
Password: admin_default_123
```

---

##  Troubleshooting

### Port Already in Use
```powershell
Get-Process python | Stop-Process -Force
```

### Missing Dependencies
```powershell
pip install -r requirements.txt
```

### Environment Setup
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

---

##  Expected Output

Each hub will show startup messages like:
```
 Phase 1: Architecture Overview
 Phase 2: Database Operations
 Phase 3: Web Scrapers Dashboard
...
Starting Flask server...
* Running on http://127.0.0.1:8503
```

---

##  For More Details

- **L1 Hub**: See `L1_REGULATIONS_HUB_GUIDE.md`
- **L3 Hub**: See `L3_OPERATIONS_CONTROL_CENTER_GUIDE.md`
- **L4 Hub**: See `L4_HUB_GUIDE.md`
- **API Docs**: See `PHASE_8_API_REFERENCE.md`

**That''s it! Your 4-hub system is now running.**
