"""
Module 5 Orchestrator - Core Engine

The Continuous QA Automation & Monitoring orchestrator that:
1. Polls all 5 hubs on a scheduled interval
2. Aggregates metrics into unified data models
3. Detects cross-hub anomalies and risks
4. Generates the Continuous QA Score (CQS)
5. Serves as the control tower for compliance
"""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from module5.hub_clients import (
    L4ExplainabilityClient,
    L2SecurityClient,
    L1RegulationsClient,
    L3OperationsClient,
    L3FairnessClient,
)


logger = logging.getLogger(__name__)


@dataclass
class HubStatus:
    """Status of a single hub."""
    hub_name: str
    is_healthy: bool
    last_update: str
    response_time_ms: float
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContinuousQAScore:
    """
    Master Continuous QA Score aggregating all 5 hubs.

    CQS = weighted average of:
    - L4 Explainability Score (20%)
    - L2 Security Score (25%)
    - L1 Compliance Score (25%)
    - L3 Operations Score (15%)
    - L3 Fairness Score (15%)
    """
    timestamp: str
    overall_cqs: float  # 0-1

    # Individual hub contributions
    l4_explainability_score: float
    l2_security_score: float
    l1_compliance_score: float
    l3_operations_score: float
    l3_fairness_score: float

    # Risk indicators
    critical_issues: int
    warnings: int

    # Hub status
    hub_statuses: List[Dict[str, Any]]

    # Alerts
    alerts: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Module5Orchestrator:
    """
    Orchestrator for Module 5: Continuous QA Automation & Monitoring.

    Pulls data from all 5 hubs, aggregates metrics, detects anomalies,
    and produces unified QA scoring.
    """

    def __init__(self, polling_interval_seconds: int = 30):
        """
        Initialize orchestrator with hub clients.

        Args:
            polling_interval_seconds: How often to poll hubs (default 30s)
        """
        self.polling_interval = polling_interval_seconds

        # Initialize hub clients
        self.l4_client = L4ExplainabilityClient()
        self.l2_client = L2SecurityClient()
        self.l1_client = L1RegulationsClient()
        self.l3_ops_client = L3OperationsClient()
        self.l3_fairness_client = L3FairnessClient()

        # Store latest snapshots
        self.latest_data: Dict[str, Any] = {}
        self.hub_statuses: Dict[str, HubStatus] = {}
        self.latest_cqs: Optional[ContinuousQAScore] = None

        logger.info("Module 5 Orchestrator initialized")

    def poll_all_hubs(self) -> ContinuousQAScore:
        """
        Poll all 5 hubs and generate unified QA score.

        Returns:
            ContinuousQAScore aggregating all hub data
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        alerts = []
        critical_issues = 0
        warning_count = 0

        # Poll L4 Explainability Hub
        l4_score = self._poll_l4_hub()
        if l4_score is None:
            l4_score = 0
            alerts.append("⚠️ L4 Explainability Hub unreachable")
            critical_issues += 1
        else:
            logger.info(f"L4 Transparency Score: {l4_score:.1%}")

        # Poll L2 Security Hub
        l2_score = self._poll_l2_hub()
        if l2_score is None:
            l2_score = 0
            alerts.append("⚠️ L2 Security Hub unreachable")
            critical_issues += 1
        else:
            logger.info(f"L2 Security Score: {l2_score:.1%}")
            if l2_score < 0.70:
                alerts.append("🔴 L2 Security score below 70%")
                warning_count += 1

        # Poll L1 Regulations Hub
        l1_score = self._poll_l1_hub()
        if l1_score is None:
            l1_score = 0
            alerts.append("⚠️ L1 Regulations Hub unreachable")
            critical_issues += 1
        else:
            logger.info(f"L1 Compliance Score: {l1_score:.1%}")
            if l1_score < 0.75:
                alerts.append("🟡 L1 Compliance score below 75%")
                warning_count += 1

        # Poll L3 Operations Hub
        l3_ops_score = self._poll_l3_operations_hub()
        if l3_ops_score is None:
            l3_ops_score = 0
            alerts.append("⚠️ L3 Operations Hub unreachable")
            critical_issues += 1
        else:
            logger.info(f"L3 Operations Score: {l3_ops_score:.1%}")
            if l3_ops_score < 0.80:
                alerts.append("🟡 L3 Operations score below 80%")
                warning_count += 1

        # Poll L3 Fairness Hub
        l3_fairness_score = self._poll_l3_fairness_hub()
        if l3_fairness_score is None:
            l3_fairness_score = 0
            alerts.append("⚠️ L3 Fairness Hub unreachable")
            critical_issues += 1
        else:
            logger.info(f"L3 Fairness Score: {l3_fairness_score:.1%}")
            if l3_fairness_score < 0.70:
                alerts.append("🟡 L3 Fairness score below 70%")
                warning_count += 1

        # Calculate weighted CQS
        cqs_weights = {
            "l4": 0.20,
            "l2": 0.25,
            "l1": 0.25,
            "l3_ops": 0.15,
            "l3_fairness": 0.15,
        }

        overall_cqs = (
            l4_score * cqs_weights["l4"]
            + l2_score * cqs_weights["l2"]
            + l1_score * cqs_weights["l1"]
            + l3_ops_score * cqs_weights["l3_ops"]
            + l3_fairness_score * cqs_weights["l3_fairness"]
        )

        # Generate CQS object
        cqs = ContinuousQAScore(
            timestamp=timestamp,
            overall_cqs=overall_cqs,
            l4_explainability_score=l4_score,
            l2_security_score=l2_score,
            l1_compliance_score=l1_score,
            l3_operations_score=l3_ops_score,
            l3_fairness_score=l3_fairness_score,
            critical_issues=critical_issues,
            warnings=warning_count,
            hub_statuses=[s.to_dict() for s in self.hub_statuses.values()],
            alerts=alerts,
        )

        self.latest_cqs = cqs
        logger.info(f"📊 Continuous QA Score: {overall_cqs:.1%}")
        return cqs

    def _poll_l4_hub(self) -> Optional[float]:
        """Poll L4 Explainability Hub."""
        try:
            start = time.time()
            snapshot = self.l4_client.get_transparency_score()
            elapsed_ms = (time.time() - start) * 1000

            self.hub_statuses["L4"] = HubStatus(
                hub_name="L4 Explainability",
                is_healthy=True,
                last_update=snapshot.timestamp,
                response_time_ms=elapsed_ms,
            )
            self.latest_data["l4"] = snapshot
            return snapshot.transparency_score
        except Exception as e:
            logger.error(f"L4 poll error: {e}")
            self.hub_statuses["L4"] = HubStatus(
                hub_name="L4 Explainability",
                is_healthy=False,
                last_update=datetime.now(timezone.utc).isoformat(),
                response_time_ms=0,
                error_message=str(e),
            )
            return None

    def _poll_l2_hub(self) -> Optional[float]:
        """Poll L2 Security Hub."""
        try:
            start = time.time()
            snapshot = self.l2_client.get_sai_score()
            elapsed_ms = (time.time() - start) * 1000

            self.hub_statuses["L2"] = HubStatus(
                hub_name="L2 Security",
                is_healthy=True,
                last_update=snapshot.timestamp,
                response_time_ms=elapsed_ms,
            )
            self.latest_data["l2"] = snapshot
            return snapshot.sai_score
        except Exception as e:
            logger.error(f"L2 poll error: {e}")
            self.hub_statuses["L2"] = HubStatus(
                hub_name="L2 Security",
                is_healthy=False,
                last_update=datetime.now(timezone.utc).isoformat(),
                response_time_ms=0,
                error_message=str(e),
            )
            return None

    def _poll_l1_hub(self) -> Optional[float]:
        """Poll L1 Regulations Hub."""
        try:
            start = time.time()
            snapshot = self.l1_client.get_compliance_score()
            elapsed_ms = (time.time() - start) * 1000

            self.hub_statuses["L1"] = HubStatus(
                hub_name="L1 Regulations",
                is_healthy=True,
                last_update=snapshot.timestamp,
                response_time_ms=elapsed_ms,
            )
            self.latest_data["l1"] = snapshot
            return snapshot.overall_score
        except Exception as e:
            logger.error(f"L1 poll error: {e}")
            self.hub_statuses["L1"] = HubStatus(
                hub_name="L1 Regulations",
                is_healthy=False,
                last_update=datetime.now(timezone.utc).isoformat(),
                response_time_ms=0,
                error_message=str(e),
            )
            return None

    def _poll_l3_operations_hub(self) -> Optional[float]:
        """Poll L3 Operations Center Hub."""
        try:
            start = time.time()
            snapshot = self.l3_ops_client.get_system_health()
            elapsed_ms = (time.time() - start) * 1000

            self.hub_statuses["L3_OPS"] = HubStatus(
                hub_name="L3 Operations",
                is_healthy=True,
                last_update=snapshot.timestamp,
                response_time_ms=elapsed_ms,
            )
            self.latest_data["l3_ops"] = snapshot
            return snapshot.system_health_score
        except Exception as e:
            logger.error(f"L3 Operations poll error: {e}")
            self.hub_statuses["L3_OPS"] = HubStatus(
                hub_name="L3 Operations",
                is_healthy=False,
                last_update=datetime.now(timezone.utc).isoformat(),
                response_time_ms=0,
                error_message=str(e),
            )
            return None

    def _poll_l3_fairness_hub(self) -> Optional[float]:
        """Poll L3 Fairness & Ethics Hub."""
        try:
            start = time.time()
            snapshot = self.l3_fairness_client.get_fairness_score()
            elapsed_ms = (time.time() - start) * 1000

            self.hub_statuses["L3_FAIRNESS"] = HubStatus(
                hub_name="L3 Fairness",
                is_healthy=True,
                last_update=snapshot.timestamp,
                response_time_ms=elapsed_ms,
            )
            self.latest_data["l3_fairness"] = snapshot
            return snapshot.overall_fairness_score
        except Exception as e:
            logger.error(f"L3 Fairness poll error: {e}")
            self.hub_statuses["L3_FAIRNESS"] = HubStatus(
                hub_name="L3 Fairness",
                is_healthy=False,
                last_update=datetime.now(timezone.utc).isoformat(),
                response_time_ms=0,
                error_message=str(e),
            )
            return None

    def get_system_overview(self) -> Dict[str, Any]:
        """Get complete system overview for dashboard."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cqs": self.latest_cqs.to_dict() if self.latest_cqs else None,
            "hub_statuses": [s.to_dict() for s in self.hub_statuses.values()],
            "latest_data": {k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in self.latest_data.items()},
        }
