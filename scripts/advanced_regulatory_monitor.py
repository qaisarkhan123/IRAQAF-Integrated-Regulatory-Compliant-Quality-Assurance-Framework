"""
Advanced Regulatory Monitoring Module
Provides real-time regulatory change tracking, compliance trend analysis, 
automated risk alerts, and regulatory impact assessment capabilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Enumeration of regulatory risk levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceStatus(Enum):
    """Enumeration of compliance statuses."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"


@dataclass
class RegulatoryChange:
    """Data class representing a regulatory change event."""
    change_id: str
    timestamp: str
    source: str
    regulation_id: str
    regulation_name: str
    change_type: str
    description: str
    impact_level: str
    affected_systems: List[str]
    implementation_deadline: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ComplianceTrend:
    """Data class representing compliance trend data."""
    metric_name: str
    timestamp: str
    compliance_score: float
    trend_direction: str  # "improving", "declining", "stable"
    velocity: float  # rate of change
    forecast_7d: float  # 7-day forecast
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RegulatoryAlert:
    """Data class representing an automated regulatory alert."""
    alert_id: str
    timestamp: str
    risk_level: str
    alert_type: str
    affected_regulation: str
    message: str
    recommended_action: str
    status: str = "open"  # open, acknowledged, resolved
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class RegulatoryChangeTracker:
    """Tracks and manages regulatory changes in real-time."""
    
    def __init__(self):
        """Initialize the tracker."""
        self.changes: List[RegulatoryChange] = []
        self.change_hash_cache: Dict[str, str] = {}
        self.subscriptions: Dict[str, List[callable]] = {}
        
    def add_change(self, 
                   source: str,
                   regulation_id: str,
                   regulation_name: str,
                   change_type: str,
                   description: str,
                   impact_level: str,
                   affected_systems: List[str],
                   implementation_deadline: Optional[str] = None) -> RegulatoryChange:
        """Add a new regulatory change to tracking."""
        timestamp = datetime.utcnow().isoformat()
        change_id = self._generate_change_id(regulation_id, description, timestamp)
        
        change = RegulatoryChange(
            change_id=change_id,
            timestamp=timestamp,
            source=source,
            regulation_id=regulation_id,
            regulation_name=regulation_name,
            change_type=change_type,
            description=description,
            impact_level=impact_level,
            affected_systems=affected_systems,
            implementation_deadline=implementation_deadline
        )
        
        self.changes.append(change)
        self._notify_subscribers("change_detected", change)
        logger.info(f"New regulatory change tracked: {regulation_name} ({change_id})")
        return change
    
    def get_changes_by_date_range(self, 
                                  start_date: str, 
                                  end_date: str) -> List[RegulatoryChange]:
        """Retrieve changes within a date range."""
        changes = []
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        for change in self.changes:
            change_dt = datetime.fromisoformat(change.timestamp)
            if start_dt <= change_dt <= end_dt:
                changes.append(change)
        
        return sorted(changes, key=lambda x: x.timestamp, reverse=True)
    
    def get_changes_by_impact_level(self, impact_level: str) -> List[RegulatoryChange]:
        """Filter changes by impact level."""
        return [c for c in self.changes if c.impact_level.lower() == impact_level.lower()]
    
    def get_critical_changes(self) -> List[RegulatoryChange]:
        """Get all critical regulatory changes."""
        return self.get_changes_by_impact_level("critical")
    
    def subscribe(self, event_type: str, callback: callable):
        """Subscribe to regulatory change events."""
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        self.subscriptions[event_type].append(callback)
    
    def _notify_subscribers(self, event_type: str, data: Any):
        """Notify all subscribers of an event."""
        if event_type in self.subscriptions:
            for callback in self.subscriptions[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in subscriber callback: {e}")
    
    def _generate_change_id(self, reg_id: str, description: str, timestamp: str) -> str:
        """Generate unique change ID."""
        content = f"{reg_id}:{description}:{timestamp}".encode()
        return hashlib.sha256(content).hexdigest()[:12]


class ComplianceTrendAnalyzer:
    """Analyzes compliance trends and patterns."""
    
    def __init__(self, window_size: int = 30):
        """Initialize analyzer with trend window size (days)."""
        self.trends: List[ComplianceTrend] = []
        self.window_size = window_size
        self.historical_scores: List[Tuple[str, float]] = []
    
    def record_compliance_score(self, 
                               metric_name: str, 
                               compliance_score: float,
                               affected_systems: Optional[List[str]] = None) -> ComplianceTrend:
        """Record a compliance score and analyze trend."""
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate trend direction
        trend_direction = self._calculate_trend_direction(metric_name, compliance_score)
        
        # Calculate velocity (rate of change)
        velocity = self._calculate_velocity(metric_name, compliance_score)
        
        # Forecast 7-day compliance
        forecast_7d = self._forecast_compliance_7d(metric_name, compliance_score)
        
        trend = ComplianceTrend(
            metric_name=metric_name,
            timestamp=timestamp,
            compliance_score=compliance_score,
            trend_direction=trend_direction,
            velocity=velocity,
            forecast_7d=forecast_7d
        )
        
        self.trends.append(trend)
        self.historical_scores.append((metric_name, compliance_score))
        
        logger.info(f"Compliance trend recorded for {metric_name}: {compliance_score}% "
                   f"(trend: {trend_direction}, velocity: {velocity:.2f})")
        
        return trend
    
    def get_trend_analysis(self, metric_name: str) -> Dict[str, Any]:
        """Get comprehensive trend analysis for a metric."""
        metric_trends = [t for t in self.trends if t.metric_name == metric_name]
        
        if not metric_trends:
            return {"error": f"No trends found for {metric_name}"}
        
        scores = [t.compliance_score for t in metric_trends]
        timestamps = [t.timestamp for t in metric_trends]
        
        return {
            "metric_name": metric_name,
            "current_score": metric_trends[-1].compliance_score if metric_trends else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "trend_direction": metric_trends[-1].trend_direction if metric_trends else "unknown",
            "velocity": metric_trends[-1].velocity if metric_trends else 0,
            "forecast_7d": metric_trends[-1].forecast_7d if metric_trends else 0,
            "total_records": len(metric_trends),
            "latest_timestamp": timestamps[-1] if timestamps else None
        }
    
    def get_all_trends(self) -> List[Dict[str, Any]]:
        """Get trend analysis for all metrics."""
        metrics = set(t.metric_name for t in self.trends)
        return [self.get_trend_analysis(m) for m in metrics]
    
    def _calculate_trend_direction(self, metric_name: str, current_score: float) -> str:
        """Calculate trend direction based on historical scores."""
        metric_scores = [s for m, s in self.historical_scores if m == metric_name]
        
        if len(metric_scores) < 2:
            return "stable"
        
        recent = metric_scores[-5:] if len(metric_scores) >= 5 else metric_scores
        avg_recent = sum(recent) / len(recent)
        
        if current_score > avg_recent + 2:
            return "improving"
        elif current_score < avg_recent - 2:
            return "declining"
        else:
            return "stable"
    
    def _calculate_velocity(self, metric_name: str, current_score: float) -> float:
        """Calculate rate of change in compliance score."""
        metric_scores = [s for m, s in self.historical_scores if m == metric_name]
        
        if len(metric_scores) < 2:
            return 0.0
        
        previous_score = metric_scores[-1]
        return current_score - previous_score
    
    def _forecast_compliance_7d(self, metric_name: str, current_score: float) -> float:
        """Forecast compliance score for next 7 days."""
        metric_scores = [s for m, s in self.historical_scores if m == metric_name]
        
        if len(metric_scores) < 2:
            return current_score
        
        # Simple linear extrapolation
        velocity = self._calculate_velocity(metric_name, current_score)
        forecast = current_score + (velocity * 7)
        
        # Bound between 0 and 100
        return max(0, min(100, forecast))


class AutomatedAlertGenerator:
    """Generates automated alerts for regulatory and compliance issues."""
    
    def __init__(self):
        """Initialize the alert generator."""
        self.alerts: List[RegulatoryAlert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = self._initialize_alert_rules()
    
    def generate_alert(self,
                      alert_type: str,
                      affected_regulation: str,
                      message: str,
                      recommended_action: str,
                      risk_level: str = "medium") -> RegulatoryAlert:
        """Generate a new regulatory alert."""
        timestamp = datetime.utcnow().isoformat()
        alert_id = self._generate_alert_id(affected_regulation, message, timestamp)
        
        alert = RegulatoryAlert(
            alert_id=alert_id,
            timestamp=timestamp,
            risk_level=risk_level,
            alert_type=alert_type,
            affected_regulation=affected_regulation,
            message=message,
            recommended_action=recommended_action,
            status="open"
        )
        
        self.alerts.append(alert)
        logger.warning(f"Alert generated [{risk_level}]: {alert_type} - {message}")
        return alert
    
    def check_compliance_threshold(self,
                                   metric_name: str,
                                   current_score: float,
                                   threshold: float = 80.0) -> Optional[RegulatoryAlert]:
        """Check if compliance score falls below threshold and generate alert if needed."""
        if current_score < threshold:
            return self.generate_alert(
                alert_type="compliance_threshold_breach",
                affected_regulation=metric_name,
                message=f"{metric_name} compliance score ({current_score:.1f}%) below threshold ({threshold:.1f}%)",
                recommended_action="Immediate action required to address compliance gaps",
                risk_level="high" if current_score < threshold * 0.8 else "medium"
            )
        return None
    
    def check_deadline_approaching(self,
                                   regulation_name: str,
                                   deadline: str,
                                   days_warning: int = 30) -> Optional[RegulatoryAlert]:
        """Check if implementation deadline is approaching and generate alert if needed."""
        try:
            deadline_dt = datetime.fromisoformat(deadline)
            current_dt = datetime.utcnow()
            days_until = (deadline_dt - current_dt).days
            
            if 0 <= days_until <= days_warning:
                return self.generate_alert(
                    alert_type="deadline_approaching",
                    affected_regulation=regulation_name,
                    message=f"Implementation deadline for {regulation_name} is in {days_until} days",
                    recommended_action="Finalize implementation and begin testing",
                    risk_level="critical" if days_until <= 7 else "high"
                )
            elif days_until < 0:
                return self.generate_alert(
                    alert_type="deadline_missed",
                    affected_regulation=regulation_name,
                    message=f"Implementation deadline for {regulation_name} was {abs(days_until)} days ago",
                    recommended_action="Escalate to management and create remediation plan",
                    risk_level="critical"
                )
        except (ValueError, TypeError) as e:
            logger.error(f"Error checking deadline: {e}")
        
        return None
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = "acknowledged"
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.status = "resolved"
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_open_alerts(self) -> List[RegulatoryAlert]:
        """Get all open alerts."""
        return [a for a in self.alerts if a.status == "open"]
    
    def get_critical_alerts(self) -> List[RegulatoryAlert]:
        """Get all critical-level alerts."""
        return [a for a in self.alerts if a.risk_level.lower() == "critical"]
    
    def get_alerts_by_regulation(self, regulation_name: str) -> List[RegulatoryAlert]:
        """Get alerts for a specific regulation."""
        return [a for a in self.alerts if regulation_name.lower() in a.affected_regulation.lower()]
    
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert rules engine."""
        return {
            "compliance_threshold": {"threshold": 80.0, "enabled": True},
            "deadline_approaching": {"days_warning": 30, "enabled": True},
            "frequency_anomaly": {"threshold": 2.5, "enabled": True},
            "pattern_change": {"enabled": True},
        }
    
    def _generate_alert_id(self, regulation: str, message: str, timestamp: str) -> str:
        """Generate unique alert ID."""
        content = f"{regulation}:{message}:{timestamp}".encode()
        return hashlib.sha256(content).hexdigest()[:12]


class RegulatoryImpactAssessor:
    """Assesses the impact of regulatory changes on compliance."""
    
    def __init__(self):
        """Initialize the assessor."""
        self.impact_assessments: List[Dict[str, Any]] = []
        self.system_mappings: Dict[str, List[str]] = {}
    
    def assess_regulatory_change(self,
                                regulation_id: str,
                                regulation_name: str,
                                affected_systems: List[str],
                                change_description: str,
                                current_compliance_status: str) -> Dict[str, Any]:
        """Assess the impact of a regulatory change."""
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate impact score (1-10)
        impact_score = self._calculate_impact_score(affected_systems, regulation_name)
        
        # Identify remediation requirements
        remediation_items = self._identify_remediation_items(
            regulation_name, affected_systems, change_description
        )
        
        # Estimate effort required
        effort_estimate = self._estimate_remediation_effort(remediation_items)
        
        assessment = {
            "assessment_id": self._generate_assessment_id(regulation_id, timestamp),
            "timestamp": timestamp,
            "regulation_id": regulation_id,
            "regulation_name": regulation_name,
            "affected_systems": affected_systems,
            "impact_score": impact_score,  # 1-10
            "current_compliance_status": current_compliance_status,
            "remediation_items": remediation_items,
            "effort_estimate_hours": effort_estimate,
            "priority_level": self._determine_priority(impact_score),
            "recommended_timeline_days": self._calculate_timeline(effort_estimate)
        }
        
        self.impact_assessments.append(assessment)
        logger.info(f"Impact assessment created for {regulation_name}: "
                   f"score={impact_score}/10, effort={effort_estimate}h")
        
        return assessment
    
    def get_impact_by_system(self, system_name: str) -> List[Dict[str, Any]]:
        """Get all impact assessments for a specific system."""
        return [a for a in self.impact_assessments 
                if system_name in a.get("affected_systems", [])]
    
    def get_high_priority_assessments(self) -> List[Dict[str, Any]]:
        """Get all high-priority impact assessments."""
        return [a for a in self.impact_assessments if a["priority_level"] in ["high", "critical"]]
    
    def _calculate_impact_score(self, affected_systems: List[str], regulation_name: str) -> int:
        """Calculate impact score based on affected systems and regulation criticality."""
        base_score = min(len(affected_systems), 5)
        
        # Boost score for known critical regulations
        critical_keywords = ["security", "privacy", "financial", "healthcare"]
        if any(keyword in regulation_name.lower() for keyword in critical_keywords):
            base_score += 2
        
        return min(base_score, 10)
    
    def _identify_remediation_items(self,
                                   regulation_name: str,
                                   affected_systems: List[str],
                                   description: str) -> List[Dict[str, str]]:
        """Identify remediation items needed."""
        items = []
        
        # Add configuration updates
        if affected_systems:
            items.append({
                "item": "Update system configurations",
                "systems": affected_systems,
                "type": "configuration"
            })
        
        # Add testing requirements
        items.append({
            "item": "Validate compliance with new requirements",
            "systems": affected_systems,
            "type": "testing"
        })
        
        # Add documentation updates
        items.append({
            "item": "Update regulatory compliance documentation",
            "systems": affected_systems,
            "type": "documentation"
        })
        
        return items
    
    def _estimate_remediation_effort(self, remediation_items: List[Dict[str, str]]) -> int:
        """Estimate effort required in hours."""
        # Base estimate: 4 hours per item
        return len(remediation_items) * 4
    
    def _determine_priority(self, impact_score: int) -> str:
        """Determine priority level based on impact score."""
        if impact_score >= 8:
            return "critical"
        elif impact_score >= 6:
            return "high"
        elif impact_score >= 4:
            return "medium"
        else:
            return "low"
    
    def _calculate_timeline(self, effort_hours: int) -> int:
        """Calculate recommended timeline in days based on effort."""
        # Assume 8 hours per day
        days = (effort_hours + 7) // 8
        return max(days, 1)
    
    def _generate_assessment_id(self, regulation_id: str, timestamp: str) -> str:
        """Generate unique assessment ID."""
        content = f"{regulation_id}:{timestamp}".encode()
        return hashlib.sha256(content).hexdigest()[:12]


# Module-level instances for convenience
_change_tracker = RegulatoryChangeTracker()
_trend_analyzer = ComplianceTrendAnalyzer()
_alert_generator = AutomatedAlertGenerator()
_impact_assessor = RegulatoryImpactAssessor()


# Module-level wrapper functions for compatibility
def add_regulatory_change(source: str,
                         regulation_id: str,
                         regulation_name: str,
                         change_type: str,
                         description: str,
                         impact_level: str,
                         affected_systems: List[str],
                         implementation_deadline: Optional[str] = None) -> Dict[str, Any]:
    """Wrapper function to add regulatory change."""
    change = _change_tracker.add_change(
        source, regulation_id, regulation_name, change_type,
        description, impact_level, affected_systems, implementation_deadline
    )
    return change.to_dict()


def record_compliance_trend(metric_name: str, 
                           compliance_score: float) -> Dict[str, Any]:
    """Wrapper function to record compliance trend."""
    trend = _trend_analyzer.record_compliance_score(metric_name, compliance_score)
    return trend.to_dict()


def generate_compliance_alert(alert_type: str,
                             affected_regulation: str,
                             message: str,
                             recommended_action: str,
                             risk_level: str = "medium") -> Dict[str, Any]:
    """Wrapper function to generate alert."""
    alert = _alert_generator.generate_alert(
        alert_type, affected_regulation, message, recommended_action, risk_level
    )
    return alert.to_dict()


def assess_regulatory_impact(regulation_id: str,
                            regulation_name: str,
                            affected_systems: List[str],
                            change_description: str,
                            current_compliance_status: str) -> Dict[str, Any]:
    """Wrapper function to assess regulatory impact."""
    return _impact_assessor.assess_regulatory_change(
        regulation_id, regulation_name, affected_systems,
        change_description, current_compliance_status
    )


def get_all_critical_changes() -> List[Dict[str, Any]]:
    """Get all critical regulatory changes."""
    return [c.to_dict() for c in _change_tracker.get_critical_changes()]


def get_all_open_alerts() -> List[Dict[str, Any]]:
    """Get all open alerts."""
    return [a.to_dict() for a in _alert_generator.get_open_alerts()]


def get_trend_analysis_for_metric(metric_name: str) -> Dict[str, Any]:
    """Get trend analysis for a specific metric."""
    return _trend_analyzer.get_trend_analysis(metric_name)


def get_high_priority_assessments() -> List[Dict[str, Any]]:
    """Get all high-priority impact assessments."""
    return _impact_assessor.get_high_priority_assessments()
