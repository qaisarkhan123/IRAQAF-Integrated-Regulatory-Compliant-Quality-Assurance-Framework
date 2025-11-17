"""
Test and validation module for new regulatory features.
Comprehensive tests for advanced monitoring, UI components, and compliance checks.
"""

import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any


class TestRegulatoryChangeTracker(unittest.TestCase):
    """Tests for RegulatoryChangeTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.advanced_regulatory_monitor import RegulatoryChangeTracker
        self.tracker = RegulatoryChangeTracker()
    
    def test_add_change(self):
        """Test adding a regulatory change."""
        change = self.tracker.add_change(
            source="Test Source",
            regulation_id="TST-001",
            regulation_name="Test Regulation",
            change_type="requirement_update",
            description="Test change",
            impact_level="high",
            affected_systems=["sys1", "sys2"]
        )
        
        self.assertIsNotNone(change.change_id)
        self.assertEqual(change.regulation_name, "Test Regulation")
        self.assertEqual(change.impact_level, "high")
        self.assertEqual(len(self.tracker.changes), 1)
    
    def test_get_critical_changes(self):
        """Test retrieving critical changes."""
        self.tracker.add_change(
            source="Test", regulation_id="TST-001", regulation_name="Critical Change",
            change_type="update", description="desc", impact_level="critical",
            affected_systems=["sys1"]
        )
        
        self.tracker.add_change(
            source="Test", regulation_id="TST-002", regulation_name="Minor Change",
            change_type="update", description="desc", impact_level="low",
            affected_systems=["sys1"]
        )
        
        critical = self.tracker.get_critical_changes()
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0].regulation_name, "Critical Change")


class TestComplianceTrendAnalyzer(unittest.TestCase):
    """Tests for ComplianceTrendAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.advanced_regulatory_monitor import ComplianceTrendAnalyzer
        self.analyzer = ComplianceTrendAnalyzer()
    
    def test_record_compliance_score(self):
        """Test recording compliance score."""
        trend = self.analyzer.record_compliance_score("GDPR", 85.0)
        
        self.assertEqual(trend.compliance_score, 85.0)
        self.assertEqual(trend.metric_name, "GDPR")
        self.assertIsNotNone(trend.timestamp)
    
    def test_trend_direction_detection(self):
        """Test trend direction detection."""
        # Record improving trend
        self.analyzer.record_compliance_score("HIPAA", 70.0)
        self.analyzer.record_compliance_score("HIPAA", 75.0)
        self.analyzer.record_compliance_score("HIPAA", 80.0)
        
        analysis = self.analyzer.get_trend_analysis("HIPAA")
        
        self.assertEqual(analysis["current_score"], 80.0)
        self.assertIn(analysis["trend_direction"], ["improving", "stable"])


class TestAutomatedAlertGenerator(unittest.TestCase):
    """Tests for AutomatedAlertGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.advanced_regulatory_monitor import AutomatedAlertGenerator
        self.generator = AutomatedAlertGenerator()
    
    def test_generate_alert(self):
        """Test generating an alert."""
        alert = self.generator.generate_alert(
            alert_type="test_alert",
            affected_regulation="TEST",
            message="Test message",
            recommended_action="Test action",
            risk_level="high"
        )
        
        self.assertIsNotNone(alert.alert_id)
        self.assertEqual(alert.alert_type, "test_alert")
        self.assertEqual(alert.status, "open")
    
    def test_alert_acknowledgment(self):
        """Test alert acknowledgment."""
        alert = self.generator.generate_alert(
            alert_type="test",
            affected_regulation="TEST",
            message="msg",
            recommended_action="act",
            risk_level="medium"
        )
        
        result = self.generator.acknowledge_alert(alert.alert_id)
        self.assertTrue(result)
        self.assertEqual(alert.status, "acknowledged")
    
    def test_get_critical_alerts(self):
        """Test retrieving critical alerts."""
        self.generator.generate_alert(
            alert_type="test1", affected_regulation="T1", message="m", 
            recommended_action="a", risk_level="critical"
        )
        
        self.generator.generate_alert(
            alert_type="test2", affected_regulation="T2", message="m",
            recommended_action="a", risk_level="low"
        )
        
        critical = self.generator.get_critical_alerts()
        self.assertEqual(len(critical), 1)


class TestComplianceValidator(unittest.TestCase):
    """Tests for ComplianceValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.advanced_compliance_checks import ComplianceValidator
        self.validator = ComplianceValidator()
    
    def test_validate_system_compliance(self):
        """Test system compliance validation."""
        result = self.validator.validate_system_compliance(
            system_name="test_system",
            framework="GDPR",
            controls={
                "lawful_basis": "compliant",
                "data_protection": "compliant",
                "privacy_by_design": "non_compliant",
                "data_subject_rights": "compliant"
            }
        )
        
        self.assertIn("compliance_percentage", result)
        self.assertIn("findings", result)
        self.assertGreater(result["compliance_percentage"], 0)
    
    def test_compliance_level_determination(self):
        """Test compliance level determination."""
        result = self.validator.validate_system_compliance(
            system_name="test_system",
            framework="GDPR",
            controls={
                "lawful_basis": "compliant",
                "data_protection": "compliant",
                "privacy_by_design": "compliant",
                "data_subject_rights": "compliant"
            }
        )
        
        self.assertEqual(result["compliance_level"], "full")


class TestComplianceGapAnalyzer(unittest.TestCase):
    """Tests for ComplianceGapAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.advanced_compliance_checks import ComplianceGapAnalyzer
        self.analyzer = ComplianceGapAnalyzer()
    
    def test_identify_gaps(self):
        """Test gap identification."""
        gaps = self.analyzer.identify_gaps(
            framework="GDPR",
            current_state={"data_protection": "partial", "dpia": "none"},
            required_state={"data_protection": "compliant", "dpia": "compliant"}
        )
        
        self.assertEqual(len(gaps), 2)
        self.assertTrue(all(isinstance(g, object) for g in gaps))
    
    def test_prioritize_gaps(self):
        """Test gap prioritization."""
        self.analyzer.identify_gaps(
            framework="GDPR",
            current_state={"lawful_basis": "none", "data_protection": "none"},
            required_state={"lawful_basis": "compliant", "data_protection": "compliant"}
        )
        
        prioritized = self.analyzer.prioritize_gaps()
        self.assertEqual(len(prioritized), 2)


class TestRemediationTracker(unittest.TestCase):
    """Tests for RemediationTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.advanced_compliance_checks import RemediationTracker
        self.tracker = RemediationTracker()
    
    def test_create_remediation_action(self):
        """Test creating remediation action."""
        action = self.tracker.create_remediation_action(
            gap_id="gap_001",
            action_title="Test Action",
            description="Test description"
        )
        
        self.assertIsNotNone(action.action_id)
        self.assertEqual(action.status, "pending")
        self.assertEqual(action.completion_percentage, 0.0)
    
    def test_update_action_status(self):
        """Test updating action status."""
        action = self.tracker.create_remediation_action(
            gap_id="gap_001",
            action_title="Test",
            description="desc"
        )
        
        result = self.tracker.update_action_status(
            action_id=action.action_id,
            status="in_progress",
            completion_percentage=50.0
        )
        
        self.assertTrue(result)
        self.assertEqual(action.status, "in_progress")
        self.assertEqual(action.completion_percentage, 50.0)
    
    def test_get_action_progress(self):
        """Test getting action progress."""
        self.tracker.create_remediation_action("gap_001", "Action 1", "desc")
        self.tracker.create_remediation_action("gap_002", "Action 2", "desc")
        
        progress = self.tracker.get_action_progress()
        
        self.assertEqual(progress["total"], 2)
        self.assertEqual(progress["pending"], 2)


class TestRegulatoryFeaturesAPI(unittest.TestCase):
    """Tests for RegulatoryFeaturesAPI."""
    
    def setUp(self):
        """Set up test fixtures."""
        from scripts.regulatory_features_api import RegulatoryFeaturesAPI
        self.api = RegulatoryFeaturesAPI()
    
    def test_track_regulatory_change(self):
        """Test tracking regulatory change through API."""
        result = self.api.track_regulatory_change(
            source="Test",
            regulation_id="TST-001",
            regulation_name="Test Reg",
            change_type="update",
            description="Test",
            impact_level="high",
            affected_systems=["sys1"]
        )
        
        self.assertIsNotNone(result["change_id"])
        self.assertEqual(result["regulation_name"], "Test Reg")
    
    def test_record_compliance_score(self):
        """Test recording compliance score through API."""
        result = self.api.record_compliance_score("GDPR", 85.0)
        
        self.assertEqual(result["compliance_score"], 85.0)
        self.assertEqual(result["metric_name"], "GDPR")
    
    def test_generate_alert_through_api(self):
        """Test alert generation through API."""
        result = self.api.generate_alert(
            alert_type="test",
            affected_regulation="TEST",
            message="msg",
            recommended_action="act",
            risk_level="high"
        )
        
        self.assertIsNotNone(result["alert_id"])
        self.assertEqual(result["status"], "open")
    
    def test_validate_system_through_api(self):
        """Test system validation through API."""
        result = self.api.validate_system_compliance(
            system_name="test_sys",
            framework="GDPR",
            controls={"lawful_basis": "compliant", "data_protection": "compliant"}
        )
        
        self.assertIn("compliance_percentage", result)
        self.assertGreater(result["compliance_percentage"], 0)


def run_all_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


def run_quick_validation():
    """Run quick validation of key features."""
    print("=" * 60)
    print("RUNNING QUICK VALIDATION OF NEW FEATURES")
    print("=" * 60)
    
    try:
        from scripts.regulatory_features_api import get_api
        api = get_api()
        
        print("\n1. Testing Regulatory Change Tracking...")
        change = api.track_regulatory_change(
            source="Validation Test",
            regulation_id="VAL-001",
            regulation_name="Validation Test Regulation",
            change_type="update",
            description="This is a validation test",
            impact_level="high",
            affected_systems=["test_system"]
        )
        print(f"   ✓ Change tracked: {change['change_id']}")
        
        print("\n2. Testing Compliance Score Recording...")
        trend = api.record_compliance_score("GDPR", 88.5)
        print(f"   ✓ Compliance score recorded: {trend['compliance_score']}%")
        
        print("\n3. Testing Alert Generation...")
        alert = api.generate_alert(
            alert_type="validation_test",
            affected_regulation="TEST_REG",
            message="This is a validation alert",
            recommended_action="No action needed for validation",
            risk_level="medium"
        )
        print(f"   ✓ Alert generated: {alert['alert_id']}")
        
        print("\n4. Testing Compliance Validation...")
        validation = api.validate_system_compliance(
            system_name="test_system",
            framework="GDPR",
            controls={
                "lawful_basis": "compliant",
                "data_protection": "compliant",
                "dpia": "non_compliant"
            }
        )
        print(f"   ✓ Validation complete: {validation['compliance_percentage']:.1f}% compliant")
        
        print("\n5. Testing Gap Identification...")
        gaps = api.identify_compliance_gaps(
            framework="GDPR",
            current_state={"data_protection": "partial"},
            required_state={"data_protection": "compliant"}
        )
        print(f"   ✓ Gaps identified: {len(gaps)} gap(s)")
        
        print("\n6. Testing System Status...")
        status = api.get_system_status()
        print(f"   ✓ Open alerts: {status['open_alerts']}")
        print(f"   ✓ Remediation progress: {status['remediation_progress']['completion_percentage']:.1f}%")
        
        print("\n" + "=" * 60)
        print("ALL VALIDATIONS PASSED ✓")
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run quick validation first
    success = run_quick_validation()
    
    if success:
        print("\n\nRunning comprehensive tests...")
        run_all_tests()
