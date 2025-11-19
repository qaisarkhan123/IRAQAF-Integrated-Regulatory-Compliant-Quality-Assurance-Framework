"""
Database models for Fairness & Ethics module
Stores fairness metric snapshots, governance assessments, and drift events
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class DriftSeverity(Enum):
    """IRAQAF Fairness drift severity levels (3-level classification)

    Based on absolute change in fairness metric:
    - NONE: change < 0.03 (acceptable variation)
    - MINOR: change 0.03-0.15 (requires monitoring)
    - MAJOR: change >= 0.15 (requires action)
    """
    NONE = "none"      # No significant drift detected
    MINOR = "minor"    # Drift detected, within acceptable bounds
    MAJOR = "major"    # Significant drift, requires intervention


@dataclass
class MetricValue:
    """Single metric value with metadata"""
    name: str
    value: float
    group: Optional[str] = None
    subgroup: Optional[str] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FairnessMetricSnapshot:
    """Complete fairness metrics snapshot for a moment in time"""
    system_id: str
    model_version: str
    timestamp: str

    # Demographic Parity metrics
    demographic_parity_gap: Dict[str, float]  # per protected attribute
    demographic_parity_scores: Dict[str, float]

    # Equal Opportunity metrics
    tpr_gap: Dict[str, float]
    tpr_scores: Dict[str, float]

    # Equalized Odds metrics
    equalized_odds_gap: Dict[str, float]
    equalized_odds_scores: Dict[str, float]

    # Predictive Parity metrics
    ppv_gap: Dict[str, float]
    ppv_scores: Dict[str, float]

    # Calibration metrics
    calibration_gap: Dict[str, float]
    calibration_scores: Dict[str, float]

    # Subgroup performance
    subgroup_accuracy_ratio: float
    subgroup_performance_scores: Dict[str, float]

    # Overall Category A score
    category_a_score: float

    # Critical issues found
    critical_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GovernanceAssessment:
    """Governance assessment results"""
    system_id: str
    timestamp: str

    # Category B: Bias Detection & Mitigation
    training_data_bias_assessment: float
    bias_mitigation_techniques: float
    proxy_variable_analysis: float
    fairness_accuracy_tradeoff: float
    category_b_score: float

    # Category C: Ethical Governance & Oversight
    ethics_committee_approval: float
    stakeholder_consultation: float
    accountability_assignment: float
    incident_response_plan: float
    category_c_score: float

    # Category D: Continuous Fairness Monitoring
    drift_detection_design: float
    subgroup_performance_tracking: float
    category_d_score: float

    # Findings and explanations
    findings: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DriftEvent:
    """Records a fairness drift detection event"""
    system_id: str
    timestamp: str
    metric_name: str
    baseline_value: float
    current_value: float
    change: float  # current - baseline
    severity: DriftSeverity
    test_type: str  # "statistical", "control_chart", "window"
    p_value: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


@dataclass
class ResearchPaper:
    """Fairness research paper metadata"""
    title: str
    authors: List[str]
    year: int
    source: str  # "arxiv", "facct", "neurips", "icml", etc.
    link: str
    topics: List[str]  # e.g. ["equalized_odds", "calibration", "medical_ai"]
    abstract: Optional[str] = None
    fetched_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Module3Score:
    """Complete Module 3 (Fairness & Ethics) score"""
    system_id: str
    timestamp: str

    # Category scores
    category_a_score: float  # Algorithmic Fairness Metrics
    category_b_score: float  # Bias Detection & Mitigation
    category_c_score: float  # Ethical Governance & Oversight
    category_d_score: float  # Continuous Fairness Monitoring

    # Overall score (weighted average)
    overall_score: float

    # Categorized issues
    # [{"issue": "...", "recommendation": "..."}]
    critical_gaps: List[Dict[str, str]]
    major_gaps: List[Dict[str, str]]
    minor_gaps: List[Dict[str, str]]

    # Status summary
    risk_level: str  # "High", "Medium", "Low"
    summary: str

    # Supporting data
    metrics_detail: Optional[Dict[str, Any]] = None
    governance_detail: Optional[Dict[str, Any]] = None
    drift_detail: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FairnessRepository:
    """
    Fairness assessment repository interface.

    NOTE: This is an in-memory reference implementation for prototyping and development.

    Production deployments MUST use a persistent SQL backend (PostgreSQL/MySQL) that:
    - Uses the same database connection pool as Module 1's compliance repository
    - Implements SQLAlchemy ORM for consistency with other modules
    - Includes audit logging and data retention policies
    - Supports transaction isolation and ACID compliance

    Migration from in-memory to SQL is straightforward - this class provides
    the interface that translates directly to SQLAlchemy models.
    """

    def __init__(self):
        raise NotImplementedError(
            "Use FairnessDatabase (in-memory) or SQLFairnessRepository")


class FairnessDatabase(FairnessRepository):
    """
    In-memory fairness assessment repository.

    Provides transient storage for development and testing. All data is lost
    when the process terminates. For production, migrate to SQL backend using
    the same interface.
    """

    def __init__(self):
        self.metric_snapshots: List[FairnessMetricSnapshot] = []
        self.governance_assessments: List[GovernanceAssessment] = []
        self.drift_events: List[DriftEvent] = []
        self.research_papers: List[ResearchPaper] = []

    def store_metric_snapshot(self, snapshot: FairnessMetricSnapshot) -> None:
        """Store a fairness metric snapshot"""
        self.metric_snapshots.append(snapshot)

    def get_metric_snapshots(self, system_id: str, limit: int = 10) -> List[FairnessMetricSnapshot]:
        """Retrieve recent metric snapshots for a system"""
        return [s for s in self.metric_snapshots if s.system_id == system_id][-limit:]

    def store_governance_assessment(self, assessment: GovernanceAssessment) -> None:
        """Store a governance assessment"""
        self.governance_assessments.append(assessment)

    def get_latest_governance(self, system_id: str) -> Optional[GovernanceAssessment]:
        """Get the latest governance assessment for a system"""
        assessments = [
            a for a in self.governance_assessments if a.system_id == system_id]
        return assessments[-1] if assessments else None

    def store_drift_event(self, event: DriftEvent) -> None:
        """Record a drift detection event"""
        self.drift_events.append(event)

    def get_drift_events(self, system_id: str, limit: int = 10) -> List[DriftEvent]:
        """Retrieve recent drift events"""
        return [e for e in self.drift_events if e.system_id == system_id][-limit:]

    def store_research_paper(self, paper: ResearchPaper) -> None:
        """Store a research paper reference"""
        self.research_papers.append(paper)

    def get_research_papers(self, topic: Optional[str] = None, limit: int = 20) -> List[ResearchPaper]:
        """Retrieve research papers, optionally filtered by topic"""
        papers = self.research_papers
        if topic:
            papers = [p for p in papers if topic.lower() in [t.lower()
                                                             for t in p.topics]]
        return sorted(papers, key=lambda p: p.year, reverse=True)[:limit]


# Global database instance
_db = FairnessDatabase()


def get_fairness_db() -> FairnessDatabase:
    """Get the global fairness database instance"""
    return _db
