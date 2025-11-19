"""
PHASE 6: Change Detection & Classification Engine

Detects and classifies regulatory changes:
- New requirements added
- Existing requirements modified
- Requirements removed
- Severity assessment
- Impact analysis

Part of IRAQAF Phase 6 - Change Monitoring System
Integrated with Phase 2 (Database), Phase 4 (NLP), Phase 5 (Scoring)
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import difflib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeverityLevel(str, Enum):
    """Change severity classification"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ChangeType(str, Enum):
    """Type of regulatory change detected"""
    NEW_REQUIREMENT = "NEW_REQUIREMENT"
    REQUIREMENT_MODIFIED = "REQUIREMENT_MODIFIED"
    REQUIREMENT_REMOVED = "REQUIREMENT_REMOVED"
    REQUIREMENT_CLARIFIED = "REQUIREMENT_CLARIFIED"
    DEADLINE_CHANGED = "DEADLINE_CHANGED"
    PENALTY_CHANGED = "PENALTY_CHANGED"


@dataclass
class Change:
    """Represents a detected regulatory change"""
    change_id: str
    regulation: str
    requirement_id: str
    change_type: ChangeType
    severity: SeverityLevel
    old_value: Optional[str]
    new_value: str
    detected_date: datetime
    description: str
    affected_systems: List[str]
    compliance_impact: str  # How this affects compliance
    recommended_action: str
    estimated_remediation_hours: float
    estimated_remediation_cost: float


@dataclass
class ChangeDetectionResult:
    """Result of change detection analysis"""
    detection_date: datetime
    total_changes: int
    critical_changes: int
    high_changes: int
    medium_changes: int
    low_changes: int
    changes: List[Change]
    summary: str


class ChangeDetector:
    """
    Detects regulatory changes by comparing current vs previous content.
    Uses hash-based change detection and semantic analysis.
    """

    def __init__(self):
        """Initialize change detector"""
        self.change_history = []
        self.requirement_hashes = {}
        self.regulations = [
            "EU AI Act",
            "GDPR",
            "ISO 13485",
            "IEC 62304",
            "FDA"
        ]

    def compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def detect_requirement_changes(
        self,
        regulation: str,
        previous_requirements: Dict[str, str],
        current_requirements: Dict[str, str]
    ) -> List[Change]:
        """
        Detect changes in requirements by comparing previous vs current state.

        Args:
            regulation: Regulation name (e.g., "GDPR")
            previous_requirements: Dict of {requirement_id: content}
            current_requirements: Dict of {requirement_id: content}

        Returns:
            List of detected changes
        """
        changes = []

        # Detect NEW requirements
        for req_id, content in current_requirements.items():
            if req_id not in previous_requirements:
                changes.append(
                    self._classify_new_requirement(
                        regulation, req_id, content
                    )
                )

        # Detect MODIFIED requirements
        for req_id, old_content in previous_requirements.items():
            if req_id in current_requirements:
                new_content = current_requirements[req_id]
                if old_content != new_content:
                    changes.append(
                        self._classify_modified_requirement(
                            regulation, req_id, old_content, new_content
                        )
                    )

        # Detect REMOVED requirements
        for req_id in previous_requirements:
            if req_id not in current_requirements:
                changes.append(
                    self._classify_removed_requirement(
                        regulation, req_id,
                        previous_requirements[req_id]
                    )
                )

        return changes

    def _classify_new_requirement(
        self,
        regulation: str,
        requirement_id: str,
        content: str
    ) -> Change:
        """Classify a newly added requirement"""
        severity = self._assess_requirement_severity(content)
        
        return Change(
            change_id=f"CHG-NEW-{requirement_id}-{datetime.now().timestamp()}",
            regulation=regulation,
            requirement_id=requirement_id,
            change_type=ChangeType.NEW_REQUIREMENT,
            severity=severity,
            old_value=None,
            new_value=content,
            detected_date=datetime.now(),
            description=f"New requirement added to {regulation}",
            affected_systems=self._identify_affected_systems(regulation),
            compliance_impact=self._assess_compliance_impact(
                regulation, content
            ),
            recommended_action=f"Review and implement new requirement: {requirement_id}",
            estimated_remediation_hours=self._estimate_remediation_hours(
                severity, "new"
            ),
            estimated_remediation_cost=self._estimate_remediation_cost(
                severity, "new"
            )
        )

    def _classify_modified_requirement(
        self,
        regulation: str,
        requirement_id: str,
        old_content: str,
        new_content: str
    ) -> Change:
        """Classify a modified requirement"""
        severity = self._assess_modification_severity(
            old_content, new_content
        )
        modification_type = self._identify_modification_type(
            old_content, new_content
        )
        
        return Change(
            change_id=f"CHG-MOD-{requirement_id}-{datetime.now().timestamp()}",
            regulation=regulation,
            requirement_id=requirement_id,
            change_type=modification_type,
            severity=severity,
            old_value=old_content,
            new_value=new_content,
            detected_date=datetime.now(),
            description=f"Requirement modified: {modification_type.value}",
            affected_systems=self._identify_affected_systems(regulation),
            compliance_impact=self._assess_compliance_impact(
                regulation, new_content
            ),
            recommended_action=f"Update implementation for: {requirement_id}",
            estimated_remediation_hours=self._estimate_remediation_hours(
                severity, "modify"
            ),
            estimated_remediation_cost=self._estimate_remediation_cost(
                severity, "modify"
            )
        )

    def _classify_removed_requirement(
        self,
        regulation: str,
        requirement_id: str,
        content: str
    ) -> Change:
        """Classify a removed requirement"""
        severity = self._assess_removal_severity(content)
        
        return Change(
            change_id=f"CHG-REM-{requirement_id}-{datetime.now().timestamp()}",
            regulation=regulation,
            requirement_id=requirement_id,
            change_type=ChangeType.REQUIREMENT_REMOVED,
            severity=severity,
            old_value=content,
            new_value=None,
            detected_date=datetime.now(),
            description=f"Requirement removed from {regulation}",
            affected_systems=self._identify_affected_systems(regulation),
            compliance_impact="Removed requirement no longer applicable",
            recommended_action=f"Retire implementation for: {requirement_id}",
            estimated_remediation_hours=self._estimate_remediation_hours(
                severity, "remove"
            ),
            estimated_remediation_cost=self._estimate_remediation_cost(
                severity, "remove"
            )
        )

    def _assess_requirement_severity(self, content: str) -> SeverityLevel:
        """Assess severity of new requirement"""
        content_lower = content.lower()
        
        # Critical keywords
        critical_keywords = [
            "mandatory", "must", "shall", "required",
            "critical", "breach", "violation", "penalty",
            "non-compliance", "enforcement"
        ]
        
        # High keywords
        high_keywords = [
            "important", "should", "recommended",
            "best practice", "guideline", "significant"
        ]
        
        critical_count = sum(
            1 for kw in critical_keywords
            if kw in content_lower
        )
        high_count = sum(
            1 for kw in high_keywords
            if kw in content_lower
        )
        
        if critical_count >= 2:
            return SeverityLevel.CRITICAL
        elif critical_count >= 1 or high_count >= 2:
            return SeverityLevel.HIGH
        elif high_count >= 1:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW

    def _assess_modification_severity(
        self,
        old_content: str,
        new_content: str
    ) -> SeverityLevel:
        """Assess severity of requirement modification"""
        # Compare similarity
        similarity = difflib.SequenceMatcher(
            None, old_content, new_content
        ).ratio()
        
        if similarity < 0.5:
            # Major change
            return SeverityLevel.CRITICAL
        elif similarity < 0.75:
            # Significant change
            return SeverityLevel.HIGH
        elif similarity < 0.9:
            # Minor change
            return SeverityLevel.MEDIUM
        else:
            # Cosmetic change
            return SeverityLevel.LOW

    def _assess_removal_severity(self, content: str) -> SeverityLevel:
        """Assess severity of requirement removal"""
        content_lower = content.lower()
        
        if any(kw in content_lower for kw in ["mandatory", "must"]):
            return SeverityLevel.CRITICAL
        elif any(kw in content_lower for kw in ["important", "should"]):
            return SeverityLevel.HIGH
        else:
            return SeverityLevel.MEDIUM

    def _identify_modification_type(
        self,
        old_content: str,
        new_content: str
    ) -> ChangeType:
        """Identify what type of modification occurred"""
        old_lower = old_content.lower()
        new_lower = new_content.lower()
        
        # Check if deadline changed
        if any(date_kw in old_lower for date_kw in ["2024", "2025", "2026"]):
            if any(date_kw in new_lower for date_kw in ["2024", "2025", "2026"]):
                if old_lower != new_lower:
                    return ChangeType.DEADLINE_CHANGED
        
        # Check if penalty changed
        if any(kw in old_lower for kw in ["fine", "penalty", "punishment"]):
            if any(kw in new_lower for kw in ["fine", "penalty", "punishment"]):
                return ChangeType.PENALTY_CHANGED
        
        # Check if clarified
        if len(new_content) > len(old_content) * 1.2:
            return ChangeType.REQUIREMENT_CLARIFIED
        
        return ChangeType.REQUIREMENT_MODIFIED

    def _identify_affected_systems(self, regulation: str) -> List[str]:
        """Identify systems affected by this regulation"""
        regulation_systems = {
            "EU AI Act": ["AI Models", "Data Pipeline", "Decision Systems"],
            "GDPR": ["Data Storage", "User Management", "Privacy Controls"],
            "ISO 13485": ["Device Software", "QA Process", "Documentation"],
            "IEC 62304": ["Medical Device", "Software Development", "Testing"],
            "FDA": ["FDA Compliance", "Regulatory", "Quality Systems"]
        }
        return regulation_systems.get(regulation, ["General"])

    def _assess_compliance_impact(
        self,
        regulation: str,
        content: str
    ) -> str:
        """Assess how this change impacts compliance"""
        content_lower = content.lower()
        
        if "data" in content_lower or "privacy" in content_lower:
            return "Impacts data handling and privacy compliance"
        elif "security" in content_lower:
            return "Impacts security requirements and safeguards"
        elif "documentation" in content_lower:
            return "Requires documentation updates"
        elif "testing" in content_lower:
            return "Requires additional testing"
        elif "audit" in content_lower:
            return "Requires audit trail maintenance"
        else:
            return "General compliance requirement"

    def _estimate_remediation_hours(
        self,
        severity: SeverityLevel,
        change_type: str
    ) -> float:
        """Estimate hours needed to remediate change"""
        base_hours = {
            "new": 40,
            "modify": 20,
            "remove": 10
        }.get(change_type, 30)
        
        multipliers = {
            SeverityLevel.CRITICAL: 2.0,
            SeverityLevel.HIGH: 1.5,
            SeverityLevel.MEDIUM: 1.0,
            SeverityLevel.LOW: 0.5
        }
        
        return base_hours * multipliers.get(severity, 1.0)

    def _estimate_remediation_cost(
        self,
        severity: SeverityLevel,
        change_type: str
    ) -> float:
        """Estimate cost to remediate change"""
        hourly_rate = 150  # Developer rate
        hours = self._estimate_remediation_hours(severity, change_type)
        return hours * hourly_rate

    def analyze_changes(
        self,
        regulation: str,
        previous_requirements: Dict[str, str],
        current_requirements: Dict[str, str]
    ) -> ChangeDetectionResult:
        """
        Analyze changes and generate detection report.

        Returns:
            ChangeDetectionResult with all detected changes
        """
        changes = self.detect_requirement_changes(
            regulation,
            previous_requirements,
            current_requirements
        )
        
        # Count by severity
        severity_counts = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 0,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.LOW: 0
        }
        
        for change in changes:
            severity_counts[change.severity] += 1
        
        # Generate summary
        summary = self._generate_summary(regulation, changes, severity_counts)
        
        return ChangeDetectionResult(
            detection_date=datetime.now(),
            total_changes=len(changes),
            critical_changes=severity_counts[SeverityLevel.CRITICAL],
            high_changes=severity_counts[SeverityLevel.HIGH],
            medium_changes=severity_counts[SeverityLevel.MEDIUM],
            low_changes=severity_counts[SeverityLevel.LOW],
            changes=changes,
            summary=summary
        )

    def _generate_summary(
        self,
        regulation: str,
        changes: List[Change],
        severity_counts: Dict
    ) -> str:
        """Generate human-readable summary of changes"""
        if not changes:
            return f"No changes detected in {regulation}"
        
        summary_parts = [
            f"{len(changes)} changes detected in {regulation}:",
            f"  • {severity_counts[SeverityLevel.CRITICAL]} CRITICAL",
            f"  • {severity_counts[SeverityLevel.HIGH]} HIGH",
            f"  • {severity_counts[SeverityLevel.MEDIUM]} MEDIUM",
            f"  • {severity_counts[SeverityLevel.LOW]} LOW"
        ]
        
        if severity_counts[SeverityLevel.CRITICAL] > 0:
            summary_parts.append(
                "\n⚠️  IMMEDIATE ACTION REQUIRED: Critical changes detected"
            )
        elif severity_counts[SeverityLevel.HIGH] > 0:
            summary_parts.append(
                "\n⚠️  URGENT: High-severity changes require planning"
            )
        
        return "\n".join(summary_parts)

    def export_changes_to_json(
        self,
        result: ChangeDetectionResult
    ) -> str:
        """Export detection result to JSON format"""
        changes_dict = [asdict(change) for change in result.changes]
        
        # Convert datetime objects to ISO format strings
        for change in changes_dict:
            change['detected_date'] = change['detected_date'].isoformat()
            change['change_type'] = change['change_type'].value
            change['severity'] = change['severity'].value
        
        result_dict = {
            'detection_date': result.detection_date.isoformat(),
            'total_changes': result.total_changes,
            'critical_changes': result.critical_changes,
            'high_changes': result.high_changes,
            'medium_changes': result.medium_changes,
            'low_changes': result.low_changes,
            'summary': result.summary,
            'changes': changes_dict
        }
        
        return json.dumps(result_dict, indent=2)


# Example usage
if __name__ == "__main__":
    detector = ChangeDetector()
    
    # Sample requirements
    previous_reqs = {
        "GDPR-1": "Organizations must implement data protection measures",
        "GDPR-2": "Data subjects have the right to be forgotten",
        "GDPR-3": "DPA must be notified within 72 hours of breach"
    }
    
    current_reqs = {
        "GDPR-1": "Organizations must implement advanced data protection measures",
        "GDPR-2": "Data subjects have the right to be forgotten",
        "GDPR-4": "Organizations must conduct DPIA for high-risk processing",
        "GDPR-5": "Annual compliance audits are now mandatory"
    }
    
    result = detector.analyze_changes("GDPR", previous_reqs, current_reqs)
    
    print("\n" + "="*70)
    print("CHANGE DETECTION REPORT")
    print("="*70)
    print(f"\n{result.summary}\n")
    
    for change in result.changes:
        print(f"\n{change.change_type.value}")
        print(f"  Requirement: {change.requirement_id}")
        print(f"  Severity: {change.severity.value}")
        print(f"  Impact: {change.compliance_impact}")
        print(f"  Remediation: {change.estimated_remediation_hours} hours (${change.estimated_remediation_cost:.0f})")
    
    print("\n" + "="*70)
    print("\nJSON Export Sample:")
    print(result.export_changes_to_json()[:500] + "...")
