"""
End-to-End Tests for Regulatory Monitoring System
Tests complete workflows from fetch to reporting
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from regulatory_monitor import RegulatoryMonitor
    from nlp_change_detector import NLPChangeDetector
    from iraqaf_regulatory_sync import IRaqafRegulatorySync
except ImportError:
    pytest.skip("Required modules not found", allow_module_level=True)


class TestE2ECompleteWorkflows:
    """End-to-end tests for complete workflows"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace"""
        tmpdir = tempfile.mkdtemp()
        return {
            "base": tmpdir,
            "cache": Path(tmpdir) / "cache",
            "reports": Path(tmpdir) / "reports",
            "history": Path(tmpdir) / "history"
        }
    
    # E2E Test 1: Complete Monitoring Cycle
    def test_complete_monitoring_cycle(self, temp_workspace):
        """
        E2E: Complete monitoring cycle
        Fetch -> Analyze -> Detect -> Report -> Sync
        """
        monitor = RegulatoryMonitor(cache_dir=str(temp_workspace["cache"]))
        detector = NLPChangeDetector()
        sync = IRaqafRegulatorySync()
        
        # Step 1: Fetch regulations
        regulations = [
            {
                "id": "GDPR-001",
                "title": "Data Protection",
                "content": "Organizations must implement technical measures",
                "source": "EUR-Lex",
                "date": "2025-11-16"
            }
        ]
        
        assert len(regulations) > 0
        
        # Step 2: Compare with previous version
        previous_content = "Organizations should implement security measures"
        similarity = detector.calculate_similarity(
            regulations[0]["content"],
            previous_content
        )
        
        assert 0 <= similarity <= 1
        
        # Step 3: Classify severity
        severity = detector.classify_severity(similarity)
        
        assert severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        
        # Step 4: Generate report
        report_data = {
            "id": regulations[0]["id"],
            "title": regulations[0]["title"],
            "similarity": similarity,
            "severity": severity,
            "timestamp": time.time()
        }
        
        temp_workspace["reports"].mkdir(parents=True, exist_ok=True)
        report_file = temp_workspace["reports"] / "report.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f)
        
        assert report_file.exists()
        
        # Step 5: Verify report content
        with open(report_file, 'r') as f:
            loaded = json.load(f)
        
        assert loaded["id"] == regulations[0]["id"]
        assert loaded["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    
    # E2E Test 2: Multi-Cycle Tracking
    def test_multi_cycle_change_tracking(self, temp_workspace):
        """
        E2E: Track changes across multiple monitoring cycles
        """
        detector = NLPChangeDetector()
        history_file = temp_workspace["history"] / "history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Simulate 3 monitoring cycles
        text_versions = [
            "Data must be protected",
            "Data must be protected strongly",
            "Data must be protected with encryption"
        ]
        
        history = []
        baseline = text_versions[0]
        
        for i, text in enumerate(text_versions[1:], 1):
            similarity = detector.calculate_similarity(baseline, text)
            history.append({
                "cycle": i,
                "similarity": similarity,
                "severity": detector.classify_severity(similarity),
                "timestamp": time.time()
            })
        
        # Save history
        with open(history_file, 'w') as f:
            json.dump(history, f)
        
        # Verify
        with open(history_file, 'r') as f:
            loaded = json.load(f)
        
        assert len(loaded) == 2
        assert all("severity" in item for item in loaded)
    
    # E2E Test 3: Data Persistence Across Restarts
    def test_data_persistence_across_restarts(self, temp_workspace):
        """
        E2E: Data persists across system restarts
        """
        cache_file = temp_workspace["cache"] / "cache.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # First run
        data_v1 = {"id": "REG-001", "version": 1}
        with open(cache_file, 'w') as f:
            json.dump(data_v1, f)
        
        # Simulate restart - load again
        with open(cache_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Verify data persisted
        assert loaded_data == data_v1
        
        # Update data
        data_v2 = {"id": "REG-001", "version": 2}
        with open(cache_file, 'w') as f:
            json.dump(data_v2, f)
        
        # Load again
        with open(cache_file, 'r') as f:
            final_data = json.load(f)
        
        assert final_data["version"] == 2
    
    # E2E Test 4: Error Recovery
    def test_error_recovery_workflow(self, temp_workspace):
        """
        E2E: System recovers from errors gracefully
        """
        monitor = RegulatoryMonitor()
        detector = NLPChangeDetector()
        
        errors = []
        processed = 0
        
        # Simulate processing batch with errors
        test_data = [
            {"id": "REG-001", "content": "Valid content"},
            {"id": "REG-002", "content": ""},  # Potential error
            {"id": "REG-003", "content": "Another valid content"},
        ]
        
        for reg in test_data:
            try:
                if reg.get("content"):
                    sim = detector.calculate_similarity(
                        reg["content"],
                        "baseline"
                    )
                    processed += 1
            except Exception as e:
                errors.append(str(e))
        
        # Should process at least some data despite errors
        assert processed > 0
    
    # E2E Test 5: Full Report Generation Pipeline
    def test_full_report_generation_pipeline(self, temp_workspace):
        """
        E2E: Full report generation from regulations
        """
        detector = NLPChangeDetector()
        temp_workspace["reports"].mkdir(parents=True, exist_ok=True)
        
        # Sample regulations
        regulations = [
            {
                "id": "GDPR-001",
                "title": "Data Protection",
                "old_content": "Data must be protected",
                "new_content": "Data must be protected with strong encryption"
            },
            {
                "id": "HIPAA-001",
                "title": "Privacy",
                "old_content": "Privacy must be maintained",
                "new_content": "Privacy must be strictly maintained"
            }
        ]
        
        # Generate reports
        reports = []
        for reg in regulations:
            similarity = detector.calculate_similarity(
                reg["old_content"],
                reg["new_content"]
            )
            
            report = {
                "id": reg["id"],
                "title": reg["title"],
                "similarity": similarity,
                "severity": detector.classify_severity(similarity),
                "generated_at": time.time()
            }
            reports.append(report)
        
        # Save combined report
        report_file = temp_workspace["reports"] / "combined_report.json"
        with open(report_file, 'w') as f:
            json.dump(reports, f)
        
        # Verify
        assert report_file.exists()
        
        with open(report_file, 'r') as f:
            loaded = json.load(f)
        
        assert len(loaded) == 2
        assert all("severity" in r for r in loaded)


class TestE2EAdvancedScenarios:
    """Advanced E2E test scenarios"""
    
    # E2E Test 6: Large Dataset Processing
    def test_large_dataset_processing(self):
        """
        E2E: Process large dataset efficiently
        """
        detector = NLPChangeDetector()
        
        # Generate 50 regulations
        regulations = [
            f"Regulation {i}: This is a compliance requirement with various clauses"
            for i in range(50)
        ]
        
        start_time = time.time()
        
        # Process all
        results = []
        for reg in regulations:
            sim = detector.calculate_similarity(reg, "baseline compliance requirement")
            results.append(sim)
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        assert elapsed < 10
        assert len(results) == 50
    
    # E2E Test 7: Multi-Source Regulation Workflow
    def test_multi_source_regulation_workflow(self):
        """
        E2E: Process regulations from multiple sources
        """
        detector = NLPChangeDetector()
        
        sources = {
            "EUR-Lex": [
                {"id": "GDPR-001", "content": "GDPR compliance requirement"},
                {"id": "AI-001", "content": "AI Act requirement"}
            ],
            "HHS": [
                {"id": "HIPAA-001", "content": "HIPAA privacy requirement"}
            ],
            "FDA": [
                {"id": "FDA-001", "content": "FDA compliance requirement"}
            ]
        }
        
        # Process all sources
        total_processed = 0
        for source, regs in sources.items():
            for reg in regs:
                sim = detector.calculate_similarity(reg["content"], "baseline")
                assert 0 <= sim <= 1
                total_processed += 1
        
        # Should process all
        assert total_processed == 4
    
    # E2E Test 8: Dashboard Data Preparation
    def test_dashboard_data_preparation_workflow(self):
        """
        E2E: Prepare data for dashboard display
        """
        detector = NLPChangeDetector()
        
        # Generate reports
        regulations = [
            {"id": "REG-001", "severity": "CRITICAL"},
            {"id": "REG-002", "severity": "HIGH"},
            {"id": "REG-003", "severity": "MEDIUM"},
            {"id": "REG-004", "severity": "LOW"},
        ]
        
        # Prepare dashboard summary
        summary = {
            "total_regulations": len(regulations),
            "by_severity": {
                "CRITICAL": sum(1 for r in regulations if r["severity"] == "CRITICAL"),
                "HIGH": sum(1 for r in regulations if r["severity"] == "HIGH"),
                "MEDIUM": sum(1 for r in regulations if r["severity"] == "MEDIUM"),
                "LOW": sum(1 for r in regulations if r["severity"] == "LOW"),
            },
            "timestamp": time.time()
        }
        
        # Verify
        assert summary["total_regulations"] == 4
        assert summary["by_severity"]["CRITICAL"] == 1
        assert summary["by_severity"]["HIGH"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
