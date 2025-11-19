# IRAQAF - Integrated Regulatory Compliant Quality Assurance Framework

**Comprehensive AI System Compliance & Governance Platform**

## Overview

IRAQAF is a production-ready framework for assessing AI system compliance across 5 regulatory levels (L1-L5). It provides a triple-dashboard architecture combining Streamlit main dashboard with two specialized Flask hubs for in-depth security and explainability assessment.

##  Key Features

- **5-Level Compliance Framework**: L1-L5 regulatory assessment
- **Triple-Dashboard Architecture**: Streamlit main + 2 Flask specialized hubs
- **Real-Time Metrics**: Live compliance scoring and visualization
- **12 Assessment Modules per Level**: Comprehensive evaluation criteria
- **Role-Based Access**: Admin/User authentication and authorization
- **AI Interpretability**: SHAP, LIME, GradCAM explanations (L4 Hub)
- **Security Analytics**: 8 security modules with real-time threat detection
- **Audit Trail**: Complete decision traceability

##  Three-Dashboard System

| Dashboard | Framework | Port | Purpose |
|-----------|-----------|------|---------|
| **Main Dashboard** | Streamlit | 8501 | L1-L5 compliance overview, authentication, RBAC |
| **Security Hub** | Flask | 8502 | 8 security modules, real-time analytics, threat detection |
| **L4 Explainability Hub** | Flask | 5000 | AI transparency, SHAP/LIME/GradCAM, decision paths |

### 1. **Main Dashboard** (Streamlit - Port 8501)
- User authentication with admin/user roles
- L1-L5 compliance modules overview
- Interactive module selection and testing
- Real-time alerts & notifications
- PDF/CSV export functionality
- Role-based access control (RBAC)

### 2. **Security & Privacy Hub** (Flask - Port 8502)
- **8 Security Assessment Modules**:
  - PII Detection & Classification
  - Encryption Validator (AES-256, TLS 1.3)
  - Data Retention Policies
  - Role-Based Access Control (RBAC)
  - Real-time Threat Detection
  - GDPR Compliance Tracking
  - Comprehensive Audit Logging
  - API Security & Rate Limiting
- Dashboard overview with security scores by category
- Real-time charts and analytics
- Beautiful dark-themed UI
- RESTful API endpoints

### 3. **L4 Explainability Hub** (Flask - Port 5000)
- **5-Tab Interactive Interface**:
  1. Overview - Dashboard with all 12 modules
  2. How Model Decides - SHAP, LIME, GradCAM, Decision Paths
  3. Detailed Analysis - Module breakdowns
  4. How Scores Calculated - Mathematical formulas
  5. Recommendations - Improvement actions
- **12 Explainability Assessment Modules**
- **4-Category Scoring** (35%, 30%, 25%, 10%)
- **AI Interpretability Methods**:
  - SHAP Force Plots (feature contributions)
  - LIME Local Explanations (model-agnostic)
  - GradCAM Attention Heatmaps (visual focus)
  - Decision Path Visualization (step-by-step reasoning)
- **Overall Transparency Score**: 85% (exceeds 80% benchmark)

##  Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment (venv)
- Flask 3.1.2+
- Streamlit 1.28+
- Windows, macOS, or Linux

### Installation

\\\ash
# Clone repository
git clone https://github.com/qaisarkhan123/IRAQAF.git
cd IRAQAF

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
\\\

### Launch All Three Dashboards

\\\powershell
# Start all dashboards at once
cd C:\Users\khan\Downloads\iraqaf_starter_kit

# Terminal 1: Main Dashboard
python -m streamlit run dashboard/app.py --server.port 8501

# Terminal 2: Security Hub
python dashboard/privacy_security_hub.py

# Terminal 3: L4 Explainability Hub
python dashboard/hub_explainability_app.py
\\\

**Access**:
- Main Dashboard: http://localhost:8501 (Login: admin / admin_default_123)
- Security Hub: http://localhost:8502
- L4 Explainability Hub: http://localhost:5000

### Launch Individual Components

\\\ash
# Main Dashboard only
streamlit run dashboard/app.py --server.port 8501

# Security Hub only
python dashboard/privacy_security_hub.py

# L4 Explainability Hub only
python dashboard/hub_explainability_app.py
\\\

##  Technology Stack

| Component | Technology | Port | Status |
|-----------|-----------|------|--------|
| Main Dashboard | Streamlit 1.28+ | 8501 |  Production Ready |
| Security Hub | Flask 3.1.2 + Matplotlib | 8502 |  Production Ready |
| L4 Hub | Flask 3.1.2 + Matplotlib + SHAP + LIME | 5000 |  Production Ready |
| Backend | Python 3.10+ | - |  Production Ready |
| Authentication | SQLAlchemy + Session Management | - |  Implemented |

##  Authentication

**Default Credentials** (CHANGE IN PRODUCTION):
- **Username**: \dmin\
- **Password**: \dmin_default_123\

### Security Notes
- Main Dashboard requires authentication
- Security Hub (port 8502) uses open API access
- L4 Hub (port 5000) uses open API access
- All hubs support RESTful API calls for integration

##  API Endpoints

### Security Hub (Port 8502)
- \GET /\ - Dashboard HTML
- \GET /api/security-score\ - Overall security score
- \GET /api/modules\ - All 8 security modules
- \GET /api/category-chart\ - Security by category visualization
- \GET /api/module-chart\ - Module scores visualization
- \GET /api/compliance/<module>\ - Module compliance details

### L4 Explainability Hub (Port 5000)
- \GET /\ - Dashboard HTML
- \GET /api/modules\ - All 12 explainability modules
- \GET /api/transparency-score\ - Overall transparency score
- \GET /api/interpretability/shap\ - SHAP visualization
- \GET /api/interpretability/lime\ - LIME explanation
- \GET /api/interpretability/gradcam\ - GradCAM heatmap
- \GET /api/interpretability/decision-path\ - Decision flow
- \GET /api/interpretability/all\ - All visualizations

##  Project Structure

\\\
IRAQAF/
 dashboard/
    app.py                          # Main Streamlit dashboard
    privacy_security_hub.py          # Security & Privacy Hub (Flask)
    hub_explainability_app.py        # L4 Explainability Hub (Flask)
    authentication.py                # Auth logic
    export_alerts_rbac.py           # Export/RBAC functions
 privacy/                            # Privacy modules
 security/                           # Security modules
 requirements.txt                    # Python dependencies
 README.md                           # This file
 QUICK_START.md                      # Getting started guide
 L4_HUB_GUIDE.md                     # L4 Hub detailed documentation
\\\

##  Testing

\\\ash
# Verify syntax of all dashboards
python -m py_compile dashboard/app.py
python -m py_compile dashboard/privacy_security_hub.py
python -m py_compile dashboard/hub_explainability_app.py

# Test API endpoints (with dashboards running)
curl http://localhost:8502/api/security-score
curl http://localhost:5000/api/transparency-score
\\\

##  L4 Explainability Hub - 4-Category Framework

### Category A: Explanation Capability (35%)
- Explanation Method Implementation (SHAP, LIME, GradCAM)
- Explanation Quality & Format
- Coverage & Completeness

### Category B: Explanation Reliability (30%)
- Fidelity Testing (score >0.5)
- Feature Consistency (Jaccard >0.7)
- Stability Testing (Spearman >0.8)

### Category C: Traceability & Auditability (25%)
- Prediction Logging & Immutability
- Model Versioning & Provenance
- Audit Trail Completeness

### Category D: Documentation Transparency (10%)
- System Documentation
- Intended Use & Scope
- Change Management & Transparency

**Current Score**: 85/100 (Exceeds 80% benchmark)

##  Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (\git checkout -b feature/AmazingFeature\)
3. Commit changes (\git commit -m 'Add AmazingFeature'\)
4. Push to branch (\git push origin feature/AmazingFeature\)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see LICENSE.md for details.

##  Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@iraqaf.example.com
- Documentation: Full guides in markdown files

---

**Last Updated**: November 19, 2025  
**Version**: 2.0 (Triple Dashboard - Flask + Streamlit Hybrid)  
**Status**:  **Production Ready**  
**Commit**: d1f1575
