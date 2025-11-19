"""
Fairness metrics library
Implements demographic parity, equal opportunity, equalized odds, predictive parity, 
calibration, and subgroup performance analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict


# Thresholds from IRAQAF specification

DEMOGRAPHIC_PARITY_THRESHOLDS = {
    0.05: 1.0,      # DPG < 0.05 → 1.0
    0.10: 0.7,      # 0.05-0.10 → 0.7
    0.15: 0.5,      # 0.10-0.15 → 0.5
    float('inf'): 0.2  # > 0.15 → 0.2
}

EQUAL_OPPORTUNITY_THRESHOLDS = {
    0.05: 1.0,
    0.10: 0.7,
    0.15: 0.5,
    float('inf'): 0.2
}

EQUALIZED_ODDS_THRESHOLDS = {
    0.05: 1.0,
    0.10: 0.7,
    0.15: 0.5,
    float('inf'): 0.2
}

PREDICTIVE_PARITY_THRESHOLDS = {
    0.05: 1.0,
    0.10: 0.7,
    0.15: 0.5,
    float('inf'): 0.2
}

CALIBRATION_THRESHOLDS = {
    0.05: 1.0,
    0.10: 0.7,
    0.15: 0.5,
    float('inf'): 0.2
}

# Subgroup accuracy ratio thresholds (from IRAQAF spec)
# Bounds: 0.90 (excellent), 0.85 (good), 0.80 (acceptable)
# Ratio = min(subgroup accuracy) / max(subgroup accuracy)
SUBGROUP_ACCURACY_RATIO_THRESHOLDS = {
    0.90: 1.0,      # Ratio >= 0.90 → 1.0 (excellent parity)
    0.85: 0.7,      # Ratio 0.85-0.89 → 0.7 (good parity)
    0.80: 0.5,      # Ratio 0.80-0.84 → 0.5 (acceptable parity)
    0.0: 0.2        # Ratio < 0.80 → 0.2 (poor parity)
}


def score_gap(gap: float, thresholds: Dict[float, float]) -> float:
    """
    Score a gap value based on thresholds.
    Thresholds dict should have keys in ascending order with corresponding scores.
    """
    for threshold, score in sorted(thresholds.items()):
        if gap <= threshold:
            return score
    return 0.2  # Default to worst score if above all thresholds


def compute_demographic_parity(y_pred: np.ndarray, sensitive_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute demographic parity metrics.

    Returns dict with:
    - per_group_rates: dict of positive prediction rate per group per attribute
    - gaps: dict of gaps per protected attribute
    - scores: dict of scores per protected attribute
    - explanations: list of human-readable explanations
    """
    results = {
        'per_group_rates': {},
        'gaps': {},
        'scores': {},
        'explanations': []
    }

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        rates = {}

        for group in groups:
            mask = sensitive_features[attr] == group
            if mask.sum() > 0:
                rate = y_pred[mask].mean()
                rates[group] = rate

        results['per_group_rates'][attr] = rates

        if len(rates) > 1:
            gap = max(rates.values()) - min(rates.values())
            results['gaps'][attr] = gap
            score = score_gap(gap, DEMOGRAPHIC_PARITY_THRESHOLDS)
            results['scores'][attr] = score

            max_group = max(rates, key=rates.get)
            min_group = min(rates, key=rates.get)
            results['explanations'].append(
                f"Demographic Parity for {attr}: {gap:.4f} (max {max_group} "
                f"{rates[max_group]:.4f}, min {min_group} {rates[min_group]:.4f}) → {score}"
            )

    return results


def compute_equal_opportunity(y_true: np.ndarray, y_pred: np.ndarray,
                              sensitive_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute equal opportunity (TPR gap) metrics.
    """
    results = {
        'per_group_tpr': {},
        'gaps': {},
        'scores': {},
        'explanations': []
    }

    # Only compute on positive cases (y_true == 1)
    positive_mask = y_true == 1
    if positive_mask.sum() == 0:
        return results

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        tprs = {}

        for group in groups:
            mask = (sensitive_features[attr] == group) & positive_mask
            if mask.sum() > 0:
                tp = ((y_pred[mask] == 1) & (y_true[mask] == 1)).sum()
                tpr = tp / mask.sum()
                tprs[group] = tpr

        results['per_group_tpr'][attr] = tprs

        if len(tprs) > 1:
            gap = max(tprs.values()) - min(tprs.values())
            results['gaps'][attr] = gap
            score = score_gap(gap, EQUAL_OPPORTUNITY_THRESHOLDS)
            results['scores'][attr] = score

            max_group = max(tprs, key=tprs.get)
            min_group = min(tprs, key=tprs.get)
            results['explanations'].append(
                f"Equal Opportunity (TPR) for {attr}: {gap:.4f} (max {max_group} "
                f"{tprs[max_group]:.4f}, min {min_group} {tprs[min_group]:.4f}) → {score}"
            )

    return results


def compute_equalized_odds(y_true: np.ndarray, y_pred: np.ndarray,
                           sensitive_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute equalized odds (TPR and FPR gap) metrics.
    """
    results = {
        'tpr_gaps': {},
        'fpr_gaps': {},
        'combined_gaps': {},
        'scores': {},
        'explanations': []
    }

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        tprs = {}
        fprs = {}

        for group in groups:
            mask = sensitive_features[attr] == group
            if mask.sum() > 0:
                # TPR: TP / (TP + FN) on positive cases
                positive_mask = (mask) & (y_true == 1)
                if positive_mask.sum() > 0:
                    tp = ((y_pred[positive_mask] == 1) & (
                        y_true[positive_mask] == 1)).sum()
                    tpr = tp / positive_mask.sum()
                    tprs[group] = tpr

                # FPR: FP / (FP + TN) on negative cases
                negative_mask = (mask) & (y_true == 0)
                if negative_mask.sum() > 0:
                    fp = ((y_pred[negative_mask] == 1) & (
                        y_true[negative_mask] == 0)).sum()
                    fpr = fp / negative_mask.sum()
                    fprs[group] = fpr

        if len(tprs) > 1:
            tpr_gap = max(tprs.values()) - min(tprs.values())
            results['tpr_gaps'][attr] = tpr_gap

        if len(fprs) > 1:
            fpr_gap = max(fprs.values()) - min(fprs.values())
            results['fpr_gaps'][attr] = fpr_gap

        # Combined gap (max of the two)
        if tprs and fprs and (len(tprs) > 1 or len(fprs) > 1):
            combined_gap = max(
                results['tpr_gaps'].get(attr, 0),
                results['fpr_gaps'].get(attr, 0)
            )
            results['combined_gaps'][attr] = combined_gap
            score = score_gap(combined_gap, EQUALIZED_ODDS_THRESHOLDS)
            results['scores'][attr] = score
            results['explanations'].append(
                f"Equalized Odds for {attr}: TPR gap {results['tpr_gaps'].get(attr, 0):.4f}, "
                f"FPR gap {results['fpr_gaps'].get(attr, 0):.4f}, combined {combined_gap:.4f} → {score}"
            )

    return results


def compute_predictive_parity(y_true: np.ndarray, y_pred: np.ndarray,
                              sensitive_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute predictive parity (PPV/precision gap) metrics.
    """
    results = {
        'per_group_ppv': {},
        'gaps': {},
        'scores': {},
        'explanations': []
    }

    # Only compute on predicted positive cases (y_pred == 1)
    pred_positive_mask = y_pred == 1
    if pred_positive_mask.sum() == 0:
        return results

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        ppvs = {}

        for group in groups:
            mask = (sensitive_features[attr] == group) & pred_positive_mask
            if mask.sum() > 0:
                tp = ((y_pred[mask] == 1) & (y_true[mask] == 1)).sum()
                ppv = tp / mask.sum()
                ppvs[group] = ppv

        results['per_group_ppv'][attr] = ppvs

        if len(ppvs) > 1:
            gap = max(ppvs.values()) - min(ppvs.values())
            results['gaps'][attr] = gap
            score = score_gap(gap, PREDICTIVE_PARITY_THRESHOLDS)
            results['scores'][attr] = score

            max_group = max(ppvs, key=ppvs.get)
            min_group = min(ppvs, key=ppvs.get)
            results['explanations'].append(
                f"Predictive Parity (PPV) for {attr}: {gap:.4f} (max {max_group} "
                f"{ppvs[max_group]:.4f}, min {min_group} {ppvs[min_group]:.4f}) → {score}"
            )

    return results


def compute_calibration(y_true: np.ndarray, y_score: Optional[np.ndarray],
                        sensitive_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute calibration gap metrics using Expected Calibration Error (ECE).
    Bins predictions and computes ECE per group.
    """
    results = {
        'per_group_ece': {},
        'gaps': {},
        'scores': {},
        'explanations': []
    }

    if y_score is None or len(y_score) == 0:
        return results

    y_score = np.array(y_score)

    def compute_ece(y_true_group: np.ndarray, y_score_group: np.ndarray, n_bins: int = 10) -> float:
        """Compute Expected Calibration Error for a group"""
        if len(y_true_group) == 0:
            return 0.0

        bins = np.linspace(0, 1, n_bins + 1)
        ece = 0.0

        for i in range(n_bins):
            mask = (y_score_group >= bins[i]) & (y_score_group < bins[i + 1])
            if mask.sum() > 0:
                accuracy = (y_true_group[mask] == (
                    y_score_group[mask] >= 0.5)).mean()
                confidence = y_score_group[mask].mean()
                ece += abs(accuracy - confidence) * \
                    mask.sum() / len(y_true_group)

        return ece

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        eces = {}

        for group in groups:
            mask = sensitive_features[attr] == group
            if mask.sum() > 0:
                ece = compute_ece(y_true[mask], y_score[mask])
                eces[group] = ece

        results['per_group_ece'][attr] = eces

        if len(eces) > 1:
            gap = max(eces.values()) - min(eces.values())
            results['gaps'][attr] = gap
            score = score_gap(gap, CALIBRATION_THRESHOLDS)
            results['scores'][attr] = score

            max_group = max(eces, key=eces.get)
            min_group = min(eces, key=eces.get)
            results['explanations'].append(
                f"Calibration (ECE) for {attr}: {gap:.4f} (max {max_group} "
                f"{eces[max_group]:.4f}, min {min_group} {eces[min_group]:.4f}) → {score}"
            )

    return results


def compute_subgroup_performance(y_true: np.ndarray, y_pred: np.ndarray,
                                 y_score: Optional[np.ndarray],
                                 sensitive_features: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute accuracy, AUC-ROC, sensitivity (TPR), specificity (TNR) per subgroup,
    including intersectional subgroups.
    """
    results = {
        'per_subgroup_metrics': {},
        'min_max_accuracy_ratio': 1.0,
        'scores': {},
        'critical_subgroups': [],
        'explanations': []
    }

    # Generate intersectional subgroups
    subgroups = []

    # Single-attribute subgroups
    for attr in sensitive_features.columns:
        for group in sensitive_features[attr].unique():
            subgroups.append({attr: group})

    # Two-attribute intersections
    attrs = list(sensitive_features.columns)
    if len(attrs) >= 2:
        for i in range(len(attrs)):
            for j in range(i + 1, len(attrs)):
                for g1 in sensitive_features[attrs[i]].unique():
                    for g2 in sensitive_features[attrs[j]].unique():
                        subgroups.append({attrs[i]: g1, attrs[j]: g2})

    accuracies = []

    for subgroup in subgroups:
        mask = pd.Series([True] * len(y_true))
        for attr, value in subgroup.items():
            mask = mask & (sensitive_features[attr] == value)

        if mask.sum() < 2:  # Skip very small subgroups
            continue

        y_true_sub = y_true[mask]
        y_pred_sub = y_pred[mask]

        # Accuracy
        accuracy = (y_pred_sub == y_true_sub).mean()
        accuracies.append(accuracy)

        # Sensitivity (TPR)
        positive_mask = y_true_sub == 1
        sensitivity = (y_pred_sub[positive_mask] == 1).mean(
        ) if positive_mask.sum() > 0 else 0.0

        # Specificity (TNR)
        negative_mask = y_true_sub == 0
        specificity = (y_pred_sub[negative_mask] == 0).mean(
        ) if negative_mask.sum() > 0 else 0.0

        # AUC-ROC
        auc = 0.0
        if y_score is not None and positive_mask.sum() > 0 and negative_mask.sum() > 0:
            from sklearn.metrics import roc_auc_score
            try:
                y_score_sub = y_score[mask]
                auc = roc_auc_score(y_true_sub, y_score_sub)
            except:
                auc = 0.0

        subgroup_name = "_".join(
            [f"{k}_{v}" for k, v in sorted(subgroup.items())])
        results['per_subgroup_metrics'][subgroup_name] = {
            'accuracy': accuracy,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'auc': auc,
            'size': mask.sum()
        }

        if accuracy < 0.75:
            results['critical_subgroups'].append({
                'subgroup': subgroup_name,
                'accuracy': accuracy,
                'size': mask.sum()
            })

    # Compute min-max ratio
    if accuracies:
        min_acc = min(accuracies)
        max_acc = max(accuracies)
        if max_acc > 0:
            results['min_max_accuracy_ratio'] = min_acc / max_acc

        # Score the ratio
        ratio = results['min_max_accuracy_ratio']
        score = 0.2
        for threshold in sorted(SUBGROUP_ACCURACY_RATIO_THRESHOLDS.keys(), reverse=True):
            if ratio <= threshold:
                score = SUBGROUP_ACCURACY_RATIO_THRESHOLDS[threshold]
                break

        results['scores']['overall'] = score
        results['explanations'].append(
            f"Subgroup Performance: Min accuracy {min_acc:.4f}, max {max_acc:.4f}, "
            f"ratio {ratio:.4f} → {score}"
        )

    return results


@dataclass
class FairnessMetrics:
    """Container for all fairness metrics"""
    demographic_parity: Dict[str, Any]
    equal_opportunity: Dict[str, Any]
    equalized_odds: Dict[str, Any]
    predictive_parity: Dict[str, Any]
    calibration: Dict[str, Any]
    subgroup_performance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def get_all_explanations(self) -> List[str]:
        """Collect all metric explanations"""
        explanations = []
        for metric_dict in [
            self.demographic_parity,
            self.equal_opportunity,
            self.equalized_odds,
            self.predictive_parity,
            self.calibration,
            self.subgroup_performance
        ]:
            explanations.extend(metric_dict.get('explanations', []))
        return explanations

    def get_average_score(self) -> float:
        """Compute average of all metric scores"""
        all_scores = []
        for metric_dict in [
            self.demographic_parity,
            self.equal_opportunity,
            self.equalized_odds,
            self.predictive_parity,
            self.calibration,
            self.subgroup_performance
        ]:
            scores = metric_dict.get('scores', {}).values()
            all_scores.extend(scores)

        return np.mean(all_scores) if all_scores else 0.5


def compute_all_fairness_metrics(y_true: np.ndarray,
                                 y_pred: np.ndarray,
                                 sensitive_features: pd.DataFrame,
                                 y_score: Optional[np.ndarray] = None) -> FairnessMetrics:
    """
    Compute all fairness metrics in one call.

    Args:
        y_true: Ground truth labels (0/1)
        y_pred: Predictions (0/1)
        sensitive_features: DataFrame with protected attributes
        y_score: Predicted probabilities (optional, for calibration/AUC)

    Returns:
        FairnessMetrics object with all results
    """
    return FairnessMetrics(
        demographic_parity=compute_demographic_parity(
            y_pred, sensitive_features),
        equal_opportunity=compute_equal_opportunity(
            y_true, y_pred, sensitive_features),
        equalized_odds=compute_equalized_odds(
            y_true, y_pred, sensitive_features),
        predictive_parity=compute_predictive_parity(
            y_true, y_pred, sensitive_features),
        calibration=compute_calibration(y_true, y_score, sensitive_features),
        subgroup_performance=compute_subgroup_performance(
            y_true, y_pred, y_score, sensitive_features)
    )
