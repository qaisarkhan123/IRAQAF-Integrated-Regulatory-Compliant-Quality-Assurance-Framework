# IRAQAF - Integrated Regulatory Compliant Quality Assurance Framework

A comprehensive AI quality assurance and regulatory compliance framework for evaluating AI systems across five critical domains.

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

```bash
# Clone and setup
git clone https://github.com/qaisarkhan123/IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework.git
cd IRAQAF-Integrated-Regulatory-Compliant-Quality-Assurance-Framework

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Launch Dashboard

```bash
streamlit run dashboard/app.py
```

Navigate to `http://localhost:8501` and log in with:
- **Username**: admin
- **Password**: admin_default_123

##  Dashboard Features

###  Authentication
- Secure login system with SHA-256 hashing
- Sign up functionality for new accounts
- Role-based access control (Admin, Analyst, Viewer)
- 8-hour session timeout for security

###  Evidence Management
Three organized tabs:
1. ** Upload & Pin** - Upload files, assign to modules with checkbox-based selector
2. ** Evidence Index** - View indexed files per module
3. ** Sync & Export** - Export reports and sync configurations

###  Module Coverage

| Module | Icon | Coverage |
|--------|------|----------|
| L1 Governance & Regulatory |  | Core audit and compliance tracking |
| L2 Privacy & Security |  | 11-category security assessment |
| L3 Fairness |  | Bias detection and fairness metrics |
| L4 Explainability |  | Model interpretability features |
| L5 Operations |  | Performance and monitoring |

###  Export Capabilities
- **CSV Export** - Structured data export with date range filtering
- **PDF Reports** - Professional PDF generation
- **JSON Export** - Machine-readable format
- **Word Documents** - DOCX format with formatting

###  UI/UX Highlights
- Clean, modern Streamlit interface
- Responsive checkbox-based module selector
- Color-coded alerts and status indicators
- Real-time data visualization
- Organized tabbed interface for better navigation

##  Project Structure

```
IRAQAF/
 dashboard/              # Main Streamlit dashboard
    app.py             # Main dashboard application
    auth_ui.py         # Authentication UI components
    export_alerts_rbac.py # Export, alerts, and RBAC managers
    ...
 core/                  # Core modules and utilities
 configs/               # Configuration files
 data/                  # Data storage and databases
 reports/               # Generated reports
 tests/                 # Test suite
 requirements.txt       # Python dependencies
```

##  Configuration

Configuration files are located in the `configs/` directory:
- `policies.yaml` - Security policies
- `compliance_map.yaml` - Compliance framework mappings
- `project.example.yaml` - Project configuration template

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

##  License

This project is part of the IRAQAF framework. See LICENSE file for details.

##  Support

For issues, questions, or contributions, please visit the GitHub repository.

---

**Last Updated**: November 2025
