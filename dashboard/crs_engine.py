"""
Compliance Readiness Score (CRS) Engine
Calculates formal CRS based on multiple components.
"""

from typing import Dict, Optional
from datetime import datetime
from regulatory_mapping_engine import RegulatoryMappingEngine

class CRSEngine:
    def __init__(self, mapping_engine: Optional[RegulatoryMappingEngine] = None):
        """Initialize the CRS engine."""
        self.mapping_engine = mapping_engine or RegulatoryMappingEngine()
    
    def calculate_regulatory_alignment(self, compliance_map: Dict) -> float:
        """
        Calculate Regulatory Alignment component (0-100).
        Based on overall compliance scores across all frameworks.
        """
        if not compliance_map.get("frameworks"):
            return 0.0
        
        total_score = 0
        framework_count = 0
        
        for framework_id, framework_data in compliance_map["frameworks"].items():
            score = framework_data.get("overall_score", 0)
            total_score += score
            framework_count += 1
        
        return (total_score / framework_count) if framework_count > 0 else 0.0
    
    def calculate_evidence_completeness(self, evidence_map: Dict) -> float:
        """
        Calculate Evidence Completeness component (0-100).
        Based on percentage of required evidence that is available.
        """
        total_required = 0
        total_provided = 0
        
        for framework_id, framework_data in self.mapping_engine.clauses.get("frameworks", {}).items():
            for clause in framework_data.get("clauses", []):
                required_evidence = clause.get("evidence_required", [])
                total_required += len(required_evidence)
                
                # Count provided evidence (would come from evidence management system)
                # For now, estimate based on typical compliance
                # In production, this would query the evidence database
                estimated_provided = len(required_evidence) * 0.75  # Placeholder
                total_provided += estimated_provided
        
        return (total_provided / total_required * 100) if total_required > 0 else 0.0
    
    def calculate_sdlc_alignment(self, sdlc_status: Dict) -> float:
        """
        Calculate SDLC Alignment component (0-100).
        Based on clause coverage across SDLC phases.
        """
        if not sdlc_status.get("phases"):
            return 0.0
        
        total_coverage = 0
        phase_count = 0
        
        for phase, phase_data in sdlc_status["phases"].items():
            coverage = phase_data.get("clause_coverage", 0)
            total_coverage += coverage
            phase_count += 1
        
        return (total_coverage / phase_count) if phase_count > 0 else 0.0
    
    def calculate_governance_maturity(self, gmi_score: float) -> float:
        """
        Calculate Governance Maturity component (0-100).
        Based on Governance Maturity Index (GMI) score.
        GMI is typically 1-5, convert to 0-100 scale.
        """
        # GMI is 1-5, convert to 0-100
        return (gmi_score / 5.0) * 100.0
    
    def calculate_post_market_monitoring(self, monitoring_status: Dict) -> float:
        """
        Calculate Post-Market Monitoring Readiness component (0-100).
        Based on monitoring capabilities and processes.
        """
        if not monitoring_status:
            return 0.0
        
        score = 0.0
        
        # Check for monitoring capabilities
        if monitoring_status.get("drift_detection_enabled", False):
            score += 25.0
        if monitoring_status.get("alerting_enabled", False):
            score += 25.0
        if monitoring_status.get("reporting_automated", False):
            score += 25.0
        if monitoring_status.get("incident_response_ready", False):
            score += 25.0
        
        return score
    
    def calculate_crs(self, 
                      compliance_map: Optional[Dict] = None,
                      evidence_map: Optional[Dict] = None,
                      sdlc_status: Optional[Dict] = None,
                      gmi_score: Optional[float] = None,
                      monitoring_status: Optional[Dict] = None) -> Dict:
        """
        Calculate the overall Compliance Readiness Score (CRS).
        
        CRS = 0.30 * RegulatoryAlignment +
              0.25 * EvidenceCompleteness +
              0.20 * SDLCAlignment +
              0.15 * GovernanceMaturity +
              0.10 * PostMarketMonitoringReadiness
        
        Returns:
            Dict with CRS score and component breakdown
        """
        # Get compliance map if not provided
        if compliance_map is None:
            compliance_map = self.mapping_engine.get_compliance_map()
        
        # Calculate components
        regulatory_alignment = self.calculate_regulatory_alignment(compliance_map)
        
        if evidence_map is None:
            evidence_map = {}
        evidence_completeness = self.calculate_evidence_completeness(evidence_map)
        
        if sdlc_status is None:
            sdlc_status = {"phases": {}}
        sdlc_alignment = self.calculate_sdlc_alignment(sdlc_status)
        
        if gmi_score is None:
            gmi_score = 3.0  # Default to level 3
        governance_maturity = self.calculate_governance_maturity(gmi_score)
        
        if monitoring_status is None:
            monitoring_status = {
                "drift_detection_enabled": True,
                "alerting_enabled": True,
                "reporting_automated": True,
                "incident_response_ready": True
            }
        post_market_monitoring = self.calculate_post_market_monitoring(monitoring_status)
        
        # Calculate weighted CRS
        crs = (
            0.30 * regulatory_alignment +
            0.25 * evidence_completeness +
            0.20 * sdlc_alignment +
            0.15 * governance_maturity +
            0.10 * post_market_monitoring
        )
        
        return {
            "crs": round(crs, 2),
            "timestamp": datetime.now().isoformat(),
            "components": {
                "regulatory_alignment": round(regulatory_alignment, 2),
                "evidence_completeness": round(evidence_completeness, 2),
                "sdlc_alignment": round(sdlc_alignment, 2),
                "governance_maturity": round(governance_maturity, 2),
                "post_market_monitoring": round(post_market_monitoring, 2)
            },
            "weights": {
                "regulatory_alignment": 0.30,
                "evidence_completeness": 0.25,
                "sdlc_alignment": 0.20,
                "governance_maturity": 0.15,
                "post_market_monitoring": 0.10
            }
        }

