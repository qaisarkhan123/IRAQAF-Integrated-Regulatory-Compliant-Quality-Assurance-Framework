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

`ash
# Clone and setup
git clone https://github.com/qaisarkhan123/IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework.git
cd IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
`

### Launch Dashboard

`ash
# Main Dashboard (Port 8501)
streamlit run dashboard/app.py --server.port 8501
`

Navigate to http://localhost:8501 and log in with:
- **Username**: admin
- **Password**: admin_default_123

##  Dashboard Features

###  Authentication
- Secure login system with SHA-256 hashing
- Sign up functionality for new accounts
- Role-based access control (Admin, Analyst, Viewer)
- 8-hour session timeout for security

###  Main Dashboard
The primary dashboard includes:
1. **Evidence Management** - Upload, index, and manage compliance evidence
2. **Five Core Modules** (L1-L5) with metrics and assessments
3. **GQAS Aggregate Score** - Overall compliance scoring system
4. **Real-time Visualization** - Interactive charts and dashboards
5. **Export Capabilities** - CSV, PDF, JSON, Word formats

###  Privacy & Security Hub
A dedicated security assessment tool on **Port 8502** accessible via:
- **Sidebar button** in main dashboard: " Privacy & Security Hub"
- **Direct URL**: http://localhost:8502

The hub provides 11 specialized security modules:
1. ** Dashboard Overview** - Security metrics and compliance status
2. ** PII Detection & Anonymization** - Personal data identification and protection
3. ** Encryption Validator** - Encryption strength and coverage analysis
4. ** Model Integrity Checker** - Model verification and tampering detection
5. ** Adversarial Attack Testing** - Security vulnerability testing
6. ** GDPR Rights Manager** - Right to access, erasure, and portability
7. ** L2 Historical Metrics** - Privacy & Security historical trends and analytics
8. ** MFA Manager** - Multi-factor authentication validation
9. ** Data Retention Manager** - Data lifecycle and retention policies
10. ** Quick Assessment Wizard** - Fast security assessment workflow

**Launch the Hub**:
`ash
# In a separate terminal
streamlit run dashboard/privacy_security_hub.py --server.port 8502
`

###  Evidence Management
Three organized tabs:
1. ** Upload & Pin** - Upload files, assign to modules with checkbox-based selector
2. ** Evidence Index** - View indexed files per module
3. ** Sync & Export** - Export reports and sync configurations

###  Module Coverage

| Module | Modules | Status |
|--------|---------|--------|
| **Main Dashboard (L1-L5)** | 5 core modules + GQAS scoring |  Running on 8501 |
| **Privacy & Security Hub** | 11 specialized security modules |  Running on 8502 |
| **L2 Assessments** | Integrated into Hub's "L2 Historical Metrics" module |  In Hub |

###  Export Capabilities
- **CSV Export** - Structured data export with date range filtering
- **PDF Reports** - Professional PDF generation
- **JSON Export** - Machine-readable format
- **Word Documents** - DOCX format with formatting

###  UI/UX Highlights
- Clean, modern Streamlit interface with gradient purple theme
- Responsive checkbox-based module selector
- Color-coded alerts and status indicators
- Real-time data visualization with Plotly
- Organized tabbed interface for better navigation
- Dedicated security hub for advanced assessments

##  Project Structure

`
IRAQAF/
 dashboard/              # Main Streamlit dashboards
    app.py             # Main dashboard application (L1-L5, GQAS scoring)
    privacy_security_hub.py # Dedicated security assessment hub
    auth_ui.py         # Authentication UI components
    export_alerts_rbac.py # Export, alerts, and RBAC managers
    l2_monitor_integration.py # L2 integration layer
    ...
 core/                  # Core modules and utilities
 configs/               # Configuration files
 data/                  # Data storage and databases
 reports/               # Generated reports
 tests/                 # Test suite
 requirements.txt       # Python dependencies
`

##  Configuration

Configuration files are located in the configs/ directory:
- policies.yaml - Security policies
- compliance_map.yaml - Compliance framework mappings
- project.example.yaml - Project configuration template

##  Compliance Frameworks

IRAQAF supports multiple compliance frameworks:
- GDPR
- HIPAA
- PCI-DSS
- ISO 27001:2022
- NIST Cybersecurity Framework 2.0

##  Security

- End-to-end encryption for sensitive data
- Role-based access control (RBAC)
- Comprehensive audit logging
- Secure session management
- Input validation and sanitization
- Dedicated security assessment hub with 11 specialized modules

##  Architecture Highlights

- **Modular Design**: Independent modules can be deployed separately
- **Dual Dashboard System**: Main dashboard for L1-L5 overview, Hub for advanced security assessments
- **Real-time Scoring**: Aggregate GQAS score includes Privacy & Security Hub assessments
- **Compliance Mapping**: Built-in framework mappings for GDPR, HIPAA, and other standards

##  License

This project is part of the IRAQAF framework. See LICENSE file for details.

##  Support

For issues, questions, or contributions, please visit the GitHub repository.

---

**Last Updated**: November 2025
**Status**:  Production Ready
