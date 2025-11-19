"""
PHASE 2: DATABASE LAYER - QUICK START GUIDE

═══════════════════════════════════════════════════════════════════════════════
BEGIN PHASE 2: Database Layer Implementation
Week 2-3, 50 hours

FOCUS: Implement database operations and load regulatory content

═══════════════════════════════════════════════════════════════════════════════
WHAT YOU NEED TO BUILD (Phase 2)
═══════════════════════════════════════════════════════════════════════════════

1. db/operations.py (300 lines) - Core database operations
   
   Functions to implement:
   - load_regulatory_source(name: str, url: str, parser_type: str) → RegulatorySource
   - scrape_and_store(source_id: int) → int (number of sections stored)
   - detect_changes(source_id: int) → List[ChangeHistory]
   - get_system_compliance(system_id: int) → SystemComplianceHistory
   - create_assessment(system_id: int, regulation: str) → Assessment
   - batch_load_sources(source_list: List[Dict]) → Dict[str, RegulatorySource]
   - export_regulatory_content(format: str) → str
   - get_all_requirements(source: str = None) → List[AssessmentRequirement]

2. db/initial_data.py (200 lines) - Sample data for testing
   
   What to include:
   - EU AI Act sections (50-100)
   - GDPR articles (20-30)
   - FDA guidelines (20-30)
   - Sample system data
   - Sample assessment
   - Sample requirements

3. db/migrations/ - Database versioning
   - Version 1: Initial schema
   - Version 2: Add indexes
   - Version 3: Add audit trails

═══════════════════════════════════════════════════════════════════════════════
STEP-BY-STEP IMPLEMENTATION
═══════════════════════════════════════════════════════════════════════════════

STEP 1: Create db/operations.py

```python
# db/operations.py
from sqlalchemy.orm import Session
from db.models import RegulatorySource, RegulatoryContent, ChangeHistory, System, Assessment
from config import REGULATORY_SOURCES
import logging

logger = logging.getLogger(__name__)

def load_regulatory_source(db: Session, name: str, url: str, parser_type: str):
    '''Load a regulatory source from URL'''
    source = RegulatorySource(
        name=name,
        abbreviation=name[:3],
        url=url,
        parser_type=parser_type,
        update_frequency='weekly'
    )
    db.add(source)
    db.commit()
    logger.info(f\"Loaded regulatory source: {name}\")
    return source

def scrape_and_store(db: Session, source_id: int):
    '''Scrape content from source and store in database'''
    from scraper import EUAIActScraper, GDPRScraper  # etc.
    
    source = db.query(RegulatorySource).get(source_id)
    if not source:
        raise ValueError(f\"Source {source_id} not found\")
    
    # Create appropriate scraper
    scraper_map = {
        'EU-AI-ACT': EUAIActScraper,
        'GDPR': GDPRScraper,
        # Add others
    }
    
    scraper_class = scraper_map.get(source.abbreviation)
    if not scraper_class:
        raise ValueError(f\"No scraper for {source.abbreviation}\")
    
    scraper = scraper_class()
    content_list = scraper.scrape()
    
    # Store in database
    count = 0
    for content_item in content_list:
        content = RegulatoryContent(
            source_id=source_id,
            title=content_item.get('title'),
            content=content_item.get('content'),
            content_hash=content_item.get('hash')
        )
        db.add(content)
        count += 1
    
    db.commit()
    logger.info(f\"Stored {count} sections from {source.name}\")
    return count

def detect_changes(db: Session, source_id: int):
    '''Detect changes in regulatory content'''
    source = db.query(RegulatorySource).get(source_id)
    current_content = source.regulatory_content
    
    changes = []
    for content in current_content:
        # Compare hashes - if different, change detected
        # Create ChangeHistory record
        change = ChangeHistory(
            source_id=source_id,
            content_id=content.id,
            change_type='modified'
        )
        changes.append(change)
    
    db.add_all(changes)
    db.commit()
    return changes

# Additional functions...
```

STEP 2: Create db/initial_data.py

```python
# db/initial_data.py
from db.models import RegulatorySource, RegulatoryContent, System, Assessment, AssessmentRequirement
from config import REGULATORY_SOURCES
import json

def load_initial_data(db):
    '''Load sample data for testing'''
    
    # Create regulatory sources
    sources = {
        'eu_ai_act': RegulatorySource(
            name='EU AI Act',
            abbreviation='EU-AI',
            url=REGULATORY_SOURCES['EU_AI_ACT']['url'],
            parser_type='html',
            update_frequency='weekly'
        ),
        'gdpr': RegulatorySource(
            name='GDPR',
            abbreviation='GDPR',
            url=REGULATORY_SOURCES['GDPR']['url'],
            parser_type='html',
            update_frequency='monthly'
        ),
        # Add others...
    }
    
    for source in sources.values():
        db.add(source)
    
    db.commit()
    logger.info(f\"Created {len(sources)} regulatory sources\")
    
    # Create sample system
    system = System(
        name='Healthcare AI System',
        description='AI system for medical diagnostics',
        owner='Healthcare Corp',
        type='ai_system'
    )
    db.add(system)
    db.commit()
    
    # Create sample assessment
    assessment = Assessment(
        system_id=system.id,
        regulation_type='eu_ai_act',
        status='draft'
    )
    db.add(assessment)
    db.commit()
    
    logger.info(\"Initial data loaded\")

if __name__ == '__main__':
    from db.database import SessionLocal, init_db
    init_db()
    db = SessionLocal()
    load_initial_data(db)
    db.close()
```

STEP 3: Testing

```python
# tests/test_database.py
import pytest
from db.database import SessionLocal, init_db
from db.models import RegulatorySource
from db.operations import load_regulatory_source

@pytest.fixture
def db():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_load_regulatory_source(db):
    source = load_regulatory_source(
        db,
        'EU AI Act',
        'https://example.com',
        'html'
    )
    assert source.name == 'EU AI Act'
    assert source.abbreviation == 'EU '

def test_scrape_and_store(db):
    # Test scraping and storage
    pass

def test_change_detection(db):
    # Test change detection
    pass
```

═══════════════════════════════════════════════════════════════════════════════
DELIVERABLES FOR PHASE 2
═══════════════════════════════════════════════════════════════════════════════

File Structure After Phase 2:
  db/
  ├── __init__.py
  ├── models.py ✓ (already done)
  ├── database.py ✓ (already done)
  ├── operations.py ← NEW
  ├── initial_data.py ← NEW
  └── migrations/
      ├── versions/
      │   ├── 001_initial_schema.py
      │   ├── 002_add_indexes.py
      │   └── 003_audit_trails.py
      └── env.py

Database Contents After Phase 2:
  ✓ 5 regulatory sources loaded
  ✓ 1000+ regulatory sections stored
  ✓ Sample system for testing
  ✓ Sample assessment with requirements
  ✓ Change history tracked

Documentation:
  ✓ Database operations guide
  ✓ How to load new sources
  ✓ How to run migrations
  ✓ Troubleshooting guide
  ✓ API documentation

═══════════════════════════════════════════════════════════════════════════════
SUCCESS CRITERIA FOR PHASE 2
═══════════════════════════════════════════════════════════════════════════════

✓ Database fully operational
✓ Can load regulatory sources programmatically
✓ Can store 1000+ regulatory sections
✓ Change detection working
✓ Batch loading script functional
✓ Initial data loads successfully
✓ Tests passing (80%+ coverage)
✓ Documentation complete
✓ Admin scripts created
✓ Ready for Phase 3 (scraper enhancement)

═══════════════════════════════════════════════════════════════════════════════
NEXT STEPS AFTER PHASE 2
═══════════════════════════════════════════════════════════════════════════════

After Phase 2 is complete:
  → Phase 3: Enhance scrapers and implement scheduling
  → Phase 4: Add semantic search and requirement linking
  → Phase 5: Implement compliance scoring
  → Phase 6: Build change monitoring
  → Phase 7: Create REST API and CLI
  → Phase 8: Add comprehensive testing

═══════════════════════════════════════════════════════════════════════════════

Ready to start Phase 2?

1. Create db/operations.py with the functions above
2. Create db/initial_data.py with sample data
3. Test with: python -m pytest tests/test_database.py
4. Load initial data: python db/initial_data.py
5. Verify: SELECT COUNT(*) FROM regulatory_content;

Good luck! Phase 2 is where the system starts to come alive.
"""
