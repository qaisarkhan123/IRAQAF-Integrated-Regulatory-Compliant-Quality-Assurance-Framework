# 🚀 IRAQAF Continuous Compliance Pipeline

Automated deployment gate that runs IRAQAF quality assessments on every push and pull request.

## 🎯 Features

✅ **Automated Compliance Checks** - Run IRAQAF assessments on every code change  
✅ **PR Comments** - Get compliance feedback directly in pull requests  
✅ **Deployment Gates** - Block deployments that don't meet compliance thresholds  
✅ **Scheduled Checks** - Run daily compliance audits  
✅ **Report Artifacts** - Archive compliance reports for audit trails  
✅ **Slack Notifications** - Get real-time compliance alerts  

## 📋 Workflow Configuration

The pipeline is defined in `.github/workflows/iraqaf-compliance-check.yml`

### Triggers

- **Push to main/develop** - Runs compliance checks
- **Pull Requests** - Adds compliance comment to PR
- **Daily Schedule** - 2 AM UTC compliance audit
- **Manual Dispatch** - Can be triggered manually

### Workflow Steps

1. **Checkout Code** - Get latest repository code
2. **Setup Python** - Initialize Python 3.11 environment
3. **Install Dependencies** - Install IRAQAF and requirements
4. **Run Assessment** - Execute IRAQAF quality checks
5. **Parse Results** - Generate markdown compliance report
6. **PR Comment** - Post results as comment on pull requests
7. **Upload Artifacts** - Archive reports for audit trail
8. **Slack Notification** - Alert team of results
9. **Deployment Gate** - Verify readiness for production

## 🔧 Configuration

### Thresholds

Edit `.github/workflows/iraqaf-compliance-check.yml`:

```yaml
- name: Fail if compliance threshold not met
  run: |
    python scripts/check_compliance_threshold.py \
      --input reports/compliance_*.json \
      --threshold 75 \  # Change this value
      --fail-on-low-score
```

### Required Modules

Edit `scripts/verify_deployment_readiness.py`:

```python
required_modules = ['L1', 'L2', 'L3']  # Customize as needed
min_score = 80  # Minimum score per module
```

### Notifications

Set up secrets in GitHub:

```bash
# Add to GitHub Secrets
SLACK_WEBHOOK  - Your Slack webhook URL
AWS_ACCESS_KEY_ID  - (optional) For S3 uploads
AWS_SECRET_ACCESS_KEY  - (optional) For S3 uploads
```

## 📊 Reports

### Generated Reports

- `compliance_report.md` - Human-readable markdown report
- `reports/compliance_*.json` - Raw IRAQAF results (JSON)
- `compliance_reports_*.tar.gz` - Archived reports

### Report Contents

- Global Quality Score
- Module-by-module breakdown
- Issues and their severity
- Risk profile classification
- Recommendations for improvement

## 🚦 Deployment Gate

Deployments to `main` branch require:

1. ✅ All modules score >= 75
2. ✅ No critical security issues
3. ✅ Compliance threshold met

### Bypass (Emergency Only)

For emergency deployments that must bypass compliance:

```bash
git push --force-with-lease  # Not recommended
```

## 🔍 Local Testing

Test the pipeline locally before pushing:

```bash
# Run compliance check
python scripts/run_compliance_check.py \
  --output reports/compliance_local.json

# Parse results
python scripts/parse_iraqaf_results.py \
  --input reports/compliance_local.json \
  --threshold 75 \
  --output compliance_report_local.md

# Check threshold
python scripts/check_compliance_threshold.py \
  --input reports/compliance_local.json \
  --threshold 75

# Verify deployment readiness
python scripts/verify_deployment_readiness.py \
  --compliance-report compliance_report_local.md \
  --required-modules L1,L2,L3 \
  --min-score 80
```

## 📈 Monitoring

### Check Workflow Status

Visit: https://github.com/YOUR_ORG/YOUR_REPO/actions

### View Reports

1. Click on workflow run
2. Download "iraqaf-compliance-reports" artifact
3. View `compliance_report.md`

### Historical Tracking

Reports are archived in:
- GitHub Actions artifacts (30-day retention)
- S3 bucket (if configured)
- Dashboard data directory

## 🎓 Best Practices

1. **Fix Before Merge** - Address compliance issues before PR merge
2. **Regular Reviews** - Check daily scheduled audit reports
3. **Document Changes** - Update IRAQAF policies when requirements change
4. **Monitor Trends** - Track compliance score trends over time
5. **Team Visibility** - Share reports with the team via Slack

## 🐛 Troubleshooting

### Workflow Fails at IRAQAF Step

```bash
# Check if IRAQAF is properly installed
pip list | grep iraqaf

# Verify core module path
python -c "from core.engine import IRAQAF"
```

### PR Comment Not Posting

- Check GitHub token permissions
- Verify workflow has `issues: write` permission
- Check branch protection rules

### S3 Upload Failing

- Verify AWS credentials are set in GitHub Secrets
- Check S3 bucket permissions
- Ensure bucket exists in specified region

## 📚 Additional Resources

- [IRAQAF Documentation](../README.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Compliance Standards](../docs/COMPLIANCE.md)

## 💬 Support

For issues or questions:
1. Check workflow run logs
2. Review compliance report
3. Contact the quality team
