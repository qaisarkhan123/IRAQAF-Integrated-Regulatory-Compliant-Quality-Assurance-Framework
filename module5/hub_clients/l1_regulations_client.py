"""
L1 Regulations & Governance Hub Client

Fetches compliance and regulatory metrics from the L1 Regulations Hub (port 8504).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .base_client import BaseHubClient


@dataclass
class ComplianceSnapshot:
    """Snapshot of compliance metrics from L1 Hub."""
    timestamp: str
    overall_score: float  # 0-1
    gdpr_score: float
    eu_ai_act_score: float
    iso_13485_score: float
    iec_62304_score: float
    fda_score: float
    compliance_gaps: int
    critical_issues: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "overall_score": self.overall_score,
            "gdpr_score": self.gdpr_score,
            "eu_ai_act_score": self.eu_ai_act_score,
            "iso_13485_score": self.iso_13485_score,
            "iec_62304_score": self.iec_62304_score,
            "fda_score": self.fda_score,
            "compliance_gaps": self.compliance_gaps,
            "critical_issues": self.critical_issues,
            "status": self.status,
        }


class L1RegulationsClient(BaseHubClient):
    """Client for L1 Regulations & Governance Hub (port 8504)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8504):
        """Initialize L1 client."""
        super().__init__(host, port)

    def get_compliance_score(self) -> ComplianceSnapshot:
        """Get overall compliance score."""
        try:
            data = self.get("/api/score")
            return ComplianceSnapshot(
                timestamp=data.get("timestamp", ""),
                overall_score=data.get("overall_score", 0),
                gdpr_score=data.get("gdpr_score", 0),
                eu_ai_act_score=data.get("eu_ai_act_score", 0),
                iso_13485_score=data.get("iso_13485_score", 0),
                iec_62304_score=data.get("iec_62304_score", 0),
                fda_score=data.get("fda_score", 0),
                compliance_gaps=data.get("compliance_gaps", 0),
                critical_issues=data.get("critical_issues", 0),
                status=data.get("status", "unknown"),
            )
        except Exception as e:
            raise ValueError(f"Failed to get L1 compliance score: {str(e)}")

    def get_framework_details(self, framework: str) -> Dict[str, Any]:
        """Get detailed compliance for a specific framework (gdpr, eu_ai_act, etc)."""
        try:
            return self.get(f"/api/framework/{framework}")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_gaps(self) -> Dict[str, Any]:
        """Get compliance gaps and recommendations."""
        try:
            return self.get("/api/gaps")
        except Exception as e:
            return {"gaps": [], "error": str(e)}

    def get_requirements(self) -> Dict[str, Any]:
        """Get regulatory requirements tracking."""
        try:
            return self.get("/api/requirements")
        except Exception as e:
            return {"requirements": [], "error": str(e)}
