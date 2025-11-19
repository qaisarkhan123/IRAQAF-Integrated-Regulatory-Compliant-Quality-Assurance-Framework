"""
Base scraper module for IRAQAF
Provides foundation for all regulatory source scrapers
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import logging
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from config import SCRAPER_CONFIG

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all regulatory scrapers
    Implements retry logic, hashing, and standard error handling
    """

    def __init__(self, source_name: str, url: str):
        self.source_name = source_name
        self.url = url
        self.session = requests.Session()
        self.session.headers.update(SCRAPER_CONFIG["headers"])
        self.session.timeout = SCRAPER_CONFIG["timeout"]

    def fetch_content(self, url: str = None) -> Optional[str]:
        """
        Fetch content from URL with retry logic and backoff
        """
        url = url or self.url
        retries = SCRAPER_CONFIG["retries"]
        backoff_factor = SCRAPER_CONFIG["backoff_factor"]

        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    timeout=SCRAPER_CONFIG["timeout"],
                    allow_redirects=True
                )
                response.raise_for_status()
                logger.info(f"{self.source_name}: Successfully fetched {url}")
                return response.text

            except requests.exceptions.Timeout:
                logger.warning(f"{self.source_name}: Timeout on attempt {attempt + 1}/{retries}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"{self.source_name}: Connection error on attempt {attempt + 1}/{retries}")
            except requests.exceptions.HTTPError as e:
                logger.error(f"{self.source_name}: HTTP error {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"{self.source_name}: Unexpected error: {str(e)}")

            if attempt < retries - 1:
                wait_time = backoff_factor ** attempt
                logger.info(f"Retrying in {wait_time:.2f} seconds...")
                import time
                time.sleep(wait_time)

        logger.error(f"{self.source_name}: Failed to fetch after {retries} attempts")
        return None

    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute SHA-256 hash for change detection"""
        return hashlib.sha256(content.encode()).hexdigest()

    @abstractmethod
    def parse_html(self, content: str) -> List[Dict]:
        """
        Parse HTML content into structured data
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    def parse_pdf(self, content: str) -> List[Dict]:
        """
        Parse PDF content into structured data
        Must be implemented by subclasses
        """
        pass

    def scrape(self) -> List[Dict]:
        """
        Main scraping method with error handling
        """
        try:
            content = self.fetch_content()
            if not content:
                return []

            # Detect content type and parse accordingly
            if content.startswith("%PDF"):
                return self.parse_pdf(content)
            else:
                return self.parse_html(content)

        except Exception as e:
            logger.error(f"{self.source_name}: Scraping failed: {str(e)}")
            return []


class HTMLScraper(BaseScraper):
    """Scraper for HTML-based regulatory documents"""

    def parse_html(self, content: str) -> List[Dict]:
        """Parse HTML using BeautifulSoup"""
        soup = BeautifulSoup(content, "html.parser")
        results = []

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text and structure
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        results.append({
            "title": soup.title.string if soup.title else "Untitled",
            "content": text,
            "hash": self.compute_hash(text),
            "extracted_at": datetime.utcnow().isoformat(),
            "source": self.source_name
        })

        return results

    def parse_pdf(self, content: str) -> List[Dict]:
        """PDF parsing delegated to PDF scraper"""
        raise NotImplementedError("Use PDFScraper for PDF content")


class PDFScraper(BaseScraper):
    """Scraper for PDF-based regulatory documents"""

    def parse_html(self, content: str) -> List[Dict]:
        """HTML parsing delegated to HTML scraper"""
        raise NotImplementedError("Use HTMLScraper for HTML content")

    def parse_pdf(self, content: str) -> List[Dict]:
        """Parse PDF using pdfplumber"""
        import pdfplumber
        from io import BytesIO

        results = []
        try:
            # Assuming content is already bytes or can be converted
            pdf_file = BytesIO(content) if isinstance(content, bytes) else content

            with pdfplumber.open(pdf_file) as pdf:
                full_text = ""
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += f"\n--- Page {i+1} ---\n{text}"

                results.append({
                    "title": f"{self.source_name} PDF",
                    "content": full_text,
                    "hash": self.compute_hash(full_text),
                    "extracted_at": datetime.utcnow().isoformat(),
                    "source": self.source_name,
                    "pages": len(pdf.pages)
                })

        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")

        return results
