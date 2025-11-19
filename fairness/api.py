"""
Module 3 Score Aggregator and API
Combines all components into Module 3 fairness score
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import Module3Score, get_fairness_db
from .bias_engine.bias_detection_engine import FairnessReport
from .governance.governance_checker import GovernanceReport
from .monitoring.fairness_monitor import DriftReport


# Module 3 Scoring Weights (IRAQAF Specification)
# Final score = 0.40*A + 0.25*B + 0.20*C + 0.15*D
CATEGORY_WEIGHTS = {
    'category_a': 0.40,  # Algorithmic Fairness Metrics (6 metrics)
    'category_b': 0.25,  # Bias Detection & Mitigation (4 items: 7-10)
    'category_c': 0.20,  # Ethical Governance & Oversight (4 items: 11-14)
    'category_d': 0.15   # Continuous Fairness Monitoring (2 items: 15-16)
}


class Module3Scorer:
    """
    Aggregates fairness metrics, governance, and monitoring into a comprehensive Module 3 score
    """

    def compute_module3_score(self,
                              fairness_report: FairnessReport,
                              governance_report: GovernanceReport,
                              drift_report: Optional[DriftReport] = None,
                              system_id: str = "default_system") -> Module3Score:
        """
        Compute the overall Module 3 (Fairness & Ethics) score.

        Args:
            fairness_report: FairnessReport from bias detection engine
            governance_report: GovernanceReport from governance checker
            drift_report: Optional DriftReport from monitoring
            system_id: System identifier

        Returns:
            Module3Score with all category scores and overall assessment
        """

        # Extract scores from reports
        category_a_score = fairness_report.category_a_score
        category_b_score = governance_report.category_b_score
        category_c_score = governance_report.category_c_score
        category_d_score = governance_report.category_d_score

        # Compute weighted overall score
        overall_score = (
            category_a_score * CATEGORY_WEIGHTS['category_a'] +
            category_b_score * CATEGORY_WEIGHTS['category_b'] +
            category_c_score * CATEGORY_WEIGHTS['category_c'] +
            category_d_score * CATEGORY_WEIGHTS['category_d']
        )

        # Categorize gaps
        critical_gaps = self._extract_critical_gaps(
            fairness_report, governance_report, drift_report
        )
        major_gaps = self._extract_major_gaps(
            fairness_report, governance_report, drift_report
        )
        minor_gaps = self._extract_minor_gaps(
            fairness_report, governance_report, drift_report
        )

        # Determine risk level
        risk_level = self._determine_risk_level(
            category_a_score, category_b_score, category_c_score, category_d_score,
            len(critical_gaps)
        )

        # Generate summary
        summary = self._generate_summary(
            overall_score, risk_level, critical_gaps, major_gaps, minor_gaps
        )

        timestamp = datetime.utcnow().isoformat() + "Z"

        return Module3Score(
            system_id=system_id,
            timestamp=timestamp,
            category_a_score=category_a_score,
            category_b_score=category_b_score,
            category_c_score=category_c_score,
            category_d_score=category_d_score,
            overall_score=overall_score,
            critical_gaps=critical_gaps,
            major_gaps=major_gaps,
            minor_gaps=minor_gaps,
            risk_level=risk_level,
            summary=summary,
            metrics_detail=fairness_report.to_dict(),
            governance_detail=governance_report.to_dict(),
            drift_detail=drift_report.to_dict() if drift_report else None
        )

    def _extract_critical_gaps(self, fairness_report: FairnessReport,
                               governance_report: GovernanceReport,
                               drift_report: Optional[DriftReport]) -> List[Dict[str, str]]:
        """
        Extract critical gaps (scores < 0.2 or critical issues).
        """
        gaps = []

        # From fairness report
        for issue in fairness_report.critical_issues:
            if issue.get('severity') == 'critical':
                gaps.append({
                    'issue': f"{issue.get('type', 'Fairness Issue')}: {issue.get('description', '')}",
                    'category': 'Algorithmic Fairness',
                    'recommendation': self._get_fairness_recommendation(issue.get('type', ''))
                })

        # From governance report
        for item, score in [
            ('ethics_committee_approval', governance_report.ethics_committee_approval),
            ('accountability_assignment', governance_report.accountability_assignment),
        ]:
            if score < 0.2:
                gaps.append({
                    'issue': f"Critical governance gap: {item.replace('_', ' ')}",
                    'category': 'Governance',
                    'recommendation': f"Immediately address {item} requirements"
                })

        # From drift report
        if drift_report and drift_report.drift_detected:
            for drift in drift_report.detected_drifts:
                if drift['severity'] == 'major':
                    gaps.append({
                        'issue': f"Major fairness drift in {drift['metric']}: {drift['change_pct']:.2f}% change",
                        'category': 'Monitoring',
                        'recommendation': f"Investigate and retrain if drift continues"
                    })

        return gaps[:5]  # Top 5 critical gaps

    def _extract_major_gaps(self, fairness_report: FairnessReport,
                            governance_report: GovernanceReport,
                            drift_report: Optional[DriftReport]) -> List[Dict[str, str]]:
        """
        Extract major gaps (0.2-0.5 score range).
        """
        gaps = []

        # From fairness report
        for issue in fairness_report.critical_issues:
            if issue.get('severity') == 'high':
                gaps.append({
                    'issue': f"{issue.get('type', 'Fairness Issue')}: {issue.get('description', '')}",
                    'category': 'Algorithmic Fairness',
                    'recommendation': self._get_fairness_recommendation(issue.get('type', ''))
                })

        # From governance report
        for item, score in [
            ('training_data_bias_assessment',
             governance_report.training_data_bias_assessment),
            ('bias_mitigation_techniques',
             governance_report.bias_mitigation_techniques),
            ('proxy_variable_analysis', governance_report.proxy_variable_analysis),
            ('fairness_accuracy_tradeoff',
             governance_report.fairness_accuracy_tradeoff),
        ]:
            if 0.2 <= score < 0.7:
                gaps.append({
                    'issue': f"Gap in: {item.replace('_', ' ')}",
                    'category': 'Bias Detection & Mitigation',
                    'recommendation': f"Strengthen documentation and analysis of {item}"
                })

        # From drift report
        if drift_report and drift_report.detected_drifts:
            for drift in drift_report.detected_drifts:
                if drift['severity'] == 'moderate':
                    gaps.append({
                        'issue': f"Moderate fairness drift in {drift['metric']}: {drift['change_pct']:.2f}% change",
                        'category': 'Monitoring',
                        'recommendation': 'Monitor closely and prepare for retraining'
                    })

        return gaps[:5]  # Top 5 major gaps

    def _extract_minor_gaps(self, fairness_report: FairnessReport,
                            governance_report: GovernanceReport,
                            drift_report: Optional[DriftReport]) -> List[Dict[str, str]]:
        """
        Extract minor gaps (0.5-0.8 score range).
        """
        gaps = []

        # From governance report
        for item, score in [
            ('stakeholder_consultation', governance_report.stakeholder_consultation),
            ('fairness_drift_detection', governance_report.fairness_drift_detection),
            ('subgroup_performance_tracking',
             governance_report.subgroup_performance_tracking),
        ]:
            if 0.5 <= score < 0.8:
                gaps.append({
                    'issue': f"Minor gap: {item.replace('_', ' ')}",
                    'category': 'Governance & Monitoring',
                    'recommendation': f"Consider enhancing {item}"
                })

        # From drift report
        if drift_report and drift_report.detected_drifts:
            for drift in drift_report.detected_drifts:
                if drift['severity'] == 'minor':
                    gaps.append({
                        'issue': f"Minor drift in {drift['metric']}: {drift['change_pct']:.2f}% change",
                        'category': 'Monitoring',
                        'recommendation': 'Continue monitoring'
                    })

        return gaps[:5]  # Top 5 minor gaps

    def _determine_risk_level(self, cat_a: float, cat_b: float, cat_c: float, cat_d: float,
                              critical_count: int) -> str:
        """Determine overall risk level"""
        if critical_count > 2 or cat_a < 0.3 or cat_c < 0.3:
            return "High"
        elif critical_count > 0 or cat_a < 0.5 or cat_b < 0.5:
            return "Medium"
        elif cat_a < 0.7 or cat_b < 0.7 or cat_c < 0.7:
            return "Medium"
        else:
            return "Low"

    def _get_fairness_recommendation(self, issue_type: str) -> str:
        """Get recommendation for specific fairness issue"""
        recommendations = {
            'Demographic Parity Violation': 'Adjust model decision thresholds per group or apply bias mitigation techniques',
            'Equal Opportunity Violation': 'Improve model performance on true positives for underperforming groups',
            'Equalized Odds Violation': 'Balance both TPR and FPR across protected groups',
            'Subgroup Performance': 'Increase data collection for underperforming subgroups and apply group-specific tuning',
            'Predictive Parity': 'Ensure precision is consistent across demographic groups'
        }
        return recommendations.get(issue_type, 'Apply fairness-aware mitigation techniques')

    def _generate_summary(self, overall_score: float, risk_level: str,
                          critical_gaps: List[Dict],
                          major_gaps: List[Dict],
                          minor_gaps: List[Dict]) -> str:
        """Generate executive summary"""

        score_desc = "Excellent" if overall_score >= 0.8 else \
            "Good" if overall_score >= 0.6 else \
            "Fair" if overall_score >= 0.4 else \
            "Poor"

        summary = f"Module 3 Fairness & Ethics Assessment: {score_desc} ({overall_score:.1%}) fairness score with {risk_level} risk. "

        if critical_gaps:
            summary += f"{len(critical_gaps)} critical issue(s) require immediate attention. "
        if major_gaps:
            summary += f"{len(major_gaps)} major gap(s) need remediation. "
        if minor_gaps:
            summary += f"{len(minor_gaps)} minor improvement(s) recommended."

        return summary


class Module3API:
    """
    API interface for Module 3 Fairness & Ethics
    """

    def __init__(self):
        self.scorer = Module3Scorer()
        self.db = get_fairness_db()

    def compute_complete_assessment(self,
                                    fairness_report: FairnessReport,
                                    governance_report: GovernanceReport,
                                    drift_report: Optional[DriftReport] = None,
                                    system_id: str = "default_system") -> Dict[str, Any]:
        """
        Compute complete Module 3 assessment and return as JSON-serializable dict.
        """
        module3_score = self.scorer.compute_module3_score(
            fairness_report, governance_report, drift_report, system_id
        )

        # Store in database
        self.db.store_metric_snapshot(fairness_report.fairness_metrics)
        self.db.store_governance_assessment(governance_report)
        if drift_report:
            # Convert drift events to storage format if needed
            pass

        return {
            'module': 'IRAQAF_MODULE_3_FAIRNESS',
            'system_id': system_id,
            'timestamp': module3_score.timestamp,
            'overall_score': module3_score.overall_score,
            'overall_score_pct': f"{module3_score.overall_score:.1%}",
            'risk_level': module3_score.risk_level,
            'summary': module3_score.summary,
            'category_scores': {
                'algorithmic_fairness': module3_score.category_a_score,
                'bias_detection_mitigation': module3_score.category_b_score,
                'ethical_governance': module3_score.category_c_score,
                'continuous_monitoring': module3_score.category_d_score
            },
            'critical_gaps': module3_score.critical_gaps,
            'major_gaps': module3_score.major_gaps,
            'minor_gaps': module3_score.minor_gaps,
            'metrics_detail': module3_score.metrics_detail,
            'governance_detail': module3_score.governance_detail,
            'drift_detail': module3_score.drift_detail
        }

    def generate_json_report(self, assessment: Dict[str, Any]) -> str:
        """Generate JSON report"""
        return json.dumps(assessment, indent=2)

    def generate_html_report(self, assessment: Dict[str, Any]) -> str:
        """Generate HTML report for visualization"""
        html = f"""
        <html>
        <head>
            <title>IRAQAF Module 3 - Fairness & Ethics Assessment</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 20px; border-radius: 5px; }}
                .score-box {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ display: inline-block; margin: 10px; }}
                .score-value {{ font-size: 32px; font-weight: bold; }}
                .risk-high {{ color: #e53e3e; }}
                .risk-medium {{ color: #dd6b20; }}
                .risk-low {{ color: #38a169; }}
                .gap-list {{ list-style: none; padding: 0; }}
                .gap-item {{ background: #fff5f5; padding: 10px; margin: 5px 0; border-left: 4px solid #e53e3e; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ IRAQAF Module 3: Fairness & Ethics Assessment</h1>
                <p>System: {assessment['system_id']}</p>
                <p>Generated: {assessment['timestamp']}</p>
            </div>
            
            <div class="score-box">
                <h2>Overall Assessment</h2>
                <div class="metric">
                    <div class="score-value">{assessment['overall_score']:.1%}</div>
                    <div>Module 3 Score</div>
                </div>
                <div class="metric">
                    <div class="score-value risk-{assessment['risk_level'].lower()}">
                        {assessment['risk_level']}
                    </div>
                    <div>Risk Level</div>
                </div>
                <p><strong>Summary:</strong> {assessment['summary']}</p>
            </div>
            
            <div class="score-box">
                <h2>Category Scores</h2>
                <ul>
                    <li><strong>Algorithmic Fairness (40%):</strong> {assessment['category_scores']['algorithmic_fairness']:.1%}</li>
                    <li><strong>Bias Detection & Mitigation (25%):</strong> {assessment['category_scores']['bias_detection_mitigation']:.1%}</li>
                    <li><strong>Ethical Governance (20%):</strong> {assessment['category_scores']['ethical_governance']:.1%}</li>
                    <li><strong>Continuous Monitoring (15%):</strong> {assessment['category_scores']['continuous_monitoring']:.1%}</li>
                </ul>
            </div>
            
            <div class="score-box">
                <h2>Critical Gaps ({len(assessment['critical_gaps'])})</h2>
                <ul class="gap-list">
        """

        for gap in assessment['critical_gaps']:
            html += f"""
                    <li class="gap-item">
                        <strong>{gap.get('issue', 'Issue')}</strong><br/>
                        <em>{gap.get('recommendation', 'No recommendation')}</em>
                    </li>
            """

        html += """
                </ul>
            </div>
            
            <div class="score-box">
                <h2>Major Gaps ({count})</h2>
                <ul class="gap-list">
        """.replace("{count}", str(len(assessment['major_gaps'])))

        for gap in assessment['major_gaps']:
            html += f"""
                    <li class="gap-item" style="border-color: #dd6b20; background: #fffaf0;">
                        <strong>{gap.get('issue', 'Issue')}</strong><br/>
                        <em>{gap.get('recommendation', 'No recommendation')}</em>
                    </li>
            """

        html += """
                </ul>
            </div>
        </body>
        </html>
        """

        return html
