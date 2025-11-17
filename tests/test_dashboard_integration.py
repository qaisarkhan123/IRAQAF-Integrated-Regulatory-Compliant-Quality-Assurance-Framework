"""
Tests for Dashboard Regulatory Integration Module
Tests Streamlit widget integration and real-time alert functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from dashboard_regulatory_integration import (
        RegulatoryDashboardIntegration,
        format_regulation_alert,
        calculate_severity_badge,
        create_impact_summary
    )
except ImportError:
    pytest.skip("dashboard_regulatory_integration module not found", allow_module_level=True)


class TestDashboardIntegration:
    """Tests for dashboard integration functionality"""
    
    @pytest.fixture
    def integration(self):
        """Fixture: Initialize dashboard integration"""
        return RegulatoryDashboardIntegration()
    
    def test_format_regulation_alert_critical(self, integration):
        """Test formatting of CRITICAL severity alert"""
        regulation = {
            'id': 'REG-001',
            'title': 'Data Protection Update',
            'date': datetime.now().isoformat(),
            'severity': 'CRITICAL',
            'content': 'New encryption requirement'
        }
        
        alert = format_regulation_alert(regulation)
        assert 'CRITICAL' in alert
        assert 'Data Protection Update' in alert
    
    def test_format_regulation_alert_high(self, integration):
        """Test formatting of HIGH severity alert"""
        regulation = {
            'id': 'REG-002',
            'title': 'Compliance Update',
            'date': datetime.now().isoformat(),
            'severity': 'HIGH',
            'content': 'New compliance requirement'
        }
        
        alert = format_regulation_alert(regulation)
        assert 'HIGH' in alert
        assert 'Compliance Update' in alert
    
    def test_calculate_severity_badge_critical(self):
        """Test severity badge for CRITICAL"""
        badge = calculate_severity_badge('CRITICAL')
        assert '🔴' in badge or 'CRITICAL' in badge
    
    def test_calculate_severity_badge_high(self):
        """Test severity badge for HIGH"""
        badge = calculate_severity_badge('HIGH')
        assert '🟠' in badge or 'HIGH' in badge
    
    def test_calculate_severity_badge_medium(self):
        """Test severity badge for MEDIUM"""
        badge = calculate_severity_badge('MEDIUM')
        assert '🟡' in badge or 'MEDIUM' in badge
    
    def test_calculate_severity_badge_low(self):
        """Test severity badge for LOW"""
        badge = calculate_severity_badge('LOW')
        assert '🟢' in badge or 'LOW' in badge
    
    def test_create_impact_summary_single_regulation(self):
        """Test creating impact summary for single regulation"""
        regulation = {
            'id': 'REG-001',
            'title': 'Update',
            'severity': 'HIGH',
            'affected_areas': ['Data Protection', 'Privacy']
        }
        
        summary = create_impact_summary([regulation])
        assert 'REG-001' in summary or 'Update' in summary
    
    def test_create_impact_summary_multiple_regulations(self):
        """Test creating impact summary for multiple regulations"""
        regulations = [
            {
                'id': 'REG-001',
                'title': 'Update 1',
                'severity': 'HIGH',
                'affected_areas': ['Area1']
            },
            {
                'id': 'REG-002',
                'title': 'Update 2',
                'severity': 'MEDIUM',
                'affected_areas': ['Area2']
            }
        ]
        
        summary = create_impact_summary(regulations)
        assert len(summary) > 0
    
    def test_dashboard_widget_rendering(self, integration):
        """Test that dashboard widgets render without errors"""
        regulation = {
            'id': 'REG-001',
            'title': 'Test Regulation',
            'date': datetime.now().isoformat(),
            'severity': 'HIGH',
            'content': 'Test content'
        }
        
        # Should not raise exception
        try:
            alert = format_regulation_alert(regulation)
            assert alert is not None
        except Exception as e:
            pytest.fail(f"Widget rendering failed: {e}")
    
    def test_alert_timestamp_formatting(self):
        """Test alert timestamp is formatted correctly"""
        now = datetime.now()
        regulation = {
            'id': 'REG-001',
            'title': 'Test',
            'date': now.isoformat(),
            'severity': 'HIGH',
            'content': 'Content'
        }
        
        alert = format_regulation_alert(regulation)
        assert isinstance(alert, str)
        assert len(alert) > 0


class TestDashboardMetrics:
    """Tests for dashboard metrics calculation"""
    
    def test_calculate_impact_score_high(self):
        """Test impact score calculation for high impact"""
        from dashboard_regulatory_integration import calculate_impact_score
        
        regulation = {
            'severity': 'CRITICAL',
            'affected_areas': ['Data', 'Privacy', 'Compliance', 'Reporting'],
            'deadline_days': 5
        }
        
        score = calculate_impact_score(regulation)
        assert score > 75  # High impact
    
    def test_calculate_impact_score_medium(self):
        """Test impact score calculation for medium impact"""
        from dashboard_regulatory_integration import calculate_impact_score
        
        regulation = {
            'severity': 'MEDIUM',
            'affected_areas': ['Data'],
            'deadline_days': 30
        }
        
        score = calculate_impact_score(regulation)
        assert 40 <= score <= 75  # Medium impact
    
    def test_calculate_impact_score_low(self):
        """Test impact score calculation for low impact"""
        from dashboard_regulatory_integration import calculate_impact_score
        
        regulation = {
            'severity': 'LOW',
            'affected_areas': ['Reporting'],
            'deadline_days': 90
        }
        
        score = calculate_impact_score(regulation)
        assert score < 40  # Low impact


class TestDashboardStateManagement:
    """Tests for dashboard state management"""
    
    def test_get_recent_regulations(self):
        """Test retrieving recent regulations"""
        from dashboard_regulatory_integration import get_recent_regulations
        
        regulations = [
            {
                'id': f'REG-{i:03d}',
                'title': f'Regulation {i}',
                'date': (datetime.now() - timedelta(days=i)).isoformat(),
                'severity': 'HIGH'
            }
            for i in range(10)
        ]
        
        recent = get_recent_regulations(regulations, days=5)
        assert len(recent) > 0
    
    def test_group_regulations_by_severity(self):
        """Test grouping regulations by severity"""
        from dashboard_regulatory_integration import group_by_severity
        
        regulations = [
            {'id': 'REG-001', 'severity': 'CRITICAL'},
            {'id': 'REG-002', 'severity': 'HIGH'},
            {'id': 'REG-003', 'severity': 'HIGH'},
            {'id': 'REG-004', 'severity': 'MEDIUM'},
        ]
        
        grouped = group_by_severity(regulations)
        assert grouped['CRITICAL'] == 1
        assert grouped['HIGH'] == 2
        assert grouped['MEDIUM'] == 1


class TestDashboardAlerts:
    """Tests for dashboard alert system"""
    
    def test_should_show_alert_critical(self):
        """Test that CRITICAL regulations trigger alerts"""
        from dashboard_regulatory_integration import should_trigger_alert
        
        regulation = {'severity': 'CRITICAL', 'deadline_days': 3}
        assert should_trigger_alert(regulation) is True
    
    def test_should_show_alert_high_imminent(self):
        """Test that HIGH severity with imminent deadline triggers alert"""
        from dashboard_regulatory_integration import should_trigger_alert
        
        regulation = {'severity': 'HIGH', 'deadline_days': 2}
        assert should_trigger_alert(regulation) is True
    
    def test_should_not_show_alert_low_distant(self):
        """Test that LOW severity with distant deadline doesn't trigger"""
        from dashboard_regulatory_integration import should_trigger_alert
        
        regulation = {'severity': 'LOW', 'deadline_days': 60}
        assert should_trigger_alert(regulation) is False


class TestDashboardDataVisualization:
    """Tests for data visualization components"""
    
    def test_prepare_timeline_data(self):
        """Test preparing data for timeline visualization"""
        from dashboard_regulatory_integration import prepare_timeline_data
        
        regulations = [
            {
                'id': 'REG-001',
                'date': (datetime.now() - timedelta(days=i)).isoformat(),
                'severity': 'HIGH'
            }
            for i in range(5)
        ]
        
        timeline = prepare_timeline_data(regulations)
        assert len(timeline) > 0
    
    def test_prepare_severity_distribution(self):
        """Test preparing severity distribution data"""
        from dashboard_regulatory_integration import prepare_severity_distribution
        
        regulations = [
            {'severity': 'CRITICAL'},
            {'severity': 'CRITICAL'},
            {'severity': 'HIGH'},
            {'severity': 'MEDIUM'},
            {'severity': 'LOW'},
        ]
        
        distribution = prepare_severity_distribution(regulations)
        assert 'CRITICAL' in distribution
        assert distribution['CRITICAL'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
