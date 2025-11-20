"""
L4 Explainability Hub Client

Fetches model interpretability metrics from the L4 Explainability Hub (port 5000).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .base_client import BaseHubClient


@dataclass
class ExplainabilitySnapshot:
    """Snapshot of explainability metrics from L4 Hub."""
    timestamp: str
    transparency_score: float  # 0-1
    shap_available: bool
    lime_available: bool
    gradcam_available: bool
    feature_importance: Dict[str, float]
    average_confidence: float
    model_version: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "transparency_score": self.transparency_score,
            "shap_available": self.shap_available,
            "lime_available": self.lime_available,
            "gradcam_available": self.gradcam_available,
            "feature_importance": self.feature_importance,
            "average_confidence": self.average_confidence,
            "model_version": self.model_version,
            "status": self.status,
        }


class L4ExplainabilityClient(BaseHubClient):
    """Client for L4 Explainability Hub (port 5000)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        """Initialize L4 client."""
        super().__init__(host, port)

    def get_transparency_score(self) -> ExplainabilitySnapshot:
        """Get overall transparency score and metrics."""
        try:
            data = self.get("/api/transparency-score")
            return ExplainabilitySnapshot(
                timestamp=data.get("timestamp", ""),
                transparency_score=data.get("transparency_score", 0),
                shap_available=data.get("shap_available", False),
                lime_available=data.get("lime_available", False),
                gradcam_available=data.get("gradcam_available", False),
                feature_importance=data.get("feature_importance", {}),
                average_confidence=data.get("average_confidence", 0),
                model_version=data.get("model_version", "unknown"),
                status=data.get("status", "unknown"),
            )
        except Exception as e:
            raise ValueError(f"Failed to get L4 transparency score: {str(e)}")

    def get_interpretability_details(self) -> Dict[str, Any]:
        """Get detailed interpretability analysis (SHAP, LIME, GradCAM)."""
        try:
            return self.get("/api/interpretability/all")
        except Exception as e:
            raise ValueError(
                f"Failed to get L4 interpretability details: {str(e)}")

    def get_model_performance(self) -> Dict[str, Any]:
        """Get model performance metrics."""
        try:
            return self.get("/api/performance")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}
