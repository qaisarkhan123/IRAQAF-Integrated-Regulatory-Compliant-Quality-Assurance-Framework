"""
Feature Integration Layer
Integrates advanced regulatory monitoring, UI components, and compliance checks
with the existing dashboard and provides unified API access.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class PersistenceManager:
    """Manages data persistence for regulatory features."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize persistence manager."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def save_data(self, key: str, data: Any, ttl_hours: int = 24) -> bool:
        """Save data with TTL."""
        try:
            cache_entry = {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "ttl_hours": ttl_hours
            }
            
            # Save to disk
            cache_file = self.cache_dir / f"{key}.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump(cache_entry, f)
            
            # Save to memory
            self.memory_cache[key] = cache_entry
            
            logger.info(f"Data persisted: {key} (TTL: {ttl_hours}h)")
            return True
        except Exception as e:
            logger.error(f"Failed to persist data: {e}")
            return False
    
    def load_data(self, key: str, check_ttl: bool = True) -> Optional[Any]:
        """Load data and check TTL if enabled."""
        try:
            # Try memory cache first
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if check_ttl and self._is_expired(entry):
                    del self.memory_cache[key]
                    return None
                return entry["data"]
            
            # Load from disk
            cache_file = self.cache_dir / f"{key}.pkl"
            if not cache_file.exists():
                return None
            
            with open(cache_file, "rb") as f:
                entry = pickle.load(f)
            
            if check_ttl and self._is_expired(entry):
                cache_file.unlink()
                return None
            
            self.memory_cache[key] = entry
            return entry["data"]
        
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return None
    
    def clear_expired(self) -> int:
        """Clear all expired entries."""
        cleared = 0
        cache_files = list(self.cache_dir.glob("*.pkl"))
        
        for cache_file in cache_files:
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)
                
                if self._is_expired(entry):
                    cache_file.unlink()
                    cleared += 1
            except Exception as e:
                logger.error(f"Error checking cache file: {e}")
        
        logger.info(f"Cleared {cleared} expired cache entries")
        return cleared
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        timestamp = datetime.fromisoformat(entry["timestamp"])
        ttl_hours = entry.get("ttl_hours", 24)
        expiration = timestamp + timedelta(hours=ttl_hours)
        return datetime.utcnow() > expiration


class FeatureCache:
    """Caching decorator for feature functions."""
    
    def __init__(self, persistence_manager: Optional[PersistenceManager] = None):
        """Initialize cache."""
        self.persistence = persistence_manager or PersistenceManager()
    
    def cached(self, ttl_hours: int = 1):
        """Decorator to cache function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = self.persistence.load_data(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.persistence.save_data(cache_key, result, ttl_hours)
                
                logger.debug(f"Cache miss for {func.__name__}, result cached")
                return result
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate unique cache key."""
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in kwargs.items())
        
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]


class RegulatoryFeaturesAPI:
    """Unified API for regulatory monitoring features."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """Initialize API."""
        self.persistence = PersistenceManager(cache_dir)
        self.cache = FeatureCache(self.persistence)
        
        # Initialize all attributes as None first
        self.change_tracker = None
        self.trend_analyzer = None
        self.alert_generator = None
        self.impact_assessor = None
        self.validator = None
        self.gap_analyzer = None
        self.remediation_tracker = None
        self.mapping_engine = None
        
        # Import feature modules
        try:
            from scripts.advanced_regulatory_monitor import (
                RegulatoryChangeTracker, ComplianceTrendAnalyzer,
                AutomatedAlertGenerator, RegulatoryImpactAssessor
            )
            self.change_tracker = RegulatoryChangeTracker()
            self.trend_analyzer = ComplianceTrendAnalyzer()
            self.alert_generator = AutomatedAlertGenerator()
            self.impact_assessor = RegulatoryImpactAssessor()
            logger.info("Advanced regulatory monitor loaded successfully")
        except ImportError as e:
            logger.warning(f"Advanced regulatory monitor not available: {e}")
        
        try:
            from scripts.advanced_compliance_checks import (
                ComplianceValidator, ComplianceGapAnalyzer,
                RemediationTracker, FrameworkMappingEngine
            )
            self.validator = ComplianceValidator()
            self.gap_analyzer = ComplianceGapAnalyzer()
            self.remediation_tracker = RemediationTracker()
            self.mapping_engine = FrameworkMappingEngine()
            logger.info("Advanced compliance checks loaded successfully")
        except ImportError as e:
            logger.warning(f"Advanced compliance checks not available: {e}")
    
    # Regulatory Change Management
    def track_regulatory_change(self,
                               source: str,
                               regulation_id: str,
                               regulation_name: str,
                               change_type: str,
                               description: str,
                               impact_level: str,
                               affected_systems: List[str],
                               implementation_deadline: Optional[str] = None) -> Dict[str, Any]:
        """Track a new regulatory change."""
        
        change = self.change_tracker.add_change(
            source, regulation_id, regulation_name, change_type,
            description, impact_level, affected_systems, implementation_deadline
        )
        
        # Persist change
        self.persistence.save_data(f"change_{change.change_id}", change.to_dict(), ttl_hours=720)
        
        return change.to_dict()
    
    def get_recent_changes(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get regulatory changes from recent period."""
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        changes = self.change_tracker.get_changes_by_date_range(
            cutoff_date, datetime.utcnow().isoformat()
        )
        return [c.to_dict() for c in changes]
    
    def get_critical_changes(self) -> List[Dict[str, Any]]:
        """Get all critical regulatory changes."""
        changes = self.change_tracker.get_critical_changes()
        return [c.to_dict() for c in changes]
    
    # Compliance Trend Analysis
    def record_compliance_score(self, metric_name: str, compliance_score: float) -> Dict[str, Any]:
        """Record a compliance score."""
        
        trend = self.trend_analyzer.record_compliance_score(metric_name, compliance_score)
        
        # Persist trend
        trend_key = f"trend_{metric_name}_{datetime.utcnow().timestamp()}"
        self.persistence.save_data(trend_key, trend.to_dict(), ttl_hours=2160)
        
        return trend.to_dict()
    
    def get_compliance_trend_analysis(self, metric_name: str) -> Dict[str, Any]:
        """Get trend analysis for a metric."""
        return self.trend_analyzer.get_trend_analysis(metric_name)
    
    def get_all_trends(self) -> List[Dict[str, Any]]:
        """Get trend analysis for all metrics."""
        return self.trend_analyzer.get_all_trends()
    
    # Alert Management
    def generate_alert(self,
                      alert_type: str,
                      affected_regulation: str,
                      message: str,
                      recommended_action: str,
                      risk_level: str = "medium") -> Dict[str, Any]:
        """Generate a regulatory alert."""
        
        if not self.alert_generator:
            logger.warning("Alert generator not available")
            return {"error": "Advanced regulatory monitor not available"}
        
        alert = self.alert_generator.generate_alert(
            alert_type, affected_regulation, message, recommended_action, risk_level
        )
        
        # Persist alert
        self.persistence.save_data(f"alert_{alert.alert_id}", alert.to_dict(), ttl_hours=720)
        
        return alert.to_dict()
    
    def get_open_alerts(self) -> List[Dict[str, Any]]:
        """Get all open alerts."""
        if not self.alert_generator:
            return []
        alerts = self.alert_generator.get_open_alerts()
        return [a.to_dict() for a in alerts]
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get all critical alerts."""
        if not self.alert_generator:
            return []
        alerts = self.alert_generator.get_critical_alerts()
        return [a.to_dict() for a in alerts]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if not self.alert_generator:
            return False
        return self.alert_generator.acknowledge_alert(alert_id)
    
    # Impact Assessment
    def assess_regulatory_impact(self,
                                regulation_id: str,
                                regulation_name: str,
                                affected_systems: List[str],
                                change_description: str,
                                current_compliance_status: str) -> Dict[str, Any]:
        """Assess impact of regulatory change."""
        
        assessment = self.impact_assessor.assess_regulatory_change(
            regulation_id, regulation_name, affected_systems,
            change_description, current_compliance_status
        )
        
        # Persist assessment
        self.persistence.save_data(f"assessment_{assessment['assessment_id']}", assessment, ttl_hours=720)
        
        return assessment
    
    def get_high_priority_assessments(self) -> List[Dict[str, Any]]:
        """Get high-priority impact assessments."""
        return self.impact_assessor.get_high_priority_assessments()
    
    # Compliance Validation
    def validate_system_compliance(self,
                                  system_name: str,
                                  framework: str,
                                  controls: Dict[str, str]) -> Dict[str, Any]:
        """Validate system compliance."""
        
        result = self.validator.validate_system_compliance(system_name, framework, controls)
        
        # Persist validation result
        self.persistence.save_data(f"validation_{result['validation_id']}", result, ttl_hours=360)
        
        return result
    
    def validate_cross_framework(self,
                                system_name: str,
                                frameworks: List[str],
                                controls: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """Validate system across multiple frameworks."""
        
        result = self.validator.cross_framework_validation(system_name, frameworks, controls)
        
        # Persist result
        self.persistence.save_data(f"cross_validation_{system_name}", result, ttl_hours=360)
        
        return result
    
    # Gap Analysis and Remediation
    def identify_compliance_gaps(self,
                                framework: str,
                                current_state: Dict[str, str],
                                required_state: Dict[str, str]) -> List[Dict[str, Any]]:
        """Identify compliance gaps."""
        
        gaps = self.gap_analyzer.identify_gaps(framework, current_state, required_state)
        return [g.to_dict() for g in gaps]
    
    def get_critical_gaps(self) -> List[Dict[str, Any]]:
        """Get all critical gaps."""
        gaps = self.gap_analyzer.get_critical_gaps()
        return [g.to_dict() for g in gaps]
    
    def create_remediation_action(self,
                                 gap_id: str,
                                 action_title: str,
                                 description: str,
                                 assigned_to: Optional[str] = None,
                                 due_date: Optional[str] = None) -> Dict[str, Any]:
        """Create remediation action."""
        
        action = self.remediation_tracker.create_remediation_action(
            gap_id, action_title, description, assigned_to, due_date
        )
        
        return action.to_dict()
    
    def update_remediation_status(self,
                                 action_id: str,
                                 status: str,
                                 completion_percentage: float = None) -> bool:
        """Update remediation action status."""
        
        return self.remediation_tracker.update_action_status(
            action_id, status, completion_percentage
        )
    
    def get_remediation_progress(self) -> Dict[str, Any]:
        """Get overall remediation progress."""
        return self.remediation_tracker.get_action_progress()
    
    # Framework Mapping
    def get_framework_mapping(self,
                             source_framework: str,
                             source_control: str,
                             target_framework: str) -> Optional[Dict[str, Any]]:
        """Get mapping between frameworks."""
        
        mapping = self.mapping_engine.get_mapping(
            source_framework, source_control, target_framework
        )
        
        if mapping:
            from dataclasses import asdict
            return asdict(mapping)
        
        return None
    
    def get_mapped_controls(self,
                           source_framework: str,
                           target_framework: str) -> Dict[str, str]:
        """Get all control mappings between frameworks."""
        
        return self.mapping_engine.get_mapped_controls(source_framework, target_framework)
    
    # Reporting and Analytics
    def generate_compliance_report(self, system_name: str) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_name": system_name,
            "compliance_trends": self.get_all_trends(),
            "open_alerts": self.get_open_alerts(),
            "critical_gaps": self.get_critical_gaps(),
            "remediation_progress": self.get_remediation_progress()
        }
        
        # Persist report
        report_key = f"report_{system_name}_{datetime.utcnow().timestamp()}"
        self.persistence.save_data(report_key, report, ttl_hours=168)
        
        return report
    
    def export_data(self, format: str = "json", data_type: str = "all") -> Optional[str]:
        """Export feature data in specified format."""
        
        export_data = {}
        
        if data_type in ["all", "alerts"] and self.alert_generator:
            export_data["alerts"] = [a.to_dict() for a in self.alert_generator.alerts]
        
        if data_type in ["all", "trends"] and self.trend_analyzer:
            export_data["trends"] = [t.to_dict() for t in self.trend_analyzer.trends]
        
        if data_type in ["all", "changes"] and self.change_tracker:
            export_data["changes"] = [c.to_dict() for c in self.change_tracker.changes]
        
        if data_type in ["all", "gaps"] and self.gap_analyzer:
            export_data["gaps"] = [g.to_dict() for g in self.gap_analyzer.gaps]
        
        if format.lower() == "json":
            return json.dumps(export_data, indent=2, default=str)
        elif format.lower() == "csv":
            # CSV export logic
            logger.warning("CSV export not yet implemented")
            return None
        
        return None
    
    # System Health
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "open_alerts": len(self.get_open_alerts()),
            "critical_alerts": len(self.get_critical_alerts()),
            "total_changes": len(self.change_tracker.changes) if self.change_tracker else 0,
            "remediation_progress": self.get_remediation_progress() if self.remediation_tracker else {},
            "cache_status": {
                "memory_cache_size": len(self.cache.persistence.memory_cache),
                "disk_cache_files": len(list(self.cache.persistence.cache_dir.glob("*.pkl")))
            }
        }
    
    def cleanup(self) -> None:
        """Clean up resources and expired cache."""
        self.persistence.clear_expired()
        logger.info("System cleanup completed")


# Global API instance
_api_instance: Optional[RegulatoryFeaturesAPI] = None


def get_api() -> RegulatoryFeaturesAPI:
    """Get or initialize the global API instance."""
    global _api_instance
    if _api_instance is None:
        _api_instance = RegulatoryFeaturesAPI()
    return _api_instance


def initialize_api(cache_dir: str = ".cache") -> RegulatoryFeaturesAPI:
    """Initialize the API with custom cache directory."""
    global _api_instance
    _api_instance = RegulatoryFeaturesAPI(cache_dir)
    return _api_instance
