# 🔐 IRAQAF Security Modules - Where to Find Them

## Dashboard Navigation Guide

### **Live Dashboard URL**
```
http://localhost:8501
```

---

## 📍 Security Modules Location in Dashboard

### **1. 🔐 L2 PRIVACY & SECURITY MONITOR** 
**Location:** Bottom of the main dashboard page (after login)
- **Visual:** Purple gradient header with 🔐 icon
- **Section:** "L2 PRIVACY & SECURITY MONITOR"
- **Toggle:** Click "📊 Click to expand security details" to view
- **What you'll see:**
  - Real-time security scanning
  - Compliance status
  - Vulnerability assessment
  - Security recommendations

**File Location:** `dashboard/l2_monitor_integration.py`

---

### **2. 🔒 L2 PRIVACY/SECURITY** 
**Location:** Main dashboard section before L2 Monitor
- **Heading:** "🔐 L2 Privacy & Security"
- **SubHeading:** "Dynamic security posture monitoring across all tested frameworks and applications"
- **Displays:**
  - Historical trends charts
  - Encryption coverage trends
  - DPIA completion status
  - Access review age
  - Incident rates
  - Key security metrics

**File Location:** `dashboard/app.py` (Lines 4275-4500)

---

## 🏗️ Security Module Files & Capabilities

### **Phase 1: Core Security Modules** ✅ IMPLEMENTED

#### **1. PII Detection & Anonymization**
```
📁 privacy/anonymization.py (554 lines)
```
**Capabilities:**
- Email, SSN, phone, credit card, passport detection
- Multiple anonymization methods (masking, hashing, tokenization)
- K-anonymity enforcement
- Differential privacy
- Privacy audit reporting

**How to Access in Dashboard:**
- Integrated into L2 Privacy/Security Monitor
- Use GDPR Rights section for data anonymization

---

#### **2. Encryption Validation**
```
📁 security/encryption_validator.py (525 lines)
```
**Capabilities:**
- Validates AES-256, TLS 1.2+ configuration
- Certificate checking
- Encryption compliance scoring
- Configuration parsing

**How to Access in Dashboard:**
- Visible in L2 Monitor encryption coverage metrics
- Check "Encryption coverage" trends chart

---

#### **3. Model Integrity Checking**
```
📁 security/model_integrity.py (519 lines)
```
**Capabilities:**
- SHA-256 checksum generation/verification
- Model versioning and lineage tracking
- Tamper detection with alerts
- Provenance reporting

**How to Access in Dashboard:**
- Integrated into model security evaluation
- Check tampering alerts in L2 Monitor

---

#### **4. Adversarial Testing**
```
📁 security/adversarial_tests.py (582 lines)
```
**Capabilities:**
- FGSM attack testing
- PGD attack evaluation
- Membership inference detection
- Robustness scoring

**How to Access in Dashboard:**
- Visible in model security scores
- Adversarial robustness metrics in L2 Monitor

---

### **Phase 2: Compliance & GDPR** ✅ IMPLEMENTED

#### **5. GDPR Rights Management**
```
📁 compliance/gdpr_rights.py (607 lines)
```
**Capabilities:**
- Right to Access (data export)
- Right to Erasure (data deletion)
- Right to Rectification (data correction)
- Right to Withdraw Consent
- Data Portability

**How to Access in Dashboard:**
1. After login, look for **GDPR/Privacy** section
2. Click on data subject requests section
3. Options to:
   - Export user data
   - Request erasure
   - Manage consent
   - View deletion history

---

### **Phase 3: Evaluation Engine** ✅ IMPLEMENTED

#### **6. L2 Evaluation (Real Checks)**
```
📁 security/l2_evaluator.py (458 lines)
```
**Capabilities:**
- Real encryption validation
- Privacy audit integration
- Model security assessment
- Governance scoring
- **SAI (Security Assurance Index) scoring (0-100)**

**How to Access in Dashboard:**
- Main L2 Privacy/Security Monitor section
- Shows overall SAI score
- Category breakdowns (A, B, C, D)
- Real-time compliance status

---

### **Phase 4: Authentication & Access Control** ✅ IMPLEMENTED

#### **7. MFA (Multi-Factor Authentication)**
```
📁 security/mfa_manager.py (597 lines)
```
**Capabilities:**
- TOTP (Time-based One-Time Passwords)
- QR code generation for authenticator apps
- Backup codes (10 recovery codes)
- Account lockout protection
- MFA audit logging

**How to Access in Dashboard:**
1. **Login Page** → "Sign Up" tab
2. After account creation → MFA setup page
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Enter 6-digit code to verify
5. Save backup codes for recovery

---

### **Phase 5: Data Retention** ✅ IMPLEMENTED

#### **8. Data Retention Manager**
```
📁 data/retention_manager.py (532 lines)
```
**Capabilities:**
- Automated retention policies
- Default policies (logs 90d, audit 365d, temp 7d)
- Scheduled purging
- Data archival
- Deletion audit trail

**How to Access in Dashboard:**
- Administrative section for data management
- Retention policies configuration
- Deletion history logs
- Compliance reporting

---

## 🎯 Quick Navigation Steps

### **To See All Security Modules in Action:**

1. **Open Dashboard**
   ```
   http://localhost:8501
   ```

2. **Login/Sign Up**
   - Create account with MFA setup (Module #7)
   - Scan QR code with phone authenticator

3. **Scroll to Bottom**
   - Find "🔐 L2 PRIVACY & SECURITY MONITOR" section
   - Styled with purple gradient header
   - Click "📊 Click to expand security details"

4. **View Security Components:**
   - **Encryption:** See real validation (Module #2)
   - **Privacy:** View anonymization status (Module #1)
   - **Model Security:** Check integrity scores (Module #3)
   - **L2 Evaluation:** View SAI score (Module #6)

5. **For GDPR Rights (Module #5):**
   - Look for Privacy/GDPR section
   - Request data export, erasure, or consent withdrawal

6. **For Data Retention (Module #8):**
   - Admin panel → Data Management
   - View retention policies and deletion history

---

## 📊 Dashboard Sections Overview

```
DASHBOARD (app.py)
├── 🔐 AUTHENTICATION (auth_ui.py)
│   ├── Login Tab
│   ├── Sign Up Tab (with MFA setup)
│   └── Logout Button
│
├── 📈 L2 PRIVACY & SECURITY Section
│   ├── Frameworks Overview
│   ├── Applications Overview
│   └── Historical Trends Charts
│       ├── Encryption Coverage
│       ├── DPIA Completion
│       ├── Access Review Age
│       └── Incident Rates
│
├── 🔐 L2 PRIVACY & SECURITY MONITOR (l2_monitor_integration.py)
│   ├── 🔒 Encryption Evaluation
│   ├── 🛡️ Privacy Audit
│   ├── ✓ Model Integrity
│   ├── ⚔️ Adversarial Testing
│   ├── ⚖️ GDPR Compliance
│   ├── 🔑 MFA Status
│   ├── 📋 Data Retention
│   └── 📊 Overall SAI Score
│
├── 👤 GDPR/Privacy Management
│   ├── Data Subject Requests
│   ├── Export Data
│   ├── Request Erasure
│   └── Manage Consent
│
└── ⚙️ Administrative
    ├── Data Retention Policies
    ├── MFA Enforcement
    ├── Audit Logs
    └── Compliance Reports
```

---

## 🔍 How to Verify Each Module is Active

### **Module Status Check:**

1. **PII Detection (Module #1)**
   - Upload/import data with emails or SSNs
   - Should show detected PII count in L2 Monitor
   - Anonymization options appear automatically

2. **Encryption Validation (Module #2)**
   - Check "Encryption coverage" in L2 Privacy/Security trends
   - Should show 0-100% coverage metric

3. **Model Integrity (Module #3)**
   - Load a model in the ML section
   - Model integrity score visible in L2 Monitor

4. **Adversarial Testing (Module #4)**
   - Train/upload a model
   - Adversarial robustness score shows in L2 Monitor
   - Scores: Excellent/Good/Acceptable/Weak/Poor

5. **GDPR Rights (Module #5)**
   - Click Privacy section
   - Options to request access/erasure visible
   - Deletion history logged and auditable

6. **L2 Evaluator (Module #6)**
   - View overall SAI score in L2 Monitor
   - Should be real score (not random)
   - Category scores for A, B, C, D visible

7. **MFA Manager (Module #7)**
   - Sign up page shows QR code
   - Backup codes generated
   - Login requires TOTP code

8. **Data Retention (Module #8)**
   - Admin section shows retention policies
   - Scheduled jobs run automatically
   - Deletion logs available for audit

---

## 📞 Support & Testing

### **Testing the Modules:**

1. Create test data with PII
2. Upload to dashboard
3. Watch real-time anonymization
4. Check SAI score increases
5. Export reports
6. Review audit logs

### **File Locations (Quick Reference):**

| Module | File | Lines |
|--------|------|-------|
| PII Detection | `privacy/anonymization.py` | 554 |
| Encryption | `security/encryption_validator.py` | 525 |
| Model Integrity | `security/model_integrity.py` | 519 |
| Adversarial Tests | `security/adversarial_tests.py` | 582 |
| GDPR Rights | `compliance/gdpr_rights.py` | 607 |
| L2 Evaluator | `security/l2_evaluator.py` | 458 |
| MFA Manager | `security/mfa_manager.py` | 597 |
| Data Retention | `data/retention_manager.py` | 532 |

---

**Dashboard is live at:** `http://localhost:8501` 🚀
