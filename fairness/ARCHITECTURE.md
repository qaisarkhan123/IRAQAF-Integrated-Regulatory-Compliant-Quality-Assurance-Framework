# IRAQAF Module 3 - Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MAIN DASHBOARD (Port 8501)                            │
│                          Streamlit/Flask App                                 │
│                                                                              │
│  Navigation Buttons:                                                        │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ L4 Explain  │ │ L2 Security  │ │ L1 Regulations │ │ L3 Operations │     │
│  │ (5000)      │ │ (8502)       │ │ (8504)       │ │ (8503)       │         │
│  └─────────────┘ └──────────────┘ └──────────────┘ └──────────────┘         │
│  ┌──────────────────────────────────────────────────────────────────┐        │
│  │  ⚖️ Module 3: Fairness & Ethics (8505) - NEW                    │        │
│  └──────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┘
                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                MODULE 3: FAIRNESS & ETHICS HUB (Port 8505)                   │
│                           Flask Application                                  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │                      Web UI (6 Tabs)                            │        │
│  │                                                                  │        │
│  │  [Dashboard] [Assessment] [Monitoring] [Research] [API] [About]         │
│  └─────────────────────────────────────────────────────────────────┘        │
│                            │                                                 │
└────────────────────────────┼─────────────────────────────────────────────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
    ┌────────▼────┐ ┌────────▼────┐ ┌────────▼────┐
    │   User I/O  │ │   API Layer │ │  Dashboard  │
    │ (HTML/CSS)  │ │  (4 routes) │ │   Backend   │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │                │               │
           └────────────────┼───────────────┘
                            │
┌───────────────────────────┼───────────────────────────────────────────────────┐
│                   MODULE 3 PYTHON PACKAGE (/fairness/)                        │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ INPUT LAYER: Data Models (models.py)                               │   │
│  │                                                                      │   │
│  │  ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐        │   │
│  │  │MetricValue   │ │FairnessMetric    │ │GovernanceAssess  │        │   │
│  │  │              │ │Snapshot          │ │ment              │        │   │
│  │  └──────────────┘ └──────────────────┘ └──────────────────┘        │   │
│  │                                                                      │   │
│  │  ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐        │   │
│  │  │DriftEvent    │ │ResearchPaper     │ │Module3Score      │        │   │
│  │  │              │ │                  │ │                  │        │   │
│  │  └──────────────┘ └──────────────────┘ └──────────────────┘        │   │
│  │                                                                      │   │
│  │  FairnessDatabase: In-memory storage + accessors                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ COMPONENT 1: METRICS COMPUTATION (metrics/fairness_metrics.py)     │   │
│  │                                                                      │   │
│  │  Input: y_true, y_pred, sensitive_features, y_score               │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │ 6 FAIRNESS METRICS:                                        │   │   │
│  │  │                                                             │   │   │
│  │  │  1. Demographic Parity Gap        Gap < 0.05 → Score 1.0 │   │   │
│  │  │  2. Equal Opportunity (TPR Gap)   Gap < 0.05 → Score 1.0 │   │   │
│  │  │  3. Equalized Odds (TPR+FPR Gap)  Gap < 0.05 → Score 1.0 │   │   │
│  │  │  4. Predictive Parity (PPV Gap)   Gap < 0.05 → Score 1.0 │   │   │
│  │  │  5. Calibration Gap (ECE)         Gap < 0.05 → Score 1.0 │   │   │
│  │  │  6. Subgroup Performance Ratio    Ratio > 0.9 → Score 1.0│   │   │
│  │  │                                                             │   │   │
│  │  │  All metrics computed with exact IRAQAF thresholds        │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  Output: FairnessMetrics {                                         │   │
│  │    demographic_parity: {...},                                     │   │
│  │    equal_opportunity: {...},                                      │   │
│  │    equalized_odds: {...},                                         │   │
│  │    predictive_parity: {...},                                      │   │
│  │    calibration: {...},                                            │   │
│  │    subgroup_performance: {...}                                    │   │
│  │  }                                                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ COMPONENT 2: BIAS DETECTION (bias_engine/bias_detection_engine.py) │   │
│  │                                                                      │   │
│  │  BiasDetectionEngine.evaluate_fairness()                           │   │
│  │                                                                      │   │
│  │  Process:                                                           │   │
│  │    1. Call Component 1: Compute all 6 metrics                      │   │
│  │    2. Aggregate scores per sensitive attribute                     │   │
│  │    3. Extract critical issues (score < 0.5)                        │   │
│  │    4. Identify worst-performing subgroups                          │   │
│  │    5. Find largest fairness gaps                                   │   │
│  │                                                                      │   │
│  │  Output: FairnessReport {                                          │   │
│  │    category_a_score,         # Average of 6 metrics (40% weight)   │   │
│  │    critical_issues,          # Issues requiring action             │   │
│  │    worst_performing_groups,  # Bottom 5 subgroups                 │   │
│  │    largest_gaps              # Top 5 gaps across metrics           │   │
│  │  }                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ COMPONENT 3: GOVERNANCE (governance/governance_checker.py)         │   │
│  │                                                                      │   │
│  │  GovernanceChecker.assess_governance()                             │   │
│  │                                                                      │   │
│  │  Input: governance_inputs (documentation dict)                     │   │
│  │                                                                      │   │
│  │  Category B: Bias Detection & Mitigation (4 items)                │   │
│  │    Item 7:  Training data bias assessment                          │   │
│  │    Item 8:  Bias mitigation techniques                             │   │
│  │    Item 9:  Proxy variable analysis                                │   │
│  │    Item 10: Fairness-accuracy tradeoff                             │   │
│  │                                                                      │   │
│  │  Category C: Ethical Governance & Oversight (4 items)             │   │
│  │    Item 11: Ethics committee approval                              │   │
│  │    Item 12: Stakeholder consultation                               │   │
│  │    Item 13: Accountability assignment                              │   │
│  │    Item 14: Incident response plan                                 │   │
│  │                                                                      │   │
│  │  Category D: Continuous Monitoring (2 items)                      │   │
│  │    Item 15: Fairness drift detection                               │   │
│  │    Item 16: Subgroup performance tracking                          │   │
│  │                                                                      │   │
│  │  Scoring: Each item 0.0/0.5/0.7/1.0 based on documentation       │   │
│  │  Per-category averages: B_score, C_score, D_score                 │   │
│  │                                                                      │   │
│  │  Output: GovernanceReport {                                        │   │
│  │    category_b_score,                                              │   │
│  │    category_c_score,         # Each 25% weight                     │   │
│  │    category_d_score,         # Each 15% weight                     │   │
│  │    item_explanations         # Per-item reasoning                  │   │
│  │  }                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ COMPONENT 4: MONITORING (monitoring/fairness_monitor.py)           │   │
│  │                                                                      │   │
│  │  FairnessMonitor.detect_fairness_drift()                           │   │
│  │                                                                      │   │
│  │  3 Drift Detection Methods:                                         │   │
│  │                                                                      │   │
│  │  Method 1: Delta-Based                                             │   │
│  │    Compare: current_metric - baseline_metric                       │   │
│  │    Severity: < 0.03 (none), 0.03-0.07 (minor), 0.07-0.15 (mod),  │   │
│  │             > 0.15 (major)                                          │   │
│  │                                                                      │   │
│  │  Method 2: Statistical (t-test)                                    │   │
│  │    Compare: baseline_window vs current_window                       │   │
│  │    Output: drift_detected, p_value, severity                       │   │
│  │                                                                      │   │
│  │  Method 3: Control Charts                                          │   │
│  │    Limits: baseline_mean ± 2σ                                      │   │
│  │    Flag: Any value outside limits                                  │   │
│  │                                                                      │   │
│  │  Output: DriftReport {                                             │   │
│  │    drift_detected,                                                 │   │
│  │    overall_severity,                                               │   │
│  │    detected_drifts,      # Per-metric drift status                │   │
│  │    recommendations       # Action items                            │   │
│  │  }                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ COMPONENT 5: RESEARCH (research_tracker/research_tracker.py)       │   │
│  │                                                                      │   │
│  │  ResearchTracker: Curated fairness papers & best practices         │   │
│  │                                                                      │   │
│  │  10 Included Papers:                                               │   │
│  │    - Fairness and Machine Learning (2023)                         │   │
│  │    - Equality of Opportunity (2016)                               │   │
│  │    - Delayed Impact of Fair ML (2018)                            │   │
│  │    - Fairness and Calibration (2018)                             │   │
│  │    - Preventing Fairness Gerrymandering (2018)                   │   │
│  │    - Plus 5+ more foundational papers                            │   │
│  │                                                                      │   │
│  │  Methods:                                                          │   │
│  │    - get_recent_papers()          # Retrieve papers               │   │
│  │    - get_recommended_practices()  # Best practices guide          │   │
│  │    - search_papers()              # Full-text search              │   │
│  │    - get_papers_by_topic()        # Topic filtering               │   │
│  │    - add_paper()                  # Add new paper                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ COMPONENT 6: SCORING & API (api.py)                               │   │
│  │                                                                      │   │
│  │  Module3Scorer.compute_module3_score()                             │   │
│  │                                                                      │   │
│  │  Inputs: fairness_report, governance_report, drift_report         │   │
│  │                                                                      │   │
│  │  Scoring Formula:                                                  │   │
│  │    Module3_Score = 0.40 × CategoryA (Metrics)                     │   │
│  │                  + 0.25 × CategoryB (Bias Detection)              │   │
│  │                  + 0.20 × CategoryC (Ethics)                      │   │
│  │                  + 0.15 × CategoryD (Monitoring)                  │   │
│  │                                                                      │   │
│  │  Gap Classification:                                              │   │
│  │    Critical: score < 0.2                                          │   │
│  │    Major:    0.2 ≤ score < 0.5                                   │   │
│  │    Minor:    0.5 ≤ score < 0.8                                   │   │
│  │                                                                      │   │
│  │  Risk Level Determination:                                        │   │
│  │    High:    Critical > 2 OR CategoryA < 0.3 OR CategoryC < 0.3   │   │
│  │    Medium:  Critical > 0 OR CategoryA < 0.5 OR CategoryB < 0.5   │   │
│  │    Low:     All categories ≥ 0.7                                  │   │
│  │                                                                      │   │
│  │  Module3API: Full reporting                                        │   │
│  │    - compute_complete_assessment()  # Full JSON assessment         │   │
│  │    - generate_json_report()         # JSON output                  │   │
│  │    - generate_html_report()         # HTML dashboard              │   │
│  │                                                                      │   │
│  │  Output: Module3Score {                                           │   │
│  │    overall_score,        # Final weighted score                    │   │
│  │    overall_score_pct,    # Percentage (0-100%)                    │   │
│  │    risk_level,           # High/Medium/Low                         │   │
│  │    summary,              # Human-readable summary                  │   │
│  │    category_scores,      # A, B, C, D breakdown                   │   │
│  │    critical_gaps,        # Critical issues list                    │   │
│  │    major_gaps,           # Major gaps list                         │   │
│  │    minor_gaps            # Minor gaps list                         │   │
│  │  }                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
    ┌────▼──────┐           ┌──────▼──────┐         ┌────────▼────┐
    │  Database │           │   Logs      │         │  JSON/HTML  │
    │ (in-mem)  │           │ (optional)  │         │  Reports    │
    └───────────┘           └─────────────┘         └─────────────┘
```

---

## Data Flow Diagram

```
INPUT DATA
    │
    ├─► y_true (binary labels)
    ├─► y_pred (predictions)
    ├─► y_score (probabilities, optional)
    └─► sensitive_features (demographics)
        │
        │
    ┌───▼────────────────────────────────────┐
    │   COMPONENT 1: METRICS                 │
    │   compute_all_fairness_metrics()       │
    └───┬────────────────────────────────────┘
        │
        ├─► Demographic Parity Score
        ├─► Equal Opportunity Score
        ├─► Equalized Odds Score
        ├─► Predictive Parity Score
        ├─► Calibration Score
        └─► Subgroup Performance Score
            │
            │
    ┌───────▼─────────────────────────────┐
    │   COMPONENT 2: BIAS DETECTION       │
    │   BiasDetectionEngine.evaluate()    │
    └───┬─────────────────────────────────┘
        │
        ├─► Category A Score (40% weight)
        ├─► Critical Issues
        ├─► Worst Performing Groups
        └─► Largest Gaps
            │
            │
    ┌───────▼──────────────────────────────────┐
    │   COMPONENT 6: FINAL SCORING            │
    │   Module3Scorer.compute_score()         │
    └───┬──────────────────────────────────────┘
        │
        │ (Parallel paths)
        │
        ├─────────────┬─────────────────────────────────┐
        │             │                                 │
        │   ┌─────────▼──────────────────────────────┐  │
        │   │   COMPONENT 3: GOVERNANCE             │  │
        │   │   GovernanceChecker.assess()          │  │
        │   │                                       │  │
        │   ├─► Category B Score (25% weight)       │  │
        │   ├─► Category C Score (20% weight)       │  │
        │   └─► Category D Score (15% weight)       │  │
        │       │                                   │  │
        │       │                                   │  │
        │   ┌───▼────────────────────────────────┐  │  │
        │   │ COMPONENT 4: MONITORING           │  │  │
        │   │ FairnessMonitor.detect_drift()    │  │  │
        │   └───┬────────────────────────────────┘  │  │
        │       │                                   │  │
        │       └─► Drift Report (severity info)    │  │
        │           │                               │  │
        │           │                               │  │
        │           └───────────────────────────────┼──┼─┐
        │                                           │  │ │
        │                                           │  │ │
        └────────────────────────────────────────────┼──┼─┘
                                                   │  │
                ┌──────────────────────────────────┘  │
                │                                     │
        ┌───────▼────────────────────────────────────▼──┐
        │   COMPONENT 5: RESEARCH (optional)            │
        │   ResearchTracker.get_papers()               │
        │                                               │
        │   ├─► Recent papers                          │
        │   ├─► Best practices                         │
        │   └─► Recommendations                        │
        └───┬──────────────────────────────────────────┘
            │
            │
    ┌───────▼──────────────────────────────┐
    │   FINAL AGGREGATION                  │
    │   Module3API.compute_complete()      │
    └───┬──────────────────────────────────┘
        │
        ├─► Module3Score {
        │     overall_score: 0.84
        │     risk_level: "Low"
        │     category_scores: {A: 0.78, B: 0.85, C: 0.92, D: 0.81}
        │     gaps: [...]
        │     recommendations: [...]
        │   }
        │
        ├─► JSON Report
        ├─► HTML Report
        └─► Dashboard UI
```

---

## Component Interaction Diagram

```
User Interface Layer (Flask Hub - Port 8505)
        │
        ├─── GET /api/module3/dashboard
        │        │
        │        └──► Module3API.compute_complete_assessment()
        │                    │
        │                    ├──► BiasDetectionEngine.evaluate_fairness()
        │                    │        │
        │                    │        └──► compute_all_fairness_metrics()
        │                    │
        │                    ├──► GovernanceChecker.assess_governance()
        │                    │
        │                    ├──► FairnessMonitor.detect_fairness_drift()
        │                    │
        │                    └──► Module3Scorer.compute_module3_score()
        │                             │
        │                             ├─► _extract_critical_gaps()
        │                             ├─► _extract_major_gaps()
        │                             ├─► _extract_minor_gaps()
        │                             ├─► _determine_risk_level()
        │                             └─► _generate_summary()
        │
        ├─── GET /api/module3/monitoring
        │        │
        │        └──► FairnessMonitor.get_metric_history()
        │
        ├─── GET /api/module3/research
        │        │
        │        └──► ResearchTracker.get_recent_papers()
        │             ResearchTracker.get_recommended_practices()
        │
        └─── GET /api/module3/metrics
                 │
                 └──► Metric definitions from fairness_metrics.py
```

---

## Database Schema (In-Memory Repository)

```
FAIRNESS REPOSITORY PATTERN
│
├─ Current: FairnessDatabase (in-memory, transient)
│  └─ Stores: metrics, governance, drift events, research papers
│     Loss: Data cleared on process exit
│     Use: Development, testing, demonstrations
│
├─ Production: Migrate to SQLFairnessRepository
│  └─ Backend: PostgreSQL/MySQL (same as Module 1)
│     Tables: fairness_metric_snapshots, governance_assessments,
│              drift_events, research_papers_cache
│     Connection: Shared pool with Module 1 compliance repository
│     Persistence: Full ACID compliance, audit logging
│
└─ Interface: FairnessRepository (abstract)
   Provides unified methods regardless of backend
   No application code changes needed for migration

CURRENT SCHEMA (FairnessDatabase)
│
├─► metric_snapshots: List[FairnessMetricSnapshot]
│   Key: (system_id, timestamp)
│   Value: {
│       demographic_parity_gap, demographic_parity_scores,
│       tpr_gap, tpr_scores,
│       equalized_odds_gap, equalized_odds_scores,
│       ppv_gap, ppv_scores,
│       calibration_gap, calibration_scores,
│       subgroup_accuracy_ratio, subgroup_performance_scores,
│       category_a_score, critical_issues
│   }
│
├─► governance_assessments: List[GovernanceAssessment]
│   Key: (system_id, assessment_date)
│   Value: {
│       category_b_score (avg of items 7-10),
│       category_c_score (avg of items 11-14),
│       category_d_score (avg of items 15-16),
│       item_explanations
│   }
│
├─► drift_events: List[DriftEvent]
│   Key: (system_id, detection_timestamp)
│   Value: {
│       metric_name, baseline_value, current_value,
│       change, severity (NONE|MINOR|MAJOR),
│       test_type, p_value
│   }
│
└─► research_papers: List[ResearchPaper]
    Key: paper_id (title + year hash)
    Value: {
        title, authors, year, source, link,
        topics, abstract, fetched_at
    }

MIGRATION PATH
│
1. Create SQLAlchemy models matching dataclass structure
2. Create SQLFairnessRepository implementing FairnessRepository
3. Update initialization: repo = SQLFairnessRepository(engine)
4. Tests pass unchanged (interface identical)
5. Deploy with persistent backend
```

---

## Weight Distribution

```
MODULE 3 FINAL SCORE (100%)
│
├─ Category A: Algorithmic Fairness (40%)
│  │
│  └─ Average of 6 Metrics:
│     ├─ Demographic Parity (1/6)
│     ├─ Equal Opportunity (1/6)
│     ├─ Equalized Odds (1/6)
│     ├─ Predictive Parity (1/6)
│     ├─ Calibration (1/6)
│     └─ Subgroup Performance (1/6)
│
├─ Category B: Bias Detection & Mitigation (25%)
│  │
│  └─ Average of Items 7-10:
│     ├─ Training Data Bias Assessment (1/4)
│     ├─ Bias Mitigation Techniques (1/4)
│     ├─ Proxy Variable Analysis (1/4)
│     └─ Fairness-Accuracy Tradeoff (1/4)
│
├─ Category C: Ethical Governance & Oversight (20%)
│  │
│  └─ Average of Items 11-14:
│     ├─ Ethics Committee Approval (1/4)
│     ├─ Stakeholder Consultation (1/4)
│     ├─ Accountability Assignment (1/4)
│     └─ Incident Response Plan (1/4)
│
└─ Category D: Continuous Monitoring (15%)
   │
   └─ Average of Items 15-16:
      ├─ Fairness Drift Detection (1/2)
      └─ Subgroup Performance Tracking (1/2)
```

---

## Threshold & Severity Classification

```
METRIC GAP SCORING (6 metrics use identical thresholds)
│
├─ Gap < 0.05    ──────► Score: 1.0 (Excellent)
├─ Gap 0.05-0.10 ──────► Score: 0.7 (Good)
├─ Gap 0.10-0.15 ──────► Score: 0.5 (Acceptable)
└─ Gap > 0.15    ──────► Score: 0.2 (Poor)

SUBGROUP ACCURACY RATIO SCORING
│ Ratio = min(subgroup_accuracy) / max(subgroup_accuracy)
│
├─ Ratio >= 0.90     ──────► Score: 1.0 (Excellent parity)
├─ Ratio 0.85-0.89   ──────► Score: 0.7 (Good parity)
├─ Ratio 0.80-0.84   ──────► Score: 0.5 (Acceptable parity)
└─ Ratio < 0.80      ──────► Score: 0.2 (Poor parity)

DRIFT SEVERITY CLASSIFICATION (3-level, based on change magnitude)
│
├─ Change < 0.03     ──────► Severity: NONE (acceptable variation)
├─ Change 0.03-0.15  ──────► Severity: MINOR (requires monitoring)
└─ Change >= 0.15    ──────► Severity: MAJOR (requires intervention)
```

---

## Execution Flow

```
User Request
    │
    ├─► Main Dashboard (8501)
    │        │
    │        └─► Click "Module 3: Fairness & Ethics"
    │
    └─► Module 3 Hub (8505)
        │
        ├─ User selects tab or API endpoint
        │
        ├─► Dashboard Tab
        │   └─ API: /api/module3/dashboard
        │      │
        │      └─ Module3API.compute_complete_assessment()
        │         ├─ BiasDetectionEngine.evaluate_fairness()
        │         │  ├─ compute_all_fairness_metrics()
        │         │  ├─ _aggregate_scores()
        │         │  ├─ _extract_critical_issues()
        │         │  ├─ _identify_worst_performing_groups()
        │         │  └─ _identify_largest_gaps()
        │         │
        │         ├─ GovernanceChecker.assess_governance()
        │         │  ├─ _score_training_data_bias_assessment()
        │         │  ├─ _score_bias_mitigation_techniques()
        │         │  ├─ ... (all 10 items)
        │         │  └─ Aggregate B, C, D scores
        │         │
        │         └─ Module3Scorer.compute_module3_score()
        │            ├─ Weighted average (A:40%, B:25%, C:20%, D:15%)
        │            ├─ Gap classification
        │            ├─ Risk level determination
        │            └─ Summary generation
        │
        ├─► Assessment Tab
        │   └─ Display detailed metrics + gaps
        │
        ├─► Monitoring Tab
        │   └─ API: /api/module3/monitoring
        │      └─ FairnessMonitor.detect_fairness_drift()
        │         ├─ detect_fairness_drift() [delta-based]
        │         ├─ detect_statistical_drift() [t-test]
        │         ├─ detect_control_chart_drift() [control limits]
        │         └─ detect_moving_window_drift() [moving windows]
        │
        ├─► Research Tab
        │   └─ API: /api/module3/research
        │      └─ ResearchTracker.get_recent_papers()
        │         ResearchTracker.get_recommended_practices()
        │
        └─► API Tab
            └─ Display endpoint documentation
```

---

## Error Handling & Edge Cases

```
INPUT VALIDATION
├─ y_true/y_pred length mismatch
│  └─► ValueError with details
├─ Empty sensitive_features
│  └─► Graceful degradation (no demographic analysis)
├─ Small subgroups (< 10 samples)
│  └─► Flag as unreliable, high variance warning
├─ All same predictions
│  └─► FPR/TNR = undefined, handled as N/A
└─ Missing sensitive attributes
   └─► Compute what's available, skip missing

OUTPUT ROBUSTNESS
├─ Invalid governance inputs
│  └─► Default to 0.0 score, explain missing data
├─ Metric computation failure
│  └─► Return None with error explanation
├─ Drift detection on insufficient history
│  └─► Return "insufficient_data" status
└─ Database full
   └─► Flush old entries, continue operation
```

---

This architecture ensures:
- ✅ **Modularity**: Each component independent, testable
- ✅ **Extensibility**: Easy to add new metrics, detection methods
- ✅ **Robustness**: Graceful error handling
- ✅ **Scalability**: In-memory DB swappable with SQL backend
- ✅ **Integration**: Flask hub integrates with main dashboard
