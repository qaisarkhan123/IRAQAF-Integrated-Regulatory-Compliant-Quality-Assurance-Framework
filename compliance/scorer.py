"""
PHASE 5: COMPLIANCE SCORING ENGINE
Automated evidence-based compliance scoring system

Features:
  - 0-100 compliance scoring per requirement
  - Evidence matrix with quality assessment
  - Confidence scoring and intervals
  - Risk-based weighting system
  - Compliance level classification (0, 25, 50, 75, 100)
  - Multi-regulation support
  - Batch assessment processing
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance level classifications"""
    NON_COMPLIANT = 0
    MINIMAL = 25
    PARTIAL = 50
    SUBSTANTIAL = 75
    FULL = 100


class EvidenceType(Enum):
    """Types of evidence for compliance"""
    DOCUMENTATION = "documentation"
    POLICY = "policy"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    AUDIT = "audit"
    CERTIFICATION = "certification"


class RiskLevel(Enum):
    """Risk levels for requirements"""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Evidence:
    """Evidence for a requirement"""
    type: EvidenceType
    description: str
    quality_score: float  # 0-100
    confidence: float  # 0-1
    timestamp: datetime = field(default_factory=datetime.now)
    
    def weighted_score(self) -> float:
        """Calculate weighted evidence score"""
        return (self.quality_score * self.confidence) / 100


@dataclass
class RequirementScore:
    """Score for a single requirement"""
    requirement_id: str
    requirement_text: str
    regulation: str
    compliance_score: float  # 0-100
    compliance_level: ComplianceLevel
    risk_level: RiskLevel
    evidence_list: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0
    confidence_interval: Tuple[float, float] = (0, 0)
    weighted_score: float = 0.0
    notes: str = ""
    assessment_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "requirement_id": self.requirement_id,
            "requirement_text": self.requirement_text,
            "regulation": self.regulation,
            "compliance_score": round(self.compliance_score, 2),
            "compliance_level": self.compliance_level.name,
            "risk_level": self.risk_level.name,
            "confidence": round(self.confidence, 3),
            "confidence_interval": [round(x, 2) for x in self.confidence_interval],
            "weighted_score": round(self.weighted_score, 2),
            "evidence_count": len(self.evidence_list),
            "notes": self.notes,
            "assessment_date": self.assessment_date.isoformat()
        }


class ComplianceScorer:
    """Main compliance scoring engine"""
    
    def __init__(self):
        """Initialize scorer with default configurations"""
        self.requirement_scores: Dict[str, RequirementScore] = {}
        self.regulations_config = self._load_regulations_config()
        
    def _load_regulations_config(self) -> Dict:
        """Load regulations configuration with weighting"""
        return {
            "EU-AI-Act": {
                "total_requirements": 25,
                "risk_weight": 0.95,
                "priority": 1
            },
            "GDPR": {
                "total_requirements": 20,
                "risk_weight": 0.90,
                "priority": 1
            },
            "ISO-13485": {
                "total_requirements": 22,
                "risk_weight": 0.85,
                "priority": 2
            },
            "IEC-62304": {
                "total_requirements": 18,
                "risk_weight": 0.85,
                "priority": 2
            },
            "FDA": {
                "total_requirements": 20,
                "risk_weight": 0.95,
                "priority": 1
            }
        }
    
    def score_requirement(
        self,
        requirement_id: str,
        requirement_text: str,
        regulation: str,
        evidence_list: List[Evidence],
        risk_level: RiskLevel,
        baseline_score: float = 0.0
    ) -> RequirementScore:
        """
        Score a single requirement based on evidence
        
        Args:
            requirement_id: Unique requirement identifier
            requirement_text: Requirement description
            regulation: Regulation name
            evidence_list: List of evidence items
            risk_level: Risk level classification
            baseline_score: Starting score (default 0)
        
        Returns:
            RequirementScore with all metrics
        """
        
        # Calculate raw compliance score from evidence
        if evidence_list:
            weighted_evidence = [e.weighted_score() for e in evidence_list]
            compliance_score = statistics.mean(weighted_evidence)
            confidence = statistics.stdev(weighted_evidence) if len(weighted_evidence) > 1 else 0
            confidence = 1.0 - (confidence / 100)  # Normalize to 0-1
        else:
            compliance_score = baseline_score
            confidence = 0.0
        
        # Apply risk weighting
        risk_multiplier = 1.0 + (risk_level.value * 0.05)  # 1.05 to 1.20
        weighted_score = min(100, compliance_score * risk_multiplier)
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(compliance_score)
        
        # Calculate confidence interval (95%)
        if evidence_list:
            std_dev = statistics.stdev([e.quality_score for e in evidence_list]) if len(evidence_list) > 1 else 0
            margin_error = 1.96 * (std_dev / (len(evidence_list) ** 0.5))
            ci_lower = max(0, compliance_score - margin_error)
            ci_upper = min(100, compliance_score + margin_error)
            confidence_interval = (ci_lower, ci_upper)
        else:
            confidence_interval = (compliance_score, compliance_score)
        
        # Create score object
        score = RequirementScore(
            requirement_id=requirement_id,
            requirement_text=requirement_text,
            regulation=regulation,
            compliance_score=compliance_score,
            compliance_level=compliance_level,
            risk_level=risk_level,
            evidence_list=evidence_list,
            confidence=confidence,
            confidence_interval=confidence_interval,
            weighted_score=weighted_score
        )
        
        self.requirement_scores[requirement_id] = score
        logger.info(f"Scored {requirement_id}: {compliance_score:.1f}% ({compliance_level.name})")
        
        return score
    
    def _determine_compliance_level(self, score: float) -> ComplianceLevel:
        """Map score to compliance level"""
        if score >= 90:
            return ComplianceLevel.FULL
        elif score >= 75:
            return ComplianceLevel.SUBSTANTIAL
        elif score >= 50:
            return ComplianceLevel.PARTIAL
        elif score >= 25:
            return ComplianceLevel.MINIMAL
        else:
            return ComplianceLevel.NON_COMPLIANT
    
    def calculate_regulation_score(self, regulation: str) -> Dict:
        """
        Calculate overall compliance score for a regulation
        
        Args:
            regulation: Regulation name
        
        Returns:
            Dictionary with regulation-level metrics
        """
        
        # Filter requirements for this regulation
        reg_scores = [
            score for score in self.requirement_scores.values()
            if score.regulation == regulation
        ]
        
        if not reg_scores:
            logger.warning(f"No scores found for {regulation}")
            return {}
        
        # Calculate metrics
        scores = [s.compliance_score for s in reg_scores]
        weighted_scores = [s.weighted_score for s in reg_scores]
        
        overall_score = statistics.mean(scores)
        weighted_overall = statistics.mean(weighted_scores)
        
        # Count compliance levels
        level_counts = {}
        for level in ComplianceLevel:
            count = sum(1 for s in reg_scores if s.compliance_level == level)
            level_counts[level.name] = count
        
        # Risk distribution
        risk_counts = {}
        for risk in RiskLevel:
            count = sum(1 for s in reg_scores if s.risk_level == risk)
            risk_counts[risk.name] = count
        
        # Non-compliant requirements
        non_compliant = [s for s in reg_scores if s.compliance_score < 50]
        
        return {
            "regulation": regulation,
            "total_requirements": len(reg_scores),
            "overall_score": round(overall_score, 2),
            "weighted_score": round(weighted_overall, 2),
            "compliance_level": self._determine_compliance_level(overall_score).name,
            "level_distribution": level_counts,
            "risk_distribution": risk_counts,
            "non_compliant_count": len(non_compliant),
            "non_compliant_ids": [s.requirement_id for s in non_compliant],
            "avg_confidence": round(statistics.mean([s.confidence for s in reg_scores]), 3)
        }
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get overall compliance portfolio summary across all regulations
        
        Returns:
            Dictionary with portfolio-level metrics
        """
        
        if not self.requirement_scores:
            return {"status": "No scores available"}
        
        all_scores = list(self.requirement_scores.values())
        
        # Overall metrics
        compliance_scores = [s.compliance_score for s in all_scores]
        weighted_scores = [s.weighted_score for s in all_scores]
        
        overall_compliance = statistics.mean(compliance_scores)
        overall_weighted = statistics.mean(weighted_scores)
        
        # Regulation breakdown
        regulations_summary = {}
        unique_regulations = set(s.regulation for s in all_scores)
        
        for reg in unique_regulations:
            regulations_summary[reg] = self.calculate_regulation_score(reg)
        
        # Compliance level distribution
        level_dist = {}
        for level in ComplianceLevel:
            count = sum(1 for s in all_scores if s.compliance_level == level)
            percentage = (count / len(all_scores)) * 100
            level_dist[level.name] = {"count": count, "percentage": round(percentage, 1)}
        
        # Risk level distribution
        risk_dist = {}
        for risk in RiskLevel:
            count = sum(1 for s in all_scores if s.risk_level == risk)
            percentage = (count / len(all_scores)) * 100
            risk_dist[risk.name] = {"count": count, "percentage": round(percentage, 1)}
        
        return {
            "total_requirements_assessed": len(all_scores),
            "overall_compliance_score": round(overall_compliance, 2),
            "overall_weighted_score": round(overall_weighted, 2),
            "overall_level": self._determine_compliance_level(overall_compliance).name,
            "compliance_level_distribution": level_dist,
            "risk_level_distribution": risk_dist,
            "regulations": regulations_summary,
            "avg_confidence": round(statistics.mean([s.confidence for s in all_scores]), 3),
            "assessment_timestamp": datetime.now().isoformat()
        }
    
    def export_scores_json(self, filepath: str) -> bool:
        """Export all scores to JSON file"""
        try:
            scores_dict = {
                rid: score.to_dict()
                for rid, score in self.requirement_scores.items()
            }
            
            with open(filepath, 'w') as f:
                json.dump(scores_dict, f, indent=2)
            
            logger.info(f"Exported {len(scores_dict)} scores to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting scores: {e}")
            return False
    
    def export_portfolio_summary(self, filepath: str) -> bool:
        """Export portfolio summary to JSON file"""
        try:
            summary = self.get_portfolio_summary()
            
            with open(filepath, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Exported portfolio summary to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting summary: {e}")
            return False


class EvidenceMatrix:
    """Management of evidence for assessments"""
    
    def __init__(self):
        """Initialize evidence matrix"""
        self.evidence_store: Dict[str, List[Evidence]] = {}
    
    def add_evidence(
        self,
        requirement_id: str,
        evidence: Evidence
    ) -> None:
        """Add evidence for a requirement"""
        if requirement_id not in self.evidence_store:
            self.evidence_store[requirement_id] = []
        
        self.evidence_store[requirement_id].append(evidence)
        logger.debug(f"Added {evidence.type.value} evidence for {requirement_id}")
    
    def get_evidence(self, requirement_id: str) -> List[Evidence]:
        """Get all evidence for a requirement"""
        return self.evidence_store.get(requirement_id, [])
    
    def evidence_quality_report(self, requirement_id: str) -> Dict:
        """Generate evidence quality report"""
        evidence_list = self.get_evidence(requirement_id)
        
        if not evidence_list:
            return {"status": "No evidence available"}
        
        # Quality metrics
        quality_scores = [e.quality_score for e in evidence_list]
        confidences = [e.confidence for e in evidence_list]
        
        type_counts = {}
        for ev in evidence_list:
            type_name = ev.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "requirement_id": requirement_id,
            "total_evidence_items": len(evidence_list),
            "avg_quality": round(statistics.mean(quality_scores), 2),
            "avg_confidence": round(statistics.mean(confidences), 3),
            "quality_range": (round(min(quality_scores), 2), round(max(quality_scores), 2)),
            "evidence_types": type_counts,
            "evidence_variety": len(type_counts)
        }
    
    def export_evidence_matrix(self, filepath: str) -> bool:
        """Export evidence matrix to JSON"""
        try:
            matrix_data = {}
            
            for req_id, evidence_list in self.evidence_store.items():
                matrix_data[req_id] = [
                    {
                        "type": e.type.value,
                        "quality": e.quality_score,
                        "confidence": e.confidence,
                        "description": e.description[:100]  # Truncate long descriptions
                    }
                    for e in evidence_list
                ]
            
            with open(filepath, 'w') as f:
                json.dump(matrix_data, f, indent=2)
            
            logger.info(f"Exported evidence matrix to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting evidence matrix: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize scorer
    scorer = ComplianceScorer()
    evidence_matrix = EvidenceMatrix()
    
    # Example: Score EU-AI-Act requirement
    evidence = [
        Evidence(
            type=EvidenceType.DOCUMENTATION,
            description="Risk assessment procedure documented",
            quality_score=95,
            confidence=0.95
        ),
        Evidence(
            type=EvidenceType.IMPLEMENTATION,
            description="Risk assessment implemented in model development",
            quality_score=87,
            confidence=0.88
        ),
        Evidence(
            type=EvidenceType.TESTING,
            description="Risk assessment tested on sample models",
            quality_score=82,
            confidence=0.85
        )
    ]
    
    # Add to evidence matrix
    for ev in evidence:
        evidence_matrix.add_evidence("EU-AI-41.1", ev)
    
    # Score the requirement
    score = scorer.score_requirement(
        requirement_id="EU-AI-41.1",
        requirement_text="High-risk AI systems must perform risk assessment",
        regulation="EU-AI-Act",
        evidence_list=evidence,
        risk_level=RiskLevel.CRITICAL
    )
    
    print("\n=== REQUIREMENT SCORE ===")
    print(json.dumps(score.to_dict(), indent=2))
    
    # Get portfolio summary
    summary = scorer.get_portfolio_summary()
    print("\n=== PORTFOLIO SUMMARY ===")
    print(json.dumps(summary, indent=2))
    
    # Evidence quality report
    report = evidence_matrix.evidence_quality_report("EU-AI-41.1")
    print("\n=== EVIDENCE QUALITY REPORT ===")
    print(json.dumps(report, indent=2))
