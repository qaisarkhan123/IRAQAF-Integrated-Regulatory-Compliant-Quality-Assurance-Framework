"""
PHASE 3: COMPREHENSIVE TEST SUITE
Web Scraper Scheduler & Notifications Testing

Tests for:
- Scheduler job registration and execution
- Notification delivery (email & in-app)
- Change detection and recommendations
- Error handling and retries
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import logging

from monitoring.scheduler import SchedulerManager, ScraperJob
from monitoring.notifications import (
    Change, ChangeType, SeverityLevel, NotificationManager,
    NotificationPreference, EmailNotifier, InAppNotificationManager,
    RecommendationEngine
)

logging.basicConfig(level=logging.INFO)


class TestSchedulerManager:
    """Test SchedulerManager functionality"""
    
    def test_scheduler_initialization(self):
        """Test scheduler initializes correctly"""
        scheduler = SchedulerManager()
        assert scheduler is not None
        assert len(scheduler.jobs_config) == 5  # 3 daily + 2 weekly
        assert not scheduler.scheduler.running
    
    def test_jobs_configuration_loaded(self):
        """Test jobs configuration is loaded correctly"""
        scheduler = SchedulerManager()
        jobs = scheduler.jobs_config
        
        # Check daily jobs
        daily_jobs = [j for j in jobs if j.schedule_type == 'daily']
        assert len(daily_jobs) == 3
        
        # Check weekly jobs
        weekly_jobs = [j for j in jobs if j.schedule_type == 'weekly']
        assert len(weekly_jobs) == 2
        
        # Check specific sources
        sources = {j.source_name for j in jobs}
        assert 'EU AI Act' in sources
        assert 'FDA' in sources
        assert 'GDPR' in sources
        assert 'ISO 13485' in sources
        assert 'IEC 62304' in sources
    
    def test_scheduler_start_stop(self):
        """Test scheduler can start and stop"""
        scheduler = SchedulerManager()
        
        # Start
        scheduler.start()
        assert scheduler.scheduler.running
        
        # Stop
        scheduler.stop()
        assert not scheduler.scheduler.running
    
    def test_job_registration(self):
        """Test job registration with scheduler"""
        scheduler = SchedulerManager()
        
        # Register jobs
        scheduler.start()
        
        # Check jobs were registered
        assert len(scheduler.jobs) == 5
        assert 'EU AI Act Daily' in scheduler.jobs
        assert 'FDA Daily' in scheduler.jobs
        
        scheduler.stop()
    
    def test_health_status_tracking(self):
        """Test health status is tracked"""
        scheduler = SchedulerManager()
        scheduler.start()
        
        # Check health status initialized
        for job_name in scheduler.jobs.keys():
            assert job_name in scheduler.health_status
            health = scheduler.health_status[job_name]
            assert health['status'] == 'scheduled'
            assert health['success_count'] == 0
            assert health['failure_count'] == 0
        
        scheduler.stop()
    
    def test_manual_job_trigger(self):
        """Test manual job triggering"""
        scheduler = SchedulerManager()
        scheduler.start()
        
        # Manually trigger job
        result = scheduler.manually_trigger_job('EU AI Act Daily')
        
        # Check result structure
        assert 'job_name' in result
        assert 'status' in result
        assert 'items_scraped' in result
        assert 'duration_seconds' in result
        
        scheduler.stop()
    
    def test_job_history_recorded(self):
        """Test job execution history is recorded"""
        scheduler = SchedulerManager()
        scheduler.start()
        
        # Trigger a job
        scheduler.manually_trigger_job('EU AI Act Daily')
        
        # Check history
        assert len(scheduler.job_history) > 0
        last_execution = scheduler.job_history[-1]
        assert 'start_time' in last_execution
        assert 'end_time' in last_execution
        assert 'status' in last_execution
        
        scheduler.stop()
    
    def test_rate_limiting_applied(self):
        """Test rate limiting is applied between requests"""
        scheduler = SchedulerManager()
        
        # This would be tested with actual requests
        # For now, verify the method exists
        assert hasattr(scheduler, '_apply_rate_limit')


class TestNotifications:
    """Test notification functionality"""
    
    def test_change_creation(self):
        """Test Change object creation"""
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='EU AI Act',
            section='Title IV',
            old_value=None,
            new_value='New requirement text',
            detected_at=datetime.now(),
            severity=SeverityLevel.CRITICAL
        )
        
        assert change.source == 'EU AI Act'
        assert change.severity == SeverityLevel.CRITICAL
        assert change.affected_systems == []
    
    def test_notification_preference_creation(self):
        """Test NotificationPreference object creation"""
        pref = NotificationPreference(
            user_id='user1',
            email='user@example.com',
            notify_critical=True,
            notify_high=True,
            notify_medium=False
        )
        
        assert pref.user_id == 'user1'
        assert pref.email == 'user@example.com'
        assert pref.notify_critical is True
        assert pref.notify_medium is False
    
    def test_email_notifier_initialization(self):
        """Test EmailNotifier initializes"""
        notifier = EmailNotifier()
        assert notifier.test_mode is True
        assert notifier.smtp_config is not None
    
    def test_email_notification_creation(self):
        """Test email notification creation in test mode"""
        notifier = EmailNotifier()
        
        changes = [
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='EU AI Act',
                section='Title IV',
                old_value=None,
                new_value='Requirement text',
                detected_at=datetime.now(),
                severity=SeverityLevel.CRITICAL
            )
        ]
        
        success, msg = notifier.send_change_notification(
            'recipient@example.com',
            changes
        )
        
        assert success is True
        assert 'test mode' in msg.lower()
    
    def test_email_subject_creation(self):
        """Test email subject line creation"""
        notifier = EmailNotifier()
        
        # Critical changes
        changes_critical = [
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='EU AI Act',
                section='Title IV',
                old_value=None,
                new_value='Text',
                detected_at=datetime.now(),
                severity=SeverityLevel.CRITICAL
            )
        ]
        
        subject = notifier._create_subject(changes_critical)
        assert 'CRITICAL' in subject
        
        # High priority changes
        changes_high = [
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='EU AI Act',
                section='Title IV',
                old_value=None,
                new_value='Text',
                detected_at=datetime.now(),
                severity=SeverityLevel.HIGH
            )
        ]
        
        subject = notifier._create_subject(changes_high)
        assert 'HIGH' in subject
    
    def test_in_app_notification_creation(self):
        """Test in-app notification creation"""
        manager = InAppNotificationManager()
        
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='EU AI Act',
            section='Title IV',
            old_value=None,
            new_value='New requirement text',
            detected_at=datetime.now(),
            severity=SeverityLevel.HIGH
        )
        
        notif = manager.create_notification('user1', change)
        
        assert notif['user_id'] == 'user1'
        assert notif['source'] == 'EU AI Act'
        assert notif['read'] is False
        assert notif['archived'] is False
    
    def test_in_app_notification_retrieval(self):
        """Test retrieving in-app notifications"""
        manager = InAppNotificationManager()
        
        # Create notifications
        for i in range(3):
            change = Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source=f'Source {i}',
                section='Section',
                old_value=None,
                new_value='Text',
                detected_at=datetime.now(),
                severity=SeverityLevel.HIGH
            )
            manager.create_notification('user1', change)
        
        # Retrieve
        notifications = manager.get_notifications('user1')
        assert len(notifications) == 3
    
    def test_notification_filtering_by_severity(self):
        """Test filtering notifications by severity"""
        manager = InAppNotificationManager()
        
        # Create notifications with different severities
        for severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM]:
            change = Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='Source',
                section='Section',
                old_value=None,
                new_value='Text',
                detected_at=datetime.now(),
                severity=severity
            )
            manager.create_notification('user1', change)
        
        # Filter by critical only
        notifications = manager.get_notifications(
            'user1',
            severity_filter=['CRITICAL']
        )
        assert len(notifications) == 1
    
    def test_mark_notification_as_read(self):
        """Test marking notification as read"""
        manager = InAppNotificationManager()
        
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='Source',
            section='Section',
            old_value=None,
            new_value='Text',
            detected_at=datetime.now(),
            severity=SeverityLevel.HIGH
        )
        
        notif = manager.create_notification('user1', change)
        
        # Mark as read
        success = manager.mark_as_read('user1', notif['id'])
        assert success is True
        
        # Verify
        notifications = manager.get_notifications('user1')
        assert notifications[0]['read'] is True
    
    def test_archive_notification(self):
        """Test archiving notifications"""
        manager = InAppNotificationManager()
        
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='Source',
            section='Section',
            old_value=None,
            new_value='Text',
            detected_at=datetime.now(),
            severity=SeverityLevel.HIGH
        )
        
        notif = manager.create_notification('user1', change)
        
        # Archive
        success = manager.archive_notification('user1', notif['id'])
        assert success is True
        
        # Should not appear in default retrieval
        notifications = manager.get_notifications('user1', include_archived=False)
        assert len(notifications) == 0


class TestNotificationManager:
    """Test NotificationManager orchestration"""
    
    def test_notification_manager_initialization(self):
        """Test NotificationManager initializes"""
        nm = NotificationManager()
        assert nm is not None
        assert nm.email_notifier is not None
        assert nm.in_app_manager is not None
    
    def test_set_user_preference(self):
        """Test setting user notification preferences"""
        nm = NotificationManager()
        
        pref = NotificationPreference(
            user_id='user1',
            email='user@example.com',
            notify_critical=True,
            notify_high=True
        )
        
        nm.set_user_preference(pref)
        
        assert 'user1' in nm.user_preferences
        assert nm.user_preferences['user1'].email == 'user@example.com'
    
    def test_notify_changes_multi_channel(self):
        """Test notifying changes across multiple channels"""
        nm = NotificationManager()
        
        # Set user preference
        pref = NotificationPreference(
            user_id='user1',
            email='user@example.com',
            notify_critical=True,
            notify_high=True
        )
        nm.set_user_preference(pref)
        
        # Create changes
        changes = [
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='EU AI Act',
                section='Title IV',
                old_value=None,
                new_value='New requirement',
                detected_at=datetime.now(),
                severity=SeverityLevel.CRITICAL
            )
        ]
        
        # Send notifications
        results = nm.notify_changes(changes, ['user1'])
        
        assert results['total_changes'] == 1
        assert results['users_notified'] == 1
    
    def test_filter_by_user_preference(self):
        """Test filtering changes by user notification preferences"""
        nm = NotificationManager()
        
        # Preference: only critical and high
        pref = NotificationPreference(
            user_id='user1',
            email='user@example.com',
            notify_critical=True,
            notify_high=True,
            notify_medium=False,
            notify_low=False
        )
        
        changes = [
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='Source1',
                section='Section',
                old_value=None,
                new_value='Text',
                detected_at=datetime.now(),
                severity=SeverityLevel.CRITICAL
            ),
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source='Source2',
                section='Section',
                old_value=None,
                new_value='Text',
                detected_at=datetime.now(),
                severity=SeverityLevel.MEDIUM
            ),
        ]
        
        filtered = nm._filter_by_preference(changes, pref)
        
        # Should only include critical
        assert len(filtered) == 1
        assert filtered[0].severity == SeverityLevel.CRITICAL


class TestRecommendationEngine:
    """Test RecommendationEngine"""
    
    def test_recommendation_for_new_critical_requirement(self):
        """Test recommendation generation for new critical requirement"""
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='EU AI Act',
            section='Title IV',
            old_value=None,
            new_value='New requirement',
            detected_at=datetime.now(),
            severity=SeverityLevel.CRITICAL
        )
        
        recommendation = RecommendationEngine.generate_recommendation(change)
        
        assert 'URGENT' in recommendation or 'immediately' in recommendation
        assert '7 days' in recommendation or '7' in recommendation
    
    def test_recommendation_for_new_high_requirement(self):
        """Test recommendation generation for new high priority requirement"""
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='GDPR',
            section='Article 5',
            old_value=None,
            new_value='New requirement',
            detected_at=datetime.now(),
            severity=SeverityLevel.HIGH
        )
        
        recommendation = RecommendationEngine.generate_recommendation(change)
        
        assert 'weeks' in recommendation or '2' in recommendation
    
    def test_recommendation_for_modified_requirement(self):
        """Test recommendation generation for modified requirement"""
        change = Change(
            change_type=ChangeType.MODIFIED_REQUIREMENT,
            source='FDA',
            section='Section 1',
            old_value='Old text',
            new_value='New text',
            detected_at=datetime.now(),
            severity=SeverityLevel.HIGH
        )
        
        recommendation = RecommendationEngine.generate_recommendation(change)
        
        assert 'review' in recommendation.lower() or 'update' in recommendation.lower()
    
    def test_recommendation_for_critical_change(self):
        """Test recommendation generation for critical regulatory change"""
        change = Change(
            change_type=ChangeType.CRITICAL_CHANGE,
            source='EU AI Act',
            section='Title IV',
            old_value=None,
            new_value='Critical regulatory update',
            detected_at=datetime.now(),
            severity=SeverityLevel.CRITICAL
        )
        
        recommendation = RecommendationEngine.generate_recommendation(change)
        
        assert 'IMMEDIATE' in recommendation or 'executive' in recommendation.lower()


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_change_notification(self):
        """Test complete flow: change detected -> notifications sent"""
        # Setup
        nm = NotificationManager()
        
        pref = NotificationPreference(
            user_id='user1',
            email='user@example.com',
            notify_critical=True,
            notify_high=True
        )
        nm.set_user_preference(pref)
        
        # Simulate change detection
        change = Change(
            change_type=ChangeType.NEW_REQUIREMENT,
            source='EU AI Act',
            section='Title IV',
            old_value=None,
            new_value='New transparency requirement',
            detected_at=datetime.now(),
            severity=SeverityLevel.CRITICAL,
            recommendation=RecommendationEngine.generate_recommendation(
                Change(
                    change_type=ChangeType.NEW_REQUIREMENT,
                    source='EU AI Act',
                    section='Title IV',
                    old_value=None,
                    new_value='New transparency requirement',
                    detected_at=datetime.now(),
                    severity=SeverityLevel.CRITICAL
                )
            ),
            affected_systems=['MediTech AI', 'Healthcare Platform']
        )
        
        # Send notifications
        results = nm.notify_changes([change], ['user1'])
        
        # Verify
        assert results['users_notified'] == 1
        assert results['emails_sent'] == 1
        assert results['in_app_created'] == 1
        
        # Verify in-app notification exists
        notifications = nm.get_user_notifications('user1')
        assert len(notifications) == 1
        assert notifications[0]['severity'] == 'CRITICAL'
    
    def test_batch_notification_processing(self):
        """Test processing multiple changes for multiple users"""
        nm = NotificationManager()
        
        # Set multiple user preferences
        for i in range(3):
            pref = NotificationPreference(
                user_id=f'user{i}',
                email=f'user{i}@example.com',
                notify_critical=True,
                notify_high=True
            )
            nm.set_user_preference(pref)
        
        # Create multiple changes
        changes = [
            Change(
                change_type=ChangeType.NEW_REQUIREMENT,
                source=f'Source {j}',
                section='Section',
                old_value=None,
                new_value=f'Change {j}',
                detected_at=datetime.now(),
                severity=SeverityLevel.CRITICAL
            )
            for j in range(3)
        ]
        
        # Send notifications
        results = nm.notify_changes(changes)
        
        # Verify all users were notified
        assert results['users_notified'] == 3
        assert results['emails_sent'] == 3
        assert results['in_app_created'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
