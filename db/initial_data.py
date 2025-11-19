"""
Initial Data Loading for IRAQAF Compliance Platform

This script populates the database with initial regulatory content:
- Loads regulatory sources (EU AI Act, GDPR, FDA, ISO 13485, IEC 62304)
- Creates sample systems for testing
- Populates with initial content
- Sets up assessment framework

Usage:
    python db/initial_data.py

Author: IRAQAF Phase 2
Date: 2024
"""

from config import config
from db.operations import db_ops
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# REGULATORY SOURCES DEFINITION
# ============================================================================

REGULATORY_SOURCES = [
    {
        'name': 'EU AI Act',
        'abbreviation': 'EU-AI',
        'url': 'https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
        'parser_type': 'html',
        'description': 'EU Regulation 2024/1689 on Artificial Intelligence',
        'update_frequency': 86400  # Daily
    },
    {
        'name': 'GDPR',
        'abbreviation': 'GDPR',
        'url': 'https://gdpr-info.eu/',
        'parser_type': 'html',
        'description': 'General Data Protection Regulation (EU) 2016/679',
        'update_frequency': 86400
    },
    {
        'name': 'FDA Medical Devices',
        'abbreviation': 'FDA',
        'url': 'https://www.fda.gov/medical-devices/',
        'parser_type': 'html',
        'description': 'FDA Medical Device Classification and Regulations',
        'update_frequency': 172800  # 48 hours
    },
    {
        'name': 'ISO 13485',
        'abbreviation': 'ISO-13485',
        'url': 'https://www.iso.org/standard/59752.html',
        'parser_type': 'html',
        'description': 'Medical devices - Quality management systems',
        'update_frequency': 604800  # Weekly
    },
    {
        'name': 'IEC 62304',
        'abbreviation': 'IEC-62304',
        'url': 'https://www.iec.ch/standard/62304',
        'parser_type': 'html',
        'description': 'Medical device software lifecycle processes',
        'update_frequency': 604800
    }
]


# ============================================================================
# SAMPLE REGULATORY CONTENT
# ============================================================================

SAMPLE_CONTENT = {
    1: [  # EU AI Act
        {
            'title': 'Chapter II: Prohibited AI Practices',
            'section': '5',
            'subsection': '1',
            'content': 'The following AI practices shall be prohibited: (a) Placing on the market or putting into service an AI system that deploys subliminal techniques beyond a person\'s consciousness in order to materially distort a person\'s behavior in a manner that causes or is likely to cause that person or another person physical, material or moral harm; (b) Placing on the market or putting into service an AI system that exploits any of the vulnerabilities of a specific group of persons due to their age, physical or mental disability, in order to materially distort the behavior of a person belonging to that group in a manner that causes or is likely to cause that person or another person physical, material or moral harm.'
        },
        {
            'title': 'Chapter III: High-Risk AI Systems',
            'section': '6',
            'subsection': '1',
            'content': 'Irrespective of whether an AI system is placed on the market or put into service independently or as a component of another product or service, that AI system shall be considered high-risk if it is intended to be used as a safety component of machinery, or where its failure or malfunction may have a reasonably foreseeable adverse effect on health and safety or the environment.'
        },
        {
            'title': 'Chapter III: Requirements for High-Risk AI',
            'section': '8',
            'subsection': '1',
            'content': 'High-risk AI systems shall meet the following requirements: (a) Risk management system; (b) Data and data governance; (c) Documentation and record keeping; (d) Transparency and provision of information to users; (e) Human oversight; (f) Accuracy, robustness and cybersecurity.'
        }
    ],
    2: [  # GDPR
        {
            'title': 'Article 1: Subject-matter and Objectives',
            'section': '1',
            'subsection': '1',
            'content': 'This Regulation lays down rules relating to the protection of natural persons with regard to the processing of personal data and rules relating to the free movement of personal data. This Regulation protects fundamental rights and freedoms of natural persons, in particular their right to the protection of personal data.'
        },
        {
            'title': 'Article 6: Lawfulness of processing',
            'section': '6',
            'subsection': '1',
            'content': 'Processing shall be lawful only if and to the extent that at least one of the following applies: (a) the data subject has given consent to the processing of his or her personal data for one or more specific purposes; (b) processing is necessary for the performance of a contract to which the data subject is party or in order to take steps at the request of the data subject prior to entering into a contract; (c) processing is necessary for compliance with a legal obligation to which the controller is subject.'
        },
        {
            'title': 'Article 5: Principles Relating to Processing',
            'section': '5',
            'subsection': '1',
            'content': 'Personal data shall be processed lawfully, fairly and in a transparent manner (lawfulness, fairness and transparency); collected for specified, explicit and legitimate purposes (purpose limitation); adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed (data minimization); accurate and kept up to date (accuracy); kept in a form which permits identification of data subjects for no longer than necessary (storage limitation).'
        }
    ],
    3: [  # FDA
        {
            'title': 'FDA Classification System',
            'section': 'Part 860',
            'subsection': '3',
            'content': 'Medical devices are classified into one of three classes depending on the controls needed to assure safety and effectiveness. Class I represents the safest and easiest devices to manufacture; Class II represents moderate-risk devices; Class III represents the highest risk devices. Most Class III devices must receive special FDA approval called Premarket Approval (PMA) before they can be legally marketed.'
        },
        {
            'title': 'Quality System Regulation',
            'section': 'Part 820',
            'subsection': '1',
            'content': 'The Quality System Regulation (QSR) is FDA\'s system for regulating medical device manufacturers. Manufacturers are required to implement and maintain systems to ensure their devices are safe and effective. This includes design controls, material specifications, production processes, acceptance criteria, and labeling procedures.'
        }
    ],
    4: [  # ISO 13485
        {
            'title': 'Quality Management System Requirements',
            'section': '4',
            'subsection': '1',
            'content': 'Organizations shall establish, implement, maintain and continually improve a quality management system, including the necessary processes and their interactions, in accordance with the requirements of this International Standard. The organization shall determine the processes needed for the quality management system and their application throughout the organization.'
        },
        {
            'title': 'Management Responsibility',
            'section': '5',
            'subsection': '1',
            'content': 'Top management shall provide evidence of its commitment to the establishment, implementation and improvement of a quality management system. This shall include communicating to the organization the importance of meeting customer as well as regulatory and legal requirements.'
        }
    ],
    5: [  # IEC 62304
        {
            'title': 'Software Development Planning',
            'section': '5',
            'subsection': '1',
            'content': 'The software development planning process shall define the overall approach, allocation of requirements, planning of activities, and resource requirements for software development. It shall ensure that necessary information and resources are made available to execute the process as planned, which includes consideration of backward compatibility.'
        },
        {
            'title': 'Software Requirements Analysis',
            'section': '6',
            'subsection': '1',
            'content': 'The software requirements analysis process shall identify all the software functional and non-functional requirements. These requirements shall form the basis for the subsequent software architectural design and implementation, and shall be documented to a degree of detail that allows an evaluation of compliance.'
        }
    ]
}


# ============================================================================
# SAMPLE SYSTEMS FOR TESTING
# ============================================================================

SAMPLE_SYSTEMS = [
    {
        'name': 'MediTech AI Diagnostic System',
        'owner': 'MediTech Inc.',
        'system_type': 'ai_system',
        'description': 'AI system for medical imaging diagnosis and analysis'
    },
    {
        'name': 'Healthcare Data Platform',
        'owner': 'DataCare Corp.',
        'system_type': 'ai_system',
        'description': 'Platform for processing and analyzing patient health data'
    },
    {
        'name': 'Compliance Monitor',
        'owner': 'Internal IT',
        'system_type': 'ai_system',
        'description': 'System for monitoring regulatory compliance'
    }
]


# ============================================================================
# LOADING FUNCTIONS
# ============================================================================

def initialize_database():
    """Initialize database schema"""
    logger.info("═" * 70)
    logger.info("IRAQAF COMPLIANCE PLATFORM - DATABASE INITIALIZATION")
    logger.info("═" * 70)
    logger.info("")

    if not db_ops.init_database():
        logger.error("✗ Failed to initialize database")
        return False

    return True


def load_regulatory_sources():
    """Load all regulatory sources into database"""
    logger.info("STEP 1: Loading Regulatory Sources")
    logger.info("-" * 70)

    result = db_ops.batch_load_sources(REGULATORY_SOURCES)
    logger.info(f"✓ Loaded {result['success']} sources")

    if result['failed'] > 0:
        logger.warning(f"⚠ Failed to load {result['failed']} sources")

    logger.info("")
    return result['success'] > 0


def load_sample_content():
    """Load sample regulatory content"""
    logger.info("STEP 2: Loading Sample Regulatory Content")
    logger.info("-" * 70)

    content_list = []
    for source_id, items in SAMPLE_CONTENT.items():
        for item in items:
            content_list.append({
                'source_id': source_id,
                'title': item['title'],
                'section': item['section'],
                'subsection': item['subsection'],
                'content': item['content']
            })

    result = db_ops.batch_load_content_parallel(content_list, max_workers=3)
    logger.info(f"✓ Loaded {result['success']} content items")

    if result['failed'] > 0:
        logger.warning(f"⚠ Failed to load {result['failed']} items")

    logger.info("")
    return result['success'] > 0


def create_sample_systems():
    """Create sample systems for testing"""
    logger.info("STEP 3: Creating Sample Systems")
    logger.info("-" * 70)

    success_count = 0
    for system_data in SAMPLE_SYSTEMS:
        system = db_ops.create_system(
            name=system_data['name'],
            owner=system_data['owner'],
            system_type=system_data['system_type'],
            description=system_data['description']
        )
        if system:
            success_count += 1

    logger.info(f"✓ Created {success_count} sample systems")
    logger.info("")
    return success_count == len(SAMPLE_SYSTEMS)


def create_sample_assessments():
    """Create sample assessments"""
    logger.info("STEP 4: Creating Sample Assessments")
    logger.info("-" * 70)

    # Create assessments for each system and regulation
    regulations = ['EU-AI', 'GDPR', 'FDA', 'ISO-13485', 'IEC-62304']
    success_count = 0

    for system_id in range(1, len(SAMPLE_SYSTEMS) + 1):
        for regulation in regulations:
            assessment = db_ops.create_assessment(
                system_id=system_id,
                regulation_type=regulation,
                assessor='initial_loader',
                overall_score=0
            )
            if assessment:
                success_count += 1

    logger.info(f"✓ Created {success_count} sample assessments")
    logger.info("")
    return success_count > 0


def verify_database():
    """Verify database is populated correctly"""
    logger.info("STEP 5: Verifying Database")
    logger.info("-" * 70)

    try:
        from db.database import get_db
        from db.models import RegulatorySource, RegulatoryContent, System, Assessment

        session = next(get_db())

        # Count records
        source_count = session.query(RegulatorySource).count()
        content_count = session.query(RegulatoryContent).count()
        system_count = session.query(System).count()
        assessment_count = session.query(Assessment).count()

        logger.info(f"✓ Regulatory Sources: {source_count}")
        logger.info(f"✓ Content Items: {content_count}")
        logger.info(f"✓ Systems: {system_count}")
        logger.info(f"✓ Assessments: {assessment_count}")

        session.close()

        return all([source_count > 0, content_count > 0, system_count > 0, assessment_count > 0])

    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")
        return False


def print_completion_summary():
    """Print completion summary"""
    logger.info("")
    logger.info("═" * 70)
    logger.info("DATABASE INITIALIZATION COMPLETE")
    logger.info("═" * 70)
    logger.info("")
    logger.info("✓ Database schema created")
    logger.info("✓ Regulatory sources loaded")
    logger.info("✓ Sample content populated")
    logger.info("✓ Sample systems created")
    logger.info("✓ Sample assessments initialized")
    logger.info("")
    logger.info("NEXT STEPS:")
    logger.info("  1. Review db/models.py for database structure")
    logger.info("  2. Run tests: python -m pytest tests/test_database.py")
    logger.info("  3. Begin Phase 2 Week 3: Batch processing & enhanced loading")
    logger.info("")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution"""
    try:
        # Step 1: Initialize database
        if not initialize_database():
            return False

        # Step 2: Load regulatory sources
        if not load_regulatory_sources():
            logger.error("✗ Failed to load regulatory sources")
            return False

        # Step 3: Load sample content
        if not load_sample_content():
            logger.error("✗ Failed to load sample content")
            return False

        # Step 4: Create sample systems
        if not create_sample_systems():
            logger.error("✗ Failed to create sample systems")
            return False

        # Step 5: Create sample assessments
        if not create_sample_assessments():
            logger.error("✗ Failed to create sample assessments")
            return False

        # Step 6: Verify database
        if not verify_database():
            logger.error("✗ Database verification failed")
            return False

        # Print completion summary
        print_completion_summary()
        return True

    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
