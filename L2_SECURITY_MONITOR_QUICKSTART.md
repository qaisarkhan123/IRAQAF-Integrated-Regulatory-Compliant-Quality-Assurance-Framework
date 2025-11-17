# L2 Security Monitor - Quick Start Guide

## 🚀 Quick Launch (5 Minutes)

### Step 1: Start the Dashboard

```bash
cd dashboard
streamlit run l2_privacy_security_monitor.py
```

**Access:** http://localhost:8501

### Step 2: Login

**Default Credentials:**
- Username: `admin`
- Password: `admin_default_123`

### Step 3: Run Your First Scan

1. Click **"🔍 Run Scan"** tab
2. Enter framework name (e.g., "My API Server")
3. Select scan type: "full", "partial", or "quick"
4. Click **"🔍 Start Scan"**
5. View results instantly

## 📊 Dashboard Sections

| Tab | Purpose | Who |
|-----|---------|-----|
| 📊 Overview | See security metrics & trends | Everyone |
| 🔍 Run Scan | Scan frameworks/apps | Analyst/Admin |
| 📋 Scan History | Review past scans & reports | Everyone |
| ⚠️ Vulnerabilities | Track security issues | Everyone |
| 📋 Policies | View compliance frameworks | Everyone |

## 🎯 Common Tasks

### Create a New User Account

1. Click "📝 Create Account" on login page
2. Enter username, password, and role
3. Click "✅ Create Account"
4. Login with new credentials

### Run a Security Scan

1. Go to **"🔍 Run Scan"**
2. Enter framework name
3. Select scan type:
   - **full**: Complete security assessment (~5 min)
   - **partial**: Key areas only (~2 min)
   - **quick**: Basic checks (~1 min)
4. Review score (0-100)

### Interpret Security Score

- 🟢 **90+**: Excellent
- 🟡 **75-89**: Good
- 🟠 **60-74**: Fair
- 🔴 **0-59**: Poor

### View Security Report

1. Go to **"📋 Scan History"**
2. Find your scan
3. Click **"📄 View Report"**
4. See detailed findings & recommendations

### Check Vulnerabilities

1. Go to **"⚠️ Vulnerabilities"**
2. Filter by severity (Critical, High, Medium, Low)
3. Click vulnerability for details

### Review Compliance Policies

1. Go to **"📋 Policies"**
2. Select policy category
3. View requirements for compliance

## 🔐 Security Features

### Multi-Level Checks

✅ **Encryption** - TLS, certificates, data protection  
✅ **Authentication** - MFA, passwords, sessions  
✅ **Data Protection** - PII handling, masking, retention  
✅ **Access Control** - RBAC, privileges, audit logs  
✅ **Vulnerabilities** - CVE tracking, patch status  
✅ **Compliance** - GDPR, HIPAA, ISO 27001, etc.

### Role-Based Access

- **Viewer**: View reports & policies
- **Analyst**: Run scans, create accounts
- **Admin**: Full access, user management

## 💡 Tips & Tricks

1. **Schedule Regular Scans**
   - Weekly full scans for critical systems
   - Daily quick scans for monitoring

2. **Monitor Trends**
   - Check "📊 Overview" for score trends
   - Track improvements over time

3. **Act on Recommendations**
   - Each scan provides specific recommendations
   - Prioritize critical findings

4. **Use Scan History**
   - Compare scores before/after fixes
   - Document compliance efforts

5. **Export Reports**
   - Reports can be exported as PDF/Excel
   - Use for compliance documentation

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't login | Check credentials, create new account |
| Can't run scan | Need analyst/admin role |
| Low score | Review recommendations & fix issues |
| Page slow | Try "quick" scan instead of "full" |
| Lost data | Scans stored in `data/security_scans/` |

## 📞 Need Help?

- Check **"❓ Help & Documentation"** in sidebar
- Review `L2_SECURITY_MONITOR_GUIDE.md`
- Check logs in `logs/dashboard.log`

## 🎓 Learning Path

**Beginner:**
1. Run first scan
2. Check security score
3. Read recommendations

**Intermediate:**
4. Run multiple scans
5. Compare framework scores
6. Track vulnerabilities

**Advanced:**
7. Create custom policies
8. Export compliance reports
9. Integrate with alerts

## 🔄 Integration with Other Modules

### Create Alerts for Issues

```python
from alerts import AlertManager
from security_monitor import SecurityMonitor

alerts = AlertManager()
scan = SecurityMonitor().start_scan("API Server")

if scan.overall_score < 70:
    alerts.create_alert(
        type="security_issue",
        severity="high",
        title=f"Low Security Score: {scan.overall_score}",
        domain="security"
    )
```

### Export Security Report

```python
from exports import ExportManager
from security_monitor import SecurityMonitor

exporter = ExportManager()
monitor = SecurityMonitor()
report = monitor.generate_report(scan_id)

# Export to PDF
exporter.to_pdf(report, "security_report.pdf")

# Export to Excel
exporter.to_excel(report, "security_report.xlsx")
```

## 📈 Best Practices

✅ **Do:**
- Run regular scans
- Act on recommendations
- Track vulnerabilities
- Update policies quarterly
- Document compliance

❌ **Don't:**
- Ignore critical findings
- Skip scans
- Use weak passwords
- Share credentials
- Delay security fixes

## 🔒 Security Reminders

- Use strong passwords for admin accounts
- Enable MFA when available
- Restrict scan access to authorized users
- Keep credentials confidential
- Audit access logs regularly

---

**Quick Reference:**
- Dashboard: http://localhost:8501
- Default Login: admin / admin_default_123
- Data Path: `data/security_scans/`
- Docs: `L2_SECURITY_MONITOR_GUIDE.md`

**Ready to go?** 🚀  
Start with "📊 Overview" to see your security landscape!
