#  Quick Start Guide - IRAQAF

## What is IRAQAF?

IRAQAF is a **Regulatory Compliance Framework** for AI systems. It assesses compliance across **5 levels (L1-L5)** and provides real-time dashboards for monitoring and improvement.

##  Three Dashboards

| Dashboard | Port | Purpose | Access |
|-----------|------|---------|--------|
| **Main Dashboard** | 8501 | L1-L5 Overview | Login required |
| **Security Hub** | 8502 | Security/Privacy deep-dive | Open API |
| **L4 Explainability Hub** | 8503 | Explainability assessment | Open API |

##  60-Second Setup

`powershell
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Launch all dashboards
python launch_dual_dashboards.py

# 3. Open in browser
# Main: http://localhost:8501
# Security: http://localhost:8502
# L4 Hub: http://localhost:8503
`

**Done!** All three dashboards are running.

##  Detailed Setup

### Step 1: Clone Repository
`ash
git clone https://github.com/qaisarkhan123/IRAQAF.git
cd IRAQAF
`

### Step 2: Create Virtual Environment
`ash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
`

### Step 3: Install Dependencies
`ash
pip install -r requirements.txt
`

### Step 4: Launch Dashboards
`ash
# Option A: Launch all 3 dashboards together
python launch_dual_dashboards.py

# Option B: Launch individual dashboards
# Main Dashboard
streamlit run dashboard/app.py

# Security Hub
python dashboard/hub_flask_app.py

# L4 Explainability Hub
python dashboard/hub_explainability_app.py
`

### Step 5: Access Dashboards

**Main Dashboard** (Streamlit)
- URL: http://localhost:8501
- Login: admin / admin_default_123
- Features: L1-L5 modules, interactive tours, configuration

**Security Hub** (Flask)
- URL: http://localhost:8502
- No login required
- Features: 10 security/privacy checks, real-time scoring

**L4 Explainability Hub** (Flask)
- URL: http://localhost:8503
- No login required
- Features: 12 explainability checks, transparency scoring, test results

##  L4 Explainability Hub

The dedicated L4 hub provides comprehensive explainability assessment:

### 4 Categories (Weighted)
1. **Explanation Capability** (35%) - Can the system explain its decisions?
2. **Explanation Reliability** (30%) - Are explanations accurate and stable?
3. **Traceability & Auditability** (25%) - Can decisions be fully traced?
4. **Documentation Transparency** (10%) - Is the system well documented?

### 12 Assessment Checks
- Explanation Methods (SHAP/LIME)
- Explanation Quality
- Coverage & Completeness
- Fidelity Testing
- Feature Consistency
- Stability Testing
- Prediction Logging
- Model Versioning
- Audit Trail
- Documentation
- Intended Use
- Change Management

### Test Results Included
-  Fidelity Test (mask features, measure change)
-  Consistency Test (Jaccard similarity for similar cases)
-  Stability Test (correlation under noise)
-  Audit Trail Test (traceability verification)

##  API Endpoints

### Main Dashboard
`
GET  http://localhost:8501          # Streamlit UI
`

### Security Hub
`
GET  http://localhost:8502/                    # Dashboard
GET  http://localhost:8502/api/modules         # All modules
GET  http://localhost:8502/api/module/<name>   # Specific module
GET  http://localhost:8502/health              # Health check
`

### L4 Explainability Hub
`
GET  http://localhost:8503/                       # Dashboard
GET  http://localhost:8503/api/modules            # 12 checks
GET  http://localhost:8503/api/categories         # 4 categories
GET  http://localhost:8503/api/transparency-score # Overall score
GET  http://localhost:8503/api/tests              # Test results
GET  http://localhost:8503/health                 # Health check
`

##  Troubleshooting

### Port Already in Use
`powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Kill process (replace PID)
taskkill /PID <PID> /F
`

### Virtual Environment Not Activating
`powershell
# Try absolute path
.\venv\Scripts\activate.ps1

# Or run PowerShell as Admin
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
`

### Dependencies Not Installing
`ash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
`

### Dashboards Not Responding
`powershell
# Kill all Python processes
taskkill /F /IM python.exe

# Restart launcher
python launch_dual_dashboards.py
`

##  Documentation

- **README.md** - Full project documentation
- **QUICK_START.md** - This guide
- **SECURITY_HUB_ENHANCEMENTS.md** - Security hub details

##  Understanding L1-L5

- **L1 - Transparency** - Basic system documentation
- **L2 - Auditability** - Decision logging and tracking
- **L3 - Robustness** - Error handling and reliability
- **L4 - Explainability** - Decision explanation capability
- **L5 - Contestability** - User appeal and recourse mechanisms

##  Tips

- **First Time?** Start with the Main Dashboard (port 8501)
- **Deep Dive?** Check Security Hub (port 8502) for security focus
- **Explainability Focus?** Use L4 Hub (port 8503) for detailed assessment
- **API Integration?** Use the exposed endpoints for programmatic access

##  Next Steps

1.  Dashboards running? Explore L1-L5 modules
2.  Check Security Hub for compliance gaps
3.  Review L4 Hub for explainability requirements
4.  Export reports for stakeholders
5.  Configure compliance thresholds

##  Support

- Email: support@iraqaf.example.com
- GitHub Issues: https://github.com/qaisarkhan123/IRAQAF/issues
- Documentation: https://iraqaf.readthedocs.io

---

**Last Updated**: November 19, 2025
**Version**: 2.0
**Status**:  Production Ready
