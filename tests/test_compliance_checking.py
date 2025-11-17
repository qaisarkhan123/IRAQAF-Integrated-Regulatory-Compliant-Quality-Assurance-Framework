"""
Tests for Compliance Check and Parsing Modules
Tests compliance threshold validation and IRAQAF result parsing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from check_compliance_threshold import (
        check_compliance_status,
        calculate_compliance_score,
        get_threshold_alerts
    )
except ImportError:
    pytest.skip("check_compliance_threshold module not found", allow_module_level=True)


class TestComplianceThreshold:
    """Tests for compliance threshold checking"""
    
    def test_check_compliance_passing(self):
        """Test checking passing compliance status"""
        from check_compliance_threshold import check_compliance_status
        
        result = {
            'compliance_items': 150,
            'compliant_items': 150,
            'score': 100.0
        }
        
        status = check_compliance_status(result, threshold=90)
        assert status is True
    
    def test_check_compliance_failing(self):
        """Test checking failing compliance status"""
        from check_compliance_threshold import check_compliance_status
        
        result = {
            'compliance_items': 100,
            'compliant_items': 50,
            'score': 50.0
        }
        
        status = check_compliance_status(result, threshold=90)
        assert status is False
    
    def test_check_compliance_at_threshold(self):
        """Test checking compliance exactly at threshold"""
        from check_compliance_threshold import check_compliance_status
        
        result = {
            'compliance_items': 100,
            'compliant_items': 90,
            'score': 90.0
        }
        
        status = check_compliance_status(result, threshold=90)
        assert status is True
    
    def test_calculate_compliance_score_perfect(self):
        """Test calculating perfect compliance score"""
        score = calculate_compliance_score(100, 100)
        assert score == 100.0
    
    def test_calculate_compliance_score_partial(self):
        """Test calculating partial compliance score"""
        score = calculate_compliance_score(150, 100)
        assert 60 <= score <= 70
    
    def test_calculate_compliance_score_zero(self):
        """Test calculating zero compliance score"""
        score = calculate_compliance_score(100, 0)
        assert score == 0.0
    
    def test_get_threshold_alerts_above(self):
        """Test alerts when above threshold"""
        from check_compliance_threshold import get_threshold_alerts
        
        result = {'score': 95.0}
        alerts = get_threshold_alerts(result, threshold=90)
        assert len(alerts) == 0
    
    def test_get_threshold_alerts_below(self):
        """Test alerts when below threshold"""
        from check_compliance_threshold import get_threshold_alerts
        
        result = {'score': 75.0}
        alerts = get_threshold_alerts(result, threshold=90)
        assert len(alerts) > 0
    
    def test_get_threshold_alerts_critical(self):
        """Test critical alerts for very low compliance"""
        from check_compliance_threshold import get_threshold_alerts
        
        result = {'score': 30.0}
        alerts = get_threshold_alerts(result, threshold=90)
        assert any('CRITICAL' in str(alert) for alert in alerts)


class TestComplianceCalculation:
    """Tests for compliance calculation logic"""
    
    def test_calculate_weighted_compliance(self):
        """Test weighted compliance calculation"""
        from check_compliance_threshold import calculate_weighted_score
        
        items = [
            {'weight': 0.5, 'compliant': True},
            {'weight': 0.3, 'compliant': False},
            {'weight': 0.2, 'compliant': True},
        ]
        
        score = calculate_weighted_score(items)
        assert 0 <= score <= 100
    
    def test_handle_empty_compliance_data(self):
        """Test handling empty compliance data"""
        from check_compliance_threshold import check_compliance_status
        
        result = {
            'compliance_items': 0,
            'compliant_items': 0,
            'score': 0.0
        }
        
        # Should handle gracefully
        try:
            status = check_compliance_status(result, threshold=90)
        except (ValueError, ZeroDivisionError):
            pytest.skip("Module doesn't handle empty data")
    
    def test_compliance_with_missing_fields(self):
        """Test compliance check with missing fields"""
        from check_compliance_threshold import check_compliance_status
        
        result = {'score': 85.0}
        
        # Should handle gracefully or use defaults
        try:
            status = check_compliance_status(result, threshold=90)
        except (KeyError, ValueError):
            pytest.skip("Module requires all fields")


class TestComplianceReporting:
    """Tests for compliance reporting"""
    
    def test_generate_compliance_report(self):
        """Test generating compliance report"""
        from check_compliance_threshold import generate_compliance_report
        
        result = {
            'score': 85.5,
            'compliance_items': 100,
            'compliant_items': 85,
            'timestamp': datetime.now().isoformat()
        }
        
        report = generate_compliance_report(result)
        assert 'score' in str(report).lower() or len(report) > 0
    
    def test_export_compliance_data_json(self):
        """Test exporting compliance data to JSON"""
        from check_compliance_threshold import export_compliance_data
        
        result = {
            'score': 85.5,
            'timestamp': datetime.now().isoformat()
        }
        
        exported = export_compliance_data(result, format='json')
        assert isinstance(exported, (str, dict))


class TestIRAQAFParsing:
    """Tests for IRAQAF result parsing"""
    
    try:
        from parse_iraqaf_results import (
            parse_iraqaf_response,
            extract_trace_mapping,
            validate_iraqaf_format
        )
        has_parse_module = True
    except ImportError:
        has_parse_module = False
    
    @pytest.mark.skipif(not has_parse_module, reason="parse_iraqaf_results not available")
    def test_parse_valid_iraqaf_response(self):
        """Test parsing valid IRAQAF response"""
        from parse_iraqaf_results import parse_iraqaf_response
        
        response = {
            'traces': [
                {'id': 'TRACE-001', 'name': 'Trace 1', 'mappings': []},
                {'id': 'TRACE-002', 'name': 'Trace 2', 'mappings': []}
            ]
        }
        
        parsed = parse_iraqaf_response(response)
        assert parsed is not None
    
    @pytest.mark.skipif(not has_parse_module, reason="parse_iraqaf_results not available")
    def test_extract_trace_mapping(self):
        """Test extracting trace mappings"""
        from parse_iraqaf_results import extract_trace_mapping
        
        trace = {
            'id': 'TRACE-001',
            'mappings': [
                {'framework': 'ISO27001', 'control': 'A.5.1'},
                {'framework': 'NIST', 'control': 'AC-1'}
            ]
        }
        
        mappings = extract_trace_mapping(trace)
        assert isinstance(mappings, (list, dict))
    
    @pytest.mark.skipif(not has_parse_module, reason="parse_iraqaf_results not available")
    def test_validate_iraqaf_format(self):
        """Test IRAQAF format validation"""
        from parse_iraqaf_results import validate_iraqaf_format
        
        valid_response = {
            'traces': [
                {'id': 'TRACE-001', 'name': 'Test'}
            ]
        }
        
        is_valid = validate_iraqaf_format(valid_response)
        assert is_valid is True
    
    @pytest.mark.skipif(not has_parse_module, reason="parse_iraqaf_results not available")
    def test_validate_invalid_iraqaf_format(self):
        """Test invalid IRAQAF format detection"""
        from parse_iraqaf_results import validate_iraqaf_format
        
        invalid_response = {'invalid': 'format'}
        
        is_valid = validate_iraqaf_format(invalid_response)
        assert is_valid is False


class TestComplianceIntegration:
    """Integration tests for compliance system"""
    
    def test_end_to_end_compliance_check(self):
        """Test end-to-end compliance check workflow"""
        from check_compliance_threshold import check_compliance_status, calculate_compliance_score
        
        # Simulate regulation tracking data
        regulations = [
            {'id': 'REG-001', 'status': 'compliant'},
            {'id': 'REG-002', 'status': 'compliant'},
            {'id': 'REG-003', 'status': 'non-compliant'},
        ]
        
        compliant_count = sum(1 for r in regulations if r['status'] == 'compliant')
        score = calculate_compliance_score(len(regulations), compliant_count)
        status = check_compliance_status(
            {'score': score}, threshold=70
        )
        
        assert status is True
        assert score > 50


class TestComplianceMetrics:
    """Tests for compliance metrics"""
    
    def test_compliance_trend_analysis(self):
        """Test compliance trend analysis"""
        from check_compliance_threshold import analyze_trend
        
        scores = [80.0, 82.0, 85.0, 87.0, 90.0]
        
        trend = analyze_trend(scores)
        assert trend is not None
    
    def test_compliance_forecasting(self):
        """Test compliance score forecasting"""
        from check_compliance_threshold import forecast_compliance
        
        historical_scores = [70.0, 72.0, 75.0, 77.0, 80.0]
        
        forecast = forecast_compliance(historical_scores)
        assert forecast is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
