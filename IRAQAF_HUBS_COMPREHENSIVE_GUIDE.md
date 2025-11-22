# IRAQAF Platform - Comprehensive Hub Modules Guide

**Version:** 2.1 - Flask Edition  
**Last Updated:** November 22, 2025  
**Platform:** Integrated Regulatory Compliance & Quality Assurance Framework (IRAQAF)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Flask Dashboard](#flask-dashboard)
3. [L1 Regulations & Governance Hub](#l1-regulations--governance-hub)
4. [L2 Privacy & Security Hub](#l2-privacy--security-hub)
5. [L3 Fairness & Ethics Hub](#l3-fairness--ethics-hub)
6. [L4 Explainability & Transparency Hub](#l4-explainability--transparency-hub)
7. [System Operations & QA Monitor (SOQM)](#system-operations--qa-monitor-soqm)
8. [Unified QA Orchestrator (UQO)](#unified-qa-orchestrator-uqo)
9. [Continuous Assurance Engine (CAE)](#continuous-assurance-engine-cae)
10. [Quick Reference](#quick-reference)
11. [API Endpoints Summary](#api-endpoints-summary)

---

## Overview

The IRAQAF platform consists of **7 specialized hub modules** plus 1 Flask-based main dashboard that together provide comprehensive quality assurance, compliance monitoring, and regulatory oversight for AI systems. Each hub focuses on specific aspects of quality, security, compliance, and operational excellence.

### 🎛️ Flask Dashboard (NEW)
- **URL**: http://localhost:8510
- **Technology**: Flask with enhanced authentication
- **Features**: Modern UI/UX, real-time monitoring, 2FA support
- **Login**: admin / admin (default credentials)

### 🚀 Hub Navigation Order

The hubs follow a logical evaluation workflow that mirrors real-world AI governance processes:

1. **⚖️ L1 Regulations & Governance** - Every evaluation begins with compliance requirements
2. **🔐 L2 Privacy & Security** - Regulations lead into privacy/security requirements  
3. **⚖️ L3 Fairness & Ethics** - Sits between privacy and explainability as per frameworks
4. **🔍 L4 Explainability & Transparency** - AI Act places XAI after fairness & risk checks
5. **⚙️ System Operations & QA Monitor (SOQM)** - Infrastructure health check before aggregation
6. **📊 Unified QA Orchestrator (UQO)** - Top-level aggregator of all hubs
7. **🤖 Continuous Assurance Engine (CAE)** - Deep drift, anomaly, and internal CQS engine

### Hub Navigation Flow

```
🚀 HUB NAVIGATION

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

### 📊 Role of Each Hub

| Hub | Purpose | Output | Role in QA |
|-----|---------|--------|------------|
| **L1** | Regulatory compliance | CRS | Legal compliance |
| **L2** | Security & privacy | SAI | Data protection |
| **L3** | Fairness & ethics | FI, EML | Bias & ethics |
| **L4** | Explainability | TS, EFI, FIC, AIx | Transparency |
| **SOQM** | System health | OPS Score | Infra reliability |
| **UQO** | Aggregator | CQS | Executive view |
| **CAE** | Drift detection | Internal CQS | Continuous monitoring |

### 🏗️ AI Quality Assurance Layers

```
AI Quality Assurance Layers
-----------------------------------
| L1 Regulatory Compliance         |
| L2 Security & Privacy            |
| L3 Fairness & Ethics             |
| L4 Explainability & Transparency |
-----------------------------------
| SOQM  (System Operations Health) |
-----------------------------------
| CAE   (Drift & Anomaly Engine)   |
-----------------------------------
| UQO   (Unified QA Orchestrator)  |
-----------------------------------
| Main Dashboard (Access Layer)    |
-----------------------------------
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN DASHBOARD (Port 8501)                │
│              Authentication + Unified Interface              │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  L1 Regs &    │ │ L2 Privacy  │ │ L3 Fairness │
│  Governance   │ │ & Security  │ │ & Ethics    │
│     (8504)    │ │    (8502)   │ │   (8506)    │
└───────────────┘ └─────────────┘ └─────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼───────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ L4 Explain &  │ │    SOQM     │ │     UQO     │
│ Transparency  │ │   (8503)    │ │   (8507)    │
│     (5000)    │ └─────────────┘ └─────────────┘
└───────────────┘         │
                 ┌────────▼────────┐
                 │      CAE        │
                 │     (8508)      │
                 └─────────────────┘
```

### 🔄 Key Architectural Features

#### **Regulatory Auto-Update & Drift Monitoring**

The IRAQAF platform features **automated regulatory monitoring** as a core architectural component:

- **Continuous Monitoring:** L1 Hub automatically monitors GDPR, EU AI Act, and HIPAA for changes
- **Version Control:** All regulation changes are versioned and tracked
- **Drift Detection:** Automatic detection of compliance drift when regulations change
- **Admin Approval:** Semi-automatic updates with human oversight
- **Impact Analysis:** Assessment of how regulatory changes affect compliance scores

**Implementation:**
```python
# Regulatory monitoring workflow
regulation_sources.json → RegulationUpdateService → 
version_comparison → drift_detection → admin_approval → 
compliance_recalculation → stakeholder_notification
```

**Benefits:**
- **Proactive Compliance:** Stay ahead of regulatory changes
- **Risk Mitigation:** Early warning of compliance gaps
- **Audit Trail:** Complete history of regulatory updates
- **Automated Workflows:** Reduce manual monitoring overhead

---

## Flask Dashboard

**Port:** 8510  
**Technology:** Flask with Jinja2 templates  
**Access:** `http://localhost:8510`  
**Requires:** Enhanced Authentication (2FA support)

### Purpose
Modern Flask-based central hub providing unified access to all IRAQAF modules with enhanced authentication, real-time monitoring, and professional UI/UX.

### Key Features
- **Authentication System**: User login, role-based access control (Admin, Analyst, Viewer)
- **Unified Navigation**: Direct links to all 6 hub modules
- **Session Management**: Track user activity, session duration, and actions
- **Integrated Reporting**: Aggregated view of all quality scores (GQAS - Global Quality Assurance Score)
- **Evidence Management**: Upload and manage supporting documents
- **Audit Logging**: Comprehensive audit trails for all actions
- **Theme Support**: Light/Dark mode with auto-detection
- **Interactive Tour**: Guided tour of dashboard features

### Modules Assessed
- L1: Regulations & Governance
- L2: Privacy & Security
- L3: Fairness & Ethics
- L4: Explainability & Transparency
- L5: Operations & Monitoring

### Authentication
- Default credentials: `admin` / `admin_default_123` (for demo)
- User management with roles and permissions
- Session-based authentication with automatic logout

---

## L4 Explainability Hub

🔍 **Port:** 5000  
**Technology:** Flask  
**Access:** `http://localhost:5000`  
**File:** `dashboard/hub_explainability_app.py`

### Purpose
Comprehensive assessment tool for AI system transparency, explainability, and interpretability. Evaluates how well AI systems can explain their decisions and predictions.

### Core Assessment Areas

#### 1. Explanation Generation Capability (35% weight)
- **Explanation Methods** (35%)
  - SHAP (SHapley Additive exPlanations) implementation
  - LIME (Local Interpretable Model-agnostic Explanations)
  - Model type coverage (7/8 major model types)
  - Automation level (95% auto-generated)
  - **Current Score:** 92/100

- **Explanation Quality** (35%)
  - Human-readable format (12-grade reading level)
  - Clinical relevance and meaningfulness
  - Visual clarity with interactive charts
  - Technical accuracy
  - **Current Score:** 88/100

- **Coverage & Completeness** (30%)
  - Binary classifications: 100% coverage
  - Multi-class predictions: 90% coverage
  - Regression predictions: 80% coverage
  - Probability distributions: 75% coverage
  - **Current Score:** 85/100

#### 2. Explanation Reliability (30% weight)
- **Fidelity Testing** (40%)
  - Feature masking tests
  - Prediction reconstruction accuracy
  - Feature impact accuracy
  - Threshold: >50% (Current: 72%)
  - **Current Score:** 72/100

- **Feature Consistency** (35%)
  - Jaccard similarity for similar cases
  - Feature overlap analysis
  - Ranking consistency (Spearman correlation)
  - Target: >0.70 (Current: 0.68)
  - **Current Score:** 68/100

- **Stability Testing** (25%)
  - Robustness to input noise
  - Spearman rank correlation under perturbations
  - Feature ranking stability
  - **Current Score:** 85/100

#### 3. Traceability & Auditability (25% weight)
- **Prediction Logging** (35%)
  - Complete field logging (18 fields per prediction)
  - Immutable, hash-verified records
  - UTC timestamp tracking
  - **Current Score:** 100/100

- **Model Versioning** (30%)
  - Version tracking with Git commit hashes
  - Training history documentation
  - Hyperparameter documentation
  - Parent model lineage tracking
  - **Current Score:** 95/100

- **Audit Trail** (35%)
  - Complete explanation history
  - User action logging
  - Change tracking
  - Compliance-ready reports
  - **Current Score:** 92/100

#### 4. Comprehensibility (10% weight)
- **User Understanding Tests**
  - User comprehension surveys
  - Explanation effectiveness metrics
  - Feedback collection
  - **Current Score:** 78/100

### Named Explainability Metrics

The L4 Hub provides four named composite metrics for advanced explainability analysis:

#### 1. Transparency Score (TS)
- **Scale:** 0-100 (higher is better)
- **Formula:** Weighted combination of explainability blocks
  - Explanation Generation Capability (35% weight)
  - Explanation Reliability (30% weight)
  - Traceability & Auditability (25% weight)
  - Comprehensibility (10% weight)
- **Purpose:** Overall explainability and transparency assessment
- **Formula:** `TS = 0.35 × EGC + 0.30 × ERF + 0.25 × TA + 0.10 × CU`
- **Current Value:** ~85/100

#### 2. Explainability Fidelity Index (EFI)
- **Scale:** 0-100 (higher is better)
- **Formula:** Weighted combination of fidelity testing components
  - Prediction reconstruction accuracy (40% weight)
  - Feature impact alignment (30% weight)
  - Masking consistency (30% weight)
- **Purpose:** Measures how accurately explanations reflect model behavior
- **Current Value:** ~72/100

#### 3. Feature Importance Consistency (FIC)
- **Scale:** 0-100 (higher is better)
- **Formula:** Weighted combination of consistency metrics
  - Jaccard similarity (50% weight)
  - Spearman rank correlation, normalized to 0-1 (50% weight)
- **Purpose:** Assesses stability of feature importance across similar inputs
- **Current Value:** ~80/100

#### 4. Auditability Index (AIx)
- **Scale:** 0-100 (higher is better)
- **Formula:** Weighted combination of traceability components
  - Prediction logging score (35% weight)
  - Model versioning score (30% weight)
  - Audit trail score (35% weight)
- **Purpose:** Evaluates completeness of logs, versioning, and audit trails
- **Current Value:** ~98/100

### API Endpoints

- `GET /` - Main dashboard interface
- `GET /api/modules` - List all explainability modules
- `GET /api/categories` - Get assessment categories
- `GET /api/transparency-score` - Overall Transparency Score (TS) using formal weighted formula
  - Returns: TS, block scores (EGC, ERF, TA, CU), category breakdown
- `GET /api/explainability-metrics` - **NEW:** Get all composite metrics in one response
  - Returns:
    - `transparency_score`: TS (overall Transparency Score)
    - `efi`: Explainability Fidelity Index
    - `fic`: Feature Importance Consistency
    - `auditability_index`: Auditability Index (AIx)
    - `blocks`: Block-level scores (explanation_generation, explanation_reliability, traceability_auditability, comprehensibility)
    - `timestamp`: ISO timestamp
- `GET /api/tests` - Run explainability tests
- `GET /api/interpretability/shap` - SHAP visualizations
- `GET /api/interpretability/lime` - LIME explanations
- `GET /api/interpretability/gradcam` - GradCAM visualizations
- `GET /api/interpretability/decision-path` - Decision path analysis
- `GET /api/interpretability/all` - All interpretability data
- `GET /health` - Health check

### Key Features
- Interactive visualizations (SHAP force plots, waterfall charts)
- Real-time explainability calculations
- Multi-model support (gradient boosting, neural networks, etc.)
- Automated explanation generation
- Detailed scoring breakdowns with formulas
- Visual charts and graphs for each metric

### Use Cases
- Regulatory compliance verification (EU AI Act, FDA guidance)
- Model transparency audits
- Stakeholder communication
- Debugging model decisions
- Clinical/medical AI system validation

---

## L2 Privacy & Security Hub

🔐 **Port:** 8502  
**Technology:** Flask  
**Access:** `http://localhost:8502`  
**File:** `dashboard/privacy_security_hub.py`

### Purpose
Comprehensive security and privacy assessment hub with 11 specialized modules evaluating data protection, encryption, access control, threat detection, and compliance.

### Security Assessment Modules

#### Privacy Mechanisms Category

1. **Anonymization & De-identification** (Score: 48/100)
   - K-anonymity implementation (current k=3, target ≥5)
   - Differential privacy (ε = 0.8)
   - Re-identification risk: 42%
   - PII detection rate: 92%
   - **Recommendations:**
     - Increase k-anonymity to 5-8
     - Reduce ε to 0.5 for stronger privacy
     - Implement t-closeness for sensitive attributes

2. **PII Detection & Extraction** (Score: 92/100)
   - Email detection: 99% accuracy
   - SSN detection: 97% accuracy
   - Phone number: 95% accuracy
   - Name extraction: 92% accuracy
   - False positive rate: 1%

3. **Data Minimization & Retention** (Score: 70/100)
   - Field justification: 78%
   - Retention compliance: 85%
   - Unnecessary fields: 12 identified
   - GDPR compliance: 100%

#### Model Integrity Category

4. **Model Security & Adversarial Testing** (Score: 96/100)
   - Model integrity: 100% (SHA-256 verified)
   - FGSM attack success: 8% (excellent)
   - Membership inference: 5%
   - Adversarial robustness: 92%

#### System Security Category

5. **Encryption Validator** (Score: 88/100)
   - AES-256 coverage: 100% at rest
   - TLS 1.3 endpoints: 95%
   - Key rotation compliance: 85%
   - Certificate validity: 45 days remaining

6. **Access Control (RBAC)** (Score: 90/100)
   - RBAC coverage: 95%
   - Principle of Least Privilege: 88%
   - MFA adoption: 85%
   - Unauthorized blocks: 403 this month

7. **Threat Detection** (Score: 87/100)
   - True positive rate: 92%
   - SIEM uptime: 99.8%
   - Detection latency: 2.3 seconds
   - Threats detected: 47 this month

8. **API Security** (Score: 86/100)
   - Rate limiting: 95% of endpoints
   - API authentication: 92%
   - Input validation: 88%
   - CORS configuration: 90%

#### Governance Category

9. **Data Retention** (Score: 85/100)
   - Retention compliance: 85%
   - Deletion success rate: 92%
   - Archive indexing: 78%
   - Regulatory coverage: 88%

10. **GDPR Compliance** (Score: 84/100)
    - Data subject rights: 100% implemented
    - Consent management: 95%
    - DPA documentation: 88%
    - Privacy by Design: 85%

11. **Audit Logging** (Score: 89/100)
    - Event capture rate: 99%
    - Forensic traceability: 92%
    - Log retention: 2 years
    - HIPAA compliance: 100%

### Overall SAI Score (Formal Category-Based Formula)

The Security Assurance Index (SAI) uses a formal weighted formula based on security categories:

**SAI = 0.30 × DataPrivacy + 0.25 × ModelIntegrity + 0.25 × SystemSecurity + 0.20 × Governance**

#### Category Breakdown:
- **Data Privacy** (30% weight): Average of Anonymization, PII Detection, Data Minimization
- **Model Integrity** (25% weight): Model Security & Adversarial Testing
- **System Security** (25% weight): Average of Encryption, Access Control, Threat Detection, API Security
- **Governance** (20% weight): Average of Data Retention, GDPR Compliance, Audit Logging

- **Current SAI:** ~84/100 (calculated using formal formula)
- **Previous SAI:** 52/100
- **Improvement:** +32 points
- **Modules Passing (≥70):** 10/11

### Composite Security Metrics

The L2 Hub provides three derived composite metrics for advanced security analysis:

#### 1. Data Leakage Probability (DLP)
- **Scale:** 0-100 (lower is better)
- **Formula:** Weighted combination of:
  - Membership inference success rate (40% weight)
  - Re-identification risk (40% weight)
  - PII detection performance (20% weight, inverted)
- **Purpose:** Assesses risk of data leakage through model outputs or de-anonymization
- **Current Value:** ~19/100 (low risk)

#### 2. Encryption Score (ES)
- **Scale:** 0-100 (higher is better)
- **Formula:** Weighted combination of:
  - AES-256 coverage (30% weight)
  - TLS 1.3 endpoint coverage (30% weight)
  - Key rotation compliance (20% weight)
  - Certificate health status (20% weight)
- **Purpose:** Evaluates overall encryption strength across data at rest and in transit
- **Current Value:** ~95/100 (excellent)

#### 3. Attack Robustness Index (ARI)
- **Scale:** 0-100 (higher is better)
- **Formula:** Multiplicative combination of:
  - Adversarial robustness score (0-100)
  - Attack success rate penalty (1 - FGSM success rate)
  - Model integrity factor (1.0 if verified, 0.5 if not)
- **Purpose:** Measures model resilience against adversarial attacks
- **Current Value:** ~85/100 (strong robustness)

### API Endpoints

- `GET /` - Main dashboard with all modules
- `GET /api/module/<module_name>` - Get detailed module assessment
  - Module names: `anonymization`, `model-security`, `data-minimization`, `pii-detection`, `encryption`, `retention`, `access-control`, `threat-detection`, `gdpr`, `audit-logging`, `api-security`
- `GET /api/sai` - Get overall SAI score breakdown (uses formal category-based formula)
  - Returns: SAI score, category breakdown, module scores, simple average (for comparison)
- `GET /api/metrics` - **NEW:** Get all composite metrics in one response
  - Returns:
    - `sai`: Overall SAI score (category-based formula)
    - `categories`: Category breakdown (data_privacy, model_integrity, system_security, governance)
    - `dlp`: Data Leakage Probability (0-100)
    - `encryption_score`: Encryption Score (0-100)
    - `attack_robustness_index`: Attack Robustness Index (0-100)
    - `module_scores`: Individual module scores
    - `timestamp`: ISO timestamp

### Key Features
- Detailed reasoning for each score
- Visual charts and gauges for metrics
- Category-based organization
- Improvement recommendations
- Interactive module cards
- Real-time assessment updates

### Use Cases
- Security audits and compliance reviews
- Privacy impact assessments (PIA/DPIA)
- GDPR compliance verification
- HIPAA compliance checks
- SOC 2 audit preparation
- Penetration testing results tracking

---

# IRAQAF Multi-Hub Architecture (7 Modules)

## L1 Regulations Hub

⚖️ **Port:** 8504  
**Technology:** Flask  
**Access:** `http://localhost:8504`  
**File:** `dashboard/l1_regulations_governance_hub.py`

### Purpose
Regulatory compliance and governance hub tracking adherence to multiple regulatory frameworks including GDPR, HIPAA, PCI-DSS, SOX, NIST, and EU AI Act.

### Core Functionality

#### Regulatory Frameworks Supported
- **GDPR** (General Data Protection Regulation)
- **HIPAA** (Health Insurance Portability and Accountability Act)
- **PCI-DSS** (Payment Card Industry Data Security Standard)
- **SOX** (Sarbanes-Oxley Act)
- **NIST** (National Institute of Standards and Technology)
- **EU AI Act** (European Union AI Regulation)
- **CCPA** (California Consumer Privacy Act)

#### Assessment Areas
1. **Compliance Scoring**
   - Clause-by-clause analysis
   - Requirement mapping
   - Evidence collection
   - Gap identification

2. **Governance Tracking**
   - Policy compliance
   - Procedure adherence
   - Documentation completeness
   - Review cycles

3. **Regulatory Alignment**
   - Framework comparison
   - Cross-compliance mapping
   - Overlapping requirements
   - Risk assessment

### API Endpoints

- `GET /` - Main dashboard interface
- `GET /api/score` - Overall compliance score
- `GET /api/compliance` - Detailed compliance breakdown
- `GET /api/governance` - Governance metrics
- `GET /api/status` - Hub status and health

### Key Features
- Multi-framework compliance tracking
- Clause-level assessment
- Evidence management
- Compliance gap analysis
- Automated compliance scoring
- Regulatory requirement mapping

### Regulatory Auto-Update & Drift Monitoring

#### Overview
The L1 Regulations Hub includes an advanced **Regulation Update Service** that automatically monitors, fetches, and tracks updates to regulatory frameworks (GDPR, EU AI Act, HIPAA, etc.) from official sources.

#### Key Features

##### 1. Automatic Regulation Monitoring
- **Periodic Polling**: Automatically checks official regulatory sources at configurable intervals (default: 24 hours)
- **Multi-Source Support**: Fetches from HTML pages, RSS feeds, and APIs
- **Change Detection**: Compares new content with stored versions to detect updates
- **Version Management**: Stores complete version history of regulation texts

##### 2. Regulation Versioning System
- **Database Schema**:
  - `regulation_versions`: Stores full text snapshots of regulations with timestamps
  - `regulation_changes`: Tracks changes between versions with diff summaries
  - `polling_status`: Monitors polling status and schedules
- **Version Tags**: Automatic tagging (e.g., "20250115_official")
- **Text Hashing**: SHA-256 hashing for efficient change detection

##### 3. Change Detection & Diff Generation
- **Unified Diff**: Generates structured diffs showing added/removed/changed sections
- **Change Summary**: Human-readable summaries of changes detected
- **Impact Assessment**: Identifies scope and magnitude of changes

##### 4. Semi-Automatic Update Workflow
- **Default Mode**: Changes detected but require manual approval before activation
- **Auto-Apply Option**: Configurable flag (`AUTO_APPLY_REGULATION_UPDATES`) for automatic activation
- **Admin Approval**: Approve/reject workflow for regulation updates
- **Audit Trail**: Complete tracking of who approved/rejected changes and when

##### 5. Regulatory Drift Detection
- **Integration**: Automatically detected by compliance drift monitor
- **CRS Impact**: Pending updates apply penalty to Compliance Readiness Score (up to 20% reduction)
- **Alert System**: Visual banners and notifications in dashboard
- **Priority Flagging**: Critical regulatory changes highlighted separately

##### 6. Admin Workflow Endpoints
- `GET /api/regulations/updates` - List all pending updates requiring review
- `GET /api/regulations/drift` - Get regulatory drift status by framework
- `POST /api/regulations/approve/<id>` - Approve and activate a regulation update
- `POST /api/regulations/reject/<id>` - Reject an update
- `POST /api/regulations/check-updates` - Manually trigger update check

##### 7. Configuration
**File**: `dashboard/configs/regulation_sources.json`

```json
[
  {
    "framework": "GDPR",
    "source_type": "html",
    "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679",
    "poll_interval_hours": 24
  },
  {
    "framework": "EU_AI_ACT",
    "source_type": "html",
    "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
    "poll_interval_hours": 24
  }
]
```

##### 8. Integration with CRS
When pending regulation changes exist:
- **Penalty Calculation**: 5% CRS reduction per pending update (max 20%)
- **Visual Indicators**: Warning badges and reduced score display
- **Recalculation**: CRS automatically recalculated after approval/rejection

##### 9. UI Features
- **Updates Tab**: Dedicated tab showing all pending regulation updates
- **Overview Banner**: Alert banner on main dashboard when updates detected
- **Approval Interface**: One-click approve/reject buttons for each update
- **Diff Preview**: View what changed between versions
- **Status Indicators**: Visual status for each framework's update state

##### 10. Background Scheduler
- **Automatic Operation**: Background thread runs continuously
- **Smart Polling**: Only polls frameworks when scheduled (based on `poll_interval_hours`)
- **Error Handling**: Graceful handling of network errors, with retry logic
- **Status Tracking**: Polling status tracked in database for monitoring

##### 11. Supported Frameworks
Currently monitored:
- **GDPR**: EUR-Lex official text
- **EU AI Act**: EUR-Lex official text
- **HIPAA**: HHS.gov official information
- **PCI-DSS**: PCI Security Standards Council documentation
- **ISO 13485**: ISO official standard information

##### 12. Database Structure
```sql
regulation_versions:
  - id, framework, version_tag, raw_text, text_hash
  - created_at, is_active, source_url

regulation_changes:
  - id, framework, old_version_id, new_version_id
  - diff_summary, diff_details
  - requires_review, approved, rejected
  - created_at, reviewed_at, reviewed_by

polling_status:
  - framework, last_polled, next_poll
  - status, error_message
```

### Use Cases
- Multi-regulatory compliance audits
- Cross-framework gap analysis
- Regulatory change impact assessment
- Compliance reporting for auditors
- Policy development and review
- **Automatic regulation change detection**
- **Regulatory drift monitoring**
- **Version-controlled compliance tracking**

---

## System Operations & QA Monitor (SOQM)

⚙️ **Port:** 8503  
**Technology:** Flask  
**Access:** `http://localhost:8503`  
**File:** `dashboard/l3_operations_control_center.py`

### Purpose
Operational cockpit providing real-time status, metrics, and controls for all 8 phases of the IRAQAF platform. Designed for developers and operators to monitor system health and performance.

### 8 Phases Monitored

#### Phase 1: Architecture & Design
- System architecture overview
- Module structure
- Core files tracking
- Component status

#### Phase 2: Database Layer
- Database connection status
- Table schemas
- Data operations
- Query performance
- **Technology:** SQLAlchemy ORM (SQLite/PostgreSQL)

#### Phase 3: Web Scrapers
- Scraper status
- Scheduler status
- Scraping jobs
- Data collection metrics

#### Phase 4: NLP Pipeline
- Natural Language Processing status
- Search functionality
- Text processing pipelines
- Entity extraction

#### Phase 5: Compliance Scoring
- Scoring engine status
- Score calculation
- Results generation
- Performance metrics

#### Phase 6: Change Monitoring
- Change detection
- Alert system
- Impact analysis
- Notification status

#### Phase 7: API/CLI
- REST API endpoints
- CLI commands
- Endpoint health
- Performance monitoring

#### Phase 8: Testing
- Test coverage
- Test results
- Code coverage metrics
- Testing pipeline status

### Key Metrics Displayed
- **Total Tests:** 105+ (98.1% pass rate)
- **Code Coverage:** 89%
- **API Endpoints:** 19+ (all operational)
- **Requirements:** 105 regulations covered
- **System Status:** OPERATIONAL
- **Coverage:** 89%

### API Endpoints

- `GET /` - Main operations dashboard
- `GET /api/status` - Overall system status
- `GET /api/phase/<phase_id>` - Get specific phase details (1-8)
- `GET /api/health` - Health check endpoint

### Key Features
- Real-time phase status monitoring
- Expandable phase cards
- Code coverage visualization
- API endpoint listing
- System health indicators
- Performance metrics
- Phase-specific details

### Use Cases
- Development workflow monitoring
- System health checks
- Performance optimization
- Debugging and troubleshooting
- Release management
- DevOps operations

---

## L3 Fairness & Ethics Hub

⚖️ **Port:** 8506  
**Technology:** Flask  
**Access:** `http://localhost:8506`  
**File:** `dashboard/l3_fairness_ethics_hub.py`

### Purpose
Comprehensive fairness and ethics evaluation hub that computes fairness metrics across protected groups, produces a Fairness Index (FI), and evaluates ethical governance maturity. Evaluates how well AI systems treat different groups fairly and ethically.

### Core Metrics

#### 1. Fairness Index (FI)
- **Scale:** 0-100 (higher is better)
- **Calculation:** Aggregated fairness scores across all protected attributes
- **Formula:** Average of attribute-level fairness scores, where each attribute score is computed from:
  - Demographic Parity Gap (DPG) score
  - Equal Opportunity Gap (EOG) score
  - Equalized Odds Gap (EOD) score
  - Subgroup Accuracy Difference (SAD) score
- **Current Value:** ~40-85/100 (depending on data)

#### 2. Group-Level Fairness Metrics

##### Demographic Parity Gap (DPG)
- **Definition:** Maximum difference in P(y_pred=1) between any two groups
- **Scale:** 0-1 (lower is better, 0 = perfect parity)
- **Formula:** max(P(positive | group_i)) - min(P(positive | group_j))
- **Threshold:** Gap < 0.05 (5%) indicates good demographic parity

##### Equal Opportunity Gap (EOG)
- **Definition:** Maximum difference in True Positive Rate (TPR) across groups
- **Scale:** 0-1 (lower is better)
- **Formula:** max(TPR | group_i) - min(TPR | group_j)
- **Threshold:** Gap < 0.05 (5%) indicates equal opportunity

##### Equalized Odds Gap (EOD)
- **Definition:** Maximum of (TPR gap, FPR gap) across groups
- **Scale:** 0-1 (lower is better)
- **Formula:** max(TPR_gap, FPR_gap)
- **Threshold:** Gap < 0.05 (5%) indicates equalized odds

##### Subgroup Accuracy Difference (SAD)
- **Definition:** Maximum accuracy difference across groups
- **Scale:** 0-1 (lower is better)
- **Formula:** max(accuracy | group_i) - min(accuracy | group_j)
- **Threshold:** Gap < 0.05 (5%) indicates consistent accuracy

#### 3. Ethical Maturity Level (EML)
- **Scale:** 1-5 (higher is better)
- **Levels:**
  - **Level 1 (0-20%):** No formal governance
  - **Level 2 (20-40%):** Basic processes documented
  - **Level 3 (40-60%):** Partially implemented
  - **Level 4 (60-80%):** Fully implemented
  - **Level 5 (80-100%):** Continuous optimization
- **Calculation:** Based on ethics checklist compliance:
  - Ethical policy documentation
  - Bias assessment (planned and regular)
  - Human oversight documentation
  - Incident reporting mechanisms
  - Fairness monitoring
  - Diverse testing data
  - Explainability requirements
  - User consent mechanisms
  - Audit trail completeness
  - Redress mechanisms
  - Stakeholder engagement
  - Regular reviews
  - Compliance tracking
  - Ethics training
- **Current Value:** Level 5 (100% checklist compliance)

### Protected Attributes Analyzed
- **Gender:** Male (M), Female (F), Other
- **Age Groups:** 18-30, 31-45, 46-60, 61+
- **Custom attributes:** Configurable based on system needs

### Gap-to-Score Conversion
Fairness gaps are converted to 0-100 scores using linear mapping:
- **Gap = 0** → Score = 100 (perfect fairness)
- **Gap ≥ 0.3 (30%)** → Score = 0 (maximum unfairness)
- **Linear interpolation** between 0 and 0.3

### API Endpoints

- `GET /` - Main dashboard with fairness metrics and ethical maturity
- `GET /health` - Health check endpoint
- `GET /api/fairness-metrics` - **Comprehensive fairness metrics**
  - Returns:
    - `fairness_index`: Overall FI (0-100)
    - `attributes`: Per-attribute fairness scores and gaps
      - `fairness_score`: Overall attribute fairness (0-100)
      - `dpg_score`, `eog_score`, `eod_score`, `sad_score`: Individual metric scores
      - `raw_metrics`: Original gap values
    - `total_records`: Number of predictions analyzed
    - `timestamp`: ISO timestamp
- `GET /api/fi` - **Fairness Index only**
  - Returns: `fairness_index` (0-100), `timestamp`
- `GET /api/eml` - **Ethical Maturity Level**
  - Returns:
    - `eml_level`: 1-5
    - `eml_label`: Human-readable label
    - `score`: 0-100 percentage
    - `passed_items`: Number of checklist items passed
    - `total_items`: Total checklist items
    - `checklist`: Full checklist with pass/fail status
    - `timestamp`: ISO timestamp
- `GET /api/groups` - **Protected groups distribution**
  - Returns:
    - `groups`: Dictionary of protected attributes and their value distributions
      - Each attribute contains value counts and percentages
    - `timestamp`: ISO timestamp
- `GET /api/summary` - **Module 5 integration endpoint**
  - Returns: `fairness_index`, `eml_level`, `eml_score`, `total_records`, `timestamp`

### Key Features
- Group-level fairness analysis
- Multiple fairness metrics (DPG, EOG, EOD, SAD)
- Protected attribute tracking
- Ethical maturity assessment
- Interactive dashboard with visualizations
- Real-time fairness monitoring
- Bias detection alerts
- Subgroup distribution analysis

### Use Cases
- Fairness audits and bias detection
- Regulatory compliance (EU AI Act, EEOC guidelines)
- Ethical AI governance
- Model fairness validation
- Protected group monitoring
- Bias mitigation tracking
- Stakeholder reporting
- Risk assessment

#### 6. Fairness Research Tracker (Real-Time Updates)

**Purpose:** Automatically track latest fairness research and best practices

**Sources Monitored:**
- arXiv (cs.LG, cs.CY categories)
- FAccT Conference proceedings
- NeurIPS/ICML fairness workshops
- ACM FAT* conference papers

**Features:**
- Weekly scraping of new papers
- Keyword-based relevance filtering
- Best practice extraction
- Integration with fairness metrics updates

**Implementation:**
```python
# Research tracker configuration
RESEARCH_SOURCES = {
    "arxiv": {
        "categories": ["cs.LG", "cs.CY"],
        "keywords": ["fairness", "bias", "discrimination", "equity"],
        "frequency": "weekly"
    },
    "facct": {
        "url": "https://facctconference.org/proceedings/",
        "frequency": "annual"
    },
    "neurips": {
        "workshop": "fairness-ml",
        "frequency": "annual"
    }
}
```

**API Endpoints:**
- `GET /api/research/latest` - Recent fairness research papers
- `GET /api/research/trends` - Emerging fairness trends
- `GET /api/research/recommendations` - Best practice updates

### Integration with Module 5
- **UQO (Unified QA Orchestrator)** polls L3 Fairness Hub at `/api/summary` for:
  - Fairness Index (FI) - used in CQS calculation (20% weight)
  - Ethical Maturity Level (EML)
  - Fairness metrics for detailed breakdown
- **CAE (Continuous Assurance Engine)** monitors fairness drift by:
  - Tracking FI trends over time
  - Detecting fairness degradation
  - Alerting on bias thresholds

---

## Unified QA Orchestrator (UQO)

📊 **Port:** 8507  
**Technology:** Flask  
**Access:** `http://localhost:8507`  
**File:** `simple_uqo.py` (Beautiful Enhanced Dashboard)

### Purpose
**Enhanced unified orchestrator** that integrates metrics from all 6 hubs (L4, L2, L1, SOQM, L3 Fairness, CAE) into a **Unified Continuous QA Score (CQS)**. Provides cross-hub aggregation, drift awareness, alert classification, and comprehensive quality oversight with historical tracking.

### Core Functionality

#### Unified Continuous QA Score (CQS) Calculation
**NEW:** Enhanced CQS formula integrating all hub metrics with configurable weights:

**Formula:** `CQS = 0.20×CRS + 0.25×SAI + 0.20×TS + 0.20×FI + 0.10×OPS + 0.05×(EML×20)`

**Components:**
- **CRS** - Compliance Readiness Score from L1 (20% weight)
- **SAI** - Security Assurance Index from L2 (25% weight) 
- **TS** - Transparency Score from L4 (20% weight)
- **FI** - Fairness Index from L3 Fairness (20% weight)
- **OPS** - Operations Score from SOQM (10% weight)
- **EML** - Ethical Maturity Level from L3 Fairness (5% weight, converted from 1-5 to 20-100 scale)

**Configuration:** Weights are configurable via `config/cqs_weights.json`

#### Beautiful Modern Dashboard

The UQO features a **stunning, modern interface** with advanced visual design:

**🎨 Visual Design:**
- **Glass Morphism:** Frosted glass effects with backdrop blur for depth
- **Animated Background:** Floating gradient particles with smooth 20s animations
- **Deep Space Theme:** Dark blues (#0f0f23, #1a1a2e, #16213e) with cyan accents
- **Gradient Typography:** Beautiful color gradients on titles and scores
- **Inter Font Family:** Modern, crisp typography for professional appearance

**⚡ Interactive Features:**
- **Hover Animations:** Cards lift 8px and shimmer on hover with light sweeps
- **Pulsing Status Indicators:** Live status dots with breathing animation
- **Button Effects:** Smooth hover transitions with gradient backgrounds
- **Rotating Background:** Subtle 10s rotating gradient in CQS section
- **Responsive Layout:** Auto-fitting hub cards (300px minimum width)

**📊 Layout Enhancements:**
- **5rem CQS Score:** Large, gradient-colored main score display
- **Hub Cards:** Individual cards for each hub with scores and status
- **Stats Row:** Centered statistics (Last Updated, Critical Issues, Warnings)
- **Professional Footer:** Clean separator with integration information

#### Enhanced Features

1. **Cross-Hub Metric Integration**
   - **L1 Hub:** CRS, regulatory drift status
   - **L2 Hub:** SAI, DLP, ES, ARI composite metrics
   - **L3 Fairness:** FI, EML, bias detection
   - **L4 Hub:** TS, EFI, FIC, AIx composite metrics
   - **SOQM:** System health, phase status
   - **CAE:** Internal CQS, drift detection

2. **Unified CQS Computation**
   - Configurable weighted formula
   - Real-time metric aggregation
   - Fallback handling for unavailable hubs
   - Historical trend logging

3. **Drift Awareness & Monitoring**
   - **Performance Drift:** PSI, KS test, ECE from CAE
   - **Fairness Drift:** Demographic parity, equalized odds monitoring
   - **Compliance Drift:** Regulatory change detection
   - **Regulatory Drift:** L1 regulation update tracking

4. **Advanced Alert Classification**
   - **Critical:** Performance/fairness drift detected
   - **Warning:** Compliance drift, regulatory changes
   - **High:** Security anomalies from L2
   - **Medium:** Fairness issues from L3
   - Multi-source alert aggregation

5. **QA History & Trending**
   - Automatic logging to `qa_history/qa_history.jsonl`
   - Historical CQS tracking
   - Component score trends
   - Configurable retention limits

6. **Automated Reporting Engine**
   - **Beautiful Modal Interface:** Professional popup with gradient styling
   - **4 Report Types:** Daily (8 AM), Weekly (Mondays 9 AM), Monthly (1st), Quarterly
   - **4 Export Formats:** JSON, CSV, PDF, Excel with instant feedback
   - **Visual Success Messages:** File names with timestamps shown
   - **Technology:** APScheduler, ReportLab for PDF generation
   - **Delivery Options:** Email (SMTP), Portal upload, REST API

### Polling Configuration
- **Polling Interval:** 30 seconds
- **Hubs Monitored:**
  - L4 Explainability: `http://localhost:5000`
  - L2 Privacy & Security: `http://localhost:8502`
  - L1 Regulations: `http://localhost:8504`
  - SOQM: `http://localhost:8503`
  - L3 Fairness & Ethics: `http://localhost:8506`

### API Endpoints

#### Core Endpoints
- `GET /` - **Enhanced dashboard** with unified CQS, drift indicators, and cross-hub metrics
- `GET /api/overview` - Complete system overview (legacy)
- `GET /api/cqs` - Current Continuous QA Score (legacy)
- `GET /api/hub-status` - All hub statuses and health
- `GET /api/hub/<hub_name>` - Specific hub data

#### **NEW: Unified QA Endpoints**
- `GET /api/qa-overview` - **Comprehensive QA overview**
  - Returns: unified CQS, all hub metrics, drift status, alerts, weights
  - Integrates: CRS, SAI, TS, FI, EML, OPS, internal CQS, drift data
- `GET /api/unified-cqs` - **Unified CQS with detailed breakdown**
  - Returns: CQS score, component breakdown, weights, formula
- `GET /api/alerts` - **Classified alerts from all sources**
  - Returns: alerts by severity, source attribution, counts
- `GET /api/qa-history` - **QA metrics history**
  - Parameters: `?limit=N` (default 100)
  - Returns: historical CQS trends, component scores

#### Legacy Endpoints (Maintained)
- `GET /api/global-cqs` - Global CQS calculation
- `GET /api/module5-core/cqs` - CAE internal CQS
- `GET /api/module5-core/alerts` - Alerts from CAE
- `GET /api/module5-core/drift` - Drift analysis from Core

### Dashboard Features
- Large CQS score display (circular gauge)
- Hub status grid with health indicators
- Real-time score updates (auto-refresh every 30s)
- Alert section for critical issues
- Individual hub score breakdowns
- Last update timestamps
- Critical issue and warning counts

#### Enhanced Dashboard Capabilities

##### **WebSocket Implementation**
- **Real-time Updates:** Live data streaming without page refresh
- **Connection Management:** Automatic reconnection on network issues
- **Event-driven Updates:** Push notifications for critical alerts
- **Bandwidth Optimization:** Delta updates for changed data only

```javascript
// WebSocket implementation example
const ws = new WebSocket('ws://localhost:8507/ws');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
```

##### **Export Functionality**
- **PDF Reports:** Professional formatted reports with charts
- **Excel Export:** Detailed data with multiple worksheets
- **JSON API:** Programmatic data access for integrations
- **CSV Export:** Raw data for analysis tools
- **Scheduled Exports:** Automated report generation and delivery

##### **Interactive Charts**
- **Drill-down Capabilities:** Click to explore detailed metrics
- **Chart.js Integration:** Responsive, animated visualizations
- **Plotly Support:** Advanced statistical charts
- **Custom Time Series:** Historical trend analysis
- **Comparative Views:** Side-by-side hub comparisons

```javascript
// Interactive chart configuration
const chartConfig = {
    type: 'line',
    data: {
        datasets: [{
            label: 'CQS Trend',
            data: cqsHistoryData,
            borderColor: '#667eea'
        }]
    },
    options: {
        responsive: true,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        onClick: (event, elements) => {
            if (elements.length > 0) {
                drillDownToDetails(elements[0].index);
            }
        }
    }
};
```

##### **Time-Range Filtering**
- **Custom Date Ranges:** Flexible period selection
- **Preset Ranges:** Last 24h, 7d, 30d, 90d options
- **Real-time Updates:** Dynamic chart updates on range change
- **Performance Optimization:** Efficient data querying
- **Bookmark Support:** Save and share filtered views

##### **Responsive Design**
- **Mobile Optimized:** Touch-friendly interface for tablets/phones
- **Adaptive Layout:** Automatic layout adjustment for screen size
- **Progressive Enhancement:** Core functionality on all devices
- **Offline Support:** Cached data for limited connectivity

##### **Theme Management**
- **Dark/Light Mode:** User preference persistence
- **High Contrast:** Accessibility compliance
- **Custom Themes:** Organizational branding support
- **Dynamic Switching:** Real-time theme changes without reload

### Automated Reporting Engine

**Report Types:**
1. **Daily Operations Report** (8 AM)
   - Hub health status
   - Critical alerts summary
   - Performance metrics
   - System availability

2. **Weekly QA Report** (Mondays, 9 AM)
   - CQS trends and analysis
   - Hub performance comparison
   - Compliance status updates
   - Risk assessment summary

3. **Monthly Compliance Report** (1st of month)
   - Regulatory compliance status
   - Evidence completeness
   - Audit trail summary
   - Governance maturity assessment

4. **Quarterly Executive Report**
   - Strategic QA overview
   - ROI analysis
   - Risk mitigation effectiveness
   - Regulatory landscape changes

**Technology Stack:**
- **Scheduler:** APScheduler for automated generation
- **PDF Generation:** ReportLab for professional reports
- **Charts:** Matplotlib/Plotly for visualizations
- **Templates:** Jinja2 for dynamic content

**Delivery Methods:**
- **Email:** SMTP integration with attachments
- **Portal Upload:** Automatic upload to dashboard
- **REST API:** Programmatic access for integrations
- **File System:** Local storage with retention policies

**Configuration:**
```python
# config/reporting.json
{
    "daily_report": {
        "enabled": true,
        "time": "08:00",
        "recipients": ["ops@company.com"],
        "format": "pdf"
    },
    "weekly_report": {
        "enabled": true,
        "day": "monday",
        "time": "09:00",
        "recipients": ["qa@company.com", "management@company.com"]
    }
}
```

### Use Cases
- Executive dashboards
- System-wide quality oversight
- Cross-hub integration monitoring
- Quality assurance reporting
- Compliance aggregation
- Risk assessment

---

## Continuous Assurance Engine (CAE)

🤖 **Port:** 8508  
**Technology:** Flask  
**Access:** `http://localhost:8508`  
**File:** `module5_core.py`

### Purpose
Deep automation engine implementing performance drift detection, fairness monitoring, security anomaly detection, compliance drift tracking, and intelligent alerting. Provides internal CQS calculation independent of hub aggregation.

### Core Capabilities

#### 1. Performance Drift Detection (30% of Internal CQS)
**Algorithms:**
- **PSI (Population Stability Index)**: Measures distribution shift in input features
  - Threshold: PSI < 0.1 (Low), 0.1-0.25 (Medium), >0.25 (High)
- **KS Test (Kolmogorov-Smirnov)**: Tests for distribution differences
  - Threshold: KS < 0.15 (acceptable)
- **ECE (Expected Calibration Error)**: Measures prediction calibration drift
  - Lower is better (target: <0.15)

**Metrics Tracked:**
- AUC drift
- Accuracy drift
- Calibration drift
- Input stability
- Concept drift

#### 2. Fairness Drift Monitoring (20% of Internal CQS)
**Algorithms:**
- **Demographic Parity Gap**: P(Y'=1|A=0) should equal P(Y'=1|A=1)
  - Target gap: <0.05 (5%)
- **Equalized Odds Gap**: TPR and FPR should be equal across groups
  - Target gap: <0.05 (5%)

**Groups Monitored:**
- Protected attributes (gender, race, age, etc.)
- Group-specific metrics
- Fairness trends over time

#### 3. Security & Privacy Anomaly Detection (15% of Internal CQS)
**Detection Methods:**
- **Access Pattern Anomaly**: 3-sigma method for unusual access patterns
- **Model Integrity Check**: SHA-256 hash verification
- **Data Leakage Detection**: Monitoring for data extraction attempts

**Metrics:**
- Access anomaly score
- Model integrity status
- Unusual pattern detection

#### 4. Compliance Drift Tracking (20% of Internal CQS)
**Frameworks Monitored:**
- **GDPR Compliance**:
  - Data retention compliance
  - Consent tracking (target: >95%)
  - Right to be forgotten (target: >98%)
  - Data portability (target: >90%)
  - DPIA score (target: >85%)

- **EU AI Act Compliance**:
  - Risk assessment (target: >85%)
  - Transparency (target: >90%)
  - Accountability (target: >80%)
  - Human oversight (target: >85%)

#### 5. System Health Monitoring (15% of Internal CQS)
**Metrics:**
- Uptime percentage (target: >99%)
- Response time (target: <200ms)
- Error rate (target: <0.5%)

### Internal CQS Calculation
Weighted average across 5 categories:
```
Internal CQS = (0.30 × Performance) +
               (0.20 × Fairness) +
               (0.15 × Security/Privacy) +
               (0.20 × Compliance) +
               (0.15 × System Health)
```

### API Endpoints

- `GET /` - Main dashboard interface
- `GET /api/internal-cqs` - Internal CQS with category breakdown
- `GET /api/drift/performance` - Performance drift analysis (PSI, KS, ECE)
- `GET /api/drift/fairness` - Fairness drift metrics
- `GET /api/security/anomalies` - Security and privacy anomalies
- `GET /api/compliance/drift` - Compliance drift tracking
- `GET /api/alerts` - Active alerts and notifications
- `GET /api/health` - Health check

### Key Features
- Automated drift detection algorithms
- Statistical testing (PSI, KS, ECE)
- Real-time anomaly detection
- Fairness metric calculation
- Compliance scoring
- Alert generation
- Historical trend tracking

### Use Cases
- Model performance monitoring
- Fairness compliance verification
- Security threat detection
- Compliance drift alerts
- Automated quality assurance
- Production model monitoring

---

## Quick Reference

### Hub Access URLs

| Hub | Port | URL | Technology |
|-----|------|-----|------------|
| **Main Dashboard** | 8501 | `http://localhost:8501` | Streamlit |
| **L1 Regulations & Governance** | 8504 | `http://localhost:8504` | Flask |
| **L2 Privacy & Security** | 8502 | `http://localhost:8502` | Flask |
| **L3 Fairness & Ethics** | 8506 | `http://localhost:8506` | Flask |
| **L4 Explainability & Transparency** | 5000 | `http://localhost:5000` | Flask |
| **SOQM** | 8503 | `http://localhost:8503` | Flask |
| **UQO** | 8507 | `http://localhost:8507` | Flask |
| **CAE** | 8508 | `http://localhost:8508` | Flask |

### Starting All Hubs

```bash
# Option 1: Use the master launcher
python launch_all_dashboards.py

# Option 2: Start individually
# Terminal 1
streamlit run dashboard/app.py --server.port 8501

# Terminal 2 - L1 Regulations & Governance
python dashboard/l1_regulations_governance_hub.py

# Terminal 3 - L2 Privacy & Security
python dashboard/privacy_security_hub.py

# Terminal 4 - L3 Fairness & Ethics
python dashboard/l3_fairness_ethics_hub.py

# Terminal 5 - L4 Explainability & Transparency
python dashboard/hub_explainability_app.py

# Terminal 6 - SOQM
python dashboard/l3_operations_control_center.py

# Terminal 7 - UQO
python module5_hub.py

# Terminal 8 - CAE
python module5_core.py
```

### Default Credentials (Main Dashboard)
- **Username:** `admin`
- **Password:** `admin_default_123`

---

## API Endpoints Summary

### Flask Dashboard (Port 8510)
```
GET  /                              # Root - redirects to login
GET  /login                         # Authentication page
POST /login                         # Login processing
GET  /logout                        # Logout
GET  /dashboard                     # Main dashboard (protected)
GET  /hub-overview                  # Hub status overview
GET  /charts                        # Interactive analytics
GET  /alerts                        # Alert management
GET  /settings                      # User settings
GET  /setup-2fa                     # 2FA setup
POST /verify-2fa                    # 2FA verification
GET  /api/live-data                 # Real-time hub data
GET  /api/dashboard-data            # Dashboard metrics
GET  /api/health-status             # Hub health status
GET  /api/alerts                    # System alerts
```

### L4 Explainability Hub (Port 5000)
```
GET  /                              # Dashboard
GET  /api/modules                   # All modules
GET  /api/categories                # Categories
GET  /api/transparency-score        # TS (formal weighted formula)
GET  /api/explainability-metrics    # All composite metrics (TS, EFI, FIC, AIx)
GET  /api/tests                     # Run tests
GET  /api/interpretability/shap     # SHAP vis
GET  /api/interpretability/lime     # LIME vis
GET  /api/interpretability/gradcam  # GradCAM vis
GET  /api/interpretability/decision-path  # Decision paths
GET  /api/interpretability/all      # All interpretability
GET  /health                        # Health check
```

### L2 Privacy & Security Hub (Port 8502)
```
GET  /                              # Dashboard
GET  /api/module/<module_name>      # Module details
GET  /api/sai                       # SAI score (formal category-based formula)
GET  /api/metrics                   # All composite metrics (SAI, DLP, ES, ARI)
```

### L1 Regulations Hub (Port 8504)
```
GET  /                              # Dashboard
GET  /api/score                     # Compliance score
GET  /api/compliance                # Compliance details
GET  /api/governance                # Governance metrics
GET  /api/status                    # Hub status
GET  /api/frameworks                # List all frameworks
GET  /api/framework/<name>          # Framework details
GET  /api/compliance-map            # Full compliance mapping
GET  /api/crs                       # Compliance Readiness Score
GET  /api/sdlc-status               # SDLC compliance status
GET  /api/gmi                       # Governance Maturity Index
GET  /api/risk-classification       # EU AI Act risk classification
GET  /api/compliance-drift          # Compliance drift status
GET  /api/regulations/drift         # Regulatory drift status
GET  /api/regulations/updates       # List pending updates
POST /api/regulations/approve/<id>  # Approve regulation update
POST /api/regulations/reject/<id>   # Reject regulation update
POST /api/regulations/check-updates # Manual update check
GET  /api/evidence/list             # List evidence files
POST /api/evidence/upload           # Upload evidence
GET  /api/summary                   # Module 5 integration endpoint
```

### System Operations & QA Monitor (SOQM) (Port 8503)
```
GET  /                              # Dashboard
GET  /api/status                    # System status
GET  /api/phase/<phase_id>          # Phase details (1-8)
GET  /api/health                    # Health check
```

### L3 Fairness & Ethics Hub (Port 8506)
```
GET  /                              # Dashboard
GET  /health                        # Health check
GET  /api/fairness-metrics          # All fairness metrics (FI, gaps, attributes)
GET  /api/fi                        # Fairness Index only
GET  /api/eml                       # Ethical Maturity Level
GET  /api/groups                    # Protected groups distribution
GET  /api/summary                   # Module 5 integration endpoint
```

### Unified QA Orchestrator (UQO) (Port 8507) - **UPGRADED**
```
# Enhanced Dashboard
GET  /                              # Unified dashboard with CQS, drift, alerts

# NEW: Unified QA Endpoints
GET  /api/qa-overview               # Comprehensive QA overview (CRS, SAI, TS, FI, EML, OPS)
GET  /api/unified-cqs               # Unified CQS with detailed breakdown
GET  /api/alerts                    # Classified alerts from all sources
GET  /api/qa-history                # QA metrics history (?limit=N)

# Legacy Endpoints (Maintained)
GET  /api/overview                  # System overview
GET  /api/cqs                       # CQS score
GET  /api/hub-status                # All hub statuses
GET  /api/hub/<hub_name>            # Specific hub
GET  /api/global-cqs                # Global CQS
GET  /api/module5-core/cqs          # Core CQS
GET  /api/module5-core/alerts       # Core alerts
GET  /api/module5-core/drift        # Core drift
```

### Continuous Assurance Engine (CAE) (Port 8508)
```
GET  /                              # Dashboard
GET  /api/internal-cqs              # Internal CQS
GET  /api/drift/performance         # Performance drift
GET  /api/drift/fairness            # Fairness drift
GET  /api/security/anomalies        # Security anomalies
GET  /api/compliance/drift          # Compliance drift
GET  /api/alerts                    # Active alerts
GET  /api/health                    # Health check
```

---

## Score Metrics Explained

### L4 Transparency Score (TS)
- **Calculation:** **Formal weighted formula**
  - **TS = 0.35 × ExplanationGeneration + 0.30 × ExplanationReliability + 0.25 × TraceabilityAuditability + 0.10 × Comprehensibility**
- **Block Scores:**
  - Explanation Generation (EGC): 35% weight
  - Explanation Reliability (ERF): 30% weight
  - Traceability & Auditability (TA): 25% weight
  - Comprehensibility (CU): 10% weight

### L4 Composite Metrics
- **EFI (Explainability Fidelity Index):** 0-100 scale (higher is better)
  - Weighted combination of reconstruction accuracy, feature impact alignment, masking consistency
- **FIC (Feature Importance Consistency):** 0-100 scale (higher is better)
  - Weighted combination of Jaccard similarity and normalized Spearman correlation
- **AIx (Auditability Index):** 0-100 scale (higher is better)
  - Weighted combination of prediction logging, model versioning, audit trail scores

### L2 SAI (Security Assurance Index)
- **Range:** 0-100
- **Calculation:** **Formal category-based weighted formula**
  - **SAI = 0.30 × DataPrivacy + 0.25 × ModelIntegrity + 0.25 × SystemSecurity + 0.20 × Governance**
- **Categories:**
  - **Data Privacy** (30% weight): Anonymization, PII Detection, Data Minimization
  - **Model Integrity** (25% weight): Model Security & Adversarial Testing
  - **System Security** (25% weight): Encryption, Access Control, Threat Detection, API Security
  - **Governance** (20% weight): Data Retention, GDPR Compliance, Audit Logging

### L2 Composite Metrics
- **DLP (Data Leakage Probability):** 0-100 scale (lower is better)
  - Weighted combination of membership inference rate, re-identification risk, PII detection
- **ES (Encryption Score):** 0-100 scale (higher is better)
  - Weighted combination of AES-256 coverage, TLS 1.3 coverage, key rotation, certificate health
- **ARI (Attack Robustness Index):** 0-100 scale (higher is better)
  - Multiplicative combination of adversarial robustness, attack success rate, model integrity

### 💻 Code Examples

#### **PSI (Population Stability Index) Calculation**
```python
import numpy as np

def calculate_psi(expected, actual, buckets=10):
    """Calculate Population Stability Index for drift detection"""
    
    # Create buckets based on expected distribution
    breakpoints = np.arange(0, buckets + 1) / buckets * 100
    
    # Calculate expected and actual percentages
    expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
    
    # Avoid division by zero
    expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
    actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
    
    # Calculate PSI
    psi = np.sum((actual_percents - expected_percents) * 
                 np.log(actual_percents / expected_percents))
    
    return psi

# Usage example
baseline_data = np.random.normal(0, 1, 1000)
current_data = np.random.normal(0.2, 1.1, 1000)  # Slight drift
psi_score = calculate_psi(baseline_data, current_data)
print(f"PSI Score: {psi_score:.4f}")  # > 0.1 indicates drift
```

#### **KS Test Implementation**
```python
from scipy import stats

def ks_drift_test(reference_data, current_data, threshold=0.05):
    """Kolmogorov-Smirnov test for distribution drift"""
    
    # Perform KS test
    ks_statistic, p_value = stats.ks_2samp(reference_data, current_data)
    
    # Determine if drift detected
    drift_detected = p_value < threshold
    
    return {
        'ks_statistic': ks_statistic,
        'p_value': p_value,
        'drift_detected': drift_detected,
        'threshold': threshold
    }

# Usage example
reference = np.random.normal(0, 1, 1000)
current = np.random.normal(0.3, 1.2, 1000)
result = ks_drift_test(reference, current)
print(f"Drift detected: {result['drift_detected']}")
```

#### **Fairness Gap Calculation**
```python
def calculate_demographic_parity_gap(y_pred, protected_attr):
    """Calculate demographic parity gap between groups"""
    
    groups = np.unique(protected_attr)
    positive_rates = {}
    
    for group in groups:
        group_mask = protected_attr == group
        group_predictions = y_pred[group_mask]
        positive_rate = np.mean(group_predictions)
        positive_rates[group] = positive_rate
    
    # Calculate maximum gap between any two groups
    rates = list(positive_rates.values())
    gap = max(rates) - min(rates)
    
    return {
        'gap': gap,
        'group_rates': positive_rates,
        'max_acceptable_gap': 0.05  # 5% threshold
    }

# Usage example
predictions = np.random.binomial(1, 0.7, 1000)
gender = np.random.choice(['M', 'F'], 1000)
fairness_result = calculate_demographic_parity_gap(predictions, gender)
print(f"Demographic parity gap: {fairness_result['gap']:.3f}")
```

#### **Alert Generation Logic**
```python
class AlertManager:
    def __init__(self):
        self.thresholds = {
            'critical': {'cqs_below': 50, 'hub_offline': True},
            'warning': {'cqs_below': 70, 'drift_detected': True}
        }
    
    def generate_alerts(self, metrics):
        """Generate alerts based on current metrics"""
        alerts = []
        
        # Critical alerts
        if metrics['cqs'] < self.thresholds['critical']['cqs_below']:
            alerts.append({
                'severity': 'critical',
                'type': 'low_cqs',
                'message': f"CQS critically low: {metrics['cqs']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Warning alerts
        if metrics['cqs'] < self.thresholds['warning']['cqs_below']:
            alerts.append({
                'severity': 'warning',
                'type': 'cqs_degradation',
                'message': f"CQS below threshold: {metrics['cqs']:.1f}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Drift alerts
        if metrics.get('drift_detected', False):
            alerts.append({
                'severity': 'warning',
                'type': 'data_drift',
                'message': "Data drift detected in model inputs",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts

# Usage example
alert_manager = AlertManager()
current_metrics = {'cqs': 45.2, 'drift_detected': True}
alerts = alert_manager.generate_alerts(current_metrics)
for alert in alerts:
    print(f"{alert['severity'].upper()}: {alert['message']}")
```

### L1 Compliance Score
- Framework-specific compliance percentages
- Clause-level pass/fail tracking
- Evidence-based assessment

### SOQM Operations Score
- Phase health status
- Code coverage metrics
- Test pass rates
- API endpoint availability

### L3 Fairness Index (FI)
- **Range:** 0-100
- **Calculation:** Average of attribute-level fairness scores
- **Metrics per Attribute:**
  - Demographic Parity Gap (DPG) → Score
  - Equal Opportunity Gap (EOG) → Score
  - Equalized Odds Gap (EOD) → Score
  - Subgroup Accuracy Difference (SAD) → Score
- **Gap-to-Score:** Linear mapping (0 gap = 100, ≥30% gap = 0)

### L3 Ethical Maturity Level (EML)
- **Range:** 1-5 (with 0-100 score)
- **Levels:**
  - Level 1: No formal governance (0-20%)
  - Level 2: Basic processes documented (20-40%)
  - Level 3: Partially implemented (40-60%)
  - Level 4: Fully implemented (60-80%)
  - Level 5: Continuous optimization (80-100%)
- **Based on:** Ethics checklist compliance (15 items)

### Module 5 Unified CQS (Continuous QA Score) - **UPGRADED**
- **NEW Formula:** `CQS = 0.20×CRS + 0.25×SAI + 0.20×TS + 0.20×FI + 0.10×OPS + 0.05×(EML×20)`
- **Components:**
  - **CRS** - L1 Compliance Readiness Score (20%)
  - **SAI** - L2 Security Assurance Index (25%)
  - **TS** - L4 Transparency Score (20%)
  - **FI** - L3 Fairness Index (20%)
  - **OPS** - SOQM Operations Score (10%)
  - **EML** - L3 Ethical Maturity Level (5%, converted from 1-5 to 20-100)
- **Configuration:** Weights configurable via `config/cqs_weights.json`
- **Features:** Cross-hub integration, drift awareness, alert classification, QA history

### CAE Internal CQS
- **Calculation:** Internal metrics-based score
- **Components:**
  - Performance Drift (30%)
  - Fairness Drift (20%)
  - Security/Privacy (15%)
  - Compliance (20%)
  - System Health (15%)

---

## Integration & Workflow

### Typical Workflow
1. **Start Main Dashboard** (Port 8501) - Authenticate and get overview
2. **L1 Regulations & Governance** (Port 8504) - Begin with compliance requirements
3. **L2 Privacy & Security** (Port 8502) - Build on regulatory foundation
4. **L3 Fairness & Ethics** (Port 8506) - Evaluate fairness after security
5. **L4 Explainability & Transparency** (Port 5000) - Add transparency layer
6. **SOQM** (Port 8503) - Check infrastructure health
7. **UQO** (Port 8507) - See aggregated CQS across all hubs
8. **CAE** (Port 8508) - Monitor continuous assurance and drift
9. **Return to Main Dashboard** - Review aggregated GQAS

### Data Flow
```
Individual Hubs → UQO → Main Dashboard
                      ↓
              CAE (Parallel Monitoring)
```

### Cross-Hub Dependencies
- **UQO** requires all 5 hubs to be running
- **Main Dashboard** can function independently but shows aggregated data
- **CAE** operates independently but enhances UQO data

---

## Technical Details

### Technologies Used
- **Main Dashboard:** Streamlit, Python, Pandas, Altair
- **Hubs:** Flask, Python, Matplotlib, NumPy
- **Database:** SQLite/PostgreSQL (via SQLAlchemy)
- **Authentication:** Custom authentication system
- **Visualization:** Matplotlib, interactive charts

### File Structure
```
dashboard/
├── app.py                          # Main dashboard
├── hub_explainability_app.py       # L4 Hub
├── privacy_security_hub.py         # L2 Hub
├── l1_regulations_governance_hub.py # L1 Hub
├── l3_operations_control_center.py  # SOQM Hub
├── l3_fairness_ethics_hub.py        # L3 Fairness Hub
├── auth_ui.py                      # Authentication UI
├── ux_enhancements.py              # Session info, themes
├── styles.css                      # Sidebar styles
└── css_loader.py                   # CSS loader utility

module5_hub.py                      # UQO (root)
module5_core.py                     # CAE (root)
start_module5_hub.py               # UQO launcher
start_module5_core.py              # CAE launcher
```

### Dependencies
- Flask, Flask-CORS
- Streamlit, streamlit-autorefresh
- Pandas, NumPy, Matplotlib
- SQLAlchemy
- Python 3.8+

---

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Check running processes: `netstat -ano | findstr :<port>`
   - Kill process or use different port

2. **Hub Not Responding**
   - Verify hub is running (check process list)
   - Check logs for errors
   - Verify dependencies are installed

3. **Authentication Issues**
   - Clear browser cache
   - Check user credentials in `data/auth/users.json`
   - Verify authentication module is imported

4. **UQO Shows No Data**
   - Ensure all 5 hubs are running
   - Check hub URLs are correct
   - Wait 30 seconds for first poll

### Debug Mode
- Enable debug mode in Main Dashboard sidebar
- Check browser console for errors
- Review application logs in `logs/` directory

---

## ⚙️ Configuration Management

### Key Configuration Files

The IRAQAF platform uses JSON configuration files for flexible parameter tuning and system customization:

#### **Core Configuration Files:**

1. **`config/cqs_weights.json`** - CQS weight tuning
   ```json
   {
     "crs": 0.20,
     "sai": 0.25,
     "ts": 0.20,
     "fi": 0.20,
     "ops_score": 0.10,
     "eml_score": 0.05
   }
   ```

2. **`config/alert_thresholds.json`** - Alert severity thresholds
   ```json
   {
     "critical": {
       "cqs_below": 50,
       "hub_offline": true,
       "compliance_drift": true
     },
     "warning": {
       "cqs_below": 70,
       "performance_degradation": 10,
       "fairness_drift": 5
     }
   }
   ```

3. **`config/drift_thresholds.json`** - Drift detection parameters
   ```json
   {
     "performance_drift": {
       "psi_threshold": 0.1,
       "ks_threshold": 0.05,
       "window_size": 1000
     },
     "fairness_drift": {
       "demographic_parity_threshold": 0.05,
       "equal_opportunity_threshold": 0.05,
       "monitoring_frequency": "daily"
     }
   }
   ```

4. **`config/regulation_sources.json`** - Regulatory scraping sources
   ```json
   [
     {
       "framework": "GDPR",
       "source_type": "html",
       "url": "https://gdpr-info.eu/",
       "poll_interval_hours": 24
     },
     {
       "framework": "EU_AI_ACT",
       "source_type": "pdf",
       "url": "https://eur-lex.europa.eu/ai-act",
       "poll_interval_hours": 24
     }
   ]
   ```

#### **Historical Data Files:**

5. **`qa_history/qa_history.jsonl`** - Historical QA metrics
   ```json
   {"timestamp": "2024-11-21T10:00:00", "cqs": 85.2, "crs": 87.5, "sai": 84.1, "ts": 85.0, "fi": 78.3, "ops": 92.1}
   {"timestamp": "2024-11-21T11:00:00", "cqs": 86.1, "crs": 88.2, "sai": 85.3, "ts": 85.5, "fi": 79.1, "ops": 91.8}
   ```

#### **Authentication Configuration:**

6. **`dashboard/data/auth/users.json`** - User management
7. **`dashboard/data/auth/sessions.json`** - Session tracking

#### **Evidence and Compliance:**

8. **`dashboard/evidence/evidence.db`** - Evidence metadata (SQLite)
9. **`dashboard/evidence/regulation_versions.db`** - Regulation versioning (SQLite)

### Configuration Best Practices

- **Version Control:** All config files are tracked in Git
- **Environment-Specific:** Use separate configs for dev/staging/prod
- **Validation:** Schema validation on config file loading
- **Hot Reload:** Most configs support runtime updates without restart
- **Backup:** Automatic backup before config changes
- **Audit Trail:** All config changes are logged

### Configuration API Endpoints

- `GET /api/config/weights` - Current CQS weights
- `POST /api/config/weights` - Update CQS weights (admin only)
- `GET /api/config/thresholds` - Current alert thresholds
- `POST /api/config/thresholds` - Update thresholds (admin only)

---

## 📊 Unified Weight Tables (Quick Reference)

### Unified CQS Weight Table

| Dimension | Source | Weight | Description |
|-----------|--------|--------|-------------|
| **Compliance** | CRS | 20% | Legal & regulatory compliance |
| **Security** | SAI | 25% | Data protection & security |
| **Fairness** | FI | 20% | Bias detection & fairness |
| **Transparency** | TS | 20% | Explainability & transparency |
| **Operations** | OPS | 10% | Infrastructure reliability |
| **Ethics** | EML(×20) | 5% | Ethical maturity level |

### L4 Transparency Score (TS) Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| **Explanation Generation** | 35% | Capability to generate explanations |
| **Explanation Reliability** | 30% | Consistency and accuracy |
| **Traceability & Auditability** | 25% | Logging and audit trails |
| **Comprehensibility** | 10% | User understanding |

### L2 Security Assessment Index (SAI) Weights

| Category | Weight | Components |
|----------|--------|------------|
| **Data Protection** | 40% | DLP, encryption, access control |
| **System Security** | 35% | Infrastructure, network security |
| **Compliance & Governance** | 25% | Policies, audit, incident response |

### L1 Compliance Readiness Score (CRS) Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| **Regulatory Alignment** | 30% | Framework compliance |
| **Evidence Completeness** | 25% | Documentation quality |
| **SDLC Alignment** | 20% | Development process |
| **Governance Maturity** | 15% | Organizational maturity |
| **Post-Market Monitoring** | 10% | Ongoing compliance |

---

## Future Enhancements

### Planned Features
- Real-time WebSocket updates
- Advanced analytics dashboards
- Custom report generation
- Integration with external monitoring tools
- Mobile-responsive design improvements
- Additional regulatory frameworks
- Machine learning-based anomaly detection
- Automated remediation suggestions

---

## Support & Documentation

### Additional Resources
- **Quick Start Guide:** See `QUICK_START_CARD.txt`
- **Module 5 Guide:** See `MODULE5_DEPLOYMENT_GUIDE.md`
- **Integration Guide:** See `MODULE5_INTEGRATION_GUIDE.md`

### Contact
For questions or issues, refer to:
- Application logs: `logs/app.log`
- Audit logs: `logs/audit.log`
- Dashboard debug output

---

**Document Version:** 1.0  
**Last Updated:** November 2024  
**Status:** ✅ Complete and Operational

