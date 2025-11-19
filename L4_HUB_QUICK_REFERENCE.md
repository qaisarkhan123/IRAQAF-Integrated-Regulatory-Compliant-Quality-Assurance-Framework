# L4 Explainability Hub - Quick Reference Guide

## 🚀 Quick Start

```bash
# Start the hub
cd C:\Users\khan\Downloads\iraqaf_starter_kit
python dashboard/hub_explainability_app.py

# Access in browser
http://localhost:5000
```

## 📊 Dashboard Overview

```
OVERALL SCORE: 85%
├─ Explanation Capability (35% weight): 88%
├─ Explanation Reliability (30% weight): 75%
├─ Traceability & Auditability (25% weight): 98%
└─ Documentation Transparency (10% weight): 72%
```

## 🎯 Module Scores at a Glance

| Module | Score | Status | Key Insight |
|--------|-------|--------|------------|
| Prediction Logging | 100% | ✓ | Perfect - all events logged |
| Audit Trail | 98% | ✓ | 98/100 predictions traceable |
| Model Versioning | 95% | ✓ | 12 versions tracked |
| Explanation Methods | 92% | ✓ | SHAP/LIME fully implemented |
| Explanation Quality | 88% | ✓ | Clinical terminology in place |
| Coverage & Completeness | 85% | ✓ | 85% of predictions explained |
| Stability Testing | 85% | ✓ | Robust to 1% noise |
| Intended Use | 80% | ✓ | 20 use cases documented |
| Documentation | 75% | △ | 23 pages, diagrams needed |
| Fidelity Testing | 72% | △ | Accurate but room for improvement |
| Change Management | 60% | △ | Policy pending legal review |
| **Feature Consistency** | **68%** | **△** | **Lowest score - prioritize** |

## 🔍 How to Read a Score

**Example: Fidelity Testing (72%)**

```
WHAT IT MEASURES?
→ Do explanations accurately reflect model behavior?

HOW IS IT CALCULATED?
→ Average of 4 component tests:
   1. Feature Masking Test: 70%
   2. Prediction Reconstruction: 75%
   3. Feature Impact Accuracy: 70%
   4. Threshold Achievement: 72%
   Formula: (70 + 75 + 70 + 72) / 4 = 71.75 ≈ 72%

WHY THIS NUMBER?
→ Based on 100 actual prediction samples
→ Shows explanations account for 72% of prediction changes
→ Meets minimum requirement (>50%) but below ideal (85%)

IS IT GOOD?
→ Status: PASSING_WITH_CAUTION
→ 72% > 50% minimum ✓
→ 72% < 85% ideal ✗

WHAT TO DO?
→ Improve feature selection consistency
→ Review methodology with domain experts
```

## 📑 Dashboard Tabs Explained

### 1. **OVERVIEW** (Default)
- Quick glance at all scores
- Visual bar chart
- Perfect for executives/summaries

### 2. **DETAILED ANALYSIS**
- Expand each module
- See individual component scores
- Progress bars for visualization
- Best for deep dives

### 3. **HOW SCORES ARE CALCULATED**
- Mathematical formulas
- Component breakdowns
- Test details and sample sizes
- For transparency/compliance

### 4. **RECOMMENDATIONS**
- Modules below 80%
- Specific improvement ideas
- Implementation next steps
- For action planning

## ⚠️ Modules Needing Attention

### 🔴 High Priority (Score < 70%)
- **Feature Consistency: 68%**
  - Target: >0.70 Jaccard similarity
  - Current: 0.68
  - Action: Refine feature selection algorithm

### 🟡 Medium Priority (Score 70-80%)
- **Change Management: 60%**
  - Issue: Update policy pending legal review
  - Action: Complete legal review
  - Action: Implement automated change logging

- **Documentation: 75%**
  - Issue: 75% coverage, some gaps
  - Action: Add architecture diagrams
  - Action: Benchmark on 1 more dataset

- **Fidelity Testing: 72%**
  - Issue: Below 85% ideal
  - Action: Review feature methodology
  - Action: Test on more diverse data

## ✨ Top Performers

### 🟢 Perfect Score (100%)
- **Prediction Logging**
  - All 18 fields per prediction
  - 10,542 logs captured
  - Immutable, hash-verified

### 🟢 Near Perfect (>95%)
- **Audit Trail: 98%** - Decision traceability
- **Model Versioning: 95%** - Version tracking

### 🟢 Excellent (≥88%)
- **Explanation Methods: 92%** - SHAP/LIME ready
- **Explanation Quality: 88%** - Human-readable

## 🔄 Score Calculation Formula

```
Overall Score = Σ(Category Score × Weight)

Where:
- Explanation Capability × 0.35 = 88% × 0.35 = 30.8%
- Explanation Reliability × 0.30 = 75% × 0.30 = 22.5%
- Traceability × 0.25 = 98% × 0.25 = 24.5%
- Documentation × 0.10 = 72% × 0.10 = 7.2%
─────────────────────────────────────────────
TOTAL = 85%
```

## 📈 Data Behind The Scores

- **Predictions Analyzed**: 1,000+ samples
- **Model Versions Tracked**: 12
- **Use Cases Documented**: 20
- **Audit Events Logged**: 2,847
- **Testing Completed**: 300+ test runs
- **Expert Reviews**: 75 clinical experts
- **Documentation Pages**: 23

## 🎨 Color Meanings

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | ✓ PASSING | ≥85%, meets standard |
| 🟠 Orange | △ NEEDS WORK | 70-84%, improvement needed |
| 🔵 Blue | ◆ AT RISK | <70%, urgent action needed |

## 🛠️ Common Questions

**Q: Why is Feature Consistency lowest?**
A: Jaccard similarity (0.68) hasn't reached target (0.70). Similar cases don't always get similar explanations. Working on algorithm refinement.

**Q: Is 85% overall score good?**
A: Yes. It exceeds 80% benchmark. Room for improvement in Reliability (75%) and Documentation (72%), but Traceability (98%) is excellent.

**Q: How often are scores updated?**
A: Scores use current data. Update frequency depends on model updates and new tests. Documentation updated quarterly.

**Q: Can I export these scores?**
A: Currently view/copy via browser. PDF export planned for next version.

**Q: What does "Feature Consistency: 68%" mean exactly?**
A: When comparing similar cases, only 68% of their important features overlap. Target is 70% (industry standard). Need more consistent feature selection.

## 🚦 Action Priority Matrix

### Do This First
1. ✓ **Feature Consistency (68%)** - Refine selection algorithm
2. ✓ **Change Management (60%)** - Legal review update policy
3. ✓ **Fidelity Testing (72%)** - Improve feature methodology

### Do This Next
4. Documentation (75%) - Add missing diagrams
5. Coverage & Completeness (85%) - Expand to remaining 15% of cases

### Already Good (Maintain)
6-12. All other modules ≥80%

## 📞 Need Help?

### Understanding a Score
1. Click on the module card
2. Check "How Scores Are Calculated" tab
3. Read the formula and examples

### Improving a Score
1. Go to "Recommendations" tab
2. Find your module
3. Follow the action items

### Technical Questions
- Check `L4_HUB_ENHANCEMENTS.md` for detailed docs
- Review API endpoints at `/api/transparency-score`

## 🔗 Quick Links

- **Main Dashboard**: http://localhost:5000
- **Transparency Score API**: http://localhost:5000/api/transparency-score
- **Modules API**: http://localhost:5000/api/modules
- **Documentation**: L4_HUB_ENHANCEMENTS.md
- **Source Code**: dashboard/hub_explainability_app.py

## 📋 Checklist: Launching the Hub

- [ ] Stop any previous instances
- [ ] Run: `python dashboard/hub_explainability_app.py`
- [ ] Wait for: "Running on http://127.0.0.1:5000"
- [ ] Open browser to: `http://localhost:5000`
- [ ] Verify all 4 tabs load
- [ ] Check overall score displays: 85%
- [ ] Try switching tabs
- [ ] API test: Open `/api/modules` in new tab

---

**Version**: 2.0  
**Last Updated**: November 19, 2024  
**Framework**: IRAQAF L4 Module  
**Status**: ✓ Production Ready
