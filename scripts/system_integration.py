"""
System Integration Coordinator

Coordinates all modules into a cohesive workflow. Manages communication
between regulatory monitoring, compliance checking, database persistence,
and real-time monitoring services.

Usage:
    from scripts.system_integration import SystemCoordinator
    
    coordinator = SystemCoordinator(db_url="sqlite:///compliance.db")
    coordinator.initialize()
    coordinator.start_monitoring()
    
    # Use through coordinator
    coordinator.track_regulatory_change(...)
    coordinator.record_compliance_score(...)
    coordinator.get_system_status()
"""

import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class SystemCoordinator:
    """
    Central coordinator managing all system components.
    
    Provides unified interface to:
    - Regulatory monitoring
    - Compliance checking
    - Database persistence
    - Real-time monitoring
    - Alert management
    - Remediation tracking
    """

    def __init__(
        self,
        db_url: str = "sqlite:///compliance.db",
        monitor_interval: int = 60,
    ):
        """
        Initialize system coordinator.
        
        Args:
            db_url: Database connection URL
            monitor_interval: Seconds between monitoring checks
        """
        self.db_url = db_url
        self.monitor_interval = monitor_interval
        self.initialized = False
        self.monitoring = False

        # Import modules
        self.database = None
        self.api = None
        self.monitor = None

        logger.info(f"SystemCoordinator initialized with DB: {db_url}")

    def initialize(self) -> None:
        """Initialize all system components."""
        try:
            # Initialize database
            logger.info("Initializing database layer...")
            from scripts.database_layer import init_db, DatabaseQueries

            init_db(self.db_url)
            self.db_queries = DatabaseQueries()

            # Initialize regulatory API
            logger.info("Initializing regulatory features API...")
            try:
                from scripts.regulatory_features_api import get_api

                self.api = get_api()
            except ImportError:
                logger.warning("Could not import regulatory_features_api")
                self.api = None

            # Initialize real-time monitor
            logger.info("Initializing real-time monitor...")
            from scripts.realtime_monitor import initialize_monitor

            self.monitor = initialize_monitor(
                update_interval=self.monitor_interval,
                api_provider=lambda: self.api,
            )

            self.initialized = True
            logger.info("System coordinator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize system coordinator: {e}")
            raise

    def start_monitoring(self) -> None:
        """Start real-time monitoring service."""
        if not self.initialized:
            raise RuntimeError("System coordinator not initialized. Call initialize() first.")

        if self.monitoring:
            logger.warning("Monitoring already running")
            return

        self.monitor.start()
        self.monitoring = True
        logger.info("Monitoring started")

    def stop_monitoring(self) -> None:
        """Stop real-time monitoring service."""
        if self.monitor and self.monitoring:
            self.monitor.stop()
            self.monitoring = False
            logger.info("Monitoring stopped")

    # ========================================================================
    # Regulatory Change Management
    # ========================================================================

    def track_regulatory_change(
        self,
        source: str,
        regulation_id: str,
        regulation_name: str,
        change_type: str,
        description: str,
        impact_level: str,
        affected_systems: Optional[List[str]] = None,
        implementation_deadline: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Track a new regulatory change.
        
        Saves to database and triggers through API and monitoring.
        """
        try:
            # Save to database
            change = self.db_queries.save_regulatory_change(
                source=source,
                regulation_id=regulation_id,
                regulation_name=regulation_name,
                change_type=change_type,
                description=description,
                impact_level=impact_level,
                affected_systems=affected_systems,
                implementation_deadline=implementation_deadline,
            )

            # Track through API if available
            if self.api:
                self.api.track_regulatory_change(
                    source=source,
                    regulation_id=regulation_id,
                    regulation_name=regulation_name,
                    change_type=change_type,
                    description=description,
                    impact_level=impact_level,
                    affected_systems=affected_systems,
                    implementation_deadline=implementation_deadline,
                )

            logger.info(f"Tracked regulatory change: {regulation_id}")
            return change.to_dict()

        except Exception as e:
            logger.error(f"Error tracking regulatory change: {e}")
            raise

    def get_recent_changes(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent regulatory changes."""
        try:
            changes = self.db_queries.get_recent_changes(days=days)
            return [c.to_dict() for c in changes]
        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")
            return []

    def get_critical_changes(self) -> List[Dict[str, Any]]:
        """Get critical regulatory changes."""
        try:
            changes = self.db_queries.get_critical_changes()
            return [c.to_dict() for c in changes]
        except Exception as e:
            logger.error(f"Error getting critical changes: {e}")
            return []

    # ========================================================================
    # Compliance Score Management
    # ========================================================================

    def record_compliance_score(
        self,
        framework: str,
        system_name: str,
        score: float,
        status: str = "compliant",
    ) -> Dict[str, Any]:
        """
        Record a compliance score.
        
        Saves to database and triggers monitoring updates.
        """
        try:
            # Save to database
            record = self.db_queries.save_compliance_score(
                framework=framework,
                system_name=system_name,
                score=score,
                status=status,
            )

            # Record through API if available
            if self.api:
                self.api.record_compliance_score(framework, score)

            logger.info(f"Recorded compliance score: {framework} = {score}%")
            return record.to_dict()

        except Exception as e:
            logger.error(f"Error recording compliance score: {e}")
            raise

    def get_compliance_scores(
        self,
        framework: str,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get compliance scores for a framework."""
        try:
            scores = self.db_queries.get_compliance_scores(framework, days)
            return [s.to_dict() for s in scores]
        except Exception as e:
            logger.error(f"Error getting compliance scores: {e}")
            return []

    # ========================================================================
    # Alert Management
    # ========================================================================

    def generate_alert(
        self,
        alert_type: str,
        message: str,
        risk_level: str,
        affected_regulation: Optional[str] = None,
        recommended_action: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a compliance alert.
        
        Saves to database and triggers monitoring notifications.
        """
        try:
            # Save to database
            alert = self.db_queries.save_alert(
                alert_type=alert_type,
                message=message,
                risk_level=risk_level,
                affected_regulation=affected_regulation,
                recommended_action=recommended_action,
            )

            # Generate through API if available
            if self.api:
                self.api.generate_alert(
                    alert_type=alert_type,
                    affected_regulation=affected_regulation or "",
                    message=message,
                    recommended_action=recommended_action or "",
                    risk_level=risk_level,
                )

            logger.info(f"Generated alert: {alert_type} - {risk_level}")
            return alert.to_dict()

        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            raise

    def get_open_alerts(self) -> List[Dict[str, Any]]:
        """Get all open alerts."""
        try:
            alerts = self.db_queries.get_open_alerts()
            return [a.to_dict() for a in alerts]
        except Exception as e:
            logger.error(f"Error getting open alerts: {e}")
            return []

    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get all critical-level alerts."""
        try:
            alerts = self.db_queries.get_critical_alerts()
            return [a.to_dict() for a in alerts]
        except Exception as e:
            logger.error(f"Error getting critical alerts: {e}")
            return []

    def acknowledge_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Acknowledge an alert."""
        try:
            alert = self.db_queries.update_alert_status(alert_id, "acknowledged")
            return alert.to_dict() if alert else None
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return None

    def resolve_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Mark an alert as resolved."""
        try:
            alert = self.db_queries.update_alert_status(alert_id, "resolved")
            return alert.to_dict() if alert else None
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return None

    # ========================================================================
    # Remediation Management
    # ========================================================================

    def create_remediation_action(
        self,
        gap_id: str,
        action_title: str,
        description: str,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: int = 0,
    ) -> Dict[str, Any]:
        """
        Create a remediation action.
        
        Saves to database and tracks progress.
        """
        try:
            action = self.db_queries.save_remediation_action(
                gap_id=gap_id,
                action_title=action_title,
                description=description,
                assigned_to=assigned_to,
                due_date=due_date,
                priority=priority,
            )

            logger.info(f"Created remediation action: {action_title}")
            return action.to_dict()

        except Exception as e:
            logger.error(f"Error creating remediation action: {e}")
            raise

    def get_pending_remediation(self) -> List[Dict[str, Any]]:
        """Get pending and in-progress remediation actions."""
        try:
            actions = self.db_queries.get_pending_remediation()
            return [a.to_dict() for a in actions]
        except Exception as e:
            logger.error(f"Error getting pending remediation: {e}")
            return []

    def get_overdue_actions(self) -> List[Dict[str, Any]]:
        """Get overdue remediation actions."""
        try:
            actions = self.db_queries.get_overdue_actions()
            return [a.to_dict() for a in actions]
        except Exception as e:
            logger.error(f"Error getting overdue actions: {e}")
            return []

    def update_remediation_status(
        self,
        action_id: str,
        status: str,
        completion_percentage: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update remediation action status."""
        try:
            action = self.db_queries.update_remediation_status(
                action_id=action_id,
                status=status,
                completion_percentage=completion_percentage,
            )
            return action.to_dict() if action else None
        except Exception as e:
            logger.error(f"Error updating remediation status: {e}")
            return None

    # ========================================================================
    # System Status & Reporting
    # ========================================================================

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            stats = self.db_queries.get_system_statistics()
            monitoring_stats = self.monitor.get_statistics() if self.monitor else {}

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "initialized": self.initialized,
                "monitoring": self.monitoring,
                **stats,
                "monitor_stats": monitoring_stats,
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

    def get_compliance_report(
        self,
        system_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a compliance report.
        
        Includes all regulatory changes, alerts, and remediation status.
        """
        try:
            report = {
                "generated_at": datetime.utcnow().isoformat(),
                "system_name": system_name or "all_systems",
                "changes": self.get_recent_changes(),
                "alerts": {
                    "open": self.get_open_alerts(),
                    "critical": self.get_critical_alerts(),
                },
                "remediation": {
                    "pending": self.get_pending_remediation(),
                    "overdue": self.get_overdue_actions(),
                },
                "system_status": self.get_system_status(),
            }
            return report
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {"error": str(e)}

    def export_compliance_data(self, format: str = "json") -> str:
        """Export all compliance data."""
        try:
            import json

            if self.api:
                return self.api.export_data(format=format)

            # Fallback to manual export
            report = self.get_compliance_report()
            return json.dumps(report, indent=2, default=str)

        except Exception as e:
            logger.error(f"Error exporting compliance data: {e}")
            return "{}"

    # ========================================================================
    # Real-Time Monitoring
    # ========================================================================

    def register_event_callback(self, event_type: str, callback) -> None:
        """Register callback for real-time events."""
        if self.monitor:
            from scripts.realtime_monitor import EventType

            try:
                event = EventType(event_type)
                self.monitor.register_callback(event, callback)
            except ValueError:
                logger.warning(f"Unknown event type: {event_type}")

    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent real-time events."""
        if self.monitor:
            events = self.monitor.get_recent_events(count)
            return [e.to_dict() for e in events]
        return []

    def get_event_history(
        self,
        event_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get event history."""
        if self.monitor:
            if event_type:
                from scripts.realtime_monitor import EventType

                try:
                    event = EventType(event_type)
                    events = self.monitor.get_event_history(event)
                except ValueError:
                    events = []
            else:
                events = self.monitor.get_event_history()

            return [e.to_dict() for e in events]
        return []

    # ========================================================================
    # Compliance Validation & Gap Analysis
    # ========================================================================

    def validate_system_compliance(
        self,
        system_name: str,
        framework: str,
        controls: Dict[str, str],
    ) -> Dict[str, Any]:
        """Validate system compliance against framework."""
        if not self.api:
            return {"error": "API not available"}

        try:
            result = self.api.validate_system_compliance(
                system_name=system_name,
                framework=framework,
                controls=controls,
            )

            # Save alert if non-compliant
            if result.get("compliance_percentage", 0) < 80:
                self.generate_alert(
                    alert_type="compliance_validation_failed",
                    message=f"System {system_name} failed {framework} validation",
                    risk_level="high",
                    affected_regulation=framework,
                )

            return result
        except Exception as e:
            logger.error(f"Error validating compliance: {e}")
            return {"error": str(e)}

    def identify_compliance_gaps(
        self,
        framework: str,
        current_state: Dict[str, str],
        required_state: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Identify compliance gaps."""
        if not self.api:
            return []

        try:
            gaps = self.api.identify_compliance_gaps(
                framework=framework,
                current_state=current_state,
                required_state=required_state,
            )

            # Create remediation actions for critical gaps
            for gap in gaps:
                if gap.get("severity") == "critical":
                    self.create_remediation_action(
                        gap_id=gap.get("gap_id", str(uuid4())),
                        action_title=f"Fix: {gap.get('requirement')}",
                        description=f"Remediate {framework} gap: {gap.get('requirement')}",
                        priority=10,
                    )

            return gaps
        except Exception as e:
            logger.error(f"Error identifying compliance gaps: {e}")
            return []

    def shutdown(self) -> None:
        """Shutdown all services gracefully."""
        logger.info("Shutting down system coordinator...")
        self.stop_monitoring()
        self.initialized = False
        logger.info("System coordinator shutdown complete")


# Global coordinator instance
_global_coordinator: Optional[SystemCoordinator] = None


def get_coordinator(
    db_url: str = "sqlite:///compliance.db",
) -> SystemCoordinator:
    """Get or create the global coordinator instance."""
    global _global_coordinator
    if _global_coordinator is None:
        _global_coordinator = SystemCoordinator(db_url=db_url)
        _global_coordinator.initialize()
    return _global_coordinator


def initialize_coordinator(
    db_url: str = "sqlite:///compliance.db",
    monitor_interval: int = 60,
    start_monitoring: bool = False,
) -> SystemCoordinator:
    """Initialize and return the global coordinator instance."""
    global _global_coordinator
    _global_coordinator = SystemCoordinator(
        db_url=db_url,
        monitor_interval=monitor_interval,
    )
    _global_coordinator.initialize()
    if start_monitoring:
        _global_coordinator.start_monitoring()
    return _global_coordinator
