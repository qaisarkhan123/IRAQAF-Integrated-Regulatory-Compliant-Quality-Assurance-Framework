"""
PHASE 4: ADVANCED TEXT PROCESSING MODULE
=========================================

Handles sophisticated document processing:
- Table extraction and preservation
- Code/formula detection
- Reference link extraction
- Multi-language support (French, German)
- Context window optimization
- Domain-specific entity recognition

Author: IRAQAF Team
Version: 1.0.0
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

try:
    import spacy
except ImportError:
    spacy = None


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ExtractedTable:
    """Represents an extracted table from document"""
    table_id: str
    title: str
    rows: List[List[str]]
    columns: List[str]
    source_section: str
    extraction_method: str  # 'html', 'pattern', 'heuristic'
    confidence: float

    def to_markdown(self) -> str:
        """Convert table to markdown format"""
        if not self.columns or not self.rows:
            return f"*Empty table: {self.title}*"

        md = f"**{self.title}**\n\n"
        md += "| " + " | ".join(self.columns) + " |\n"
        md += "|" + "|".join(["---"] * len(self.columns)) + "|\n"

        for row in self.rows:
            md += "| " + " | ".join(str(cell) for cell in row) + " |\n"

        return md

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class CodeBlock:
    """Represents extracted code or formula"""
    block_id: str
    language: str  # 'python', 'sql', 'formula', 'pseudocode', 'unknown'
    content: str
    context: str  # surrounding text
    line_start: int
    line_end: int
    confidence: float


@dataclass
class Reference:
    """Represents extracted reference or link"""
    reference_id: str
    text: str
    target: str  # what it references
    reference_type: str  # 'internal', 'external', 'regulation', 'standard'
    target_section: Optional[str]
    url: Optional[str]
    confidence: float


@dataclass
class RequirementEntity:
    """Domain-specific requirement entity"""
    entity_id: str
    requirement_id: str  # e.g., "EU-AI-41.1"
    text: str
    entity_type: str  # 'requirement', 'clause', 'definition', 'obligation'
    regulation: str
    section: str
    mandatory: bool  # True if 'shall', 'must'
    confidence: float
    related_articles: List[str]


# ============================================================================
# TABLE EXTRACTION
# ============================================================================

class TableExtractor:
    """Extracts tables from regulatory documents"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.table_counter = 0

    def extract_html_tables(self, html_content: str) -> List[ExtractedTable]:
        """Extract tables from HTML content"""
        tables = []

        # Simple regex-based table extraction for HTML
        table_pattern = r'<table[^>]*>(.*?)</table>'
        table_matches = re.findall(
            table_pattern, html_content, re.DOTALL | re.IGNORECASE)

        for table_html in table_matches:
            table = self._parse_html_table(table_html)
            if table:
                tables.append(table)

        return tables

    def _parse_html_table(self, table_html: str) -> Optional[ExtractedTable]:
        """Parse individual HTML table"""
        try:
            self.table_counter += 1
            table_id = f"TABLE_{self.table_counter:04d}"

            # Extract headers
            header_pattern = r'<th[^>]*>(.*?)</th>'
            headers = re.findall(header_pattern, table_html, re.IGNORECASE)
            headers = [re.sub(r'<[^>]+>', '', h).strip() for h in headers]

            # Extract rows
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            rows_html = re.findall(
                row_pattern, table_html, re.DOTALL | re.IGNORECASE)

            rows = []
            for row_html in rows_html:
                cell_pattern = r'<t[d|h][^>]*>(.*?)</t[d|h]>'
                cells = re.findall(cell_pattern, row_html, re.IGNORECASE)
                cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                if cells:
                    rows.append(cells)

            if rows:
                return ExtractedTable(
                    table_id=table_id,
                    title=f"Table {self.table_counter}",
                    rows=rows,
                    columns=headers if headers else [
                        f"Col_{i}" for i in range(len(rows[0]))],
                    source_section="Unknown",
                    extraction_method="html",
                    confidence=0.95
                )
        except Exception as e:
            self.logger.warning(f"Error parsing HTML table: {e}")

        return None

    def extract_pattern_tables(self, text: str) -> List[ExtractedTable]:
        """Extract tables from pattern-based delimiters (pipes, dashes, etc.)"""
        tables = []

        # Markdown table pattern: | col | col |
        md_table_pattern = r'\|([^\n\|]+(?:\|[^\n\|]+)*)\|(?:\n\|[\s\-\|\:]+\|)?(?:\n\|([^\n\|]+(?:\|[^\n\|]+)*)\|)*'

        matches = re.finditer(md_table_pattern, text)
        for match in matches:
            table = self._parse_markdown_table(match.group(0))
            if table:
                tables.append(table)

        return tables

    def _parse_markdown_table(self, md_table: str) -> Optional[ExtractedTable]:
        """Parse markdown-style table"""
        try:
            self.table_counter += 1
            lines = md_table.strip().split('\n')

            # Parse header
            header_line = lines[0]
            headers = [h.strip() for h in header_line.split('|')[1:-1]]

            # Parse rows (skip separator line)
            rows = []
            for line in lines[2:]:
                if line.strip():
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    rows.append(cells)

            if rows:
                return ExtractedTable(
                    table_id=f"TABLE_{self.table_counter:04d}",
                    title=f"Table {self.table_counter}",
                    rows=rows,
                    columns=headers if headers else [
                        f"Col_{i}" for i in range(len(rows[0]))],
                    source_section="Unknown",
                    extraction_method="pattern",
                    confidence=0.88
                )
        except Exception as e:
            self.logger.warning(f"Error parsing markdown table: {e}")

        return None


# ============================================================================
# CODE & FORMULA EXTRACTION
# ============================================================================

class CodeFormulaExtractor:
    """Detects and preserves code blocks and formulas"""

    LANGUAGE_PATTERNS = {
        'python': r'(def |import |from |class |if __name__|for |while )',
        'sql': r'(SELECT |INSERT |UPDATE |DELETE |CREATE |ALTER |DROP )',
        'formula': r'([\+\-\*/] |= |< |> |≤ |≥ |∑ |∏ |∫ |√)',
        'pseudocode': r'(Input:|Output:|Algorithm:|Procedure:)',
    }

    CODE_BLOCK_PATTERNS = [
        r'```([a-zA-Z0-9_]*)\n(.*?)\n```',  # Markdown code blocks
        r'<code[^>]*>(.*?)</code>',  # HTML code tags
        r'\{code[^}]*\}(.*?)\{/code\}',  # Wiki-style
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.block_counter = 0

    def extract_code_blocks(self, text: str) -> List[CodeBlock]:
        """Extract all code blocks from text"""
        blocks = []

        for pattern in self.CODE_BLOCK_PATTERNS:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                language = match.group(
                    1) if match.lastindex >= 1 else 'unknown'
                content = match.group(
                    2) if match.lastindex >= 2 else match.group(1)

                block = self._create_code_block(
                    content=content,
                    language=language,
                    context=self._get_context(text, match.start(), match.end())
                )
                blocks.append(block)

        return blocks

    def detect_formulas(self, text: str) -> List[CodeBlock]:
        """Detect mathematical formulas"""
        formulas = []

        # LaTeX formula pattern: $...$ or $$...$$
        latex_patterns = [
            r'\$\$(.*?)\$\$',  # Display mode
            r'(?<!\$)\$(.*?)\$(?!\$)',  # Inline mode
        ]

        for pattern in latex_patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                formula_text = match.group(1).strip()
                if formula_text:
                    self.block_counter += 1
                    formulas.append(CodeBlock(
                        block_id=f"FORMULA_{self.block_counter:04d}",
                        language='formula',
                        content=formula_text,
                        context=self._get_context(
                            text, match.start(), match.end()),
                        line_start=text[:match.start()].count('\n'),
                        line_end=text[:match.end()].count('\n'),
                        confidence=0.92
                    ))

        return formulas

    def _create_code_block(self, content: str, language: str, context: str) -> CodeBlock:
        """Create code block with language detection"""
        self.block_counter += 1

        # Detect language if not provided
        if language == 'unknown' or not language:
            language = self._detect_language(content)

        return CodeBlock(
            block_id=f"CODE_{self.block_counter:04d}",
            language=language,
            content=content,
            context=context,
            line_start=0,
            line_end=content.count('\n'),
            confidence=self._calculate_confidence(language, content)
        )

    def _detect_language(self, content: str) -> str:
        """Detect programming language from content"""
        scores = {}
        for lang, pattern in self.LANGUAGE_PATTERNS.items():
            matches = len(re.findall(pattern, content))
            scores[lang] = matches

        return max(scores, key=scores.get) if scores else 'unknown'

    def _calculate_confidence(self, language: str, content: str) -> float:
        """Calculate confidence in language detection"""
        if language == 'unknown':
            return 0.5

        pattern = self.LANGUAGE_PATTERNS.get(language, r'')
        matches = len(re.findall(pattern, content))
        confidence = min(0.99, 0.7 + (matches * 0.05))

        return confidence

    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Get surrounding context"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]


# ============================================================================
# REFERENCE EXTRACTION
# ============================================================================

class ReferenceExtractor:
    """Extracts references, links, and cross-references"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ref_counter = 0

    def extract_all_references(self, text: str) -> List[Reference]:
        """Extract all types of references"""
        references = []

        references.extend(self.extract_urls(text))
        references.extend(self.extract_internal_refs(text))
        references.extend(self.extract_regulation_refs(text))
        references.extend(self.extract_footnotes(text))

        return references

    def extract_urls(self, text: str) -> List[Reference]:
        """Extract URLs and external links"""
        references = []

        url_pattern = r'https?://[^\s\)\]\}\>\"\']+'
        matches = re.finditer(url_pattern, text, re.IGNORECASE)

        for match in matches:
            self.ref_counter += 1
            references.append(Reference(
                reference_id=f"REF_{self.ref_counter:04d}",
                text=match.group(0),
                target=match.group(0),
                reference_type='external',
                target_section=None,
                url=match.group(0),
                confidence=0.99
            ))

        return references

    def extract_internal_refs(self, text: str) -> List[Reference]:
        """Extract internal references like 'see section 3.2'"""
        references = []

        patterns = [
            (r'see\s+(?:section|§)\s+([0-9\.]+)', 'section'),
            (r'Article\s+([0-9]+)', 'article'),
            (r'Clause\s+([0-9\.]+)', 'clause'),
            (r'Figure\s+([0-9]+)', 'figure'),
            (r'Table\s+([0-9]+)', 'table'),
        ]

        for pattern, ref_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                self.ref_counter += 1
                references.append(Reference(
                    reference_id=f"REF_{self.ref_counter:04d}",
                    text=match.group(0),
                    target=match.group(1),
                    reference_type='internal',
                    target_section=match.group(1),
                    url=None,
                    confidence=0.85
                ))

        return references

    def extract_regulation_refs(self, text: str) -> List[Reference]:
        """Extract references to regulations (e.g., 'EU AI Act Article 41.1')"""
        references = []

        # Pattern: Regulation Article X.Y
        pattern = r'(?:EU|ISO|GDPR|FDA|IEC|NIST|SOC)\s+(?:AI\s+Act\s+)?(?:Article|Section)\s+([0-9\.]+(?:\([a-z]\))?)'
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            self.ref_counter += 1
            references.append(Reference(
                reference_id=f"REF_{self.ref_counter:04d}",
                text=match.group(0),
                target=match.group(1),
                reference_type='regulation',
                target_section=match.group(1),
                url=None,
                confidence=0.9
            ))

        return references

    def extract_footnotes(self, text: str) -> List[Reference]:
        """Extract footnote/endnote references"""
        references = []

        # Pattern: [1], [2], etc.
        pattern = r'\[([0-9]+)\]'
        matches = re.finditer(pattern, text)

        for match in matches:
            self.ref_counter += 1
            references.append(Reference(
                reference_id=f"REF_{self.ref_counter:04d}",
                text=match.group(0),
                target=f"footnote_{match.group(1)}",
                reference_type='internal',
                target_section=None,
                url=None,
                confidence=0.88
            ))

        return references


# ============================================================================
# REQUIREMENT ENTITY RECOGNITION
# ============================================================================

class RequirementEntityRecognizer:
    """Domain-specific NER for requirement extraction"""

    REQUIREMENT_KEYWORDS = {
        'shall': True,
        'must': True,
        'required': True,
        'requirement': True,
        'mandatory': True,
        'should': False,
        'may': False,
        'optional': False,
        'recommended': False,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.entity_counter = 0

    def extract_requirements(self, text: str, regulation: str, section: str) -> List[RequirementEntity]:
        """Extract requirement entities from text"""
        requirements = []

        sentences = self._split_sentences(text)

        for sent_idx, sentence in enumerate(sentences):
            # Check if sentence contains requirement keywords
            is_mandatory = self._is_mandatory(sentence)

            if self._contains_requirement(sentence) or is_mandatory:
                self.entity_counter += 1
                req_id = f"{self._get_regulation_prefix(regulation)}-{section.replace('.', '-')}-{self.entity_counter}"

                entity = RequirementEntity(
                    entity_id=f"ENT_{self.entity_counter:05d}",
                    requirement_id=req_id,
                    text=sentence.strip(),
                    entity_type=self._classify_entity(sentence),
                    regulation=regulation,
                    section=section,
                    mandatory=is_mandatory,
                    confidence=self._calculate_requirement_confidence(
                        sentence),
                    related_articles=self._extract_related_articles(sentence)
                )
                requirements.append(entity)

        return requirements

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _is_mandatory(self, text: str) -> bool:
        """Check if text is mandatory (contains 'shall', 'must')"""
        mandatory_words = r'\b(shall|must)\b'
        return bool(re.search(mandatory_words, text, re.IGNORECASE))

    def _contains_requirement(self, text: str) -> bool:
        """Check if text contains requirement indicators"""
        req_words = r'\b(requirement|requirement|specification|guideline|criteria)\b'
        return bool(re.search(req_words, text, re.IGNORECASE))

    def _classify_entity(self, text: str) -> str:
        """Classify entity type"""
        if re.search(r'\b(definition|defined as|means)\b', text, re.IGNORECASE):
            return 'definition'
        elif re.search(r'\b(clause|paragraph|subsection)\b', text, re.IGNORECASE):
            return 'clause'
        elif re.search(r'\b(shall|must)\b', text, re.IGNORECASE):
            return 'requirement'
        else:
            return 'obligation'

    def _calculate_requirement_confidence(self, text: str) -> float:
        """Calculate confidence in requirement detection"""
        confidence = 0.5

        if self._is_mandatory(text):
            confidence += 0.3
        if self._contains_requirement(text):
            confidence += 0.2
        if len(text.split()) > 5:  # Longer texts are more likely actual requirements
            confidence += 0.1

        return min(0.99, confidence)

    def _extract_related_articles(self, text: str) -> List[str]:
        """Extract related article references"""
        articles = []
        pattern = r'(?:Article|Section)\s+([0-9\.]+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return list(set(matches))

    def _get_regulation_prefix(self, regulation: str) -> str:
        """Get regulation prefix for requirement ID"""
        prefixes = {
            'EU AI Act': 'EU-AI',
            'GDPR': 'GDPR',
            'FDA': 'FDA',
            'ISO 13485': 'ISO-13485',
            'IEC 62304': 'IEC-62304',
        }
        return prefixes.get(regulation, regulation.upper()[:3])


# ============================================================================
# LANGUAGE SUPPORT
# ============================================================================

class MultiLanguageProcessor:
    """Handles multi-language document processing"""

    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
    }

    # Language-specific requirement keywords
    REQUIREMENT_KEYWORDS_MULTI = {
        'en': ['shall', 'must', 'required', 'requirement', 'mandatory'],
        'fr': ['doit', 'doit être', 'exigence', 'obligatoire', 'nécessaire'],
        'de': ['soll', 'muss', 'erforderlich', 'Anforderung', 'obligatorisch'],
        'es': ['debe', 'debe ser', 'requisito', 'obligatorio', 'necesario'],
        'it': ['deve', 'deve essere', 'requisito', 'obbligatorio', 'necessario'],
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect document language"""
        try:
            if TextBlob is not None:
                blob = TextBlob(text[:500])
                lang = blob.detect_language()
                return lang, 0.8
        except Exception as e:
            self.logger.warning(f"Language detection error: {e}")

        # Fallback: check for language-specific keywords
        return self._detect_by_keywords(text)

    def _detect_by_keywords(self, text: str) -> Tuple[str, float]:
        """Fallback language detection by keywords"""
        text_lower = text.lower()
        scores = {}

        for lang, keywords in self.REQUIREMENT_KEYWORDS_MULTI.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[lang] = score

        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(0.7, 0.3 + (scores[best_lang] * 0.1))
            return best_lang, confidence

        return 'en', 0.5

    def translate_requirement_keywords(self, language: str) -> List[str]:
        """Get requirement keywords for language"""
        return self.REQUIREMENT_KEYWORDS_MULTI.get(language, self.REQUIREMENT_KEYWORDS_MULTI['en'])


# ============================================================================
# CONTEXT WINDOW OPTIMIZER
# ============================================================================

class ContextWindowOptimizer:
    """Optimizes context windows for NLP processing"""

    def __init__(self, window_size: int = 512, overlap: int = 50):
        self.window_size = window_size
        self.overlap = overlap
        self.logger = logging.getLogger(__name__)

    def create_context_windows(self, text: str) -> List[Dict[str, Any]]:
        """Create overlapping context windows for processing"""
        windows = []
        words = text.split()

        start = 0
        while start < len(words):
            end = min(start + self.window_size, len(words))

            window_text = ' '.join(words[start:end])
            window_hash = hashlib.md5(window_text.encode()).hexdigest()

            windows.append({
                'window_id': f"WIN_{len(windows):04d}",
                'text': window_text,
                'start_idx': start,
                'end_idx': end,
                'word_count': end - start,
                'hash': window_hash,
            })

            start = end - self.overlap

        self.logger.info(
            f"Created {len(windows)} context windows from {len(words)} words")
        return windows

    def merge_overlapping_results(self, windows: List[Dict], results: List[Dict]) -> List[Dict]:
        """Merge results from overlapping windows to remove duplicates"""
        seen_hashes = set()
        merged = []

        for result in results:
            result_hash = hashlib.md5(str(result).encode()).hexdigest()
            if result_hash not in seen_hashes:
                merged.append(result)
                seen_hashes.add(result_hash)

        return merged


# ============================================================================
# ADVANCED TEXT PROCESSOR (Main Class)
# ============================================================================

class AdvancedTextProcessor:
    """Main processor combining all text processing capabilities"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.table_extractor = TableExtractor()
        self.code_extractor = CodeFormulaExtractor()
        self.ref_extractor = ReferenceExtractor()
        self.req_recognizer = RequirementEntityRecognizer()
        self.lang_processor = MultiLanguageProcessor()
        self.context_optimizer = ContextWindowOptimizer()

    def process_document(self, text: str, regulation: str, section: str) -> Dict[str, Any]:
        """
        Process complete document with all NLP enhancements

        Returns:
            Dict with tables, code blocks, references, requirements, etc.
        """
        self.logger.info(f"Processing document: {regulation} - {section}")

        # Detect language
        language, lang_confidence = self.lang_processor.detect_language(text)

        # Extract structural elements
        tables = self.table_extractor.extract_html_tables(text)
        tables.extend(self.table_extractor.extract_pattern_tables(text))

        code_blocks = self.code_extractor.extract_code_blocks(text)
        formulas = self.code_extractor.detect_formulas(text)

        references = self.ref_extractor.extract_all_references(text)

        # Extract requirements
        requirements = self.req_recognizer.extract_requirements(
            text, regulation, section)

        # Create context windows
        context_windows = self.context_optimizer.create_context_windows(text)

        return {
            'regulation': regulation,
            'section': section,
            'language': language,
            'language_confidence': lang_confidence,
            'tables': [t.to_dict() for t in tables],
            'code_blocks': [asdict(c) for c in code_blocks],
            'formulas': [asdict(f) for f in formulas],
            'references': [asdict(r) for r in references],
            'requirements': [asdict(req) for req in requirements],
            'context_windows': context_windows,
            'statistics': {
                'total_tables': len(tables),
                'total_code_blocks': len(code_blocks),
                'total_formulas': len(formulas),
                'total_references': len(references),
                'total_requirements': len(requirements),
                'text_length': len(text),
                'word_count': len(text.split()),
            }
        }

    def batch_process(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process multiple documents

        Args:
            documents: List of {'text': str, 'regulation': str, 'section': str}

        Returns:
            List of processed documents
        """
        results = []
        for doc in documents:
            try:
                result = self.process_document(
                    text=doc['text'],
                    regulation=doc['regulation'],
                    section=doc['section']
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing document: {e}")
                results.append({
                    'error': str(e),
                    'regulation': doc.get('regulation'),
                    'section': doc.get('section')
                })

        return results


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


if __name__ == "__main__":
    setup_logging()

    # Example usage
    processor = AdvancedTextProcessor()

    sample_text = """
    <table>
    <tr><th>Requirement</th><th>Category</th></tr>
    <tr><td>System shall have encryption</td><td>Security</td></tr>
    </table>
    
    Algorithm:
    ```python
    def check_compliance(score):
        return score >= 0.8
    ```
    
    See Section 3.2 for details. References: https://example.com/docs
    
    Requirements:
    - The system shall implement role-based access control.
    - All data must be encrypted using AES-256.
    - The system should provide audit logs.
    """

    result = processor.process_document(
        text=sample_text,
        regulation='EU AI Act',
        section='4.1'
    )

    print(json.dumps(result, indent=2, default=str))
