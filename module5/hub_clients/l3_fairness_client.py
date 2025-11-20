"""
L3 Fairness & Ethics Hub Client

Fetches fairness and bias metrics from the L3 Fairness & Ethics Hub (port 8506).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .base_client import BaseHubClient


@dataclass
class FairnessSnapshot:
    """Snapshot of fairness metrics from L3 Fairness Hub."""
    timestamp: str
    overall_fairness_score: float  # 0-1
    demographic_parity_gap: float
    equalized_odds_gap: float
    calibration_score: float
    governance_score: float
    bias_detected: bool
    at_risk_subgroups: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "overall_fairness_score": self.overall_fairness_score,
            "demographic_parity_gap": self.demographic_parity_gap,
            "equalized_odds_gap": self.equalized_odds_gap,
            "calibration_score": self.calibration_score,
            "governance_score": self.governance_score,
            "bias_detected": self.bias_detected,
            "at_risk_subgroups": self.at_risk_subgroups,
            "status": self.status,
        }


class L3FairnessClient(BaseHubClient):
    """Client for L3 Fairness & Ethics Hub (port 8506)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8506):
        """Initialize L3 Fairness client."""
        super().__init__(host, port)

    def get_fairness_score(self) -> FairnessSnapshot:
        """Get overall fairness score and bias metrics."""
        try:
            # Get FI and detailed metrics
            fi_data = self.get("/api/fi")
            metrics_data = self.get("/api/fairness-metrics")
            eml_data = self.get("/api/eml")
            
            fairness_index_pct = fi_data.get("fairness_index", 0.0)
            fairness_index = fairness_index_pct / 100.0  # Convert to 0-1 scale
            
            # Extract gaps from metrics
            all_attrs = metrics_data.get("attributes", {})
            max_dpg = 0.0
            max_eod_gap = 0.0
            
            for attr, scores in all_attrs.items():
                raw_metrics = scores.get("raw_metrics", {})
                max_dpg = max(max_dpg, raw_metrics.get("demographic_parity_gap", 0.0))
                max_eod_gap = max(max_eod_gap, raw_metrics.get("equalized_odds_gap", 0.0))
            
            eml_score_pct = eml_data.get("score", 0.0)
            governance_score = eml_score_pct / 100.0  # Convert to 0-1 scale
            
            bias_detected = max_dpg > 0.1 or max_eod_gap > 0.1
            at_risk_count = len([a for a in all_attrs.values() if a.get("fairness_score", 100) < 70])
            status = "healthy" if fairness_index > 0.7 else "warning"
            
            return FairnessSnapshot(
                timestamp=fi_data.get("timestamp", ""),
                overall_fairness_score=fairness_index,
                demographic_parity_gap=max_dpg,
                equalized_odds_gap=max_eod_gap,
                calibration_score=fairness_index,  # Use FI as proxy for now
                governance_score=governance_score,
                bias_detected=bias_detected,
                at_risk_subgroups=at_risk_count,
                status=status,
            )
        except Exception as e:
            raise ValueError(f"Failed to get L3 fairness score: {str(e)}")

    def get_bias_analysis(self) -> Dict[str, Any]:
        """Get detailed bias analysis by subgroup."""
        try:
            return self.get("/api/bias-analysis")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_subgroup_metrics(self, subgroup: str) -> Dict[str, Any]:
        """Get fairness metrics for a specific subgroup."""
        try:
            return self.get(f"/api/subgroup/{subgroup}")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_governance_status(self) -> Dict[str, Any]:
        """Get governance and ethics review status."""
        try:
            return self.get("/api/governance")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}
