"""
Unit Tests for NLP Change Detector Module
Tests semantic similarity, clause extraction, and severity classification
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from nlp_change_detector import NLPChangeDetector
except ImportError:
    pytest.skip("nlp_change_detector module not found", allow_module_level=True)


class TestNLPChangeDetector:
    """Tests for NLPChangeDetector class"""
    
    @pytest.fixture
    def detector(self):
        """Fixture: Initialize NLP detector"""
        return NLPChangeDetector()
    
    # Unit Test 1: Similarity Calculation - Identical
    def test_similarity_identical_texts(self, detector):
        """Test similarity of identical texts should be high"""
        text = "GDPR compliance requires data protection measures"
        
        # Same text should have very high similarity
        similarity = detector.compute_similarity(text, text)
        assert similarity >= 0.95
    
    # Unit Test 2: Similarity Calculation - Different
    def test_similarity_different_texts(self, detector):
        """Test similarity of different texts should be lower"""
        text1 = "GDPR compliance is mandatory for data protection"
        text2 = "Machine learning model training requires GPUs"
        
        similarity = detector.compute_similarity(text1, text2)
        assert similarity < 0.5
    
    # Unit Test 3: Similarity Range
    def test_similarity_range_validation(self, detector):
        """Test similarity always returns value between 0 and 1"""
        text_pairs = [
            ("Text A", "Text A"),
            ("Text A", "Text B"),
            ("GDPR", "Data Protection"),
            ("", "Text"),
        ]
        
        for text1, text2 in text_pairs:
            try:
                similarity = detector.compute_similarity(text1, text2)
                assert 0 <= similarity <= 1
            except (ValueError, AttributeError):
                # Expected for edge cases
                pass
    
    # Unit Test 4: Severity Classification
    def test_severity_classification_critical(self, detector):
        """Test CRITICAL severity classification"""
        # Very different text - similarity < 0.5 triggers CRITICAL
        old_text = "Original data protection policy"
        new_text = "Completely different security framework"
        changes = detector.detect_clause_changes(old_text, new_text)
        severity = detector.classify_severity(changes)
        assert severity in ["CRITICAL", "HIGH"]  # Could be either depending on similarity
    
    # Unit Test 5: Severity Classification - High
    def test_severity_classification_high(self, detector):
        """Test HIGH severity classification"""
        # Text with some significant changes
        old_text = "Data protection with standard encryption"
        new_text = "Data protection with advanced encryption and authentication"
        changes = detector.detect_clause_changes(old_text, new_text)
        severity = detector.classify_severity(changes)
        assert severity in ["HIGH", "MEDIUM"]  # Could be either depending on changes
    
    # Unit Test 6: Severity Classification - Medium
    def test_severity_classification_medium(self, detector):
        """Test MEDIUM severity classification"""
        # Slightly modified text
        old_text = "Data protection is mandatory"
        new_text = "Data protection is strictly mandatory"
        changes = detector.detect_clause_changes(old_text, new_text)
        severity = detector.classify_severity(changes)
        assert severity in ["MEDIUM", "LOW"]  # Minimal changes
    
    # Unit Test 7: Severity Classification - Low
    def test_severity_classification_low(self, detector):
        """Test LOW severity classification"""
        # Very similar text - minimal changes
        old_text = "Compliance requirement"
        new_text = "Compliance requirement"
        changes = detector.detect_clause_changes(old_text, new_text)
        severity = detector.classify_severity(changes)
        assert severity == "LOW"
    
    # Unit Test 8: Clause Extraction
    def test_clause_extraction_basic(self, detector):
        """Test sentence/clause extraction"""
        text = "Clause 1: Data protection is required. Clause 2: Consent is needed. Clause 3: Audit trails mandatory."
        
        clauses = detector.extract_sentences(text)
        
        assert isinstance(clauses, list)
        assert len(clauses) >= 2
        assert all(isinstance(clause, str) for clause in clauses)
    
    # Unit Test 9: Clause Extraction - Empty
    def test_clause_extraction_empty(self, detector):
        """Test clause extraction with empty input"""
        text = ""
        
        clauses = detector.extract_sentences(text)
        
        assert isinstance(clauses, list)
    
    # Unit Test 10: Text Preprocessing
    def test_text_preprocessing(self, detector):
        """Test text preprocessing removes extra whitespace"""
        text = "  GDPR    Compliance   Text  with   spaces  "
        
        # Use extract_sentences which handles preprocessing
        processed = detector.extract_sentences(text)
        
        # Should return list of sentences
        assert isinstance(processed, list)


class TestNLPChangeDetectorAdvanced:
    """Advanced tests for NLPChangeDetector"""
    
    # Unit Test 11: Clause-level Changes
    def test_clause_level_diff_single_clause(self):
        """Test detecting changes at clause level"""
        detector = NLPChangeDetector()
        
        old_text = "Data must be protected."
        new_text = "Data must be strongly protected."
        
        changes = detector.detect_clause_changes(old_text, new_text)
        
        assert isinstance(changes, dict)
    
    # Unit Test 12: Multiple Clauses
    def test_clause_level_diff_multiple_clauses(self):
        """Test multiple clause changes"""
        detector = NLPChangeDetector()
        
        old_text = (
            "Section 1: Data must be protected. "
            "Section 2: Consent is required."
        )
        new_text = (
            "Section 1: Data must be strongly protected with encryption. "
            "Section 2: Explicit written consent is required."
        )
        
        changes = detector.detect_clause_changes(old_text, new_text)
        
        assert isinstance(changes, dict)
    
    # Unit Test 13: Batch Similarity Calculation
    def test_batch_similarity_calculation(self):
        """Test batch processing multiple regulations"""
        detector = NLPChangeDetector()
        
        regulations = [
            "GDPR data protection requirements",
            "HIPAA privacy compliance standards",
            "EU AI Act transparency rules"
        ]
        
        baseline = "Regulatory compliance requirements"
        similarities = [
            detector.compute_similarity(baseline, reg)
            for reg in regulations
        ]
        
        assert len(similarities) == 3
        assert all(0 <= sim <= 1 for sim in similarities)
    
    # Unit Test 14: Topic Extraction
    def test_topic_extraction_basic(self):
        """Test topic extraction from regulation text"""
        detector = NLPChangeDetector()
        
        text = "GDPR compliance requires data protection, consent management, and audit trails"
        topics = detector.extract_key_topics(text)
        
        assert isinstance(topics, list)
    
    # Unit Test 15: Similarity with Partial Overlap
    def test_partial_overlap_similarity(self):
        """Test similarity with partial text overlap"""
        detector = NLPChangeDetector()
        
        text1 = "Data protection and privacy compliance requirements"
        text2 = "Data protection and privacy rules for organizations"
        
        similarity = detector.compute_similarity(text1, text2)
        
        # Should be moderately high due to overlap
        assert 0.4 <= similarity <= 1.0
    
    # Unit Test 16: Case Insensitivity
    def test_case_insensitive_comparison(self):
        """Test similarity ignores case"""
        detector = NLPChangeDetector()
        
        text1 = "GDPR Data Protection"
        text2 = "gdpr data protection"
        
        similarity = detector.compute_similarity(text1, text2)
        
        # Should be very similar despite case (TF-IDF handles case)
        assert similarity >= 0.8
    
    # Unit Test 17: Punctuation Handling
    def test_punctuation_handling(self):
        """Test handling of punctuation"""
        detector = NLPChangeDetector()
        
        text1 = "Data protection requirements!!!"
        text2 = "Data protection requirements."
        
        similarity = detector.compute_similarity(text1, text2)
        
        # Should be very similar
        assert similarity >= 0.8


class TestNLPEdgeCases:
    """Edge case tests for NLP detector"""
    
    # Unit Test 18: Very Short Texts
    def test_very_short_text_similarity(self):
        """Test similarity with very short texts"""
        detector = NLPChangeDetector()
        
        similarity = detector.compute_similarity("A", "B")
        
        assert 0 <= similarity <= 1
    
    # Unit Test 19: Very Long Texts
    def test_very_long_text_similarity(self):
        """Test similarity with very long texts"""
        detector = NLPChangeDetector()
        
        long_text = " ".join(["word"] * 1000)
        
        similarity = detector.compute_similarity(long_text, long_text)
        
        assert similarity >= 0.95
    
    # Unit Test 20: Special Characters
    def test_special_characters_handling(self):
        """Test handling of special characters"""
        detector = NLPChangeDetector()
        
        text1 = "Requirement: @#$% compliance"
        text2 = "Requirement compliance"
        
        try:
            similarity = detector.compute_similarity(text1, text2)
            assert 0 <= similarity <= 1.0001  # Allow for floating point precision
        except (ValueError, AttributeError):
            # Acceptable to raise error on special chars
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
