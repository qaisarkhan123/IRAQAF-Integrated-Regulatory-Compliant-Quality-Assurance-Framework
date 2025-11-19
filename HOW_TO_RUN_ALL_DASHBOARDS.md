# 🚀 HOW TO RUN ALL THREE DASHBOARDS

There are **3 easy ways** to start all three dashboards every time:

---

## **METHOD 1: PowerShell Script (Recommended for Windows) ⭐**

### Step 1: Open PowerShell
1. Press `Win + R`
2. Type `powershell` and press Enter
3. Or right-click → Open PowerShell

### Step 2: Navigate to Project
```powershell
cd C:\Users\khan\Downloads\iraqaf_starter_kit
```

### Step 3: Run the Startup Script
```powershell
.\START_ALL_DASHBOARDS.ps1
```

**What happens:**
- ✅ All old processes are stopped
- ✅ Dashboard 1 starts on port 8501 (Main)
- ✅ Dashboard 2 starts on port 8502 (Security)
- ✅ Dashboard 3 starts on port 5000 (L4 Hub)
- ✅ All three dashboards open in browser automatically
- ✅ You see status messages in PowerShell

---

## **METHOD 2: Python Script (Works Everywhere)**

### Step 1: Open Terminal/PowerShell

### Step 2: Navigate to Project
```bash
cd C:\Users\khan\Downloads\iraqaf_starter_kit
```

### Step 3: Run Python Startup Script
```bash
python START_ALL_DASHBOARDS.py
```

**What happens:**
- Same as Method 1, but using Python
- Works on Windows, Mac, and Linux
- Shows same beautiful status output

---

## **METHOD 3: Manual - Start Each Separately (If Scripts Fail)**

If the scripts don't work, use this method:

### Terminal 1 - Main Dashboard (Port 8501)
```bash
cd C:\Users\khan\Downloads\iraqaf_starter_kit
python -m streamlit run dashboard/app.py --server.port 8501
```

### Terminal 2 - Security Hub (Port 8502)
Open a new PowerShell and run:
```bash
cd C:\Users\khan\Downloads\iraqaf_starter_kit
python dashboard/privacy_security_hub.py
```

### Terminal 3 - L4 Hub (Port 5000)
Open another new PowerShell and run:
```bash
cd C:\Users\khan\Downloads\iraqaf_starter_kit
python dashboard/hub_explainability_app.py
```

---

## **🌐 ACCESS YOUR DASHBOARDS**

Once started, open these URLs in your browser:

| Dashboard | URL | Port | Feature |
|-----------|-----|------|---------|
| **Main Dashboard** | http://localhost:8501 | 8501 | Authentication, RBAC, Alerts |
| **Security Hub** | http://localhost:8502 | 8502 | 8 Security Modules |
| **L4 Explainability** | http://localhost:5000 | 5000 | SHAP/LIME/GradCAM (Score: 85/100) |

---

## **🔐 LOGIN CREDENTIALS**

```
Username: admin
Password: admin_default_123
```

---

## **📝 L4 HUB - 5 TABS AVAILABLE**

Once you open http://localhost:5000, you'll see 5 tabs:

1. **Overview** - 12 modules dashboard view
2. **🔍 How Model Decides** - SHAP, LIME, GradCAM, Decision Paths (AI explainability)
3. **Detailed Analysis** - Complete breakdown of all 12 modules with scores
4. **How Scores Are Calculated** - Mathematical formulas and calculation steps
5. **Recommendations** - Improvement suggestions for each module

---

## **⚠️ STOPPING ALL DASHBOARDS**

### Option A: Close Terminal Windows
Simply close the PowerShell/Terminal windows where they're running.

### Option B: Stop from PowerShell
```powershell
Stop-Process -Name streamlit -Force
Stop-Process -Name python -Force
```

### Option C: Kill Port Processes
```powershell
netstat -ano | findstr ":8501 :8502 :5000"
taskkill /PID <PID> /F
```

---

## **✅ WHAT EACH DASHBOARD DOES**

### 📊 Main Dashboard (8501)
- User authentication (Login/Sign Up)
- Role-based access control (RBAC)
- L1-L5 compliance module assessment
- Real-time alerts & notifications
- PDF/CSV export functionality
- Feature cards and module selection

### 🔐 Security Hub (8502)
- **8 Security Modules:**
  1. PII Detection & Classification
  2. Encryption Validator (AES-256, TLS 1.3)
  3. Data Retention Policies
  4. Role-Based Access Control
  5. Real-time Threat Detection
  6. GDPR Compliance Tracking
  7. Comprehensive Audit Logging
  8. API Security & Rate Limiting
- Real-time analytics and charts
- Security scoring system

### 🔍 L4 Explainability Hub (5000)
- **4 AI Interpretability Methods:**
  - SHAP Force Plots (feature contributions)
  - LIME Explanations (local interpretable)
  - GradCAM Heatmaps (attention visualization)
  - Decision Paths (step-by-step reasoning)
- **12 Explainability Assessment Modules:**
  1. Explanation Methods (92%)
  2. Explanation Quality (88%)
  3. Coverage & Completeness (85%)
  4. Fidelity Testing (72%)
  5. Feature Consistency (68%)
  6. Stability Testing (85%)
  7. Prediction Logging (100%)
  8. Model Versioning (95%)
  9. Audit Trail (98%)
  10. Documentation (75%)
  11. Intended Use (80%)
  12. Change Management (60%)
- **4-Category Scoring:**
  - Explanation Generation (35% weight) = 88%
  - Explanation Reliability (30% weight) = 75%
  - Traceability & Auditability (25% weight) = 98%
  - Documentation Transparency (10% weight) = 72%
  - **Overall Score: 85/100** ✅ (Exceeds 80% benchmark)

---

## **🔧 TROUBLESHOOTING**

### Issue: "Port already in use"
```powershell
# Find and kill process using the port
netstat -ano | findstr ":8501"
taskkill /PID <PID> /F
```

### Issue: "Python not found"
Make sure virtual environment exists:
```powershell
cd C:\Users\khan\Downloads\iraqaf_starter_kit
ls venv/Scripts/python.exe
```

### Issue: "Module not found" (SHAP, Flask, etc.)
Install missing packages:
```powershell
cd C:\Users\khan\Downloads\iraqaf_starter_kit
.\venv\Scripts\pip install flask flask-cors shap lime matplotlib
```

### Issue: Script won't run (Permission denied)
Enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## **📚 FILE LOCATIONS**

| File | Purpose |
|------|---------|
| `START_ALL_DASHBOARDS.ps1` | PowerShell launcher (Recommended) |
| `START_ALL_DASHBOARDS.py` | Python launcher (Cross-platform) |
| `dashboard/app.py` | Main Dashboard (Streamlit) |
| `dashboard/privacy_security_hub.py` | Security Hub (Flask) |
| `dashboard/hub_explainability_app.py` | L4 Hub (Flask) |

---

## **🎯 QUICK START CHECKLIST**

- [ ] Virtual environment activated (`venv` folder exists)
- [ ] Dependencies installed (Flask, Streamlit, SHAP, LIME, etc.)
- [ ] Ports 8501, 8502, 5000 are available (not blocked)
- [ ] PowerShell execution policy allows scripts
- [ ] You're in the correct directory: `C:\Users\khan\Downloads\iraqaf_starter_kit`

---

## **💡 PRO TIPS**

1. **Use Method 1 (PowerShell script)** - Easiest and most reliable
2. **Don't close browser tabs** - Keep them open for quick navigation
3. **Check terminal windows** - Each shows live server output for debugging
4. **Bookmark the URLs** - Save time accessing dashboards
5. **Use Ctrl+Shift+Esc** - Open Task Manager to see running processes
6. **Run as Admin** - Sometimes needed for port binding (if issues occur)

---

## **🎉 YOU'RE ALL SET!**

Just run one command and all three dashboards start automatically:

```powershell
.\START_ALL_DASHBOARDS.ps1
```

Everything will be running and accessible in your browser! 🚀

---

**Questions?** Check the terminal output for error messages or refer to individual dashboard documentation.
