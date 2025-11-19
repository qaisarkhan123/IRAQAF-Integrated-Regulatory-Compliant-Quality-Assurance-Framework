# Module 3: Fairness & Ethics - Specification Clarifications

This document provides detailed clarifications on the implementation to ensure alignment with the IRAQAF specification.

---

## 1. Threshold Definitions

### Subgroup Accuracy Ratio (Metric 6)

**Definition**: The ratio of minimum to maximum subgroup accuracy across all subgroups (including intersectional combinations).

```
Ratio = min_accuracy / max_accuracy across all subgroups
```

**Scoring Thresholds** (from IRAQAF spec):
- **Ratio ≥ 0.90** → Score **1.0** (excellent parity)
- **Ratio 0.85-0.89** → Score **0.7** (good parity)
- **Ratio 0.80-0.84** → Score **0.5** (acceptable parity)
- **Ratio < 0.80** → Score **0.2** (poor parity)

**Implementation**: See `fairness/metrics/fairness_metrics.py` lines 45-50
```python
SUBGROUP_ACCURACY_RATIO_THRESHOLDS = {
    0.90: 1.0,      # Ratio >= 0.90 → 1.0 (excellent parity)
    0.85: 0.7,      # Ratio 0.85-0.89 → 0.7 (good parity)
    0.80: 0.5,      # Ratio 0.80-0.84 → 0.5 (acceptable parity)
    0.0: 0.2        # Ratio < 0.80 → 0.2 (poor parity)
}
```

### Other Gap Metrics (Metrics 1-5)

All demographic parity, equal opportunity, equalized odds, predictive parity, and calibration use identical thresholds:
- **Gap < 0.05** → Score **1.0**
- **Gap 0.05-0.10** → Score **0.7**
- **Gap 0.10-0.15** → Score **0.5**
- **Gap > 0.15** → Score **0.2**

---

## 2. Drift Severity Classification (3-Level)

**IRAQAF specifies a 3-level drift severity system** based on absolute change in fairness metrics:

```
Level 1: NONE
  - Change < 0.03
  - Acceptable natural variation
  - No intervention required

Level 2: MINOR
  - Change 0.03 to 0.15
  - Requires monitoring and tracking
  - May need process adjustments

Level 3: MAJOR
  - Change >= 0.15
  - Requires immediate investigation
  - Model retraining typically necessary
```

**Implementation**: `fairness/monitoring/fairness_monitor.py`

The monitor uses 4 detection methods:
1. **Delta-based**: Direct change comparison
2. **Statistical (t-test)**: Two-window comparison with p-value
3. **Control charts**: Mean ± 2σ limits
4. **Moving windows**: Non-overlapping window analysis

**Note**: Earlier drafts used a 4-level system (none, minor, moderate, major). This has been corrected to the IRAQAF 3-level specification.

---

## 3. Governance Scoring Approach

### Component Structure

**Categories B, C, D** evaluate governance and ethics:
- **Category B (Bias Detection & Mitigation)**: Items 7-10 (4 items)
- **Category C (Ethical Governance & Oversight)**: Items 11-14 (4 items)
- **Category D (Continuous Monitoring)**: Items 15-16 (2 items)

### Scoring Methodology

**Item-level scoring**: Each item is scored on a 4-point scale:
- **0.0** = Not implemented / No documentation
- **0.5** = Partial implementation
- **0.7** = Substantial / Mostly complete
- **1.0** = Complete / Fully implemented

**Category scores**: **Simple arithmetic averages** of item scores
```
Category B Score = (Item7 + Item8 + Item9 + Item10) / 4
Category C Score = (Item11 + Item12 + Item13 + Item14) / 4
Category D Score = (Item15 + Item16) / 2
```

### Final Weighting

These category scores are then weighted in the **Module3Scorer**:

```
Module3_Score = 0.40×CategoryA + 0.25×CategoryB + 0.20×CategoryC + 0.15×CategoryD
```

Where:
- **CategoryA** = Average of 6 fairness metrics (40% weight)
- **CategoryB** = Average of items 7-10 (25% weight)
- **CategoryC** = Average of items 11-14 (20% weight)
- **CategoryD** = Average of items 15-16 (15% weight)

**Implementation**: `fairness/governance/governance_checker.py` and `fairness/api.py`

---

## 4. Database/Repository Pattern

### Current Implementation (Development)

**FairnessDatabase** is an in-memory implementation providing:
- Transient storage for metrics, governance, drift, research
- List-based storage with filtering methods
- Suitable for development, testing, demonstrations
- **Data loss on process exit**

### Production Architecture

**Production deployments MUST use a persistent SQL backend:**

```
Interface: FairnessRepository (abstract base class)
   ↓
Implementation: FairnessDatabase (in-memory, current)
   ↓
Target: SQLFairnessRepository (PostgreSQL/MySQL)
```

**Key requirements for production migration:**
1. Use the **same database connection pool** as Module 1's compliance repository
2. Implement with **SQLAlchemy ORM** for consistency
3. Include **audit logging** and data retention policies
4. Ensure **ACID compliance** and transaction isolation
5. Map dataclass fields directly to SQL tables

**Tables needed for production:**
- `fairness_metric_snapshots` - Historical metrics
- `governance_assessments` - Governance scores
- `drift_events` - Detected drift events
- `research_papers_cache` - Cached research database

**Migration path**: The interface is identical between implementations, so no application code changes are needed.

---

## 5. Research Tracker: Paper Refresh Mechanism

### Current Implementation (Static)

The tracker includes 10+ foundational papers embedded as a static list suitable for:
- Development and testing
- Demonstrations
- Initial deployments

### Production Enhancement (Dynamic)

For production environments, integrate automated refresh mechanisms:

**Paper sources:**
1. **ArXiv API**
   ```python
   query = "fairness AND (machine learning OR AI)"
   papers = arxiv_fetcher.fetch_recent(days=30)
   ```

2. **Hugging Face Hub**
   - Fairness models and datasets
   - Community discussions

3. **Papers with Code**
   - Implementation links
   - Benchmarks and evaluations

4. **Custom domain journals**
   - Healthcare AI journals
   - Financial services publications

**Refresh strategy:**
- **Development**: Static (current)
- **Production**: Hourly/daily scheduled refresh depending on use case
- **Caching**: Store in research_papers table (FairnessRepository)
- **Deduplication**: By title + year hash

**Best practices source:**
- Compiled from 50+ papers and practitioner experience
- Covers: metric selection, bias detection, mitigation, governance, monitoring, transparency
- Updated quarterly with emerging techniques

**Implementation location**: `fairness/research_tracker/research_tracker.py`

---

## 6. Category Weights Clarification

### Why 0.40 / 0.25 / 0.20 / 0.15?

These weights reflect the **relative importance** in the IRAQAF framework:

| Category | Weight | Items | Rationale |
|----------|--------|-------|-----------|
| **A: Algorithmic Fairness** | **40%** | 6 metrics | Core fairness evaluation; directly measurable |
| **B: Bias Detection** | **25%** | Items 7-10 | Prerequisite to mitigation; 4 key requirements |
| **C: Ethical Governance** | **20%** | Items 11-14 | Organizational/process; 4 key requirements |
| **D: Continuous Monitoring** | **15%** | Items 15-16 | Ongoing compliance; 2 key requirements |

Total = 100%

### Why Simple Averages?

- **Transparency**: Each item has equal voice within its category
- **Flexibility**: Missing items result in lower category scores (not hidden)
- **Auditability**: Simple math, easy to verify
- **Scalability**: Can add/remove items without recalibrating weights

---

## 7. Implementation Checklist

✅ **Thresholds Updated**
- Subgroup ratio: 0.90 / 0.85 / 0.80 confirmed
- Drift severity: 3-level (none / minor / major) implemented
- All 6 metrics: Identical 0.05 / 0.10 / 0.15 gap thresholds

✅ **Governance Clarified**
- Item scoring: 0.0 / 0.5 / 0.7 / 1.0 scale documented
- Category computation: Simple averages (4 items, 4 items, 2 items)
- Final scoring: 0.40 / 0.25 / 0.20 / 0.15 weights

✅ **Database Pattern Established**
- Repository interface defined
- In-memory implementation current
- Migration path to SQL documented
- Dataclass-to-ORM mapping ready

✅ **Research Tracker Documented**
- Static list for development
- Production refresh mechanism outlined
- Integration points identified (ArXiv, HF Hub, Papers with Code)

---

## 8. Files Updated

- `fairness/metrics/fairness_metrics.py` - Clarified threshold comments
- `fairness/models.py` - Added FairnessRepository base class, updated docstrings
- `fairness/monitoring/fairness_monitor.py` - Fixed to 3-level severity system
- `fairness/governance/governance_checker.py` - Enhanced docstring with scoring approach
- `fairness/research_tracker/research_tracker.py` - Added refresh mechanism documentation
- `fairness/api.py` - Clarified weight meanings and category definitions
- `fairness/ARCHITECTURE.md` - Updated threshold and severity tables
- `fairness/MODULE3_DOCUMENTATION.md` - Added governance scoring details, research refresh docs

---

## 9. Next Steps

### Immediate (For Handoff)
1. ✅ Review threshold implementations
2. ✅ Verify drift severity matches 3-level spec
3. ✅ Confirm governance simple averages
4. Run test suite: `pytest fairness/tests/test_module3.py -v`

### Short Term (Development)
1. Implement SQLFairnessRepository with SQLAlchemy
2. Add ArXiv API integration to ResearchTracker
3. Create migration guide (in-memory → SQL)
4. Add performance benchmarks

### Medium Term (Production)
1. Deploy with SQL backend
2. Enable automated research refresh
3. Add audit logging and retention policies
4. Integrate with Module 1 compliance repository

---

## 10. References

**IRAQAF Specification**: Original governance, metrics, and scoring definitions
**Implementation**: `fairness/` module with all components
**Documentation**: 
- `README.md` - Quick overview
- `QUICKSTART.md` - 5-minute guide
- `MODULE3_DOCUMENTATION.md` - Complete API reference
- `ARCHITECTURE.md` - System design and data flow
- This file - Clarifications and rationale
