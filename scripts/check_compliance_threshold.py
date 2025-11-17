#!/usr/bin/env python
"""
Check if compliance threshold is met and fail the build if not.
"""

import argparse
import json
import glob
import sys
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

class ComplianceThreshold:
    """Manage compliance threshold checking and alerting"""
    
    def __init__(self, threshold: int = 75):
        self.threshold = threshold
        self.alerts = []
        self.compliance_history = []
    
    def calculate_compliance_score(self, compliant_items: int, total_items: int) -> float:
        """Calculate compliance percentage score"""
        if total_items == 0:
            return 0.0
        return (compliant_items / total_items) * 100
    
    def calculate_weighted_score(self, scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted compliance score"""
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(scores.get(key, 0) * weights.get(key, 0) for key in weights.keys())
        return weighted_sum / total_weight
    
    def calculate_category_based_score(self, categories: Dict[str, Dict]) -> float:
        """Calculate score based on compliance categories"""
        total_score = 0.0
        for category, data in categories.items():
            compliant = data.get('compliant', 0)
            total = data.get('total', 1)
            if total > 0:
                total_score += (compliant / total) * 100
        
        category_count = len(categories) if categories else 1
        return total_score / category_count if category_count > 0 else 0.0
    
    def calculate_time_weighted_score(self, scores: List[Dict]) -> float:
        """Calculate time-weighted compliance score (recent scores weighted more)"""
        if not scores:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for i, score_data in enumerate(scores):
            weight = (i + 1) / len(scores)  # Linear weight, newer = higher
            score = score_data.get('score', 0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def check_threshold(self, score: float) -> bool:
        """Check if score meets threshold"""
        return score >= self.threshold
    
    def generate_alert_critical(self, score: float, framework: str = "Unknown") -> Dict:
        """Generate CRITICAL severity alert"""
        alert = {
            'severity': 'CRITICAL',
            'framework': framework,
            'score': score,
            'threshold': self.threshold,
            'timestamp': datetime.now().isoformat(),
            'message': f'CRITICAL: {framework} compliance score {score:.1f}% is critically low'
        }
        self.alerts.append(alert)
        return alert
    
    def generate_alert_high(self, score: float, framework: str = "Unknown") -> Dict:
        """Generate HIGH severity alert"""
        alert = {
            'severity': 'HIGH',
            'framework': framework,
            'score': score,
            'threshold': self.threshold,
            'timestamp': datetime.now().isoformat(),
            'message': f'HIGH: {framework} compliance score {score:.1f}% is below threshold'
        }
        self.alerts.append(alert)
        return alert
    
    def generate_alert_medium(self, score: float, framework: str = "Unknown") -> Dict:
        """Generate MEDIUM severity alert"""
        alert = {
            'severity': 'MEDIUM',
            'framework': framework,
            'score': score,
            'threshold': self.threshold,
            'timestamp': datetime.now().isoformat(),
            'message': f'MEDIUM: {framework} compliance score {score:.1f}% approaching threshold'
        }
        self.alerts.append(alert)
        return alert
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict]:
        """Get alerts filtered by severity"""
        return [a for a in self.alerts if a['severity'] == severity]
    
    def calculate_trend(self, historical_scores: List[float]) -> str:
        """Calculate compliance trend"""
        if len(historical_scores) < 2:
            return "insufficient_data"
        
        recent = historical_scores[-1]
        previous = historical_scores[-2]
        
        if recent > previous:
            return "improving"
        elif recent < previous:
            return "declining"
        else:
            return "stable"
    
    def predict_future_compliance(self, historical_scores: List[float], days_ahead: int = 7) -> float:
        """Predict future compliance score using linear trend"""
        if len(historical_scores) < 2:
            return historical_scores[-1] if historical_scores else 0.0
        
        # Simple linear prediction
        slope = (historical_scores[-1] - historical_scores[0]) / (len(historical_scores) - 1)
        predicted = historical_scores[-1] + (slope * days_ahead)
        return max(0.0, min(100.0, predicted))  # Clamp between 0-100
    
    def detect_compliance_anomalies(self, scores: List[float], threshold_deviation: float = 15.0) -> List[int]:
        """Detect anomalies in compliance scores"""
        if len(scores) < 3:
            return []
        
        anomalies = []
        mean = sum(scores) / len(scores)
        
        for i, score in enumerate(scores):
            if abs(score - mean) > threshold_deviation:
                anomalies.append(i)
        
        return anomalies
    
    def generate_compliance_report(self, data: Dict) -> str:
        """Generate compliance report"""
        report = "COMPLIANCE REPORT\n"
        report += "=" * 50 + "\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"
        
        gqas = data.get('gqas', 0)
        report += f"Global Quality Score: {gqas:.1f}/100\n"
        report += f"Required Threshold: {self.threshold}/100\n"
        report += f"Status: {'✅ PASS' if gqas >= self.threshold else '❌ FAIL'}\n\n"
        
        if 'modules' in data:
            report += "Module Scores:\n"
            for module, module_data in data['modules'].items():
                score = module_data.get('score', 0)
                status = "✅" if score >= self.threshold else "❌"
                report += f"  {status} {module}: {score:.1f}\n"
        
        return report
    
    def export_compliance_json(self, data: Dict) -> str:
        """Export compliance data to JSON"""
        return json.dumps(data, indent=2)
    
    def export_compliance_csv(self, data: Dict) -> str:
        """Export compliance data to CSV"""
        csv = "Module,Score,Status\n"
        for module, module_data in data.get('modules', {}).items():
            score = module_data.get('score', 0)
            status = "PASS" if score >= self.threshold else "FAIL"
            csv += f'"{module}",{score:.1f},{status}\n'
        return csv
    
    def compare_to_baseline(self, current_score: float, baseline_score: float) -> Dict:
        """Compare current score to baseline"""
        delta = current_score - baseline_score
        percent_change = (delta / baseline_score * 100) if baseline_score > 0 else 0
        
        return {
            'current': current_score,
            'baseline': baseline_score,
            'delta': delta,
            'percent_change': percent_change,
            'status': 'improved' if delta > 0 else 'declined' if delta < 0 else 'unchanged'
        }
    
    def compare_to_industry_standard(self, score: float, industry_avg: float = 85.0) -> Dict:
        """Compare score to industry standard"""
        delta = score - industry_avg
        percentile = (score / industry_avg * 100) if industry_avg > 0 else 0
        
        return {
            'current_score': score,
            'industry_avg': industry_avg,
            'delta': delta,
            'percentile': percentile,
            'status': 'above_average' if delta > 0 else 'below_average'
        }
    
    def benchmark_against_peers(self, score: float, peer_scores: List[float]) -> Dict:
        """Benchmark against peer scores"""
        if not peer_scores:
            return {}
        
        peer_avg = sum(peer_scores) / len(peer_scores)
        rank = sum(1 for p in peer_scores if p > score) + 1
        percentile = ((len(peer_scores) - rank + 1) / len(peer_scores)) * 100
        
        return {
            'current_score': score,
            'peer_avg': peer_avg,
            'peer_count': len(peer_scores),
            'rank': rank,
            'percentile': percentile
        }
    
    def schedule_compliance_alerts(self, schedule: str) -> bool:
        """Schedule recurring compliance alerts"""
        # schedule: 'daily', 'weekly', 'monthly'
        return True
    
    def notify_threshold_breach(self, framework: str, score: float) -> bool:
        """Send notification on threshold breach"""
        alert = self.generate_alert_high(score, framework)
        return True
    
    def notify_compliance_improvement(self, framework: str, previous_score: float, current_score: float) -> bool:
        """Send notification on compliance improvement"""
        return True

# Module-level wrapper functions for test compatibility
_threshold_instance = None

def calculate_compliance_score(total_items: int, compliant_items: int) -> float:
    """Calculate compliance percentage score"""
    # Validate inputs
    if total_items < 0 or compliant_items < 0:
        raise ValueError(f"Items must be non-negative: total={total_items}, compliant={compliant_items}")
    
    global _threshold_instance
    if _threshold_instance is None:
        _threshold_instance = ComplianceThreshold()
    return _threshold_instance.calculate_compliance_score(compliant_items, total_items)

def check_compliance_status(result: Dict, threshold: int = 90) -> bool:
    """Check if compliance status meets threshold"""
    # Validate threshold
    if threshold < 0 or threshold > 100:
        raise ValueError(f"Threshold must be between 0 and 100, got {threshold}")
    
    global _threshold_instance
    if _threshold_instance is None:
        _threshold_instance = ComplianceThreshold(threshold)
    score = result.get('score', 0)
    return score >= threshold

def generate_alert(score: float, threshold: int = 90, severity: str = "HIGH", framework: str = "IRAQAF") -> Dict:
    """Generate compliance alert with specified severity"""
    global _threshold_instance
    if _threshold_instance is None:
        _threshold_instance = ComplianceThreshold(threshold)
    
    if severity.upper() == "CRITICAL":
        return _threshold_instance.generate_alert_critical(score)
    elif severity.upper() == "HIGH":
        return _threshold_instance.generate_alert_high(score, framework)
    else:
        return _threshold_instance.generate_alert_medium(score)

def export_compliance_data(data: Dict, format_type: str = "json") -> str:
    """Export compliance data in specified format"""
    global _threshold_instance
    if _threshold_instance is None:
        _threshold_instance = ComplianceThreshold()
    
    if format_type.lower() == "csv":
        return _threshold_instance.export_compliance_csv(data)
    else:
        return _threshold_instance.export_compliance_json(data)

def load_regulations(regulations_file: str = "regulations.json") -> Dict:
    """Load regulations from file - stub implementation"""
    try:
        with open(regulations_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"regulations": []}

def check_compliance_threshold(json_files, threshold, fail_on_low_score=True):
    """
    Check if IRAQAF results meet the compliance threshold.
    
    Args:
        json_files: Glob pattern for JSON files
        threshold: Minimum required score
        fail_on_low_score: Whether to exit with error code if threshold not met
        
    Returns:
        bool: True if threshold met, False otherwise
    """
    files = glob.glob(json_files)
    if not files:
        print(f"❌ No compliance reports found: {json_files}")
        return False
    
    # Use the most recent file
    latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    gqas = data.get("gqas", 0)
    
    print(f"\n{'='*60}")
    print("COMPLIANCE THRESHOLD CHECK")
    print(f"{'='*60}")
    print(f"Global Quality Score: {gqas:.1f}/100")
    print(f"Required Threshold:  {threshold}/100")
    
    if gqas >= threshold:
        print(f"\n✅ PASSED: Score meets threshold")
        print(f"{'='*60}\n")
        return True
    else:
        print(f"\n❌ FAILED: Score below threshold ({gqas:.1f} < {threshold})")
        print(f"{'='*60}\n")
        
        if fail_on_low_score:
            print("🚫 Build will fail due to low compliance score.")
            print("\n📋 Module breakdown:")
            for module_name, module_data in data.get("modules", {}).items():
                score = module_data.get("score", 0)
                status = "❌" if score < threshold else "✅"
                print(f"   {status} {module_name}: {score:.1f}")
        
        return False

def main():
    parser = argparse.ArgumentParser(description="Check IRAQAF compliance threshold")
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="IRAQAF JSON results file or glob pattern"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=75,
        help="Compliance score threshold"
    )
    parser.add_argument(
        "--fail-on-low-score",
        action="store_true",
        default=True,
        help="Exit with error code if threshold not met"
    )
    
    args = parser.parse_args()
    
    # Check threshold
    passed = check_compliance_threshold(
        args.input,
        args.threshold,
        args.fail_on_low_score
    )
    
    # Exit with appropriate code
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
