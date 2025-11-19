"""
SQLAlchemy ORM Models for IRAQAF
Defines database schema for all compliance data
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


class RegulatorySource(Base):
    """
    Represents a regulatory source (EU AI Act, GDPR, ISO 13485, etc.)
    """
    __tablename__ = "regulatory_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    abbreviation = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    url = Column(String(500))
    parser_type = Column(String(50))  # html, pdf, docx
    update_frequency = Column(String(50))  # daily, weekly, monthly
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    regulatory_content = relationship("RegulatoryContent", back_populates="source")
    change_history = relationship("ChangeHistory", back_populates="source")

    def __repr__(self):
        return f"<RegulatorySource {self.abbreviation}>"


class RegulatoryContent(Base):
    """
    Stores parsed content from regulatory documents
    """
    __tablename__ = "regulatory_content"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("regulatory_sources.id"), nullable=False)
    title = Column(String(500), nullable=False)
    section = Column(String(255))
    subsection = Column(String(255))
    content = Column(Text, nullable=False)
    content_hash = Column(String(64))  # SHA-256 hash for change detection
    extraction_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    source = relationship("RegulatorySource", back_populates="regulatory_content")
    change_history = relationship("ChangeHistory", back_populates="content")

    def __repr__(self):
        return f"<RegulatoryContent {self.source_id}: {self.title}>"


class ChangeHistory(Base):
    """
    Tracks changes detected in regulatory documents
    """
    __tablename__ = "change_history"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("regulatory_sources.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("regulatory_content.id"))
    change_type = Column(String(50))  # added, modified, removed
    old_value = Column(Text)
    new_value = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)
    notification_sent = Column(Boolean, default=False)

    # Relationships
    source = relationship("RegulatorySource", back_populates="change_history")
    content = relationship("RegulatoryContent", back_populates="change_history")

    def __repr__(self):
        return f"<ChangeHistory {self.change_type} at {self.detected_at}>"


class System(Base):
    """
    Represents a system being assessed for compliance
    """
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    owner = Column(String(255))
    type = Column(String(100))  # ai_system, medical_device, data_processor
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    compliance_history = relationship("SystemComplianceHistory", back_populates="system")
    assessments = relationship("Assessment", back_populates="system")

    def __repr__(self):
        return f"<System {self.name}>"


class SystemComplianceHistory(Base):
    """
    Tracks compliance scores over time for each system
    """
    __tablename__ = "system_compliance_history"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    eu_ai_act_score = Column(Float)
    gdpr_score = Column(Float)
    iso_13485_score = Column(Float)
    iec_62304_score = Column(Float)
    fda_score = Column(Float)
    overall_score = Column(Float)

    # Relationships
    system = relationship("System", back_populates="compliance_history")

    def __repr__(self):
        return f"<SystemComplianceHistory {self.system_id} @ {self.assessment_date}>"


class Document(Base):
    """
    Represents uploaded or ingested documents (PDF, DOCX, TXT)
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(500), nullable=False)
    content_type = Column(String(50))  # pdf, docx, txt, html
    file_path = Column(String(1000))
    file_hash = Column(String(64))  # SHA-256
    extracted_text = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    parsed_sections = Column(Integer, default=0)

    def __repr__(self):
        return f"<Document {self.filename}>"


class Assessment(Base):
    """
    Represents a compliance assessment for a system against regulations
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    regulation_type = Column(String(100))  # eu_ai_act, gdpr, iso_13485, etc.
    overall_score = Column(Float)
    status = Column(String(50))  # draft, completed, reviewed
    assessor = Column(String(255))

    # Relationships
    system = relationship("System", back_populates="assessments")
    requirements = relationship("AssessmentRequirement", back_populates="assessment")

    def __repr__(self):
        return f"<Assessment {self.system_id} - {self.regulation_type}>"


class AssessmentRequirement(Base):
    """
    Individual requirement assessment within an assessment
    """
    __tablename__ = "assessment_requirements"

    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    requirement_id = Column(String(100))  # e.g., "EU-AI-41.1"
    requirement_text = Column(Text, nullable=False)
    status = Column(String(50))  # compliant, non_compliant, partial, not_applicable
    score = Column(Float)  # 0-100
    evidence = Column(Text)  # Description of evidence
    gaps = Column(Text)  # Description of gaps
    recommendations = Column(Text)
    assessment_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("Assessment", back_populates="requirements")

    def __repr__(self):
        return f"<AssessmentRequirement {self.requirement_id}>"
