# IRAQAF MODULE 1 - FULL SPECIFICATION COMPLIANCE ROADMAP

**Objective**: Transform from 10% to 100% specification compliance

**Current State**: MVP-level Flask app (883 lines, excellent UI, minimal backend)

**Target State**: Enterprise-grade modular system with all 4 components, database, scheduling, testing

**Estimated Effort**: 300-400 development hours

---

## PHASE 1: FOUNDATION & ARCHITECTURE (Week 1-2, ~40 hours)

### 1.1 Restructure Project Layout

**Create Directory Structure**:
```
iraqaf_starter_kit/
├── requirements.txt                    # All 9+ dependencies
├── setup.py                           # Package setup
├── main.py                            # Entry point
├── config.py                          # Configuration
│
├── scraper/
│   ├── __init__.py
│   ├── base.py                       # BaseScraper class
│   ├── eu_ai_act.py                 # EU AI Act scraper
│   ├── gdpr.py                       # GDPR scraper
│   ├── iso_13485.py                 # ISO scraper
│   ├── iec_62304.py                 # IEC scraper
│   ├── fda.py                       # FDA scraper
│   └── utils.py                     # Helper functions
│
├── nlp/
│   ├── __init__.py
│   ├── ingestion.py                 # Document parsing (PDF, DOCX)
│   ├── pipeline.py                  # NLP preprocessing
│   ├── keywords.py                  # Keyword dictionaries
│   ├── clause_detector.py           # Clause reference detection
│   ├── similarity.py                # TF-IDF & cosine similarity
│   └── classifier.py                # Document type classification
│
├── compliance/
│   ├── __init__.py
│   ├── checklists.py                # Requirement data (JSON-backed)
│   ├── scorer.py                    # Scoring logic
│   ├── gap_analysis.py              # Gap categorization
│   └── crs_calculator.py            # CRS weighted calculation
│
├── monitoring/
│   ├── __init__.py
│   ├── scheduler.py                 # APScheduler setup
│   ├── change_detector.py           # SHA-256 hashing
│   ├── notifications.py             # Email service
│   └── alert_manager.py             # Alert logic
│
├── db/
│   ├── __init__.py
│   ├── models.py                    # SQLAlchemy models (8 tables)
│   ├── session.py                   # DB session management
│   └── migrations.py                # Alembic migrations
│
├── api_or_cli/
│   ├── __init__.py
│   ├── cli.py                       # CLI commands
│   ├── routes.py                    # FastAPI/Flask routes
│   └── schemas.py                   # Pydantic schemas (request/response)
│
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py              # Scraper tests
│   ├── test_nlp.py                  # NLP tests
│   ├── test_scoring.py              # Scoring tests
│   ├── test_api.py                  # API tests
│   ├── fixtures.py                  # Test data
│   └── integration_test.py           # End-to-end
│
├── dashboard/                        # Keep existing Flask UI
│   ├── app.py                       # Main dashboard
│   ├── privacy_security_hub.py
│   ├── hub_explainability_app.py
│   └── l1_regulations_governance_hub.py  # Existing (refactor later)
│
└── data/                            # Sample data
    ├── sample_documents/
    ├── mock_html/
    └── expected_outputs/
```

### 1.2 Dependencies (requirements.txt)

```
# Core
python>=3.8
flask==2.3.0
fastapi==0.95.0
uvicorn==0.21.0

# Web Scraping
requests==2.31.0
beautifulsoup4==4.12.0

# NLP
spacy==3.5.0
nltk==3.8.0
scikit-learn==1.2.0

# Document Parsing
PyPDF2==3.0.0
pdfplumber==0.9.0
python-docx==0.8.11

# Database
SQLAlchemy==2.0.0
alembic==1.10.0
sqlite3  # built-in

# Scheduling
APScheduler==3.10.0

# Utilities
python-dotenv==1.0.0
pydantic==1.10.0
pytest==7.3.0
pytest-cov==4.1.0

# Logging & Monitoring
python-json-logger==2.0.0
```

### 1.3 Configuration Module (config.py)

```python
# Database
DATABASE_URL = "sqlite:///./iraqaf.db"  # Switch to PostgreSQL later
SQLALCHEMY_ECHO = False

# Scraping
SCRAPER_TIMEOUT = 30
SCRAPER_MAX_RETRIES = 3
SCRAPER_BACKOFF_FACTOR = 1.5
SCRAPER_DELAY = 1.0  # Seconds between requests

# Scheduling
SCHEDULE_EU_AI_ACT = "0 */6 * * *"  # Every 6 hours
SCHEDULE_GDPR = "0 0 * * 0"  # Weekly, Monday
SCHEDULE_ISO_IEC = "0 0 1 * *"  # Monthly, 1st day

# Email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "${SMTP_USERNAME}"
SMTP_PASSWORD = "${SMTP_PASSWORD}"

# NLP
TF_IDF_MAX_FEATURES = 5000
TF_IDF_NGRAM_RANGE = (1, 3)
SIMILARITY_THRESHOLD = 0.65

# Scoring
SCORE_WEIGHTS = {
    "GDPR": 0.25,
    "EU_AI_ACT": 0.35,
    "ISO_13485": 0.25,
    "IEC_62304": 0.10,
    "FDA": 0.05
}
```

### 1.4 Main Entry Point (main.py)

```python
#!/usr/bin/env python3
"""IRAQAF Module 1 - Main Entry Point"""

import sys
from scraper import run_all_scrapers, detect_changes
from nlp import analyze_documents
from compliance import assess_system
from monitoring import start_scheduler
from api_or_cli import create_app, run_cli

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        run_cli(sys.argv[1:])
    else:
        # API mode
        app = create_app()
        app.run(host="0.0.0.0", port=8000)
```

---

## PHASE 2: DATABASE LAYER (Week 2-3, ~50 hours)

### 2.1 SQLAlchemy Models (db/models.py)

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RegulatorySource(Base):
    """Represents a regulatory source (EU AI Act, GDPR, etc)"""
    __tablename__ = "regulatory_sources"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)  # "EU AI Act", "GDPR", etc
    url = Column(String(500))
    category = Column(String(50))  # GDPR, EU_AI, ISO, IEC, FDA
    last_scraped = Column(DateTime, nullable=True)
    last_hash = Column(String(64), nullable=True)  # SHA-256 of last content
    status = Column(String(20), default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)

class RegulatoryContent(Base):
    """Stores actual regulatory content (articles, clauses, etc)"""
    __tablename__ = "regulatory_content"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("regulatory_sources.id"))
    section = Column(String(100))  # "Article 6", "Annex IV", etc
    subsection = Column(String(100), nullable=True)
    content = Column(Text)  # Full text of the section
    content_hash = Column(String(64))  # SHA-256 hash
    version = Column(Integer, default=1)
    effective_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChangeHistory(Base):
    """Tracks changes to regulatory content"""
    __tablename__ = "change_history"
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("regulatory_sources.id"))
    old_hash = Column(String(64))
    new_hash = Column(String(64))
    change_type = Column(String(20))  # critical, major, minor
    description = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)
    impact_score = Column(Float)  # 0-1

class System(Base):
    """Represents a system being assessed"""
    __tablename__ = "systems"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(Text, nullable=True)
    contact_email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemComplianceHistory(Base):
    """Stores historical compliance assessments per system"""
    __tablename__ = "system_compliance_history"
    
    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("systems.id"))
    assessment_date = Column(DateTime, default=datetime.utcnow)
    crs_score = Column(Float)  # 0-100
    per_regulation_scores = Column(JSON)  # {GDPR: 85, EU_AI: 90, ...}
    gaps_found = Column(Integer)

class Document(Base):
    """Uploaded documents for analysis"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("systems.id"))
    filename = Column(String(200))
    content_hash = Column(String(64))
    doc_type = Column(String(50))  # DPIA, Risk Management File, Quality Manual
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class Assessment(Base):
    """Individual compliance assessments"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("systems.id"))
    crs_score = Column(Float)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class AssessmentRequirement(Base):
    """Individual requirement scores within an assessment"""
    __tablename__ = "assessment_requirements"
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    requirement_id = Column(String(100))  # "GDPR_1", "EU_AI_25", etc
    score = Column(Float)  # 0-1
    evidence = Column(Text, nullable=True)
```

### 2.2 Database Session Management (db/session.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database schema"""
    Base.metadata.create_all(bind=engine)
```

---

## PHASE 3: WEB SCRAPER (Week 3-5, ~60 hours)

### 3.1 Base Scraper Class (scraper/base.py)

```python
import requests
import time
import logging
from requests.adapters import HTTPAdapter
from urllib.robotparser import RobotFileParser
import hashlib

class BaseScraper:
    """Base class for regulatory scrapers with retry logic & robots.txt respect"""
    
    def __init__(self, name, url, category, timeout=30, max_retries=3, delay=1.0):
        self.name = name
        self.url = url
        self.category = category
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = self._create_session()
    
    def _create_session(self):
        """Create requests session with retry strategy"""
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=3)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": "IRAQAF-Scraper/1.0 (Compliance Analysis)"
        })
        return session
    
    def _check_robots_txt(self, url):
        """Check robots.txt before scraping"""
        try:
            rp = RobotFileParser()
            rp.set_url(url.replace("/api/", "/").rstrip("/") + "/robots.txt")
            rp.read()
            return rp.can_fetch(self.session.headers["User-Agent"], url)
        except Exception as e:
            self.logger.warning(f"Could not check robots.txt: {e}")
            return True  # Proceed if robots.txt unavailable
    
    def fetch(self, url, **kwargs):
        """Fetch URL with retries and backoff"""
        if not self._check_robots_txt(url):
            self.logger.warning(f"robots.txt forbids scraping {url}")
            return None
        
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                backoff = 1.5 ** attempt
                self.logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {backoff}s")
                time.sleep(backoff)
        
        self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    @staticmethod
    def compute_hash(content):
        """Compute SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def scrape(self):
        """To be implemented by subclasses"""
        raise NotImplementedError
    
    def parse_content(self, html):
        """To be implemented by subclasses"""
        raise NotImplementedError
```

### 3.2 EU AI Act Scraper (scraper/eu_ai_act.py)

```python
from bs4 import BeautifulSoup
from .base import BaseScraper
from db.models import RegulatorySource, RegulatoryContent, ChangeHistory
from db.session import SessionLocal

class EUAIActScraper(BaseScraper):
    """Scrapes EU AI Act from EUR-Lex"""
    
    def __init__(self):
        super().__init__(
            name="EU AI Act",
            url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024L1689",
            category="EU_AI"
        )
    
    def scrape(self):
        """Scrape EU AI Act articles and annexes"""
        response = self.fetch(self.url)
        if not response:
            return None
        
        content = self.parse_content(response.text)
        return self.store_content(content)
    
    def parse_content(self, html):
        """Parse HTML into structured sections"""
        soup = BeautifulSoup(html, "html.parser")
        sections = {}
        
        # Extract Articles 6, 9, 13, 14, 52
        target_articles = [6, 9, 13, 14, 52]
        
        for article_num in target_articles:
            article_text = self._extract_article(soup, article_num)
            if article_text:
                sections[f"Article {article_num}"] = article_text
        
        # Extract Annexes IV, VI, VII, VIII
        for annex in ["IV", "VI", "VII", "VIII"]:
            annex_text = self._extract_annex(soup, annex)
            if annex_text:
                sections[f"Annex {annex}"] = annex_text
        
        return sections
    
    def _extract_article(self, soup, article_num):
        """Extract specific article from HTML"""
        # Implementation depends on EUR-Lex HTML structure
        # Typically: find heading with "Article N", then all content until next Article
        pattern = f"Article {article_num}"
        # ... actual parsing logic
        return None
    
    def _extract_annex(self, soup, annex):
        """Extract specific annex"""
        # ... implementation
        return None
    
    def store_content(self, sections):
        """Store parsed content in database"""
        db = SessionLocal()
        try:
            # Get or create source
            source = db.query(RegulatorySource).filter_by(name="EU AI Act").first()
            if not source:
                source = RegulatorySource(
                    name="EU AI Act",
                    url=self.url,
                    category="EU_AI",
                    status="active"
                )
                db.add(source)
                db.flush()
            
            # Store each section
            for section_name, content_text in sections.items():
                content_hash = self.compute_hash(content_text)
                
                # Check for changes
                existing = db.query(RegulatoryContent).filter_by(
                    source_id=source.id,
                    section=section_name
                ).first()
                
                if existing and existing.content_hash != content_hash:
                    # Record change
                    change = ChangeHistory(
                        source_id=source.id,
                        old_hash=existing.content_hash,
                        new_hash=content_hash,
                        change_type=self._classify_change(existing.content, content_text),
                        description=f"Update to {section_name}",
                        impact_score=0.8
                    )
                    db.add(change)
                    existing.content = content_text
                    existing.content_hash = content_hash
                    existing.version += 1
                elif not existing:
                    # New section
                    reg_content = RegulatoryContent(
                        source_id=source.id,
                        section=section_name,
                        content=content_text,
                        content_hash=content_hash,
                        effective_date=datetime.utcnow()
                    )
                    db.add(reg_content)
            
            db.commit()
            return True
        finally:
            db.close()
    
    def _classify_change(self, old_content, new_content):
        """Classify change as critical, major, or minor"""
        # Simple heuristic: length difference
        if abs(len(new_content) - len(old_content)) / max(len(old_content), 1) > 0.3:
            return "critical"
        elif abs(len(new_content) - len(old_content)) / max(len(old_content), 1) > 0.1:
            return "major"
        else:
            return "minor"
```

### 3.3 Scraper Runner (scraper/__init__.py)

```python
from .eu_ai_act import EUAIActScraper
from .gdpr import GDPRScraper
from .iso_13485 import ISO13485Scraper
from .iec_62304 import IEC62304Scraper
from .fda import FDAScraper

def run_all_scrapers():
    """Run all scrapers"""
    scrapers = [
        EUAIActScraper(),
        GDPRScraper(),
        ISO13485Scraper(),
        IEC62304Scraper(),
        FDAScraper()
    ]
    
    for scraper in scrapers:
        try:
            scraper.scrape()
            print(f"✅ {scraper.name} scraped successfully")
        except Exception as e:
            print(f"❌ {scraper.name} failed: {e}")
```

---

## PHASE 4: NLP PIPELINE (Week 5-7, ~80 hours)

### 4.1 Document Ingestion (nlp/ingestion.py)

```python
import PyPDF2
import pdfplumber
from docx import Document as DocxDocument
from pathlib import Path
from typing import List, Dict

class DocumentIngestion:
    """Handle PDF, DOCX, TXT, MD document parsing"""
    
    @staticmethod
    def ingest(file_path: str) -> Dict:
        """Ingest any supported document format"""
        path = Path(file_path)
        
        if path.suffix.lower() == ".pdf":
            return DocumentIngestion.ingest_pdf(file_path)
        elif path.suffix.lower() == ".docx":
            return DocumentIngestion.ingest_docx(file_path)
        elif path.suffix.lower() in [".txt", ".md"]:
            return DocumentIngestion.ingest_text(file_path)
        else:
            raise ValueError(f"Unsupported format: {path.suffix}")
    
    @staticmethod
    def ingest_pdf(file_path: str) -> Dict:
        """Parse PDF with page tracking"""
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    pages.append({
                        "page": page_num,
                        "content": text,
                        "metadata": page.metadata
                    })
        except Exception as e:
            raise Exception(f"PDF parsing failed: {e}")
        
        return {
            "filename": Path(file_path).name,
            "format": "pdf",
            "total_pages": len(pages),
            "pages": pages,
            "full_text": "\n".join(p["content"] for p in pages)
        }
    
    @staticmethod
    def ingest_docx(file_path: str) -> Dict:
        """Parse DOCX with heading tracking"""
        doc = DocxDocument(file_path)
        content = []
        
        for para in doc.paragraphs:
            content.append({
                "text": para.text,
                "style": para.style.name,
                "level": para.paragraph_format.outline_level
            })
        
        return {
            "filename": Path(file_path).name,
            "format": "docx",
            "sections": len(doc.sections),
            "paragraphs": content,
            "full_text": "\n".join(c["text"] for c in content)
        }
    
    @staticmethod
    def ingest_text(file_path: str) -> Dict:
        """Parse TXT/MD files"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        return {
            "filename": Path(file_path).name,
            "format": Path(file_path).suffix.lower().lstrip("."),
            "full_text": text
        }
```

### 4.2 Keyword Detection (nlp/keywords.py)

```python
KEYWORD_DICTIONARIES = {
    "GDPR": {
        "lawful_basis": ["lawful basis", "legal basis", "GDPR Article 6"],
        "data_subject_rights": ["right to access", "right to erasure", "right to be forgotten"],
        "data_protection": ["data protection", "personal data", "processing"],
        "privacy": ["privacy by design", "privacy by default", "privacy impact"],
        # ... 20 items total
    },
    "EU_AI_ACT": {
        "high_risk": ["high-risk", "high risk system", "prohibited"],
        "transparency": ["transparency", "explainability", "interpretability"],
        "human_oversight": ["human oversight", "meaningful human control"],
        # ... 25 items total
    },
    "ISO_13485": {
        "quality_management": ["quality management", "QMS", "quality system"],
        "risk_management": ["risk management", "risk analysis", "hazard"],
        "design_control": ["design control", "design verification"],
        # ... 20 items total
    },
    "IEC_62304": {
        "software_lifecycle": ["software lifecycle", "lifecycle process"],
        "verification": ["verification", "testing", "validation"],
        "documentation": ["documentation", "specifications", "traceability"],
        # ... 15 items total
    },
    "FDA": {
        "510k": ["510k", "predicate device", "substantial equivalence"],
        "clinical_evaluation": ["clinical evaluation", "performance data"],
        "labeling": ["labeling", "instructions for use", "IFU"],
        # ... 10 items total
    }
}

class KeywordDetector:
    """Detect keywords in documents with context extraction"""
    
    def __init__(self):
        self.keywords = KEYWORD_DICTIONARIES
    
    def detect(self, text: str, regulation: str) -> List[Dict]:
        """Find keywords and their context"""
        sentences = self._sentence_tokenize(text)
        matches = []
        
        for idx, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            
            for keyword_group, keywords in self.keywords[regulation].items():
                for keyword in keywords:
                    if keyword.lower() in sentence_lower:
                        # Extract context (±2 sentences)
                        start = max(0, idx - 2)
                        end = min(len(sentences), idx + 3)
                        context = " ".join(sentences[start:end])
                        
                        matches.append({
                            "keyword": keyword,
                            "keyword_group": keyword_group,
                            "sentence": sentence,
                            "context": context,
                            "page": self._estimate_page(text, sentence),
                            "confidence": 0.95
                        })
        
        return matches
    
    def _sentence_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenization"""
        # In production, use spaCy: nlp = spacy.load("en_core_web_sm")
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _estimate_page(self, text: str, sentence: str) -> int:
        """Estimate page number based on character position"""
        pos = text.find(sentence)
        chars_per_page = 3000  # Rough estimate
        return max(1, pos // chars_per_page + 1)
```

### 4.3 Clause Reference Detection (nlp/clause_detector.py)

```python
import re
from typing import List, Dict

class ClauseDetector:
    """Detect regulatory clause references in text"""
    
    # Regex patterns for each regulation
    PATTERNS = {
        "GDPR": [
            r"Article\s+\d+",
            r"GDPR\s+Article\s+\d+",
            r"Recital\s+\d+",
        ],
        "EU_AI_ACT": [
            r"Article\s+\d+",
            r"Annex\s+([IVX]+)",
            r"Section\s+\d+",
        ],
        "ISO_13485": [
            r"Clause\s+[\d.]+",
            r"ISO\s+13485[\s:]?[\d.]*",
        ],
        "IEC_62304": [
            r"Clause\s+[\d.]+",
            r"IEC\s+62304[\s:]?[\d.]*",
        ],
        "FDA": [
            r"21\s+CFR\s+[\d.]+",
            r"510\(k\)",
        ]
    }
    
    @classmethod
    def detect(cls, text: str, regulation: str) -> List[Dict]:
        """Find clause references"""
        matches = []
        
        for pattern in cls.PATTERNS.get(regulation, []):
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Get context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                matches.append({
                    "reference": match.group(0),
                    "position": match.start(),
                    "context": context,
                    "regulation": regulation
                })
        
        return matches
```

### 4.4 Semantic Similarity (nlp/similarity.py)

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticSimilarity:
    """Calculate TF-IDF based semantic similarity"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words="english"
        )
        self.cache = {}
    
    def calculate_similarity(self, requirement: str, document_text: str) -> float:
        """Calculate similarity between requirement and document"""
        try:
            # Vectorize
            tfidf_matrix = self.vectorizer.fit_transform([requirement, document_text])
            
            # Cosine similarity
            similarity = cosine_similarity(tfidf_matrix)[0][1]
            return float(similarity)
        except Exception as e:
            print(f"Similarity calculation failed: {e}")
            return 0.0
    
    def batch_similarity(self, requirements: List[str], document_text: str) -> Dict:
        """Calculate similarity for multiple requirements"""
        results = {}
        for req in requirements:
            results[req] = self.calculate_similarity(req, document_text)
        return results
```

---

## PHASE 5: COMPLIANCE SCORING (Week 7-9, ~80 hours)

### 5.1 Requirement Checklists (compliance/checklists.py)

```python
REQUIREMENTS = {
    "GDPR": [
        {
            "id": "GDPR_1",
            "article": "Article 5",
            "description": "Establish lawful basis for processing",
            "weight": 1.0,
            "impact": "critical"
        },
        {
            "id": "GDPR_2",
            "article": "Article 6",
            "description": "Implement data subject consent mechanisms",
            "weight": 1.0,
            "impact": "critical"
        },
        # ... 18 more items
    ],
    "EU_AI_ACT": [
        {
            "id": "EU_AI_1",
            "article": "Article 6",
            "annex": "III",
            "description": "Risk classification of AI system",
            "weight": 1.0,
            "impact": "critical"
        },
        # ... 24 more items
    ],
    "ISO_13485": [
        {
            "id": "ISO_1",
            "clause": "4.2",
            "description": "Document management system",
            "weight": 1.0,
            "impact": "major"
        },
        # ... 19 more items
    ],
    "IEC_62304": [
        {
            "id": "IEC_1",
            "section": "5.1",
            "description": "Software development planning",
            "weight": 1.0,
            "impact": "major"
        },
        # ... 14 more items
    ],
    "FDA": [
        {
            "id": "FDA_1",
            "cfr": "21 CFR Part 11",
            "description": "Electronic records compliance",
            "weight": 1.0,
            "impact": "critical"
        },
        # ... 9 more items
    ]
}
```

### 5.2 Scoring Logic (compliance/scorer.py)

```python
from typing import Dict, List
from .checklists import REQUIREMENTS
from nlp.similarity import SemanticSimilarity

class ComplianceScorer:
    """Score system compliance based on evidence"""
    
    SCORE_MAPPING = {
        "full_evidence": 1.0,      # Complete compliance
        "substantial": 0.6,         # Most evidence present
        "partial": 0.3,             # Some evidence
        "none": 0.0                 # No evidence
    }
    
    def __init__(self):
        self.similarity = SemanticSimilarity()
    
    def score_requirement(self, requirement: Dict, evidence: str, docs_dict: Dict = None) -> Dict:
        """Score a single requirement"""
        base_score = self._find_base_score(requirement, evidence)
        
        # Upgrade based on similarity
        sim_score = self.similarity.calculate_similarity(
            requirement["description"],
            evidence
        )
        if sim_score > 0.75:
            base_score = min(1.0, base_score + 0.2)  # Upgrade
        elif sim_score < 0.3:
            base_score = max(0.0, base_score - 0.1)  # Downgrade
        
        # Override to 1.0 if dedicated document exists
        regulation = self._get_regulation_for_requirement(requirement)
        if docs_dict and regulation in docs_dict and docs_dict[regulation].get("dedicated"):
            base_score = 1.0
        
        return {
            "requirement_id": requirement["id"],
            "score": base_score,
            "similarity": sim_score,
            "justification": self._generate_justification(base_score, sim_score)
        }
    
    def _find_base_score(self, requirement: Dict, evidence: str) -> float:
        """Determine base score from evidence"""
        evidence_lower = evidence.lower()
        req_desc_lower = requirement["description"].lower()
        
        if req_desc_lower in evidence_lower:
            return self.SCORE_MAPPING["full_evidence"]
        elif any(word in evidence_lower for word in req_desc_lower.split() if len(word) > 4):
            return self.SCORE_MAPPING["substantial"]
        elif any(word in evidence_lower for word in req_desc_lower.split()[:2]):
            return self.SCORE_MAPPING["partial"]
        else:
            return self.SCORE_MAPPING["none"]
    
    def _get_regulation_for_requirement(self, requirement: Dict) -> str:
        """Get regulation name from requirement"""
        for reg, reqs in REQUIREMENTS.items():
            if any(r["id"] == requirement["id"] for r in reqs):
                return reg
        return None
    
    def _generate_justification(self, score: float, similarity: float) -> str:
        """Generate explanation for score"""
        if score == 1.0:
            return "Full evidence of compliance found"
        elif score == 0.6:
            return f"Substantial evidence found (similarity: {similarity:.0%})"
        elif score == 0.3:
            return f"Partial evidence found (similarity: {similarity:.0%})"
        else:
            return "No evidence of compliance found"
```

### 5.3 CRS Calculator (compliance/crs_calculator.py)

```python
from typing import Dict, List
from .checklists import REQUIREMENTS

class CRSCalculator:
    """Calculate Compliance Risk Score"""
    
    WEIGHTS = {
        "GDPR": 0.25,
        "EU_AI_ACT": 0.35,
        "ISO_13485": 0.25,
        "IEC_62304": 0.10,
        "FDA": 0.05
    }
    
    @classmethod
    def calculate(cls, requirement_scores: Dict[str, List[Dict]]) -> Dict:
        """Calculate overall CRS from requirement scores"""
        regulation_scores = {}
        
        # Calculate per-regulation average
        for regulation, scores in requirement_scores.items():
            if scores:
                avg_score = sum(s["score"] for s in scores) / len(scores)
                regulation_scores[regulation] = {
                    "average": avg_score,
                    "count": len(scores),
                    "compliant": sum(1 for s in scores if s["score"] == 1.0),
                    "gaps": sum(1 for s in scores if s["score"] < 1.0)
                }
        
        # Calculate weighted CRS
        crs = 0.0
        weights_used = 0.0
        
        for regulation, weight in cls.WEIGHTS.items():
            if regulation in regulation_scores:
                score = regulation_scores[regulation]["average"]
                crs += score * weight
                weights_used += weight
        
        # Normalize if not all regulations are present
        if weights_used > 0:
            crs = (crs / weights_used) * 100
        
        return {
            "crs_score": round(crs, 2),
            "per_regulation_scores": regulation_scores,
            "max_possible": 100.0,
            "compliance_percentage": round(crs, 1)
        }
```

---

## PHASE 6: CHANGE MONITORING & SCHEDULING (Week 9-11, ~70 hours)

### 6.1 Scheduler (monitoring/scheduler.py)

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scraper import run_all_scrapers
from monitoring import detect_changes, send_notifications
import logging

class ComplianceScheduler:
    """APScheduler for regulatory monitoring"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start scheduler"""
        # Daily EU AI Act check
        self.scheduler.add_job(
            run_all_scrapers,
            trigger=CronTrigger(hour=0, minute=0),  # Midnight
            id="daily_scrape",
            name="Daily regulatory scrape"
        )
        
        # Weekly GDPR/FDA check (Monday)
        self.scheduler.add_job(
            run_all_scrapers,
            trigger=CronTrigger(day_of_week=0, hour=2),  # Monday 2am
            id="weekly_scrape",
            name="Weekly GDPR/FDA check"
        )
        
        # Monthly ISO/IEC check
        self.scheduler.add_job(
            run_all_scrapers,
            trigger=CronTrigger(day=1, hour=3),  # 1st of month, 3am
            id="monthly_scrape",
            name="Monthly ISO/IEC check"
        )
        
        # Detect changes (every 6 hours)
        self.scheduler.add_job(
            detect_changes,
            trigger=CronTrigger(hour="*/6"),
            id="change_detection",
            name="Change detection"
        )
        
        self.scheduler.start()
        self.logger.info("Compliance scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        self.scheduler.shutdown()
        self.logger.info("Compliance scheduler stopped")
```

### 6.2 Email Notifications (monitoring/notifications.py)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

class NotificationService:
    """Send email notifications on regulatory changes"""
    
    EMAIL_TEMPLATES = {
        "critical": {
            "subject": "🚨 CRITICAL: Regulatory Change Detected",
            "body": """
CRITICAL regulatory update detected:

Change: {change_description}
Regulation: {regulation}
Impact: Critical - Immediate review required
Detected: {detected_date}

This change may significantly impact your system's compliance.
Please review immediately and take corrective actions.

IRAQAF Compliance Team
            """
        },
        "major": {
            "subject": "⚠️ MAJOR: Regulatory Update Detected",
            "body": """
Major regulatory update detected:

Change: {change_description}
Regulation: {regulation}
Impact: Major - Review within 7 days
Detected: {detected_date}

This change may impact your system's compliance.
Please review and plan corrective actions.

IRAQAF Compliance Team
            """
        },
        "minor": {
            "subject": "ℹ️ Minor: Regulatory Update",
            "body": """
Minor regulatory update detected:

Change: {change_description}
Regulation: {regulation}
Impact: Minor
Detected: {detected_date}

For informational purposes.

IRAQAF Compliance Team
            """
        }
    }
    
    @staticmethod
    def send_change_notification(recipient: str, change: Dict, severity: str = "major"):
        """Send notification about regulatory change"""
        template = NotificationService.EMAIL_TEMPLATES[severity]
        
        body = template["body"].format(
            change_description=change["description"],
            regulation=change["source_id"],
            detected_date=change["detected_at"],
            impact=change["impact_score"]
        )
        
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient
        msg["Subject"] = template["subject"]
        
        msg.attach(MIMEText(body, "plain"))
        
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
```

---

## PHASE 7: CLI & API INTERFACE (Week 11-12, ~60 hours)

### 7.1 CLI Commands (api_or_cli/cli.py)

```python
import click
import json
from pathlib import Path
from compliance import assess_system
from scraper import run_all_scrapers
from nlp import analyze_documents

@click.group()
def cli():
    """IRAQAF Module 1 - Compliance Analysis System"""
    pass

@cli.command()
def scrape_regulations():
    """Scrape all regulatory sources"""
    click.echo("Scraping regulations...")
    run_all_scrapers()
    click.echo("✅ Scraping complete")

@cli.command()
@click.argument("folder", type=click.Path(exists=True))
def analyze_docs(folder):
    """Analyze documents in folder"""
    click.echo(f"Analyzing documents in {folder}...")
    docs = Path(folder).glob("*.*")
    analysis = analyze_documents(list(docs))
    click.echo(json.dumps(analysis, indent=2))

@cli.command()
@click.argument("folder", type=click.Path(exists=True))
def assess(folder):
    """Run compliance assessment on folder"""
    click.echo(f"Assessing system using documents in {folder}...")
    result = assess_system(folder)
    click.echo(json.dumps(result, indent=2))

if __name__ == "__main__":
    cli()
```

### 7.2 FastAPI Endpoints (api_or_cli/routes.py)

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from .schemas import AssessmentRequest, AssessmentResponse
from compliance import assess_system
from scraper import run_all_scrapers

app = FastAPI(title="IRAQAF Module 1", version="1.0.0")

@app.post("/documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and analyze documents"""
    try:
        # Save uploaded files
        file_paths = []
        for file in files:
            path = f"uploads/{file.filename}"
            with open(path, "wb") as f:
                f.write(await file.read())
            file_paths.append(path)
        
        # Analyze
        analysis = analyze_documents(file_paths)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/assessments")
async def create_assessment(request: AssessmentRequest):
    """Run compliance assessment"""
    try:
        result = assess_system(request.document_paths)
        return AssessmentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Fetch assessment results"""
    # Query database
    db = SessionLocal()
    assessment = db.query(Assessment).filter_by(id=assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"assessment": assessment}

@app.post("/scrape")
async def trigger_scrape():
    """Manually trigger scraping"""
    run_all_scrapers()
    return {"status": "scraping started"}
```

---

## PHASE 8: TESTING & QUALITY ASSURANCE (Week 12-14, ~60 hours)

### 8.1 Unit Tests (tests/test_scoring.py)

```python
import pytest
from compliance.scorer import ComplianceScorer
from compliance.crs_calculator import CRSCalculator
from compliance.checklists import REQUIREMENTS

def test_score_full_evidence():
    """Test scoring with full evidence"""
    scorer = ComplianceScorer()
    requirement = REQUIREMENTS["GDPR"][0]
    evidence = requirement["description"]  # Exact match
    
    result = scorer.score_requirement(requirement, evidence)
    assert result["score"] == 1.0

def test_score_no_evidence():
    """Test scoring with no evidence"""
    scorer = ComplianceScorer()
    requirement = REQUIREMENTS["GDPR"][0]
    evidence = "Completely unrelated text"
    
    result = scorer.score_requirement(requirement, evidence)
    assert result["score"] == 0.0

def test_crs_calculation():
    """Test CRS weighted average"""
    scores = {
        "GDPR": [{"score": 0.8}, {"score": 0.9}],
        "EU_AI_ACT": [{"score": 0.7}],
        "ISO_13485": [{"score": 0.6}],
        "IEC_62304": [{"score": 0.5}],
        "FDA": [{"score": 0.4}]
    }
    
    result = CRSCalculator.calculate(scores)
    assert 0 <= result["crs_score"] <= 100
    assert result["crs_score"] == pytest.approx(66.4, rel=0.1)

def test_gap_categorization():
    """Test gap classification"""
    # Critical: score 0-0.2
    # Major: score 0.2-0.6
    # Minor: score 0.6-1.0
    # Compliant: score 1.0
    pass
```

### 8.2 Integration Test (tests/integration_test.py)

```python
import pytest
from pathlib import Path
from nlp.ingestion import DocumentIngestion
from compliance.scorer import ComplianceScorer
from compliance.crs_calculator import CRSCalculator

def test_end_to_end_assessment():
    """Test: Document → Analysis → Assessment → CRS"""
    
    # 1. Ingest document
    doc_path = "tests/fixtures/sample_quality_manual.pdf"
    doc = DocumentIngestion.ingest(doc_path)
    assert doc["total_pages"] > 0
    
    # 2. Analyze document
    from nlp import KeywordDetector
    detector = KeywordDetector()
    keywords = detector.detect(doc["full_text"], "GDPR")
    assert len(keywords) > 0
    
    # 3. Score requirements
    scorer = ComplianceScorer()
    scores = {}
    for regulation in ["GDPR", "EU_AI_ACT", "ISO_13485"]:
        reg_scores = []
        for req in REQUIREMENTS[regulation]:
            score = scorer.score_requirement(req, doc["full_text"])
            reg_scores.append(score)
        scores[regulation] = reg_scores
    
    # 4. Calculate CRS
    crs_result = CRSCalculator.calculate(scores)
    
    # Assertions
    assert "crs_score" in crs_result
    assert 0 <= crs_result["crs_score"] <= 100
    assert "per_regulation_scores" in crs_result
```

---

## FINAL DELIVERABLES

### After All 8 Phases (16 weeks, ~400 hours):

✅ **100% Specification Compliance**
- ✅ Component 1: Web Scraper (45/45 items)
- ✅ Component 2: NLP Pipeline (42/42 items)
- ✅ Component 3: Compliance Scorer (43/43 items)
- ✅ Component 4: Change Monitor (38/38 items)
- ✅ Database Layer (8/8 tables)
- ✅ API/CLI Interface (5/5 items)
- ✅ Testing Framework (6/6 test suites)
- ✅ Technology Stack (9/9 components)

**Total Implementation**: ~2,500 lines of production code

**Features**:
- Autonomous regulatory monitoring
- Advanced NLP with semantic similarity
- Automated compliance assessment
- Real-time change detection & alerts
- Persistent data storage
- CLI & REST API
- Comprehensive testing
- Enterprise-ready

**Next Integration**: Can then build UI dashboards on top of this backend.

---

**Status**: Ready to begin Phase 1 implementation whenever you approve.
