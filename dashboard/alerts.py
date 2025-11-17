"""
Real-time alerts and notifications system for regulatory changes.
Handles alert generation, storage, and delivery.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages regulatory change alerts and notifications."""
    
    def __init__(self, alerts_dir: Path = None):
        """Initialize alert manager with storage directory."""
        if alerts_dir is None:
            alerts_dir = Path.cwd() / "data" / "alerts"
        self.alerts_dir = alerts_dir
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        self.alerts_file = self.alerts_dir / "active_alerts.json"
        self._load_alerts()
    
    def _load_alerts(self) -> None:
        """Load alerts from storage."""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    self.alerts = json.load(f)
            else:
                self.alerts = []
        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
            self.alerts = []
    
    def _save_alerts(self) -> None:
        """Persist alerts to storage."""
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def create_alert(self, 
                    alert_type: str,
                    severity: str,
                    title: str,
                    description: str,
                    domain: str = "General",
                    metadata: Dict = None) -> str:
        """
        Create a new alert.
        
        Args:
            alert_type: Type of alert (e.g., 'regulatory_change', 'compliance_issue', 'threshold_breach')
            severity: 'critical', 'high', 'medium', 'low'
            title: Brief alert title
            description: Detailed alert description
            domain: Regulatory domain (FDA, EPA, SEC, etc.)
            metadata: Additional metadata dict
            
        Returns:
            Alert ID
        """
        alert = {
            "id": f"alert_{len(self.alerts)}_{datetime.now().timestamp()}",
            "type": alert_type,
            "severity": severity,
            "title": title,
            "description": description,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "read": False,
            "metadata": metadata or {}
        }
        self.alerts.append(alert)
        self._save_alerts()
        return alert["id"]
    
    def get_alerts(self, 
                  domain: Optional[str] = None,
                  severity: Optional[str] = None,
                  unread_only: bool = False,
                  hours: int = 24) -> List[Dict]:
        """
        Retrieve alerts with optional filtering.
        
        Args:
            domain: Filter by regulatory domain
            severity: Filter by severity level
            unread_only: Return only unread alerts
            hours: Return alerts from last N hours (0 for all)
            
        Returns:
            List of alerts matching criteria
        """
        cutoff_time = datetime.now() - timedelta(hours=hours) if hours > 0 else None
        filtered = self.alerts
        
        # Filter by time
        if cutoff_time:
            filtered = [
                a for a in filtered 
                if datetime.fromisoformat(a["created_at"]) > cutoff_time
            ]
        
        # Filter by domain
        if domain:
            filtered = [a for a in filtered if a["domain"] == domain]
        
        # Filter by severity
        if severity:
            filtered = [a for a in filtered if a["severity"] == severity]
        
        # Filter by read status
        if unread_only:
            filtered = [a for a in filtered if not a["read"]]
        
        return sorted(filtered, key=lambda x: x["created_at"], reverse=True)
    
    def mark_as_read(self, alert_id: str) -> bool:
        """Mark an alert as read."""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["read"] = True
                self._save_alerts()
                return True
        return False
    
    def mark_all_as_read(self, domain: Optional[str] = None) -> int:
        """Mark all alerts as read, optionally filtered by domain."""
        count = 0
        for alert in self.alerts:
            if not alert["read"]:
                if domain is None or alert["domain"] == domain:
                    alert["read"] = True
                    count += 1
        if count > 0:
            self._save_alerts()
        return count
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert by ID."""
        original_len = len(self.alerts)
        self.alerts = [a for a in self.alerts if a["id"] != alert_id]
        if len(self.alerts) < original_len:
            self._save_alerts()
            return True
        return False
    
    def get_stats(self, hours: int = 24) -> Dict:
        """Get alert statistics."""
        recent_alerts = self.get_alerts(hours=hours)
        
        return {
            "total": len(recent_alerts),
            "unread": sum(1 for a in recent_alerts if not a["read"]),
            "critical": sum(1 for a in recent_alerts if a["severity"] == "critical"),
            "high": sum(1 for a in recent_alerts if a["severity"] == "high"),
            "by_domain": {}
        }
    
    def display_alert_toast(self, alert: Dict) -> None:
        """Display alert as Streamlit toast notification."""
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "ℹ️",
            "low": "📌"
        }
        emoji = severity_emoji.get(alert["severity"], "📢")
        st.toast(
            f"{emoji} {alert['title']}\n{alert['description'][:100]}...",
            icon=emoji
        )
    
    def display_alert_history(self, limit: int = 10) -> None:
        """Display alert history in Streamlit sidebar."""
        recent_alerts = self.get_alerts(hours=0)[:limit]
        
        if not recent_alerts:
            st.info("No alerts yet")
            return
        
        severity_colors = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        for alert in recent_alerts:
            color = severity_colors.get(alert["severity"], "⚪")
            read_indicator = "✓" if alert["read"] else "●"
            
            with st.container(border=True):
                st.markdown(
                    f"{color} **{alert['title']}** {read_indicator}\n"
                    f"*{alert['domain']}* | {alert['created_at'][:10]}"
                )
                if st.button("Mark as read", key=f"read_{alert['id']}"):
                    self.mark_as_read(alert["id"])
                    st.rerun()
