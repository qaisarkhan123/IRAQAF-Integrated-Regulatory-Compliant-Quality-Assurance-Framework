"""
Governance Maturity Index (GMI) Calculator
Assesses governance maturity on a 1-5 scale.
"""

from typing import Dict, List
from datetime import datetime

class GovernanceMaturity:
    def __init__(self):
        """Initialize the governance maturity calculator."""
        self.maturity_levels = {
            1: {
                "name": "No formal governance",
                "description": "No documented governance processes",
                "criteria": [
                    "No governance documentation",
                    "Ad-hoc decision making",
                    "No compliance tracking"
                ]
            },
            2: {
                "name": "Basic processes documented",
                "description": "Some governance processes are documented",
                "criteria": [
                    "Basic policies exist",
                    "Some documentation",
                    "Manual compliance tracking"
                ]
            },
            3: {
                "name": "Partially implemented compliance",
                "description": "Governance processes are partially implemented",
                "criteria": [
                    "Structured policies",
                    "Regular reviews",
                    "Semi-automated tracking"
                ]
            },
            4: {
                "name": "Fully implemented governance",
                "description": "Comprehensive governance framework in place",
                "criteria": [
                    "Complete policy framework",
                    "Automated compliance monitoring",
                    "Regular audits",
                    "Executive oversight"
                ]
            },
            5: {
                "name": "Continuous governance optimization",
                "description": "Advanced governance with continuous improvement",
                "criteria": [
                    "Predictive compliance analytics",
                    "Real-time monitoring",
                    "Continuous improvement processes",
                    "Industry-leading practices"
                ]
            }
        }
    
    def assess_maturity(self, governance_indicators: Dict) -> Dict:
        """
        Assess governance maturity based on indicators.
        
        Args:
            governance_indicators: Dict with various governance metrics
        
        Returns:
            GMI score and detailed assessment
        """
        scores = {
            "documentation": self._score_documentation(governance_indicators),
            "processes": self._score_processes(governance_indicators),
            "monitoring": self._score_monitoring(governance_indicators),
            "oversight": self._score_oversight(governance_indicators),
            "automation": self._score_automation(governance_indicators)
        }
        
        # Calculate overall GMI (average of component scores)
        overall_gmi = sum(scores.values()) / len(scores)
        
        # Round to nearest 0.5
        overall_gmi = round(overall_gmi * 2) / 2
        
        level_info = self.maturity_levels.get(int(overall_gmi), self.maturity_levels[1])
        
        return {
            "gmi": overall_gmi,
            "timestamp": datetime.now().isoformat(),
            "level": int(overall_gmi),
            "level_name": level_info["name"],
            "level_description": level_info["description"],
            "components": scores,
            "recommendations": self._get_recommendations(overall_gmi, scores)
        }
    
    def _score_documentation(self, indicators: Dict) -> float:
        """Score documentation maturity (1-5)."""
        score = 1.0
        
        if indicators.get("policies_documented", False):
            score += 0.5
        if indicators.get("procedures_documented", False):
            score += 0.5
        if indicators.get("compliance_docs_complete", False):
            score += 1.0
        if indicators.get("technical_docs_complete", False):
            score += 1.0
        if indicators.get("version_controlled", False):
            score += 1.0
        
        return min(score, 5.0)
    
    def _score_processes(self, indicators: Dict) -> float:
        """Score process maturity (1-5)."""
        score = 1.0
        
        if indicators.get("change_management_defined", False):
            score += 0.5
        if indicators.get("risk_assessment_process", False):
            score += 0.5
        if indicators.get("incident_response_defined", False):
            score += 1.0
        if indicators.get("regular_reviews", False):
            score += 1.0
        if indicators.get("continuous_improvement", False):
            score += 1.0
        
        return min(score, 5.0)
    
    def _score_monitoring(self, indicators: Dict) -> float:
        """Score monitoring maturity (1-5)."""
        score = 1.0
        
        if indicators.get("compliance_tracking_enabled", False):
            score += 1.0
        if indicators.get("automated_alerts", False):
            score += 1.0
        if indicators.get("real_time_monitoring", False):
            score += 1.0
        if indicators.get("drift_detection", False):
            score += 1.0
        if indicators.get("predictive_analytics", False):
            score += 1.0
        
        return min(score, 5.0)
    
    def _score_oversight(self, indicators: Dict) -> float:
        """Score oversight maturity (1-5)."""
        score = 1.0
        
        if indicators.get("executive_oversight", False):
            score += 1.0
        if indicators.get("board_committee", False):
            score += 1.0
        if indicators.get("regular_audits", False):
            score += 1.0
        if indicators.get("external_audits", False):
            score += 1.0
        if indicators.get("escalation_path_defined", False):
            score += 1.0
        
        return min(score, 5.0)
    
    def _score_automation(self, indicators: Dict) -> float:
        """Score automation maturity (1-5)."""
        score = 1.0
        
        if indicators.get("automated_compliance_checks", False):
            score += 1.0
        if indicators.get("automated_reporting", False):
            score += 1.0
        if indicators.get("automated_evidence_collection", False):
            score += 1.0
        if indicators.get("ai_powered_analytics", False):
            score += 1.0
        if indicators.get("fully_integrated_systems", False):
            score += 1.0
        
        return min(score, 5.0)
    
    def _get_recommendations(self, gmi: float, component_scores: Dict) -> List[str]:
        """Get recommendations for improving governance maturity."""
        recommendations = []
        
        if gmi < 2.0:
            recommendations.append("Establish basic governance documentation and policies")
            recommendations.append("Implement manual compliance tracking processes")
        elif gmi < 3.0:
            recommendations.append("Develop structured governance framework")
            recommendations.append("Implement regular compliance reviews")
        elif gmi < 4.0:
            recommendations.append("Automate compliance monitoring and reporting")
            recommendations.append("Establish executive oversight and regular audits")
        elif gmi < 5.0:
            recommendations.append("Implement predictive compliance analytics")
            recommendations.append("Establish continuous improvement processes")
        
        # Component-specific recommendations
        min_component = min(component_scores.items(), key=lambda x: x[1])
        if min_component[1] < gmi - 0.5:
            recommendations.append(f"Focus on improving {min_component[0]} maturity")
        
        return recommendations
    
    def get_maturity_level_info(self, level: int) -> Dict:
        """Get information about a specific maturity level."""
        return self.maturity_levels.get(level, self.maturity_levels[1])

