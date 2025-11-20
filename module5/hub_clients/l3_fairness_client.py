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
            data = self.get("/api/fairness-score")
            return FairnessSnapshot(
                timestamp=data.get("timestamp", ""),
                overall_fairness_score=data.get("overall_fairness_score", 0),
                demographic_parity_gap=data.get("demographic_parity_gap", 0),
                equalized_odds_gap=data.get("equalized_odds_gap", 0),
                calibration_score=data.get("calibration_score", 0),
                governance_score=data.get("governance_score", 0),
                bias_detected=data.get("bias_detected", False),
                at_risk_subgroups=data.get("at_risk_subgroups", 0),
                status=data.get("status", "unknown"),
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
