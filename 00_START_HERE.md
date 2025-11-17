#  Getting Started - IRAQAF Dashboard

Welcome! This guide will get you up and running in 5 minutes.

##  Quick Setup (5 minutes)

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Launch Dashboard
```bash
streamlit run dashboard/app.py
```

You'll see:
```
Local URL: http://localhost:8501
```

### 3. Login
Use default credentials:
- **Username**: admin
- **Password**: admin_default_123

### 4. Explore Dashboard
After login, you'll see:
-  **Evidence Management** - Upload and manage compliance evidence
-  **5 Assessment Modules** (L1-L5)
-  **Export & Reports** - Generate compliance reports

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
- Role-based access control supports: Admin, Analyst, Viewer
- Create new accounts in the **Sign Up** tab on login page

##  Module Overview

| Module | Focus | Use Case |
|--------|-------|----------|
| **L1**  | Governance & Regulatory | Audit compliance tracking |
| **L2**  | Privacy & Security | Security posture assessment |
| **L3**  | Fairness | Bias detection and fairness metrics |
| **L4**  | Explainability | Model transparency analysis |
| **L5**  | Operations | Performance monitoring |

##  Configuration

### Change Admin Password
The default credentials are in `configs/users.json`. Change them immediately in production:
```json
{
  "admin": {
    "password_hash": "new_hash_here",
    "role": "admin"
  }
}
```

### Adjust Session Timeout
Edit the session timeout in `dashboard/app.py` (currently 8 hours):
```python
SESSION_TIMEOUT = 8 * 60 * 60  # in seconds
```

##  Troubleshooting

### Dashboard won't start
```bash
# Kill any existing Streamlit process
Get-Process streamlit -ErrorAction SilentlyContinue | Stop-Process -Force

# Try again
streamlit run dashboard/app.py --logger.level=debug
```

### Port 8501 already in use
```bash
# Use a different port
streamlit run dashboard/app.py --server.port=8502
```

### Missing modules
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

##  Next Steps

1.  Run the dashboard
2.  Upload your first compliance evidence
3.  Explore the module assessment features
4.  Generate your first report
5.  Customize for your organization

##  Learn More

- **README.md** - Full project documentation
- **QUICK_START.md** - Command reference
- **dashboard/app.py** - Main application code
- **configs/** - Configuration examples

##  Pro Tips

- Use **Ctrl+Shift+R** to refresh Streamlit apps
- Uploaded files are stored in `data/uploads/`
- Reports are saved in `reports/` directory
- Check `logs/` for debugging information

---

**Need Help?** Check the README.md or visit the GitHub repository.

**Last Updated**: November 2025
