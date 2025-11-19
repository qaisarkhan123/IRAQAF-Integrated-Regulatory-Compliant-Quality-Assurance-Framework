# Module 3 Quick Start Guide

## Installation & Setup

### 1. Prerequisites
- Python 3.9+
- Existing IRAQAF installation
- Dependencies: numpy, pandas, scikit-learn, scipy, flask

### 2. Verify Module Installation

```bash
cd fairness
python -c "import models; import metrics; import bias_engine; print('✓ Module 3 installed')"
```

### 3. Start the Flask Hub

```bash
python dashboard/fairness_ethics_hub.py
```

Then open: **http://localhost:8505**

---

## 5-Minute Example

### Step 1: Prepare Your Data

```python
import numpy as np
import pandas as pd

# Your model predictions
y_true = np.array([1, 0, 1, 1, 0, 0, 1, 0])
y_pred = np.array([1, 0, 1, 0, 0, 0, 1, 0])
y_score = np.array([0.9, 0.1, 0.8, 0.4, 0.2, 0.15, 0.85, 0.3])

# Protected attributes
sensitive_features = pd.DataFrame({
    'gender': ['F', 'F', 'F', 'F', 'M', 'M', 'M', 'M'],
    'race': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
})
```

### Step 2: Evaluate Fairness

```python
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine

engine = BiasDetectionEngine()
report = engine.evaluate_fairness(
    y_true, y_pred, sensitive_features, y_score,
    system_id='my_model_v1'
)

print(f"Category A Score: {report.category_a_score:.1%}")
```

### Step 3: Assess Governance

```python
from fairness.governance.governance_checker import GovernanceChecker

checker = GovernanceChecker()
gov_report = checker.assess_governance({
    'training_data_bias_assessment': {'comprehensive': True},
    'ethics_committee_approval': {'approved': True},
    'accountability_assignment': {'clear': True}
})

print(f"Governance Score: {(gov_report.category_b_score + gov_report.category_c_score + gov_report.category_d_score) / 3:.1%}")
```

### Step 4: Get Complete Score

```python
from fairness.api import Module3API

api = Module3API()
assessment = api.compute_complete_assessment(report, gov_report, system_id='my_model_v1')

print(f"Overall Score: {assessment['overall_score']:.1%}")
print(f"Risk Level: {assessment['risk_level']}")
print(f"Summary: {assessment['summary']}")
```

### Step 5: Export Report

```python
# JSON export
json_report = api.generate_json_report(assessment)

# HTML export
html_report = api.generate_html_report(assessment)
```

---

## Common Tasks

### Check for Bias

```python
# All critical issues
for issue in report.critical_issues:
    print(f"⚠ {issue['type']}: {issue['description']}")
    print(f"  Recommendation: {issue['recommendation']}")
```

### Monitor Drift

```python
from fairness.monitoring.fairness_monitor import FairnessMonitor

monitor = FairnessMonitor()

# Log metrics over time
for week in range(1, 5):
    metrics = compute_current_metrics()  # Your function
    monitor.log_fairness_metric('my_model', 'demo_parity_gap', metrics['dp_gap'], timestamp=week)

# Detect drift
drift_report = monitor.detect_fairness_drift(
    'my_model',
    baseline={'demo_parity_gap': 0.05},
    current={'demo_parity_gap': 0.15}
)
print(f"Drift: {drift_report.overall_severity}")
```

### Get Research

```python
from fairness.research_tracker import get_research_tracker

tracker = get_research_tracker()
papers = tracker.get_recent_papers(topic_filter='equalized_odds')
practices = tracker.get_recommended_practices()
```

---

## Integration with Main Dashboard

Add to `app.py` sidebar:

```python
# In your navigation buttons
st.button("⚖️ Module 3: Fairness & Ethics", 
          icon="⚖️",
          use_container_width=True,
          on_click=lambda: webbrowser.open("http://localhost:8505"))
```

---

## Test It

```bash
# Run test suite
pytest fairness/tests/test_module3.py -v

# Run specific test
pytest fairness/tests/test_module3.py::test_bias_detection_engine -v
```

---

## Troubleshooting

### Import Errors
```bash
pip install scipy  # If statistical tests fail
```

### Flask Hub Not Starting
```bash
# Check if port 8505 is available
netstat -ano | findstr :8505

# If in use, kill process or change port in fairness_ethics_hub.py
```

### Metric Computation Errors
- Ensure y_true and y_pred are same length
- Ensure sensitive_features has same number of rows
- For small datasets (< 50 samples), expect higher variance

---

## Next Steps

1. ✅ Review `MODULE3_DOCUMENTATION.md` for detailed API
2. ✅ Run test suite to validate installation
3. ✅ Integrate hub into main dashboard
4. ✅ Start monitoring your models
5. ✅ Set up governance documentation

---

## Key Metrics Reference

| Metric | Metric | Best Case | Threshold |
|--------|--------|-----------|-----------|
| Demographic Parity Gap | DP | < 0.05 | Score 1.0 |
| Equal Opportunity Gap | EO | < 0.05 | Score 1.0 |
| Equalized Odds Gap | EO² | < 0.05 | Score 1.0 |
| Predictive Parity Gap | PP | < 0.05 | Score 1.0 |
| Calibration Gap (ECE) | Cal | < 0.05 | Score 1.0 |
| Subgroup Accuracy Ratio | Subgroup | > 0.90 | Score 1.0 |

---

## Support

For issues or questions:
1. Check inline code documentation
2. Review tests for usage examples
3. Consult MODULE3_DOCUMENTATION.md
