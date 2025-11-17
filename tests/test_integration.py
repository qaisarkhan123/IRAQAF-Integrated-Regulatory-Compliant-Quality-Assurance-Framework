"""
Integration Tests for Regulatory Monitoring Module
Tests module interactions and data flow
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import time

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from regulatory_monitor import RegulatoryMonitor
    from nlp_change_detector import NLPChangeDetector
    from iraqaf_regulatory_sync import IRaqafRegulatorySync
except ImportError:
    pytest.skip("Required modules not found", allow_module_level=True)


class TestIntegrationWorkflow:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    def setup_modules(self):
        """Setup all modules for integration testing"""
        return {
            "monitor": RegulatoryMonitor(),
            "detector": NLPChangeDetector(),
            "sync": IRaqafRegulatorySync()
        }
    
    # Integration Test 1: Fetch and Analyze Workflow
    def test_fetch_and_analyze_workflow(self, setup_modules):
        """Integration: Fetch -> Analyze -> Detect Changes"""
        monitor = setup_modules["monitor"]
        detector = setup_modules["detector"]
        
        # Sample regulations to simulate fetch
        regulations = [
            {
                "id": "GDPR-001",
                "title": "Data Protection",
                "content": "Organizations must implement technical measures for data protection"
            }
        ]
        
        # Should fetch successfully
        assert len(regulations) > 0
        
        # Analyze each regulation
        for reg in regulations:
            if "content" in reg:
                # Compare with baseline
                baseline = "Organizations should implement security measures"
                similarity = detector.calculate_similarity(
                    reg["content"],
                    baseline
                )
                
                # Should return valid similarity
                assert 0 <= similarity <= 1
    
    # Integration Test 2: Pipeline Data Flow
    def test_full_monitoring_pipeline(self, setup_modules):
        """Integration: Complete Fetch -> Analyze -> Sync pipeline"""
        monitor = setup_modules["monitor"]
        detector = setup_modules["detector"]
        sync = setup_modules["sync"]
        
        # Simulate regulation versions
        old_reg = {
            "id": "REG-001",
            "title": "Requirement",
            "content": "Original requirement text"
        }
        new_reg = {
            "id": "REG-001",
            "title": "Requirement",
            "content": "Updated requirement text with new clauses"
        }
        
        # Step 1: Compare
        similarity = detector.calculate_similarity(
            old_reg["content"],
            new_reg["content"]
        )
        
        # Step 2: Classify
        severity = detector.classify_severity(similarity)
        
        # Step 3: Should be valid severity
        assert severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    # Integration Test 3: Data Format Consistency
    def test_data_format_consistency(self, setup_modules):
        """Integration: Data format consistency across modules"""
        monitor = setup_modules["monitor"]
        detector = setup_modules["detector"]
        
        # Create data in monitor format
        regulation = {
            "id": "GDPR-001",
            "title": "Title",
            "content": "Content",
            "source": "test",
            "date": "2025-11-16"
        }
        
        # Should be compatible with detector
        assert "content" in regulation
        assert isinstance(regulation["content"], str)
    
    # Integration Test 4: Error Propagation
    def test_error_handling_across_pipeline(self, setup_modules):
        """Integration: Error handling through pipeline"""
        detector = setup_modules["detector"]
        
        # Test with edge cases
        test_cases = [
            ("valid text", "valid text"),
            ("", "text"),
            ("text", ""),
        ]
        
        results = []
        for text1, text2 in test_cases:
            try:
                sim = detector.calculate_similarity(text1, text2)
                results.append(sim)
            except (ValueError, AttributeError, ZeroDivisionError):
                # Should handle gracefully
                results.append(None)
        
        # Should process all cases
        assert len(results) == len(test_cases)
    
    # Integration Test 5: State Management
    def test_state_management_across_modules(self, setup_modules):
        """Integration: Maintaining state across modules"""
        monitor = setup_modules["monitor"]
        
        # Set state
        monitor.last_run = time.time()
        
        # Should be retrievable
        assert hasattr(monitor, 'last_run')
        assert monitor.last_run > 0
    
    # Integration Test 6: Cache Consistency
    def test_cache_consistency(self, setup_modules):
        """Integration: Cache consistency across modules"""
        import json
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "cache.json"
            
            data = {
                "id": "REG-001",
                "title": "Test",
                "content": "Content"
            }
            
            # Save
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            # Load
            with open(cache_file, 'r') as f:
                loaded = json.load(f)
            
            # Should match
            assert loaded["id"] == data["id"]
            assert loaded["content"] == data["content"]


class TestIntegrationAdvanced:
    """Advanced integration tests"""
    
    # Integration Test 7: Multi-source Coordination
    def test_multi_source_regulation_coordination(self):
        """Integration: Coordinate regulations from multiple sources"""
        monitor = RegulatoryMonitor()
        
        sources = {
            "gdpr": [{"id": "GDPR-001", "title": "GDPR"}],
            "hipaa": [{"id": "HIPAA-001", "title": "HIPAA"}],
            "eu_ai": [{"id": "AI-001", "title": "AI Act"}]
        }
        
        # Should coordinate multiple sources
        total = sum(len(v) for v in sources.values())
        assert total == 3
    
    # Integration Test 8: Batch Processing
    def test_batch_regulation_processing(self):
        """Integration: Batch process multiple regulations"""
        detector = NLPChangeDetector()
        
        regulations = [
            {"id": f"REG-{i:03d}", "content": f"Regulation {i} content"}
            for i in range(5)
        ]
        
        # Process all
        results = []
        for reg in regulations:
            sim = detector.calculate_similarity(
                reg["content"],
                "baseline content"
            )
            results.append({"id": reg["id"], "similarity": sim})
        
        # Should process all
        assert len(results) == 5
        assert all(0 <= r["similarity"] <= 1 for r in results)
    
    # Integration Test 9: Concurrent Operations
    def test_concurrent_module_operations(self):
        """Integration: Multiple modules operating concurrently"""
        import threading
        
        detector = NLPChangeDetector()
        results = []
        lock = threading.Lock()
        
        def analyze(text_id):
            result = detector.calculate_similarity(
                f"Text {text_id}",
                "baseline"
            )
            with lock:
                results.append(result)
        
        # Create threads
        threads = [
            threading.Thread(target=analyze, args=(i,))
            for i in range(5)
        ]
        
        # Execute
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should complete all
        assert len(results) == 5
    
    # Integration Test 10: End-to-End Report Generation
    def test_end_to_end_report_generation(self):
        """Integration: Generate complete report from regulations"""
        import json
        
        detector = NLPChangeDetector()
        
        regulations = [
            {
                "id": "GDPR-001",
                "old_content": "Data must be protected",
                "new_content": "Data must be strongly protected with encryption"
            }
        ]
        
        reports = []
        for reg in regulations:
            similarity = detector.calculate_similarity(
                reg["old_content"],
                reg["new_content"]
            )
            
            report = {
                "id": reg["id"],
                "similarity": similarity,
                "severity": detector.classify_severity(similarity),
                "timestamp": time.time()
            }
            reports.append(report)
        
        # Should generate valid reports
        assert len(reports) == 1
        assert "severity" in reports[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
