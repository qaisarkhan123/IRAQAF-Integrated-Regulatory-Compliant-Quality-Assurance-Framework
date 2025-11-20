"""
Module 5 Core Client
Polls Module 5 Core (port 8508) for internal metrics, drift analysis, and alerts

This client enables Module 5 Hub to integrate Core-level deep monitoring
with hub-level orchestration for unified Continuous QA Score (CQS).
"""

import requests
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CoreMetrics:
    """Module 5 Core internal metrics snapshot"""
    timestamp: str
    internal_cqs: float  # 0-100
    performance_score: float
    fairness_score: float
    security_score: float
    compliance_score: float
    system_health_score: float
    is_healthy: bool
    error_message: Optional[str] = None


@dataclass
class DriftAnalysis:
    """Drift detection analysis"""
    timestamp: str
    # Population Stability Index (0.0 = stable, >0.25 = significant drift)
    psi_input: float
    # K-S test (0.0 = identical, 1.0 = completely different)
    ks_statistic: float
    ece_score: float  # Expected Calibration Error (0.0 = perfect, 1.0 = worst)
    concept_drift_detected: bool
    performance_trend: str  # "stable", "improving", "degrading"


@dataclass
class FairnessMetrics:
    """Fairness drift metrics"""
    timestamp: str
    demographic_parity_gap: float  # Percentage difference in selection rates
    equalized_odds_gap: float  # Maximum difference in TPR/FPR
    fairness_score: float  # Overall fairness (0-100)
    groups_analyzed: int
    bias_detected: bool
    action_recommended: Optional[str] = None


@dataclass
class Alert:
    """Alert from Module 5 Core"""
    alert_id: str
    timestamp: str
    severity: str  # "CRITICAL", "WARNING", "INFO"
    category: str  # "DRIFT", "FAIRNESS", "SECURITY", "COMPLIANCE"
    message: str
    recommended_action: Optional[str] = None


class Module5CoreClient:
    """HTTP client for Module 5 Core (port 8508)"""

    def __init__(self, base_url: str = "http://127.0.0.1:8508", timeout: int = 5):
        """
        Initialize Core client

        Args:
            base_url: Module 5 Core base URL
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.last_error = None

    def get_internal_cqs(self) -> Optional[CoreMetrics]:
        """
        Get Module 5 Core's internal Continuous QA Score

        Returns:
            CoreMetrics object with CQS breakdown, or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/internal-cqs",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return CoreMetrics(
                timestamp=data.get('timestamp', datetime.now().isoformat()),
                internal_cqs=float(data.get('overall_cqs', 0)),
                performance_score=float(
                    data.get('categories', {}).get('performance', 0)),
                fairness_score=float(
                    data.get('categories', {}).get('fairness', 0)),
                security_score=float(
                    data.get('categories', {}).get('security_privacy', 0)),
                compliance_score=float(
                    data.get('categories', {}).get('compliance', 0)),
                system_health_score=float(
                    data.get('categories', {}).get('system_health', 0)),
                is_healthy=True
            )
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error fetching internal CQS: {e}")
            return CoreMetrics(
                timestamp=datetime.now().isoformat(),
                internal_cqs=0,
                performance_score=0,
                fairness_score=0,
                security_score=0,
                compliance_score=0,
                system_health_score=0,
                is_healthy=False,
                error_message=str(e)
            )

    def get_drift_analysis(self) -> Optional[DriftAnalysis]:
        """
        Get performance drift analysis (PSI, KS, ECE)

        Returns:
            DriftAnalysis object, or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/drift/performance",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return DriftAnalysis(
                timestamp=data.get('timestamp', datetime.now().isoformat()),
                psi_input=float(data.get('psi_input', 0)),
                ks_statistic=float(data.get('ks_statistic', 0)),
                ece_score=float(data.get('ece_score', 0)),
                concept_drift_detected=data.get(
                    'concept_drift_detected', False),
                performance_trend=data.get('trend', 'stable')
            )
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error fetching drift analysis: {e}")
            return None

    def get_fairness_metrics(self) -> Optional[FairnessMetrics]:
        """
        Get fairness drift metrics

        Returns:
            FairnessMetrics object, or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/drift/fairness",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return FairnessMetrics(
                timestamp=data.get('timestamp', datetime.now().isoformat()),
                demographic_parity_gap=float(
                    data.get('demographic_parity_gap', 0)),
                equalized_odds_gap=float(data.get('equalized_odds_gap', 0)),
                fairness_score=float(data.get('fairness_score', 0)),
                groups_analyzed=int(data.get('groups_analyzed', 0)),
                bias_detected=data.get('bias_detected', False),
                action_recommended=data.get('action_recommended')
            )
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error fetching fairness metrics: {e}")
            return None

    def get_security_anomalies(self) -> Optional[Dict]:
        """
        Get security & privacy anomaly detection results

        Returns:
            Dictionary with security metrics, or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/security/anomalies",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error fetching security anomalies: {e}")
            return None

    def get_compliance_drift(self) -> Optional[Dict]:
        """
        Get compliance drift detection results

        Returns:
            Dictionary with compliance metrics, or None if error
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/compliance/drift",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error fetching compliance drift: {e}")
            return None

    def get_active_alerts(self) -> List[Alert]:
        """
        Get all active alerts from Module 5 Core

        Returns:
            List of Alert objects
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/alerts",
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            alerts = []
            for alert_data in data.get('active_alerts', []):
                alerts.append(Alert(
                    alert_id=alert_data.get('alert_id', ''),
                    timestamp=alert_data.get(
                        'timestamp', datetime.now().isoformat()),
                    severity=alert_data.get('severity', 'INFO'),
                    category=alert_data.get('category', 'OTHER'),
                    message=alert_data.get('message', ''),
                    recommended_action=alert_data.get('recommended_action')
                ))
            return alerts
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error fetching alerts: {e}")
            return []

    def is_healthy(self) -> bool:
        """Check if Module 5 Core is responding"""
        try:
            response = requests.get(
                f"{self.base_url}/api/internal-cqs",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception:
            return False
