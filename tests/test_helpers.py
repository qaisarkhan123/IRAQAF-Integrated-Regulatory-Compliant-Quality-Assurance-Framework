"""
Unit tests for IRAQAF dashboard helper functions.

Run with: 
    pytest tests/test_helpers.py -v
    
Install: 
    pip install pytest pytest-cov pytest-mock
"""

import pytest
import pandas as pd
import json
import os
import tempfile
from pathlib import Path
import sys

# Add dashboard directory to path
dashboard_dir = Path(__file__).parent.parent / "dashboard"
sys.path.insert(0, str(dashboard_dir))

print(f"[TEST] Python path includes: {dashboard_dir}")
print(f"[TEST] Dashboard app.py exists: {(dashboard_dir / 'app.py').exists()}")

# Now we can import from app
try:
    import app
    print("[TEST] Successfully imported app module")
except ImportError as e:
    print(f"[TEST] Failed to import app: {e}")
    raise


class TestDeltaBadge:
    """Test suite for _delta_badge function"""

    def test_positive_delta(self):
        """Test upward change shows green arrow"""
        result = app._delta_badge(10.0, 5.0)
        assert "▲" in result
        assert "#00c851" in result  # green color
        assert "+5.00" in result

    def test_negative_delta(self):
        """Test downward change shows red arrow"""
        result = app._delta_badge(5.0, 10.0)
        assert "▼" in result
        assert "#ff4b4b" in result  # red color
        assert "-5.00" in result

    def test_no_change(self):
        """Test equal values show gray square"""
        result = app._delta_badge(5.0, 5.0)
        assert "■" in result
        assert "#999999" in result  # gray color
        assert "+0.00" in result

    def test_none_old_value(self):
        """Test None old value returns dash"""
        result = app._delta_badge(10.0, None)
        assert result == "—"

    def test_none_new_value(self):
        """Test None new value returns dash"""
        result = app._delta_badge(None, 5.0)
        assert result == "—"

    def test_both_none(self):
        """Test both None returns dash"""
        result = app._delta_badge(None, None)
        assert result == "—"


class TestHumanSize:
    """Test suite for _human_size function"""

    def test_bytes(self):
        assert app._human_size(500) == "500 B"

    def test_kilobytes(self):
        assert app._human_size(2048) == "2 KB"

    def test_megabytes(self):
        assert app._human_size(5 * 1024 * 1024) == "5 MB"

    def test_gigabytes(self):
        assert app._human_size(3 * 1024 * 1024 * 1024) == "3 GB"

    def test_zero(self):
        assert app._human_size(0) == "0 B"


class TestLabelFromPath:
    """Test suite for _label_from_path function"""

    def test_with_timestamp(self):
        path = "reports/L1-20240115-143022.json"
        assert app._label_from_path(path) == "20240115-143022"

    def test_without_timestamp(self):
        path = "reports/AGG-latest.json"
        assert app._label_from_path(path) == "AGG-latest"

    def test_complex_path(self):
        path = "/var/data/reports/L3-20231201-093045.json"
        assert app._label_from_path(path) == "20231201-093045"

    def test_windows_path(self):
        """Test Windows-style path"""
        path = "C:\\Users\\khan\\reports\\L1-20240115-143022.json"
        assert app._label_from_path(path) == "20240115-143022"


class TestHashFile:
    """Test suite for _hash_file function"""

    def test_hash_small_file(self):
        """Test hashing a small text file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_path = f.name

        try:
            mtime = os.path.getmtime(temp_path)
            result = app._hash_file(temp_path, _mtime=mtime)
            assert result is not None
            assert len(result) == 64  # SHA256 produces 64 hex chars
            assert isinstance(result, str)
        finally:
            os.unlink(temp_path)

    def test_hash_nonexistent_file(self):
        """Test hashing returns None for missing file"""
        result = app._hash_file("C:\\nonexistent\\path\\file.txt")
        assert result is None

    def test_hash_consistency(self):
        """Test same content produces same hash"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("consistent content")
            temp_path = f.name

        try:
            mtime = os.path.getmtime(temp_path)
            hash1 = app._hash_file(temp_path, _mtime=mtime)
            hash2 = app._hash_file(temp_path, _mtime=mtime)
            assert hash1 == hash2
        finally:
            os.unlink(temp_path)


class TestLoadJson:
    """Test suite for _load_json function"""

    def test_load_valid_json(self):
        """Test loading valid JSON file"""
        data = {"module": "L1", "score": 95.5}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name

        try:
            result = app._load_json(temp_path)
            assert result == data
        finally:
            os.unlink(temp_path)

    def test_load_invalid_json(self):
        """Test loading invalid JSON returns None"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            temp_path = f.name

        try:
            result = app._load_json(temp_path)
            assert result is None
        finally:
            os.unlink(temp_path)

    def test_load_nonexistent_file(self):
        """Test loading missing file returns None"""
        result = app._load_json("C:\\nonexistent\\file.json")
        assert result is None


class TestNormalizeClauseEvidence:
    """Test suite for _normalize_clause_evidence function"""

    def test_normalize_empty_report(self):
        """Test normalizing empty report"""
        result = app._normalize_clause_evidence({})
        assert result == {}

    def test_normalize_adds_evidence_links(self):
        """Test that missing evidence_links are added"""
        report = {
            "metrics": {
                "clauses": [
                    {
                        "framework": "GDPR",
                        "id": "Art5",
                        "evidence": [{"path": "doc1.pdf"}, {"path": "doc2.pdf"}]
                    }
                ]
            }
        }

        result = app._normalize_clause_evidence(report)
        assert "evidence_links" in result["metrics"]["clauses"][0]
        assert len(result["metrics"]["clauses"][0]["evidence_links"]) == 2

    def test_normalize_preserves_existing_links(self):
        """Test that existing evidence_links are preserved"""
        report = {
            "metrics": {
                "clauses": [
                    {
                        "framework": "GDPR",
                        "id": "Art5",
                        "evidence_links": ["existing.pdf"]
                    }
                ]
            }
        }

        result = app._normalize_clause_evidence(report)
        assert "existing.pdf" in result["metrics"]["clauses"][0]["evidence_links"]


class TestSanitizeName:
    """Test suite for _sanitize_name function"""

    def test_sanitize_normal_name(self):
        """Test sanitizing normal filename"""
        assert app._sanitize_name("document.pdf") == "document.pdf"

    def test_sanitize_special_chars(self):
        """Test sanitizing removes special characters"""
        result = app._sanitize_name("file@#$%name!.pdf")
        # Should only keep allowed characters
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_sanitize_path_separators(self):
        """Test sanitizing removes path separators"""
        result = app._sanitize_name("../../../etc/passwd")
        assert "/" not in result
        assert "\\" not in result


# Pytest configuration
@pytest.fixture
def sample_l1_report():
    """Fixture providing sample L1 report data"""
    return {
        "module": "L1",
        "score": 92.5,
        "band": "green",
        "metrics": {
            "coverage_percent": 95.0,
            "clauses": [
                {
                    "framework": "GDPR",
                    "id": "Art5_Data_Principles",
                    "passed": True,
                    "weight": 1.0
                },
                {
                    "framework": "EU_AI_ACT",
                    "id": "Art9_Data_Governance",
                    "passed": False,
                    "weight": 0.8,
                    "why_failed": "Missing data lineage documentation"
                }
            ]
        },
        "evidence": ["docs/privacy_policy.pdf", "docs/dpia.docx"]
    }


@pytest.fixture
def temp_reports_dir(tmp_path):
    """Fixture providing temporary reports directory"""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    return reports_dir


# Integration tests
class TestIntegration:
    """Integration tests for end-to-end workflows"""

    def test_full_report_loading_workflow(self, sample_l1_report, temp_reports_dir):
        """Test complete workflow of saving and loading a report"""
        # Save report
        report_path = temp_reports_dir / "L1-20240115-143022.json"
        with open(report_path, 'w') as f:
            json.dump(sample_l1_report, f)

        # Load and normalize
        loaded = app._load_json(str(report_path))
        assert loaded is not None

        normalized = app._normalize_clause_evidence(loaded)
        assert "evidence_links" in normalized["metrics"]["clauses"][0]


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v", "--tb=short"])
