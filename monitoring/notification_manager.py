"""
PHASE 6: Notification & Alerting System

Sends notifications on regulatory changes:
- Email alerts on critical/high severity changes
- In-app notifications (dashboard)
- Change digests (daily/weekly)
- Escalation rules
- Audit trail of all notifications

Part of IRAQAF Phase 6 - Change Monitoring System
"""

import json
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channel"""
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"
    DASHBOARD = "DASHBOARD"
    WEBHOOK = "WEBHOOK"
    SMS = "SMS"


class NotificationPriority(str, Enum):
    """Notification priority level"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class NotificationStatus(str, Enum):
    """Status of notification delivery"""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    ACKNOWLEDGED = "ACKNOWLEDGED"


@dataclass
class Notification:
    """Represents a single notification"""
    notification_id: str
    timestamp: datetime
    priority: NotificationPriority
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    change_id: Optional[str]
    status: NotificationStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    acknowledgment_time: Optional[datetime]


@dataclass
class NotificationDigest:
    """Daily/weekly summary of changes"""
    digest_id: str
    period_start: datetime
    period_end: datetime
    digest_type: str  # "DAILY", "WEEKLY"
    total_notifications: int
    critical_count: int
    high_count: int
    changes_summary: List[str]
    recipient: str
    status: NotificationStatus


class NotificationManager:
    """
    Manages notifications for regulatory changes and compliance events.
    Handles email, in-app, webhook, and digest notifications.
    """

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        from_address: str = "iraqaf@compliance.local"
    ):
        """
        Initialize notification manager.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            from_address: Sender email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_address = from_address
        self.notification_history = []
        self.notification_queue = []

    def create_change_notification(
        self,
        change_id: str,
        change_type: str,
        severity: str,
        regulation: str,
        requirement_id: str,
        affected_systems: List[str],
        description: str,
        recipients: List[str]
    ) -> List[Notification]:
        """
        Create notifications for a detected change.

        Returns:
            List of created notifications
        """
        priority = self._map_severity_to_priority(severity)
        notifications = []

        # Determine notification channels based on priority
        channels = self._determine_channels(priority)

        for recipient in recipients:
            for channel in channels:
                notification = self._create_notification(
                    change_id=change_id,
                    priority=priority,
                    channel=channel,
                    recipient=recipient,
                    change_type=change_type,
                    regulation=regulation,
                    requirement_id=requirement_id,
                    affected_systems=affected_systems,
                    description=description
                )
                notifications.append(notification)
                self.notification_queue.append(notification)

        return notifications

    def _map_severity_to_priority(self, severity: str) -> NotificationPriority:
        """Map change severity to notification priority"""
        severity_map = {
            "CRITICAL": NotificationPriority.CRITICAL,
            "HIGH": NotificationPriority.HIGH,
            "MEDIUM": NotificationPriority.MEDIUM,
            "LOW": NotificationPriority.LOW
        }
        return severity_map.get(severity, NotificationPriority.INFO)

    def _determine_channels(
        self,
        priority: NotificationPriority
    ) -> List[NotificationChannel]:
        """Determine notification channels based on priority"""
        if priority == NotificationPriority.CRITICAL:
            return [
                NotificationChannel.EMAIL,
                NotificationChannel.DASHBOARD,
                NotificationChannel.WEBHOOK,
                NotificationChannel.SMS
            ]
        elif priority == NotificationPriority.HIGH:
            return [
                NotificationChannel.EMAIL,
                NotificationChannel.DASHBOARD,
                NotificationChannel.WEBHOOK
            ]
        elif priority == NotificationPriority.MEDIUM:
            return [
                NotificationChannel.DASHBOARD,
                NotificationChannel.EMAIL
            ]
        else:
            return [NotificationChannel.DASHBOARD]

    def _create_notification(
        self,
        change_id: str,
        priority: NotificationPriority,
        channel: NotificationChannel,
        recipient: str,
        change_type: str,
        regulation: str,
        requirement_id: str,
        affected_systems: List[str],
        description: str
    ) -> Notification:
        """Create a notification object"""
        notification_id = f"NOTIF-{datetime.now().timestamp()}"

        subject, body = self._generate_notification_content(
            change_type=change_type,
            regulation=regulation,
            requirement_id=requirement_id,
            affected_systems=affected_systems,
            description=description,
            channel=channel
        )

        return Notification(
            notification_id=notification_id,
            timestamp=datetime.now(),
            priority=priority,
            channel=channel,
            recipient=recipient,
            subject=subject,
            body=body,
            change_id=change_id,
            status=NotificationStatus.PENDING,
            sent_at=None,
            delivered_at=None,
            error_message=None,
            acknowledgment_time=None
        )

    def _generate_notification_content(
        self,
        change_type: str,
        regulation: str,
        requirement_id: str,
        affected_systems: List[str],
        description: str,
        channel: NotificationChannel
    ) -> Tuple[str, str]:
        """Generate subject and body for notification"""
        subject = f"[ALERT] {regulation} {change_type}: {requirement_id}"

        if channel == NotificationChannel.EMAIL:
            body = self._generate_email_body(
                change_type, regulation, requirement_id,
                affected_systems, description
            )
        elif channel == NotificationChannel.SMS:
            body = f"{regulation}: {requirement_id} {change_type.lower()}. Action required."
        else:
            body = description

        return subject, body

    def _generate_email_body(
        self,
        change_type: str,
        regulation: str,
        requirement_id: str,
        affected_systems: List[str],
        description: str
    ) -> str:
        """Generate email body with HTML formatting"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ background: #e74c3c; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
        .content {{ border: 1px solid #ddd; padding: 20px; }}
        .footer {{ background: #ecf0f1; padding: 10px; font-size: 12px; }}
        .change-type {{ font-weight: bold; color: #e74c3c; }}
        .systems {{ background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #3498db; }}
        .action {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 3px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Regulatory Change Alert</h2>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="content">
            <p>A regulatory change has been detected in <strong>{regulation}</strong>:</p>

            <p><span class="change-type">{change_type}</span></p>
            <p><strong>Requirement ID:</strong> {requirement_id}</p>
            <p><strong>Description:</strong> {description}</p>

            <div class="systems">
                <strong>Affected Systems:</strong>
                <ul>
                    {''.join(f'<li>{s}</li>' for s in affected_systems)}
                </ul>
            </div>

            <div class="action">
                <strong>Required Action:</strong>
                <ul>
                    <li>Review the change details</li>
                    <li>Assess impact on your organization</li>
                    <li>Plan remediation activities</li>
                    <li>Update compliance documentation</li>
                </ul>
            </div>

            <p><a href="https://compliance.local:8504/changes">View Full Change Details</a></p>
        </div>
        <div class="footer">
            <p>IRAQAF Compliance Monitoring System</p>
            <p>This is an automated alert. Do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""

    def send_notifications(
        self,
        notifications: List[Notification]
    ) -> Dict[str, int]:
        """
        Send pending notifications.

        Returns:
            Dictionary with counts: sent, delivered, failed
        """
        results = {"sent": 0, "delivered": 0, "failed": 0}

        for notification in notifications:
            if notification.status != NotificationStatus.PENDING:
                continue

            try:
                if notification.channel == NotificationChannel.EMAIL:
                    self._send_email(notification)
                    notification.status = NotificationStatus.DELIVERED
                    notification.delivered_at = datetime.now()
                    results["delivered"] += 1
                elif notification.channel == NotificationChannel.DASHBOARD:
                    notification.status = NotificationStatus.DELIVERED
                    notification.delivered_at = datetime.now()
                    results["delivered"] += 1
                elif notification.channel == NotificationChannel.WEBHOOK:
                    self._send_webhook(notification)
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now()
                    results["sent"] += 1
                elif notification.channel == NotificationChannel.SMS:
                    self._send_sms(notification)
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.now()
                    results["sent"] += 1

                self.notification_history.append(notification)

            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
                notification.status = NotificationStatus.FAILED
                notification.error_message = str(e)
                results["failed"] += 1

        return results

    def _send_email(self, notification: Notification) -> None:
        """Send email notification (simulated in demo mode)"""
        logger.info(
            f"[EMAIL] To: {notification.recipient} | "
            f"Subject: {notification.subject}"
        )
        # In production, connect to SMTP server
        # For now, just log the action

    def _send_sms(self, notification: Notification) -> None:
        """Send SMS notification (simulated in demo mode)"""
        logger.info(
            f"[SMS] To: {notification.recipient} | "
            f"Message: {notification.body[:50]}..."
        )
        # In production, use SMS API (Twilio, AWS SNS, etc.)

    def _send_webhook(self, notification: Notification) -> None:
        """Send webhook notification (simulated in demo mode)"""
        logger.info(
            f"[WEBHOOK] Change: {notification.change_id} | "
            f"Recipient: {notification.recipient}"
        )
        # In production, make HTTP POST to webhook URL

    def create_daily_digest(
        self,
        recipient: str,
        notifications: List[Notification],
        period_start: datetime,
        period_end: datetime
    ) -> NotificationDigest:
        """Create daily digest of notifications"""
        digest_id = f"DIGEST-DAILY-{datetime.now().timestamp()}"

        # Filter notifications for recipient in period
        relevant = [
            n for n in notifications
            if n.recipient == recipient
            and period_start <= n.timestamp <= period_end
        ]

        critical_count = sum(
            1 for n in relevant
            if n.priority == NotificationPriority.CRITICAL
        )
        high_count = sum(
            1 for n in relevant
            if n.priority == NotificationPriority.HIGH
        )

        # Generate summary
        changes_summary = [
            f"{n.subject}" for n in relevant
        ][:10]  # Top 10

        digest = NotificationDigest(
            digest_id=digest_id,
            period_start=period_start,
            period_end=period_end,
            digest_type="DAILY",
            total_notifications=len(relevant),
            critical_count=critical_count,
            high_count=high_count,
            changes_summary=changes_summary,
            recipient=recipient,
            status=NotificationStatus.PENDING
        )

        return digest

    def create_weekly_digest(
        self,
        recipient: str,
        notifications: List[Notification],
        period_start: datetime,
        period_end: datetime
    ) -> NotificationDigest:
        """Create weekly digest of notifications"""
        digest_id = f"DIGEST-WEEKLY-{datetime.now().timestamp()}"

        # Filter notifications for recipient in period
        relevant = [
            n for n in notifications
            if n.recipient == recipient
            and period_start <= n.timestamp <= period_end
        ]

        critical_count = sum(
            1 for n in relevant
            if n.priority == NotificationPriority.CRITICAL
        )
        high_count = sum(
            1 for n in relevant
            if n.priority == NotificationPriority.HIGH
        )

        # Generate summary
        changes_summary = [
            f"{n.subject}" for n in relevant
        ][:20]  # Top 20

        digest = NotificationDigest(
            digest_id=digest_id,
            period_start=period_start,
            period_end=period_end,
            digest_type="WEEKLY",
            total_notifications=len(relevant),
            critical_count=critical_count,
            high_count=high_count,
            changes_summary=changes_summary,
            recipient=recipient,
            status=NotificationStatus.PENDING
        )

        return digest

    def get_notification_history(
        self,
        recipient: Optional[str] = None,
        days: int = 30
    ) -> List[Notification]:
        """Get notification history"""
        cutoff_date = datetime.now() - timedelta(days=days)

        history = [
            n for n in self.notification_history
            if n.timestamp >= cutoff_date
        ]

        if recipient:
            history = [n for n in history if n.recipient == recipient]

        return sorted(history, key=lambda n: n.timestamp, reverse=True)

    def export_notifications_to_json(
        self,
        notifications: List[Notification]
    ) -> str:
        """Export notifications to JSON"""
        notif_list = []
        for n in notifications:
            notif_dict = asdict(n)
            notif_dict['timestamp'] = n.timestamp.isoformat()
            if n.sent_at:
                notif_dict['sent_at'] = n.sent_at.isoformat()
            if n.delivered_at:
                notif_dict['delivered_at'] = n.delivered_at.isoformat()
            if n.acknowledgment_time:
                notif_dict['acknowledgment_time'] = n.acknowledgment_time.isoformat()
            notif_dict['priority'] = n.priority.value
            notif_dict['channel'] = n.channel.value
            notif_dict['status'] = n.status.value
            notif_list.append(notif_dict)

        return json.dumps(notif_list, indent=2)


# Example usage
if __name__ == "__main__":
    manager = NotificationManager()

    # Create notifications for a change
    notifications = manager.create_change_notification(
        change_id="CHG-001",
        change_type="NEW_REQUIREMENT",
        severity="CRITICAL",
        regulation="GDPR",
        requirement_id="GDPR-4",
        affected_systems=["Data Storage", "User Management"],
        description="New requirement for automated DPIA",
        recipients=["compliance@acme.com", "ciso@acme.com"]
    )

    print(f"\n✓ Created {len(notifications)} notifications")
    print(f"  Channels: {set(n.channel.value for n in notifications)}")
    print(f"  Priority: {notifications[0].priority.value}")

    # Send notifications
    results = manager.send_notifications(notifications)
    print(f"\nNotification Results:")
    print(f"  Sent: {results['sent']}")
    print(f"  Delivered: {results['delivered']}")
    print(f"  Failed: {results['failed']}")

    # Create daily digest
    digest = manager.create_daily_digest(
        recipient="compliance@acme.com",
        notifications=manager.notification_history,
        period_start=datetime.now() - timedelta(days=1),
        period_end=datetime.now()
    )

    print(f"\n✓ Daily Digest Created: {digest.digest_id}")
    print(f"  Total Notifications: {digest.total_notifications}")
    print(f"  Critical: {digest.critical_count}, High: {digest.high_count}")
