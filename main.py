"""
Main entry point for IRAQAF Phase 1
Initializes database, creates configuration, and sets up logging
"""

import logging.config
from config import LOGGING_CONFIG, DATABASE_URL
from db.database import init_db

# Setup logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def initialize_system():
    """Initialize the IRAQAF system"""
    logger.info("=" * 60)
    logger.info("IRAQAF - PHASE 1: ARCHITECTURE RESTRUCTURING")
    logger.info("=" * 60)

    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info(f"Database initialized at: {DATABASE_URL}")

    # Verify imports
    logger.info("Verifying module imports...")
    try:
        from scraper.base_scraper import BaseScraper
        from scraper.scrapers import EUAIActScraper
        from nlp_pipeline.document_processor import DocumentProcessor
        from db.models import (
            RegulatorySource,
            RegulatoryContent,
            Assessment,
        )
        logger.info("✓ All core modules imported successfully")
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        raise

    logger.info("=" * 60)
    logger.info("PHASE 1 INITIALIZATION COMPLETE")
    logger.info("=" * 60)
    logger.info("System is ready for Phase 2: Database Layer Implementation")


if __name__ == "__main__":
    initialize_system()
