"""
SDLC Compliance Tracker
Tracks compliance coverage across SDLC phases.
"""

from typing import Dict, List, Optional
from datetime import datetime
from regulatory_mapping_engine import RegulatoryMappingEngine

class SDLCTracker:
    def __init__(self, mapping_engine: Optional[RegulatoryMappingEngine] = None):
        """Initialize the SDLC tracker."""
        self.mapping_engine = mapping_engine or RegulatoryMappingEngine()
        self.phases = [
            "Design",
            "Data Collection",
            "Model Training",
            "Validation",
            "Deployment",
            "Post-Market Monitoring"
        ]
    
    def get_clauses_by_phase(self, phase: str) -> Dict:
        """Get all clauses applicable to a specific SDLC phase."""
        clauses_by_framework = {}
        total_clauses = 0
        
        for framework_id, framework_data in self.mapping_engine.clauses.get("frameworks", {}).items():
            phase_clauses = []
            
            for clause in framework_data.get("clauses", []):
                if phase in clause.get("sdlc_phase", []):
                    phase_clauses.append({
                        "clause_id": clause.get("clause_id"),
                        "title": clause.get("title", ""),
                        "category": clause.get("category", ""),
                        "risk_level": clause.get("risk_level", "medium")
                    })
                    total_clauses += 1
            
            if phase_clauses:
                clauses_by_framework[framework_id] = phase_clauses
        
        return {
            "phase": phase,
            "total_clauses": total_clauses,
            "frameworks": clauses_by_framework
        }
    
    def get_sdlc_status(self, compliance_map: Optional[Dict] = None) -> Dict:
        """
        Get compliance status across all SDLC phases.
        
        Returns:
            Dict with per-phase clause coverage and compliance status
        """
        if compliance_map is None:
            compliance_map = self.mapping_engine.get_compliance_map()
        
        sdlc_status = {
            "timestamp": datetime.now().isoformat(),
            "phases": {}
        }
        
        for phase in self.phases:
            phase_data = self.get_clauses_by_phase(phase)
            
            # Calculate compliance for this phase
            compliant_clauses = 0
            total_clauses = phase_data["total_clauses"]
            
            if total_clauses > 0:
                # Check compliance for each clause in this phase
                for framework_id, clauses in phase_data["frameworks"].items():
                    framework_compliance = compliance_map.get("frameworks", {}).get(framework_id, {})
                    framework_clauses = framework_compliance.get("clauses", [])
                    
                    for clause_info in clauses:
                        clause_id = clause_info["clause_id"]
                        # Find matching clause in compliance map
                        for comp_clause in framework_clauses:
                            if comp_clause.get("clause_id") == clause_id:
                                if comp_clause.get("compliant", False):
                                    compliant_clauses += 1
                                break
            
            clause_coverage = (compliant_clauses / total_clauses * 100) if total_clauses > 0 else 0
            
            sdlc_status["phases"][phase] = {
                "phase": phase,
                "total_clauses": total_clauses,
                "compliant_clauses": compliant_clauses,
                "clause_coverage": round(clause_coverage, 2),
                "frameworks": phase_data["frameworks"]
            }
        
        # Calculate overall SDLC score
        total_coverage = sum(
            phase_data.get("clause_coverage", 0) 
            for phase_data in sdlc_status["phases"].values()
        )
        sdlc_status["overall_score"] = round(
            total_coverage / len(self.phases) if self.phases else 0, 2
        )
        
        return sdlc_status
    
    def get_phase_gaps(self, sdlc_status: Dict) -> Dict:
        """Identify gaps in SDLC phase compliance."""
        gaps = {
            "critical_gaps": [],
            "high_priority_gaps": [],
            "medium_priority_gaps": []
        }
        
        for phase, phase_data in sdlc_status.get("phases", {}).items():
            coverage = phase_data.get("clause_coverage", 0)
            
            if coverage < 50:
                gaps["critical_gaps"].append({
                    "phase": phase,
                    "coverage": coverage,
                    "total_clauses": phase_data.get("total_clauses", 0),
                    "compliant_clauses": phase_data.get("compliant_clauses", 0)
                })
            elif coverage < 75:
                gaps["high_priority_gaps"].append({
                    "phase": phase,
                    "coverage": coverage,
                    "total_clauses": phase_data.get("total_clauses", 0),
                    "compliant_clauses": phase_data.get("compliant_clauses", 0)
                })
            elif coverage < 90:
                gaps["medium_priority_gaps"].append({
                    "phase": phase,
                    "coverage": coverage,
                    "total_clauses": phase_data.get("total_clauses", 0),
                    "compliant_clauses": phase_data.get("compliant_clauses", 0)
                })
        
        return gaps

