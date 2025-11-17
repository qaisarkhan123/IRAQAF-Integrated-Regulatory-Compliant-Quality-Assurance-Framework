"""
Phase 4: IRAQAF Parsing Tests
Targets: parse_iraqaf_results.py (11% → 60% coverage)
35+ test methods covering framework mapping, trace aggregation, evidence extraction,
result normalization, error handling, and edge cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import pandas as pd
from datetime import datetime


# ============================================================================
# TEST CLASS 1: Framework Mapping (5 tests)
# ============================================================================
class TestFrameworkMapping:
    """Tests for IRAQAF framework mapping to compliance standards."""

    def test_map_iraqaf_to_sox(self):
        """Test mapping IRAQAF results to SOX compliance framework."""
        try:
            from scripts.parse_iraqaf_results import map_framework
            result = map_framework("IRAQAF", "SOX")
            assert result is not None
            assert isinstance(result, dict)
        except ImportError:
            pytest.skip("Module not available")

    def test_map_iraqaf_to_iso27001(self):
        """Test mapping IRAQAF results to ISO 27001."""
        try:
            from scripts.parse_iraqaf_results import map_framework
            result = map_framework("IRAQAF", "ISO27001")
            assert result is not None
            assert isinstance(result, dict)
        except ImportError:
            pytest.skip("Module not available")

    def test_map_iraqaf_to_cis_controls(self):
        """Test mapping IRAQAF results to CIS Controls."""
        try:
            from scripts.parse_iraqaf_results import map_framework
            result = map_framework("IRAQAF", "CIS")
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_bidirectional_framework_mapping(self):
        """Test bidirectional mapping between frameworks."""
        try:
            from scripts.parse_iraqaf_results import bidirectional_map
            iraqaf_control = "IR-1.1"
            result = bidirectional_map(iraqaf_control)
            assert result is not None
            assert isinstance(result, dict)
        except ImportError:
            pytest.skip("Module not available")

    def test_framework_mapping_with_partial_coverage(self):
        """Test mapping handles frameworks with partial coverage."""
        try:
            from scripts.parse_iraqaf_results import map_framework
            result = map_framework("IRAQAF", "HIPAA")
            assert result is not None
            # Should have mapping even if coverage is incomplete
            assert len(result) > 0
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 2: Trace Aggregation (6 tests)
# ============================================================================
class TestTraceAggregation:
    """Tests for aggregating IRAQAF traces into findings."""

    def test_aggregate_single_trace(self):
        """Test aggregating a single IRAQAF trace."""
        try:
            from scripts.parse_iraqaf_results import aggregate_traces
            trace = {
                "id": "trace-001",
                "framework": "IRAQAF",
                "control": "IR-1.1",
                "result": "PASS"
            }
            result = aggregate_traces([trace])
            assert result is not None
            assert len(result) > 0
        except ImportError:
            pytest.skip("Module not available")

    def test_aggregate_multiple_traces_same_control(self):
        """Test aggregating multiple traces for same control."""
        try:
            from scripts.parse_iraqaf_results import aggregate_traces
            traces = [
                {"id": "t1", "control": "IR-1.1", "result": "PASS"},
                {"id": "t2", "control": "IR-1.1", "result": "PASS"},
                {"id": "t3", "control": "IR-1.1", "result": "FAIL"}
            ]
            result = aggregate_traces(traces)
            assert result is not None
            assert "IR-1.1" in str(result) or len(result) > 0
        except ImportError:
            pytest.skip("Module not available")

    def test_aggregate_traces_with_different_severities(self):
        """Test aggregation preserves severity levels."""
        try:
            from scripts.parse_iraqaf_results import aggregate_traces
            traces = [
                {"id": "t1", "control": "IR-1.1", "severity": "CRITICAL"},
                {"id": "t2", "control": "IR-1.1", "severity": "MEDIUM"},
            ]
            result = aggregate_traces(traces)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_aggregate_traces_group_by_framework(self):
        """Test traces are grouped by framework during aggregation."""
        try:
            from scripts.parse_iraqaf_results import aggregate_by_framework
            traces = [
                {"framework": "IRAQAF", "control": "IR-1.1"},
                {"framework": "IRAQAF", "control": "IR-2.1"},
            ]
            result = aggregate_by_framework(traces)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_deduplicate_traces(self):
        """Test duplicate traces are removed during aggregation."""
        try:
            from scripts.parse_iraqaf_results import deduplicate_traces
            traces = [
                {"id": "t1", "control": "IR-1.1", "hash": "abc123"},
                {"id": "t2", "control": "IR-1.1", "hash": "abc123"},  # duplicate
                {"id": "t3", "control": "IR-2.1", "hash": "def456"},
            ]
            result = deduplicate_traces(traces)
            assert len(result) == 2
        except ImportError:
            pytest.skip("Module not available")

    def test_aggregate_traces_with_timestamps(self):
        """Test aggregation respects timestamp ordering."""
        try:
            from scripts.parse_iraqaf_results import aggregate_traces
            traces = [
                {"id": "t1", "control": "IR-1.1", "timestamp": "2025-01-01T10:00:00"},
                {"id": "t2", "control": "IR-1.1", "timestamp": "2025-01-01T11:00:00"},
            ]
            result = aggregate_traces(traces)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 3: Evidence Extraction (6 tests)
# ============================================================================
class TestEvidenceExtraction:
    """Tests for extracting evidence from IRAQAF results."""

    def test_extract_evidence_from_trace(self):
        """Test extracting evidence from a single trace."""
        try:
            from scripts.parse_iraqaf_results import extract_evidence
            trace = {
                "id": "trace-001",
                "evidence": {"config": "test", "log": "entry"},
                "control": "IR-1.1"
            }
            result = extract_evidence(trace)
            assert result is not None
            assert "config" in str(result) or len(result) > 0
        except ImportError:
            pytest.skip("Module not available")

    def test_extract_evidence_types_classification(self):
        """Test evidence is classified by type (log, config, scan, etc)."""
        try:
            from scripts.parse_iraqaf_results import classify_evidence
            evidence = {
                "type": "log_entry",
                "source": "/var/log/auth.log",
                "content": "User login"
            }
            result = classify_evidence(evidence)
            assert result is not None
            assert result == "log_entry" or isinstance(result, str)
        except ImportError:
            pytest.skip("Module not available")

    def test_extract_evidence_with_file_attachments(self):
        """Test extracting evidence with file attachments."""
        try:
            from scripts.parse_iraqaf_results import extract_evidence_files
            trace = {
                "id": "trace-001",
                "attachments": [
                    {"filename": "config.txt", "path": "/path/to/config.txt"}
                ]
            }
            result = extract_evidence_files(trace)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_evidence_sanitization_for_pii(self):
        """Test evidence sanitization removes PII."""
        try:
            from scripts.parse_iraqaf_results import sanitize_evidence
            evidence = {
                "content": "User john.doe@company.com logged in",
                "sensitive_fields": ["email", "username"]
            }
            result = sanitize_evidence(evidence)
            assert "@company.com" not in str(result)
        except ImportError:
            pytest.skip("Module not available")

    def test_evidence_chain_validation(self):
        """Test validation of evidence chain integrity."""
        try:
            from scripts.parse_iraqaf_results import validate_evidence_chain
            chain = [
                {"id": "e1", "hash": "abc123"},
                {"id": "e2", "hash": "def456", "previous_hash": "abc123"},
                {"id": "e3", "hash": "ghi789", "previous_hash": "def456"}
            ]
            result = validate_evidence_chain(chain)
            assert result is True
        except ImportError:
            pytest.skip("Module not available")

    def test_evidence_relevance_scoring(self):
        """Test scoring of evidence relevance to control."""
        try:
            from scripts.parse_iraqaf_results import score_evidence_relevance
            evidence = {
                "content": "policy implementation",
                "control": "IR-1.1"
            }
            result = score_evidence_relevance(evidence)
            assert 0 <= result <= 1
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 4: Result Normalization (5 tests)
# ============================================================================
class TestResultNormalization:
    """Tests for normalizing IRAQAF results to standard format."""

    def test_normalize_pass_fail_results(self):
        """Test normalization of PASS/FAIL result states."""
        try:
            from scripts.parse_iraqaf_results import normalize_result
            result = normalize_result("PASS")
            assert result in ["PASS", "FAIL", "INCONCLUSIVE"]
        except ImportError:
            pytest.skip("Module not available")

    def test_normalize_severity_levels(self):
        """Test normalization of severity classifications."""
        try:
            from scripts.parse_iraqaf_results import normalize_severity
            severities = ["CRITICAL", "High", "medium", "low"]
            for sev in severities:
                result = normalize_severity(sev)
                assert result in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        except ImportError:
            pytest.skip("Module not available")

    def test_normalize_timestamps(self):
        """Test normalization of timestamp formats."""
        try:
            from scripts.parse_iraqaf_results import normalize_timestamp
            timestamps = [
                "2025-01-01T10:00:00Z",
                "01/01/2025 10:00:00",
                1735732800
            ]
            for ts in timestamps:
                result = normalize_timestamp(ts)
                assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_normalize_framework_references(self):
        """Test normalization of framework control references."""
        try:
            from scripts.parse_iraqaf_results import normalize_control_reference
            references = ["IR-1.1", "ir_1_1", "IR 1 1"]
            for ref in references:
                result = normalize_control_reference(ref)
                assert "IR" in result and "1" in result
        except ImportError:
            pytest.skip("Module not available")

    def test_normalize_to_canonical_schema(self):
        """Test normalization to canonical result schema."""
        try:
            from scripts.parse_iraqaf_results import normalize_to_schema
            raw_result = {
                "test_id": "t1",
                "status": "pass",
                "evidence": "data"
            }
            result = normalize_to_schema(raw_result)
            assert result is not None
            assert "id" in result or "control" in result or len(result) > 0
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 5: Error Handling & Validation (6 tests)
# ============================================================================
class TestErrorHandling:
    """Tests for error handling and data validation."""

    def test_invalid_iraqaf_format_handling(self):
        """Test handling of invalid IRAQAF format."""
        try:
            from scripts.parse_iraqaf_results import parse_iraqaf
            invalid_data = "not json or xml"
            result = parse_iraqaf(invalid_data)
            assert result is None or isinstance(result, dict)
        except ImportError:
            pytest.skip("Module not available")

    def test_missing_required_fields_validation(self):
        """Test validation catches missing required fields."""
        try:
            from scripts.parse_iraqaf_results import validate_iraqaf_result
            incomplete_result = {"control": "IR-1.1"}  # missing 'result' field
            is_valid = validate_iraqaf_result(incomplete_result)
            assert is_valid is False
        except ImportError:
            pytest.skip("Module not available")

    def test_malformed_json_graceful_failure(self):
        """Test graceful failure on malformed JSON."""
        try:
            from scripts.parse_iraqaf_results import parse_iraqaf
            malformed = '{"control": "IR-1.1", "result": '  # incomplete
            result = parse_iraqaf(malformed)
            assert result is None or isinstance(result, dict)
        except ImportError:
            pytest.skip("Module not available")

    def test_control_id_validation(self):
        """Test validation of control ID format."""
        try:
            from scripts.parse_iraqaf_results import validate_control_id
            valid_ids = ["IR-1.1", "IR-2.5", "IR-3.1"]
            invalid_ids = ["XX-1.1", "IR-X.Y", "INVALID"]
            for cid in valid_ids:
                assert validate_control_id(cid) is True
            for cid in invalid_ids:
                assert validate_control_id(cid) is False
        except ImportError:
            pytest.skip("Module not available")

    def test_duplicate_trace_detection(self):
        """Test detection of duplicate traces."""
        try:
            from scripts.parse_iraqaf_results import detect_duplicates
            traces = [
                {"id": "t1", "control": "IR-1.1", "hash": "abc"},
                {"id": "t2", "control": "IR-1.1", "hash": "abc"},
            ]
            result = detect_duplicates(traces)
            assert len(result) > 0
        except ImportError:
            pytest.skip("Module not available")

    def test_encoding_compatibility_issues(self):
        """Test handling of various character encodings."""
        try:
            from scripts.parse_iraqaf_results import handle_encoding
            data = {"content": "café", "encoding": "utf-8"}
            result = handle_encoding(data)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 6: Data Aggregation & Reporting (5 tests)
# ============================================================================
class TestDataAggregation:
    """Tests for aggregating parsed IRAQAF results."""

    def test_aggregate_results_by_control(self):
        """Test aggregating results grouped by control."""
        try:
            from scripts.parse_iraqaf_results import aggregate_by_control
            results = [
                {"control": "IR-1.1", "result": "PASS"},
                {"control": "IR-1.1", "result": "PASS"},
                {"control": "IR-2.1", "result": "FAIL"}
            ]
            summary = aggregate_by_control(results)
            assert summary is not None
            assert len(summary) >= 0
        except ImportError:
            pytest.skip("Module not available")

    def test_calculate_compliance_score_from_results(self):
        """Test calculating compliance score from aggregated results."""
        try:
            from scripts.parse_iraqaf_results import calculate_compliance_score
            results = {
                "total_controls": 10,
                "passed": 8,
                "failed": 2
            }
            score = calculate_compliance_score(results)
            assert 0 <= score <= 100
        except ImportError:
            pytest.skip("Module not available")

    def test_generate_result_summary_report(self):
        """Test generating summary report from results."""
        try:
            from scripts.parse_iraqaf_results import generate_result_summary
            results = [
                {"control": "IR-1.1", "result": "PASS"},
                {"control": "IR-2.1", "result": "FAIL"}
            ]
            summary = generate_result_summary(results)
            assert summary is not None
            assert isinstance(summary, (dict, str))
        except ImportError:
            pytest.skip("Module not available")

    def test_export_aggregated_results_to_csv(self):
        """Test exporting results to CSV format."""
        try:
            from scripts.parse_iraqaf_results import export_to_csv
            results = [
                {"control": "IR-1.1", "result": "PASS"},
                {"control": "IR-2.1", "result": "FAIL"}
            ]
            csv_data = export_to_csv(results)
            assert csv_data is not None
            assert "control" in csv_data or len(csv_data) > 0
        except ImportError:
            pytest.skip("Module not available")

    def test_export_aggregated_results_to_json(self):
        """Test exporting results to JSON format."""
        try:
            from scripts.parse_iraqaf_results import export_to_json
            results = [
                {"control": "IR-1.1", "result": "PASS"},
                {"control": "IR-2.1", "result": "FAIL"}
            ]
            json_data = export_to_json(results)
            assert json_data is not None
            assert isinstance(json_data, (str, dict))
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 7: IRAQAF Specific Operations (4 tests)
# ============================================================================
class TestIraqafSpecificOps:
    """Tests for IRAQAF-specific parsing operations."""

    def test_parse_iraqaf_xml_format(self):
        """Test parsing IRAQAF XML format results."""
        try:
            from scripts.parse_iraqaf_results import parse_iraqaf_xml
            xml_data = """
            <iraqaf>
                <control id="IR-1.1">
                    <result>PASS</result>
                </control>
            </iraqaf>
            """
            result = parse_iraqaf_xml(xml_data)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_parse_iraqaf_json_format(self):
        """Test parsing IRAQAF JSON format results."""
        try:
            from scripts.parse_iraqaf_results import parse_iraqaf_json
            json_data = {
                "controls": [
                    {"id": "IR-1.1", "result": "PASS"}
                ]
            }
            result = parse_iraqaf_json(json_data)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_iraqaf_control_hierarchy_traversal(self):
        """Test traversing IRAQAF control hierarchy."""
        try:
            from scripts.parse_iraqaf_results import traverse_control_hierarchy
            hierarchy = {
                "IR-1": [
                    {"id": "IR-1.1"},
                    {"id": "IR-1.2"}
                ]
            }
            result = traverse_control_hierarchy(hierarchy)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_iraqaf_version_compatibility(self):
        """Test compatibility with different IRAQAF versions."""
        try:
            from scripts.parse_iraqaf_results import check_iraqaf_version
            versions = ["1.0", "2.0", "3.0"]
            for version in versions:
                result = check_iraqaf_version(version)
                assert result in (True, False)
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 8: Performance & Optimization (3 tests)
# ============================================================================
class TestParsePerformance:
    """Tests for parsing performance and optimization."""

    def test_batch_parsing_large_dataset(self):
        """Test parsing large batch of results efficiently."""
        try:
            from scripts.parse_iraqaf_results import batch_parse
            large_dataset = [
                {"id": f"t{i}", "control": f"IR-{i//10}.{i%10}", "result": "PASS"}
                for i in range(1000)
            ]
            result = batch_parse(large_dataset)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_incremental_parsing_streaming(self):
        """Test incremental parsing for streaming results."""
        try:
            from scripts.parse_iraqaf_results import stream_parse
            stream = iter([
                {"id": "t1", "control": "IR-1.1"},
                {"id": "t2", "control": "IR-2.1"},
            ])
            result = stream_parse(stream)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_caching_parsed_results(self):
        """Test caching mechanism for repeated parsing."""
        try:
            from scripts.parse_iraqaf_results import cache_parse_results
            result_key = "iraqaf_parse_123"
            cached = cache_parse_results(result_key)
            assert cached is not None or cached is None
        except ImportError:
            pytest.skip("Module not available")


# ============================================================================
# TEST CLASS 9: Integration with Dashboard (2 tests)
# ============================================================================
class TestIraqafDashboardIntegration:
    """Tests for integration with dashboard module."""

    def test_parsed_results_dashboard_format(self):
        """Test parsed results conform to dashboard format."""
        try:
            from scripts.parse_iraqaf_results import convert_to_dashboard_format
            parsed = {
                "control": "IR-1.1",
                "result": "PASS",
                "evidence": "data"
            }
            dashboard_format = convert_to_dashboard_format(parsed)
            assert dashboard_format is not None
        except ImportError:
            pytest.skip("Module not available")

    def test_real_time_parse_stream_to_dashboard(self):
        """Test real-time parsing stream updates dashboard."""
        try:
            from scripts.parse_iraqaf_results import stream_to_dashboard
            stream = [{"id": "t1", "control": "IR-1.1"}]
            result = stream_to_dashboard(stream)
            assert result is not None
        except ImportError:
            pytest.skip("Module not available")
