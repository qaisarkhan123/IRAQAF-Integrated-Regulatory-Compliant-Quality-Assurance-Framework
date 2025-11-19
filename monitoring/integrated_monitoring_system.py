"""
PHASE 6: Integrated Monitoring System

Orchestrates all monitoring components:
- Change detection
- Impact assessment
- Notification system
- Compliance drift tracking
- Real-time monitoring dashboard integration

Part of IRAQAF Phase 6 - Change Monitoring System (Weeks 9-10, 70 hours)
Integrates with all prior phases for full system compliance monitoring
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from monitoring.change_detector import ChangeDetector, ChangeDetectionResult
from monitoring.impact_assessor import ImpactAssessor, ImpactAssessmentResult
from monitoring.notification_manager import (
    NotificationManager,
    NotificationPriority,
    NotificationStatus
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MonitoringReport:
    """Complete monitoring report combining all components"""
    report_id: str
    report_date: datetime
    monitoring_period_start: datetime
    monitoring_period_end: datetime

    # Change detection
    total_changes: int
    critical_changes: int
    high_changes: int
    medium_changes: int
    low_changes: int

    # Impact assessment
    regulations_affected: List[str]
    systems_affected: List[str]
    overall_compliance_score: float
    score_change_percent: float

    # Notifications
    notifications_sent: int
    notifications_delivered: int
    critical_alerts: int

    # Remediation
    total_remediation_hours: float
    total_remediation_cost: float
    top_priority_actions: List[Dict]

    # Status
    monitoring_status: str
    next_monitoring_run: datetime
    summary: str


class IntegratedMonitoringSystem:
    """
    Integrated monitoring system combining change detection,
    impact assessment, and notifications.

    This is the core of Phase 6 and integrates all prior phases:
    - Phase 2 (Database) for regulatory content
    - Phase 4 (NLP) for semantic analysis
    - Phase 5 (Scoring) for compliance scoring
    """

    def __init__(self, monitoring_interval_hours: int = 24):
        """
        Initialize integrated monitoring system.

        Args:
            monitoring_interval_hours: Hours between monitoring runs (default 24)
        """
        self.detector = ChangeDetector()
        self.assessor = ImpactAssessor()
        self.notification_manager = NotificationManager()
        self.monitoring_interval = timedelta(hours=monitoring_interval_hours)
        self.monitoring_history = []
        self.last_monitoring_run = None

    def execute_monitoring_cycle(
        self,
        system_id: str,
        previous_state: Dict[str, Dict[str, str]],
        current_state: Dict[str, Dict[str, str]],
        previous_compliance_scores: Dict[str, float],
        current_compliance_scores: Dict[str, float],
        recipients: List[str]
    ) -> MonitoringReport:
        """
        Execute complete monitoring cycle.

        Args:
            system_id: System being monitored
            previous_state: Previous regulatory requirements by regulation
            current_state: Current regulatory requirements by regulation
            previous_compliance_scores: Previous compliance scores
            current_compliance_scores: Current compliance scores
            recipients: Notification recipients

        Returns:
            Complete monitoring report
        """
        logger.info("="*70)
        logger.info("STARTING PHASE 6 INTEGRATED MONITORING CYCLE")
        logger.info("="*70)

        report_id = f"RPT-{datetime.now().timestamp()}"
        all_changes = []
        all_drifts = []
        all_notifications = []

        # Step 1: Detect changes in all regulations
        logger.info("\n[STEP 1] Detecting regulatory changes...")
        for regulation in current_state:
            logger.info(f"  • Scanning {regulation}...")

            prev_reqs = previous_state.get(regulation, {})
            curr_reqs = current_state[regulation]

            detection_result = self.detector.analyze_changes(
                regulation,
                prev_reqs,
                curr_reqs
            )

            all_changes.extend(detection_result.changes)

            logger.info(f"    Found {detection_result.total_changes} changes")
            if detection_result.critical_changes > 0:
                logger.warning(
                    f"    ⚠️  {detection_result.critical_changes} CRITICAL changes!"
                )

        # Step 2: Assess compliance drift
        logger.info("\n[STEP 2] Assessing compliance drift...")
        regulations_affected = set()
        systems_affected = set()
        total_remediation_hours = 0
        total_remediation_cost = 0

        for regulation in current_state:
            logger.info(f"  • Analyzing {regulation}...")

            # Build compliance metrics from scores
            prev_scores = previous_compliance_scores.get(regulation, {})
            curr_scores = current_compliance_scores.get(regulation, {})

            # Create compliance metrics (simplified for demo)
            prev_metrics = [
                self._create_compliance_metric(
                    req_id, regulation, score, score
                )
                for req_id, score in prev_scores.items()
            ]

            curr_metrics = [
                self._create_compliance_metric(
                    req_id, regulation, prev_scores.get(req_id, 0), score
                )
                for req_id, score in curr_scores.items()
            ]

            assessment = self.assessor.assess_compliance_drift(
                regulation,
                system_id,
                prev_metrics,
                curr_metrics
            )

            all_drifts.extend(assessment.drifts)
            regulations_affected.add(regulation)
            systems_affected.update(
                set(system for systems in
                    [d.affected_systems for d in assessment.drifts]
                    for system in systems)
            )

            total_remediation_hours += assessment.total_remediation_hours
            total_remediation_cost += assessment.total_remediation_cost

            logger.info(
                f"    Compliance: {assessment.current_overall_score:.1%}")
            logger.info(f"    Change: {assessment.score_change:+.1%}")
            logger.info(f"    Drifts detected: {len(assessment.drifts)}")

        # Step 3: Create and send notifications
        logger.info("\n[STEP 3] Creating notifications...")

        for change in all_changes:
            notifications = self.notification_manager.create_change_notification(
                change_id=change.change_id,
                change_type=change.change_type.value,
                severity=change.severity.value,
                regulation=change.regulation,
                requirement_id=change.requirement_id,
                affected_systems=change.affected_systems,
                description=change.description,
                recipients=recipients
            )
            all_notifications.extend(notifications)

        # Send notifications
        send_results = self.notification_manager.send_notifications(
            all_notifications
        )

        logger.info(f"  Notifications created: {len(all_notifications)}")
        logger.info(f"  • Sent: {send_results['sent']}")
        logger.info(f"  • Delivered: {send_results['delivered']}")
        logger.info(f"  • Failed: {send_results['failed']}")

        # Step 4: Generate priority actions
        logger.info("\n[STEP 4] Generating action plan...")

        top_priority_actions = self._extract_top_actions(
            all_drifts,
            max_actions=5
        )

        logger.info(f"  Top priority actions: {len(top_priority_actions)}")
        for i, action in enumerate(top_priority_actions, 1):
            logger.info(
                f"    {i}. {action['requirement']} - "
                f"${action['estimated_cost']}"
            )

        # Step 5: Generate monitoring report
        logger.info("\n[STEP 5] Generating monitoring report...")

        # Calculate overall compliance
        all_current_scores = []
        for regulation_scores in current_compliance_scores.values():
            all_current_scores.extend(regulation_scores.values())

        overall_score = (
            sum(all_current_scores) / len(all_current_scores) / 100
            if all_current_scores else 0
        )

        # Calculate score change
        all_previous_scores = []
        for regulation_scores in previous_compliance_scores.values():
            all_previous_scores.extend(regulation_scores.values())

        prev_overall_score = (
            sum(all_previous_scores) / len(all_previous_scores) / 100
            if all_previous_scores else 0
        )

        score_change = (overall_score - prev_overall_score) * 100

        # Generate summary
        summary = self._generate_monitoring_summary(
            len(all_changes),
            len(all_drifts),
            len(all_notifications),
            overall_score,
            score_change
        )

        # Create report
        report = MonitoringReport(
            report_id=report_id,
            report_date=datetime.now(),
            monitoring_period_start=self.last_monitoring_run or datetime.now() -
            self.monitoring_interval,
            monitoring_period_end=datetime.now(),

            total_changes=len(all_changes),
            critical_changes=sum(
                1 for c in all_changes if c.severity.value == "CRITICAL"),
            high_changes=sum(
                1 for c in all_changes if c.severity.value == "HIGH"),
            medium_changes=sum(
                1 for c in all_changes if c.severity.value == "MEDIUM"),
            low_changes=sum(
                1 for c in all_changes if c.severity.value == "LOW"),

            regulations_affected=list(regulations_affected),
            systems_affected=list(systems_affected),
            overall_compliance_score=overall_score,
            score_change_percent=score_change,

            notifications_sent=send_results['sent'],
            notifications_delivered=send_results['delivered'],
            critical_alerts=sum(
                1 for n in all_notifications if n.priority == NotificationPriority.CRITICAL),

            total_remediation_hours=total_remediation_hours,
            total_remediation_cost=total_remediation_cost,
            top_priority_actions=top_priority_actions,

            monitoring_status="COMPLETE",
            next_monitoring_run=datetime.now() + self.monitoring_interval,
            summary=summary
        )

        self.monitoring_history.append(report)
        self.last_monitoring_run = datetime.now()

        logger.info("\n" + "="*70)
        logger.info("MONITORING CYCLE COMPLETE")
        logger.info("="*70)

        return report

    def _create_compliance_metric(
        self,
        requirement_id: str,
        regulation: str,
        previous_score: float,
        current_score: float
    ):
        """Create a compliance metric from scores"""
        from monitoring.impact_assessor import (
            ComplianceMetric, ComplianceStatus
        )

        # Determine status from score
        if current_score >= 80:
            status = ComplianceStatus.COMPLIANT
        elif current_score >= 50:
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT

        prev_status = (
            ComplianceStatus.COMPLIANT if previous_score >= 80
            else ComplianceStatus.PARTIALLY_COMPLIANT if previous_score >= 50
            else ComplianceStatus.NON_COMPLIANT
        )

        return ComplianceMetric(
            requirement_id=requirement_id,
            regulation=regulation,
            previous_score=previous_score,
            current_score=current_score,
            status_previous=prev_status,
            status_current=status,
            evidence_count=int(current_score / 10),
            gap_description=None if status == ComplianceStatus.COMPLIANT else "Gap detected",
            remediation_hours=40 if status == ComplianceStatus.NON_COMPLIANT else 0,
            remediation_cost=6000 if status == ComplianceStatus.NON_COMPLIANT else 0
        )

    def _extract_top_actions(
        self,
        drifts: List,
        max_actions: int = 5
    ) -> List[Dict]:
        """Extract top priority actions from drifts"""
        actions = []

        for drift in drifts[:max_actions]:
            action = {
                "priority": drift.remediation_priority,
                "requirement": drift.metric.requirement_id,
                "issue": drift.metric.gap_description or "Non-compliance",
                "estimated_hours": drift.metric.remediation_hours,
                "estimated_cost": f"${drift.metric.remediation_cost:,.0f}",
                "risk_level": drift.risk_level,
                "systems": ", ".join(drift.affected_systems)
            }
            actions.append(action)

        return actions

    def _generate_monitoring_summary(
        self,
        total_changes: int,
        total_drifts: int,
        total_notifications: int,
        overall_score: float,
        score_change: float
    ) -> str:
        """Generate monitoring cycle summary"""
        summary_parts = [
            "═"*70,
            "MONITORING CYCLE SUMMARY",
            "═"*70,
            "",
            f"📊 Regulatory Changes: {total_changes} detected",
            f"📉 Compliance Drifts: {total_drifts} identified",
            f"🔔 Notifications: {total_notifications} sent",
            "",
            f"Compliance Score: {overall_score:.1%}",
            f"Score Change: {score_change:+.1%}",
        ]

        if score_change > 5:
            summary_parts.append("✓ Compliance improving")
        elif score_change < -5:
            summary_parts.append("⚠️  Compliance declining")
        else:
            summary_parts.append("→ Compliance stable")

        return "\n".join(summary_parts)

    def export_report_to_json(self, report: MonitoringReport) -> str:
        """Export monitoring report to JSON"""
        report_dict = asdict(report)
        report_dict['report_date'] = report.report_date.isoformat()
        report_dict['monitoring_period_start'] = report.monitoring_period_start.isoformat()
        report_dict['monitoring_period_end'] = report.monitoring_period_end.isoformat()
        report_dict['next_monitoring_run'] = report.next_monitoring_run.isoformat()
        report_dict['overall_compliance_score'] = f"{report.overall_compliance_score:.1%}"

        return json.dumps(report_dict, indent=2)

    def get_monitoring_history(
        self,
        days: int = 30
    ) -> List[MonitoringReport]:
        """Get monitoring history"""
        cutoff_date = datetime.now() - timedelta(days=days)

        history = [
            r for r in self.monitoring_history
            if r.report_date >= cutoff_date
        ]

        return sorted(history, key=lambda r: r.report_date, reverse=True)


# Example usage and demo
if __name__ == "__main__":
    system = IntegratedMonitoringSystem(monitoring_interval_hours=24)

    # Sample previous state
    previous_state = {
        "GDPR": {
            "GDPR-1": "Organizations must implement data protection measures",
            "GDPR-2": "Data subjects have the right to be forgotten",
            "GDPR-3": "DPA must be notified within 72 hours of breach"
        },
        "EU AI Act": {
            "AI-1": "AI systems must be transparent",
            "AI-2": "High-risk AI requires human oversight"
        }
    }

    # Sample current state (with changes)
    current_state = {
        "GDPR": {
            "GDPR-1": "Organizations must implement advanced data protection measures",
            "GDPR-2": "Data subjects have the right to be forgotten",
            "GDPR-4": "Organizations must conduct DPIA for high-risk processing",
            "GDPR-5": "Annual compliance audits are now mandatory"
        },
        "EU AI Act": {
            "AI-1": "AI systems must be fully transparent and explainable",
            "AI-2": "High-risk AI requires real-time human oversight",
            "AI-3": "All AI training data must be documented"
        }
    }

    # Sample compliance scores (before)
    previous_scores = {
        "GDPR": {"GDPR-1": 85, "GDPR-2": 60, "GDPR-3": 75},
        "EU AI Act": {"AI-1": 70, "AI-2": 80}
    }

    # Sample compliance scores (after)
    current_scores = {
        "GDPR": {"GDPR-1": 90, "GDPR-2": 45, "GDPR-4": 30, "GDPR-5": 20},
        "EU AI Act": {"AI-1": 85, "AI-2": 75, "AI-3": 40}
    }

    # Execute monitoring cycle
    report = system.execute_monitoring_cycle(
        system_id="acme-corp",
        previous_state=previous_state,
        current_state=current_state,
        previous_compliance_scores=previous_scores,
        current_compliance_scores=current_scores,
        recipients=["compliance@acme.com", "ciso@acme.com"]
    )

    # Display report
    print("\n" + report.summary)
    print(f"\n💾 Report saved: {report.report_id}")
    print(
        f"📅 Period: {report.monitoring_period_start.date()} to {report.monitoring_period_end.date()}")
    print(
        f"🎯 Next run: {report.next_monitoring_run.strftime('%Y-%m-%d %H:%M')}")
