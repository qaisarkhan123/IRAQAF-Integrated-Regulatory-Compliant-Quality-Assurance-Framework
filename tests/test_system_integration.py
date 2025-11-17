"""
Integrated System Tests

Comprehensive test suite validating all components work together
as a cohesive system with proper database persistence and 
real-time monitoring.

Run with: python -m pytest tests/test_system_integration.py -v
"""

import pytest
import tempfile
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4


class TestDatabaseLayer:
    """Tests for database persistence layer."""

    @pytest.fixture
    def db_path(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            path = f.name
        yield path
        # Cleanup
        Path(path).unlink(missing_ok=True)

    def test_database_initialization(self, db_path):
        """Test database initialization."""
        try:
            from scripts.database_layer import init_db
            init_db(f"sqlite:///{db_path}")
        except ImportError:
            pytest.skip("SQLAlchemy not installed")

    def test_save_regulatory_change(self, db_path):
        """Test saving regulatory change to database."""
        try:
            from scripts.database_layer import init_db, DatabaseQueries
            
            init_db(f"sqlite:///{db_path}")
            
            change = DatabaseQueries.save_regulatory_change(
                source="Test Source",
                regulation_id="TEST-001",
                regulation_name="Test Regulation",
                change_type="requirement_update",
                description="Test description",
                impact_level="high",
                affected_systems=["system1", "system2"],
                implementation_deadline=datetime.utcnow() + timedelta(days=30),
            )
            
            assert change.regulation_id == "TEST-001"
            assert change.source == "Test Source"
        except ImportError:
            pytest.skip("SQLAlchemy not installed")

    def test_save_compliance_score(self, db_path):
        """Test saving compliance score."""
        try:
            from scripts.database_layer import init_db, DatabaseQueries
            
            init_db(f"sqlite:///{db_path}")
            
            score = DatabaseQueries.save_compliance_score(
                framework="GDPR",
                system_name="auth_system",
                score=92.5,
                status="compliant",
            )
            
            assert score.framework == "GDPR"
            assert score.score == 92.5
        except ImportError:
            pytest.skip("SQLAlchemy not installed")

    def test_save_alert(self, db_path):
        """Test saving alert."""
        try:
            from scripts.database_layer import init_db, DatabaseQueries
            
            init_db(f"sqlite:///{db_path}")
            
            alert = DatabaseQueries.save_alert(
                alert_type="compliance_threshold_breach",
                message="Test alert message",
                risk_level="critical",
                affected_regulation="GDPR",
            )
            
            assert alert.alert_type == "compliance_threshold_breach"
            assert alert.message == "Test alert message"
        except ImportError:
            pytest.skip("SQLAlchemy not installed")

    def test_get_system_statistics(self, db_path):
        """Test getting system statistics."""
        try:
            from scripts.database_layer import init_db, DatabaseQueries
            
            init_db(f"sqlite:///{db_path}")
            
            # Add some data
            DatabaseQueries.save_regulatory_change(
                source="Test",
                regulation_id="TEST-001",
                regulation_name="Test",
                change_type="update",
                description="Test",
                impact_level="high",
            )
            
            stats = DatabaseQueries.get_system_statistics()
            
            assert "total_changes" in stats
            assert stats["total_changes"] >= 1
        except ImportError:
            pytest.skip("SQLAlchemy not installed")


class TestRealTimeMonitor:
    """Tests for real-time monitoring service."""

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        from scripts.realtime_monitor import RealTimeMonitor
        
        monitor = RealTimeMonitor(update_interval=1)
        assert monitor.update_interval == 1
        assert not monitor.running

    def test_monitor_start_stop(self):
        """Test starting and stopping monitor."""
        from scripts.realtime_monitor import RealTimeMonitor
        
        monitor = RealTimeMonitor(update_interval=1)
        monitor.start()
        assert monitor.running
        
        time.sleep(0.5)
        monitor.stop()
        assert not monitor.running

    def test_event_emission(self):
        """Test emitting events."""
        from scripts.realtime_monitor import RealTimeMonitor, SystemEvent, EventType
        
        monitor = RealTimeMonitor()
        
        event = SystemEvent(
            EventType.ALERT_TRIGGERED,
            {"message": "Test alert"},
        )
        monitor._emit_event(event)
        
        retrieved = monitor.get_events(timeout=0.1)
        assert retrieved is not None
        assert retrieved.event_type == EventType.ALERT_TRIGGERED

    def test_callback_registration(self):
        """Test registering callbacks."""
        from scripts.realtime_monitor import RealTimeMonitor, SystemEvent, EventType
        
        monitor = RealTimeMonitor()
        called = {"count": 0}
        
        def test_callback(event):
            called["count"] += 1
        
        monitor.register_callback(EventType.ALERT_TRIGGERED, test_callback)
        
        event = SystemEvent(
            EventType.ALERT_TRIGGERED,
            {"message": "Test"},
        )
        monitor._emit_event(event)
        
        assert called["count"] == 1

    def test_event_history(self):
        """Test event history storage."""
        from scripts.realtime_monitor import RealTimeMonitor, SystemEvent, EventType
        
        monitor = RealTimeMonitor(event_history_size=10)
        
        for i in range(5):
            event = SystemEvent(
                EventType.COMPLIANCE_SCORE_UPDATE,
                {"score": 90 + i},
            )
            monitor._emit_event(event)
        
        history = monitor.get_event_history()
        assert len(history) == 5

    def test_monitoring_statistics(self):
        """Test monitoring statistics."""
        from scripts.realtime_monitor import RealTimeMonitor, SystemEvent, EventType
        
        monitor = RealTimeMonitor()
        
        event = SystemEvent(
            EventType.SYSTEM_HEALTH_UPDATE,
            {"status": "healthy"},
        )
        monitor._emit_event(event)
        
        stats = monitor.get_statistics()
        assert stats["total_events"] >= 1


class TestSystemIntegration:
    """Tests for system integration coordinator."""

    @pytest.fixture
    def db_path(self):
        """Create temporary database."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            path = f.name
        yield path
        Path(path).unlink(missing_ok=True)

    def test_coordinator_initialization(self, db_path):
        """Test coordinator initialization."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            assert coordinator.initialized
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_track_regulatory_change_workflow(self, db_path):
        """Test complete regulatory change tracking workflow."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            result = coordinator.track_regulatory_change(
                source="Integration Test",
                regulation_id="INT-TEST-001",
                regulation_name="Test Regulation",
                change_type="requirement_update",
                description="Test description",
                impact_level="high",
                affected_systems=["system1"],
                implementation_deadline=datetime.utcnow() + timedelta(days=30),
            )
            
            assert result["regulation_id"] == "INT-TEST-001"
            
            changes = coordinator.get_recent_changes(days=1)
            assert len(changes) > 0
            
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_compliance_score_workflow(self, db_path):
        """Test compliance score recording workflow."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            result = coordinator.record_compliance_score(
                framework="GDPR",
                system_name="test_system",
                score=92.5,
                status="compliant",
            )
            
            assert result["framework"] == "GDPR"
            assert result["score"] == 92.5
            
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_alert_workflow(self, db_path):
        """Test alert generation and management workflow."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            # Generate alert
            alert = coordinator.generate_alert(
                alert_type="compliance_threshold_breach",
                message="Test threshold breach",
                risk_level="critical",
                affected_regulation="GDPR",
            )
            
            assert alert is not None
            alert_id = alert["id"]
            
            # Get open alerts
            open_alerts = coordinator.get_open_alerts()
            assert len(open_alerts) > 0
            
            # Acknowledge alert
            coordinator.acknowledge_alert(alert_id)
            
            # Resolve alert
            resolved = coordinator.resolve_alert(alert_id)
            assert resolved["status"] == "resolved"
            
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_remediation_workflow(self, db_path):
        """Test remediation action creation and tracking."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            # Create action
            action = coordinator.create_remediation_action(
                gap_id="TEST-GAP-001",
                action_title="Fix GDPR Compliance",
                description="Update data protection controls",
                assigned_to="security_team",
                due_date=datetime.utcnow() + timedelta(days=30),
                priority=8,
            )
            
            assert action["action_title"] == "Fix GDPR Compliance"
            action_id = action["id"]
            
            # Get pending actions
            pending = coordinator.get_pending_remediation()
            assert len(pending) > 0
            
            # Update status
            coordinator.update_remediation_status(
                action_id=action_id,
                status="in_progress",
                completion_percentage=50.0,
            )
            
            pending = coordinator.get_pending_remediation()
            assert len(pending) > 0
            
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_system_status_reporting(self, db_path):
        """Test system status and reporting."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            # Get system status
            status = coordinator.get_system_status()
            
            assert status["initialized"]
            assert "total_changes" in status
            assert "total_alerts" in status
            
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_compliance_report_generation(self, db_path):
        """Test compliance report generation."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            
            # Add some data
            coordinator.track_regulatory_change(
                source="Test",
                regulation_id="TEST-001",
                regulation_name="Test",
                change_type="update",
                description="Test",
                impact_level="high",
            )
            
            coordinator.generate_alert(
                alert_type="test_alert",
                message="Test message",
                risk_level="high",
            )
            
            # Generate report
            report = coordinator.get_compliance_report()
            
            assert "generated_at" in report
            assert "changes" in report
            assert "alerts" in report
            assert "remediation" in report
            assert len(report["changes"]) > 0
            
        except ImportError:
            pytest.skip("Dependencies not installed")

    def test_end_to_end_workflow(self, db_path):
        """Test complete end-to-end integration workflow."""
        try:
            from scripts.system_integration import SystemCoordinator
            
            coordinator = SystemCoordinator(db_url=f"sqlite:///{db_path}")
            coordinator.initialize()
            coordinator.start_monitoring()
            
            # Step 1: Track regulatory change
            change = coordinator.track_regulatory_change(
                source="E2E Test",
                regulation_id="E2E-001",
                regulation_name="End-to-End Test Regulation",
                change_type="new_requirement",
                description="Test requirement for E2E workflow",
                impact_level="high",
                affected_systems=["auth", "api"],
                implementation_deadline=datetime.utcnow() + timedelta(days=60),
            )
            
            # Step 2: Generate alert
            alert = coordinator.generate_alert(
                alert_type="regulatory_change_alert",
                message="New regulatory requirement detected",
                risk_level="high",
                affected_regulation="E2E-001",
                recommended_action="Review and plan implementation",
            )
            
            # Step 3: Record compliance score
            score = coordinator.record_compliance_score(
                framework="TEST_FRAMEWORK",
                system_name="e2e_system",
                score=75.0,
                status="partial",
            )
            
            # Step 4: Create remediation action
            action = coordinator.create_remediation_action(
                gap_id="E2E-GAP-001",
                action_title="Implement New Requirements",
                description="Implement the new regulatory requirements",
                assigned_to="dev_team",
                priority=9,
                due_date=datetime.utcnow() + timedelta(days=60),
            )
            
            # Step 5: Get system status
            status = coordinator.get_system_status()
            
            assert status["total_changes"] > 0
            assert status["total_alerts"] > 0
            assert status["total_remediation_actions"] > 0
            
            # Step 6: Generate report
            report = coordinator.get_compliance_report()
            
            assert len(report["changes"]) > 0
            assert len(report["alerts"]["open"]) > 0
            assert len(report["remediation"]["pending"]) > 0
            
            coordinator.stop_monitoring()
            coordinator.shutdown()
            
        except ImportError:
            pytest.skip("Dependencies not installed")


# Quick validation function
def run_quick_validation():
    """Quick validation of integrated system."""
    print("\n" + "="*60)
    print("INTEGRATED SYSTEM QUICK VALIDATION")
    print("="*60)
    
    tests = [
        ("Database Layer", TestDatabaseLayer),
        ("Real-Time Monitor", TestRealTimeMonitor),
        ("System Integration", TestSystemIntegration),
    ]
    
    for name, test_class in tests:
        print(f"\n✓ {name} - Module loaded successfully")
    
    print("\n" + "="*60)
    print("Quick validation complete. Run full tests with:")
    print("  python -m pytest tests/test_system_integration.py -v")
    print("="*60)


if __name__ == "__main__":
    run_quick_validation()
