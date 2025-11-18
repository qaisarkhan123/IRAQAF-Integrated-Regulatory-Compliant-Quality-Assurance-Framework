# IRAQAF - Integrated Regulatory Compliant Quality Assurance Framework

**Comprehensive AI System Compliance & Governance Platform**

## Overview

IRAQAF is a production-ready framework for assessing AI system compliance across 5 regulatory levels (L1-L5). It provides dual-dashboard architecture combining Streamlit main dashboard with specialized Flask hubs for in-depth module assessment.

##  Key Features

- **5-Level Compliance Framework**: L1-L5 regulatory assessment
- **Dual-Dashboard Architecture**: Streamlit main interface + Flask specialized hubs
- **Real-Time Metrics**: Live compliance scoring and visualization
- **12 Assessment Modules per Level**: Comprehensive evaluation criteria
- **Role-Based Access**: Admin/User authentication and authorization
- **Audit Trail**: Complete decision traceability

##  Dual Dashboard System

### 1. **Main Dashboard** (Streamlit - Port 8501)
   - L1-L5 compliance modules overview
   - Interactive tours for each level
   - User authentication
   - Dashboard configuration
   - Module deep-dives and testing

### 2. **Security & Privacy Hub** (Flask - Port 8502)
   - 10 security/privacy assessment checks
   - Real-time threat analysis
   - Compliance score visualization
   - Module breakdown with Chart.js
   - RESTful API endpoints

### 3. **L4 Explainability Hub** (Flask - Port 8503)  NEW
   - 12 explainability assessment checks
   - 4-category transparency scoring (35%, 30%, 25%, 10%)
   - Fidelity, consistency, stability testing
   - Audit trail verification
   - Model versioning & provenance tracking
   - Interactive transparency dashboard

##  Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment (venv)
- Flask 3.1.2
- Streamlit 1.28+

### Installation

`ash
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
`

### Launch All Dashboards

`ash
python launch_dual_dashboards.py
`

This starts:
- **Main Dashboard**: http://localhost:8501 (requires login)
- **Security Hub**: http://localhost:8502
- **L4 Explainability Hub**: http://localhost:8503

### Launch Individual Components

`ash
# Main Dashboard only
streamlit run dashboard/app.py

# Security Hub only
python dashboard/hub_flask_app.py

# L4 Explainability Hub only
python dashboard/hub_explainability_app.py
`

##  Technology Stack

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| Main Dashboard | Streamlit 1.28+ | 8501 | L1-L5 compliance overview |
| Security Hub | Flask 3.1.2 + Chart.js | 8502 | Security/Privacy deep-dive |
| L4 Hub | Flask 3.1.2 + Chart.js | 8503 | Explainability assessment |
| Backend | Python 3.10+ | - | Core logic & APIs |
| Database | SQLite/PostgreSQL | - | Audit logs & history |

##  Authentication

**Default Credentials** (change in production):
- **Username**: admin
- **Password**: admin_default_123

Security hubs are accessible without authentication (open API access).

##  Documentation

- README.md - Project overview and setup
- QUICK_START.md - Step-by-step getting started guide
- SECURITY_HUB_ENHANCEMENTS.md - Security hub deep-dive

##  Project Structure

`
IRAQAF/
 dashboard/
    app.py                      # Main Streamlit dashboard
    hub_flask_app.py            # Security & Privacy Hub
    hub_explainability_app.py   # L4 Explainability Hub
    modules/                    # L1-L5 module implementations
 launch_dual_dashboards.py       # Universal launcher script
 requirements.txt                # Python dependencies
 README.md                       # This file
`

##  API Endpoints

### Security Hub (Port 8502)
- GET / - Dashboard HTML
- GET /api/modules - All security modules
- GET /api/module/<name> - Specific module data
- GET /api/check/<check_name> - Individual check status
- GET /health - Health check

### L4 Explainability Hub (Port 8503)
- GET / - Dashboard HTML
- GET /api/modules - All explainability modules (12 checks)
- GET /api/categories - 4-category breakdown
- GET /api/transparency-score - Overall transparency score
- GET /api/tests - Test results (fidelity, consistency, stability, audit)
- GET /health - Health check

##  L4 Explainability Hub Details

The dedicated L4 hub assesses explainability across 4 categories:

### Category A: Explanation Capability (35%)
- Explanation Method Implementation
- Explanation Quality & Format
- Coverage & Completeness

### Category B: Explanation Reliability (30%)
- Fidelity Testing (>0.5 threshold)
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

##  Testing

`ash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_app.py -v
`

##  Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit changes (git commit -m 'Add AmazingFeature')
4. Push to branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see LICENSE.md for details.

##  Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: support@iraqaf.example.com
- Documentation: https://iraqaf.readthedocs.io

---

**Last Updated**: November 19, 2025
**Version**: 2.0 (Dual Dashboard + L4 Hub)
**Status**:  Production Ready
