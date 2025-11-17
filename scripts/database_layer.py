"""
Database Persistence Layer for Regulatory Monitoring System

Provides SQLAlchemy-based ORM models and database connection management
for storing regulatory changes, compliance scores, alerts, and remediation actions.
Supports SQLite (default) and PostgreSQL (production).

Usage:
    from scripts.database_layer import get_db_session, init_db
    
    # Initialize database
    init_db("sqlite:///compliance.db")
    
    # Use session
    with get_db_session() as session:
        regulations = session.query(RegulatoryChange).all()
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Global database components
Base = declarative_base()
_engine = None
_session_factory = None


# ============================================================================
# Enums
# ============================================================================

class RiskLevelEnum(str, Enum):
    """Risk level classifications."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ComplianceStatusEnum(str, Enum):
    """Compliance status values."""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"


class AlertStatusEnum(str, Enum):
    """Alert lifecycle statuses."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class RemediationStatusEnum(str, Enum):
    """Remediation action statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ============================================================================
# Models
# ============================================================================

class RegulatoryChange(Base):
    """
    Represents a regulatory change event.
    
    Tracks new or updated regulations with implementation deadlines,
    impact levels, and affected systems.
    """
    __tablename__ = "regulatory_changes"

    id = Column(String(64), primary_key=True)
    source = Column(String(256), nullable=False)
    regulation_id = Column(String(128), unique=True, nullable=False)
    regulation_name = Column(String(512), nullable=False)
    change_type = Column(String(128), nullable=False)  # requirement_update, new_requirement, etc.
    description = Column(Text, nullable=False)
    impact_level = Column(SQLEnum(RiskLevelEnum), nullable=False)
    affected_systems = Column(Text)  # JSON-encoded list
    implementation_deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_critical = Column(Boolean, default=False)

    # Relationships
    alerts = relationship("ComplianceAlert", back_populates="regulatory_change")
    impacts = relationship("RegulatoryImpact", back_populates="regulatory_change")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source": self.source,
            "regulation_id": self.regulation_id,
            "regulation_name": self.regulation_name,
            "change_type": self.change_type,
            "description": self.description,
            "impact_level": self.impact_level.value,
            "affected_systems": self.affected_systems,
            "implementation_deadline": self.implementation_deadline.isoformat() if self.implementation_deadline else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_critical": self.is_critical,
        }


class ComplianceScore(Base):
    """
    Represents a compliance score for a framework at a point in time.
    
    Stores historical compliance data for trend analysis and reporting.
    """
    __tablename__ = "compliance_scores"

    id = Column(String(64), primary_key=True)
    framework = Column(String(128), nullable=False)  # GDPR, HIPAA, SOC2, etc.
    system_name = Column(String(256), nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    status = Column(SQLEnum(ComplianceStatusEnum), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "framework": self.framework,
            "system_name": self.system_name,
            "score": self.score,
            "status": self.status.value,
            "recorded_at": self.recorded_at.isoformat(),
        }


class ComplianceAlert(Base):
    """
    Represents a compliance-related alert or incident.
    
    Tracks alerts with status lifecycle from open to resolved.
    """
    __tablename__ = "compliance_alerts"

    id = Column(String(64), primary_key=True)
    alert_type = Column(String(128), nullable=False)
    affected_regulation = Column(String(256))
    message = Column(Text, nullable=False)
    recommended_action = Column(Text)
    risk_level = Column(SQLEnum(RiskLevelEnum), nullable=False)
    status = Column(SQLEnum(AlertStatusEnum), default=AlertStatusEnum.OPEN, nullable=False)
    regulatory_change_id = Column(String(64), ForeignKey("regulatory_changes.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)

    # Relationships
    regulatory_change = relationship("RegulatoryChange", back_populates="alerts")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "affected_regulation": self.affected_regulation,
            "message": self.message,
            "recommended_action": self.recommended_action,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


class RemediationAction(Base):
    """
    Represents a remediation action to address a compliance gap.
    
    Tracks action lifecycle from creation to completion with progress tracking.
    """
    __tablename__ = "remediation_actions"

    id = Column(String(64), primary_key=True)
    gap_id = Column(String(256), nullable=False)
    action_title = Column(String(512), nullable=False)
    description = Column(Text, nullable=False)
    assigned_to = Column(String(256))
    status = Column(SQLEnum(RemediationStatusEnum), default=RemediationStatusEnum.PENDING, nullable=False)
    priority = Column(Integer, default=0)  # 0-10
    completion_percentage = Column(Float, default=0.0)
    due_date = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "gap_id": self.gap_id,
            "action_title": self.action_title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "priority": self.priority,
            "completion_percentage": self.completion_percentage,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class RegulatoryImpact(Base):
    """
    Represents the assessed impact of a regulatory change on systems.
    
    Links regulatory changes to system impact analysis.
    """
    __tablename__ = "regulatory_impacts"

    id = Column(String(64), primary_key=True)
    regulatory_change_id = Column(String(64), ForeignKey("regulatory_changes.id"), nullable=False)
    system_name = Column(String(256), nullable=False)
    impact_score = Column(Integer)  # 1-10
    priority_level = Column(SQLEnum(RiskLevelEnum))
    effort_estimate_hours = Column(Integer)
    recommended_timeline_days = Column(Integer)
    assessment_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    regulatory_change = relationship("RegulatoryChange", back_populates="impacts")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "regulatory_change_id": self.regulatory_change_id,
            "system_name": self.system_name,
            "impact_score": self.impact_score,
            "priority_level": self.priority_level.value if self.priority_level else None,
            "effort_estimate_hours": self.effort_estimate_hours,
            "recommended_timeline_days": self.recommended_timeline_days,
            "assessment_date": self.assessment_date.isoformat(),
        }


class SystemHealthLog(Base):
    """
    Represents system health metrics and monitoring logs.
    
    Tracks system performance and health metrics over time.
    """
    __tablename__ = "system_health_logs"

    id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_changes = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    open_alerts = Column(Integer, default=0)
    total_gaps = Column(Integer, default=0)
    remediation_progress = Column(Float, default=0.0)
    avg_compliance_score = Column(Float)
    cache_size = Column(Integer, default=0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "total_changes": self.total_changes,
            "critical_alerts": self.critical_alerts,
            "open_alerts": self.open_alerts,
            "total_gaps": self.total_gaps,
            "remediation_progress": self.remediation_progress,
            "avg_compliance_score": self.avg_compliance_score,
            "cache_size": self.cache_size,
        }


# ============================================================================
# Database Connection Management
# ============================================================================

def init_db(database_url: str = "sqlite:///compliance.db", echo: bool = False) -> None:
    """
    Initialize the database connection and create tables.
    
    Args:
        database_url: Connection string (SQLite or PostgreSQL)
        echo: Enable SQL query logging
        
    Example:
        init_db("sqlite:///compliance.db")
        init_db("postgresql://user:password@localhost/compliance")
    """
    global _engine, _session_factory

    try:
        _engine = create_engine(database_url, echo=echo, pool_pre_ping=True)
        _session_factory = sessionmaker(bind=_engine)
        
        # Create all tables
        Base.metadata.create_all(_engine)
        logger.info(f"Database initialized: {database_url}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@contextmanager
def get_db_session() -> Session:
    """
    Get a database session using context manager.
    
    Usage:
        with get_db_session() as session:
            results = session.query(RegulatoryChange).all()
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


# ============================================================================
# Database Query Helpers
# ============================================================================

class DatabaseQueries:
    """Helper methods for common database queries."""

    @staticmethod
    def get_recent_changes(days: int = 30) -> List[RegulatoryChange]:
        """Get regulatory changes from the last N days."""
        with get_db_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            return session.query(RegulatoryChange).filter(
                RegulatoryChange.created_at >= cutoff
            ).all()

    @staticmethod
    def get_critical_changes() -> List[RegulatoryChange]:
        """Get all critical regulatory changes."""
        with get_db_session() as session:
            return session.query(RegulatoryChange).filter(
                RegulatoryChange.is_critical == True
            ).all()

    @staticmethod
    def get_open_alerts() -> List[ComplianceAlert]:
        """Get all open (unresolved) alerts."""
        with get_db_session() as session:
            return session.query(ComplianceAlert).filter(
                ComplianceAlert.status == AlertStatusEnum.OPEN
            ).all()

    @staticmethod
    def get_critical_alerts() -> List[ComplianceAlert]:
        """Get all critical-level alerts."""
        with get_db_session() as session:
            return session.query(ComplianceAlert).filter(
                ComplianceAlert.risk_level == RiskLevelEnum.CRITICAL
            ).all()

    @staticmethod
    def get_compliance_scores(framework: str, days: int = 30) -> List[ComplianceScore]:
        """Get compliance scores for a framework over time."""
        with get_db_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            return session.query(ComplianceScore).filter(
                ComplianceScore.framework == framework,
                ComplianceScore.recorded_at >= cutoff
            ).order_by(ComplianceScore.recorded_at).all()

    @staticmethod
    def get_pending_remediation() -> List[RemediationAction]:
        """Get all pending or in-progress remediation actions."""
        with get_db_session() as session:
            return session.query(RemediationAction).filter(
                RemediationAction.status.in_([
                    RemediationStatusEnum.PENDING,
                    RemediationStatusEnum.IN_PROGRESS
                ])
            ).all()

    @staticmethod
    def get_overdue_actions() -> List[RemediationAction]:
        """Get remediation actions that are overdue."""
        with get_db_session() as session:
            return session.query(RemediationAction).filter(
                RemediationAction.due_date < datetime.utcnow(),
                RemediationAction.status != RemediationStatusEnum.COMPLETED
            ).all()

    @staticmethod
    def save_compliance_score(
        framework: str,
        system_name: str,
        score: float,
        status: str
    ) -> ComplianceScore:
        """Save a compliance score to the database."""
        from uuid import uuid4
        
        with get_db_session() as session:
            record = ComplianceScore(
                id=str(uuid4()),
                framework=framework,
                system_name=system_name,
                score=score,
                status=ComplianceStatusEnum(status),
            )
            session.add(record)
            session.commit()
            return record

    @staticmethod
    def save_alert(
        alert_type: str,
        message: str,
        risk_level: str,
        affected_regulation: Optional[str] = None,
        recommended_action: Optional[str] = None,
    ) -> ComplianceAlert:
        """Save an alert to the database."""
        from uuid import uuid4
        
        with get_db_session() as session:
            alert = ComplianceAlert(
                id=str(uuid4()),
                alert_type=alert_type,
                message=message,
                risk_level=RiskLevelEnum(risk_level),
                affected_regulation=affected_regulation,
                recommended_action=recommended_action,
            )
            session.add(alert)
            session.commit()
            return alert

    @staticmethod
    def save_regulatory_change(
        source: str,
        regulation_id: str,
        regulation_name: str,
        change_type: str,
        description: str,
        impact_level: str,
        affected_systems: Optional[List[str]] = None,
        implementation_deadline: Optional[datetime] = None,
    ) -> RegulatoryChange:
        """Save a regulatory change to the database."""
        from uuid import uuid4
        import json
        
        with get_db_session() as session:
            change = RegulatoryChange(
                id=str(uuid4()),
                source=source,
                regulation_id=regulation_id,
                regulation_name=regulation_name,
                change_type=change_type,
                description=description,
                impact_level=RiskLevelEnum(impact_level),
                affected_systems=json.dumps(affected_systems or []),
                implementation_deadline=implementation_deadline,
            )
            session.add(change)
            session.commit()
            return change

    @staticmethod
    def save_remediation_action(
        gap_id: str,
        action_title: str,
        description: str,
        assigned_to: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: int = 0,
    ) -> RemediationAction:
        """Save a remediation action to the database."""
        from uuid import uuid4
        
        with get_db_session() as session:
            action = RemediationAction(
                id=str(uuid4()),
                gap_id=gap_id,
                action_title=action_title,
                description=description,
                assigned_to=assigned_to,
                due_date=due_date,
                priority=priority,
            )
            session.add(action)
            session.commit()
            return action

    @staticmethod
    def update_alert_status(alert_id: str, status: str) -> Optional[ComplianceAlert]:
        """Update alert status."""
        with get_db_session() as session:
            alert = session.query(ComplianceAlert).filter(
                ComplianceAlert.id == alert_id
            ).first()
            
            if alert:
                alert.status = AlertStatusEnum(status)
                if status == "acknowledged":
                    alert.acknowledged_at = datetime.utcnow()
                elif status == "resolved":
                    alert.resolved_at = datetime.utcnow()
                session.commit()
            return alert

    @staticmethod
    def update_remediation_status(
        action_id: str,
        status: str,
        completion_percentage: Optional[float] = None,
    ) -> Optional[RemediationAction]:
        """Update remediation action status."""
        with get_db_session() as session:
            action = session.query(RemediationAction).filter(
                RemediationAction.id == action_id
            ).first()
            
            if action:
                action.status = RemediationStatusEnum(status)
                if completion_percentage is not None:
                    action.completion_percentage = completion_percentage
                if status == "in_progress" and not action.started_at:
                    action.started_at = datetime.utcnow()
                elif status == "completed":
                    action.completed_at = datetime.utcnow()
                session.commit()
            return action

    @staticmethod
    def get_system_statistics() -> Dict[str, Any]:
        """Get overall system statistics."""
        with get_db_session() as session:
            return {
                "total_changes": session.query(RegulatoryChange).count(),
                "critical_changes": session.query(RegulatoryChange).filter(
                    RegulatoryChange.is_critical == True
                ).count(),
                "total_alerts": session.query(ComplianceAlert).count(),
                "open_alerts": session.query(ComplianceAlert).filter(
                    ComplianceAlert.status == AlertStatusEnum.OPEN
                ).count(),
                "critical_alerts": session.query(ComplianceAlert).filter(
                    ComplianceAlert.risk_level == RiskLevelEnum.CRITICAL
                ).count(),
                "total_remediation_actions": session.query(RemediationAction).count(),
                "completed_actions": session.query(RemediationAction).filter(
                    RemediationAction.status == RemediationStatusEnum.COMPLETED
                ).count(),
                "pending_actions": session.query(RemediationAction).filter(
                    RemediationAction.status == RemediationStatusEnum.PENDING
                ).count(),
            }
