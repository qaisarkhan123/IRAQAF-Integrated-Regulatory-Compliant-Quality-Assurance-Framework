import pytest
from pathlib import Path
import sys

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dashboard.app import (
    load_json,
    validate_and_sanitize_input,
    batch_process_evidence_files,
    _hash_file,
)


def test_load_json_valid():
    """Test loading valid JSON"""
    test_file = ROOT / "test_data" / "valid.json"
    result = load_json(str(test_file))
    assert isinstance(result, dict)
    assert result.get("module") == "L1"


def test_validate_input_email():
    """Test email validation"""
    is_valid, sanitized, error = validate_and_sanitize_input(
        "test@example.com",
        input_type="email",
    )
    assert is_valid
    assert "@" in sanitized
    # Accept empty string or None (no error)
    assert not error


def test_validate_input_malicious():
    """Test that malicious input is blocked/sanitized"""
    is_valid, sanitized, error = validate_and_sanitize_input(
        "../../../etc/passwd",
        input_type="filename",
    )
    assert ".." not in sanitized


def test_hash_file_consistency():
    """Test file hashing is consistent"""
    test_file = ROOT / "test_data" / "sample.pdf"
    hash1 = _hash_file(str(test_file))
    hash2 = _hash_file(str(test_file))
    assert hash1 == hash2
    assert isinstance(hash1, str)
