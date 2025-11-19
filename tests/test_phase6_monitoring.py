"""
PHASE 6: Comprehensive Testing Suite

Tests for all Phase 6 monitoring components:
- Change detection
- Impact assessment
- Notification system
- Integrated monitoring
"""

import pytest
import json
from datetime import datetime, timedelta
from monitoring.change_detector import (
    ChangeDetector, ChangeDetectionResult, SeverityLevel, ChangeType
)
from monitoring.impact_assessor import (
    ImpactAssessor, ComplianceMetric, ComplianceStatus
)
from monitoring.notification_manager import (
    NotificationManager, NotificationPriority, NotificationChannel
)
from monitoring.integrated_monitoring_system import IntegratedMonitoringSystem


class TestChangeDetector:
    """Tests for change detection engine"""
    
    def test_detect_new_requirement(self):
        """Test detection of new requirements"""
        detector = ChangeDetector()
        
        previous = {"REQ-1": "Requirement 1"}
        current = {
            "REQ-1": "Requirement 1",
            "REQ-2": "Requirement 2 - mandatory requirement"
        }
        
        result = detector.analyze_changes("GDPR", previous, current)
        
        assert result.total_changes == 1
        assert result.critical_changes >= 0
        assert len(result.changes) == 1
        assert result.changes[0].change_type == ChangeType.NEW_REQUIREMENT

    def test_detect_modified_requirement(self):
        """Test detection of modified requirements"""
        detector = ChangeDetector()
        
        previous = {"REQ-1": "Original requirement"}
        current = {"REQ-1": "Updated requirement with new details"}
        
        result = detector.analyze_changes("GDPR", previous, current)
        
        assert result.total_changes == 1
        assert result.changes[0].change_type == ChangeType.REQUIREMENT_MODIFIED

    def test_detect_removed_requirement(self):
        """Test detection of removed requirements"""
        detector = ChangeDetector()
        
        previous = {
            "REQ-1": "Requirement 1",
            "REQ-2": "Requirement 2"
        }
        current = {"REQ-1": "Requirement 1"}
        
        result = detector.analyze_changes("GDPR", previous, current)
        
        assert result.total_changes == 1
        assert result.changes[0].change_type == ChangeType.REQUIREMENT_REMOVED

    def test_severity_assessment(self):
        """Test severity assessment"""
        detector = ChangeDetector()
        
        # Critical content
        critical_content = "All organizations must implement mandatory security controls"
        severity = detector._assess_requirement_severity(critical_content)
        
        assert severity == SeverityLevel.CRITICAL
        
        # Low content
        low_content = "Consider implementing optional enhancements"
        severity = detector._assess_requirement_severity(low_content)
        
        assert severity == SeverityLevel.LOW

    def test_change_hash_consistency(self):
        """Test hash computation consistency"""
        detector = ChangeDetector()
        
        content = "Test requirement content"
        hash1 = detector.compute_hash(content)
        hash2 = detector.compute_hash(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256


class TestImpactAssessor:
    """Tests for impact assessment engine"""
    
    def test_compliance_drift_detection(self):
        """Test compliance drift detection"""
        assessor = ImpactAssessor()
        
        previous_metric = ComplianceMetric(
            requirement_id="REQ-1",
            regulation="GDPR",
            previous_score=85.0,
            current_score=85.0,
            status_previous=ComplianceStatus.COMPLIANT,
            status_current=ComplianceStatus.COMPLIANT,
            evidence_count=5,
            gap_description=None,
            remediation_hours=0,
            remediation_cost=0
        )
        
        current_metric = ComplianceMetric(
            requirement_id="REQ-1",
            regulation="GDPR",
            previous_score=85.0,
            current_score=50.0,
            status_previous=ComplianceStatus.COMPLIANT,
            status_current=ComplianceStatus.PARTIALLY_COMPLIANT,
            evidence_count=3,
            gap_description="Partial implementation",
            remediation_hours=20,
            remediation_cost=3000
        )
        
        result = assessor.assess_compliance_drift(
            "GDPR",
            "test-system",
            [previous_metric],
            [current_metric]
        )
        
        assert len(result.drifts) > 0
        assert result.score_change < 0  # Compliance degraded

    def test_action_plan_generation(self):
        """Test action plan generation"""
        assessor = ImpactAssessor()
        
        metric = ComplianceMetric(
            requirement_id="REQ-1",
            regulation="GDPR",
            previous_score=0.0,
            current_score=0.0,
            status_previous=ComplianceStatus.UNKNOWN,
            status_current=ComplianceStatus.NON_COMPLIANT,
            evidence_count=0,
            gap_description="Requirement not implemented",
            remediation_hours=40,
            remediation_cost=6000
        )
        
        from monitoring.impact_assessor import DriftType, ComplianceDrift
        drift = ComplianceDrift(
            metric=metric,
            drift_type=DriftType.NEW_GAP,
            drift_magnitude=-100,
            risk_level="CRITICAL",
            affected_systems=["Data Storage"],
            remediation_priority=1
        )
        
        action_plan = assessor._create_action_plan([drift])
        
        assert len(action_plan) > 0
        assert action_plan[0]['priority'] == 1
        assert len(action_plan[0]['recommended_actions']) > 0


class TestNotificationManager:
    """Tests for notification system"""
    
    def test_notification_creation(self):
        """Test notification creation"""
        manager = NotificationManager()
        
        notifications = manager.create_change_notification(
            change_id="CHG-001",
            change_type="NEW_REQUIREMENT",
            severity="CRITICAL",
            regulation="GDPR",
            requirement_id="GDPR-4",
            affected_systems=["Data Storage"],
            description="New requirement",
            recipients=["admin@test.com"]
        )
        
        assert len(notifications) > 0
        assert all(n.priority == NotificationPriority.CRITICAL for n in notifications)

    def test_notification_channels(self):
        """Test channel selection based on priority"""
        manager = NotificationManager()
        
        # Critical gets multiple channels
        critical_channels = manager._determine_channels(NotificationPriority.CRITICAL)
        assert len(critical_channels) >= 3
        
        # Low priority gets fewer channels
        low_channels = manager._determine_channels(NotificationPriority.LOW)
        assert len(low_channels) == 1

    def test_daily_digest_creation(self):
        """Test daily digest creation"""
        manager = NotificationManager()
        
        # Create some notifications
        notifications = manager.create_change_notification(
            change_id="CHG-001",
            change_type="NEW_REQUIREMENT",
            severity="HIGH",
            regulation="GDPR",
            requirement_id="GDPR-1",
            affected_systems=["System"],
            description="Test",
            recipients=["user@test.com"]
        )
        
        manager.send_notifications(notifications)
        
        # Create digest
        digest = manager.create_daily_digest(
            recipient="user@test.com",
            notifications=manager.notification_history,
            period_start=datetime.now() - timedelta(days=1),
            period_end=datetime.now()
        )
        
        assert digest.digest_type == "DAILY"
        assert digest.total_notifications > 0


class TestIntegratedMonitoring:
    """Tests for integrated monitoring system"""
    
    def test_monitoring_cycle_execution(self):
        """Test complete monitoring cycle"""
        system = IntegratedMonitoringSystem()
        
        previous_state = {
            "GDPR": {"REQ-1": "Requirement 1"}
        }
        current_state = {
            "GDPR": {
                "REQ-1": "Updated requirement",
                "REQ-2": "New mandatory requirement"
            }
        }
        
        previous_scores = {"GDPR": {"REQ-1": 85}}
        current_scores = {"GDPR": {"REQ-1": 90, "REQ-2": 30}}
        
        report = system.execute_monitoring_cycle(
            system_id="test-system",
            previous_state=previous_state,
            current_state=current_state,
            previous_compliance_scores=previous_scores,
            current_compliance_scores=current_scores,
            recipients=["admin@test.com"]
        )
        
        assert report.total_changes > 0
        assert report.monitoring_status == "COMPLETE"
        assert report.next_monitoring_run > report.report_date

    def test_monitoring_history(self):
        """Test monitoring history tracking"""
        system = IntegratedMonitoringSystem()
        
        # Execute multiple cycles
        for i in range(3):
            system.execute_monitoring_cycle(
                system_id="test",
                previous_state={"GDPR": {"R1": f"Req {i}"}},
                current_state={"GDPR": {"R1": f"Req {i+1}"}},
                previous_compliance_scores={"GDPR": {"R1": 80}},
                current_compliance_scores={"GDPR": {"R1": 85}},
                recipients=["test@test.com"]
            )
        
        history = system.get_monitoring_history(days=1)
        assert len(history) == 3


class TestJSONExport:
    """Tests for JSON export functionality"""
    
    def test_change_detection_json_export(self):
        """Test JSON export of changes"""
        detector = ChangeDetector()
        
        result = detector.analyze_changes(
            "GDPR",
            {"R1": "Old"},
            {"R1": "New", "R2": "Added"}
        )
        
        json_str = detector.export_changes_to_json(result)
        data = json.loads(json_str)
        
        assert data['total_changes'] > 0
        assert 'changes' in data

    def test_impact_assessment_json_export(self):
        """Test JSON export of impact assessment"""
        assessor = ImpactAssessor()
        
        metric = ComplianceMetric(
            requirement_id="REQ-1",
            regulation="GDPR",
            previous_score=80,
            current_score=80,
            status_previous=ComplianceStatus.COMPLIANT,
            status_current=ComplianceStatus.COMPLIANT,
            evidence_count=4,
            gap_description=None,
            remediation_hours=0,
            remediation_cost=0
        )
        
        result = assessor.assess_compliance_drift(
            "GDPR",
            "system",
            [metric],
            [metric]
        )
        
        json_str = assessor.export_assessment_to_json(result)
        data = json.loads(json_str)
        
        assert 'total_requirements' in data
        assert 'action_plan' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
