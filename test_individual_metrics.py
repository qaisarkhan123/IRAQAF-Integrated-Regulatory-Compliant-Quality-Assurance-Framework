#!/usr/bin/env python3
"""
Individual Advanced Metrics Testing
Test each metric calculation separately
"""

from dashboard.metrics_calculations import PSICalculator, KSTestCalculator, FairnessGapCalculator, AlertGenerator
import numpy as np

def test_psi():
    print("🔍 Testing PSI Calculation...")
    baseline = np.random.normal(0, 1, 1000)
    current = np.random.normal(0.1, 1.05, 1000)  # Slight drift
    
    result = PSICalculator.calculate_psi(baseline, current)
    print(f"   PSI Score: {result['psi_score']:.4f}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Interpretation: {result['interpretation']}")
    return result

def test_ks():
    print("\n📊 Testing KS Test...")
    reference = np.random.normal(0, 1, 1000)
    current = np.random.normal(0.3, 1.2, 1000)  # Different distribution
    
    result = KSTestCalculator.ks_drift_test(reference, current)
    print(f"   KS Statistic: {result['ks_statistic']:.4f}")
    print(f"   P-value: {result['p_value']:.6f}")
    print(f"   Drift Detected: {result['drift_detected']}")
    print(f"   Interpretation: {result['interpretation']}")
    return result

def test_fairness():
    print("\n⚖️ Testing Fairness Gap Calculation...")
    n_samples = 1000
    protected_attr = np.random.choice(['Group_A', 'Group_B'], n_samples)
    
    # Introduce bias: Group_A gets more positive predictions
    y_pred = np.where(protected_attr == 'Group_A', 
                     np.random.binomial(1, 0.8, n_samples),  # 80% positive rate
                     np.random.binomial(1, 0.6, n_samples))  # 60% positive rate
    
    result = FairnessGapCalculator.calculate_demographic_parity_gap(y_pred, protected_attr)
    print(f"   Demographic Parity Gap: {result['demographic_parity_gap']:.3f}")
    print(f"   Group Rates: {result['group_positive_rates']}")
    print(f"   Fairness Level: {result['fairness_level']}")
    print(f"   Interpretation: {result['interpretation']}")
    return result

def test_alerts():
    print("\n🚨 Testing Alert Generation...")
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
    print(f"   Generated {len(alerts)} alerts:")
    
    for alert in alerts:
        print(f"     {alert['severity'].upper()}: {alert['title']} - {alert['message']}")
    
    # Get alert summary
    summary = alert_gen.get_alert_summary(alerts)
    print(f"\n   Alert Summary:")
    print(f"     Total: {summary['total_alerts']}")
    print(f"     Critical: {summary['critical_count']}")
    print(f"     Warning: {summary['warning_count']}")
    print(f"     Action Required: {summary['action_required_count']}")
    
    return alerts, summary

if __name__ == "__main__":
    print("IRAQAF Advanced Metrics - Individual Testing")
    print("=" * 50)
    
    psi_result = test_psi()
    ks_result = test_ks()
    fairness_result = test_fairness()
    alerts, alert_summary = test_alerts()
    
    print("\n✅ All individual metric tests completed successfully!")
    print("\n📋 Summary:")
    print(f"   PSI: {psi_result['risk_level']} risk")
    print(f"   KS Test: {'Drift detected' if ks_result['drift_detected'] else 'No drift'}")
    print(f"   Fairness: {fairness_result['fairness_level']}")
    print(f"   Alerts: {alert_summary['total_alerts']} generated")
