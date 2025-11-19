"""
Ethical Governance Checker
Evaluates governance and ethics documentation requirements
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GovernanceReport:
    """Governance assessment report"""
    system_id: str
    timestamp: str

    # Category B scores
    training_data_bias_assessment: float
    bias_mitigation_techniques: float
    proxy_variable_analysis: float
    fairness_accuracy_tradeoff: float
    category_b_score: float
    category_b_findings: List[str]

    # Category C scores
    ethics_committee_approval: float
    stakeholder_consultation: float
    accountability_assignment: float
    incident_response_plan: float
    category_c_score: float
    category_c_findings: List[str]

    # Category D scores
    fairness_drift_detection: float
    subgroup_performance_tracking: float
    category_d_score: float
    category_d_findings: List[str]

    # Explanations per item
    item_explanations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'system_id': self.system_id,
            'timestamp': self.timestamp,
            'category_b': {
                'training_data_bias_assessment': self.training_data_bias_assessment,
                'bias_mitigation_techniques': self.bias_mitigation_techniques,
                'proxy_variable_analysis': self.proxy_variable_analysis,
                'fairness_accuracy_tradeoff': self.fairness_accuracy_tradeoff,
                'score': self.category_b_score,
                'findings': self.category_b_findings
            },
            'category_c': {
                'ethics_committee_approval': self.ethics_committee_approval,
                'stakeholder_consultation': self.stakeholder_consultation,
                'accountability_assignment': self.accountability_assignment,
                'incident_response_plan': self.incident_response_plan,
                'score': self.category_c_score,
                'findings': self.category_c_findings
            },
            'category_d': {
                'fairness_drift_detection': self.fairness_drift_detection,
                'subgroup_performance_tracking': self.subgroup_performance_tracking,
                'score': self.category_d_score,
                'findings': self.category_d_findings
            },
            'item_explanations': self.item_explanations
        }


class GovernanceChecker:
    """
    Evaluates governance and ethics requirements (Categories B, C, D)

    SCORING APPROACH:
    Each governance item (7-16) is scored 0.0 (not implemented), 0.5 (partial),
    0.7 (substantial), or 1.0 (complete). Category scores are simple arithmetic
    averages of item scores:

    - Category B (Bias Detection): avg(items 7-10)
    - Category C (Ethical Governance): avg(items 11-14)
    - Category D (Continuous Monitoring): avg(items 15-16)

    These category scores are then used in Module3Scorer with weights:
    Final = 0.40*CategoryA + 0.25*CategoryB + 0.20*CategoryC + 0.15*CategoryD
    """

    def assess_governance(self, governance_inputs: Dict[str, Any], system_id: str = "default_system") -> GovernanceReport:
        """
        Assess governance compliance.

        Args:
            governance_inputs: Dict with governance assessment data, e.g.:
                {
                    'training_data_bias_assessment': {
                        'present': bool,
                        'documented': bool,
                        'includes_analysis': bool
                    },
                    'ethics_committee_approval': {
                        'approved': bool,
                        'date': str,
                        'documentation': bool
                    },
                    # ... etc
                }
            system_id: System identifier

        Returns:
            GovernanceReport with all scores and findings
        """

        timestamp = datetime.utcnow().isoformat() + "Z"
        explanations = {}

        # ===== CATEGORY B: Bias Detection & Mitigation =====

        # Item 7: Training Data Bias Assessment
        training_bias_score, training_bias_exp = self._score_training_data_bias(
            governance_inputs.get('training_data_bias_assessment', {})
        )
        explanations['training_data_bias_assessment'] = training_bias_exp

        # Item 8: Bias Mitigation Techniques Applied
        mitigation_score, mitigation_exp = self._score_bias_mitigation_techniques(
            governance_inputs.get('bias_mitigation_techniques', {})
        )
        explanations['bias_mitigation_techniques'] = mitigation_exp

        # Item 9: Proxy Variable Analysis
        proxy_score, proxy_exp = self._score_proxy_variable_analysis(
            governance_inputs.get('proxy_variable_analysis', {})
        )
        explanations['proxy_variable_analysis'] = proxy_exp

        # Item 10: Fairness-Accuracy Trade-off Documentation
        tradeoff_score, tradeoff_exp = self._score_fairness_accuracy_tradeoff(
            governance_inputs.get('fairness_accuracy_tradeoff', {})
        )
        explanations['fairness_accuracy_tradeoff'] = tradeoff_exp

        category_b_score = (
            training_bias_score + mitigation_score + proxy_score + tradeoff_score) / 4.0
        category_b_findings = [training_bias_exp,
                               mitigation_exp, proxy_exp, tradeoff_exp]

        # ===== CATEGORY C: Ethical Governance & Oversight =====

        # Item 11: Ethics Committee Approval
        ethics_approval_score, ethics_approval_exp = self._score_ethics_committee_approval(
            governance_inputs.get('ethics_committee_approval', {})
        )
        explanations['ethics_committee_approval'] = ethics_approval_exp

        # Item 12: Stakeholder Consultation
        stakeholder_score, stakeholder_exp = self._score_stakeholder_consultation(
            governance_inputs.get('stakeholder_consultation', {})
        )
        explanations['stakeholder_consultation'] = stakeholder_exp

        # Item 13: Accountability & Responsibility Assignment
        accountability_score, accountability_exp = self._score_accountability_assignment(
            governance_inputs.get('accountability_assignment', {})
        )
        explanations['accountability_assignment'] = accountability_exp

        # Item 14: Fairness Incident Response Plan
        incident_response_score, incident_response_exp = self._score_incident_response_plan(
            governance_inputs.get('incident_response_plan', {})
        )
        explanations['incident_response_plan'] = incident_response_exp

        category_c_score = (ethics_approval_score + stakeholder_score +
                            accountability_score + incident_response_score) / 4.0
        category_c_findings = [
            ethics_approval_exp, stakeholder_exp, accountability_exp, incident_response_exp]

        # ===== CATEGORY D: Continuous Fairness Monitoring =====

        # Item 15: Fairness Drift Detection (design & documentation)
        drift_detection_score, drift_detection_exp = self._score_fairness_drift_detection(
            governance_inputs.get('fairness_drift_detection', {})
        )
        explanations['fairness_drift_detection'] = drift_detection_exp

        # Item 16: Subgroup Performance Tracking (design & documentation)
        subgroup_tracking_score, subgroup_tracking_exp = self._score_subgroup_performance_tracking(
            governance_inputs.get('subgroup_performance_tracking', {})
        )
        explanations['subgroup_performance_tracking'] = subgroup_tracking_exp

        category_d_score = (drift_detection_score +
                            subgroup_tracking_score) / 2.0
        category_d_findings = [drift_detection_exp, subgroup_tracking_exp]

        return GovernanceReport(
            system_id=system_id,
            timestamp=timestamp,
            training_data_bias_assessment=training_bias_score,
            bias_mitigation_techniques=mitigation_score,
            proxy_variable_analysis=proxy_score,
            fairness_accuracy_tradeoff=tradeoff_score,
            category_b_score=category_b_score,
            category_b_findings=category_b_findings,
            ethics_committee_approval=ethics_approval_score,
            stakeholder_consultation=stakeholder_score,
            accountability_assignment=accountability_score,
            incident_response_plan=incident_response_score,
            category_c_score=category_c_score,
            category_c_findings=category_c_findings,
            fairness_drift_detection=drift_detection_score,
            subgroup_performance_tracking=subgroup_tracking_score,
            category_d_score=category_d_score,
            category_d_findings=category_d_findings,
            item_explanations=explanations
        )

    # ===== CATEGORY B SCORERS =====

    def _score_training_data_bias_assessment(self, data: Dict) -> tuple:
        """
        Item 7: Training Data Bias Assessment
        1.0: Comprehensive bias analysis documented (demographic distribution, historical bias)
        0.6: Demographics documented but no bias analysis
        0.5: Minimal documentation
        0.0: No documentation
        """
        if not data:
            return 0.0, "No training data bias assessment documentation provided"

        has_comprehensive = data.get('comprehensive_bias_analysis', False)
        has_demographics = data.get('demographic_distribution', False)
        has_historical = data.get('historical_bias_checked', False)
        has_any_doc = data.get('documented', False)

        if has_comprehensive and has_demographics and has_historical:
            return 1.0, "Comprehensive training data bias assessment documented"
        elif has_demographics and has_historical:
            return 1.0, "Training data demographics and historical bias documented"
        elif has_demographics:
            return 0.6, "Demographics documented but limited bias analysis"
        elif has_any_doc:
            return 0.5, "Minimal training data documentation provided"
        else:
            return 0.0, "No training data bias assessment documented"

    def _score_bias_mitigation_techniques(self, data: Dict) -> tuple:
        """
        Item 8: Bias Mitigation Techniques Applied
        1.0: Multiple mitigation techniques applied and evaluated
        0.6: One or more mitigation techniques applied with limited evaluation
        0.5: Mitigation techniques mentioned but not evaluated
        0.0: No mitigation techniques documented
        """
        if not data:
            return 0.0, "No bias mitigation techniques documented"

        techniques = data.get('techniques', [])
        evaluated = data.get('evaluated', False)
        multiple = len(techniques) > 1 if isinstance(
            techniques, list) else False
        mentioned = data.get('mentioned', False)

        if multiple and evaluated:
            return 1.0, f"Multiple mitigation techniques applied and evaluated: {techniques}"
        elif techniques and evaluated:
            return 1.0, f"Bias mitigation techniques applied and evaluated: {techniques}"
        elif techniques and mentioned:
            return 0.5, f"Bias mitigation techniques mentioned: {techniques}, but not formally evaluated"
        elif mentioned:
            return 0.5, "Bias mitigation mentioned but not detailed"
        else:
            return 0.0, "No bias mitigation techniques documented"

    def _score_proxy_variable_analysis(self, data: Dict) -> tuple:
        """
        Item 9: Proxy Variable Analysis
        1.0: Proxy variables identified and mitigation plan documented
        0.6: Proxy variables identified but mitigation incomplete
        0.5: Proxy variables mentioned but not systematically analyzed
        0.0: No proxy variable analysis
        """
        if not data:
            return 0.0, "No proxy variable analysis documented"

        identified = data.get('proxy_variables_identified', False)
        mitigation_plan = data.get('mitigation_plan_documented', False)
        systematic = data.get('systematic_analysis', False)
        mentioned = data.get('mentioned', False)

        if identified and mitigation_plan:
            return 1.0, f"Proxy variables identified and mitigation plan documented: {data.get('details', '')}"
        elif identified and systematic:
            return 1.0, "Proxy variables systematically analyzed with documented findings"
        elif identified:
            return 0.6, "Proxy variables identified but mitigation incomplete"
        elif mentioned:
            return 0.5, "Proxy variables mentioned but not systematically analyzed"
        else:
            return 0.0, "No proxy variable analysis documented"

    def _score_fairness_accuracy_tradeoff(self, data: Dict) -> tuple:
        """
        Item 10: Fairness-Accuracy Trade-off Documentation
        1.0: Trade-offs explicitly documented with rationale and stakeholder input
        0.6: Trade-offs mentioned with some rationale
        0.5: Trade-offs acknowledged but minimal documentation
        0.0: No documentation of trade-offs
        """
        if not data:
            return 0.0, "No fairness-accuracy trade-off documentation"

        explicit = data.get('explicitly_documented', False)
        with_rationale = data.get('with_rationale', False)
        stakeholder_input = data.get('stakeholder_input', False)
        mentioned = data.get('mentioned', False)
        acknowledged = data.get('acknowledged', False)

        if explicit and with_rationale and stakeholder_input:
            return 1.0, "Fairness-accuracy trade-offs explicitly documented with rationale and stakeholder input"
        elif explicit and with_rationale:
            return 1.0, "Fairness-accuracy trade-offs documented with clear rationale"
        elif mentioned and with_rationale:
            return 0.6, "Trade-offs mentioned with some rationale"
        elif acknowledged:
            return 0.5, "Trade-offs acknowledged but minimal documentation"
        else:
            return 0.0, "No fairness-accuracy trade-off documentation"

    # ===== CATEGORY C SCORERS =====

    def _score_ethics_committee_approval(self, data: Dict) -> tuple:
        """
        Item 11: Ethics Committee Approval
        1.0: Ethics committee approval obtained and documented
        0.6: Ethics review conducted with minor documentation gaps
        0.5: Ethics review mentioned but not formally documented
        0.0: No ethics committee involvement
        """
        if not data:
            return 0.0, "No ethics committee approval documentation"

        approved = data.get('approved', False)
        documented = data.get('documented', False)
        reviewed = data.get('reviewed', False)
        mentioned = data.get('mentioned', False)
        approval_date = data.get('approval_date')

        if approved and documented:
            return 1.0, f"Ethics committee approval obtained and documented (approved: {approval_date})"
        elif reviewed and documented:
            return 1.0, "Ethics committee review conducted and documented"
        elif reviewed:
            return 0.6, "Ethics review conducted with some documentation"
        elif mentioned:
            return 0.5, "Ethics review mentioned but not formally documented"
        else:
            return 0.0, "No ethics committee involvement documented"

    def _score_stakeholder_consultation(self, data: Dict) -> tuple:
        """
        Item 12: Stakeholder Consultation
        1.0: Comprehensive stakeholder consultation documented with feedback incorporated
        0.6: Stakeholder consultation conducted with limited documentation
        0.5: Consultation mentioned but minimal evidence
        0.0: No stakeholder consultation
        """
        if not data:
            return 0.0, "No stakeholder consultation documented"

        comprehensive = data.get('comprehensive', False)
        feedback_incorporated = data.get('feedback_incorporated', False)
        documented = data.get('documented', False)
        conducted = data.get('conducted', False)
        mentioned = data.get('mentioned', False)
        stakeholders = data.get('stakeholder_groups', [])

        if comprehensive and feedback_incorporated:
            return 1.0, f"Comprehensive stakeholder consultation documented with feedback incorporated from: {stakeholders}"
        elif conducted and documented:
            return 1.0, "Stakeholder consultation conducted and documented"
        elif conducted:
            return 0.6, "Stakeholder consultation conducted with limited documentation"
        elif mentioned:
            return 0.5, "Stakeholder consultation mentioned but minimal evidence"
        else:
            return 0.0, "No stakeholder consultation documented"

    def _score_accountability_assignment(self, data: Dict) -> tuple:
        """
        Item 13: Accountability & Responsibility Assignment
        1.0: Clear accountability structure with named roles and review procedures
        0.6: Accountability structure defined but incomplete
        0.5: Accountability mentioned but vague
        0.0: No accountability structure
        """
        if not data:
            return 0.0, "No accountability structure documented"

        clear = data.get('clear', False)
        named_roles = data.get('named_roles', False)
        review_procedures = data.get('review_procedures', False)
        defined = data.get('defined', False)
        mentioned = data.get('mentioned', False)
        roles = data.get('roles', [])

        if clear and named_roles and review_procedures:
            return 1.0, f"Clear accountability structure with named roles and review procedures: {roles}"
        elif clear and named_roles:
            return 1.0, f"Accountability structure clearly defined with named roles: {roles}"
        elif defined:
            return 0.6, "Accountability structure defined but may be incomplete"
        elif mentioned:
            return 0.5, "Accountability mentioned but lacks clarity"
        else:
            return 0.0, "No accountability structure documented"

    def _score_incident_response_plan(self, data: Dict) -> tuple:
        """
        Item 14: Fairness Incident Response Plan
        1.0: Comprehensive plan documented with procedures, escalation path, and remediation
        0.6: Plan exists but missing some components
        0.5: Plan mentioned but not detailed
        0.0: No plan documented
        """
        if not data:
            return 0.0, "No fairness incident response plan documented"

        comprehensive = data.get('comprehensive', False)
        has_procedures = data.get('procedures_documented', False)
        has_escalation = data.get('escalation_path', False)
        has_remediation = data.get('remediation_steps', False)
        exists = data.get('exists', False)
        mentioned = data.get('mentioned', False)

        if comprehensive and has_procedures and has_escalation and has_remediation:
            return 1.0, "Comprehensive fairness incident response plan with procedures, escalation, and remediation"
        elif has_procedures and has_escalation:
            return 1.0, "Incident response plan documented with procedures and escalation path"
        elif exists:
            return 0.6, "Fairness incident response plan exists but missing some components"
        elif mentioned:
            return 0.5, "Fairness incident response plan mentioned but not detailed"
        else:
            return 0.0, "No fairness incident response plan documented"

    # ===== CATEGORY D SCORERS =====

    def _score_fairness_drift_detection(self, data: Dict) -> tuple:
        """
        Item 15: Fairness Drift Detection (design & documentation)
        1.0: Comprehensive drift detection system designed and documented
        0.6: Drift detection approach documented but implementation incomplete
        0.5: Drift detection mentioned but not detailed
        0.0: No drift detection documentation
        """
        if not data:
            return 0.0, "No fairness drift detection system documented"

        comprehensive = data.get('comprehensive', False)
        designed = data.get('designed', False)
        documented = data.get('documented', False)
        implemented = data.get('implemented', False)
        mentioned = data.get('mentioned', False)
        detection_method = data.get('detection_method', 'unspecified')

        if comprehensive and designed and documented:
            return 1.0, f"Comprehensive fairness drift detection system designed and documented using: {detection_method}"
        elif designed and documented:
            return 1.0, f"Fairness drift detection system designed and documented using: {detection_method}"
        elif designed and implemented:
            return 1.0, "Fairness drift detection system designed and implemented"
        elif designed:
            return 0.6, "Fairness drift detection approach documented but implementation incomplete"
        elif mentioned:
            return 0.5, "Fairness drift detection mentioned but not detailed"
        else:
            return 0.0, "No fairness drift detection documentation"

    def _score_subgroup_performance_tracking(self, data: Dict) -> tuple:
        """
        Item 16: Subgroup Performance Tracking (design & documentation)
        1.0: Systematic subgroup tracking (including intersectional) designed and documented
        0.6: Subgroup tracking approach documented but incomplete
        0.5: Subgroup tracking mentioned but not systematic
        0.0: No subgroup tracking documentation
        """
        if not data:
            return 0.0, "No subgroup performance tracking documentation"

        systematic = data.get('systematic', False)
        intersectional = data.get('intersectional_subgroups', False)
        designed = data.get('designed', False)
        documented = data.get('documented', False)
        implemented = data.get('implemented', False)
        mentioned = data.get('mentioned', False)
        tracked_subgroups = data.get('tracked_subgroups', [])

        if systematic and intersectional and designed and documented:
            return 1.0, f"Systematic subgroup performance tracking (including intersectional) designed and documented for: {tracked_subgroups}"
        elif systematic and designed and documented:
            return 1.0, f"Systematic subgroup performance tracking designed and documented for: {tracked_subgroups}"
        elif designed and documented:
            return 1.0, "Subgroup performance tracking system designed and documented"
        elif designed:
            return 0.6, "Subgroup performance tracking approach documented but implementation may be incomplete"
        elif mentioned:
            return 0.5, "Subgroup performance tracking mentioned but not systematic"
        else:
            return 0.0, "No subgroup performance tracking documentation"
