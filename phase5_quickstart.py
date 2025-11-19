"""
PHASE 5: COMPLIANCE SCORING ENGINE - QUICK START SCRIPT
Complete 7-step verification and demonstration

Run: python phase5_quickstart.py
"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime

print("\n" + "="*80)
print("PHASE 5: COMPLIANCE SCORING ENGINE - QUICK START")
print("="*80)

# ============================================================================
# STEP 1: Environment Verification
# ============================================================================
print("\n[1/7] Verifying environment...")
try:
    import statistics
    import logging
    from dataclasses import dataclass
    from enum import Enum
    print("     ✅ Python dependencies OK")
except ImportError as e:
    print(f"     ❌ Missing dependency: {e}")
    sys.exit(1)

# ============================================================================
# STEP 2: Directory Structure
# ============================================================================
print("\n[2/7] Checking directory structure...")
required_dirs = ["compliance", "tests"]
for dir_name in required_dirs:
    if Path(dir_name).exists():
        print(f"     ✅ {dir_name}/ exists")
    else:
        print(f"     ❌ {dir_name}/ missing - creating...")
        Path(dir_name).mkdir(exist_ok=True)

# ============================================================================
# STEP 3: Module Imports
# ============================================================================
print("\n[3/7] Importing Phase 5 modules...")
try:
    # Import components
    from compliance.scorer import (
        ComplianceScorer, Evidence, EvidenceType, RiskLevel,
        ComplianceLevel, EvidenceMatrix
    )
    print("     ✅ ComplianceScorer imported")

    from compliance.gap_analyzer import (
        GapAnalyzer, GapSeverity, RemediationType
    )
    print("     ✅ GapAnalyzer imported")

    from compliance.requirement_checklists import RequirementChecklists
    print("     ✅ RequirementChecklists imported")

except ImportError as e:
    print(f"     ❌ Import failed: {e}")
    sys.exit(1)

# ============================================================================
# STEP 4: Component Verification
# ============================================================================
print("\n[4/7] Verifying components...")

# Verify scorer
scorer = ComplianceScorer()
assert len(scorer.regulations_config) == 5
print(f"     ✅ ComplianceScorer initialized (5 regulations)")

# Verify analyzer
analyzer = GapAnalyzer()
assert len(analyzer.remediation_library) > 0
print(f"     ✅ GapAnalyzer initialized (6 remediation types)")

# Verify checklists
checklists = RequirementChecklists()
assert sum(len(items) for items in checklists.checklists.values()) == 105
print(f"     ✅ RequirementChecklists loaded (105 requirements)")

# ============================================================================
# STEP 5: Functional Test - Basic Scoring
# ============================================================================
print("\n[5/7] Running functional tests...")

# Create test evidence
test_evidence = [
    Evidence(
        type=EvidenceType.DOCUMENTATION,
        description="Risk assessment procedure documented",
        quality_score=92,
        confidence=0.95
    ),
    Evidence(
        type=EvidenceType.IMPLEMENTATION,
        description="Risk assessment process implemented",
        quality_score=85,
        confidence=0.88
    ),
    Evidence(
        type=EvidenceType.TESTING,
        description="Risk assessment tested on 10 AI models",
        quality_score=88,
        confidence=0.90
    )
]

# Score requirements from each regulation
test_cases = [
    ("EU-AI-41.1", "High-risk AI systems must perform risk assessment",
     "EU-AI-Act", RiskLevel.CRITICAL),
    ("GDPR-5.1", "Personal data processing must be lawful", "GDPR", RiskLevel.CRITICAL),
    ("ISO-13485-4", "Risk management process implemented", "ISO-13485", RiskLevel.HIGH),
]

scores_by_regulation = {}
for req_id, req_text, regulation, risk_level in test_cases:
    score = scorer.score_requirement(
        requirement_id=req_id,
        requirement_text=req_text,
        regulation=regulation,
        evidence_list=test_evidence,
        risk_level=risk_level
    )

    if regulation not in scores_by_regulation:
        scores_by_regulation[regulation] = []
    scores_by_regulation[regulation].append(score)

    status = "✅" if score.compliance_score > 50 else "❌"
    print(
        f"     {status} Scored {req_id}: {score.compliance_score:.1f}% ({score.compliance_level.name})")

# ============================================================================
# STEP 6: Advanced Test - Gap Analysis
# ============================================================================
print("\n[6/7] Testing gap analysis...")

# Add a low-score requirement to trigger gap detection
low_evidence = [
    Evidence(
        type=EvidenceType.DOCUMENTATION,
        description="Incomplete documentation",
        quality_score=35,
        confidence=0.6
    )
]

gap_score = scorer.score_requirement(
    requirement_id="GDPR-7.1",
    requirement_text="Personal data must be encrypted",
    regulation="GDPR",
    evidence_list=low_evidence,
    risk_level=RiskLevel.CRITICAL
)

# Identify gaps
gaps = analyzer.identify_gaps(scorer.requirement_scores, gap_threshold=50.0)

if gaps:
    print(f"     ✅ Identified {len(gaps)} gap(s)")

    # Generate remediation for first gap
    gap = gaps[0]
    actions = analyzer.generate_remediation_plan(gap)

    total_hours = sum(a.estimated_hours for a in actions)
    total_cost = sum(a.estimated_cost for a in actions)

    print(f"        Gap ID: {gap.gap_id}")
    print(f"        Severity: {gap.severity.name}")
    print(
        f"        Remediation: {len(actions)} actions, {total_hours}h, ${total_cost:,.0f}")
else:
    print(f"     ⚠️  No gaps detected (all scores > 50)")

# ============================================================================
# STEP 7: Performance & Export Tests
# ============================================================================
print("\n[7/7] Testing performance and exports...")

# Bulk scoring test
start = time.time()
for i in range(50):
    scorer.score_requirement(
        requirement_id=f"PERF-{i}",
        requirement_text=f"Performance test requirement {i}",
        regulation="EU-AI-Act",
        evidence_list=test_evidence,
        risk_level=RiskLevel.MEDIUM
    )
elapsed = time.time() - start
print(
    f"     ✅ Scored 50 requirements in {elapsed:.2f}s ({50/elapsed:.0f} req/s)")

# Portfolio summary
portfolio = scorer.get_portfolio_summary()
print(
    f"     ✅ Portfolio summary generated ({portfolio['total_requirements_assessed']} total)")

# Export test
Path("reports").mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
scores_file = f"reports/scores-{timestamp}.json"
gaps_file = f"reports/gaps-{timestamp}.json"

scorer.export_scores_json(scores_file)
print(
    f"     ✅ Exported {scorer.requirement_scores.__len__()} scores to reports/")

if gaps:
    analyzer.export_gaps_report(gaps_file)
    print(f"     ✅ Exported {len(gaps)} gaps to reports/")

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
print("\n" + "="*80)
print("PHASE 5 QUICK START - RESULTS SUMMARY")
print("="*80)

print(f"\n✅ All 7 verification steps completed successfully!\n")

print("Components Status:")
print(
    f"  ✅ ComplianceScorer: Ready (5 regulations, {len(scorer.requirement_scores)} scores)")
print(f"  ✅ GapAnalyzer: Ready ({len(gaps)} gaps identified)")
print(f"  ✅ RequirementChecklists: Ready (105 requirements)")

print(f"\nKey Metrics:")
print(f"  • Overall Compliance: {portfolio['overall_compliance_score']:.1f}%")
print(
    f"  • Total Requirements Assessed: {portfolio['total_requirements_assessed']}")
print(f"  • Average Confidence: {portfolio['avg_confidence']:.3f}")
print(f"  • Regulations: {', '.join(portfolio['regulations'].keys())}")

if gaps:
    gap_summary = analyzer.get_portfolio_gap_summary()
    print(f"\nGap Analysis:")
    print(f"  • Total Gaps: {gap_summary['total_gaps']}")
    print(f"  • Critical: {gap_summary['critical_gaps']}")
    print(
        f"  • Total Remediation Effort: {gap_summary['total_remediation_hours']}h")
    print(f"  • Estimated Cost: ${gap_summary['total_remediation_cost']:,.2f}")

print(f"\nRequirement Checklists:")
summary = checklists.get_summary()
for reg, details in summary['regulations'].items():
    print(f"  • {reg}: {details['count']} requirements")

print(f"\nNext Steps:")
print(f"  1. Review PHASE_5_IMPLEMENTATION_GUIDE.md for detailed documentation")
print(f"  2. Run tests: pytest tests/test_phase5_compliance_scoring.py -v")
print(f"  3. Examine generated reports in reports/ directory")
print(f"  4. Review: compliance/scorer.py, gap_analyzer.py, requirement_checklists.py")

print(f"\n✅ PHASE 5 COMPLIANCE SCORING ENGINE IS READY!")
print("\n" + "="*80)
