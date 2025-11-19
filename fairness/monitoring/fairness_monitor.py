"""
Fairness Drift Monitoring
Detects and tracks fairness metric changes over time
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from scipy import stats


@dataclass
class DriftReport:
    """Drift detection report"""
    system_id: str
    timestamp: str

    # Drift status
    drift_detected: bool
    overall_severity: str  # "none", "minor", "moderate", "major"

    # Detected drifts
    detected_drifts: List[Dict[str, Any]] = field(default_factory=list)

    # Metric changes
    metric_changes: Dict[str, float] = field(default_factory=dict)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'system_id': self.system_id,
            'timestamp': self.timestamp,
            'drift_detected': self.drift_detected,
            'overall_severity': self.overall_severity,
            'detected_drifts': self.detected_drifts,
            'metric_changes': self.metric_changes,
            'recommendations': self.recommendations
        }


class FairnessMonitor:
    """
    Fairness Drift Monitor
    Detects statistical changes in fairness metrics over time
    """

    # IRAQAF drift severity (3-level): based on metric change magnitude
    # Thresholds: change < 0.03 (none), 0.03-0.15 (minor), >= 0.15 (major)
    SEVERITY_LEVELS = {
        'none': 0.03,           # Change < 0.03 → no drift
        'minor': 0.15,          # Change 0.03-0.15 → minor drift
        'major': float('inf')   # Change >= 0.15 → major drift
    }

    def __init__(self):
        self.historical_metrics: Dict[str, List[Tuple[str, float]]] = {}

    def log_fairness_metric(self, system_id: str, metric_name: str, value: float, timestamp: Optional[str] = None) -> None:
        """
        Log a fairness metric value for drift tracking.

        Args:
            system_id: System identifier
            metric_name: Name of the metric (e.g., "demographic_parity_gap_gender")
            value: Metric value
            timestamp: ISO timestamp (if None, uses current time)
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"

        key = f"{system_id}:{metric_name}"
        if key not in self.historical_metrics:
            self.historical_metrics[key] = []

        self.historical_metrics[key].append((timestamp, value))

    def detect_fairness_drift(self, system_id: str, baseline_metrics: Dict[str, float],
                              current_metrics: Dict[str, float]) -> DriftReport:
        """
        Detect fairness drift by comparing current metrics to baseline.

        Args:
            system_id: System identifier
            baseline_metrics: Baseline metric values (dict of metric_name -> value)
            current_metrics: Current metric values

        Returns:
            DriftReport with detected drifts and severity classification
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        detected_drifts = []
        metric_changes = {}
        recommendations = []
        max_severity = 'none'

        for metric_name, current_value in current_metrics.items():
            if metric_name not in baseline_metrics:
                continue

            baseline_value = baseline_metrics[metric_name]
            change = current_value - baseline_value
            metric_changes[metric_name] = change

            # Classify drift severity
            severity = self._classify_severity(abs(change))

            if severity != 'none':
                detected_drifts.append({
                    'metric': metric_name,
                    'baseline': baseline_value,
                    'current': current_value,
                    'change': change,
                    'change_pct': (change / baseline_value * 100) if baseline_value != 0 else 0,
                    'severity': severity,
                    'detection_method': 'delta'
                })

                # Update max severity
                if self._severity_rank(severity) > self._severity_rank(max_severity):
                    max_severity = severity

        # Generate recommendations based on detected drifts
        for drift in detected_drifts:
            metric = drift['metric']
            severity = drift['severity']

            if severity == 'major':
                recommendations.append(
                    f"URGENT: Major drift detected in {metric} ({drift['change_pct']:.2f}% change). "
                    f"Immediate investigation and potential model retraining required."
                )
            elif severity == 'minor':
                recommendations.append(
                    f"Minor drift in {metric}. Continue monitoring for escalation."
                )

        drift_detected = len(detected_drifts) > 0

        return DriftReport(
            system_id=system_id,
            timestamp=timestamp,
            drift_detected=drift_detected,
            overall_severity=max_severity,
            detected_drifts=detected_drifts,
            metric_changes=metric_changes,
            recommendations=recommendations
        )

    def detect_statistical_drift(self, system_id: str, metric_name: str,
                                 baseline_window: int = 10,
                                 current_window: int = 5,
                                 alpha: float = 0.05) -> Tuple[bool, float, str]:
        """
        Perform statistical drift detection using t-test on metric windows.

        Args:
            system_id: System identifier
            metric_name: Metric name
            baseline_window: Number of recent values to use as baseline
            current_window: Number of recent values to compare
            alpha: Significance level for t-test

        Returns:
            Tuple of (drift_detected, p_value, severity)
        """
        key = f"{system_id}:{metric_name}"
        if key not in self.historical_metrics or len(self.historical_metrics[key]) < baseline_window + current_window:
            return False, 1.0, 'none'

        all_values = [v for _, v in self.historical_metrics[key]]

        # Split into baseline and current windows
        baseline_vals = np.array(
            all_values[-baseline_window - current_window:-current_window])
        current_vals = np.array(all_values[-current_window:])

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(current_vals, baseline_vals)

        drift_detected = p_value < alpha

        # Estimate severity
        change = np.mean(current_vals) - np.mean(baseline_vals)
        severity = self._classify_severity(abs(change))

        return drift_detected, p_value, severity

    def detect_control_chart_drift(self, system_id: str, metric_name: str,
                                   window_size: int = 10,
                                   sigma_limit: float = 2.0) -> Tuple[bool, float, str]:
        """
        Perform control chart-based drift detection (mean ± sigma limits).

        Args:
            system_id: System identifier
            metric_name: Metric name
            window_size: Window size for computing mean and std
            sigma_limit: Number of standard deviations for control limits

        Returns:
            Tuple of (drift_detected, distance_from_mean, severity)
        """
        key = f"{system_id}:{metric_name}"
        if key not in self.historical_metrics or len(self.historical_metrics[key]) < window_size:
            return False, 0.0, 'none'

        all_values = np.array([v for _, v in self.historical_metrics[key]])

        # Use all but last value for baseline
        baseline_vals = all_values[:-1]
        current_val = all_values[-1]

        mean = np.mean(baseline_vals)
        std = np.std(baseline_vals)

        # Compute distance from mean
        distance = abs(current_val - mean) / (std + 1e-8)

        # Check if outside control limits
        drift_detected = distance > sigma_limit

        # Estimate severity based on actual change
        change = current_val - mean
        severity = self._classify_severity(abs(change))

        return drift_detected, distance, severity

    def detect_moving_window_drift(self, system_id: str, metric_name: str,
                                   baseline_end_idx: int = -20,
                                   comparison_start_idx: int = -10) -> Tuple[bool, float, str]:
        """
        Compare two non-overlapping windows using mean difference.

        Args:
            system_id: System identifier
            metric_name: Metric name
            baseline_end_idx: End index for baseline window (negative indexing)
            comparison_start_idx: Start index for comparison window

        Returns:
            Tuple of (drift_detected, delta, severity)
        """
        key = f"{system_id}:{metric_name}"
        if key not in self.historical_metrics:
            return False, 0.0, 'none'

        all_values = np.array([v for _, v in self.historical_metrics[key]])

        if len(all_values) < abs(baseline_end_idx):
            return False, 0.0, 'none'

        baseline_vals = all_values[:baseline_end_idx]
        comparison_vals = all_values[comparison_start_idx:]

        if len(baseline_vals) == 0 or len(comparison_vals) == 0:
            return False, 0.0, 'none'

        delta = np.mean(comparison_vals) - np.mean(baseline_vals)
        drift_detected = abs(delta) > 0.03

        severity = self._classify_severity(abs(delta))

        return drift_detected, delta, severity

    def _classify_severity(self, change: float) -> str:
        """Classify drift severity based on absolute change (3-level IRAQAF)

        - NONE: change < 0.03 (acceptable variation)
        - MINOR: change 0.03-0.15 (requires monitoring)
        - MAJOR: change >= 0.15 (requires action)
        """
        if change < 0.03:
            return 'none'
        elif change < 0.15:
            return 'minor'
        else:
            return 'major'

    def _severity_rank(self, severity: str) -> int:
        """Get numeric rank for severity (for comparison)"""
        rank_map = {'none': 0, 'minor': 1, 'major': 2}
        return rank_map.get(severity, 0)

    def get_metric_history(self, system_id: str, metric_name: str, limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        Retrieve historical values for a metric.

        Args:
            system_id: System identifier
            metric_name: Metric name
            limit: Maximum number of records to return

        Returns:
            List of (timestamp, value) tuples
        """
        key = f"{system_id}:{metric_name}"
        history = self.historical_metrics.get(key, [])

        if limit:
            return history[-limit:]
        return history


# Global monitor instance
_monitor = FairnessMonitor()


def get_fairness_monitor() -> FairnessMonitor:
    """Get the global fairness monitor instance"""
    return _monitor
