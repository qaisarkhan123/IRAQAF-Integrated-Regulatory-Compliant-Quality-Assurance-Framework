# IRAQAF - Integrated Regulatory Compliant Quality Assurance Framework

A comprehensive AI quality assurance and regulatory compliance framework for evaluating AI systems across five critical domains with dedicated security assessment tools.

##  Overview

IRAQAF provides a modular approach to evaluate AI systems across:

- **L1 Governance & Regulatory** - Compliance requirements and audit trails
- **L2 Privacy & Security** - Data protection, encryption, and security controls
- **L3 Fairness** - Bias detection and fairness metrics
- **L4 Explainability & Transparency** - Model interpretability and transparency
- **L5 Operations & Monitoring** - Performance tracking and operational compliance

##  Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

\\\ash
# Clone and setup
git clone https://github.com/qaisarkhan123/IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework.git
cd IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
\\\

### Launch Dual Dashboard System

**Method 1: Automated Launcher (Recommended)**
\\\ash
python launch_dual_dashboards.py
\\\

**Method 2: Manual Launch**
\\\ash
# Terminal 1 - Main Dashboard (Port 8501)
streamlit run dashboard/app.py --server.port 8501

# Terminal 2 - Security Hub (Port 8502)
python dashboard/hub_flask_app.py
\\\

### Access Dashboard

Navigate to:
- **Main Dashboard**: http://localhost:8501
- **Security Hub**: http://localhost:8502

**Login Credentials**:
- **Username**: admin
- **Password**: admin_default_123

##  Dual Dashboard System

### Main Dashboard (Streamlit, Port 8501)

The primary dashboard includes:
1. **Evidence Management** - Upload, index, and manage compliance evidence
2. **Five Core Modules** (L1-L5) with metrics and assessments
3. **GQAS Aggregate Score** - Overall compliance scoring system
4. **Real-time Visualization** - Interactive charts and dashboards
5. **Export Capabilities** - CSV, PDF, JSON, Word formats
6. **Role-Based Access Control** - Admin, Analyst, Viewer roles
7. **Secure Authentication** - SHA-256 hashing with 8-hour timeout

### Privacy & Security Hub (Flask, Port 8502)

A lightweight, visualization-focused security assessment tool with 10 specialized modules.

**Features**:
-  Interactive visualizations with Chart.js
-  Ultra-fast startup (<2 seconds) with zero crashes
-  Beautiful responsive UI with dark gradient theme
-  RESTful API endpoints for integration
-  Real-time KPI cards and analytics dashboard

##  Technology Stack

| Component | Technology | Port |
|-----------|-----------|------|
| Main Dashboard | Streamlit 1.x | 8501 |
| Security Hub | Flask 3.1.2 + Chart.js | 8502 |
| Database | SQLite | N/A |
| Authentication | SHA-256 | N/A |

##  Security Features

- **End-to-end encryption** for sensitive data
- **Role-based access control (RBAC)** - Admin, Analyst, Viewer roles
- **Comprehensive audit logging** - Track all user actions
- **Secure session management** - 8-hour timeout with SHA-256 hashing
- **Input validation and sanitization** - Prevent injection attacks

##  Project Structure

\\\
IRAQAF/
 dashboard/              # Main Streamlit dashboards
    app.py             # Main dashboard (L1-L5, GQAS scoring)
    hub_flask_app.py   # Flask-based security hub
    auth_ui.py         # Authentication UI
    ...
 core/                  # Core modules
 configs/               # Configuration files
 data/                  # Data storage
 reports/               # Generated reports
 tests/                 # Test suite
 launch_dual_dashboards.py # Launcher script
 requirements.txt       # Dependencies
 README.md             # This file
\\\

##  Compliance Frameworks

- GDPR
- HIPAA
- PCI-DSS
- ISO 27001:2022
- NIST Cybersecurity Framework 2.0

##  Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Command reference guide
- **[SECURITY_HUB_ENHANCEMENTS.md](./SECURITY_HUB_ENHANCEMENTS.md)** - Hub features

##  Support

For issues or questions, visit the GitHub repository.

---

**Last Updated**: November 2025  
**Status**:  Production Ready  
**Version**: 2.1 (Flask Hub)
