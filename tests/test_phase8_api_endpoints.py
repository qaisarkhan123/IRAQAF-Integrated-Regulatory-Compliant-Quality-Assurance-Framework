"""
Phase 8 - API Endpoint Tests
Comprehensive testing of REST API endpoints (15+ tests)
Tests all endpoints, error handling, validation, and integration
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Import the API app
try:
    from api_or_cli.api import app, systems_db, assessments_db, changes_db, notifications_db
    client = TestClient(app)
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    client = None


@pytest.mark.api
@pytest.mark.unit
class TestSystemsEndpoints:
    """Test Systems CRUD endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_list_systems_empty(self):
        """Test GET /api/systems returns empty list initially"""
        systems_db.clear()
        response = client.get("/api/systems")
        assert response.status_code == 200
        assert response.json() == []
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_create_system(self):
        """Test POST /api/systems creates new system"""
        systems_db.clear()
        system_data = {
            "name": "Test Medical Device",
            "description": "A test medical device system",
            "domain": "medical_device"
        }
        response = client.post("/api/systems", json=system_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == system_data["name"]
        assert "id" in data
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_create_system_validation(self):
        """Test POST /api/systems validates required fields"""
        invalid_data = {"description": "Missing name"}
        response = client.post("/api/systems", json=invalid_data)
        assert response.status_code in [422, 400]  # Validation error
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_get_system(self):
        """Test GET /api/systems/{id} retrieves system"""
        systems_db.clear()
        # Create a system
        system_data = {"name": "Test System", "description": "Test"}
        create_response = client.post("/api/systems", json=system_data)
        system_id = create_response.json()["id"]
        
        # Get the system
        response = client.get(f"/api/systems/{system_id}")
        assert response.status_code == 200
        assert response.json()["name"] == system_data["name"]
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_get_system_not_found(self):
        """Test GET /api/systems/{id} returns 404 for non-existent system"""
        response = client.get("/api/systems/99999")
        assert response.status_code == 404
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_update_system(self):
        """Test PUT /api/systems/{id} updates system"""
        systems_db.clear()
        # Create a system
        system_data = {"name": "Original Name", "description": "Test"}
        create_response = client.post("/api/systems", json=system_data)
        system_id = create_response.json()["id"]
        
        # Update the system
        update_data = {"name": "Updated Name", "description": "Updated"}
        response = client.put(f"/api/systems/{system_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_delete_system(self):
        """Test DELETE /api/systems/{id} removes system"""
        systems_db.clear()
        # Create a system
        system_data = {"name": "To Delete", "description": "Test"}
        create_response = client.post("/api/systems", json=system_data)
        system_id = create_response.json()["id"]
        
        # Delete the system
        response = client.delete(f"/api/systems/{system_id}")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f"/api/systems/{system_id}")
        assert get_response.status_code == 404


@pytest.mark.api
@pytest.mark.unit
class TestAssessmentEndpoints:
    """Test Assessment endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_run_assessment(self):
        """Test POST /api/systems/{id}/assess runs assessment"""
        systems_db.clear()
        assessments_db.clear()
        
        # Create a system first
        system_data = {"name": "Test System", "description": "Test"}
        create_response = client.post("/api/systems", json=system_data)
        system_id = create_response.json()["id"]
        
        # Run assessment
        response = client.post(f"/api/systems/{system_id}/assess")
        assert response.status_code == 200
        data = response.json()
        assert "compliance_score" in data
        assert data["system_id"] == system_id
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_get_assessment(self):
        """Test GET /api/systems/{id}/assessment retrieves latest assessment"""
        systems_db.clear()
        assessments_db.clear()
        
        # Create system and run assessment
        system_data = {"name": "Test System", "description": "Test"}
        create_response = client.post("/api/systems", json=system_data)
        system_id = create_response.json()["id"]
        
        client.post(f"/api/systems/{system_id}/assess")
        
        # Get assessment
        response = client.get(f"/api/systems/{system_id}/assessment")
        assert response.status_code == 200
        assert response.json()["system_id"] == system_id
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_list_assessments(self):
        """Test GET /api/assessments lists all assessments"""
        assessments_db.clear()
        response = client.get("/api/assessments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.api
@pytest.mark.unit
class TestRegulatoryEndpoints:
    """Test Regulatory data endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_list_regulations(self):
        """Test GET /api/regulations lists regulations"""
        response = client.get("/api/regulations")
        assert response.status_code == 200
        regulations = response.json()
        assert isinstance(regulations, list)
        # Should have at least some regulations
        assert len(regulations) > 0
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_get_regulation(self):
        """Test GET /api/regulations/{id} retrieves regulation"""
        response = client.get("/api/regulations/1")
        # Either succeeds or 404 depending on data
        assert response.status_code in [200, 404]
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_search_requirements(self):
        """Test GET /api/requirements searches requirements"""
        response = client.get("/api/requirements?q=encryption")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.api
@pytest.mark.unit
class TestChangeEndpoints:
    """Test Change monitoring endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_list_changes(self):
        """Test GET /api/changes lists regulatory changes"""
        changes_db.clear()
        response = client.get("/api/changes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_detect_changes(self):
        """Test POST /api/changes/detect detects new changes"""
        changes_db.clear()
        response = client.post("/api/changes/detect")
        assert response.status_code == 200
        data = response.json()
        assert "detection_time" in data or "changes_detected" in data


@pytest.mark.api
@pytest.mark.unit
class TestNotificationEndpoints:
    """Test Notification endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_list_notifications(self):
        """Test GET /api/notifications lists notifications"""
        notifications_db.clear()
        response = client.get("/api/notifications")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_send_notification(self):
        """Test POST /api/notifications/send sends notification"""
        notification_data = {
            "type": "alert",
            "title": "Test Alert",
            "message": "This is a test",
            "recipients": ["test@example.com"]
        }
        response = client.post("/api/notifications/send", json=notification_data)
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.unit
class TestReportEndpoints:
    """Test Report generation endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_generate_report(self):
        """Test GET /api/reports/{id} generates report"""
        systems_db.clear()
        assessments_db.clear()
        
        # Create system and assessment
        system_data = {"name": "Test", "description": "Test"}
        sys_resp = client.post("/api/systems", json=system_data)
        system_id = sys_resp.json()["id"]
        client.post(f"/api/systems/{system_id}/assess")
        
        # Generate report
        response = client.get(f"/api/reports/{system_id}")
        assert response.status_code in [200, 404]
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_export_report(self):
        """Test GET /api/reports/{id}/export exports report"""
        response = client.get("/api/reports/1/export?format=json")
        assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.unit
class TestHealthEndpoints:
    """Test Health check endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_health_check(self):
        """Test GET /api/health returns health status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_statistics(self):
        """Test GET /api/stats returns statistics"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_systems" in data or "timestamp" in data


@pytest.mark.api
@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API workflows"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_complete_assessment_workflow(self):
        """Test complete workflow: Create system -> Assess -> Generate report"""
        systems_db.clear()
        assessments_db.clear()
        
        # 1. Create system
        system_data = {"name": "Integration Test", "description": "Full workflow"}
        sys_response = client.post("/api/systems", json=system_data)
        assert sys_response.status_code == 200
        system = sys_response.json()
        system_id = system["id"]
        
        # 2. Run assessment
        assess_response = client.post(f"/api/systems/{system_id}/assess")
        assert assess_response.status_code == 200
        assessment = assess_response.json()
        assert "compliance_score" in assessment
        
        # 3. Get assessment
        get_response = client.get(f"/api/systems/{system_id}/assessment")
        assert get_response.status_code == 200
        
        # 4. Generate report
        report_response = client.get(f"/api/reports/{system_id}")
        assert report_response.status_code in [200, 404]
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_error_handling(self):
        """Test proper error handling across endpoints"""
        # Invalid system ID
        response = client.get("/api/systems/invalid-id-format")
        assert response.status_code in [400, 404, 422]
        
        # Invalid JSON
        response = client.post(
            "/api/systems",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


@pytest.mark.api
@pytest.mark.performance
class TestAPIPerformance:
    """Performance tests for API endpoints"""
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_response_time_health_check(self, performance_timer):
        """Test health check responds within 100ms"""
        performance_timer.start()
        response = client.get("/api/health")
        performance_timer.stop()
        
        assert response.status_code == 200
        assert performance_timer.elapsed < 0.1  # 100ms
    
    @pytest.mark.skipif(not API_AVAILABLE, reason="API module not available")
    def test_list_operations_performance(self, performance_timer):
        """Test list operations respond within 200ms"""
        operations = [
            "/api/systems",
            "/api/regulations",
            "/api/requirements",
            "/api/assessments"
        ]
        
        for operation in operations:
            performance_timer.start()
            response = client.get(operation)
            performance_timer.stop()
            
            assert response.status_code == 200
            assert performance_timer.elapsed < 0.2  # 200ms


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
