"""
IRAQAF Scraper Module
Initialization and public API
"""

from .base_scraper import BaseScraper, HTMLScraper, PDFScraper
from .scrapers import (
    EUAIActScraper,
    GDPRScraper,
    ISO13485Scraper,
    IEC62304Scraper,
    FDAScraper,
)

__all__ = [
    "BaseScraper",
    "HTMLScraper",
    "PDFScraper",
    "EUAIActScraper",
    "GDPRScraper",
    "ISO13485Scraper",
    "IEC62304Scraper",
    "FDAScraper",
]
