"""
L2 Privacy & Security Hub Client

Fetches security and privacy metrics from the L2 Privacy & Security Hub (port 8502).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .base_client import BaseHubClient


@dataclass
class SecuritySnapshot:
    """Snapshot of security metrics from L2 Hub."""
    timestamp: str
    sai_score: float  # Security Assessment Index (0-1)
    anonymization_score: float
    model_security_score: float
    access_control_score: float
    data_minimization_score: float
    encryption_score: float
    pii_detection_risk: float
    vulnerability_count: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "sai_score": self.sai_score,
            "anonymization_score": self.anonymization_score,
            "model_security_score": self.model_security_score,
            "access_control_score": self.access_control_score,
            "data_minimization_score": self.data_minimization_score,
            "encryption_score": self.encryption_score,
            "pii_detection_risk": self.pii_detection_risk,
            "vulnerability_count": self.vulnerability_count,
            "status": self.status,
        }


class L2SecurityClient(BaseHubClient):
    """Client for L2 Privacy & Security Hub (port 8502)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8502):
        """Initialize L2 client."""
        super().__init__(host, port)

    def get_sai_score(self) -> SecuritySnapshot:
        """Get Security Assessment Index (SAI) and module scores."""
        try:
            data = self.get("/api/sai")
            return SecuritySnapshot(
                timestamp=data.get("timestamp", ""),
                sai_score=data.get("sai_score", 0),
                anonymization_score=data.get("anonymization_score", 0),
                model_security_score=data.get("model_security_score", 0),
                access_control_score=data.get("access_control_score", 0),
                data_minimization_score=data.get("data_minimization_score", 0),
                encryption_score=data.get("encryption_score", 0),
                pii_detection_risk=data.get("pii_detection_risk", 0),
                vulnerability_count=data.get("vulnerability_count", 0),
                status=data.get("status", "unknown"),
            )
        except Exception as e:
            raise ValueError(f"Failed to get L2 SAI score: {str(e)}")

    def get_module_details(self, module_name: str) -> Dict[str, Any]:
        """Get detailed metrics for a specific security module."""
        try:
            return self.get(f"/api/module/{module_name}")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_all_modules(self) -> Dict[str, Any]:
        """Get all security module assessments."""
        try:
            return self.get("/api/all-modules")
        except Exception as e:
            return {"status": "unavailable", "modules": [], "error": str(e)}

    def get_pii_detected(self) -> Dict[str, Any]:
        """Get PII detection results."""
        try:
            return self.get("/api/pii-detection")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_vulnerabilities(self) -> Dict[str, Any]:
        """Get identified vulnerabilities."""
        try:
            return self.get("/api/vulnerabilities")
        except Exception as e:
            return {"vulnerabilities": [], "error": str(e)}
