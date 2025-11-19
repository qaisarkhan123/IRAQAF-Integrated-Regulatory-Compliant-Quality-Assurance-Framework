"""
PHASE 6: Impact Assessment Engine

Assesses compliance drift and impact of regulatory changes:
- Compares current system against previous assessment
- Identifies newly non-compliant areas
- Estimates remediation effort and cost
- Creates prioritized action plans

Part of IRAQAF Phase 6 - Change Monitoring System
Integrated with Phase 5 (Scoring Engine)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceStatus(str, Enum):
    """Compliance status for a requirement"""
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    UNKNOWN = "UNKNOWN"


class DriftType(str, Enum):
    """Type of compliance drift"""
    POSITIVE_DRIFT = "POSITIVE_DRIFT"      # Improved compliance
    NEGATIVE_DRIFT = "NEGATIVE_DRIFT"      # Degraded compliance
    NEW_GAP = "NEW_GAP"                    # New non-compliance
    RESOLVED_GAP = "RESOLVED_GAP"          # Gap fixed
    UNCHANGED = "UNCHANGED"                # No change


@dataclass
class ComplianceMetric:
    """Represents a compliance measurement"""
    requirement_id: str
    regulation: str
    previous_score: float
    current_score: float
    status_previous: ComplianceStatus
    status_current: ComplianceStatus
    evidence_count: int
    gap_description: Optional[str]
    remediation_hours: float
    remediation_cost: float


@dataclass
class ComplianceDrift:
    """Represents drift in a compliance metric"""
    metric: ComplianceMetric
    drift_type: DriftType
    drift_magnitude: float  # Change in score
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    affected_systems: List[str]
    remediation_priority: int  # 1=highest


@dataclass
class ImpactAssessmentResult:
    """Result of impact assessment"""
    assessment_date: datetime
    regulation: str
    system_id: str
    total_requirements: int
    compliant_count: int
    non_compliant_count: int
    partially_compliant_count: int
    previous_overall_score: float
    current_overall_score: float
    score_change: float
    drifts: List[ComplianceDrift]
    total_remediation_hours: float
    total_remediation_cost: float
    action_plan: List[Dict]
    risk_summary: str


class ImpactAssessor:
    """
    Assesses impact of regulatory changes on system compliance.
    Tracks compliance drift and generates remediation plans.
    """

    def __init__(self):
        """Initialize impact assessor"""
        self.assessment_history = []

    def assess_compliance_drift(
        self,
        regulation: str,
        system_id: str,
        previous_metrics: List[ComplianceMetric],
        current_metrics: List[ComplianceMetric]
    ) -> ImpactAssessmentResult:
        """
        Assess compliance drift between two assessment points.

        Args:
            regulation: Regulation being assessed
            system_id: System being assessed
            previous_metrics: Metrics from previous assessment
            current_metrics: Metrics from current assessment

        Returns:
            ImpactAssessmentResult with drift analysis
        """
        # Build metric lookup
        previous_lookup = {
            m.requirement_id: m for m in previous_metrics
        }
        current_lookup = {
            m.requirement_id: m for m in current_metrics
        }

        # Analyze drifts
        drifts = []
        for req_id, current_metric in current_lookup.items():
            if req_id in previous_lookup:
                previous_metric = previous_lookup[req_id]
                drift = self._analyze_drift(
                    previous_metric,
                    current_metric
                )
                if drift:
                    drifts.append(drift)

        # Detect new gaps
        for req_id, current_metric in current_lookup.items():
            if req_id not in previous_lookup:
                if current_metric.status_current == ComplianceStatus.NON_COMPLIANT:
                    drifts.append(
                        self._create_new_gap_drift(current_metric)
                    )

        # Sort by priority
        drifts.sort(key=lambda d: d.remediation_priority)

        # Calculate metrics
        compliant_count = sum(
            1 for m in current_metrics
            if m.status_current == ComplianceStatus.COMPLIANT
        )
        non_compliant_count = sum(
            1 for m in current_metrics
            if m.status_current == ComplianceStatus.NON_COMPLIANT
        )
        partially_compliant_count = sum(
            1 for m in current_metrics
            if m.status_current == ComplianceStatus.PARTIALLY_COMPLIANT
        )

        previous_overall = self._calculate_overall_score(previous_metrics)
        current_overall = self._calculate_overall_score(current_metrics)
        score_change = current_overall - previous_overall

        # Create action plan
        action_plan = self._create_action_plan(drifts)

        # Generate risk summary
        risk_summary = self._generate_risk_summary(drifts, score_change)

        # Calculate remediation totals
        total_remediation_hours = sum(d.metric.remediation_hours for d in drifts)
        total_remediation_cost = sum(d.metric.remediation_cost for d in drifts)

        return ImpactAssessmentResult(
            assessment_date=datetime.now(),
            regulation=regulation,
            system_id=system_id,
            total_requirements=len(current_metrics),
            compliant_count=compliant_count,
            non_compliant_count=non_compliant_count,
            partially_compliant_count=partially_compliant_count,
            previous_overall_score=previous_overall,
            current_overall_score=current_overall,
            score_change=score_change,
            drifts=drifts,
            total_remediation_hours=total_remediation_hours,
            total_remediation_cost=total_remediation_cost,
            action_plan=action_plan,
            risk_summary=risk_summary
        )

    def _analyze_drift(
        self,
        previous: ComplianceMetric,
        current: ComplianceMetric
    ) -> Optional[ComplianceDrift]:
        """Analyze drift between two metrics"""
        score_change = current.current_score - previous.previous_score

        # Determine drift type
        if current.status_current == ComplianceStatus.COMPLIANT:
            if previous.status_previous == ComplianceStatus.NON_COMPLIANT:
                drift_type = DriftType.RESOLVED_GAP
            else:
                drift_type = DriftType.UNCHANGED
        elif current.status_current == ComplianceStatus.NON_COMPLIANT:
            if previous.status_previous == ComplianceStatus.COMPLIANT:
                drift_type = DriftType.NEGATIVE_DRIFT
            else:
                drift_type = DriftType.UNCHANGED
        else:
            # Partially compliant
            if score_change > 5:
                drift_type = DriftType.POSITIVE_DRIFT
            elif score_change < -5:
                drift_type = DriftType.NEGATIVE_DRIFT
            else:
                drift_type = DriftType.UNCHANGED

        # Skip if no meaningful drift
        if drift_type == DriftType.UNCHANGED:
            return None

        # Determine risk level
        if abs(score_change) > 30:
            risk_level = "CRITICAL"
        elif abs(score_change) > 20:
            risk_level = "HIGH"
        elif abs(score_change) > 10:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Set priority (1 = highest)
        priority_map = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        priority = priority_map.get(risk_level, 5)

        return ComplianceDrift(
            metric=current,
            drift_type=drift_type,
            drift_magnitude=score_change,
            risk_level=risk_level,
            affected_systems=self._identify_affected_systems(current),
            remediation_priority=priority
        )

    def _create_new_gap_drift(
        self,
        metric: ComplianceMetric
    ) -> ComplianceDrift:
        """Create drift for newly detected non-compliant requirement"""
        return ComplianceDrift(
            metric=metric,
            drift_type=DriftType.NEW_GAP,
            drift_magnitude=-100,  # New non-compliance is worst case
            risk_level="CRITICAL",
            affected_systems=self._identify_affected_systems(metric),
            remediation_priority=1
        )

    def _calculate_overall_score(
        self,
        metrics: List[ComplianceMetric]
    ) -> float:
        """Calculate overall compliance score"""
        if not metrics:
            return 0.0

        total_score = sum(m.current_score for m in metrics)
        return (total_score / len(metrics)) / 100.0

    def _identify_affected_systems(self, metric: ComplianceMetric) -> List[str]:
        """Identify systems affected by this metric"""
        regulation_systems = {
            "EU AI Act": ["AI Models", "Data Pipeline", "Decision Systems"],
            "GDPR": ["Data Storage", "User Management", "Privacy Controls"],
            "ISO 13485": ["Device Software", "QA Process", "Documentation"],
            "IEC 62304": ["Medical Device", "Software Development", "Testing"],
            "FDA": ["FDA Compliance", "Regulatory", "Quality Systems"]
        }
        return regulation_systems.get(metric.regulation, ["General"])

    def _create_action_plan(
        self,
        drifts: List[ComplianceDrift]
    ) -> List[Dict]:
        """Create prioritized action plan from drifts"""
        action_plan = []

        for i, drift in enumerate(drifts, 1):
            action = {
                "priority": drift.remediation_priority,
                "requirement": drift.metric.requirement_id,
                "issue": drift.metric.gap_description or "Non-compliance detected",
                "current_status": drift.metric.status_current.value,
                "required_status": ComplianceStatus.COMPLIANT.value,
                "systems_affected": drift.affected_systems,
                "estimated_hours": drift.metric.remediation_hours,
                "estimated_cost": f"${drift.metric.remediation_cost:,.0f}",
                "risk_level": drift.risk_level,
                "recommended_actions": self._get_remediation_actions(drift),
                "timeline": self._estimate_timeline(
                    drift.metric.remediation_hours
                ),
                "owner": "Compliance Team"
            }
            action_plan.append(action)

        return action_plan

    def _get_remediation_actions(self, drift: ComplianceDrift) -> List[str]:
        """Get recommended remediation actions"""
        req_id = drift.metric.requirement_id
        regulation = drift.metric.regulation
        status = drift.metric.status_current

        actions = []

        # Generic actions for all non-compliant items
        if status == ComplianceStatus.NON_COMPLIANT:
            actions.append(f"Implement control: {req_id}")
            actions.append("Create implementation plan")
            actions.append("Assign resources and timeline")
            actions.append("Create test cases for verification")
            actions.append("Document implementation details")

        # Specific actions by regulation
        if regulation == "GDPR":
            actions.append("Review privacy impact assessment")
            actions.append("Update data protection documentation")
        elif regulation == "EU AI Act":
            actions.append("Review AI risk classification")
            actions.append("Update AI transparency documentation")
        elif regulation == "ISO 13485":
            actions.append("Update quality management system")
            actions.append("Add device traceability records")

        return actions

    def _estimate_timeline(self, hours: float) -> str:
        """Estimate timeline for remediation"""
        days = hours / 8  # 8-hour workday

        if days <= 1:
            return "1-2 days"
        elif days <= 5:
            return f"{int(days)} days"
        elif days <= 20:
            weeks = int(days / 5)
            return f"{weeks}-{weeks+1} weeks"
        else:
            weeks = int(days / 5)
            return f"{weeks}+ weeks"

    def _generate_risk_summary(
        self,
        drifts: List[ComplianceDrift],
        score_change: float
    ) -> str:
        """Generate human-readable risk summary"""
        critical_count = sum(1 for d in drifts if d.risk_level == "CRITICAL")
        high_count = sum(1 for d in drifts if d.risk_level == "HIGH")

        if critical_count > 0:
            return (
                f"⚠️  CRITICAL: {critical_count} critical gaps require "
                f"immediate attention. Overall compliance declined "
                f"by {abs(score_change):.1f}%"
            )
        elif high_count > 0:
            return (
                f"⚠️  HIGH PRIORITY: {high_count} high-severity gaps need "
                f"urgent remediation. Score change: {score_change:+.1f}%"
            )
        elif score_change < 0:
            return (
                f"⚠️  Compliance degraded by {abs(score_change):.1f}%. "
                f"Review and address identified gaps."
            )
        elif score_change > 0:
            return (
                f"✓ Compliance improved by {score_change:.1f}%. "
                f"Continue current initiatives."
            )
        else:
            return (
                "Compliance status unchanged. Continue monitoring."
            )

    def export_assessment_to_json(
        self,
        result: ImpactAssessmentResult
    ) -> str:
        """Export assessment result to JSON format"""
        result_dict = {
            'assessment_date': result.assessment_date.isoformat(),
            'regulation': result.regulation,
            'system_id': result.system_id,
            'total_requirements': result.total_requirements,
            'compliant_count': result.compliant_count,
            'non_compliant_count': result.non_compliant_count,
            'partially_compliant_count': result.partially_compliant_count,
            'previous_overall_score': f"{result.previous_overall_score:.2%}",
            'current_overall_score': f"{result.current_overall_score:.2%}",
            'score_change': f"{result.score_change:+.2%}",
            'total_remediation_hours': result.total_remediation_hours,
            'total_remediation_cost': f"${result.total_remediation_cost:,.0f}",
            'risk_summary': result.risk_summary,
            'action_plan': result.action_plan,
            'drifts': [
                {
                    'requirement_id': d.metric.requirement_id,
                    'drift_type': d.drift_type.value,
                    'risk_level': d.risk_level,
                    'drift_magnitude': f"{d.drift_magnitude:+.1f}%"
                }
                for d in result.drifts
            ]
        }

        return json.dumps(result_dict, indent=2)


# Example usage
if __name__ == "__main__":
    assessor = ImpactAssessor()

    # Sample previous metrics
    previous_metrics = [
        ComplianceMetric(
            requirement_id="GDPR-1",
            regulation="GDPR",
            previous_score=85.0,
            current_score=85.0,
            status_previous=ComplianceStatus.COMPLIANT,
            status_current=ComplianceStatus.COMPLIANT,
            evidence_count=5,
            gap_description=None,
            remediation_hours=0,
            remediation_cost=0
        ),
        ComplianceMetric(
            requirement_id="GDPR-2",
            regulation="GDPR",
            previous_score=60.0,
            current_score=45.0,
            status_previous=ComplianceStatus.PARTIALLY_COMPLIANT,
            status_current=ComplianceStatus.NON_COMPLIANT,
            evidence_count=2,
            gap_description="Right to erasure not fully implemented",
            remediation_hours=40,
            remediation_cost=6000
        ),
    ]

    current_metrics = [
        ComplianceMetric(
            requirement_id="GDPR-1",
            regulation="GDPR",
            previous_score=85.0,
            current_score=90.0,
            status_previous=ComplianceStatus.COMPLIANT,
            status_current=ComplianceStatus.COMPLIANT,
            evidence_count=6,
            gap_description=None,
            remediation_hours=0,
            remediation_cost=0
        ),
        ComplianceMetric(
            requirement_id="GDPR-2",
            regulation="GDPR",
            previous_score=60.0,
            current_score=35.0,
            status_previous=ComplianceStatus.PARTIALLY_COMPLIANT,
            status_current=ComplianceStatus.NON_COMPLIANT,
            evidence_count=1,
            gap_description="Right to erasure: No automated process, manual requests only",
            remediation_hours=60,
            remediation_cost=9000
        ),
        ComplianceMetric(
            requirement_id="GDPR-3",
            regulation="GDPR",
            previous_score=0.0,
            current_score=0.0,
            status_previous=ComplianceStatus.UNKNOWN,
            status_current=ComplianceStatus.NON_COMPLIANT,
            evidence_count=0,
            gap_description="Data breach notification - new requirement",
            remediation_hours=80,
            remediation_cost=12000
        )
    ]

    result = assessor.assess_compliance_drift(
        "GDPR",
        "acme-corp",
        previous_metrics,
        current_metrics
    )

    print("\n" + "="*70)
    print("IMPACT ASSESSMENT REPORT")
    print("="*70)
    print(f"\nRegulation: {result.regulation}")
    print(f"System: {result.system_id}")
    print(f"\nCompliance Status:")
    print(f"  Compliant: {result.compliant_count}/{result.total_requirements}")
    print(f"  Non-Compliant: {result.non_compliant_count}/{result.total_requirements}")
    print(f"  Partially Compliant: {result.partially_compliant_count}/{result.total_requirements}")
    print(f"\nScore Change: {result.score_change:+.1%}")
    print(f"Remediation Needed: {result.total_remediation_hours} hours (${result.total_remediation_cost:,.0f})")
    print(f"\n{result.risk_summary}")
    print("\n" + "="*70)
