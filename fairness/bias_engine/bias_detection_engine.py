"""
Bias Detection Engine
Orchestrates fairness metrics computation and scoring
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from ..metrics.fairness_metrics import (
    compute_all_fairness_metrics,
    FairnessMetrics
)


@dataclass
class FairnessReport:
    """Complete fairness evaluation report"""
    system_id: str
    model_version: str
    timestamp: str

    # Raw metrics
    fairness_metrics: FairnessMetrics

    # Category A aggregated scores
    demographic_parity_score: float
    equal_opportunity_score: float
    equalized_odds_score: float
    predictive_parity_score: float
    calibration_score: float
    subgroup_performance_score: float

    # Overall Category A score
    category_a_score: float  # Algorithmic Fairness Metrics

    # Critical findings
    critical_issues: List[Dict[str, str]] = field(default_factory=list)
    worst_performing_groups: List[Dict[str, Any]] = field(default_factory=list)
    largest_gaps: List[Dict[str, Any]] = field(default_factory=list)

    # Detailed explanations
    explanations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'system_id': self.system_id,
            'model_version': self.model_version,
            'timestamp': self.timestamp,
            'fairness_metrics': self.fairness_metrics.to_dict(),
            'demographic_parity_score': self.demographic_parity_score,
            'equal_opportunity_score': self.equal_opportunity_score,
            'equalized_odds_score': self.equalized_odds_score,
            'predictive_parity_score': self.predictive_parity_score,
            'calibration_score': self.calibration_score,
            'subgroup_performance_score': self.subgroup_performance_score,
            'category_a_score': self.category_a_score,
            'critical_issues': self.critical_issues,
            'worst_performing_groups': self.worst_performing_groups,
            'largest_gaps': self.largest_gaps,
            'explanations': self.explanations
        }


class BiasDetectionEngine:
    """
    Bias Detection Engine
    Orchestrates computation of fairness metrics and generates comprehensive bias reports
    """

    def __init__(self):
        pass

    def evaluate_fairness(self,
                          y_true: np.ndarray,
                          y_pred: np.ndarray,
                          sensitive_features: pd.DataFrame,
                          y_score: Optional[np.ndarray] = None,
                          system_id: str = "default_system",
                          model_version: str = "1.0") -> FairnessReport:
        """
        Evaluate fairness of a model's predictions.

        Args:
            y_true: Ground truth labels (0/1)
            y_pred: Model predictions (0/1)
            sensitive_features: DataFrame with protected attributes
            y_score: Predicted probabilities (optional)
            system_id: System identifier
            model_version: Model version string

        Returns:
            FairnessReport with comprehensive analysis
        """
        # Compute all fairness metrics
        metrics = compute_all_fairness_metrics(
            y_true, y_pred, sensitive_features, y_score)

        # Compute individual metric scores
        dp_score = self._aggregate_scores(
            metrics.demographic_parity.get('scores', {}))
        eo_score = self._aggregate_scores(
            metrics.equal_opportunity.get('scores', {}))
        eo_odds_score = self._aggregate_scores(
            metrics.equalized_odds.get('scores', {}))
        pp_score = self._aggregate_scores(
            metrics.predictive_parity.get('scores', {}))
        cal_score = self._aggregate_scores(
            metrics.calibration.get('scores', {}))
        subgroup_score = self._aggregate_scores(
            metrics.subgroup_performance.get('scores', {}))

        # Compute Category A score (average of all metrics)
        category_a_score = np.mean(
            [dp_score, eo_score, eo_odds_score, pp_score, cal_score, subgroup_score])

        # Identify critical issues
        critical_issues = self._extract_critical_issues(
            metrics, y_true, y_pred, sensitive_features)
        worst_groups = self._identify_worst_performing_groups(metrics)
        largest_gaps = self._identify_largest_gaps(metrics)

        timestamp = datetime.utcnow().isoformat() + "Z"

        report = FairnessReport(
            system_id=system_id,
            model_version=model_version,
            timestamp=timestamp,
            fairness_metrics=metrics,
            demographic_parity_score=dp_score,
            equal_opportunity_score=eo_score,
            equalized_odds_score=eo_odds_score,
            predictive_parity_score=pp_score,
            calibration_score=cal_score,
            subgroup_performance_score=subgroup_score,
            category_a_score=category_a_score,
            critical_issues=critical_issues,
            worst_performing_groups=worst_groups,
            largest_gaps=largest_gaps,
            explanations=metrics.get_all_explanations()
        )

        return report

    def _aggregate_scores(self, scores: Dict[str, float]) -> float:
        """
        Aggregate individual metric scores into a category score.
        Average across all groups/attributes.
        """
        if not scores:
            return 0.5  # Neutral score if no data

        return np.mean(list(scores.values()))

    def _extract_critical_issues(self,
                                 metrics: FairnessMetrics,
                                 y_true: np.ndarray,
                                 y_pred: np.ndarray,
                                 sensitive_features: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Extract critical fairness issues (scores < 0.5)
        """
        issues = []

        # Check demographic parity
        for attr, score in metrics.demographic_parity.get('scores', {}).items():
            if score < 0.5:
                gap = metrics.demographic_parity['gaps'][attr]
                issues.append({
                    'type': 'Demographic Parity Violation',
                    'attribute': attr,
                    'gap': gap,
                    'score': score,
                    'description': f"Large disparity in positive prediction rates across {attr} groups (gap: {gap:.4f})",
                    'severity': 'critical' if score < 0.2 else 'high'
                })

        # Check equal opportunity
        for attr, score in metrics.equal_opportunity.get('scores', {}).items():
            if score < 0.5:
                gap = metrics.equal_opportunity['gaps'][attr]
                issues.append({
                    'type': 'Equal Opportunity Violation',
                    'attribute': attr,
                    'gap': gap,
                    'score': score,
                    'description': f"True Positive Rate differs significantly across {attr} groups (gap: {gap:.4f})",
                    'severity': 'critical' if score < 0.2 else 'high'
                })

        # Check equalized odds
        for attr, score in metrics.equalized_odds.get('scores', {}).items():
            if score < 0.5:
                combined_gap = metrics.equalized_odds['combined_gaps'][attr]
                issues.append({
                    'type': 'Equalized Odds Violation',
                    'attribute': attr,
                    'gap': combined_gap,
                    'score': score,
                    'description': f"TPR and/or FPR differ significantly across {attr} groups (gap: {combined_gap:.4f})",
                    'severity': 'critical' if score < 0.2 else 'high'
                })

        # Check subgroup performance
        for subgroup in metrics.subgroup_performance.get('critical_subgroups', []):
            issues.append({
                'type': 'Subgroup Performance',
                'subgroup': subgroup['subgroup'],
                'accuracy': subgroup['accuracy'],
                'size': subgroup['size'],
                'description': f"Subgroup {subgroup['subgroup']} has low accuracy ({subgroup['accuracy']:.4f}) with n={subgroup['size']}",
                'severity': 'critical' if subgroup['accuracy'] < 0.6 else 'high'
            })

        return sorted(issues, key=lambda x: x.get('score', 0))

    def _identify_worst_performing_groups(self, metrics: FairnessMetrics) -> List[Dict[str, Any]]:
        """
        Identify groups with the worst fairness performance
        """
        worst = []

        # From subgroup performance
        for subgroup_name, subgroup_metrics in metrics.subgroup_performance.get('per_subgroup_metrics', {}).items():
            worst.append({
                'subgroup': subgroup_name,
                'accuracy': subgroup_metrics['accuracy'],
                'sensitivity': subgroup_metrics['sensitivity'],
                'specificity': subgroup_metrics['specificity'],
                'auc': subgroup_metrics['auc'],
                'size': subgroup_metrics['size']
            })

        # Sort by accuracy
        worst.sort(key=lambda x: x['accuracy'])

        return worst[:5]  # Return top 5 worst

    def _identify_largest_gaps(self, metrics: FairnessMetrics) -> List[Dict[str, Any]]:
        """
        Identify the largest fairness gaps across groups
        """
        gaps = []

        for attr, gap in metrics.demographic_parity.get('gaps', {}).items():
            gaps.append({
                'metric': 'demographic_parity',
                'attribute': attr,
                'gap': gap,
                'per_group': metrics.demographic_parity['per_group_rates'][attr]
            })

        for attr, gap in metrics.equal_opportunity.get('gaps', {}).items():
            gaps.append({
                'metric': 'equal_opportunity',
                'attribute': attr,
                'gap': gap,
                'per_group': metrics.equal_opportunity['per_group_tpr'][attr]
            })

        for attr, gap in metrics.equalized_odds.get('combined_gaps', {}).items():
            gaps.append({
                'metric': 'equalized_odds',
                'attribute': attr,
                'gap': gap,
                'per_group': {
                    'tpr': metrics.equalized_odds['tpr_gaps'][attr],
                    'fpr': metrics.equalized_odds['fpr_gaps'][attr]
                }
            })

        # Sort by gap size
        gaps.sort(key=lambda x: x['gap'], reverse=True)

        return gaps[:5]  # Return top 5 largest gaps
