#  Getting Started - IRAQAF Dashboard

Welcome! This guide will get you up and running in 5 minutes.

##  Quick Setup (5 minutes)

### 1. Activate Virtual Environment
\\\ash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
\\\

### 2. Launch Main Dashboard
\\\ash
streamlit run dashboard/app.py --server.port 8501
\\\

You'll see:
\\\
Local URL: http://localhost:8501
\\\

### 3. Login
Use default credentials:
- **Username**: admin
- **Password**: admin_default_123

### 4. Explore Dashboard
After login, you'll see:
-  **Evidence Management** - Upload and manage compliance evidence
-  **5 Assessment Modules** (L1-L5) - Core compliance assessments
-  **GQAS Scoring** - Aggregate quality assurance score
-  **Export & Reports** - Generate compliance reports

### 5. Access Privacy & Security Hub (NEW)
In the left sidebar, scroll to ** Security Tools** section and click:
- ** Privacy & Security Hub** - Opens dedicated security assessment tool
- Or access directly at: http://localhost:8502

##  Privacy & Security Hub

A dedicated security assessment tool with 11 specialized modules:

1. ** Dashboard Overview** - Security metrics and compliance status
2. ** PII Detection & Anonymization** - Personal data identification
3. ** Encryption Validator** - Encryption strength analysis
4. ** Model Integrity Checker** - Model verification
5. ** Adversarial Attack Testing** - Vulnerability testing
6. ** GDPR Rights Manager** - Rights management
7. ** L2 Historical Metrics** - L2 privacy & security trends and historical analytics
8. ** MFA Manager** - Multi-factor authentication
9. ** Data Retention Manager** - Data lifecycle policies
10. ** Quick Assessment Wizard** - Fast assessment workflow

### Launch Privacy & Security Hub (Optional)
If running separately:
\\\ash
# In a new terminal
streamlit run dashboard/privacy_security_hub.py --server.port 8502
\\\

##  What You Can Do

### Upload Evidence
1. Go to **Evidence Management**  **Upload & Pin** tab
2. Click ** Choose Files** to upload documents
3. Select which modules the evidence applies to (checkboxes)
4. Click ** Save & Pin Files**

### View Evidence Index
1. Go to **Evidence Management**  ** Evidence Index** tab
2. Select a module to see all indexed files
3. Browse organized evidence by category

### Export Reports
1. Go to **Evidence Management**  ** Sync & Export** tab
2. Select export format (CSV, PDF, JSON, Word)
3. Choose date range (optional)
4. Click **Download**

Alternatively, use the ** Export & Reports** sidebar option for quick exports.

##  Security & Authentication

- All sessions are encrypted with SHA-256
- Sessions timeout after 8 hours
- Role-based access control: Admin, Analyst, Viewer
- Create new accounts in the **Sign Up** tab on login page
- Privacy & Security Hub includes advanced security assessments

##  Module Overview

| Module | Focus | Use Case |
|--------|-------|----------|
| **L1**  | Governance & Regulatory | Audit compliance tracking |
| **L2**  | Privacy & Security | Security posture (also in Hub with historical metrics) |
| **L3**  | Fairness | Bias detection and fairness metrics |
| **L4**  | Explainability | Model transparency analysis |
| **L5**  | Operations | Performance monitoring |

##  Configuration

### Change Admin Password
The default credentials are in \configs/users.json\. Change them immediately in production:
\\\json
{
  "admin": {
    "password_hash": "new_hash_here",
    "role": "admin"
  }
}
\\\

### Adjust Session Timeout
Edit the session timeout in \dashboard/app.py\ (currently 8 hours):
\\\python
SESSION_TIMEOUT = 8 * 60 * 60  # in seconds
\\\

##  Troubleshooting

### Dashboard won't start
\\\ash
# Kill any existing Streamlit process
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force

# Try again
streamlit run dashboard/app.py --logger.level=debug
\\\

### Port 8501 already in use
\\\ash
# Use a different port
streamlit run dashboard/app.py --server.port=8502
\\\

### Privacy & Security Hub not accessible
\\\ash
# Make sure port 8502 is available
netstat -ano | findstr :8502

# Launch the hub if not running
streamlit run dashboard/privacy_security_hub.py --server.port 8502
\\\

### Missing modules
\\\ash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
\\\

##  Next Steps

1.  Run the main dashboard
2.  Access Privacy & Security Hub from sidebar
3.  Upload your first compliance evidence
4.  Explore the module assessment features
5.  Generate your first report
6.  Run security assessments in the Hub

##  Learn More

- **README.md** - Full project documentation
- **QUICK_START.md** - Command reference
- **dashboard/app.py** - Main application code
- **dashboard/privacy_security_hub.py** - Security hub code
- **configs/** - Configuration examples

##  Pro Tips

- Use **Ctrl+Shift+R** to refresh Streamlit apps
- Uploaded files are stored in \data/uploads/\
- Reports are saved in \eports/\ directory
- Check \logs/\ for debugging information
- L2 Historical Metrics in the Hub provide trend analysis for privacy & security

---

**Need Help?** Check the README.md or visit the GitHub repository.

**Last Updated**: November 2025
**Version**: 2.0 (with Privacy & Security Hub)
