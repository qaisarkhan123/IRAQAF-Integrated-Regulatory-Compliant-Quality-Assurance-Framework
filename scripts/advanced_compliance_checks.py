"""
Advanced Compliance Checks Module
Provides comprehensive compliance validation, gap analysis, and remediation tracking.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    NIST = "nist"
    CUSTOM = "custom"


class ComplianceLevel(Enum):
    """Compliance level classifications."""
    FULL = "full"
    SUBSTANTIAL = "substantial"
    PARTIAL = "partial"
    MINIMAL = "minimal"
    NONE = "none"


@dataclass
class ComplianceGap:
    """Represents a compliance gap."""
    gap_id: str
    framework: str
    requirement: str
    current_status: str
    required_status: str
    severity: str  # critical, high, medium, low
    affected_systems: List[str]
    remediation_plan: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemediationAction:
    """Represents a remediation action."""
    action_id: str
    gap_id: str
    action_title: str
    description: str
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, blocked
    completion_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FrameworkMappingRule:
    """Maps controls between compliance frameworks."""
    source_framework: str
    target_framework: str
    source_control: str
    target_control: str
    compatibility_level: str  # full, partial, none
    notes: Optional[str] = None


class ComplianceValidator:
    """Validates compliance across multiple frameworks and controls."""
    
    def __init__(self):
        """Initialize validator."""
        self.framework_requirements: Dict[str, List[str]] = self._load_frameworks()
        self.validation_results: List[Dict[str, Any]] = []
        self.system_controls: Dict[str, Dict[str, str]] = {}
    
    def validate_system_compliance(self,
                                  system_name: str,
                                  framework: str,
                                  controls: Dict[str, str]) -> Dict[str, Any]:
        """Validate a system against a compliance framework."""
        
        timestamp = datetime.utcnow().isoformat()
        validation_id = self._generate_validation_id(system_name, framework, timestamp)
        
        # Get required controls for framework
        required_controls = self.framework_requirements.get(framework.lower(), [])
        
        # Check each control
        compliant_controls = 0
        non_compliant_controls = 0
        pending_controls = 0
        
        findings = []
        
        for control in required_controls:
            status = controls.get(control, "unknown").lower()
            
            if status == "compliant":
                compliant_controls += 1
            elif status == "non_compliant":
                non_compliant_controls += 1
                findings.append({
                    "control": control,
                    "status": "non_compliant",
                    "severity": self._determine_control_severity(control)
                })
            else:
                pending_controls += 1
        
        # Calculate compliance percentage
        total_controls = len(required_controls)
        compliance_percentage = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
        
        # Determine overall compliance level
        compliance_level = self._determine_compliance_level(compliance_percentage)
        
        result = {
            "validation_id": validation_id,
            "timestamp": timestamp,
            "system_name": system_name,
            "framework": framework,
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "non_compliant_controls": non_compliant_controls,
            "pending_controls": pending_controls,
            "compliance_percentage": compliance_percentage,
            "compliance_level": compliance_level,
            "findings": findings
        }
        
        self.validation_results.append(result)
        self.system_controls[system_name] = controls
        
        logger.info(f"Compliance validation for {system_name}: {compliance_percentage:.1f}% compliant")
        
        return result
    
    def cross_framework_validation(self,
                                  system_name: str,
                                  frameworks: List[str],
                                  controls: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """Validate system across multiple frameworks."""
        
        results = {}
        for framework in frameworks:
            framework_controls = controls.get(framework, {})
            results[framework] = self.validate_system_compliance(system_name, framework, framework_controls)
        
        # Calculate cross-framework compliance score
        scores = [r["compliance_percentage"] for r in results.values()]
        overall_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "system_name": system_name,
            "frameworks_validated": frameworks,
            "results": results,
            "overall_compliance_percentage": overall_score,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_system_compliance_trend(self, system_name: str) -> List[Dict[str, Any]]:
        """Get compliance trend for a system over time."""
        return [r for r in self.validation_results if r["system_name"] == system_name]
    
    def _load_frameworks(self) -> Dict[str, List[str]]:
        """Load framework requirements."""
        return {
            "gdpr": [
                "lawful_basis",
                "data_protection",
                "privacy_by_design",
                "data_subject_rights",
                "dpia",
                "security_measures",
                "incident_response"
            ],
            "hipaa": [
                "access_controls",
                "audit_controls",
                "integrity_controls",
                "transmission_security",
                "administrative_safeguards",
                "physical_safeguards",
                "technical_safeguards"
            ],
            "soc2": [
                "access_controls",
                "change_management",
                "monitoring",
                "incident_response",
                "system_availability",
                "processing_integrity"
            ],
            "iso27001": [
                "information_security_policies",
                "access_control",
                "cryptography",
                "physical_security",
                "operations_security",
                "communications_security",
                "system_acquisition"
            ],
            "pci_dss": [
                "firewall_configuration",
                "default_passwords",
                "data_protection",
                "vulnerability_management",
                "access_control",
                "vulnerability_testing",
                "security_policy"
            ],
            "nist": [
                "identify",
                "protect",
                "detect",
                "respond",
                "recover"
            ]
        }
    
    def _determine_compliance_level(self, percentage: float) -> str:
        """Determine compliance level from percentage."""
        if percentage >= 95:
            return ComplianceLevel.FULL.value
        elif percentage >= 75:
            return ComplianceLevel.SUBSTANTIAL.value
        elif percentage >= 50:
            return ComplianceLevel.PARTIAL.value
        elif percentage > 0:
            return ComplianceLevel.MINIMAL.value
        else:
            return ComplianceLevel.NONE.value
    
    def _determine_control_severity(self, control: str) -> str:
        """Determine severity of a control gap."""
        critical_controls = ["access_controls", "encryption", "authentication", "audit"]
        
        if any(critical in control.lower() for critical in critical_controls):
            return "critical"
        elif "security" in control.lower():
            return "high"
        else:
            return "medium"
    
    def _generate_validation_id(self, system: str, framework: str, timestamp: str) -> str:
        """Generate unique validation ID."""
        import hashlib
        content = f"{system}:{framework}:{timestamp}".encode()
        return hashlib.sha256(content).hexdigest()[:12]


class ComplianceGapAnalyzer:
    """Analyzes and tracks compliance gaps."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.gaps: List[ComplianceGap] = []
        self.gap_mappings: Dict[str, str] = {}
    
    def identify_gaps(self,
                     framework: str,
                     current_state: Dict[str, str],
                     required_state: Dict[str, str]) -> List[ComplianceGap]:
        """Identify gaps between current and required state."""
        
        identified_gaps = []
        
        for requirement, required_status in required_state.items():
            current_status = current_state.get(requirement, "none")
            
            if current_status != required_status:
                gap = self._create_gap(
                    framework, requirement, current_status, required_status
                )
                identified_gaps.append(gap)
                self.gaps.append(gap)
        
        logger.info(f"Identified {len(identified_gaps)} compliance gaps for {framework}")
        return identified_gaps
    
    def prioritize_gaps(self) -> List[ComplianceGap]:
        """Get gaps sorted by severity and impact."""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        return sorted(
            self.gaps,
            key=lambda x: (severity_order.get(x.severity, 99), len(x.affected_systems)),
            reverse=False
        )
    
    def get_gaps_by_framework(self, framework: str) -> List[ComplianceGap]:
        """Get all gaps for a specific framework."""
        return [g for g in self.gaps if g.framework.lower() == framework.lower()]
    
    def get_gaps_by_system(self, system_name: str) -> List[ComplianceGap]:
        """Get all gaps affecting a specific system."""
        return [g for g in self.gaps if system_name in g.affected_systems]
    
    def get_critical_gaps(self) -> List[ComplianceGap]:
        """Get all critical compliance gaps."""
        return [g for g in self.gaps if g.severity.lower() == "critical"]
    
    def _create_gap(self,
                   framework: str,
                   requirement: str,
                   current: str,
                   required: str) -> ComplianceGap:
        """Create a compliance gap record."""
        import hashlib
        
        gap_id = hashlib.sha256(f"{framework}:{requirement}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]
        
        severity = self._assess_gap_severity(requirement, current, required)
        
        return ComplianceGap(
            gap_id=gap_id,
            framework=framework,
            requirement=requirement,
            current_status=current,
            required_status=required,
            severity=severity,
            affected_systems=[]
        )
    
    def _assess_gap_severity(self, requirement: str, current: str, required: str) -> str:
        """Assess gap severity."""
        critical_keywords = ["access", "encryption", "authentication", "security"]
        
        if current == "none" and required == "compliant":
            if any(kw in requirement.lower() for kw in critical_keywords):
                return "critical"
            return "high"
        elif current == "partial":
            return "medium"
        else:
            return "low"


class RemediationTracker:
    """Tracks remediation actions and progress."""
    
    def __init__(self):
        """Initialize tracker."""
        self.actions: List[RemediationAction] = []
        self.progress_history: List[Dict[str, Any]] = []
    
    def create_remediation_action(self,
                                 gap_id: str,
                                 action_title: str,
                                 description: str,
                                 assigned_to: Optional[str] = None,
                                 due_date: Optional[str] = None) -> RemediationAction:
        """Create a remediation action for a gap."""
        
        import hashlib
        action_id = hashlib.sha256(f"{gap_id}:{action_title}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]
        
        action = RemediationAction(
            action_id=action_id,
            gap_id=gap_id,
            action_title=action_title,
            description=description,
            assigned_to=assigned_to,
            due_date=due_date,
            status="pending",
            completion_percentage=0.0
        )
        
        self.actions.append(action)
        logger.info(f"Remediation action created: {action_title} ({action_id})")
        
        return action
    
    def update_action_status(self,
                           action_id: str,
                           status: str,
                           completion_percentage: float = None) -> bool:
        """Update remediation action status."""
        
        for action in self.actions:
            if action.action_id == action_id:
                action.status = status
                if completion_percentage is not None:
                    action.completion_percentage = min(100, max(0, completion_percentage))
                
                logger.info(f"Action {action_id} updated to {status} "
                           f"({action.completion_percentage:.0f}% complete)")
                return True
        
        return False
    
    def get_open_actions(self) -> List[RemediationAction]:
        """Get all open remediation actions."""
        return [a for a in self.actions if a.status in ["pending", "in_progress"]]
    
    def get_overdue_actions(self) -> List[RemediationAction]:
        """Get overdue remediation actions."""
        overdue = []
        current_date = datetime.utcnow().date()
        
        for action in self.actions:
            if action.due_date and action.status != "completed":
                due_date = datetime.fromisoformat(action.due_date).date()
                if due_date < current_date:
                    overdue.append(action)
        
        return overdue
    
    def get_action_progress(self) -> Dict[str, Any]:
        """Get overall remediation progress."""
        if not self.actions:
            return {"total": 0, "completed": 0, "in_progress": 0, "pending": 0, "blocked": 0}
        
        completed = len([a for a in self.actions if a.status == "completed"])
        in_progress = len([a for a in self.actions if a.status == "in_progress"])
        pending = len([a for a in self.actions if a.status == "pending"])
        blocked = len([a for a in self.actions if a.status == "blocked"])
        
        return {
            "total": len(self.actions),
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "blocked": blocked,
            "completion_percentage": (completed / len(self.actions) * 100) if self.actions else 0
        }


class FrameworkMappingEngine:
    """Maps and translates controls between compliance frameworks."""
    
    def __init__(self):
        """Initialize engine."""
        self.mappings: List[FrameworkMappingRule] = []
        self._initialize_mappings()
    
    def get_mapping(self,
                   source_framework: str,
                   source_control: str,
                   target_framework: str) -> Optional[FrameworkMappingRule]:
        """Get mapping between frameworks."""
        
        for mapping in self.mappings:
            if (mapping.source_framework.lower() == source_framework.lower() and
                mapping.source_control.lower() == source_control.lower() and
                mapping.target_framework.lower() == target_framework.lower()):
                return mapping
        
        return None
    
    def get_mapped_controls(self,
                           source_framework: str,
                           target_framework: str) -> Dict[str, str]:
        """Get all control mappings between two frameworks."""
        
        mappings = {}
        for mapping in self.mappings:
            if (mapping.source_framework.lower() == source_framework.lower() and
                mapping.target_framework.lower() == target_framework.lower()):
                mappings[mapping.source_control] = mapping.target_control
        
        return mappings
    
    def assess_control_compatibility(self,
                                    control_implementation: Dict[str, Any]) -> Dict[str, str]:
        """Assess how a control implementation aligns with different frameworks."""
        
        compatibility = {}
        # Implementation logic would map control to frameworks
        return compatibility
    
    def _initialize_mappings(self):
        """Initialize cross-framework mappings."""
        # Example mappings
        sample_mappings = [
            FrameworkMappingRule(
                "gdpr", "iso27001",
                "data_protection", "cryptography",
                "partial", "GDPR data protection aligns with ISO encryption controls"
            ),
            FrameworkMappingRule(
                "hipaa", "soc2",
                "access_controls", "access_controls",
                "full", "Direct alignment between HIPAA and SOC2 access requirements"
            ),
        ]
        self.mappings.extend(sample_mappings)


# Module-level instances
_validator = ComplianceValidator()
_gap_analyzer = ComplianceGapAnalyzer()
_remediation_tracker = RemediationTracker()
_mapping_engine = FrameworkMappingEngine()


# Module-level wrapper functions
def validate_system(system_name: str,
                   framework: str,
                   controls: Dict[str, str]) -> Dict[str, Any]:
    """Wrapper to validate system compliance."""
    return _validator.validate_system_compliance(system_name, framework, controls)


def identify_gaps(framework: str,
                 current_state: Dict[str, str],
                 required_state: Dict[str, str]) -> List[Dict[str, Any]]:
    """Wrapper to identify compliance gaps."""
    gaps = _gap_analyzer.identify_gaps(framework, current_state, required_state)
    return [g.to_dict() for g in gaps]


def create_remediation(gap_id: str,
                      action_title: str,
                      description: str) -> Dict[str, Any]:
    """Wrapper to create remediation action."""
    action = _remediation_tracker.create_remediation_action(gap_id, action_title, description)
    return action.to_dict()


def get_remediation_progress() -> Dict[str, Any]:
    """Wrapper to get remediation progress."""
    return _remediation_tracker.get_action_progress()


def get_framework_mapping(source_framework: str,
                         source_control: str,
                         target_framework: str) -> Optional[Dict[str, Any]]:
    """Wrapper to get framework mapping."""
    mapping = _mapping_engine.get_mapping(source_framework, source_control, target_framework)
    return asdict(mapping) if mapping else None
