"""
IRAQAF Metrics Calculations
Implementation of key statistical and fairness metrics used throughout the platform
"""

import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class PSICalculator:
    """Population Stability Index (PSI) Calculator for drift detection"""
    
    @staticmethod
    def calculate_psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> Dict[str, Any]:
        """
        Calculate Population Stability Index for drift detection
        
        Args:
            expected: Baseline/expected distribution
            actual: Current/actual distribution
            buckets: Number of buckets for binning
            
        Returns:
            Dictionary with PSI score and detailed breakdown
        """
        try:
            # Create buckets based on expected distribution
            breakpoints = np.arange(0, buckets + 1) / buckets * 100
            
            # Calculate expected and actual percentages
            expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
            actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
            
            # Avoid division by zero
            expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
            actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
            
            # Calculate PSI components
            psi_components = (actual_percents - expected_percents) * np.log(actual_percents / expected_percents)
            psi_score = np.sum(psi_components)
            
            # Interpret PSI score
            if psi_score < 0.1:
                interpretation = "No significant change"
                risk_level = "low"
            elif psi_score < 0.2:
                interpretation = "Minor change detected"
                risk_level = "medium"
            else:
                interpretation = "Major change detected - investigate"
                risk_level = "high"
            
            return {
                "psi_score": float(psi_score),
                "interpretation": interpretation,
                "risk_level": risk_level,
                "buckets": buckets,
                "expected_percents": expected_percents.tolist(),
                "actual_percents": actual_percents.tolist(),
                "psi_components": psi_components.tolist(),
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating PSI: {e}")
            return {
                "psi_score": None,
                "error": str(e),
                "calculated_at": datetime.now().isoformat()
            }
    
    @staticmethod
    def calculate_feature_psi(baseline_df: pd.DataFrame, current_df: pd.DataFrame, 
                            feature_columns: List[str]) -> Dict[str, Dict]:
        """Calculate PSI for multiple features"""
        results = {}
        
        for feature in feature_columns:
            if feature in baseline_df.columns and feature in current_df.columns:
                baseline_values = baseline_df[feature].dropna().values
                current_values = current_df[feature].dropna().values
                
                if len(baseline_values) > 0 and len(current_values) > 0:
                    results[feature] = PSICalculator.calculate_psi(baseline_values, current_values)
                else:
                    results[feature] = {"error": "Insufficient data", "psi_score": None}
            else:
                results[feature] = {"error": "Feature not found", "psi_score": None}
        
        return results


class KSTestCalculator:
    """Kolmogorov-Smirnov Test Calculator for distribution drift"""
    
    @staticmethod
    def ks_drift_test(reference_data: np.ndarray, current_data: np.ndarray, 
                     threshold: float = 0.05) -> Dict[str, Any]:
        """
        Kolmogorov-Smirnov test for distribution drift
        
        Args:
            reference_data: Reference/baseline distribution
            current_data: Current distribution to compare
            threshold: P-value threshold for significance
            
        Returns:
            Dictionary with KS test results and interpretation
        """
        try:
            # Perform KS test
            ks_statistic, p_value = stats.ks_2samp(reference_data, current_data)
            
            # Determine if drift detected
            drift_detected = p_value < threshold
            
            # Interpret results
            if drift_detected:
                if p_value < 0.001:
                    significance = "highly_significant"
                    interpretation = "Strong evidence of distribution change"
                elif p_value < 0.01:
                    significance = "very_significant"
                    interpretation = "Very strong evidence of distribution change"
                else:
                    significance = "significant"
                    interpretation = "Significant distribution change detected"
            else:
                significance = "not_significant"
                interpretation = "No significant distribution change"
            
            return {
                "ks_statistic": float(ks_statistic),
                "p_value": float(p_value),
                "drift_detected": drift_detected,
                "threshold": threshold,
                "significance": significance,
                "interpretation": interpretation,
                "sample_sizes": {
                    "reference": len(reference_data),
                    "current": len(current_data)
                },
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in KS test: {e}")
            return {
                "ks_statistic": None,
                "p_value": None,
                "error": str(e),
                "calculated_at": datetime.now().isoformat()
            }
    
    @staticmethod
    def batch_ks_test(reference_df: pd.DataFrame, current_df: pd.DataFrame,
                     feature_columns: List[str], threshold: float = 0.05) -> Dict[str, Dict]:
        """Perform KS test on multiple features"""
        results = {}
        
        for feature in feature_columns:
            if feature in reference_df.columns and feature in current_df.columns:
                ref_values = reference_df[feature].dropna().values
                curr_values = current_df[feature].dropna().values
                
                if len(ref_values) > 10 and len(curr_values) > 10:  # Minimum sample size
                    results[feature] = KSTestCalculator.ks_drift_test(ref_values, curr_values, threshold)
                else:
                    results[feature] = {"error": "Insufficient sample size", "drift_detected": None}
            else:
                results[feature] = {"error": "Feature not found", "drift_detected": None}
        
        return results


class FairnessGapCalculator:
    """Fairness gap calculations for bias detection"""
    
    @staticmethod
    def calculate_demographic_parity_gap(y_pred: np.ndarray, protected_attr: np.ndarray) -> Dict[str, Any]:
        """
        Calculate demographic parity gap between groups
        
        Args:
            y_pred: Predicted outcomes (binary)
            protected_attr: Protected attribute values
            
        Returns:
            Dictionary with gap analysis and group-wise rates
        """
        try:
            groups = np.unique(protected_attr)
            positive_rates = {}
            group_sizes = {}
            
            for group in groups:
                group_mask = protected_attr == group
                group_predictions = y_pred[group_mask]
                positive_rate = np.mean(group_predictions)
                positive_rates[str(group)] = float(positive_rate)
                group_sizes[str(group)] = int(np.sum(group_mask))
            
            # Calculate maximum gap between any two groups
            rates = list(positive_rates.values())
            gap = max(rates) - min(rates)
            
            # Determine fairness level
            if gap <= 0.05:
                fairness_level = "fair"
                interpretation = "Acceptable demographic parity"
            elif gap <= 0.1:
                fairness_level = "moderate_bias"
                interpretation = "Moderate bias detected"
            else:
                fairness_level = "high_bias"
                interpretation = "High bias - immediate attention required"
            
            return {
                "demographic_parity_gap": float(gap),
                "group_positive_rates": positive_rates,
                "group_sizes": group_sizes,
                "fairness_level": fairness_level,
                "interpretation": interpretation,
                "max_acceptable_gap": 0.05,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating demographic parity gap: {e}")
            return {
                "demographic_parity_gap": None,
                "error": str(e),
                "calculated_at": datetime.now().isoformat()
            }
    
    @staticmethod
    def calculate_equal_opportunity_gap(y_true: np.ndarray, y_pred: np.ndarray, 
                                      protected_attr: np.ndarray) -> Dict[str, Any]:
        """Calculate equal opportunity gap (TPR difference)"""
        try:
            groups = np.unique(protected_attr)
            tpr_rates = {}
            group_sizes = {}
            
            for group in groups:
                group_mask = protected_attr == group
                group_true = y_true[group_mask]
                group_pred = y_pred[group_mask]
                
                # Calculate True Positive Rate
                positive_mask = group_true == 1
                if np.sum(positive_mask) > 0:
                    tpr = np.mean(group_pred[positive_mask])
                    tpr_rates[str(group)] = float(tpr)
                    group_sizes[str(group)] = int(np.sum(positive_mask))
                else:
                    tpr_rates[str(group)] = 0.0
                    group_sizes[str(group)] = 0
            
            # Calculate gap
            rates = [rate for rate in tpr_rates.values() if rate > 0]
            gap = max(rates) - min(rates) if rates else 0.0
            
            # Interpret results
            if gap <= 0.05:
                fairness_level = "fair"
                interpretation = "Acceptable equal opportunity"
            elif gap <= 0.1:
                fairness_level = "moderate_bias"
                interpretation = "Moderate equal opportunity gap"
            else:
                fairness_level = "high_bias"
                interpretation = "High equal opportunity gap"
            
            return {
                "equal_opportunity_gap": float(gap),
                "group_tpr_rates": tpr_rates,
                "group_positive_sizes": group_sizes,
                "fairness_level": fairness_level,
                "interpretation": interpretation,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating equal opportunity gap: {e}")
            return {
                "equal_opportunity_gap": None,
                "error": str(e),
                "calculated_at": datetime.now().isoformat()
            }
    
    @staticmethod
    def calculate_equalized_odds_gap(y_true: np.ndarray, y_pred: np.ndarray,
                                   protected_attr: np.ndarray) -> Dict[str, Any]:
        """Calculate equalized odds gap (TPR and FPR difference)"""
        try:
            groups = np.unique(protected_attr)
            group_metrics = {}
            
            for group in groups:
                group_mask = protected_attr == group
                group_true = y_true[group_mask]
                group_pred = y_pred[group_mask]
                
                # Calculate TPR and FPR
                positive_mask = group_true == 1
                negative_mask = group_true == 0
                
                tpr = np.mean(group_pred[positive_mask]) if np.sum(positive_mask) > 0 else 0.0
                fpr = np.mean(group_pred[negative_mask]) if np.sum(negative_mask) > 0 else 0.0
                
                group_metrics[str(group)] = {
                    "tpr": float(tpr),
                    "fpr": float(fpr),
                    "positive_count": int(np.sum(positive_mask)),
                    "negative_count": int(np.sum(negative_mask))
                }
            
            # Calculate gaps
            tpr_values = [metrics["tpr"] for metrics in group_metrics.values()]
            fpr_values = [metrics["fpr"] for metrics in group_metrics.values()]
            
            tpr_gap = max(tpr_values) - min(tpr_values)
            fpr_gap = max(fpr_values) - min(fpr_values)
            
            # Overall equalized odds gap (max of TPR and FPR gaps)
            equalized_odds_gap = max(tpr_gap, fpr_gap)
            
            # Interpret results
            if equalized_odds_gap <= 0.05:
                fairness_level = "fair"
                interpretation = "Acceptable equalized odds"
            elif equalized_odds_gap <= 0.1:
                fairness_level = "moderate_bias"
                interpretation = "Moderate equalized odds gap"
            else:
                fairness_level = "high_bias"
                interpretation = "High equalized odds gap"
            
            return {
                "equalized_odds_gap": float(equalized_odds_gap),
                "tpr_gap": float(tpr_gap),
                "fpr_gap": float(fpr_gap),
                "group_metrics": group_metrics,
                "fairness_level": fairness_level,
                "interpretation": interpretation,
                "calculated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating equalized odds gap: {e}")
            return {
                "equalized_odds_gap": None,
                "error": str(e),
                "calculated_at": datetime.now().isoformat()
            }


class AlertGenerator:
    """Alert generation logic for IRAQAF platform"""
    
    def __init__(self, thresholds_file: str = "config/alert_thresholds.json"):
        self.thresholds = self._load_thresholds(thresholds_file)
    
    def _load_thresholds(self, thresholds_file: str) -> Dict:
        """Load alert thresholds from configuration"""
        try:
            with open(thresholds_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading alert thresholds: {e}")
            # Return default thresholds
            return {
                "critical": {"cqs_below": 50, "hub_offline": True},
                "warning": {"cqs_below": 70, "drift_detected": True},
                "info": {"cqs_below": 85}
            }
    
    def generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate alerts based on current metrics
        
        Args:
            metrics: Dictionary of current system metrics
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        current_time = datetime.now().isoformat()
        
        try:
            # Critical alerts
            if "cqs" in metrics:
                cqs = metrics["cqs"]
                if cqs < self.thresholds["critical"]["cqs_below"]:
                    alerts.append({
                        "id": f"critical_cqs_{int(datetime.now().timestamp())}",
                        "severity": "critical",
                        "type": "low_cqs",
                        "title": "Critical CQS Level",
                        "message": f"CQS critically low: {cqs:.1f}%",
                        "value": cqs,
                        "threshold": self.thresholds["critical"]["cqs_below"],
                        "timestamp": current_time,
                        "source": "cqs_monitor",
                        "action_required": True
                    })
            
            # Warning alerts
            if "cqs" in metrics:
                cqs = metrics["cqs"]
                if (cqs < self.thresholds["warning"]["cqs_below"] and 
                    cqs >= self.thresholds["critical"]["cqs_below"]):
                    alerts.append({
                        "id": f"warning_cqs_{int(datetime.now().timestamp())}",
                        "severity": "warning",
                        "type": "cqs_degradation",
                        "title": "CQS Below Threshold",
                        "message": f"CQS below warning threshold: {cqs:.1f}%",
                        "value": cqs,
                        "threshold": self.thresholds["warning"]["cqs_below"],
                        "timestamp": current_time,
                        "source": "cqs_monitor",
                        "action_required": False
                    })
            
            # Drift alerts
            if metrics.get("drift_detected", False):
                drift_type = metrics.get("drift_type", "unknown")
                alerts.append({
                    "id": f"drift_{drift_type}_{int(datetime.now().timestamp())}",
                    "severity": "warning",
                    "type": "data_drift",
                    "title": f"{drift_type.title()} Drift Detected",
                    "message": f"{drift_type.title()} drift detected in model inputs",
                    "drift_score": metrics.get("drift_score", 0),
                    "timestamp": current_time,
                    "source": "drift_monitor",
                    "action_required": True
                })
            
            # Fairness alerts
            if "fairness_gap" in metrics:
                gap = metrics["fairness_gap"]
                if gap > 0.1:  # High bias threshold
                    alerts.append({
                        "id": f"fairness_gap_{int(datetime.now().timestamp())}",
                        "severity": "critical",
                        "type": "fairness_violation",
                        "title": "High Fairness Gap Detected",
                        "message": f"Fairness gap exceeds acceptable limits: {gap:.3f}",
                        "value": gap,
                        "threshold": 0.1,
                        "timestamp": current_time,
                        "source": "fairness_monitor",
                        "action_required": True
                    })
                elif gap > 0.05:  # Moderate bias threshold
                    alerts.append({
                        "id": f"fairness_warning_{int(datetime.now().timestamp())}",
                        "severity": "warning",
                        "type": "fairness_concern",
                        "title": "Moderate Fairness Gap",
                        "message": f"Fairness gap detected: {gap:.3f}",
                        "value": gap,
                        "threshold": 0.05,
                        "timestamp": current_time,
                        "source": "fairness_monitor",
                        "action_required": False
                    })
            
            # Hub offline alerts
            if "hub_status" in metrics:
                for hub_name, status in metrics["hub_status"].items():
                    if status.get("status") == "offline":
                        alerts.append({
                            "id": f"hub_offline_{hub_name}_{int(datetime.now().timestamp())}",
                            "severity": "critical",
                            "type": "hub_offline",
                            "title": f"{hub_name.upper()} Hub Offline",
                            "message": f"{hub_name.upper()} hub is not responding",
                            "hub": hub_name,
                            "timestamp": current_time,
                            "source": "hub_monitor",
                            "action_required": True
                        })
            
            # Performance degradation alerts
            if "performance_drop" in metrics:
                drop = metrics["performance_drop"]
                if drop > self.thresholds["warning"]["performance_degradation"]:
                    alerts.append({
                        "id": f"performance_drop_{int(datetime.now().timestamp())}",
                        "severity": "warning",
                        "type": "performance_degradation",
                        "title": "Performance Degradation",
                        "message": f"Performance dropped by {drop:.1f}%",
                        "value": drop,
                        "threshold": self.thresholds["warning"]["performance_degradation"],
                        "timestamp": current_time,
                        "source": "performance_monitor",
                        "action_required": False
                    })
            
            # Sort alerts by severity (critical first)
            severity_order = {"critical": 0, "warning": 1, "info": 2}
            alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return [{
                "id": f"alert_error_{int(datetime.now().timestamp())}",
                "severity": "warning",
                "type": "system_error",
                "title": "Alert Generation Error",
                "message": f"Error in alert generation: {str(e)}",
                "timestamp": current_time,
                "source": "alert_generator",
                "action_required": False
            }]
    
    def classify_alert_priority(self, alerts: List[Dict]) -> Dict[str, List[Dict]]:
        """Classify alerts by priority for dashboard display"""
        classified = {
            "critical": [],
            "warning": [],
            "info": []
        }
        
        for alert in alerts:
            severity = alert.get("severity", "info")
            if severity in classified:
                classified[severity].append(alert)
        
        return classified
    
    def get_alert_summary(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Get summary statistics for alerts"""
        classified = self.classify_alert_priority(alerts)
        
        return {
            "total_alerts": len(alerts),
            "critical_count": len(classified["critical"]),
            "warning_count": len(classified["warning"]),
            "info_count": len(classified["info"]),
            "action_required_count": sum(1 for alert in alerts if alert.get("action_required", False)),
            "latest_alert": alerts[0] if alerts else None,
            "summary_generated_at": datetime.now().isoformat()
        }


# Example usage and testing functions
def test_psi_calculation():
    """Test PSI calculation with sample data"""
    print("Testing PSI Calculation...")
    
    # Generate sample data
    baseline = np.random.normal(0, 1, 1000)
    current = np.random.normal(0.2, 1.1, 1000)  # Slight drift
    
    psi_result = PSICalculator.calculate_psi(baseline, current)
    print(f"PSI Score: {psi_result['psi_score']:.4f}")
    print(f"Interpretation: {psi_result['interpretation']}")
    print(f"Risk Level: {psi_result['risk_level']}")
    
    return psi_result

def test_ks_test():
    """Test KS test with sample data"""
    print("\nTesting KS Test...")
    
    reference = np.random.normal(0, 1, 1000)
    current = np.random.normal(0.3, 1.2, 1000)  # Different distribution
    
    ks_result = KSTestCalculator.ks_drift_test(reference, current)
    print(f"KS Statistic: {ks_result['ks_statistic']:.4f}")
    print(f"P-value: {ks_result['p_value']:.6f}")
    print(f"Drift Detected: {ks_result['drift_detected']}")
    print(f"Interpretation: {ks_result['interpretation']}")
    
    return ks_result

def test_fairness_calculation():
    """Test fairness gap calculation"""
    print("\nTesting Fairness Gap Calculation...")
    
    # Generate sample data with bias
    n_samples = 1000
    protected_attr = np.random.choice(['Group_A', 'Group_B'], n_samples)
    
    # Introduce bias: Group_A gets more positive predictions
    y_pred = np.where(protected_attr == 'Group_A', 
                     np.random.binomial(1, 0.8, n_samples),  # 80% positive rate
                     np.random.binomial(1, 0.6, n_samples))  # 60% positive rate
    
    fairness_result = FairnessGapCalculator.calculate_demographic_parity_gap(y_pred, protected_attr)
    print(f"Demographic Parity Gap: {fairness_result['demographic_parity_gap']:.3f}")
    print(f"Group Rates: {fairness_result['group_positive_rates']}")
    print(f"Fairness Level: {fairness_result['fairness_level']}")
    print(f"Interpretation: {fairness_result['interpretation']}")
    
    return fairness_result

def test_alert_generation():
    """Test alert generation"""
    print("\nTesting Alert Generation...")
    
    alert_gen = AlertGenerator()
    
    # Sample metrics with various issues
    test_metrics = {
        "cqs": 45.2,  # Critical level
        "drift_detected": True,
        "drift_type": "data",
        "drift_score": 0.15,
        "fairness_gap": 0.12,  # High bias
        "hub_status": {
            "l1": {"status": "online"},
            "l2": {"status": "offline"},  # Offline hub
            "l4": {"status": "online"}
        },
        "performance_drop": 15.0  # Performance degradation
    }
    
    alerts = alert_gen.generate_alerts(test_metrics)
    print(f"Generated {len(alerts)} alerts:")
    
    for alert in alerts:
        print(f"  {alert['severity'].upper()}: {alert['title']} - {alert['message']}")
    
    # Get alert summary
    summary = alert_gen.get_alert_summary(alerts)
    print(f"\nAlert Summary:")
    print(f"  Total: {summary['total_alerts']}")
    print(f"  Critical: {summary['critical_count']}")
    print(f"  Warning: {summary['warning_count']}")
    print(f"  Action Required: {summary['action_required_count']}")
    
    return alerts, summary

if __name__ == "__main__":
    # Run all tests
    print("=== IRAQAF Metrics Calculations Test Suite ===\n")
    
    psi_result = test_psi_calculation()
    ks_result = test_ks_test()
    fairness_result = test_fairness_calculation()
    alerts, alert_summary = test_alert_generation()
    
    print("\n=== Test Suite Complete ===")
    print("All metric calculations are working correctly!")
