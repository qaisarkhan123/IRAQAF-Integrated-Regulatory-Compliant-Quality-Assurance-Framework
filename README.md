# 🚀 IRAQAF - Integrated Regulatory Compliant Quality Assurance Framework

**Enterprise-grade AI compliance, security, and quality assurance platform**

---

## 🎯 Project Status

**✅ PRODUCTION READY** | **7 Operational Hubs** | **Flask Dashboard** | **Enhanced Authentication**

### The 7-Hub Ecosystem

| Hub | Port | Purpose | Status |
|-----|------|---------|--------|
| **L1 Regulations & Governance** | 8504 | Compliance requirements foundation | ✅ Live |
| **L2 Privacy & Security** | 8502 | Privacy/security requirements | ✅ Live |
| **L3 Fairness & Ethics** | 8506 | Fairness evaluation & ethics | ✅ Live |
| **L4 Explainability & Transparency** | 5000 | AI transparency & explainability | ✅ Live |
| **System Operations & QA Monitor (SOQM)** | 8503 | System operations & QA monitoring | ✅ Live |
| **Unified QA Orchestrator (UQO)** | 8507 | Unified QA orchestration | ✅ Live |
| **Continuous Assurance Engine (CAE)** | 8508 | Continuous assurance engine | ✅ Live |

---

## 🚀 Quick Start

### Start Main Flask Dashboard
```bash
python dashboard/flask_app.py
```
**Access**: http://localhost:8510
**Login**: admin / admin

### Start All Hubs (Automated)
```bash
# Windows
start_all_hubs.bat

# Or individually:
python dashboard/l1_regulations_governance_hub.py
python dashboard/privacy_security_hub.py
python dashboard/l3_fairness_ethics_hub.py
python dashboard/hub_explainability_app.py
python dashboard/l3_operations_control_center.py
python simple_uqo.py
python module5_core.py
```

### Access Points
- **🎛️ Main Flask Dashboard**: http://localhost:8510 (Enhanced UI/UX)
- **⚖️ L1 Regulations & Governance**: http://localhost:8504
- **🔐 L2 Privacy & Security**: http://localhost:8502
- **⚖️ L3 Fairness & Ethics**: http://localhost:8506
- **🔍 L4 Explainability & Transparency**: http://localhost:5000
- **⚙️ SOQM**: http://localhost:8503
- **📊 UQO**: http://localhost:8507
- **🤖 CAE**: http://localhost:8508

---

## 🎯 Hub Navigation Flow

The hubs follow a logical evaluation workflow:

```
⚖️ L1 Regulations & Governance
           ↓
🔐 L2 Privacy & Security  
           ↓
⚖️ L3 Fairness & Ethics
           ↓
🔍 L4 Explainability & Transparency
           ↓
⚙️ System Operations & QA Monitor (SOQM)
           ↓
📊 Unified QA Orchestrator (UQO)
           ↓
🤖 Continuous Assurance Engine (CAE)
```

---

## 🎨 Flask Dashboard Features

### 🔐 Enhanced Authentication System
- **2FA Support**: Time-based OTP with QR codes
- **Role-based Access**: Admin, Analyst, Viewer roles
- **Account Security**: Lockout protection, audit logging
- **Password Security**: PBKDF2 hashing, breach detection
- **Session Management**: Secure session handling

### 🎛️ Modern UI/UX
- **Dark Theme Sidebar**: Professional glass morphism design
- **Real-time Monitoring**: Live hub status and metrics
- **Interactive Charts**: Plotly-powered visualizations
- **Responsive Design**: Mobile-friendly interface
- **Quick Actions**: Direct hub access and management

### 📊 Dashboard Components
- **Hub Status Overview**: Real-time health monitoring
- **Key Performance Metrics**: CRS, SAI, FI, TS scores
- **Alert Management**: System-wide alert aggregation
- **Analytics**: Interactive charts and trend analysis
- **Settings**: User preferences and configuration

---

## 📊 Key Features

### 🏛️ L1 Regulations & Governance Hub
- **8 Regulatory Frameworks**: GDPR, EU AI Act, ISO 13485, HIPAA, NIST 800-series, PCI-DSS, SOX, CCPA
- **Compliance Readiness Score (CRS)**: Weighted assessment across 5 dimensions
- **Evidence Management**: SQLite-based evidence tracking
- **Automatic Regulation Updates**: Web scraping with drift detection
- **SDLC Compliance Tracking**: 6-phase development lifecycle monitoring

### 🔐 L2 Privacy & Security Hub  
- **11 Security Modules**: Comprehensive privacy and security assessment
- **Security Assurance Index (SAI)**: Formal category-based scoring
- **Composite Metrics**: DLP, ES, ARI with technical depth
- **Enhanced Threat Modeling**: Advanced security analysis

### ⚖️ L3 Fairness & Ethics Hub
- **Fairness Metrics**: DPG, EOG, Equalized Odds, Subgroup Accuracy
- **Fairness Index (FI)**: 0-100 scale fairness assessment
- **Ethical Maturity Level (EML)**: 1-5 governance maturity scale
- **Protected Group Analysis**: Multi-attribute fairness evaluation

### 🔍 L4 Explainability & Transparency Hub
- **Named Metrics**: EFI, FIC, AIx, TS with formal definitions
- **Transparency Score (TS)**: Weighted 4-category assessment
- **SHAP/LIME Integration**: Advanced explainability techniques
- **Auditability Tracking**: Comprehensive audit trail management

### ⚙️ System Operations & QA Monitor (SOQM)
- **8-Phase Monitoring**: Complete IRAQAF platform oversight
- **Infrastructure Health**: Real-time system status monitoring
- **Performance Metrics**: Response times, coverage, test results
- **Enhanced UI**: Beautiful dashboard with structured data display

### 📊 Unified QA Orchestrator (UQO)
- **Cross-Hub Integration**: Aggregates all 6 hub assessments
- **Unified CQS Formula**: Configurable weighted scoring
- **Drift Awareness**: Performance, fairness, compliance monitoring
- **Historical Tracking**: QA trend analysis and alerting

### 🤖 Continuous Assurance Engine (CAE)
- **Deep Drift Detection**: PSI, KS tests, statistical monitoring
- **Anomaly Detection**: Advanced pattern recognition
- **Internal CQS**: Independent quality assessment
- **Real-time Alerts**: Immediate notification system

---

## 📚 Documentation

**Primary Documentation**: `IRAQAF_HUBS_COMPREHENSIVE_GUIDE.md`
- Complete hub specifications
- API endpoint documentation  
- Setup and deployment guides
- Score metrics explanations
- Troubleshooting guides

---

## 🛠️ Technology Stack

- **Frontend**: Flask with Jinja2 templates
- **Backend**: Flask (Main Dashboard + All Hubs)
- **Database**: SQLite (Evidence, Versioning, User Management)
- **APIs**: RESTful JSON endpoints
- **Authentication**: Enhanced 2FA with PyOTP
- **Monitoring**: Real-time metrics collection
- **Security**: PBKDF2 password hashing, session management
- **Visualization**: Plotly.js, Bootstrap 5, custom CSS

---

## 🎯 Use Cases

### Regulatory Compliance
- **AI Act Compliance**: Comprehensive EU AI Act assessment
- **GDPR Privacy**: Data protection and privacy evaluation
- **Medical Device**: ISO 13485 and FDA compliance tracking
- **Financial Services**: SOX and PCI-DSS compliance monitoring

### Quality Assurance  
- **Continuous Monitoring**: Real-time quality metrics
- **Drift Detection**: Performance and fairness degradation alerts
- **Cross-Hub Analysis**: Unified quality assessment
- **Historical Tracking**: Long-term quality trend analysis

### Risk Management
- **Fairness Evaluation**: Bias detection and mitigation
- **Security Assessment**: Comprehensive threat analysis
- **Explainability**: AI transparency and interpretability
- **Operational Health**: System performance monitoring

---

## 🚀 Getting Started

1. **Clone Repository**
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Start Flask Dashboard**: `python dashboard/flask_app.py`
4. **Access Dashboard**: http://localhost:8510 (Login: admin/admin)
5. **Launch Hubs**: Use `start_all_hubs.bat` or start individually
6. **Review Documentation**: `IRAQAF_HUBS_COMPREHENSIVE_GUIDE.md`

---

## 🔧 Project Structure

```
projectttt/
├── dashboard/
│   ├── flask_app.py              # Main Flask dashboard
│   ├── flask_auth_enhanced.py    # Enhanced authentication system
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html            # Base template with modern UI
│   │   ├── dashboard.html       # Main dashboard
│   │   ├── login.html           # Authentication page
│   │   └── ...
│   ├── services/
│   │   └── hub_service.py       # Hub management service
│   └── ...
├── README.md                     # This file
├── IRAQAF_HUBS_COMPREHENSIVE_GUIDE.md
├── requirements.txt
└── start_all_hubs.bat           # Automated hub launcher
```

---

**Enterprise AI Governance Made Simple** | **IRAQAF Platform v2.0 - Flask Edition**