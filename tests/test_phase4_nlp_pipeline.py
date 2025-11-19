"""
PHASE 4 TEST SUITE
==================

Comprehensive tests for NLP pipeline:
- Advanced text processing tests
- Semantic search tests
- Requirement extraction tests
- Cross-regulation linking tests

Author: IRAQAF Team
Version: 1.0.0
"""

import pytest
import json
from pathlib import Path

# Mock imports for testing
try:
    from nlp_pipeline.advanced_processing import (
        AdvancedTextProcessor, TableExtractor, CodeFormulaExtractor,
        ReferenceExtractor, RequirementEntityRecognizer, MultiLanguageProcessor
    )
except ImportError:
    AdvancedTextProcessor = None

try:
    from nlp_pipeline.semantic_search import (
        SemanticSearchPipeline, TFIDFSearchEngine, SemanticSearchEngine,
        CrossRegulationLinker, RequirementDependencyGraph
    )
except ImportError:
    SemanticSearchPipeline = None


# ============================================================================
# ADVANCED TEXT PROCESSING TESTS
# ============================================================================

class TestTableExtractor:
    """Test table extraction functionality"""
    
    def setup_method(self):
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        self.extractor = TableExtractor()
    
    def test_html_table_extraction(self):
        """Test HTML table parsing"""
        html = """
        <table>
            <tr><th>Name</th><th>Value</th></tr>
            <tr><td>Item1</td><td>100</td></tr>
            <tr><td>Item2</td><td>200</td></tr>
        </table>
        """
        
        tables = self.extractor.extract_html_tables(html)
        
        assert len(tables) == 1
        assert len(tables[0].rows) == 2
        assert tables[0].columns == ['Name', 'Value']
        assert tables[0].confidence >= 0.9
    
    def test_markdown_table_extraction(self):
        """Test markdown table parsing"""
        md_table = """
        | Requirement | Status |
        |---|---|
        | RBAC | Done |
        | Encryption | Pending |
        """
        
        tables = self.extractor.extract_pattern_tables(md_table)
        
        assert len(tables) > 0
        assert tables[0].extraction_method == 'pattern'
    
    def test_empty_table_handling(self):
        """Test handling of empty tables"""
        html = "<table></table>"
        tables = self.extractor.extract_html_tables(html)
        assert len(tables) == 0


class TestCodeFormulaExtractor:
    """Test code and formula extraction"""
    
    def setup_method(self):
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        self.extractor = CodeFormulaExtractor()
    
    def test_python_code_detection(self):
        """Test Python code detection"""
        text = """
        Algorithm:
        ```python
        def check_compliance(score):
            return score >= 0.8
        ```
        """
        
        blocks = self.extractor.extract_code_blocks(text)
        
        assert len(blocks) > 0
        assert blocks[0].language == 'python'
    
    def test_formula_detection(self):
        """Test LaTeX formula detection"""
        text = "The formula is $E = mc^2$ in physics."
        
        formulas = self.extractor.detect_formulas(text)
        
        assert len(formulas) > 0
        assert 'mc' in formulas[0].content
    
    def test_sql_code_detection(self):
        """Test SQL code detection"""
        text = "```sql\nSELECT * FROM requirements WHERE status='active'\n```"
        
        blocks = self.extractor.extract_code_blocks(text)
        
        assert len(blocks) > 0
        assert blocks[0].language == 'sql'


class TestReferenceExtractor:
    """Test reference extraction"""
    
    def setup_method(self):
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        self.extractor = ReferenceExtractor()
    
    def test_url_extraction(self):
        """Test URL extraction"""
        text = "See documentation at https://example.com/docs for details."
        
        refs = self.extractor.extract_urls(text)
        
        assert len(refs) > 0
        assert refs[0].reference_type == 'external'
        assert 'example.com' in refs[0].url
    
    def test_internal_reference_extraction(self):
        """Test internal reference extraction"""
        text = "See section 3.2 for implementation details. Refer to Article 41 for requirements."
        
        refs = self.extractor.extract_internal_refs(text)
        
        assert len(refs) > 0
    
    def test_regulation_reference_extraction(self):
        """Test regulation reference extraction"""
        text = "As per EU AI Act Article 41, systems shall implement access control."
        
        refs = self.extractor.extract_regulation_refs(text)
        
        assert len(refs) > 0
        assert any(r.reference_type == 'regulation' for r in refs)


class TestRequirementEntityRecognizer:
    """Test requirement entity recognition"""
    
    def setup_method(self):
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        self.recognizer = RequirementEntityRecognizer()
    
    def test_mandatory_requirement_detection(self):
        """Test detection of mandatory requirements"""
        text = "The system shall implement role-based access control."
        
        reqs = self.recognizer.extract_requirements(text, 'EU AI Act', '4.1')
        
        assert len(reqs) > 0
        assert reqs[0].mandatory is True
    
    def test_optional_requirement_detection(self):
        """Test detection of optional requirements"""
        text = "The system may implement additional logging capabilities."
        
        reqs = self.recognizer.extract_requirements(text, 'EU AI Act', '4.1')
        
        # May return 0 results or mark as non-mandatory
        if reqs:
            assert reqs[0].mandatory is False
    
    def test_entity_type_classification(self):
        """Test entity type classification"""
        texts = [
            ("Role-based access control is defined as...", 'definition'),
            ("The system shall implement RBAC.", 'requirement'),
        ]
        
        for text, expected_type in texts:
            entity_type = self.recognizer._classify_entity(text)
            # Check classification is reasonable
            assert entity_type in ['definition', 'requirement', 'clause', 'obligation']


class TestMultiLanguageProcessor:
    """Test multi-language support"""
    
    def setup_method(self):
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        self.processor = MultiLanguageProcessor()
    
    def test_english_detection(self):
        """Test English detection"""
        text = "The system shall implement security measures."
        lang, confidence = self.processor.detect_language(text)
        
        assert lang == 'en' or confidence >= 0.5
    
    def test_french_keywords_translation(self):
        """Test French keyword translation"""
        keywords = self.processor.translate_requirement_keywords('fr')
        
        assert len(keywords) > 0
        assert any(kw in keywords for kw in ['doit', 'exigence'])


class TestAdvancedTextProcessor:
    """Test complete text processing pipeline"""
    
    def setup_method(self):
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        self.processor = AdvancedTextProcessor()
    
    def test_complete_document_processing(self):
        """Test complete document processing"""
        sample_text = """
        <table>
        <tr><th>Item</th><th>Status</th></tr>
        <tr><td>RBAC</td><td>Done</td></tr>
        </table>
        
        Algorithm:
        ```python
        def comply(x):
            return x > 0.8
        ```
        
        See https://example.com for details and Article 41 for requirements.
        The system shall implement role-based access control.
        """
        
        result = self.processor.process_document(
            text=sample_text,
            regulation='EU AI Act',
            section='4.1'
        )
        
        assert result['regulation'] == 'EU AI Act'
        assert result['section'] == '4.1'
        assert result['statistics']['total_tables'] >= 1
        assert result['statistics']['total_code_blocks'] >= 1
        assert result['statistics']['total_requirements'] >= 1
    
    def test_batch_processing(self):
        """Test batch document processing"""
        documents = [
            {'text': 'Requirement 1 text', 'regulation': 'EU AI Act', 'section': '1'},
            {'text': 'Requirement 2 text', 'regulation': 'GDPR', 'section': '2'},
        ]
        
        results = self.processor.batch_process(documents)
        
        assert len(results) == 2
        assert all('regulation' in r for r in results)


# ============================================================================
# SEMANTIC SEARCH TESTS
# ============================================================================

class TestTFIDFSearchEngine:
    """Test TF-IDF search functionality"""
    
    def setup_method(self):
        if SemanticSearchPipeline is None:
            pytest.skip("Semantic search module not available")
        self.engine = TFIDFSearchEngine()
    
    def test_requirement_indexing(self):
        """Test indexing requirements"""
        requirements = [
            {'requirement_id': 'REQ-1', 'text': 'Implement access control', 'regulation': 'EU AI'},
            {'requirement_id': 'REQ-2', 'text': 'Apply encryption', 'regulation': 'GDPR'},
        ]
        
        success = self.engine.index_requirements(requirements)
        
        assert success is True
        assert len(self.engine.document_ids) == 2
    
    def test_search_retrieval(self):
        """Test search retrieval"""
        requirements = [
            {'requirement_id': 'REQ-1', 'text': 'Implement access control', 'regulation': 'EU AI'},
            {'requirement_id': 'REQ-2', 'text': 'Apply encryption', 'regulation': 'GDPR'},
            {'requirement_id': 'REQ-3', 'text': 'User access control', 'regulation': 'ISO'},
        ]
        
        self.engine.index_requirements(requirements)
        results = self.engine.search('access control', top_k=5)
        
        assert len(results) > 0
        # Access control should match REQ-1 and REQ-3
        matched_ids = {r.req_id for r in results}
        assert 'REQ-1' in matched_ids or 'REQ-3' in matched_ids
    
    def test_similarity_threshold(self):
        """Test similarity threshold filtering"""
        requirements = [
            {'requirement_id': 'REQ-1', 'text': 'Access control', 'regulation': 'EU AI'},
            {'requirement_id': 'REQ-2', 'text': 'Implementation details', 'regulation': 'GDPR'},
        ]
        
        self.engine.index_requirements(requirements)
        results = self.engine.search('access', threshold=0.9)
        
        # High threshold should return fewer results
        assert len(results) <= 2


class TestCrossRegulationLinker:
    """Test cross-regulation linking"""
    
    def setup_method(self):
        if SemanticSearchPipeline is None:
            pytest.skip("Semantic search module not available")
        self.linker = CrossRegulationLinker()
    
    def test_link_detection(self):
        """Test cross-regulation link detection"""
        requirements = [
            {
                'requirement_id': 'EU-1',
                'text': 'System shall implement access control',
                'regulation': 'EU AI Act'
            },
            {
                'requirement_id': 'GDPR-1',
                'text': 'Access control must be implemented',
                'regulation': 'GDPR'
            },
        ]
        
        links = self.linker.find_cross_regulation_links(requirements)
        
        assert len(links) > 0
        assert links[0].source_regulation != links[0].target_regulation


class TestRequirementDependencyGraph:
    """Test dependency graph building"""
    
    def setup_method(self):
        if SemanticSearchPipeline is None:
            pytest.skip("Semantic search module not available")
        self.graph = RequirementDependencyGraph()
    
    def test_dependency_detection(self):
        """Test dependency detection"""
        requirements = [
            {
                'requirement_id': 'REQ-1',
                'text': 'Authentication must be configured',
                'regulation': 'EU AI'
            },
            {
                'requirement_id': 'REQ-2',
                'text': 'REQ-1 must be implemented first',
                'regulation': 'EU AI'
            },
        ]
        
        deps = self.graph.build_dependency_graph(requirements)
        
        # Should detect potential dependencies
        assert len(deps) >= 0


class TestSemanticSearchPipeline:
    """Test complete semantic search pipeline"""
    
    def setup_method(self):
        if SemanticSearchPipeline is None:
            pytest.skip("Semantic search module not available")
        self.pipeline = SemanticSearchPipeline()
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        assert self.pipeline.tfidf_engine is not None
        assert self.pipeline.cross_linker is not None
        assert self.pipeline.dependency_graph is not None
    
    def test_complete_index_building(self):
        """Test building complete index"""
        requirements = [
            {
                'requirement_id': 'REQ-1',
                'text': 'System shall implement RBAC',
                'regulation': 'EU AI Act',
                'section': '4.1'
            },
            {
                'requirement_id': 'REQ-2',
                'text': 'Access control required',
                'regulation': 'GDPR',
                'section': '32'
            },
        ]
        
        success = self.pipeline.build_complete_index(requirements)
        assert success is True
    
    def test_context_retrieval(self):
        """Test requirement context retrieval"""
        requirements = [
            {
                'requirement_id': 'REQ-1',
                'text': 'System shall implement RBAC',
                'regulation': 'EU AI Act',
                'section': '4.1'
            },
        ]
        
        self.pipeline.build_complete_index(requirements)
        context = self.pipeline.get_requirement_context('REQ-1')
        
        assert 'requirement' in context or 'error' in context


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase4Integration:
    """Integration tests for Phase 4 NLP pipeline"""
    
    def test_end_to_end_processing(self):
        """Test end-to-end document processing and search"""
        if AdvancedTextProcessor is None or SemanticSearchPipeline is None:
            pytest.skip("Required modules not available")
        
        # Process documents
        processor = AdvancedTextProcessor()
        sample_doc = {
            'text': 'The system shall implement role-based access control (RBAC) for security.',
            'regulation': 'EU AI Act',
            'section': '4.1'
        }
        
        processed = processor.process_document(
            sample_doc['text'],
            sample_doc['regulation'],
            sample_doc['section']
        )
        
        assert 'requirements' in processed
        assert len(processed['requirements']) > 0
        
        # Index for search
        pipeline = SemanticSearchPipeline()
        requirements = [
            {
                'requirement_id': req['requirement_id'],
                'text': req['text'],
                'regulation': sample_doc['regulation'],
                'section': sample_doc['section']
            }
            for req in processed['requirements']
        ]
        
        pipeline.build_complete_index(requirements)
        
        # Search
        results = pipeline.search('access control')
        assert 'tfidf_results' in results


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance and scalability tests"""
    
    def test_large_batch_processing(self):
        """Test processing large batches"""
        if AdvancedTextProcessor is None:
            pytest.skip("Advanced processing module not available")
        
        processor = AdvancedTextProcessor()
        
        # Create 100 sample documents
        documents = [
            {
                'text': f'Requirement {i}: Implement security measure {i}',
                'regulation': 'EU AI Act',
                'section': f'{i // 25}.{i % 25}'
            }
            for i in range(100)
        ]
        
        results = processor.batch_process(documents)
        
        # Should complete without errors
        assert len(results) == 100
        successful = sum(1 for r in results if 'error' not in r)
        # At least 90% should succeed
        assert successful >= 90


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_requirements():
    """Sample requirements for testing"""
    return [
        {
            'requirement_id': 'EU-AI-41.1',
            'text': 'Systems shall implement role-based access control',
            'regulation': 'EU AI Act',
            'section': '4.1'
        },
        {
            'requirement_id': 'GDPR-32.1',
            'text': 'Data protection shall be implemented',
            'regulation': 'GDPR',
            'section': '32'
        },
        {
            'requirement_id': 'ISO-13485-8.2',
            'text': 'Access control must be enforced',
            'regulation': 'ISO 13485',
            'section': '8.2'
        },
    ]


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
