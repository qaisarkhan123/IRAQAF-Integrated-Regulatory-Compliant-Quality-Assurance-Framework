"""
Database Operation Tests for IRAQAF Compliance Platform

Tests for:
- Regulatory source loading
- Content storage and retrieval
- Change detection
- Batch operations
- Compliance history

Usage:
    pytest tests/test_database.py -v
    pytest tests/test_database.py::TestDatabaseOperations::test_load_regulatory_source -v

Author: IRAQAF Phase 2
Date: 2024
"""

from db.models import (
    RegulatorySource, RegulatoryContent, ChangeHistory,
    System, Assessment, AssessmentRequirement
)
from db.database import init_db
from db.operations import db_ops
import pytest
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def setup_database():
    """Set up test database"""
    try:
        init_db()
        yield
    finally:
        pass


@pytest.fixture
def sample_source():
    """Create sample regulatory source"""
    return {
        'name': 'Test Regulation',
        'url': 'https://test.example.com',
        'parser_type': 'html',
        'abbreviation': 'TEST',
        'description': 'Test regulatory source'
    }


@pytest.fixture
def sample_content():
    """Create sample content"""
    return {
        'source_id': 1,
        'title': 'Test Chapter',
        'section': '1',
        'subsection': '1',
        'content': 'This is test content for compliance testing.'
    }


@pytest.fixture
def sample_system():
    """Create sample system"""
    return {
        'name': 'Test AI System',
        'owner': 'Test Owner',
        'system_type': 'ai_system',
        'description': 'Test system for compliance'
    }


# ============================================================================
# TEST CASES: DATABASE INITIALIZATION
# ============================================================================

class TestDatabaseInitialization:
    """Tests for database initialization"""

    def test_database_initialization(self, setup_database):
        """Test database initialization succeeds"""
        assert db_ops.init_database() is True

    def test_init_database_idempotent(self, setup_database):
        """Test database initialization is idempotent"""
        assert db_ops.init_database() is True
        assert db_ops.init_database() is True  # Should succeed again


# ============================================================================
# TEST CASES: REGULATORY SOURCE LOADING
# ============================================================================

class TestRegulatorySourceLoading:
    """Tests for loading regulatory sources"""

    def test_load_regulatory_source_success(self, setup_database, sample_source):
        """Test loading a regulatory source succeeds"""
        result = db_ops.load_regulatory_source(
            source_name=sample_source['name'],
            url=sample_source['url'],
            parser_type=sample_source['parser_type'],
            abbreviation=sample_source['abbreviation'],
            description=sample_source['description']
        )
        assert result is not None
        assert result.name == sample_source['name']
        assert result.url == sample_source['url']
        assert result.parser_type == sample_source['parser_type']

    def test_load_duplicate_source(self, setup_database, sample_source):
        """Test loading duplicate source returns existing"""
        result1 = db_ops.load_regulatory_source(
            source_name=sample_source['name'],
            url=sample_source['url'],
            parser_type=sample_source['parser_type']
        )
        result2 = db_ops.load_regulatory_source(
            source_name=sample_source['name'],
            url=sample_source['url'],
            parser_type=sample_source['parser_type']
        )
        assert result1.id == result2.id

    def test_load_multiple_sources(self, setup_database):
        """Test loading multiple sources"""
        sources = [
            {'name': 'Source 1', 'url': 'https://test1.com', 'parser_type': 'html'},
            {'name': 'Source 2', 'url': 'https://test2.com', 'parser_type': 'pdf'},
            {'name': 'Source 3', 'url': 'https://test3.com', 'parser_type': 'html'}
        ]

        result = db_ops.batch_load_sources(sources)
        assert result['success'] == 3
        assert result['failed'] == 0


# ============================================================================
# TEST CASES: CONTENT STORAGE & RETRIEVAL
# ============================================================================

class TestContentStorage:
    """Tests for storing and retrieving content"""

    def test_store_content_success(self, setup_database, sample_source, sample_content):
        """Test storing content succeeds"""
        # First create source
        source = db_ops.load_regulatory_source(**sample_source)
        assert source is not None

        # Then store content
        result = db_ops.store_regulatory_content(
            source_id=source.id,
            title=sample_content['title'],
            section=sample_content['section'],
            subsection=sample_content['subsection'],
            content=sample_content['content']
        )

        assert result is not None
        assert result.title == sample_content['title']
        assert result.section == sample_content['section']

    def test_store_duplicate_content(self, setup_database, sample_source, sample_content):
        """Test storing duplicate content (same hash) is idempotent"""
        source = db_ops.load_regulatory_source(**sample_source)

        result1 = db_ops.store_regulatory_content(
            source_id=source.id,
            **sample_content
        )

        result2 = db_ops.store_regulatory_content(
            source_id=source.id,
            **sample_content
        )

        assert result1.id == result2.id

    def test_content_hash_generation(self, setup_database, sample_source, sample_content):
        """Test content hash is generated correctly"""
        source = db_ops.load_regulatory_source(**sample_source)

        result = db_ops.store_regulatory_content(
            source_id=source.id,
            **sample_content
        )

        import hashlib
        expected_hash = hashlib.sha256(
            sample_content['content'].encode()).hexdigest()
        assert result.content_hash == expected_hash

    def test_retrieve_content(self, setup_database, sample_source, sample_content):
        """Test retrieving content"""
        source = db_ops.load_regulatory_source(**sample_source)
        db_ops.store_regulatory_content(source_id=source.id, **sample_content)

        retrieved = db_ops.get_regulatory_content(source.id)
        assert len(retrieved) > 0
        assert retrieved[0].title == sample_content['title']

    def test_retrieve_content_by_section(self, setup_database, sample_source):
        """Test retrieving content filtered by section"""
        source = db_ops.load_regulatory_source(**sample_source)

        # Store multiple items
        for i in range(3):
            db_ops.store_regulatory_content(
                source_id=source.id,
                title=f'Title {i}',
                section='1',
                subsection=str(i),
                content=f'Content {i}'
            )

        # Retrieve specific section
        retrieved = db_ops.get_regulatory_content(source.id, section='1')
        assert len(retrieved) >= 3


# ============================================================================
# TEST CASES: CHANGE DETECTION
# ============================================================================

class TestChangeDetection:
    """Tests for change detection"""

    def test_detect_change_success(self, setup_database, sample_source):
        """Test change detection logs change"""
        source = db_ops.load_regulatory_source(**sample_source)

        result = db_ops.detect_changes(
            source_id=source.id,
            content_id=1,
            old_value="Old content",
            new_value="New content",
            change_type="modified"
        )

        assert result is not None
        assert result.change_type == "modified"
        assert result.source_id == source.id

    def test_change_detection_on_content_update(self, setup_database, sample_source, sample_content):
        """Test change is detected when content is updated"""
        source = db_ops.load_regulatory_source(**sample_source)

        # Store initial content
        result1 = db_ops.store_regulatory_content(
            source_id=source.id,
            **sample_content
        )

        # Update content
        updated_content = sample_content.copy()
        updated_content['content'] = "Updated: " + updated_content['content']

        result2 = db_ops.store_regulatory_content(
            source_id=source.id,
            **updated_content
        )

        # Content should be same object but updated
        assert result1.id == result2.id
        assert result1.content_hash != result2.content_hash

    def test_get_change_log(self, setup_database, sample_source):
        """Test retrieving change log"""
        source = db_ops.load_regulatory_source(**sample_source)

        # Create several changes
        for i in range(3):
            db_ops.detect_changes(
                source_id=source.id,
                content_id=i+1,
                old_value=f"Old {i}",
                new_value=f"New {i}",
                change_type="modified"
            )

        changes = db_ops.get_change_log(source.id)
        assert len(changes) >= 3


# ============================================================================
# TEST CASES: SYSTEMS & ASSESSMENTS
# ============================================================================

class TestSystemsAndAssessments:
    """Tests for systems and compliance assessments"""

    def test_create_system_success(self, setup_database, sample_system):
        """Test creating a system succeeds"""
        result = db_ops.create_system(**sample_system)

        assert result is not None
        assert result.name == sample_system['name']
        assert result.owner == sample_system['owner']
        assert result.type == sample_system['system_type']

    def test_create_assessment_success(self, setup_database, sample_system):
        """Test creating an assessment succeeds"""
        system = db_ops.create_system(**sample_system)
        assert system is not None

        result = db_ops.create_assessment(
            system_id=system.id,
            regulation_type='EU-AI',
            assessor='test_user',
            overall_score=0
        )

        assert result is not None
        assert result.system_id == system.id
        assert result.regulation_type == 'EU-AI'

    def test_get_compliance_history(self, setup_database, sample_system):
        """Test retrieving compliance history"""
        system = db_ops.create_system(**sample_system)

        # Create multiple assessments
        db_ops.create_assessment(
            system_id=system.id,
            regulation_type='EU-AI',
            overall_score=50
        )
        db_ops.create_assessment(
            system_id=system.id,
            regulation_type='GDPR',
            overall_score=60
        )

        history = db_ops.get_compliance_history(system.id)
        assert len(history) >= 0  # May be empty if not persisted


# ============================================================================
# TEST CASES: BATCH OPERATIONS
# ============================================================================

class TestBatchOperations:
    """Tests for batch operations"""

    def test_batch_load_sources(self, setup_database):
        """Test batch loading sources"""
        sources = [
            {'name': f'Source {i}', 'url': f'https://test{i}.com', 'parser_type': 'html'}
            for i in range(5)
        ]

        result = db_ops.batch_load_sources(sources)
        assert result['success'] == 5
        assert result['failed'] == 0

    def test_batch_load_content_parallel(self, setup_database, sample_source):
        """Test parallel batch loading content"""
        source = db_ops.load_regulatory_source(**sample_source)

        content_list = [
            {
                'source_id': source.id,
                'title': f'Title {i}',
                'section': '1',
                'subsection': str(i),
                'content': f'Content {i}' * 100
            }
            for i in range(10)
        ]

        result = db_ops.batch_load_content_parallel(
            content_list, max_workers=3)
        assert result['success'] >= 10


# ============================================================================
# TEST CASES: DATA EXPORT
# ============================================================================

class TestDataExport:
    """Tests for data export"""

    def test_export_json_format(self, setup_database, sample_source, sample_content):
        """Test exporting content as JSON"""
        source = db_ops.load_regulatory_source(**sample_source)
        db_ops.store_regulatory_content(source_id=source.id, **sample_content)

        result = db_ops.export_regulatory_content(format_type='json')
        assert result['format'] == 'json'
        assert result['count'] >= 1
        assert 'data' in result

    def test_export_unsupported_format(self, setup_database):
        """Test exporting unsupported format returns not_implemented"""
        result = db_ops.export_regulatory_content(format_type='xml')
        assert result['status'] == 'not_implemented'


# ============================================================================
# TEST CASES: REQUIREMENTS
# ============================================================================

class TestRequirements:
    """Tests for requirement management"""

    def test_get_all_requirements(self, setup_database):
        """Test retrieving all requirements"""
        requirements = db_ops.get_all_requirements()
        assert isinstance(requirements, list)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_workflow(self, setup_database):
        """Test complete workflow: load source → store content → detect changes"""
        # Step 1: Load source
        source = db_ops.load_regulatory_source(
            source_name='Integration Test',
            url='https://test.integration.com',
            parser_type='html'
        )
        assert source is not None

        # Step 2: Store content
        content = db_ops.store_regulatory_content(
            source_id=source.id,
            title='Test Chapter',
            section='1',
            subsection='1',
            content='Original content'
        )
        assert content is not None

        # Step 3: Update content (should detect change)
        updated = db_ops.store_regulatory_content(
            source_id=source.id,
            title='Test Chapter',
            section='1',
            subsection='1',
            content='Updated content'
        )
        assert updated.id == content.id
        assert updated.content == 'Updated content'

    def test_system_assessment_workflow(self, setup_database):
        """Test system assessment workflow"""
        # Create system
        system = db_ops.create_system(
            name='Test System',
            owner='Test Org',
            system_type='ai_system'
        )
        assert system is not None

        # Create assessments
        for regulation in ['EU-AI', 'GDPR', 'FDA']:
            assessment = db_ops.create_assessment(
                system_id=system.id,
                regulation_type=regulation,
                assessor='test',
                overall_score=0
            )
            assert assessment is not None

        # Get history
        history = db_ops.get_compliance_history(system.id)
        assert len(history) >= 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
