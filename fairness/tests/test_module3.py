"""
Tests for Module 3 Fairness & Ethics
"""

import numpy as np
import pandas as pd
import pytest
from datetime import datetime

from fairness.metrics.fairness_metrics import (
    compute_demographic_parity,
    compute_equal_opportunity,
    compute_equalized_odds,
    compute_predictive_parity,
    compute_calibration,
    compute_subgroup_performance,
    compute_all_fairness_metrics
)
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine
from fairness.governance.governance_checker import GovernanceChecker
from fairness.monitoring.fairness_monitor import FairnessMonitor
from fairness.api import Module3API


# ===== FIXTURES =====

@pytest.fixture
def synthetic_biased_data():
    """
    Create synthetic dataset with known bias patterns.
    Group 0 (Female) has lower positive rate than Group 1 (Male)
    """
    np.random.seed(42)
    n_samples = 1000

    # True labels
    y_true = np.concatenate([
        np.random.binomial(1, 0.4, n_samples // 2),  # Group 0
        np.random.binomial(1, 0.5, n_samples // 2)   # Group 1
    ])

    # Biased predictions: Group 0 has 30% positive rate, Group 1 has 60%
    y_pred = np.concatenate([
        np.random.binomial(1, 0.3, n_samples // 2),  # Biased against Group 0
        np.random.binomial(1, 0.6, n_samples // 2)
    ])

    # Predicted probabilities
    y_score = np.concatenate([
        np.random.uniform(0.2, 0.8, n_samples // 2),
        np.random.uniform(0.3, 0.9, n_samples // 2)
    ])

    # Sensitive features
    sensitive_features = pd.DataFrame({
        'gender': ['Female'] * (n_samples // 2) + ['Male'] * (n_samples // 2),
        'age_group': ['20-40'] * (n_samples // 4) + ['40+'] * (n_samples // 4) +
        ['20-40'] * (n_samples // 4) + ['40+'] * (n_samples // 4)
    })

    return y_true, y_pred, y_score, sensitive_features


@pytest.fixture
def governance_inputs():
    """Sample governance inputs"""
    return {
        'training_data_bias_assessment': {
            'comprehensive_bias_analysis': True,
            'demographic_distribution': True,
            'historical_bias_checked': True,
            'documented': True
        },
        'bias_mitigation_techniques': {
            'techniques': ['reweighting', 'threshold_optimization'],
            'evaluated': True,
            'mentioned': True
        },
        'proxy_variable_analysis': {
            'proxy_variables_identified': True,
            'mitigation_plan_documented': True,
            'systematic_analysis': True,
            'mentioned': True
        },
        'fairness_accuracy_tradeoff': {
            'explicitly_documented': True,
            'with_rationale': True,
            'stakeholder_input': False,
            'mentioned': True,
            'acknowledged': True
        },
        'ethics_committee_approval': {
            'approved': True,
            'documented': True,
            'reviewed': True,
            'mentioned': True,
            'approval_date': '2025-01-01'
        },
        'stakeholder_consultation': {
            'comprehensive': True,
            'feedback_incorporated': True,
            'documented': True,
            'conducted': True,
            'mentioned': True,
            'stakeholder_groups': ['domain_experts', 'affected_community']
        },
        'accountability_assignment': {
            'clear': True,
            'named_roles': True,
            'review_procedures': True,
            'defined': True,
            'mentioned': True,
            'roles': ['fairness_lead', 'ethics_officer']
        },
        'incident_response_plan': {
            'comprehensive': True,
            'procedures_documented': True,
            'escalation_path': True,
            'remediation_steps': True,
            'exists': True,
            'mentioned': True
        },
        'fairness_drift_detection': {
            'comprehensive': True,
            'designed': True,
            'documented': True,
            'implemented': True,
            'mentioned': True,
            'detection_method': 'statistical_tests'
        },
        'subgroup_performance_tracking': {
            'systematic': True,
            'intersectional_subgroups': True,
            'designed': True,
            'documented': True,
            'implemented': True,
            'mentioned': True,
            'tracked_subgroups': ['gender', 'age', 'gender_age']
        }
    }


# ===== TESTS: DEMOGRAPHIC PARITY =====

def test_demographic_parity_perfect_parity():
    """Test demographic parity with perfect parity (score 1.0)"""
    y_pred = np.array([1, 1, 0, 0, 1, 1, 0, 0])
    sensitive_features = pd.DataFrame({
        'group': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B']
    })

    result = compute_demographic_parity(y_pred, sensitive_features)

    # Both groups have 50% positive rate
    assert result['scores']['group'] == 1.0
    assert result['gaps']['group'] == 0.0


def test_demographic_parity_large_gap():
    """Test demographic parity with large gap (score 0.2)"""
    y_pred = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    sensitive_features = pd.DataFrame({
        'group': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B']
    })

    result = compute_demographic_parity(y_pred, sensitive_features)

    # Group A has 100%, Group B has 0%
    assert result['gaps']['group'] == 1.0
    assert result['scores']['group'] == 0.2


# ===== TESTS: EQUAL OPPORTUNITY =====

def test_equal_opportunity_perfect():
    """Test equal opportunity with perfect TPR parity"""
    y_true = np.array([1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
    y_pred = np.array([1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0])
    sensitive_features = pd.DataFrame({
        'group': ['A', 'A', 'A', 'A', 'B', 'B', 'A', 'A', 'A', 'A', 'B', 'B']
    })

    result = compute_equal_opportunity(y_true, y_pred, sensitive_features)

    # Both groups have same TPR (2/4 = 0.5)
    assert result['scores']['group'] == 1.0


# ===== TESTS: SUBGROUP PERFORMANCE =====

def test_subgroup_performance_intersectional(synthetic_biased_data):
    """Test subgroup performance including intersectional analysis"""
    y_true, y_pred, y_score, sensitive_features = synthetic_biased_data

    result = compute_subgroup_performance(
        y_true, y_pred, y_score, sensitive_features)

    # Should have subgroups for both single and intersectional
    assert len(result['per_subgroup_metrics']) > 0
    assert 'overall' in result['scores']

    # Accuracy ratio should be between 0 and 1
    assert 0 <= result['min_max_accuracy_ratio'] <= 1


# ===== TESTS: BIAS DETECTION ENGINE =====

def test_bias_detection_engine(synthetic_biased_data):
    """Test bias detection engine on synthetic biased data"""
    y_true, y_pred, y_score, sensitive_features = synthetic_biased_data

    engine = BiasDetectionEngine()
    report = engine.evaluate_fairness(
        y_true, y_pred, sensitive_features, y_score)

    assert report.system_id == 'default_system'
    assert 0 <= report.category_a_score <= 1
    assert len(report.critical_issues) > 0  # Should detect bias
    assert len(report.worst_performing_groups) > 0
    assert len(report.largest_gaps) > 0


# ===== TESTS: GOVERNANCE CHECKER =====

def test_governance_checker_perfect_score(governance_inputs):
    """Test governance checker with perfect governance documentation"""
    checker = GovernanceChecker()
    report = checker.assess_governance(governance_inputs)

    # All scores should be 1.0 with perfect inputs
    assert report.category_b_score == 1.0
    assert report.category_c_score == 1.0
    assert report.category_d_score == 1.0


def test_governance_checker_partial_documentation():
    """Test governance checker with incomplete documentation"""
    partial_inputs = {
        'training_data_bias_assessment': {
            'demographic_distribution': True,
            'documented': True
        },
        'ethics_committee_approval': {},
        'accountability_assignment': {
            'mentioned': True
        }
    }

    checker = GovernanceChecker()
    report = checker.assess_governance(partial_inputs)

    # Scores should reflect incomplete documentation
    assert report.training_data_bias_assessment == 0.6
    assert report.ethics_committee_approval == 0.0
    assert report.accountability_assignment == 0.5


# ===== TESTS: FAIRNESS MONITORING =====

def test_fairness_monitor_drift_detection():
    """Test fairness drift monitoring"""
    monitor = FairnessMonitor()

    # Log baseline metrics
    baseline = {
        'demographic_parity_gap_gender': 0.05,
        'tpr_gap_gender': 0.04,
        'subgroup_accuracy_female': 0.85
    }

    # Log current metrics with drift
    current = {
        'demographic_parity_gap_gender': 0.12,  # Increased gap (0.07 change)
        'tpr_gap_gender': 0.04,
        'subgroup_accuracy_female': 0.82
    }

    report = monitor.detect_fairness_drift('test_system', baseline, current)

    assert report.drift_detected
    assert report.overall_severity in ['minor', 'moderate', 'major']
    assert len(report.detected_drifts) > 0


def test_fairness_monitor_metric_logging():
    """Test metric logging and retrieval"""
    monitor = FairnessMonitor()

    # Log metrics over time
    monitor.log_fairness_metric('sys1', 'metric1', 0.05)
    monitor.log_fairness_metric('sys1', 'metric1', 0.06)
    monitor.log_fairness_metric('sys1', 'metric1', 0.07)

    history = monitor.get_metric_history('sys1', 'metric1')

    assert len(history) == 3
    assert history[0][1] == 0.05
    assert history[-1][1] == 0.07


# ===== TESTS: END-TO-END =====

def test_end_to_end_module3_assessment(synthetic_biased_data, governance_inputs):
    """End-to-end test of complete Module 3 assessment"""
    y_true, y_pred, y_score, sensitive_features = synthetic_biased_data

    # Step 1: Run bias detection
    engine = BiasDetectionEngine()
    fairness_report = engine.evaluate_fairness(
        y_true, y_pred, sensitive_features, y_score,
        system_id='test_system', model_version='1.0'
    )

    # Step 2: Assess governance
    checker = GovernanceChecker()
    governance_report = checker.assess_governance(
        governance_inputs, 'test_system')

    # Step 3: Compute Module 3 score
    api = Module3API()
    assessment = api.compute_complete_assessment(
        fairness_report, governance_report,
        system_id='test_system'
    )

    # Verify results
    assert assessment['module'] == 'IRAQAF_MODULE_3_FAIRNESS'
    assert 0 <= assessment['overall_score'] <= 1
    assert assessment['risk_level'] in ['Low', 'Medium', 'High']
    assert 'category_scores' in assessment
    assert 'critical_gaps' in assessment

    print(f"\nEnd-to-End Test Results:")
    print(f"  Overall Score: {assessment['overall_score']:.1%}")
    print(f"  Risk Level: {assessment['risk_level']}")
    print(f"  Summary: {assessment['summary']}")


# ===== TESTS: EDGE CASES =====

def test_small_group_handling():
    """Test handling of small groups"""
    y_true = np.array([1, 0, 1])
    y_pred = np.array([1, 0, 1])
    sensitive_features = pd.DataFrame({
        'group': ['A', 'A', 'B']  # Group B has only 1 sample
    })

    result = compute_demographic_parity(y_pred, sensitive_features)

    # Should handle small groups gracefully
    assert 'group' in result['scores']


def test_missing_sensitive_features():
    """Test handling of missing sensitive features"""
    y_true = np.array([1, 0, 1, 0])
    y_pred = np.array([1, 0, 1, 0])
    sensitive_features = pd.DataFrame()  # Empty

    result = compute_demographic_parity(y_pred, sensitive_features)

    # Should return empty results
    assert len(result['scores']) == 0


def test_all_same_predictions():
    """Test with all same predictions (degenerate case)"""
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.array([1, 1, 1, 1])  # All 1s
    sensitive_features = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B']
    })

    result = compute_demographic_parity(y_pred, sensitive_features)

    # Both groups have 100% positive rate
    assert result['scores']['group'] == 1.0
    assert result['gaps']['group'] == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
