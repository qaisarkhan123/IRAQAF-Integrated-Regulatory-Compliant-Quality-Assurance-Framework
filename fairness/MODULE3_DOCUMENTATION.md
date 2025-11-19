# IRAQAF Module 3: Fairness & Ethics
## Complete Implementation Guide

### Overview

**Module 3** provides a comprehensive framework for evaluating and monitoring algorithmic fairness in AI systems. It covers **6 fairness metrics**, **bias detection**, **ethical governance**, and **continuous monitoring** with clear scoring thresholds derived from academic literature.

**Overall Module 3 Score = 0.40×CategoryA + 0.25×CategoryB + 0.20×CategoryC + 0.15×CategoryD**

---

## Architecture

```
fairness/
├── __init__.py                          # Package exports
├── models.py                            # Data models (DB, snapshots, scores)
├── api.py                               # Main scoring & reporting API
│
├── metrics/
│   ├── __init__.py
│   └── fairness_metrics.py              # 6 fairness metrics library
│
├── bias_engine/
│   ├── __init__.py
│   └── bias_detection_engine.py         # Orchestrates metrics, identifies issues
│
├── governance/
│   ├── __init__.py
│   └── governance_checker.py            # Categories B, C, D scoring
│
├── monitoring/
│   ├── __init__.py
│   └── fairness_monitor.py              # Drift detection (statistical + control charts)
│
├── research_tracker/
│   ├── __init__.py
│   └── research_tracker.py              # Curated research papers & best practices
│
└── tests/
    ├── __init__.py
    └── test_module3.py                  # Comprehensive test suite
```

---

## Component 1: Fairness Metrics Library

### 6 Metrics Evaluated

#### 1. **Demographic Parity** (Statistical Parity)
- **Definition**: Equal positive prediction rate across demographic groups
- **Formula**: DPG = max(P(Ŷ=1|group_i)) − min(P(Ŷ=1|group_i))
- **Scoring**:
  - DPG < 0.05 → **1.0** (excellent)
  - 0.05–0.10 → **0.7** (good)
  - 0.10–0.15 → **0.5** (acceptable)
  - > 0.15 → **0.2** (poor)

#### 2. **Equal Opportunity** (TPR Parity)
- **Definition**: Equal True Positive Rate across groups (on positive cases)
- **Formula**: TPR_gap = max(TPR_i) − min(TPR_i) where TPR_i = TP_i / (TP_i + FN_i)
- **Scoring**: Same thresholds as demographic parity

#### 3. **Equalized Odds** (TPR + FPR)
- **Definition**: Equal TPR AND equal FPR across groups
- **Formula**: Combined_gap = max(TPR_gap, FPR_gap)
- **Scoring**: Same thresholds

#### 4. **Predictive Parity** (Precision Fairness)
- **Definition**: Equal precision (PPV) across groups for positive predictions
- **Formula**: PPV_gap = max(PPV_i) − min(PPV_i) where PPV_i = TP_i / (TP_i + FP_i)
- **Scoring**: Same thresholds

#### 5. **Calibration Gap**
- **Definition**: Expected Calibration Error (ECE) consistency across groups
- **Method**: Bin predictions (0-10%, 10-20%, ..., 90-100%), compute ECE per group
- **Formula**: Cal_gap = max(ECE_i) − min(ECE_i)
- **Scoring**: Same thresholds

#### 6. **Subgroup Performance** (Intersectional)
- **Definition**: Accuracy consistency across subgroups (including intersectional)
- **Metric**: Min/Max accuracy ratio across ALL subgroups
- **Scoring**:
  - Ratio > 0.90 → **1.0** (excellent)
  - 0.85–0.90 → **0.7** (good)
  - 0.75–0.85 → **0.5** (acceptable)
  - < 0.75 → **0.2** (poor)

### Usage Example

```python
import numpy as np
import pandas as pd
from fairness.metrics.fairness_metrics import compute_all_fairness_metrics

# Prepare data
y_true = np.array([1, 0, 1, 0, 1, 1, 0, 0])
y_pred = np.array([1, 0, 1, 0, 1, 0, 0, 0])  # Predictions
y_score = np.array([0.9, 0.1, 0.8, 0.2, 0.85, 0.4, 0.15, 0.3])  # Probabilities

# Protected attributes
sensitive_features = pd.DataFrame({
    'gender': ['F', 'F', 'F', 'F', 'M', 'M', 'M', 'M'],
    'age_group': ['<30', '<30', '30+', '30+', '<30', '<30', '30+', '30+']
})

# Compute all metrics
metrics = compute_all_fairness_metrics(y_true, y_pred, sensitive_features, y_score)

# Access results
print(f"Demographic Parity Score: {metrics.demographic_parity['scores']}")
print(f"Equal Opportunity Score: {metrics.equal_opportunity['scores']}")
print(f"Subgroup Performance: {metrics.subgroup_performance['per_subgroup_metrics']}")
```

---

## Component 2: Bias Detection Engine

Orchestrates all fairness metrics and identifies critical issues.

### Usage Example

```python
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine

engine = BiasDetectionEngine()

# Run fairness evaluation
report = engine.evaluate_fairness(
    y_true=y_true,
    y_pred=y_pred,
    sensitive_features=sensitive_features,
    y_score=y_score,
    system_id='my_model_v1',
    model_version='1.0'
)

# Results
print(f"Category A Score: {report.category_a_score:.2%}")
print(f"Critical Issues: {report.critical_issues}")
print(f"Worst Performing Groups: {report.worst_performing_groups}")
print(f"Largest Gaps: {report.largest_gaps}")

# Export to dict
report_dict = report.to_dict()
```

### Outputs

- **Category A Score**: Weighted average of all 6 metric scores
- **Critical Issues**: List of fairness violations (score < 0.5)
- **Worst Performing Groups**: Subgroups with lowest accuracy
- **Largest Gaps**: Metrics with biggest disparities

---

## Component 3: Governance Checker

Evaluates Categories B, C, D based on documentation/process requirements.

**SCORING APPROACH:**
Each item (7-16) is scored on a 4-point scale: 0.0 (not implemented), 0.5 (partial), 0.7 (substantial), 1.0 (complete). **Category scores are simple arithmetic averages:**
- **Category B** = avg(items 7-10)
- **Category C** = avg(items 11-14)  
- **Category D** = avg(items 15-16)

These category scores are then weighted in the final Module 3 score: 0.40×A + 0.25×B + 0.20×C + 0.15×D

### Category B: Bias Detection & Mitigation (Items 7-10)

| Item | Requirement | Score | Condition |
|------|-------------|-------|-----------|
| 7. Training Data Bias | Assessment of historical bias and demographics | 1.0 | Comprehensive analysis documented |
| | | 0.6 | Demographics documented, limited bias analysis |
| | | 0.5 | Minimal documentation |
| | | 0.0 | No documentation |
| 8. Bias Mitigation | Techniques applied and evaluated | 1.0 | Multiple techniques applied & evaluated |
| | | 0.6 | Some techniques, limited evaluation |
| | | 0.5 | Techniques mentioned, not evaluated |
| | | 0.0 | No techniques documented |
| 9. Proxy Variables | Identification and mitigation plan | 1.0 | Identified with mitigation plan |
| | | 0.6 | Identified, mitigation incomplete |
| | | 0.5 | Mentioned, not systematic |
| | | 0.0 | No analysis |
| 10. Fairness-Accuracy Tradeoff | Documentation with rationale | 1.0 | Explicit, with rationale & stakeholder input |
| | | 0.6 | Mentioned with rationale |
| | | 0.5 | Acknowledged, minimal docs |
| | | 0.0 | No documentation |

### Category C: Ethical Governance & Oversight (Items 11-14)

| Item | Requirement | Score | Condition |
|------|-------------|-------|-----------|
| 11. Ethics Committee | Approval and documentation | 1.0 | Approved and documented |
| | | 0.6 | Reviewed with limited docs |
| | | 0.5 | Mentioned, not formal |
| | | 0.0 | No involvement |
| 12. Stakeholder Consultation | Including affected communities | 1.0 | Comprehensive, feedback incorporated |
| | | 0.6 | Conducted with limited docs |
| | | 0.5 | Mentioned, minimal evidence |
| | | 0.0 | No consultation |
| 13. Accountability | Clear responsibility assignment | 1.0 | Clear structure with named roles |
| | | 0.6 | Structure defined, incomplete |
| | | 0.5 | Mentioned, vague |
| | | 0.0 | No structure |
| 14. Incident Response | Fairness-specific procedures | 1.0 | Comprehensive plan with procedures |
| | | 0.6 | Plan exists, incomplete |
| | | 0.5 | Mentioned, not detailed |
| | | 0.0 | No plan |

### Category D: Continuous Fairness Monitoring (Items 15-16)

| Item | Requirement | Score | Condition |
|------|-------------|-------|-----------|
| 15. Fairness Drift Detection | Design & documentation | 1.0 | Comprehensive system, designed & documented |
| | | 0.6 | Approach documented, incomplete |
| | | 0.5 | Mentioned, not detailed |
| | | 0.0 | No documentation |
| 16. Subgroup Performance Tracking | Including intersectional | 1.0 | Systematic (intersectional), designed & documented |
| | | 0.6 | Approach documented, incomplete |
| | | 0.5 | Mentioned, not systematic |
| | | 0.0 | No tracking |

### Usage Example

```python
from fairness.governance.governance_checker import GovernanceChecker

checker = GovernanceChecker()

governance_inputs = {
    'training_data_bias_assessment': {
        'comprehensive_bias_analysis': True,
        'demographic_distribution': True,
        'historical_bias_checked': True,
        'documented': True
    },
    'ethics_committee_approval': {
        'approved': True,
        'documented': True,
        'approval_date': '2025-01-15'
    },
    'accountability_assignment': {
        'clear': True,
        'named_roles': True,
        'roles': ['fairness_lead', 'ethics_officer']
    },
    # ... more items ...
}

report = checker.assess_governance(governance_inputs)

print(f"Category B Score: {report.category_b_score:.2%}")
print(f"Category C Score: {report.category_c_score:.2%}")
print(f"Category D Score: {report.category_d_score:.2%}")
print(f"Item Explanations: {report.item_explanations}")
```

---

## Component 4: Fairness Drift Monitoring

Detects statistical changes in fairness metrics over time.

### Drift Detection Methods

#### 1. **Delta-Based Detection** (Simple)
- Compare current vs. baseline
- Classify severity: minor (<0.03), moderate (0.03-0.07), major (>0.07)

#### 2. **Statistical Testing** (t-test)
- Compare metric windows (baseline vs. recent)
- Two-sample t-test with α=0.05
- Returns p-value and severity

#### 3. **Control Charts** (±2σ limits)
- Compute mean and std from baseline period
- Flag values outside ±2σ
- Continuous monitoring approach

#### 4. **Moving Window Comparison**
- Compare two non-overlapping time windows
- Detect sustained changes in fairness

### Usage Example

```python
from fairness.monitoring.fairness_monitor import FairnessMonitor

monitor = FairnessMonitor()

# Log baseline metrics
baseline = {
    'demographic_parity_gap_gender': 0.05,
    'tpr_gap_race': 0.04,
    'calibration_gap_age': 0.03
}

# Log current metrics
current = {
    'demographic_parity_gap_gender': 0.12,  # 0.07 change
    'tpr_gap_race': 0.04,
    'calibration_gap_age': 0.08  # 0.05 change
}

# Detect drift
report = monitor.detect_fairness_drift('system_id', baseline, current)

print(f"Drift Detected: {report.drift_detected}")
print(f"Severity: {report.overall_severity}")
print(f"Detected Drifts: {report.detected_drifts}")
print(f"Recommendations: {report.recommendations}")

# Statistical drift detection
drift_detected, p_value, severity = monitor.detect_statistical_drift(
    'system_id', 'demographic_parity_gap_gender'
)

# Control chart drift detection
drift_detected, distance, severity = monitor.detect_control_chart_drift(
    'system_id', 'demographic_parity_gap_gender'
)
```

### Drift Severity Classification

- **None** (change < 0.03): Continue normal monitoring
- **Minor** (0.03-0.07): Monitor closely, watch for escalation
- **Moderate** (0.07-0.15): Investigate root cause, prepare for retraining
- **Major** (> 0.15): Immediate action required, recommend retraining

---

## Component 5: Research Tracker

Curated database of fairness research papers and best practices.

**PAPER SOURCES & REFRESH:**
- **Current**: Static list of 10+ foundational papers (development/demo)
- **Production Refresh**: Integrate automated scrapers:
  * ArXiv API: `arxiv_query = "fairness AND (machine learning OR AI)"`
  * Hugging Face Hub: Fairness models and datasets
  * Papers with Code: Implementation links and benchmarks
  * Scheduled refresh: Daily/hourly depending on use case
- **Best Practices**: Compiled from 50+ papers, updated quarterly

### Included Sample Papers

- **Fairness and Machine Learning** (Barocas, Hardt, Narayanan 2023) - Comprehensive textbook
- **Equality of Opportunity** (Hardt et al. 2016) - Equal opportunity criterion
- **Delayed Impact of Fair ML** (Liu et al. 2018) - Feedback loops and dynamics
- **Fairness and Calibration** (Kleinberg et al. 2018) - Impossibilities
- **Intersectional Subgroup Fairness** (Buolamwini & Gebru 2018) - Intersectionality
- Plus 5+ more papers on fairness, bias mitigation, governance

### Usage Example

```python
from fairness.research_tracker import get_research_tracker

tracker = get_research_tracker()

# Get recent papers (static in dev, dynamic in prod with refresh)
papers = tracker.get_recent_papers(limit=10, topic_filter='equalized_odds', year_from=2015)

# Get papers by topic
calibration_papers = tracker.get_papers_by_topic('calibration')

# Get best practices (governance, metrics, mitigation, etc.)
practices = tracker.get_recommended_practices()
# Returns dict with sections:
# - fairness_metrics
# - bias_detection
# - bias_mitigation
# - governance
# - monitoring
# - transparency

# Search papers
results = tracker.search_papers('intersectionality')

# Production: Trigger refresh (production code should call periodically)
# tracker.refresh_papers_from_arxiv(query="fairness machine learning")
```

---

## Component 6: Module 3 Scoring & API

Final integration that combines all components into single score.

### Score Aggregation

```
Module3Score = 0.40 × CategoryA_Score
              + 0.25 × CategoryB_Score
              + 0.20 × CategoryC_Score
              + 0.15 × CategoryD_Score
```

### Risk Level Determination

- **High Risk**: Critical count > 2 OR CategoryA < 0.3 OR CategoryC < 0.3
- **Medium Risk**: Critical count > 0 OR CategoryA < 0.5 OR CategoryB < 0.5
- **Low Risk**: All categories ≥ 0.7

### Usage Example

```python
from fairness.api import Module3API
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine
from fairness.governance.governance_checker import GovernanceChecker

# Run components
engine = BiasDetectionEngine()
fairness_report = engine.evaluate_fairness(y_true, y_pred, sensitive_features, y_score)

checker = GovernanceChecker()
governance_report = checker.assess_governance(governance_inputs)

# Compute Module 3 score
api = Module3API()
assessment = api.compute_complete_assessment(
    fairness_report,
    governance_report,
    system_id='my_model'
)

# Export as JSON
json_report = api.generate_json_report(assessment)

# Export as HTML
html_report = api.generate_html_report(assessment)
```

### Output Format

```json
{
  "module": "IRAQAF_MODULE_3_FAIRNESS",
  "system_id": "my_model",
  "timestamp": "2025-01-15T10:30:00Z",
  "overall_score": 0.84,
  "overall_score_pct": "84%",
  "risk_level": "Low",
  "summary": "Module 3 Fairness & Ethics Assessment: Excellent (84%) fairness score with Low risk...",
  "category_scores": {
    "algorithmic_fairness": 0.78,
    "bias_detection_mitigation": 0.85,
    "ethical_governance": 0.92,
    "continuous_monitoring": 0.81
  },
  "critical_gaps": [
    {
      "issue": "Demographic Parity Violation: Gender",
      "category": "Algorithmic Fairness",
      "recommendation": "Adjust model decision thresholds per gender group..."
    }
  ],
  "major_gaps": [...],
  "minor_gaps": [...],
  "metrics_detail": {...},
  "governance_detail": {...},
  "drift_detail": null
}
```

---

## Flask Hub: Fairness & Ethics Hub (Port 8505)

A Flask application providing interactive dashboard and REST API.

### Running the Hub

```bash
python dashboard/fairness_ethics_hub.py
```

Access at: **http://localhost:8505**

### Features

- 📊 **Dashboard**: Overall scores, category breakdowns, gap analysis
- 📋 **Assessment**: Detailed fairness metrics and findings
- 📈 **Monitoring**: Drift detection status and alerts
- 📚 **Research**: Latest papers and best practices
- 🔌 **API**: REST endpoints for programmatic access

### REST Endpoints

- `GET /api/module3/dashboard` - Dashboard data
- `GET /api/module3/monitoring` - Monitoring status
- `GET /api/module3/research` - Research papers
- `GET /api/module3/metrics` - Metric descriptions

---

## Testing

Run comprehensive test suite:

```bash
pytest fairness/tests/test_module3.py -v
```

### Test Coverage

- ✓ Metric correctness (demographic parity, equal opportunity, etc.)
- ✓ Edge cases (small groups, missing features, degenerate cases)
- ✓ Bias detection engine
- ✓ Governance scoring logic
- ✓ Drift detection
- ✓ End-to-end assessment

---

## Best Practices

### Fairness Evaluation

1. **Use Multiple Metrics**: No single metric captures all fairness notions
2. **Include Intersectionality**: Analyze subgroups across multiple attributes
3. **Regular Auditing**: At deployment and ongoing (weekly/monthly)
4. **Stakeholder Input**: Include domain experts and affected communities

### Bias Mitigation

1. **Pre-processing**: Resampling, reweighting, data augmentation
2. **In-processing**: Fairness-aware training, constrained optimization
3. **Post-processing**: Threshold optimization, output calibration
4. **Document Trade-offs**: Explicitly document fairness-accuracy trade-offs

### Governance

1. **Ethics Review**: Obtain committee approval
2. **Stakeholder Consultation**: Include affected communities
3. **Clear Accountability**: Named roles and procedures
4. **Incident Response**: Document procedures and escalation

### Monitoring

1. **Continuous Tracking**: All fairness metrics
2. **Drift Detection**: Statistical monitoring with clear triggers
3. **Alerting**: Notify team of changes
4. **Retraining**: Have clear triggers for model updates

---

## References

**Foundational Papers**:
- Hardt et al. (2016) - "Equality of Opportunity in Supervised Learning"
- Barocas et al. (2023) - "Fairness and Machine Learning"
- Buolamwini & Gebru (2018) - "Preventing Fairness Gerrymandering"

**Specification**:
- IRAQAF (Integrated Regulatory Compliance & Quality Assurance Framework)
- Medical device fairness requirements
- FDA guidance on AI/ML in medical devices

---

## Support & Documentation

For more information, see:
- `MODULE3_ARCHITECTURE.md` - Detailed architecture
- `FAIRNESS_METRICS_GUIDE.md` - Metrics explanations
- `GOVERNANCE_REQUIREMENTS.md` - Governance details
- `API_REFERENCE.md` - Full API documentation
