"""
Regulatory Mapping Engine
Evaluates compliance status for all regulatory frameworks and clauses.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class RegulatoryMappingEngine:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the regulatory mapping engine."""
        if config_path is None:
            config_path = Path(__file__).parent / "configs" / "regulation_clauses.json"
        
        self.config_path = Path(config_path)
        self.clauses = self._load_clauses()
        self.frameworks = list(self.clauses.get("frameworks", {}).keys())
    
    def _load_clauses(self) -> Dict:
        """Load regulation clauses from JSON configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at {self.config_path}")
            return {"frameworks": {}}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {"frameworks": {}}
    
    def get_all_frameworks(self) -> List[Dict]:
        """Get list of all supported frameworks."""
        frameworks_list = []
        for framework_id, framework_data in self.clauses.get("frameworks", {}).items():
            frameworks_list.append({
                "id": framework_id,
                "name": framework_data.get("name", framework_id),
                "version": framework_data.get("version", "Unknown"),
                "jurisdiction": framework_data.get("jurisdiction", "Unknown"),
                "clause_count": len(framework_data.get("clauses", []))
            })
        return frameworks_list
    
    def get_framework(self, framework_name: str) -> Optional[Dict]:
        """Get detailed information about a specific framework."""
        framework_data = self.clauses.get("frameworks", {}).get(framework_name)
        if not framework_data:
            return None
        
        return {
            "id": framework_name,
            "name": framework_data.get("name", framework_name),
            "version": framework_data.get("version", "Unknown"),
            "jurisdiction": framework_data.get("jurisdiction", "Unknown"),
            "clauses": framework_data.get("clauses", [])
        }
    
    def evaluate_clause_compliance(self, framework: str, clause_id: str, 
                                   evidence_status: Dict[str, bool]) -> Dict:
        """
        Evaluate compliance status for a specific clause.
        
        Args:
            framework: Framework identifier (e.g., "GDPR")
            clause_id: Clause identifier (e.g., "Art.5")
            evidence_status: Dict mapping evidence types to boolean availability
        
        Returns:
            Compliance evaluation result
        """
        framework_data = self.clauses.get("frameworks", {}).get(framework)
        if not framework_data:
            return {
                "compliant": False,
                "error": f"Framework {framework} not found"
            }
        
        clause = None
        for c in framework_data.get("clauses", []):
            if c.get("clause_id") == clause_id:
                clause = c
                break
        
        if not clause:
            return {
                "compliant": False,
                "error": f"Clause {clause_id} not found in {framework}"
            }
        
        required_evidence = clause.get("evidence_required", [])
        provided_evidence = [ev for ev, available in evidence_status.items() if available]
        
        evidence_completeness = len(provided_evidence) / len(required_evidence) if required_evidence else 0
        compliance_threshold = clause.get("compliance_threshold", 0.90)
        is_compliant = evidence_completeness >= compliance_threshold
        
        return {
            "clause_id": clause_id,
            "framework": framework,
            "title": clause.get("title", ""),
            "category": clause.get("category", ""),
            "required_evidence": required_evidence,
            "provided_evidence": provided_evidence,
            "evidence_completeness": evidence_completeness,
            "compliance_threshold": compliance_threshold,
            "compliant": is_compliant,
            "risk_level": clause.get("risk_level", "medium"),
            "sdlc_phases": clause.get("sdlc_phase", [])
        }
    
    def get_compliance_map(self, evidence_status_map: Optional[Dict] = None) -> Dict:
        """
        Get comprehensive compliance map across all frameworks.
        
        Args:
            evidence_status_map: Optional dict mapping (framework, clause_id) to evidence status
        
        Returns:
            Complete compliance mapping
        """
        if evidence_status_map is None:
            evidence_status_map = {}
        
        compliance_map = {
            "timestamp": datetime.now().isoformat(),
            "frameworks": {}
        }
        
        for framework_id, framework_data in self.clauses.get("frameworks", {}).items():
            framework_compliance = {
                "name": framework_data.get("name", framework_id),
                "version": framework_data.get("version", "Unknown"),
                "jurisdiction": framework_data.get("jurisdiction", "Unknown"),
                "clauses": []
            }
            
            total_score = 0
            clause_count = 0
            
            for clause in framework_data.get("clauses", []):
                clause_id = clause.get("clause_id")
                key = f"{framework_id}:{clause_id}"
                
                # Get evidence status for this clause
                evidence_status = evidence_status_map.get(key, {})
                if not evidence_status:
                    # Default: assume no evidence available
                    evidence_status = {ev: False for ev in clause.get("evidence_required", [])}
                
                evaluation = self.evaluate_clause_compliance(
                    framework_id, clause_id, evidence_status
                )
                
                framework_compliance["clauses"].append(evaluation)
                
                if evaluation.get("compliant"):
                    total_score += 1
                clause_count += 1
            
            framework_compliance["overall_score"] = (total_score / clause_count * 100) if clause_count > 0 else 0
            framework_compliance["compliant_clauses"] = total_score
            framework_compliance["total_clauses"] = clause_count
            
            compliance_map["frameworks"][framework_id] = framework_compliance
        
        return compliance_map
    
    def get_clauses_by_category(self, framework: str, category: str) -> List[Dict]:
        """Get all clauses in a specific category for a framework."""
        framework_data = self.clauses.get("frameworks", {}).get(framework)
        if not framework_data:
            return []
        
        return [
            clause for clause in framework_data.get("clauses", [])
            if clause.get("category", "").lower() == category.lower()
        ]
    
    def get_clauses_by_sdlc_phase(self, framework: str, phase: str) -> List[Dict]:
        """Get all clauses applicable to a specific SDLC phase."""
        framework_data = self.clauses.get("frameworks", {}).get(framework)
        if not framework_data:
            return []
        
        return [
            clause for clause in framework_data.get("clauses", [])
            if phase in clause.get("sdlc_phase", [])
        ]

