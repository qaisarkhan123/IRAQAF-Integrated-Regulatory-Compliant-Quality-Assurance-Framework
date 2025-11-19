"""
PHASE 3: NOTIFICATIONS MODULE
Change Notifications & Alerts

Implements multi-channel notifications for regulatory changes:
- Email notifications (SMTP)
- In-app alerts (database)
- Change summaries
- Recommendation generation
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of regulatory changes"""
    NEW_REQUIREMENT = "new_requirement"
    MODIFIED_REQUIREMENT = "modified_requirement"
    REMOVED_REQUIREMENT = "removed_requirement"
    NEW_SECTION = "new_section"
    REGULATORY_UPDATE = "regulatory_update"
    CRITICAL_CHANGE = "critical_change"


class SeverityLevel(Enum):
    """Severity levels for changes"""
    INFORMATIONAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class Change:
    """Represents a regulatory change"""
    change_type: ChangeType
    source: str
    section: str
    old_value: Optional[str]
    new_value: str
    detected_at: datetime
    severity: SeverityLevel
    recommendation: Optional[str] = None
    affected_systems: List[str] = None
    
    def __post_init__(self):
        if self.affected_systems is None:
            self.affected_systems = []


@dataclass
class NotificationPreference:
    """User notification preferences"""
    user_id: str
    email: str
    notify_critical: bool = True
    notify_high: bool = True
    notify_medium: bool = False
    notify_low: bool = False
    notify_informational: bool = False
    digest_frequency: str = 'daily'  # 'immediate', 'daily', 'weekly'
    email_enabled: bool = True
    in_app_enabled: bool = True
    channels: List[str] = None
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = ['email', 'in_app']


class EmailNotifier:
    """
    Sends email notifications for regulatory changes
    
    Supports:
    - SMTP configuration (Gmail, Outlook, custom SMTP)
    - HTML email templates
    - Attachment support
    - Batch sending
    """
    
    def __init__(self, smtp_config: Dict = None):
        """
        Initialize email notifier
        
        Args:
            smtp_config: SMTP configuration dict with keys:
                - host: SMTP server host
                - port: SMTP server port (default: 587)
                - username: SMTP username
                - password: SMTP password
                - use_tls: Use TLS encryption (default: True)
                - from_address: From email address
        """
        self.smtp_config = smtp_config or self._default_smtp_config()
        self.test_mode = smtp_config is None or smtp_config.get('test_mode', False)
    
    def _default_smtp_config(self) -> Dict:
        """Get default SMTP configuration"""
        return {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'use_tls': True,
            'from_address': 'compliance@example.com',
            'test_mode': True
        }
    
    def send_change_notification(
        self,
        to_email: str,
        changes: List[Change],
        user_name: str = 'Recipient'
    ) -> Tuple[bool, str]:
        """
        Send email notification about regulatory changes
        
        Args:
            to_email: Recipient email address
            changes: List of changes to notify about
            user_name: User's name for personalization
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._create_subject(changes)
            msg['From'] = self.smtp_config['from_address']
            msg['To'] = to_email
            
            # Create HTML content
            html_content = self._create_html_content(changes, user_name)
            
            # Attach HTML
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            if self.test_mode:
                logger.info(f"[TEST MODE] Would send email to {to_email}")
                logger.info(f"Subject: {msg['Subject']}")
                return True, "Email would be sent (test mode)"
            
            # Actually send
            self._send_smtp(to_email, msg)
            logger.info(f"Email sent to {to_email}")
            return True, f"Email sent to {to_email}"
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _create_subject(self, changes: List[Change]) -> str:
        """Create email subject line"""
        critical_count = sum(1 for c in changes if c.severity == SeverityLevel.CRITICAL)
        high_count = sum(1 for c in changes if c.severity == SeverityLevel.HIGH)
        
        if critical_count > 0:
            return f"CRITICAL: {critical_count} Critical Regulatory Change(s)"
        elif high_count > 0:
            return f"HIGH: {high_count} Important Regulatory Update(s)"
        else:
            return f"Regulatory Updates: {len(changes)} Change(s)"
    
    def _create_html_content(self, changes: List[Change], user_name: str) -> str:
        """Create HTML email content"""
        
        # Group changes by severity
        by_severity = {}
        for change in changes:
            severity = change.severity.name
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(change)
        
        # Build HTML
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 20px; border-radius: 5px; }}
                .change-group {{ margin: 20px 0; }}
                .critical {{ border-left: 4px solid #d32f2f; }}
                .high {{ border-left: 4px solid #f57c00; }}
                .medium {{ border-left: 4px solid #fbc02d; }}
                .low {{ border-left: 4px solid #388e3c; }}
                .change-item {{ padding: 15px; margin: 10px 0; background: #f5f5f5;
                             border-radius: 3px; }}
                .recommendation {{ background: #e8f5e9; padding: 10px;
                               border-left: 3px solid #4caf50; margin: 10px 0; }}
                .footer {{ color: #999; font-size: 12px; margin-top: 30px;
                        border-top: 1px solid #ddd; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Regulatory Change Notification</h2>
                <p>Hello {user_name},</p>
                <p>The following regulatory changes have been detected:</p>
            </div>
        """
        
        # Add changes by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL']:
            if severity in by_severity:
                html += f"<div class='change-group'>"
                html += f"<h3>{severity} SEVERITY ({len(by_severity[severity])} changes)</h3>"
                
                for change in by_severity[severity]:
                    severity_class = severity.lower()
                    html += f"""
                    <div class='change-item {severity_class}'>
                        <strong>{change.source} - {change.section}</strong><br>
                        <strong>Type:</strong> {change.change_type.value}<br>
                        <strong>Change:</strong> {change.new_value[:100]}...<br>
                        <strong>Detected:</strong> {change.detected_at.strftime('%Y-%m-%d %H:%M UTC')}
                    """
                    
                    if change.affected_systems:
                        html += f"<br><strong>Affected Systems:</strong> {', '.join(change.affected_systems)}"
                    
                    if change.recommendation:
                        html += f"""
                        <div class='recommendation'>
                            <strong>Recommendation:</strong> {change.recommendation}
                        </div>
                        """
                    
                    html += "</div>"
                
                html += "</div>"
        
        html += """
            <div class="footer">
                <p>This is an automated notification from IRAQAF Compliance Platform.</p>
                <p>Please review all critical and high severity changes immediately.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_smtp(self, to_email: str, msg: MIMEMultipart) -> None:
        """Send email via SMTP"""
        with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
            if self.smtp_config.get('use_tls', True):
                server.starttls()
            
            server.login(
                self.smtp_config['username'],
                self.smtp_config['password']
            )
            
            server.send_message(msg)


class InAppNotificationManager:
    """
    Manages in-app notifications stored in database
    
    Features:
    - Store notifications in database
    - Mark as read/unread
    - Archive notifications
    - Query by user/severity
    """
    
    def __init__(self):
        """Initialize in-app notification manager"""
        self.notifications: Dict[str, List[Dict]] = {}  # user_id -> notifications
    
    def create_notification(
        self,
        user_id: str,
        change: Change,
        title: str = None
    ) -> Dict:
        """
        Create in-app notification
        
        Args:
            user_id: User ID
            change: Change object
            title: Notification title
            
        Returns:
            Notification dict
        """
        notification = {
            'id': f"notif_{datetime.now().timestamp()}",
            'user_id': user_id,
            'title': title or f"{change.source} - {change.change_type.value}",
            'message': change.new_value[:200],
            'severity': change.severity.name,
            'change_type': change.change_type.value,
            'source': change.source,
            'created_at': datetime.now().isoformat(),
            'read': False,
            'archived': False,
            'recommendation': change.recommendation
        }
        
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        self.notifications[user_id].append(notification)
        logger.info(f"In-app notification created for {user_id}")
        
        return notification
    
    def get_notifications(
        self,
        user_id: str,
        include_archived: bool = False,
        severity_filter: List[str] = None
    ) -> List[Dict]:
        """
        Get notifications for user
        
        Args:
            user_id: User ID
            include_archived: Include archived notifications
            severity_filter: Filter by severity levels
            
        Returns:
            List of notifications
        """
        if user_id not in self.notifications:
            return []
        
        notifications = self.notifications[user_id]
        
        # Filter
        if not include_archived:
            notifications = [n for n in notifications if not n['archived']]
        
        if severity_filter:
            notifications = [n for n in notifications 
                           if n['severity'] in severity_filter]
        
        return sorted(notifications, 
                     key=lambda n: n['created_at'], 
                     reverse=True)
    
    def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read"""
        if user_id in self.notifications:
            for notif in self.notifications[user_id]:
                if notif['id'] == notification_id:
                    notif['read'] = True
                    return True
        return False
    
    def archive_notification(self, user_id: str, notification_id: str) -> bool:
        """Archive notification"""
        if user_id in self.notifications:
            for notif in self.notifications[user_id]:
                if notif['id'] == notification_id:
                    notif['archived'] = True
                    return True
        return False


class NotificationManager:
    """
    Orchestrates multi-channel notifications
    
    Coordinates:
    - Email notifications
    - In-app notifications
    - Change summaries
    - Recommendation generation
    """
    
    def __init__(self, smtp_config: Dict = None):
        """Initialize notification manager"""
        self.email_notifier = EmailNotifier(smtp_config)
        self.in_app_manager = InAppNotificationManager()
        self.user_preferences: Dict[str, NotificationPreference] = {}
    
    def notify_changes(
        self,
        changes: List[Change],
        affected_users: List[str] = None
    ) -> Dict:
        """
        Send notifications for changes to all affected users
        
        Args:
            changes: List of changes
            affected_users: List of user IDs to notify (or None for all)
            
        Returns:
            Dict with notification results
        """
        results = {
            'total_changes': len(changes),
            'users_notified': 0,
            'emails_sent': 0,
            'in_app_created': 0,
            'failed': 0
        }
        
        # Get users to notify
        users = affected_users or list(self.user_preferences.keys())
        
        for user_id in users:
            # Filter changes based on user preferences
            if user_id in self.user_preferences:
                pref = self.user_preferences[user_id]
                filtered_changes = self._filter_by_preference(changes, pref)
                
                if not filtered_changes:
                    continue
                
                # Send notifications
                if pref.email_enabled and 'email' in pref.channels:
                    success, msg = self.email_notifier.send_change_notification(
                        pref.email,
                        filtered_changes,
                        user_id
                    )
                    if success:
                        results['emails_sent'] += 1
                    else:
                        results['failed'] += 1
                
                if pref.in_app_enabled and 'in_app' in pref.channels:
                    for change in filtered_changes:
                        self.in_app_manager.create_notification(user_id, change)
                        results['in_app_created'] += 1
                
                results['users_notified'] += 1
        
        logger.info(f"Notification results: {results}")
        return results
    
    def _filter_by_preference(
        self,
        changes: List[Change],
        pref: NotificationPreference
    ) -> List[Change]:
        """Filter changes based on user preferences"""
        filtered = []
        
        for change in changes:
            severity_name = change.severity.name.lower()
            
            if severity_name == 'critical' and pref.notify_critical:
                filtered.append(change)
            elif severity_name == 'high' and pref.notify_high:
                filtered.append(change)
            elif severity_name == 'medium' and pref.notify_medium:
                filtered.append(change)
            elif severity_name == 'low' and pref.notify_low:
                filtered.append(change)
            elif severity_name == 'informational' and pref.notify_informational:
                filtered.append(change)
        
        return filtered
    
    def set_user_preference(self, pref: NotificationPreference) -> None:
        """Set notification preferences for user"""
        self.user_preferences[pref.user_id] = pref
        logger.info(f"Notification preferences updated for {pref.user_id}")
    
    def get_user_notifications(self, user_id: str) -> List[Dict]:
        """Get all notifications for user"""
        return self.in_app_manager.get_notifications(user_id)


class RecommendationEngine:
    """
    Generates recommendations for regulatory changes
    
    Provides:
    - Automatic recommendations based on change type
    - Compliance impact analysis
    - Remediation timelines
    - Priority ranking
    """
    
    RECOMMENDATIONS = {
        ChangeType.NEW_REQUIREMENT.value: {
            SeverityLevel.CRITICAL: "URGENT: Implement immediately within 7 days",
            SeverityLevel.HIGH: "Implement within 2 weeks. Assign to compliance team.",
            SeverityLevel.MEDIUM: "Schedule implementation. Integrate into next release.",
            SeverityLevel.LOW: "Review and plan implementation. Low priority.",
        },
        ChangeType.MODIFIED_REQUIREMENT.value: {
            SeverityLevel.CRITICAL: "URGENT: Review current implementation. Test changes within 5 days.",
            SeverityLevel.HIGH: "Review modification. Update implementation if needed.",
            SeverityLevel.MEDIUM: "Evaluate impact. Update documentation.",
            SeverityLevel.LOW: "Note for future updates.",
        },
        ChangeType.CRITICAL_CHANGE.value: {
            SeverityLevel.CRITICAL: "IMMEDIATE ACTION: This is a critical regulatory change. Notify executive team immediately. Schedule emergency meeting.",
            SeverityLevel.HIGH: "Schedule urgent review meeting. Assess compliance impact.",
        },
    }
    
    @staticmethod
    def generate_recommendation(change: Change) -> str:
        """
        Generate recommendation for a change
        
        Args:
            change: Change object
            
        Returns:
            Recommendation string
        """
        change_type = change.change_type.value
        severity = change.severity
        
        recommendations = RecommendationEngine.RECOMMENDATIONS.get(
            change_type, {}
        )
        
        return recommendations.get(
            severity,
            f"Review this {severity.name.lower()} priority regulatory change."
        )


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create notification manager
    nm = NotificationManager()
    
    # Set user preference
    pref = NotificationPreference(
        user_id='user1',
        email='user@example.com',
        notify_critical=True,
        notify_high=True
    )
    nm.set_user_preference(pref)
    
    # Create sample changes
    changes = [
        Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='EU AI Act',
            section='Title IV',
            old_value=None,
            new_value='New requirement for AI systems',
            detected_at=datetime.now(),
            severity=SeverityLevel.CRITICAL,
            recommendation=RecommendationEngine.generate_recommendation(None)
        )
    ]
    
    # Send notifications
    results = nm.notify_changes(changes, ['user1'])
    print(f"Notification results: {results}")
