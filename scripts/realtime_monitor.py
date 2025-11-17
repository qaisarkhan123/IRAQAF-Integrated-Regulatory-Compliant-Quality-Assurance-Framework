"""
Real-Time Monitoring Service for Regulatory Compliance

Continuously monitors regulatory changes, compliance scores, and system health.
Provides background monitoring with threading, polling, and event notification.
Supports WebSocket for real-time dashboard updates.

Usage:
    from scripts.realtime_monitor import RealTimeMonitor
    
    monitor = RealTimeMonitor(update_interval=60)
    monitor.start()
    
    # Listen for updates
    for event in monitor.get_events():
        print(f"Event: {event}")
    
    monitor.stop()
"""

import logging
import threading
import time
import queue
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4
from collections import deque
import json

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Real-time event types."""
    REGULATORY_CHANGE = "regulatory_change"
    COMPLIANCE_SCORE_UPDATE = "compliance_score_update"
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_RESOLVED = "alert_resolved"
    REMEDIATION_PROGRESS = "remediation_progress"
    SYSTEM_HEALTH_UPDATE = "system_health_update"
    THRESHOLD_BREACH = "threshold_breach"
    DEADLINE_WARNING = "deadline_warning"


class SystemEvent:
    """Represents a real-time system event."""

    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str = "system",
        timestamp: Optional[datetime] = None,
    ):
        self.id = str(uuid4())
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class MonitoringState:
    """Tracks the current state of the system for change detection."""

    def __init__(self):
        self.last_alert_count = 0
        self.last_critical_alert_count = 0
        self.last_change_count = 0
        self.last_compliance_scores: Dict[str, float] = {}
        self.last_remediation_count = 0
        self.last_avg_compliance = 0.0
        self.last_update = datetime.utcnow()

    def update(self, new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect changes between old and new state.
        
        Returns:
            Dictionary of detected changes
        """
        changes = {}

        # Alert changes
        new_alert_count = new_state.get("total_alerts", 0)
        new_critical_count = new_state.get("critical_alerts", 0)

        if new_alert_count != self.last_alert_count:
            changes["alert_count_change"] = {
                "old": self.last_alert_count,
                "new": new_alert_count,
                "delta": new_alert_count - self.last_alert_count,
            }
            self.last_alert_count = new_alert_count

        if new_critical_count != self.last_critical_alert_count:
            changes["critical_alert_change"] = {
                "old": self.last_critical_alert_count,
                "new": new_critical_count,
                "delta": new_critical_count - self.last_critical_alert_count,
            }
            self.last_critical_alert_count = new_critical_count

        # Regulatory change count
        new_change_count = new_state.get("total_changes", 0)
        if new_change_count != self.last_change_count:
            changes["change_count_change"] = {
                "old": self.last_change_count,
                "new": new_change_count,
                "delta": new_change_count - self.last_change_count,
            }
            self.last_change_count = new_change_count

        # Compliance scores
        new_scores = new_state.get("compliance_scores", {})
        for framework, score in new_scores.items():
            old_score = self.last_compliance_scores.get(framework, 0)
            if score != old_score:
                if "compliance_score_changes" not in changes:
                    changes["compliance_score_changes"] = {}
                changes["compliance_score_changes"][framework] = {
                    "old": old_score,
                    "new": score,
                    "delta": score - old_score,
                }
            self.last_compliance_scores[framework] = score

        # Remediation progress
        new_remediation_count = new_state.get("completed_actions", 0)
        if new_remediation_count != self.last_remediation_count:
            changes["remediation_progress"] = {
                "old": self.last_remediation_count,
                "new": new_remediation_count,
                "delta": new_remediation_count - self.last_remediation_count,
            }
            self.last_remediation_count = new_remediation_count

        # Average compliance
        new_avg = new_state.get("avg_compliance", 0.0)
        if new_avg != self.last_avg_compliance:
            changes["avg_compliance_change"] = {
                "old": self.last_avg_compliance,
                "new": new_avg,
                "delta": new_avg - self.last_avg_compliance,
            }
            self.last_avg_compliance = new_avg

        self.last_update = datetime.utcnow()
        return changes


class RealTimeMonitor:
    """
    Real-time monitoring service for regulatory compliance system.
    
    Continuously monitors changes and generates events.
    Supports multiple monitoring strategies and event callbacks.
    """

    def __init__(
        self,
        update_interval: int = 60,
        event_history_size: int = 1000,
        api_provider: Optional[Callable] = None,
    ):
        """
        Initialize the monitoring service.
        
        Args:
            update_interval: Seconds between monitoring checks
            event_history_size: Maximum events to keep in history
            api_provider: Callable that returns the API instance for data queries
        """
        self.update_interval = update_interval
        self.running = False
        self.monitor_thread = None

        # Event management
        self.event_queue: queue.Queue = queue.Queue()
        self.event_history: deque = deque(maxlen=event_history_size)
        self.state = MonitoringState()

        # Callbacks
        self.callbacks: Dict[EventType, List[Callable]] = {}
        self.api_provider = api_provider

        logger.info(f"RealTimeMonitor initialized with {update_interval}s interval")

    def register_callback(self, event_type: EventType, callback: Callable) -> None:
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
        logger.debug(f"Registered callback for {event_type.value}")

    def _emit_event(self, event: SystemEvent) -> None:
        """Emit an event to all registered callbacks and queue."""
        # Add to history
        self.event_history.append(event)

        # Add to queue
        self.event_queue.put(event)

        # Call registered callbacks
        callbacks = self.callbacks.get(event.event_type, [])
        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in callback: {e}")

    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state from API."""
        if not self.api_provider:
            return {}

        try:
            api = self.api_provider()
            if not api:
                return {}

            stats = api.get_system_status()
            scores = {}

            # Try to get compliance trends
            try:
                for framework in ["GDPR", "HIPAA", "SOC2", "ISO27001"]:
                    trend = api.get_compliance_trend_analysis(framework)
                    if trend:
                        scores[framework] = trend.get("current_score", 0)
            except:
                pass

            return {
                **stats,
                "compliance_scores": scores,
            }
        except Exception as e:
            logger.error(f"Error getting system state: {e}")
            return {}

    def _check_thresholds(self, state: Dict[str, Any]) -> None:
        """Check for threshold breaches and emit events."""
        # Check alert thresholds
        critical_alerts = state.get("critical_alerts", 0)
        if critical_alerts > 0:
            self._emit_event(
                SystemEvent(
                    EventType.THRESHOLD_BREACH,
                    {
                        "threshold": "critical_alerts",
                        "value": critical_alerts,
                        "severity": "high" if critical_alerts > 5 else "medium",
                    },
                    source="threshold_monitor",
                )
            )

        # Check compliance scores
        for framework, score in state.get("compliance_scores", {}).items():
            if score < 80:
                severity = "critical" if score < 70 else "high" if score < 80 else "medium"
                self._emit_event(
                    SystemEvent(
                        EventType.THRESHOLD_BREACH,
                        {
                            "framework": framework,
                            "score": score,
                            "threshold": 80,
                            "severity": severity,
                        },
                        source="compliance_monitor",
                    )
                )

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        logger.info("Starting monitoring loop")

        while self.running:
            try:
                # Get current system state
                current_state = self._get_system_state()

                if current_state:
                    # Detect changes
                    changes = self.state.update(current_state)

                    # Emit events for detected changes
                    if changes:
                        self._emit_event(
                            SystemEvent(
                                EventType.SYSTEM_HEALTH_UPDATE,
                                changes,
                                source="state_detector",
                            )
                        )

                    # Check thresholds
                    self._check_thresholds(current_state)

                # Sleep until next check
                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.update_interval)

        logger.info("Monitoring loop stopped")

    def start(self) -> None:
        """Start the real-time monitoring service."""
        if self.running:
            logger.warning("Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Real-time monitoring started")

    def stop(self) -> None:
        """Stop the real-time monitoring service."""
        if not self.running:
            logger.warning("Monitor not running")
            return

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Real-time monitoring stopped")

    def get_events(self, timeout: float = 1.0) -> Optional[SystemEvent]:
        """
        Get next event from queue (non-blocking).
        
        Usage:
            while True:
                event = monitor.get_events()
                if event:
                    print(f"Event: {event.to_json()}")
        """
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_recent_events(self, count: int = 10) -> List[SystemEvent]:
        """Get recent events from history."""
        return list(self.event_history)[-count:]

    def get_event_history(self, event_type: Optional[EventType] = None) -> List[SystemEvent]:
        """Get event history, optionally filtered by type."""
        if event_type is None:
            return list(self.event_history)
        return [e for e in self.event_history if e.event_type == event_type]

    def clear_event_queue(self) -> int:
        """Clear the event queue and return count of cleared events."""
        count = 0
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                count += 1
            except queue.Empty:
                break
        return count

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        event_counts = {}
        for event_type in EventType:
            count = sum(
                1 for e in self.event_history if e.event_type == event_type
            )
            if count > 0:
                event_counts[event_type.value] = count

        return {
            "running": self.running,
            "total_events": len(self.event_history),
            "event_counts": event_counts,
            "last_update": self.state.last_update.isoformat(),
            "uptime_seconds": (
                datetime.utcnow() - self.state.last_update
            ).total_seconds(),
        }


# Global monitor instance
_global_monitor: Optional[RealTimeMonitor] = None


def get_monitor(api_provider: Optional[Callable] = None) -> RealTimeMonitor:
    """Get or create the global monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = RealTimeMonitor(api_provider=api_provider)
    return _global_monitor


def initialize_monitor(
    update_interval: int = 60,
    api_provider: Optional[Callable] = None,
) -> RealTimeMonitor:
    """Initialize and return the global monitor instance."""
    global _global_monitor
    _global_monitor = RealTimeMonitor(
        update_interval=update_interval,
        api_provider=api_provider,
    )
    return _global_monitor
