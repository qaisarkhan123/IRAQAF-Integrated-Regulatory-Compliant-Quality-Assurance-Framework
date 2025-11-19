# IRAQAF Module 3: Fairness & Ethics ⚖️

**A comprehensive framework for algorithmic fairness evaluation, bias detection, and continuous monitoring in AI/ML systems.**

## 🎯 Overview

Module 3 provides production-ready tools for:

✅ **6 Fairness Metrics** - Demographic parity, equal opportunity, equalized odds, predictive parity, calibration, subgroup performance  
✅ **Bias Detection** - Automated identification of fairness violations across demographics  
✅ **Governance Assessment** - Scoring for Categories B, C, D compliance (10-item checklist)  
✅ **Drift Monitoring** - Statistical detection of fairness degradation over time  
✅ **Research Tracking** - Curated fairness research papers and best practices  
✅ **Interactive Dashboard** - Flask hub with 6 tabs and REST API (port 8505)  

---

## 📊 Key Features

### 6-Metric Fairness Framework

| Metric | Definition | Best Score |
|--------|-----------|-----------|
| **Demographic Parity** | Equal positive prediction rate across groups | Gap < 0.05 → 1.0 |
| **Equal Opportunity** | Equal TPR (recall) across groups | Gap < 0.05 → 1.0 |
| **Equalized Odds** | Equal TPR and FPR across groups | Gap < 0.05 → 1.0 |
| **Predictive Parity** | Equal precision across groups | Gap < 0.05 → 1.0 |
| **Calibration** | Equal Expected Calibration Error (ECE) | Gap < 0.05 → 1.0 |
| **Subgroup Performance** | Accuracy across intersectional subgroups | Ratio > 0.90 → 1.0 |

### Governance Assessment (10 Items)

- **Category B** (Bias Detection & Mitigation): Training data bias, mitigation techniques, proxy variables, fairness-accuracy tradeoff
- **Category C** (Ethical Governance): Ethics committee, stakeholder consultation, accountability, incident response
- **Category D** (Continuous Monitoring): Drift detection, subgroup performance tracking

### Overall Scoring

```
Module3Score = 0.40 × CategoryA (Metrics)
             + 0.25 × CategoryB (Bias Detection)
             + 0.20 × CategoryC (Ethics Governance)
             + 0.15 × CategoryD (Monitoring)
```

**Risk Levels**: High / Medium / Low (based on score and critical issues)

---

## 🚀 Quick Start

### 1. Start the Hub

```bash
python dashboard/fairness_ethics_hub.py
```

Open: **http://localhost:8505**

### 2. Run a Quick Assessment

```python
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine
import pandas as pd
import numpy as np

# Your data
y_true = np.array([1, 0, 1, 0, 1, 1, 0, 0])
y_pred = np.array([1, 0, 1, 0, 1, 0, 0, 0])
sensitive_features = pd.DataFrame({'gender': ['F']*4 + ['M']*4})

# Evaluate
engine = BiasDetectionEngine()
report = engine.evaluate_fairness(y_true, y_pred, sensitive_features)

print(f"Fairness Score: {report.category_a_score:.1%}")
```

### 3. Read Full Documentation

- 📖 `MODULE3_DOCUMENTATION.md` - Complete API reference
- 🏃 `QUICKSTART.md` - 5-minute examples
- 🧪 `fairness/tests/test_module3.py` - Usage examples

---

## 📁 Directory Structure

```
fairness/
├── MODULE3_DOCUMENTATION.md      # Complete guide
├── QUICKSTART.md                 # Quick examples
├── README.md                     # This file
│
├── models.py                     # Data models (10 dataclasses)
├── api.py                        # Scoring API
│
├── metrics/
│   └── fairness_metrics.py       # 6 fairness metrics
├── bias_engine/
│   └── bias_detection_engine.py  # Metric orchestration
├── governance/
│   └── governance_checker.py     # Governance scoring
├── monitoring/
│   └── fairness_monitor.py       # Drift detection
├── research_tracker/
│   └── research_tracker.py       # Papers & best practices
│
└── tests/
    └── test_module3.py           # 15+ comprehensive tests

dashboard/
└── fairness_ethics_hub.py        # Flask hub (port 8505)
```

---

## 💻 Core Components

### Component 1: Fairness Metrics Library
Compute 6 complementary fairness metrics with exact thresholds from academic literature.

**File**: `fairness/metrics/fairness_metrics.py` (600+ lines)

```python
from fairness.metrics.fairness_metrics import compute_all_fairness_metrics

metrics = compute_all_fairness_metrics(y_true, y_pred, sensitive_features, y_score)
print(metrics.demographic_parity['scores'])
print(metrics.subgroup_performance['per_subgroup_metrics'])
```

### Component 2: Bias Detection Engine
Orchestrates metrics and identifies critical bias issues.

**File**: `fairness/bias_engine/bias_detection_engine.py` (240 lines)

```python
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine

engine = BiasDetectionEngine()
report = engine.evaluate_fairness(y_true, y_pred, sensitive_features)
print(f"Score: {report.category_a_score}")
print(f"Critical Issues: {report.critical_issues}")
```

### Component 3: Governance Checker
Scores Categories B, C, D based on documentation/process.

**File**: `fairness/governance/governance_checker.py` (450+ lines)

```python
from fairness.governance.governance_checker import GovernanceChecker

checker = GovernanceChecker()
report = checker.assess_governance(governance_inputs)
print(f"Governance Score: {report.category_b_score + report.category_c_score + report.category_d_score} / 3.0")
```

### Component 4: Fairness Monitoring
Detects statistical changes in fairness metrics (3 methods).

**File**: `fairness/monitoring/fairness_monitor.py` (380+ lines)

```python
from fairness.monitoring.fairness_monitor import FairnessMonitor

monitor = FairnessMonitor()
drift_report = monitor.detect_fairness_drift('system_id', baseline, current)
print(f"Drift Severity: {drift_report.overall_severity}")
```

### Component 5: Research Tracker
Curated fairness research papers and best practices.

**File**: `fairness/research_tracker/research_tracker.py` (280+ lines)

```python
from fairness.research_tracker import get_research_tracker

tracker = get_research_tracker()
papers = tracker.get_recent_papers(topic_filter='equalized_odds')
practices = tracker.get_recommended_practices()
```

### Component 6: Module 3 API
Integrates all components into single score with weighted averaging.

**File**: `fairness/api.py` (420+ lines)

```python
from fairness.api import Module3API

api = Module3API()
assessment = api.compute_complete_assessment(fairness_report, governance_report)
json_output = api.generate_json_report(assessment)
html_report = api.generate_html_report(assessment)
```

---

## 🌐 Flask Hub (Port 8505)

Interactive dashboard with 6 tabs:

| Tab | Features |
|-----|----------|
| **Dashboard** | Overall scores, category breakdown, risk level |
| **Assessment** | Metric details, critical/major/minor gaps, recommendations |
| **Monitoring** | Drift status, control charts, alerts |
| **Research** | Curated papers, best practices |
| **API** | REST endpoint documentation |
| **About** | Feature summary, metric glossary |

### REST Endpoints

```bash
# Get dashboard data
GET http://localhost:8505/api/module3/dashboard

# Get monitoring status
GET http://localhost:8505/api/module3/monitoring

# Get research papers
GET http://localhost:8505/api/module3/research

# Get metric definitions
GET http://localhost:8505/api/module3/metrics
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest fairness/tests/test_module3.py -v
```

### Test Coverage
- ✓ Metric computation accuracy
- ✓ Bias detection engine
- ✓ Governance scoring
- ✓ Drift detection
- ✓ End-to-end assessment
- ✓ Edge cases (small groups, missing features)

### Example Test Usage
```python
def test_demographic_parity():
    # Perfect parity: all groups have 50% positive rate
    metrics = compute_all_fairness_metrics(y_true, y_pred, perfect_parity_features)
    assert metrics.demographic_parity['scores'] == 1.0
```

---

## 📋 Use Cases

### Use Case 1: Model Audit
Evaluate existing model for fairness issues:
```python
report = engine.evaluate_fairness(y_true, y_pred, sensitive_features)
# Check category_a_score and critical_issues
```

### Use Case 2: Governance Compliance
Assess compliance with IRAQAF governance requirements:
```python
report = checker.assess_governance(governance_inputs)
# Check category_b_score, category_c_score, category_d_score
```

### Use Case 3: Continuous Monitoring
Track fairness over time and detect degradation:
```python
monitor.log_fairness_metric('system', 'metric_name', value)
drift_report = monitor.detect_fairness_drift('system', baseline, current)
```

### Use Case 4: Research & Learning
Discover latest fairness research and best practices:
```python
papers = tracker.get_recent_papers()
practices = tracker.get_recommended_practices()
```

---

## 🔑 Key Concepts

### Fairness Metrics

- **Demographic Parity (DP)**: Ensures equal positive prediction rate across groups
  - Common baseline metric, but can perpetuate downstream discrimination
  
- **Equal Opportunity (EO)**: Ensures equal True Positive Rate (TPR) across groups
  - Focuses on false negatives; important for high-stakes scenarios
  
- **Equalized Odds (EO²)**: Combines equal TPR and FPR across groups
  - Most restrictive; rarely achievable without significant tradeoffs
  
- **Predictive Parity (PP)**: Ensures equal precision across groups
  - Important when costs of false positives differ by group
  
- **Calibration**: Ensures model confidence matches actual accuracy across groups
  - Prediction probabilities calibrated to true positive rates
  
- **Subgroup Performance**: Accuracy consistency across intersectional groups
  - Catches "fairness gerrymandering" where aggregated metrics hide disparities

### Governance Categories

- **Category B**: Bias detection and mitigation (pre/in/post-processing)
- **Category C**: Ethical governance and oversight (ethics review, accountability)
- **Category D**: Continuous fairness monitoring and tracking

### Drift Detection

- **Delta-Based**: Simple change detection (current vs. baseline)
- **Statistical (t-test)**: Tests if difference is statistically significant
- **Control Charts**: Monitors against baseline mean ± 2σ
- **Moving Windows**: Compares non-overlapping time periods

---

## 📚 References

**Key Papers**:
- Hardt et al. (2016) - "Equality of Opportunity in Supervised Learning"
- Barocas, Hardt, Narayanan (2023) - "Fairness and Machine Learning"
- Buolamwini & Gebru (2018) - "Preventing Fairness Gerrymandering"
- Liu et al. (2018) - "Delayed Impact of Fair Machine Learning"

**Specifications**:
- IRAQAF: Integrated Regulatory Compliance & Quality Assurance Framework
- FDA Guidance: AI/ML in Medical Devices

---

## 🛠️ Integration

### Add to Main Dashboard

Add navigation button in `app.py`:
```python
if st.button("⚖️ Module 3: Fairness & Ethics", use_container_width=True):
    import webbrowser
    webbrowser.open("http://localhost:8505")
```

### Use in Custom Scripts
```python
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine
from fairness.api import Module3API

# Your model evaluation workflow...
engine = BiasDetectionEngine()
report = engine.evaluate_fairness(...)

# Continue with governance and scoring...
api = Module3API()
assessment = api.compute_complete_assessment(...)
```

---

## ⚠️ Important Notes

### Fairness Impossibilities
- Cannot optimize all metrics simultaneously
- Different metrics appropriate for different use cases
- Trade-offs must be explicitly documented

### Implementation Considerations
- Use multiple metrics; no single metric captures all fairness notions
- Include intersectionality; single-attribute analysis can hide disparities
- Involve stakeholders; fairness is not purely technical
- Monitor continuously; fairness issues can emerge over time
- Document trade-offs; fairness-accuracy tradeoffs are real

### Data Requirements
- Minimum 100+ samples per sensitive group for reliable estimates
- Balanced or imbalanced datasets both supported
- Missing sensitive attributes handled gracefully

---

## 📖 Documentation

- **MODULE3_DOCUMENTATION.md** - Complete API reference
- **QUICKSTART.md** - 5-minute getting started guide
- **test_module3.py** - Usage examples via tests
- Inline code documentation - Comprehensive docstrings

---

## 📞 Support

### Troubleshooting

**Import Errors:**
```bash
pip install scipy  # If statistical tests fail
pip install flask  # If hub fails to start
```

**Hub Not Starting:**
```bash
# Check if port 8505 is in use
netstat -ano | findstr :8505
```

**Metric Computation Errors:**
- Ensure y_true and y_pred same length
- Ensure sensitive_features same number of rows
- For small datasets, expect higher variance

### Getting Help
1. Review inline code documentation and docstrings
2. Check test files for usage examples
3. Read MODULE3_DOCUMENTATION.md
4. Run `pytest fairness/tests/test_module3.py -v` for test examples

---

## ✅ Quality Checklist

- ✅ Production-ready code with comprehensive docstrings
- ✅ Type hints throughout
- ✅ 15+ comprehensive tests with edge case coverage
- ✅ All thresholds from IRAQAF specification implemented exactly
- ✅ Modular architecture with clear separation of concerns
- ✅ No external unimplemented dependencies
- ✅ In-memory database with SQL-compatible interface
- ✅ Interactive Flask dashboard with 6 tabs
- ✅ REST API for programmatic access
- ✅ Curated research tracker with 10+ papers

---

## 🎓 Learning Resources

### For Beginners
Start with `QUICKSTART.md` for 5-minute examples.

### For ML Engineers
Review `fairness/metrics/fairness_metrics.py` for metric implementation details.

### For Data Scientists
Check `fairness/tests/test_module3.py` for realistic workflows.

### For Governance
Read `fairness/governance/governance_checker.py` for compliance requirements.

---

## 🌟 Features at a Glance

| Feature | Details |
|---------|---------|
| **6 Fairness Metrics** | DP, EO, EO², PP, Calibration, Subgroup |
| **Bias Detection** | Automatic critical issue extraction |
| **Governance** | 10-item compliance assessment |
| **Monitoring** | 3-method drift detection |
| **Research** | 10+ curated papers + best practices |
| **API** | JSON/HTML reporting |
| **Hub** | 6-tab interactive dashboard (port 8505) |
| **Tests** | 15+ comprehensive tests |
| **Documentation** | Complete inline + guides |

---

**IRAQAF Module 3: Fairness & Ethics** - Making AI/ML systems fairer, more transparent, and compliant. ⚖️

v1.0 | 2025-01-15 | Production-Ready
