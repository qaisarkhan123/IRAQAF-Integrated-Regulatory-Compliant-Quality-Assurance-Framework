"""
Database Operations Module for IRAQAF Compliance Platform

This module provides core database operations for:
- Loading regulatory sources
- Scraping and storing content
- Detecting changes in regulatory content
- Batch operations with parallel processing
- Compliance history tracking
- Requirement management

Author: IRAQAF Phase 2
Date: 2024
"""

import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup

from config import config
from db.database import init_db, get_db
from db.models import (
    Base, RegulatorySource, RegulatoryContent, ChangeHistory,
    System, SystemComplianceHistory, Assessment, AssessmentRequirement
)

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseOperations:
    """Core database operations for compliance platform"""

    def __init__(self):
        """Initialize database operations"""
        self.engine = create_engine(config.DATABASE_URL)
        self.session = None

    def init_database(self) -> bool:
        """
        Initialize database and create all tables

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            init_db()
            logger.info("✓ Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            return False

    def load_regulatory_source(
        self,
        source_name: str,
        url: str,
        parser_type: str,
        abbreviation: str = "",
        description: str = "",
        update_frequency: int = 86400
    ) -> Optional[RegulatorySource]:
        """
        Load a regulatory source into database

        Args:
            source_name: Name of regulatory source (e.g., "EU AI Act")
            url: URL of regulatory source
            parser_type: Type of parser ('html' or 'pdf')
            abbreviation: Short abbreviation (e.g., "EU-AI")
            description: Source description
            update_frequency: Update frequency in seconds (default: 24h)

        Returns:
            RegulatorySource object if successful, None otherwise
        """
        try:
            session = next(get_db())

            # Check if source already exists
            existing = session.query(RegulatorySource).filter_by(name=source_name).first()
            if existing:
                logger.info(f"ℹ Source '{source_name}' already exists")
                return existing

            # Create new source
            source = RegulatorySource(
                name=source_name,
                abbreviation=abbreviation or source_name[:4].upper(),
                description=description,
                url=url,
                parser_type=parser_type,
                update_frequency=update_frequency,
                last_updated=datetime.utcnow()
            )

            session.add(source)
            session.commit()
            logger.info(f"✓ Loaded regulatory source: {source_name}")
            return source

        except Exception as e:
            logger.error(f"✗ Failed to load source {source_name}: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def store_regulatory_content(
        self,
        source_id: int,
        title: str,
        section: str,
        subsection: str,
        content: str
    ) -> Optional[RegulatoryContent]:
        """
        Store regulatory content in database

        Args:
            source_id: ID of regulatory source
            title: Content title
            section: Section number/name
            subsection: Subsection number/name
            content: Actual content text

        Returns:
            RegulatoryContent object if successful, None otherwise
        """
        try:
            session = next(get_db())

            # Compute SHA-256 hash for change detection
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Check if content already exists
            existing = session.query(RegulatoryContent).filter_by(
                source_id=source_id,
                section=section,
                subsection=subsection
            ).first()

            if existing and existing.content_hash == content_hash:
                logger.debug(f"ℹ Content unchanged for {section}.{subsection}")
                return existing

            # If content exists but hash changed, detect change
            if existing and existing.content_hash != content_hash:
                self.detect_changes(
                    source_id=source_id,
                    content_id=existing.id,
                    old_value=existing.content,
                    new_value=content
                )
                existing.content = content
                existing.content_hash = content_hash
                existing.extraction_date = datetime.utcnow()
                session.commit()
                logger.info(f"✓ Updated content: {section}.{subsection}")
                return existing

            # Create new content entry
            content_obj = RegulatoryContent(
                source_id=source_id,
                title=title,
                section=section,
                subsection=subsection,
                content=content,
                content_hash=content_hash,
                extraction_date=datetime.utcnow(),
                is_active=True
            )

            session.add(content_obj)
            session.commit()
            logger.info(f"✓ Stored content: {section}.{subsection}")
            return content_obj

        except Exception as e:
            logger.error(f"✗ Failed to store content: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def detect_changes(
        self,
        source_id: int,
        content_id: int,
        old_value: str,
        new_value: str,
        change_type: str = "modified"
    ) -> Optional[ChangeHistory]:
        """
        Detect and log changes in regulatory content

        Args:
            source_id: ID of regulatory source
            content_id: ID of content that changed
            old_value: Previous content value
            new_value: New content value
            change_type: Type of change ('added', 'modified', 'removed')

        Returns:
            ChangeHistory object if successful, None otherwise
        """
        try:
            session = next(get_db())

            change = ChangeHistory(
                source_id=source_id,
                content_id=content_id,
                change_type=change_type,
                old_value=old_value[:500] if old_value else None,  # Store first 500 chars
                new_value=new_value[:500] if new_value else None,  # Store first 500 chars
                detected_at=datetime.utcnow(),
                notification_sent=False
            )

            session.add(change)
            session.commit()
            logger.info(f"✓ Logged change for content_id {content_id}")
            return change

        except Exception as e:
            logger.error(f"✗ Failed to log change: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def create_system(
        self,
        name: str,
        owner: str,
        system_type: str = "ai_system",
        description: str = ""
    ) -> Optional[System]:
        """
        Create a system for compliance assessment

        Args:
            name: System name
            owner: System owner
            system_type: Type ('ai_system' or 'medical_device')
            description: System description

        Returns:
            System object if successful, None otherwise
        """
        try:
            session = next(get_db())

            system = System(
                name=name,
                description=description,
                owner=owner,
                type=system_type,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(system)
            session.commit()
            logger.info(f"✓ Created system: {name}")
            return system

        except Exception as e:
            logger.error(f"✗ Failed to create system: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def create_assessment(
        self,
        system_id: int,
        regulation_type: str,
        assessor: str = "system",
        overall_score: float = 0
    ) -> Optional[Assessment]:
        """
        Create a compliance assessment

        Args:
            system_id: ID of system being assessed
            regulation_type: Type of regulation (e.g., 'EU-AI', 'GDPR')
            assessor: Name of assessor
            overall_score: Initial assessment score

        Returns:
            Assessment object if successful, None otherwise
        """
        try:
            session = next(get_db())

            assessment = Assessment(
                system_id=system_id,
                assessment_date=datetime.utcnow(),
                regulation_type=regulation_type,
                overall_score=overall_score,
                status="draft",
                assessor=assessor
            )

            session.add(assessment)
            session.commit()
            logger.info(f"✓ Created assessment for system_id {system_id}")
            return assessment

        except Exception as e:
            logger.error(f"✗ Failed to create assessment: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def get_compliance_history(self, system_id: int) -> List[SystemComplianceHistory]:
        """
        Get compliance history for a system

        Args:
            system_id: ID of system

        Returns:
            List of SystemComplianceHistory records
        """
        try:
            session = next(get_db())
            history = session.query(SystemComplianceHistory).filter_by(
                system_id=system_id
            ).order_by(SystemComplianceHistory.assessment_date.desc()).all()
            logger.info(f"✓ Retrieved {len(history)} compliance history records")
            return history

        except Exception as e:
            logger.error(f"✗ Failed to retrieve compliance history: {e}")
            return []
        finally:
            session.close()

    def batch_load_sources(self, sources: List[Dict]) -> Dict[str, int]:
        """
        Load multiple regulatory sources in batch

        Args:
            sources: List of source dictionaries with keys:
                     name, url, parser_type, abbreviation, description

        Returns:
            Dictionary with counts: {'success': int, 'failed': int}
        """
        success_count = 0
        failed_count = 0

        for source in sources:
            result = self.load_regulatory_source(
                source_name=source['name'],
                url=source['url'],
                parser_type=source['parser_type'],
                abbreviation=source.get('abbreviation', ''),
                description=source.get('description', '')
            )
            if result:
                success_count += 1
            else:
                failed_count += 1

        logger.info(f"✓ Batch load complete: {success_count} success, {failed_count} failed")
        return {'success': success_count, 'failed': failed_count}

    def batch_load_content_parallel(
        self,
        content_list: List[Dict],
        max_workers: int = 3
    ) -> Dict[str, int]:
        """
        Load regulatory content in parallel batches

        Args:
            content_list: List of content dictionaries with keys:
                         source_id, title, section, subsection, content
            max_workers: Maximum parallel workers (default: 3)

        Returns:
            Dictionary with counts: {'success': int, 'failed': int, 'skipped': int}
        """
        success_count = 0
        failed_count = 0
        skipped_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for item in content_list:
                future = executor.submit(
                    self.store_regulatory_content,
                    source_id=item['source_id'],
                    title=item['title'],
                    section=item['section'],
                    subsection=item['subsection'],
                    content=item['content']
                )
                futures.append(future)

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"✗ Parallel load failed: {e}")
                    failed_count += 1

        logger.info(
            f"✓ Parallel batch complete: {success_count} success, "
            f"{failed_count} failed, {skipped_count} skipped"
        )
        return {
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count
        }

    def get_regulatory_content(
        self,
        source_id: int,
        section: Optional[str] = None
    ) -> List[RegulatoryContent]:
        """
        Retrieve regulatory content

        Args:
            source_id: ID of regulatory source
            section: Optional section filter

        Returns:
            List of RegulatoryContent objects
        """
        try:
            session = next(get_db())
            query = session.query(RegulatoryContent).filter_by(
                source_id=source_id,
                is_active=True
            )

            if section:
                query = query.filter_by(section=section)

            content = query.all()
            logger.info(f"✓ Retrieved {len(content)} content items")
            return content

        except Exception as e:
            logger.error(f"✗ Failed to retrieve content: {e}")
            return []
        finally:
            session.close()

    def export_regulatory_content(
        self,
        format_type: str = "json"
    ) -> Dict:
        """
        Export regulatory content in various formats

        Args:
            format_type: Export format ('json', 'csv', 'html')

        Returns:
            Dictionary with export data or path
        """
        try:
            session = next(get_db())
            content = session.query(RegulatoryContent).filter_by(is_active=True).all()

            if format_type == "json":
                data = [
                    {
                        "id": c.id,
                        "source": c.regulatory_source.name,
                        "title": c.title,
                        "section": c.section,
                        "subsection": c.subsection,
                        "content_hash": c.content_hash,
                        "extraction_date": str(c.extraction_date)
                    }
                    for c in content
                ]
                logger.info(f"✓ Exported {len(data)} items as JSON")
                return {"format": "json", "count": len(data), "data": data}

            logger.warning(f"⚠ Format '{format_type}' not yet implemented")
            return {"format": format_type, "status": "not_implemented"}

        except Exception as e:
            logger.error(f"✗ Export failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            session.close()

    def get_all_requirements(
        self,
        source_id: Optional[int] = None
    ) -> List[AssessmentRequirement]:
        """
        Get all assessment requirements

        Args:
            source_id: Optional filter by regulatory source

        Returns:
            List of AssessmentRequirement objects
        """
        try:
            session = next(get_db())
            query = session.query(AssessmentRequirement)

            if source_id:
                # Filter by source via assessment
                query = query.join(Assessment).filter(
                    Assessment.regulation_type == self._get_regulation_type(source_id)
                )

            requirements = query.all()
            logger.info(f"✓ Retrieved {len(requirements)} requirements")
            return requirements

        except Exception as e:
            logger.error(f"✗ Failed to retrieve requirements: {e}")
            return []
        finally:
            session.close()

    def get_change_log(
        self,
        source_id: Optional[int] = None,
        limit: int = 100
    ) -> List[ChangeHistory]:
        """
        Get change history log

        Args:
            source_id: Optional filter by source
            limit: Maximum number of records to return

        Returns:
            List of ChangeHistory objects
        """
        try:
            session = next(get_db())
            query = session.query(ChangeHistory)

            if source_id:
                query = query.filter_by(source_id=source_id)

            changes = query.order_by(
                ChangeHistory.detected_at.desc()
            ).limit(limit).all()

            logger.info(f"✓ Retrieved {len(changes)} change records")
            return changes

        except Exception as e:
            logger.error(f"✗ Failed to retrieve change log: {e}")
            return []
        finally:
            session.close()

    def _get_regulation_type(self, source_id: int) -> str:
        """Helper to get regulation type from source"""
        try:
            session = next(get_db())
            source = session.query(RegulatorySource).filter_by(id=source_id).first()
            return source.abbreviation if source else "UNKNOWN"
        except Exception:
            return "UNKNOWN"
        finally:
            session.close()


# Singleton instance
db_ops = DatabaseOperations()


if __name__ == "__main__":
    print("✓ Database operations module loaded")
    print("✓ Use: from db.operations import db_ops")
