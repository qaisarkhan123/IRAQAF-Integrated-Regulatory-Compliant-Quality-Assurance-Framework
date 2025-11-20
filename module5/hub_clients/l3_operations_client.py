"""
L3 Operations Center Hub Client

Fetches operational and system health metrics from the L3 Operations Center (port 8503).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from .base_client import BaseHubClient


@dataclass
class OperationsSnapshot:
    """Snapshot of operational metrics from L3 Hub."""
    timestamp: str
    system_health_score: float  # 0-1
    uptime_percentage: float
    average_response_time_ms: float
    throughput_requests_per_min: float
    error_rate: float
    active_deployments: int
    critical_alerts: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "system_health_score": self.system_health_score,
            "uptime_percentage": self.uptime_percentage,
            "average_response_time_ms": self.average_response_time_ms,
            "throughput_requests_per_min": self.throughput_requests_per_min,
            "error_rate": self.error_rate,
            "active_deployments": self.active_deployments,
            "critical_alerts": self.critical_alerts,
            "status": self.status,
        }


class L3OperationsClient(BaseHubClient):
    """Client for L3 Operations Center Hub (port 8503)."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8503):
        """Initialize L3 Operations client."""
        super().__init__(host, port)

    def get_system_health(self) -> OperationsSnapshot:
        """Get overall system health score."""
        try:
            data = self.get("/api/health")
            return OperationsSnapshot(
                timestamp=data.get("timestamp", ""),
                system_health_score=data.get("system_health_score", 0),
                uptime_percentage=data.get("uptime_percentage", 0),
                average_response_time_ms=data.get(
                    "average_response_time_ms", 0),
                throughput_requests_per_min=data.get(
                    "throughput_requests_per_min", 0),
                error_rate=data.get("error_rate", 0),
                active_deployments=data.get("active_deployments", 0),
                critical_alerts=data.get("critical_alerts", 0),
                status=data.get("status", "unknown"),
            )
        except Exception as e:
            raise ValueError(f"Failed to get L3 system health: {str(e)}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics (latency, throughput, etc)."""
        try:
            return self.get("/api/performance")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

    def get_active_alerts(self) -> Dict[str, Any]:
        """Get active operational alerts."""
        try:
            return self.get("/api/alerts")
        except Exception as e:
            return {"alerts": [], "error": str(e)}

    def get_sla_status(self) -> Dict[str, Any]:
        """Get SLA compliance status."""
        try:
            return self.get("/api/sla")
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}
