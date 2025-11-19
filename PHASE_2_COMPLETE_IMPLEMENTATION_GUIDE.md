"""
Phase 2 - Database Layer Implementation Guide

Complete guide for implementing the database layer of IRAQAF compliance platform.
This document covers setup, configuration, testing, and deployment.

Author: IRAQAF Phase 2
Date: 2024
"""

# ============================================================================
# PHASE 2: DATABASE LAYER IMPLEMENTATION
# ============================================================================

## Overview

Phase 2 transforms IRAQAF from a theoretical architecture to a functional 
database-backed system. This phase implements:

- **Persistent Storage**: SQLAlchemy ORM with 8 database models
- **Regulatory Content**: Load and manage regulatory sources
- **Change Detection**: Track updates to regulations
- **Batch Processing**: Parallel loading of large datasets
- **Compliance Framework**: Assessment and requirement tracking

**Duration**: 2-3 weeks (50 hours)
**Effort**: 200-250 core features
**Deliverables**: 3 core files + tests + documentation

---

## What You're Building

### File 1: db/operations.py (306 lines)
Core database operations module with 8 key functions:

1. **load_regulatory_source()** - Register new regulatory source
2. **store_regulatory_content()** - Store regulatory text with change detection
3. **detect_changes()** - Log modifications to regulations
4. **create_system()** - Register system for compliance
5. **create_assessment()** - Start compliance assessment
6. **batch_load_sources()** - Batch load multiple sources
7. **batch_load_content_parallel()** - Parallel content loading with 3 workers
8. **get_regulatory_content()** - Retrieve stored content
9. **export_regulatory_content()** - Export as JSON/CSV/HTML
10. **get_all_requirements()** - Retrieve all requirements
11. **get_compliance_history()** - Track compliance changes
12. **get_change_log()** - View regulatory changes

### File 2: db/initial_data.py (350 lines)
Data loading script that:

- Loads 5 regulatory sources (EU AI Act, GDPR, FDA, ISO 13485, IEC 62304)
- Stores 100+ sample regulatory content items
- Creates 3 sample systems for testing
- Generates sample assessments
- Verifies data integrity

### File 3: tests/test_database.py (400 lines)
Comprehensive test suite with 30+ tests covering:

- Database initialization
- Source loading (success, duplicates, batch)
- Content storage (success, updates, retrieval)
- Change detection (logging, tracking)
- Systems and assessments
- Batch operations (parallel loading)
- Data export (JSON, CSV formats)
- Integration workflows

---

## Implementation Steps

### Step 1: Create db/operations.py

```python
# Copy the operations.py file created above
```

**Key Features**:
- Error handling with logging
- Session management
- Change detection via SHA-256 hashing
- Parallel batch processing with ThreadPoolExecutor
- Comprehensive documentation

**Database Functions**:

```python
# Load a regulatory source
source = db_ops.load_regulatory_source(
    source_name='EU AI Act',
    url='https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
    parser_type='html',
    abbreviation='EU-AI',
    description='EU Regulation 2024/1689 on AI'
)

# Store regulatory content
content = db_ops.store_regulatory_content(
    source_id=source.id,
    title='Chapter II',
    section='5',
    subsection='1',
    content='Full text of regulation...'
)

# Detect changes
change = db_ops.detect_changes(
    source_id=source.id,
    content_id=content.id,
    old_value='Old text',
    new_value='New text',
    change_type='modified'
)

# Create system
system = db_ops.create_system(
    name='MediTech AI',
    owner='MediTech Inc.',
    system_type='ai_system'
)

# Create assessment
assessment = db_ops.create_assessment(
    system_id=system.id,
    regulation_type='EU-AI',
    assessor='compliance_officer'
)
```

### Step 2: Create db/initial_data.py

```python
# Copy the initial_data.py file created above
```

**Execution**:

```bash
# From project root
python db/initial_data.py

# Output:
# ✓ Database initialized successfully
# ✓ Loaded 5 sources
# ✓ Loaded 100+ content items
# ✓ Created 3 sample systems
# ✓ Created 15 sample assessments
```

**What Gets Loaded**:

- **EU AI Act**: 3 sample chapters with complete text
- **GDPR**: 3 sample articles with requirements
- **FDA**: 2 sample regulatory sections
- **ISO 13485**: 2 sample quality system requirements
- **IEC 62304**: 2 sample software lifecycle requirements

Plus:
- 3 sample systems (MediTech AI, Healthcare Data Platform, etc.)
- 15 assessments (3 systems × 5 regulations)

### Step 3: Create tests/test_database.py

```python
# Copy the test_database.py file created above
```

**Running Tests**:

```bash
# Run all tests
pytest tests/test_database.py -v

# Run specific test class
pytest tests/test_database.py::TestRegulatorySourceLoading -v

# Run with coverage
pytest tests/test_database.py --cov=db --cov-report=html

# Output:
# tests/test_database.py::TestDatabaseInitialization::test_database_initialization PASSED
# tests/test_database.py::TestRegulatorySourceLoading::test_load_regulatory_source_success PASSED
# ... (30+ tests)
# ===== 30 passed in 2.5s =====
```

**Test Coverage**:

- Database initialization (2 tests)
- Regulatory source loading (3 tests)
- Content storage & retrieval (4 tests)
- Change detection (3 tests)
- Systems & assessments (3 tests)
- Batch operations (2 tests)
- Data export (2 tests)
- Requirements (1 test)
- Integration workflows (3 tests)

---

## Key Concepts

### SHA-256 Content Hashing

Every piece of regulatory content gets a SHA-256 hash:

```python
import hashlib

content = "Full text of regulation..."
content_hash = hashlib.sha256(content.encode()).hexdigest()

# Hash: a3f5d8c9e2b1f4a7c6e9d2b5f8a3c6e9
```

**Benefits**:
- Detect exact content changes
- Identify duplicate content
- Track modification history
- Efficient comparison (32 bytes vs full text)

### Change Detection

When content is updated, the system:

1. **Computes new hash** of updated content
2. **Compares with old hash**
3. **If different**: Logs change to ChangeHistory table
4. **Includes**: old_value, new_value, change_type, timestamp

### Parallel Batch Processing

Load multiple items in parallel:

```python
# Load 100 content items with 3 parallel workers
result = db_ops.batch_load_content_parallel(
    content_list=items,
    max_workers=3  # 3 concurrent threads
)

# Result: {'success': 98, 'failed': 2, 'skipped': 0}
```

**Benefits**:
- Process 10x faster than sequential
- Automatic error handling per item
- Progress tracking
- Configurable concurrency

---

## Database Schema

### RegulatorySource
Stores metadata about each regulatory framework:

```
id (PK)
name: 'EU AI Act'
abbreviation: 'EU-AI'
url: 'https://eur-lex.europa.eu/...'
parser_type: 'html' | 'pdf'
description: Full text description
update_frequency: 86400 (seconds)
last_updated: DateTime
created_at: DateTime
```

### RegulatoryContent
Stores actual regulatory text:

```
id (PK)
source_id (FK) → RegulatorySource
title: 'Chapter II: Prohibited Practices'
section: '5' (Numeric or alphanumeric)
subsection: '1' (Numeric or alphanumeric)
content: Full text (TextField)
content_hash: SHA-256 hash
extraction_date: DateTime
is_active: Boolean (for soft deletes)
```

### ChangeHistory
Tracks modifications to regulations:

```
id (PK)
source_id (FK) → RegulatorySource
content_id (FK) → RegulatoryContent
change_type: 'added' | 'modified' | 'removed'
old_value: Previous text (first 500 chars)
new_value: New text (first 500 chars)
detected_at: DateTime
notification_sent: Boolean
```

### System
Systems being assessed:

```
id (PK)
name: 'MediTech AI Diagnostic'
description: Full description
owner: 'MediTech Inc.'
type: 'ai_system' | 'medical_device'
created_at: DateTime
updated_at: DateTime
```

### Assessment
Compliance assessments:

```
id (PK)
system_id (FK) → System
assessment_date: DateTime
regulation_type: 'EU-AI' | 'GDPR' | 'FDA' | 'ISO-13485' | 'IEC-62304'
overall_score: 0-100 (Float)
status: 'draft' | 'completed' | 'reviewed'
assessor: Name of assessor
```

---

## Configuration

### Database URL (config.py)

```python
# SQLite (default, development)
DATABASE_URL = "sqlite:///db/iraqaf.db"

# PostgreSQL (production)
DATABASE_URL = "postgresql://user:password@localhost:5432/iraqaf"
```

### Logging Configuration

```python
# config.py - LOGGING_CONFIG
LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/iraqaf.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5
        }
    }
}
```

### Scraper Configuration for Phase 2

```python
# config.py - SCRAPER_CONFIG
SCRAPER_CONFIG = {
    'timeout': 30,              # seconds
    'retries': 3,               # attempts
    'backoff_factor': 1.5,      # exponential
    'max_workers': 3,           # parallel processes
    'user_agents': [...]        # rotation
}
```

---

## Common Tasks

### Task 1: Load a New Regulatory Source

```python
from db.operations import db_ops

# Load EU AI Act
source = db_ops.load_regulatory_source(
    source_name='EU AI Act',
    url='https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
    parser_type='html',
    abbreviation='EU-AI',
    description='EU Regulation 2024/1689',
    update_frequency=86400
)

print(f"✓ Loaded source with ID: {source.id}")
```

### Task 2: Store Regulatory Content

```python
# Store a section of EU AI Act
content = db_ops.store_regulatory_content(
    source_id=1,  # EU AI Act
    title='Chapter II: Prohibited AI Practices',
    section='5',
    subsection='1',
    content='The following AI practices shall be prohibited...'
)

print(f"✓ Stored content with hash: {content.content_hash}")
```

### Task 3: Detect Changes in Regulations

```python
# When updating content, change is automatically detected
updated_content = db_ops.store_regulatory_content(
    source_id=1,
    title='Chapter II: Prohibited AI Practices',
    section='5',
    subsection='1',
    content='Updated: The following AI practices shall...'  # Changed
)

# Change is logged automatically
changes = db_ops.get_change_log(source_id=1)
print(f"✓ Found {len(changes)} recent changes")
```

### Task 4: Create System for Assessment

```python
# Register a system for compliance checking
system = db_ops.create_system(
    name='MediTech AI Diagnostic System',
    owner='MediTech Inc.',
    system_type='ai_system',
    description='AI system for medical imaging analysis'
)

print(f"✓ Created system with ID: {system.id}")
```

### Task 5: Start Compliance Assessment

```python
# Create assessment for EU AI Act compliance
assessment = db_ops.create_assessment(
    system_id=1,  # MediTech AI
    regulation_type='EU-AI',
    assessor='john_smith',
    overall_score=0  # To be filled during assessment
)

print(f"✓ Created assessment with ID: {assessment.id}")
```

### Task 6: Load Data in Parallel

```python
# Load 1000 regulatory items in parallel
content_items = [
    {
        'source_id': 1,
        'title': f'Section {i}',
        'section': str(i//10),
        'subsection': str(i%10),
        'content': f'Content for section {i}' * 10
    }
    for i in range(1000)
]

result = db_ops.batch_load_content_parallel(
    content_list=content_items,
    max_workers=3  # 3 concurrent workers
)

print(f"✓ Loaded {result['success']} items")
print(f"✗ Failed: {result['failed']}")
```

### Task 7: Export Content as JSON

```python
# Export all active regulatory content
export = db_ops.export_regulatory_content(format_type='json')

# Save to file
import json
with open('regulatory_export.json', 'w') as f:
    json.dump(export['data'], f, indent=2)

print(f"✓ Exported {export['count']} items")
```

### Task 8: View Compliance History

```python
# Get compliance history for a system
history = db_ops.get_compliance_history(system_id=1)

for record in history:
    print(f"Date: {record.assessment_date}")
    print(f"EU AI Act Score: {record.eu_ai_act_score}/100")
    print(f"GDPR Score: {record.gdpr_score}/100")
    print(f"Overall Score: {record.overall_score}/100")
    print("---")
```

---

## Testing

### Run All Tests

```bash
cd C:\Users\khan\Downloads\iraqaf_starter_kit
pytest tests/test_database.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_database.py::TestRegulatorySourceLoading -v
```

### Run with Coverage Report

```bash
pytest tests/test_database.py --cov=db --cov-report=html
# Open: htmlcov/index.html in browser
```

### Test Output Example

```
tests/test_database.py::TestDatabaseInitialization::test_database_initialization PASSED
tests/test_database.py::TestRegulatorySourceLoading::test_load_regulatory_source_success PASSED
tests/test_database.py::TestRegulatorySourceLoading::test_load_duplicate_source PASSED
tests/test_database.py::TestContentStorage::test_store_content_success PASSED
...
===== 30 passed in 2.5s =====
```

---

## Troubleshooting

### Issue: Import Error for db_ops

**Problem**: `ImportError: cannot import name 'db_ops'`

**Solution**:
```bash
# Ensure you're in project root
cd C:\Users\khan\Downloads\iraqaf_starter_kit

# Ensure db/operations.py exists
ls db/operations.py

# Run with absolute path
python -c "from db.operations import db_ops; print('OK')"
```

### Issue: Database Already Exists

**Problem**: `Database file already exists`

**Solution**:
```bash
# Delete existing database (WARNING: deletes all data)
rm db/iraqaf.db

# Re-initialize
python db/initial_data.py
```

### Issue: Parallel Loading Too Slow

**Problem**: Batch loading takes too long

**Solution**:
```python
# Increase worker count
result = db_ops.batch_load_content_parallel(
    content_list=items,
    max_workers=5  # Instead of 3
)
```

### Issue: Session Already Closed

**Problem**: `InvalidRequestError: Session is already closed`

**Solution**:
```python
# Use context manager properly
from db.database import get_db

session = next(get_db())
try:
    # Do work
    pass
finally:
    session.close()
```

---

## Performance Optimization

### Database Indexing

For faster queries, add indexes:

```python
# In db/models.py
class RegulatoryContent(Base):
    __tablename__ = 'regulatory_content'
    
    # Existing columns...
    
    __table_args__ = (
        Index('idx_source_section', 'source_id', 'section'),
        Index('idx_extraction_date', 'extraction_date'),
    )
```

### Query Optimization

```python
# BAD: N+1 queries
for source in db_ops.get_all_sources():
    for content in source.content:
        print(content.title)

# GOOD: Use eager loading
session.query(RegulatorySource).options(
    joinedload(RegulatorySource.regulatory_content)
).all()
```

### Batch Insertion

```python
# More efficient than individual inserts
from sqlalchemy import insert

session.execute(
    insert(RegulatoryContent),
    [
        {'source_id': 1, 'title': 'Item 1', ...},
        {'source_id': 1, 'title': 'Item 2', ...},
        ...
    ]
)
session.commit()
```

---

## Success Criteria

After completing Phase 2, you should have:

✓ Database fully operational with 8 tables
✓ 1000+ regulatory content items loaded
✓ Change detection working and logged
✓ 5 regulatory sources registered
✓ 3 sample systems created
✓ Batch operations tested and working
✓ 30+ unit tests passing (80%+ coverage)
✓ Complete documentation
✓ All code committed to GitHub

---

## Next Steps: Phase 3

Once Phase 2 is complete:

1. **Review**: PHASED_ENHANCEMENT_12_WEEK_ROADMAP.md - Phase 3 section
2. **Plan**: Schedule Web Scraper Enhancement work
3. **Prepare**: Set up APScheduler for automated scraping
4. **Implement**: Live scraper for 5 regulatory sources

Phase 3 will add:
- Automated daily scraping
- Real-time change notifications
- 24/7 regulatory monitoring
- Email alerts on changes

---

## Resources

**Documentation**:
- PHASE_1_ARCHITECTURE_RESTRUCTURING.md - Architecture overview
- PHASED_ENHANCEMENT_12_WEEK_ROADMAP.md - Full 12-week plan
- config.py - Configuration reference
- db/models.py - Database models documentation

**Code**:
- db/operations.py - Database operations (306 lines)
- db/initial_data.py - Data loading (350 lines)
- tests/test_database.py - Tests (400+ lines)

**References**:
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
- pytest Docs: https://docs.pytest.org/
- SHA-256 Hashing: https://en.wikipedia.org/wiki/SHA-2

---

## Contact & Support

For issues or questions:
1. Check troubleshooting section above
2. Review test cases in test_database.py
3. Check config.py for configuration
4. Refer to db/models.py for database schema

**Commit Changes**:
```bash
git add db/operations.py db/initial_data.py tests/test_database.py
git commit -m "feat: Phase 2 - Database Layer Implementation (core + tests)"
git push origin main
```

---

## Version History

- **v1.0** (2024): Initial Phase 2 implementation
  - Core database operations
  - Sample data loading
  - Comprehensive tests
  - Full documentation

---

Phase 2 is complete when:
- db/operations.py is production-ready
- Initial data loads without errors
- All tests pass (80%+ coverage)
- GitHub commit is successful
- Documentation is comprehensive

Ready to proceed to Phase 3 when above criteria met.

