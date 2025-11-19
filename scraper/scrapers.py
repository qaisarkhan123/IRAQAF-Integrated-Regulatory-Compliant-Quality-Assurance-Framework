"""
Scraper implementations for specific regulatory sources
"""

from .base_scraper import HTMLScraper, PDFScraper
import logging

logger = logging.getLogger(__name__)


class EUAIActScraper(HTMLScraper):
    """Scraper for EU AI Act"""

    def __init__(self):
        super().__init__(
            "EU-AI-ACT",
            "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"
        )


class GDPRScraper(HTMLScraper):
    """Scraper for GDPR"""

    def __init__(self):
        super().__init__(
            "GDPR",
            "https://gdpr-info.eu/"
        )


class ISO13485Scraper(PDFScraper):
    """Scraper for ISO 13485 (Medical Device QMS)"""

    def __init__(self):
        super().__init__(
            "ISO-13485",
            "https://www.iso.org/standard/59752.html"
        )


class IEC62304Scraper(PDFScraper):
    """Scraper for IEC 62304 (Medical Device Software)"""

    def __init__(self):
        super().__init__(
            "IEC-62304",
            "https://www.iec.ch/standard/62304"
        )


class FDAScraper(HTMLScraper):
    """Scraper for FDA medical device regulations"""

    def __init__(self):
        super().__init__(
            "FDA",
            "https://www.fda.gov/medical-devices/"
        )
