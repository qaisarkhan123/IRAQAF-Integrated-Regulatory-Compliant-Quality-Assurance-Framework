"""
PHASE 1: ARCHITECTURE RESTRUCTURING GUIDE

This document outlines the completion of Phase 1 of the IRAQAF Phased Enhancement roadmap.
Phase 1 establishes the modular architecture foundation for all subsequent phases.

TIMELINE: Week 1-2 (40 hours)
STATUS: ✓ COMPLETE

═══════════════════════════════════════════════════════════════════════════════
DIRECTORY STRUCTURE CREATED
═══════════════════════════════════════════════════════════════════════════════

iraqaf_starter_kit/
├── config.py                          # Centralized configuration
├── main.py                            # Phase 1 initialization script
├── requirements.txt                   # All dependencies (9 new libraries)
│
├── db/                                # Database Layer
│   ├── __init__.py
│   ├── models.py                      # 8 SQLAlchemy ORM models
│   └── database.py                    # Session management
│
├── scraper/                           # Web Scraping Module
│   ├── base_scraper.py                # BaseScraper class with retry logic
│   └── scrapers.py                    # EU AI Act, GDPR, ISO 13485, etc.
│
├── nlp_pipeline/                      # NLP Processing Pipeline
│   └── document_processor.py           # Text extraction & semantic analysis
│
├── compliance/                        # Compliance Scoring (Phase 3)
│   └── [To be implemented]
│
├── monitoring/                        # Change Monitoring (Phase 4)
│   └── [To be implemented]
│
├── api_or_cli/                        # API & CLI (Phase 5)
│   └── [To be implemented]
│
└── tests/                             # Testing (Phase 6)
    └── [To be implemented]

═══════════════════════════════════════════════════════════════════════════════
FILES CREATED & THEIR PURPOSE
═══════════════════════════════════════════════════════════════════════════════

1. CONFIG.PY (Centralized Configuration)
   - Database URL and connection settings
   - Scraper configuration (timeouts, retries, user agents)
   - NLP model selection and parameters
   - Regulatory sources registry (URLS, parsers, update frequency)
   - Logging configuration
   - API and monitoring settings

2. DB/MODELS.PY (8 SQLAlchemy ORM Models)
   
   a) RegulatorySource
      - Stores EU AI Act, GDPR, ISO 13485, IEC 62304, FDA
      - Fields: name, abbreviation, description, URL, parser_type, update_frequency
      - Relationships: regulatory_content, change_history
   
   b) RegulatoryContent
      - Parsed regulatory document sections
      - Fields: title, section, subsection, content, content_hash
      - Used for semantic search and requirement matching
   
   c) ChangeHistory
      - Tracks detected changes in regulatory documents
      - Fields: change_type (added/modified/removed), old_value, new_value
      - Used by monitoring system
   
   d) System
      - Represents system under assessment
      - Fields: name, description, owner, type (ai_system/medical_device)
      - Root entity for compliance tracking
   
   e) SystemComplianceHistory
      - Compliance scores over time per system
      - Fields: Scores for EU AI Act, GDPR, ISO 13485, IEC 62304, FDA
      - Enables trend analysis and historical tracking
   
   f) Document
      - Uploaded/ingested documents (PDF, DOCX, TXT, HTML)
      - Fields: filename, content_type, extracted_text, parsed_sections
      - SHA-256 hashing for change detection
   
   g) Assessment
      - Compliance assessment for a system against one regulation
      - Fields: assessment_date, regulation_type, overall_score, status
      - Link between system and individual requirement assessments
   
   h) AssessmentRequirement
      - Individual requirement within an assessment
      - Fields: requirement_id (e.g., "EU-AI-41.1"), status, score, evidence, gaps, recommendations
      - Granular compliance tracking at requirement level

3. DB/DATABASE.PY (Session Management)
   - SQLAlchemy engine setup
   - Session factory (SessionLocal)
   - init_db() function to create tables
   - get_db() generator for dependency injection

4. SCRAPER/BASE_SCRAPER.PY (Abstract Scraper Base Class)
   
   Features:
   - HTTPScraper: Handles HTTP requests with retry/backoff logic
   - fetch_content(): Implements exponential backoff retry (3 attempts, 1.5x factor)
   - compute_hash(): SHA-256 hashing for change detection
   - Abstract methods: parse_html() and parse_pdf()
   - Session management with proper headers
   - Comprehensive error handling and logging
   
   Retry Logic:
   - Timeout: Up to 3 attempts with exponential backoff
   - Connection Error: Same retry policy
   - HTTP 4xx/5xx: Logged and raised for handling

5. SCRAPER/SCRAPERS.PY (Specific Scrapers)
   - EUAIActScraper: For EU AI Act regulations
   - GDPRScraper: For GDPR text
   - ISO13485Scraper: For ISO 13485 medical device standards
   - IEC62304Scraper: For IEC 62304 software standards
   - FDAScraper: For FDA medical device regulations

6. NLP_PIPELINE/DOCUMENT_PROCESSOR.PY (NLP Pipeline)
   
   Features:
   - extract_text(): Supports PDF, DOCX, TXT, HTML extraction
   - chunk_text(): Overlapping text chunks for processing (512 tokens, 50 token overlap)
   - extract_entities(): Named entity recognition + requirement extraction
   - compute_semantic_similarity(): TF-IDF + cosine similarity
   - find_relevant_clauses(): Match requirements to regulatory clauses
   
   Models:
   - spaCy: For tokenization and NER
   - NLTK: For sentence tokenization
   - scikit-learn: TF-IDF and cosine similarity
   
   Semantic Matching:
   - TF-IDF vectorization with 1000 max features
   - Cosine similarity threshold: 0.7 (70%)
   - Returns relevant clauses ranked by similarity score

7. MAIN.PY (Phase 1 Initialization)
   - Initializes database schema
   - Verifies all module imports
   - Checks dependencies
   - Ready for Phase 2 database operations

═══════════════════════════════════════════════════════════════════════════════
DEPENDENCIES INSTALLED (requirements.txt)
═══════════════════════════════════════════════════════════════════════════════

Web Scraping:
  ✓ requests==2.31.0
  ✓ beautifulsoup4==4.12.2

NLP Processing:
  ✓ spacy==3.7.2
  ✓ nltk==3.8.1

Machine Learning:
  ✓ scikit-learn==1.3.2

PDF/Document Processing:
  ✓ PyPDF2==4.0.1
  ✓ pdfplumber==0.10.3
  ✓ python-docx==0.8.11

Database & ORM:
  ✓ SQLAlchemy==2.0.23

Task Scheduling:
  ✓ APScheduler==3.10.4

Web Framework:
  ✓ Flask==3.0.0
  ✓ Flask-SQLAlchemy==3.1.1
  ✓ Flask-RESTful==0.3.10

Data & Visualization:
  ✓ pandas==2.1.3
  ✓ numpy==1.26.2
  ✓ matplotlib==3.8.2
  ✓ plotly==5.18.0

Dashboard:
  ✓ streamlit==1.29.0
  ✓ Pillow==10.1.0

Testing:
  ✓ pytest==7.4.3
  ✓ pytest-cov==4.1.0

Utilities:
  ✓ python-dotenv==1.0.0
  ✓ python-dateutil==2.8.2

═══════════════════════════════════════════════════════════════════════════════
HOW TO USE PHASE 1 OUTPUT
═══════════════════════════════════════════════════════════════════════════════

1. Install Dependencies:
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm

2. Initialize System:
   python main.py

3. Verify Database:
   - File: db/iraqaf.db (SQLite)
   - Tables: 8 tables created with proper relationships

4. Test Imports:
   python -c "from scraper.scrapers import EUAIActScraper; print('✓ Scrapers loaded')"
   python -c "from nlp_pipeline.document_processor import DocumentProcessor; print('✓ NLP loaded')"

═══════════════════════════════════════════════════════════════════════════════
READY FOR PHASE 2
═══════════════════════════════════════════════════════════════════════════════

Phase 1 establishes the architectural foundation. All subsequent phases build on this:

NEXT STEPS (Phase 2 - Week 2-3, 50 hours):
  → Database Layer Implementation
  → Add regulatory source loading
  → Implement change detection
  → Setup batch operations

The modular structure means:
  ✓ Each module is independently testable
  ✓ Scrapers can be developed in parallel
  ✓ NLP pipeline scales independently
  ✓ Database can be swapped (SQLite → PostgreSQL)
  ✓ API layer will use these modules cleanly

═══════════════════════════════════════════════════════════════════════════════
ARCHITECTURE PRINCIPLES
═══════════════════════════════════════════════════════════════════════════════

Separation of Concerns:
  - db/: Data layer only
  - scraper/: Web scraping only
  - nlp_pipeline/: Text processing only
  - compliance/: Business logic
  - monitoring/: Notifications
  - api_or_cli/: Interface layer

Clean Dependencies:
  - config.py → All modules depend on this
  - models.py → Database models isolated
  - base_scraper.py → All scrapers inherit from this
  - document_processor.py → All NLP tasks use this

Testing Ready:
  - Each module has clear boundaries
  - Mocking is straightforward
  - Unit tests can be written independently

Scalability:
  - Database: Can scale to PostgreSQL
  - Scrapers: Can add parallel execution
  - NLP: Can add GPU support later
  - API: Can add caching layer

═══════════════════════════════════════════════════════════════════════════════
PHASE 1 COMPLETE ✓
═══════════════════════════════════════════════════════════════════════════════

Architecture is established and ready for Phase 2 database operations.
Total effort: 40 hours across 2 weeks.
Next milestone: Database layer with regulatory content loading.
"""

PHASE_1_GUIDE = __doc__
