# 🚀 IRAQAF Continuous Compliance Setup Guide

## Quick Start (5 minutes)

### Step 1: Enable GitHub Actions

1. Go to your repository settings
2. Enable Actions (usually enabled by default)
3. Verify workflow file exists: `.github/workflows/iraqaf-compliance-check.yml`

### Step 2: Add GitHub Secrets

1. Go to **Settings → Secrets and variables → Actions**
2. Add the following secrets:

#### Slack Webhook (Optional)
```
Name: SLACK_WEBHOOK
Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

Get Slack webhook: https://api.slack.com/messaging/webhooks

#### AWS Credentials (Optional - for S3 uploads)
```
Name: AWS_ACCESS_KEY_ID
Value: your_access_key

Name: AWS_SECRET_ACCESS_KEY
Value: your_secret_key
```

### Step 3: First Run

Simply push to `main` or `develop` branch:

```bash
git push origin main
```

Then check **Actions** tab to see your workflow running.

## 🧪 Local Testing

Test the pipeline locally before pushing:

```bash
# Install dependencies
pip install -r requirements.txt

# Run local pipeline
python scripts/run_local_pipeline.py \
  --threshold 75 \
  --required-modules L1,L2,L3 \
  --min-score 80
```

This will:
1. ✅ Run IRAQAF assessment
2. ✅ Generate markdown report
3. ✅ Check threshold
4. ✅ Verify deployment readiness

## 📋 Customization

### Change Compliance Threshold

Edit `.github/workflows/iraqaf-compliance-check.yml`:

```yaml
- name: Fail if compliance threshold not met
  run: |
    python scripts/check_compliance_threshold.py \
      --input reports/compliance_*.json \
      --threshold 85 \  # ← Change here
      --fail-on-low-score
```

### Change Required Modules

Edit `scripts/verify_deployment_readiness.py`:

```python
required_modules = ['L1', 'L2', 'L3', 'L4']  # Add L4, L5 as needed
min_score = 80  # Adjust minimum score
```

### Change Check Schedule

Edit `.github/workflows/iraqaf-compliance-check.yml`:

```yaml
schedule:
  # Run compliance checks daily at 2 AM UTC
  - cron: '0 2 * * *'  # ← Change this cron expression
```

Common cron examples:
- `0 * * * *` - Every hour
- `0 2 * * *` - Daily at 2 AM UTC
- `0 10 * * 1` - Every Monday at 10 AM UTC
- `0 0 1 * *` - First day of month at midnight

## 🔍 Monitoring

### View Workflow Runs

1. Go to **Actions** tab
2. Click on **IRAQAF Continuous Compliance Check**
3. See all workflow runs with status

### Download Reports

1. Click on a workflow run
2. Scroll to **Artifacts**
3. Download `iraqaf-compliance-reports`
4. Extract and view `compliance_report.md`

### View PR Comments

Compliance reports are automatically posted on pull requests:

1. Go to pull request
2. Scroll to comments
3. Find IRAQAF compliance report

## 🚦 Deployment Protection

### Require Checks Before Merge

1. Go to **Settings → Branches → Branch protection rules**
2. Click **Add rule** for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select:
   - `compliance-check`
   - `deployment-gate`

This prevents merging until compliance passes!

## 📊 What Gets Checked?

The pipeline runs IRAQAF assessment on:

- **L1: Governance** - Code compliance and standards
- **L2: Privacy** - Data privacy and security
- **L3: Fairness** - Bias and fairness checks
- **L4: Explainability** - Model interpretability
- **L5: Operations** - Operational readiness

Each module gets a score, and overall Global Quality Score (GQAS) is calculated.

## 🆘 Troubleshooting

### Workflow Not Running

**Problem:** Push to main but no workflow triggered

**Solution:**
1. Check `.github/workflows/` directory exists
2. Verify branch name is `main` or `develop`
3. Check Actions are enabled in settings
4. Try pushing to a different branch

### Python Module Import Error

**Problem:** `Import "core" could not be resolved`

**Solution:**
1. Ensure requirements.txt is up to date
2. Run locally: `pip install -r requirements.txt`
3. Check that `core/` directory exists in project root

### Slack Notification Not Working

**Problem:** No Slack message received

**Solution:**
1. Verify `SLACK_WEBHOOK` secret is set
2. Test webhook URL manually
3. Check Slack workspace permissions
4. Remove `if: always()` condition to only notify on failure

### S3 Upload Failing

**Problem:** Upload to S3 fails

**Solution:**
1. Verify AWS credentials are correct
2. Check S3 bucket exists
3. Remove S3 upload steps if not needed (edit workflow YAML)
4. Test credentials locally: `aws s3 ls`

## 📈 Best Practices

1. **Run Locally First** - Always test with `run_local_pipeline.py` before pushing
2. **Fix Issues Immediately** - Don't merge with low compliance scores
3. **Review Reports** - Check the markdown reports for recommendations
4. **Update Regularly** - Review and update thresholds quarterly
5. **Document Changes** - When changing thresholds, update this guide

## 🎯 Success Criteria

✅ **Workflow configured** - Pipeline runs on every push  
✅ **Reports generated** - Markdown reports available  
✅ **Thresholds set** - Compliance requirements defined  
✅ **Branch protection** - Main branch requires passing checks  
✅ **Team notified** - Slack or email alerts configured  

## 📚 Next Steps

1. ✅ Complete setup (you're here!)
2. ⬜ Make first push to trigger workflow
3. ⬜ Review generated compliance report
4. ⬜ Set up Slack notifications (optional)
5. ⬜ Enable branch protection rules
6. ⬜ Add to team documentation

## 💬 Questions?

Check:
- `.github/DEPLOYMENT_GATE.md` - Detailed documentation
- `scripts/` - Python script documentation
- GitHub Actions logs - Workflow execution details
- IRAQAF docs - Assessment methodology
