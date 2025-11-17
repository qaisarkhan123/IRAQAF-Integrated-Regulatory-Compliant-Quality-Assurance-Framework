# L2 Privacy/Security Monitoring System

## Overview

The L2 Privacy/Security Monitoring System is a real-time security and privacy assessment platform that scans frameworks and applications to evaluate their security posture. It integrates with the shared authentication system and provides comprehensive compliance checking against major regulatory frameworks.

## Features

### 🔒 Core Security Checks

1. **Encryption Assessment**
   - TLS/SSL version verification
   - Cipher suite validation
   - Certificate validity checks
   - Data at-rest encryption verification

2. **Authentication & Access Control**
   - Multi-factor authentication (MFA) status
   - Password policy enforcement
   - Session timeout management
   - Role-based access control (RBAC)
   - Privilege escalation monitoring

3. **Data Protection**
   - PII (Personally Identifiable Information) classification
   - Data masking implementation
   - Backup encryption
   - Data retention policies
   - GDPR compliance verification

4. **Vulnerability Management**
   - Continuous vulnerability scanning
   - Known vulnerability database
   - CVE tracking
   - Penetration testing results

5. **Compliance Assessment**
   - GDPR compliance checking
   - HIPAA readiness
   - PCI-DSS validation
   - ISO 27001 certification status
   - SOX compliance verification

### 📊 Security Score Calculation

The overall security score (0-100) is calculated using weighted categories:

| Category | Weight | Focus |
|----------|--------|-------|
| Encryption | 25% | Data protection in transit/rest |
| Authentication | 20% | User identity verification |
| Data Protection | 20% | PII and sensitive data handling |
| Access Control | 15% | Permission management |
| Vulnerabilities | 15% | Known security issues |
| Compliance | 5% | Regulatory adherence |

**Score Interpretation:**
- 🟢 **90-100:** Excellent security posture
- 🟡 **75-89:** Good security with minor improvements needed
- 🟠 **60-74:** Fair security, attention recommended
- 🔴 **0-59:** Poor security, immediate action required

### 🚀 Real-Time Monitoring

- Continuous security scanning
- Alert generation for critical issues
- Vulnerability tracking
- Compliance status updates
- Historical trend analysis

## Installation

### Prerequisites

```bash
pip install streamlit pandas plotly
```

### Import Modules

```python
from security_monitor import SecurityMonitor, SecurityScan
from authentication import AuthenticationManager
```

## Usage

### Basic Scan

```python
from security_monitor import SecurityMonitor

# Initialize monitor
monitor = SecurityMonitor()

# Run a security scan
scan = monitor.start_scan(
    framework_name="API Server",
    scan_type="full"  # "full", "partial", or "quick"
)

# Check results
print(f"Overall Score: {scan.overall_score}/100")
print(f"Recommendations: {len(scan.recommendations)}")
```

### Get Security Summary

```python
summary = monitor.get_security_summary()

print(f"Total Scans: {summary['total_scans']}")
print(f"Average Score: {summary['average_score']}/100")
print(f"Frameworks Scanned: {summary['frameworks_scanned']}")

# Framework-specific stats
for fw_stat in summary['framework_stats']:
    print(f"{fw_stat['framework']}: {fw_stat['average_score']}/100")
```

### Generate Security Report

```python
report = monitor.generate_report(scan_id="SCAN-xyz123")

print(f"Report ID: {report['report_id']}")
print(f"Executive Summary: {report['executive_summary']}")
print(f"Recommendations: {report['recommendations']}")
```

### Add Known Vulnerabilities

```python
vuln = monitor.add_vulnerability(
    framework="API Server",
    vulnerability_id="VULN-001",
    severity="high",  # "critical", "high", "medium", "low"
    description="SQL injection vulnerability in user endpoint",
    cve="CVE-2024-12345"
)
```

### View Security Policies

```python
# Get all policies
all_policies = monitor.get_policies()

# Get policies by category
gdpr_policies = monitor.get_policies(category="privacy")
```

## Dashboard UI

### Authentication

- Login with shared credentials (admin/admin_default_123)
- Role-based access control
- User registration for new accounts

### Dashboard Tabs

#### 1. 📊 Overview
- Security summary metrics
- Framework status visualization
- Average security scores
- Last scan timestamps

#### 2. 🔍 Run Scan
- Start new security scans
- Select scan type (full/partial/quick)
- Real-time scan results
- Category-specific findings

#### 3. 📋 Scan History
- View past scans
- Filter by framework
- Filter by score threshold
- Generate detailed reports

#### 4. ⚠️ Vulnerabilities
- Known vulnerabilities database
- Filter by severity
- CVE tracking
- Status management

#### 5. 📋 Policies
- Compliance frameworks (GDPR, HIPAA, ISO 27001, etc.)
- Policy requirements
- Category filtering

## Running the L2 Monitor Dashboard

```bash
cd dashboard
streamlit run l2_privacy_security_monitor.py
```

Access at: http://localhost:8501

**Default Login:**
- Username: `admin`
- Password: `admin_default_123`
- Role: Administrator

## Data Storage

Security scan data is stored in JSON format:

```
data/
├── security_scans/
│   ├── security_scans.json      # All scan results
│   ├── vulnerabilities.json     # Vulnerability database
│   └── security_policies.json   # Policy configurations
```

### Scan Data Structure

```json
{
  "scan_id": "SCAN-07a1157b15a6",
  "framework": "API Server",
  "timestamp": "2024-11-17T14:30:00",
  "scan_type": "full",
  "results": {
    "encryption": {
      "status": "passed",
      "score": 95,
      "details": { ... }
    },
    "authentication": { ... },
    "data_protection": { ... },
    "access_control": { ... },
    "vulnerability": { ... },
    "compliance": { ... }
  },
  "overall_score": 92,
  "recommendations": [ ... ]
}
```

## Security Recommendations Engine

The system automatically generates recommendations based on scan results:

**Example Recommendations:**
- 🟢 Upgrade to TLS 1.3
- 🟡 Implement mandatory MFA
- 🔴 Apply critical security patches immediately
- 🟠 Conduct compliance audit
- 🔵 Enable continuous security monitoring

## Integration with Other Modules

### Shared Authentication

The L2 Monitor uses the same `AuthenticationManager` as other dashboard modules:

```python
from authentication import AuthenticationManager

auth = AuthenticationManager()
user = auth.authenticate_user("admin", "admin_default_123")
```

### Alert Integration

Integrate with AlertManager to create alerts for security findings:

```python
from alerts import AlertManager
from security_monitor import SecurityMonitor

alerts = AlertManager()
monitor = SecurityMonitor()

scan = monitor.start_scan("API Server")
if scan.overall_score < 70:
    alerts.create_alert(
        type="security_issue",
        severity="high",
        title=f"Low Security Score: {scan.overall_score}",
        description=f"Framework {scan.framework} has security issues",
        domain="security"
    )
```

### Export Compliance Reports

Use the ExportManager to generate compliance reports:

```python
from exports import ExportManager

exporter = ExportManager()
report = monitor.generate_report(scan_id)

# Export as PDF
pdf_path = exporter.to_pdf(report, filename="security_report.pdf")

# Export as Excel
excel_path = exporter.to_excel(report, filename="security_report.xlsx")
```

## Best Practices

1. **Regular Scanning**
   - Run full scans weekly for critical systems
   - Use quick scans for daily monitoring
   - Run partial scans after deployments

2. **Vulnerability Management**
   - Review CVEs weekly
   - Track remediation status
   - Set remediation timelines by severity

3. **Compliance**
   - Map policies to your systems
   - Document compliance status
   - Maintain audit trails

4. **Monitoring**
   - Track score trends
   - Set alert thresholds
   - Review recommendations regularly

5. **Access Control**
   - Assign roles appropriately
   - Restrict scan permissions to analysts/admins
   - Audit user access regularly

## Security Considerations

1. **Data Privacy**
   - Scan data contains sensitive information
   - Restrict access to authorized personnel
   - Encrypt stored scan data

2. **Authentication**
   - Use strong passwords
   - Enable MFA for admin accounts
   - Rotate credentials regularly

3. **Compliance**
   - Maintain compliance documentation
   - Track audit findings
   - Document remediation efforts

## Troubleshooting

### Scan Not Starting
- Check authentication credentials
- Verify user role (needs analyst or admin)
- Check disk space for data storage

### Low Security Scores
- Review recommendations
- Address critical findings first
- Re-scan after implementing fixes

### Missing Policies
- Verify policies.json exists
- Check policy data format
- Reload page to refresh

## API Reference

### SecurityMonitor Class

```python
class SecurityMonitor:
    def start_scan(framework_name, scan_type) -> SecurityScan
    def get_recent_scans(framework=None, limit=10) -> List[Dict]
    def get_scan_by_id(scan_id) -> Optional[Dict]
    def get_security_summary() -> Dict
    def add_vulnerability(framework, vulnerability_id, severity, description, cve)
    def get_policies(category=None) -> List[Dict]
    def generate_report(scan_id) -> Optional[Dict]
```

### SecurityScan Class

```python
class SecurityScan:
    scan_id: str
    framework: str
    timestamp: str
    scan_type: str
    results: Dict
    overall_score: int
    recommendations: List[Dict]
    scan_duration: float
```

## Future Enhancements

- Real-time threat detection
- Integration with SIEM systems
- Machine learning-based anomaly detection
- Automated remediation suggestions
- Multi-tenant support
- API for third-party integrations

## Support

For issues or questions, contact the development team or check the logs in `logs/dashboard.log`.

---

**Version:** 1.0.0  
**Last Updated:** November 17, 2024  
**Status:** Production Ready ✅
