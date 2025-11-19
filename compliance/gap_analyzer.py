"""
PHASE 5: GAP ANALYSIS ENGINE
Identifies and analyzes compliance gaps with remediation strategies

Features:
  - Automatic gap identification (score < 50)
  - Gap classification: Critical, High, Medium, Low
  - Remediation effort quantification
  - Timeline estimation
  - Cost estimation
  - Risk mitigation strategies
  - Prioritized action plans
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GapSeverity(Enum):
    """Gap severity levels"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class RemediationType(Enum):
    """Types of remediation actions"""
    DOCUMENTATION = "documentation"
    POLICY_CREATION = "policy_creation"
    IMPLEMENTATION = "implementation"
    TRAINING = "training"
    PROCESS_REDESIGN = "process_redesign"
    TECHNOLOGY_UPGRADE = "technology_upgrade"
    THIRD_PARTY = "third_party_service"


@dataclass
class RemediationAction:
    """Action to remediate a gap"""
    action_id: str
    action_type: RemediationType
    description: str
    estimated_hours: int
    estimated_cost: float
    dependencies: List[str] = field(default_factory=list)
    timeline_days: int = 30
    owner_role: str = "Compliance Officer"
    success_metrics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "action_id": self.action_id,
            "type": self.action_type.value,
            "description": self.description,
            "estimated_hours": self.estimated_hours,
            "estimated_cost": self.estimated_cost,
            "timeline_days": self.timeline_days,
            "owner_role": self.owner_role,
            "dependencies": self.dependencies,
            "success_metrics": self.success_metrics
        }


@dataclass
class ComplianceGap:
    """Represents a compliance gap"""
    gap_id: str
    requirement_id: str
    requirement_text: str
    regulation: str
    current_score: float  # 0-100
    target_score: float  # 0-100 (usually 100)
    gap_size: float  # target - current
    severity: GapSeverity
    root_cause: str
    impact_description: str
    remediation_actions: List[RemediationAction] = field(default_factory=list)
    identified_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "gap_id": self.gap_id,
            "requirement_id": self.requirement_id,
            "requirement_text": self.requirement_text[:100],
            "regulation": self.regulation,
            "current_score": round(self.current_score, 2),
            "target_score": self.target_score,
            "gap_size": round(self.gap_size, 2),
            "severity": self.severity.name,
            "root_cause": self.root_cause,
            "impact": self.impact_description[:150],
            "remediation_count": len(self.remediation_actions),
            "total_remediation_hours": sum(a.estimated_hours for a in self.remediation_actions),
            "total_remediation_cost": sum(a.estimated_cost for a in self.remediation_actions),
            "identified_date": self.identified_date.isoformat()
        }


class GapAnalyzer:
    """Gap analysis engine"""
    
    def __init__(self):
        """Initialize gap analyzer"""
        self.gaps: Dict[str, ComplianceGap] = {}
        self.remediation_library = self._load_remediation_library()
    
    def _load_remediation_library(self) -> Dict:
        """Load standard remediation actions"""
        return {
            "doc_creation": {
                "type": RemediationType.DOCUMENTATION,
                "hours": 40,
                "cost": 2000,
                "timeline_days": 14
            },
            "policy_dev": {
                "type": RemediationType.POLICY_CREATION,
                "hours": 60,
                "cost": 3000,
                "timeline_days": 21
            },
            "implement": {
                "type": RemediationType.IMPLEMENTATION,
                "hours": 120,
                "cost": 6000,
                "timeline_days": 45
            },
            "training": {
                "type": RemediationType.TRAINING,
                "hours": 30,
                "cost": 1500,
                "timeline_days": 14
            },
            "process_redesign": {
                "type": RemediationType.PROCESS_REDESIGN,
                "hours": 100,
                "cost": 5000,
                "timeline_days": 30
            },
            "tech_upgrade": {
                "type": RemediationType.TECHNOLOGY_UPGRADE,
                "hours": 150,
                "cost": 15000,
                "timeline_days": 60
            }
        }
    
    def identify_gaps(
        self,
        requirement_scores: Dict,
        gap_threshold: float = 50.0
    ) -> List[ComplianceGap]:
        """
        Identify gaps from requirement scores
        
        Args:
            requirement_scores: Dict of requirement IDs to scores
            gap_threshold: Score below which is considered a gap
        
        Returns:
            List of identified gaps
        """
        
        identified_gaps = []
        
        for req_id, score_obj in requirement_scores.items():
            if score_obj.compliance_score < gap_threshold:
                # Determine gap severity
                gap_size = gap_threshold - score_obj.compliance_score
                severity = self._determine_severity(gap_size, score_obj.risk_level.value)
                
                # Determine root cause
                root_cause = self._analyze_root_cause(score_obj)
                
                # Determine impact
                impact = self._determine_impact(severity, score_obj.regulation)
                
                # Create gap
                gap_id = f"GAP-{req_id}-{datetime.now().strftime('%Y%m%d')}"
                gap = ComplianceGap(
                    gap_id=gap_id,
                    requirement_id=req_id,
                    requirement_text=score_obj.requirement_text,
                    regulation=score_obj.regulation,
                    current_score=score_obj.compliance_score,
                    target_score=100.0,
                    gap_size=gap_size,
                    severity=severity,
                    root_cause=root_cause,
                    impact_description=impact
                )
                
                self.gaps[gap_id] = gap
                identified_gaps.append(gap)
                logger.info(f"Identified gap {gap_id}: {severity.name} severity")
        
        return identified_gaps
    
    def _determine_severity(
        self,
        gap_size: float,
        risk_level: int
    ) -> GapSeverity:
        """Determine gap severity from size and risk"""
        combined_score = gap_size + (risk_level * 15)
        
        if combined_score >= 60:
            return GapSeverity.CRITICAL
        elif combined_score >= 45:
            return GapSeverity.HIGH
        elif combined_score >= 30:
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW
    
    def _analyze_root_cause(self, score_obj) -> str:
        """Analyze root cause of gap"""
        if not score_obj.evidence_list:
            return "Lack of evidence/documentation"
        
        if score_obj.confidence < 0.5:
            return "Low confidence in existing evidence"
        
        avg_quality = statistics.mean([e.quality_score for e in score_obj.evidence_list])
        if avg_quality < 60:
            return "Poor quality evidence"
        
        if len(score_obj.evidence_list) < 2:
            return "Insufficient evidence diversity"
        
        return "Partial implementation"
    
    def _determine_impact(self, severity: GapSeverity, regulation: str) -> str:
        """Determine business impact of gap"""
        impact_map = {
            GapSeverity.CRITICAL: "Immediate regulatory violation and fines",
            GapSeverity.HIGH: "Significant compliance risk and potential penalties",
            GapSeverity.MEDIUM: "Moderate compliance risk and improvement needed",
            GapSeverity.LOW: "Minor gap, monitoring recommended"
        }
        
        base_impact = impact_map[severity]
        
        if regulation in ["EU-AI-Act", "GDPR", "FDA"]:
            return f"{base_impact} in {regulation} (High Priority Regulation)"
        
        return base_impact
    
    def generate_remediation_plan(
        self,
        gap: ComplianceGap
    ) -> List[RemediationAction]:
        """
        Generate remediation plan for a gap
        
        Args:
            gap: ComplianceGap to remediate
        
        Returns:
            List of remediation actions
        """
        
        actions = []
        
        # Determine remediation actions based on severity and root cause
        if gap.severity == GapSeverity.CRITICAL:
            # Critical gaps need comprehensive approach
            actions.extend([
                self._create_action("RAC-01", RemediationType.DOCUMENTATION, gap),
                self._create_action("RAC-02", RemediationType.POLICY_CREATION, gap),
                self._create_action("RAC-03", RemediationType.IMPLEMENTATION, gap)
            ])
        elif gap.severity == GapSeverity.HIGH:
            actions.extend([
                self._create_action("RAH-01", RemediationType.DOCUMENTATION, gap),
                self._create_action("RAH-02", RemediationType.IMPLEMENTATION, gap)
            ])
        elif gap.severity == GapSeverity.MEDIUM:
            actions.append(
                self._create_action("RAM-01", RemediationType.DOCUMENTATION, gap)
            )
        else:  # LOW
            actions.append(
                self._create_action("RAL-01", RemediationType.TRAINING, gap)
            )
        
        # Add training for all
        actions.append(
            self._create_action("TRN-01", RemediationType.TRAINING, gap)
        )
        
        gap.remediation_actions = actions
        logger.info(f"Generated {len(actions)} remediation actions for {gap.gap_id}")
        
        return actions
    
    def _create_action(
        self,
        action_id: str,
        action_type: RemediationType,
        gap: ComplianceGap
    ) -> RemediationAction:
        """Create a remediation action"""
        
        lib_key = {
            RemediationType.DOCUMENTATION: "doc_creation",
            RemediationType.POLICY_CREATION: "policy_dev",
            RemediationType.IMPLEMENTATION: "implement",
            RemediationType.TRAINING: "training",
            RemediationType.PROCESS_REDESIGN: "process_redesign",
            RemediationType.TECHNOLOGY_UPGRADE: "tech_upgrade"
        }.get(action_type, "doc_creation")
        
        lib_action = self.remediation_library[lib_key]
        
        # Adjust effort based on gap severity
        severity_multiplier = 1.0 + (gap.severity.value * 0.15)
        hours = int(lib_action["hours"] * severity_multiplier)
        cost = lib_action["cost"] * severity_multiplier
        
        return RemediationAction(
            action_id=action_id,
            action_type=action_type,
            description=f"{action_type.value.replace('_', ' ').title()} for {gap.requirement_id}",
            estimated_hours=hours,
            estimated_cost=cost,
            timeline_days=lib_action["timeline_days"],
            success_metrics=[
                f"Evidence quality score > 85",
                f"Compliance score increased to {min(100, gap.current_score + 40)}"
            ]
        )
    
    def get_portfolio_gap_summary(self) -> Dict:
        """Get overall gap portfolio summary"""
        
        if not self.gaps:
            return {"status": "No gaps identified"}
        
        gaps_list = list(self.gaps.values())
        
        # Severity distribution
        severity_dist = {}
        for severity in GapSeverity:
            count = sum(1 for g in gaps_list if g.severity == severity)
            percentage = (count / len(gaps_list)) * 100 if gaps_list else 0
            severity_dist[severity.name] = {
                "count": count,
                "percentage": round(percentage, 1)
            }
        
        # Remediation totals
        total_hours = sum(
            sum(a.estimated_hours for a in g.remediation_actions)
            for g in gaps_list if g.remediation_actions
        )
        total_cost = sum(
            sum(a.estimated_cost for a in g.remediation_actions)
            for g in gaps_list if g.remediation_actions
        )
        
        # Timeline estimation (critical path)
        max_timeline = max(
            (max(a.timeline_days for a in g.remediation_actions) if g.remediation_actions else 0)
            for g in gaps_list
        )
        
        # Regulation breakdown
        reg_gap_counts = {}
        for g in gaps_list:
            if g.regulation not in reg_gap_counts:
                reg_gap_counts[g.regulation] = 0
            reg_gap_counts[g.regulation] += 1
        
        return {
            "total_gaps": len(gaps_list),
            "severity_distribution": severity_dist,
            "critical_gaps": severity_dist[GapSeverity.CRITICAL.name]["count"],
            "high_gaps": severity_dist[GapSeverity.HIGH.name]["count"],
            "total_remediation_hours": total_hours,
            "total_remediation_cost": round(total_cost, 2),
            "estimated_timeline_days": max_timeline,
            "regulation_breakdown": reg_gap_counts,
            "avg_gap_size": round(statistics.mean([g.gap_size for g in gaps_list]), 2),
            "summary_timestamp": datetime.now().isoformat()
        }
    
    def get_prioritized_action_plan(self, max_actions: Optional[int] = None) -> List[Dict]:
        """
        Get prioritized action plan across all gaps
        
        Args:
            max_actions: Maximum number of actions to return
        
        Returns:
            Prioritized list of actions
        """
        
        all_actions = []
        
        for gap in self.gaps.values():
            if not gap.remediation_actions:
                self.generate_remediation_plan(gap)
            
            for action in gap.remediation_actions:
                priority = self._calculate_action_priority(gap, action)
                all_actions.append({
                    "priority": priority,
                    "gap_id": gap.gap_id,
                    "requirement_id": gap.requirement_id,
                    "action": action.to_dict()
                })
        
        # Sort by priority
        all_actions.sort(key=lambda x: x["priority"], reverse=True)
        
        if max_actions:
            all_actions = all_actions[:max_actions]
        
        return all_actions
    
    def _calculate_action_priority(self, gap: ComplianceGap, action: RemediationAction) -> float:
        """Calculate priority score for an action"""
        # Higher severity = higher priority
        severity_score = gap.severity.value * 25
        
        # Shorter timeline = higher priority
        timeline_score = (100 - action.timeline_days) if action.timeline_days <= 100 else 0
        
        # Lower cost might enable quicker action
        cost_score = (1000 - action.estimated_cost) / 10 if action.estimated_cost <= 1000 else 0
        
        return severity_score + timeline_score + cost_score
    
    def export_gaps_report(self, filepath: str) -> bool:
        """Export gaps report to JSON"""
        try:
            gaps_data = {
                gap_id: gap.to_dict()
                for gap_id, gap in self.gaps.items()
            }
            
            with open(filepath, 'w') as f:
                json.dump(gaps_data, f, indent=2)
            
            logger.info(f"Exported {len(gaps_data)} gaps to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting gaps: {e}")
            return False
    
    def export_action_plan(self, filepath: str) -> bool:
        """Export action plan to JSON"""
        try:
            action_plan = self.get_prioritized_action_plan()
            summary = self.get_portfolio_gap_summary()
            
            export_data = {
                "summary": summary,
                "action_plan": action_plan
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported action plan to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting action plan: {e}")
            return False


# Example usage
if __name__ == "__main__":
    from compliance.scorer import (
        ComplianceScorer, Evidence, EvidenceType, RiskLevel
    )
    
    # Create sample scores
    scorer = ComplianceScorer()
    
    # Create a sample gap (low score)
    low_evidence = [
        Evidence(
            type=EvidenceType.DOCUMENTATION,
            description="Incomplete documentation",
            quality_score=35,
            confidence=0.6
        )
    ]
    
    score = scorer.score_requirement(
        requirement_id="GDPR-5.1",
        requirement_text="Data must be processed lawfully",
        regulation="GDPR",
        evidence_list=low_evidence,
        risk_level=RiskLevel.CRITICAL
    )
    
    # Analyze gaps
    analyzer = GapAnalyzer()
    gaps = analyzer.identify_gaps(scorer.requirement_scores, gap_threshold=50)
    
    print(f"\n=== IDENTIFIED GAPS ===")
    print(f"Total gaps: {len(gaps)}")
    
    for gap in gaps:
        print(f"\nGap: {gap.gap_id}")
        print(f"  Requirement: {gap.requirement_id}")
        print(f"  Severity: {gap.severity.name}")
        print(f"  Root Cause: {gap.root_cause}")
        
        # Generate remediation plan
        actions = analyzer.generate_remediation_plan(gap)
        print(f"  Remediation Actions: {len(actions)}")
        for action in actions:
            print(f"    - {action.action_type.value}: {action.estimated_hours}h, ${action.estimated_cost}")
    
    # Portfolio summary
    summary = analyzer.get_portfolio_gap_summary()
    print("\n=== GAP PORTFOLIO SUMMARY ===")
    print(json.dumps(summary, indent=2))
