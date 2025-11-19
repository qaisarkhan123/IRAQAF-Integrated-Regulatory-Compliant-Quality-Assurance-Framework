#  Quick Start Guide - IRAQAF

## What is IRAQAF?

IRAQAF is a **Regulatory Compliance Framework** for AI systems. It assesses compliance across **5 levels (L1-L5)** and provides real-time dashboards for monitoring and improvement.

##  Three Dashboards

| Dashboard | Port | Framework | Purpose |
|-----------|------|-----------|---------|
| **Main Dashboard** | 8501 | Streamlit | L1-L5 Compliance Overview |
| **Security Hub** | 8502 | Flask | 8 Security Modules & Analytics |
| **L4 Explainability Hub** | 5000 | Flask | AI Transparency with SHAP/LIME/GradCAM |

##  60-Second Setup

\\\powershell
# 1. Navigate to project
cd C:\Users\khan\Downloads\iraqaf_starter_kit

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Launch dashboards (in separate terminals)
# Terminal 1:
python -m streamlit run dashboard/app.py --server.port 8501

# Terminal 2:
python dashboard/privacy_security_hub.py

# Terminal 3:
python dashboard/hub_explainability_app.py

# 4. Open in browser
# Main:     http://localhost:8501 (Login: admin/admin_default_123)
# Security: http://localhost:8502
# L4 Hub:   http://localhost:5000
\\\

##  What's in Each Dashboard?

###  Main Dashboard (Port 8501)
- **Requires Login**: admin / admin_default_123
- **Features**:
  - L1-L5 compliance modules
  - Real-time alerts & notifications
  - PDF/CSV export
  - Role-based access control (RBAC)
  - Navigation buttons to Security Hub & L4 Hub

###  Security Hub (Port 8502)
- **Access**: Open API (no authentication)
- **8 Security Modules**:
  - PII Detection & Classification
  - Encryption Validator (AES-256, TLS 1.3)
  - Data Retention Policies
  - Role-Based Access Control
  - Real-time Threat Detection
  - GDPR Compliance Tracking
  - Comprehensive Audit Logging
  - API Security & Rate Limiting
- **Features**:
  - Dashboard overview tabs
  - Real-time security charts
  - Module assessment details

###  L4 Explainability Hub (Port 5000)
- **Access**: Open API (no authentication)
- **5 Interactive Tabs**:
  1. Overview - Dashboard with 12 modules
  2. How Model Decides - SHAP, LIME, GradCAM, Decision Paths
  3. Detailed Analysis - Module breakdowns
  4. How Scores Calculated - Mathematical formulas
  5. Recommendations - Improvement actions
- **AI Interpretability Methods**:
  - SHAP Force Plots (feature contributions)
  - LIME Explanations (local interpretable model)
  - GradCAM Heatmaps (attention visualization)
  - Decision Paths (step-by-step reasoning)
- **Current Score**: 85/100 (exceeds 80% benchmark)

##  Common Tasks

### Start Only Main Dashboard
\\\ash
streamlit run dashboard/app.py --server.port 8501
\\\

### Start Only Security Hub
\\\ash
python dashboard/privacy_security_hub.py
\\\

### Start Only L4 Explainability Hub
\\\ash
python dashboard/hub_explainability_app.py
\\\

### Test API Endpoints
\\\ash
# Security Hub - Get overall security score
curl http://localhost:8502/api/security-score

# L4 Hub - Get transparency score
curl http://localhost:5000/api/transparency-score

# L4 Hub - Get SHAP interpretability
curl http://localhost:5000/api/interpretability/shap
\\\

##  Troubleshooting

### Port Already in Use
\\\powershell
# Kill process on port 8501
netstat -ano | findstr ":8501"
taskkill /PID <PID> /F

# Kill process on port 8502
netstat -ano | findstr ":8502"
taskkill /PID <PID> /F

# Kill process on port 5000
netstat -ano | findstr ":5000"
taskkill /PID <PID> /F
\\\

### Dashboard Not Starting
1. Verify Python 3.10+ installed: \python --version\
2. Check virtual environment: \env\Scripts\activate\
3. Install dependencies: \pip install -r requirements.txt\
4. Verify syntax: \python -m py_compile dashboard/app.py\

### Dependencies Missing
\\\ash
pip install -r requirements.txt
# Or install individually:
pip install streamlit flask flask-cors matplotlib numpy pandas sqlalchemy
pip install shap lime
\\\

##  Default Credentials

**Main Dashboard Only** (Security & L4 hubs are open API):
- **Username**: admin
- **Password**: admin_default_123

 **CHANGE THESE IN PRODUCTION!**

##  Dashboard URLs

- **Main Dashboard**: http://localhost:8501
- **Security Hub**: http://localhost:8502
- **L4 Explainability Hub**: http://localhost:5000

##  Next Steps

1.  Start all three dashboards
2.  Login to Main Dashboard (admin/admin_default_123)
3.  Click buttons to explore Security Hub & L4 Hub
4.  Test API endpoints
5.  Review full documentation in README.md & L4_HUB_GUIDE.md

##  Pro Tips

- **Use multiple terminals**: Each dashboard needs its own terminal window
- **Wait for startup**: Flask apps load in 2-3 seconds, Streamlit in 8-12 seconds
- **Check logs**: Terminal output shows any errors or warnings
- **Use dark mode**: All dashboards have beautiful dark themes
- **Export data**: Main dashboard supports PDF & CSV exports

---

**Version**: 2.0  
**Last Updated**: November 19, 2025  
**Status**:  Production Ready
