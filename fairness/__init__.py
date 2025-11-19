"""
Fairness & Ethics Module (Module 3) for IRAQAF
"""

__version__ = "1.0.0"
__author__ = "IRAQAF Team"

from .models import FairnessDatabase, Module3Score, DriftSeverity
from .metrics.fairness_metrics import compute_all_fairness_metrics
from .bias_engine.bias_detection_engine import BiasDetectionEngine, FairnessReport
from .governance.governance_checker import GovernanceChecker, GovernanceReport
from .monitoring.fairness_monitor import FairnessMonitor, get_fairness_monitor
from .research_tracker.research_tracker import ResearchTracker, get_research_tracker
from .api import Module3API, Module3Scorer

__all__ = [
    'FairnessDatabase',
    'Module3Score',
    'DriftSeverity',
    'compute_all_fairness_metrics',
    'BiasDetectionEngine',
    'FairnessReport',
    'GovernanceChecker',
    'GovernanceReport',
    'FairnessMonitor',
    'ResearchTracker',
    'Module3API',
    'Module3Scorer',
    'get_fairness_monitor',
    'get_research_tracker'
]
