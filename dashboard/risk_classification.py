"""
EU AI Act Risk Classification Engine
Classifies AI systems according to EU AI Act risk categories.
"""

from typing import Dict, List, Optional
from datetime import datetime

class RiskClassification:
    def __init__(self):
        """Initialize the risk classification engine."""
        self.risk_categories = {
            "prohibited": {
                "name": "Prohibited AI Systems",
                "description": "AI systems that are prohibited under EU AI Act",
                "compliance_threshold": 1.0,
                "requirements": "Must not be deployed"
            },
            "high_risk": {
                "name": "High-Risk AI Systems",
                "description": "AI systems subject to strict compliance requirements",
                "compliance_threshold": 0.90,
                "requirements": "Full compliance with all high-risk requirements"
            },
            "limited_risk": {
                "name": "Limited Risk AI Systems",
                "description": "AI systems with transparency obligations",
                "compliance_threshold": 0.75,
                "requirements": "Transparency and user notification requirements"
            },
            "minimal_risk": {
                "name": "Minimal Risk AI Systems",
                "description": "AI systems with no specific compliance requirements",
                "compliance_threshold": 0.50,
                "requirements": "General AI Act principles apply"
            }
        }
    
    def classify_system(self, system_characteristics: Dict) -> Dict:
        """
        Classify an AI system based on its characteristics.
        
        Args:
            system_characteristics: Dict with system information:
                - intended_use: Primary use case
                - data_type: Type of data processed
                - model_purpose: Purpose of the AI model
                - deployment_context: Where/how it's deployed
                - decision_impact: Impact of decisions made
        
        Returns:
            Risk classification result
        """
        intended_use = system_characteristics.get("intended_use", "").lower()
        data_type = system_characteristics.get("data_type", "").lower()
        model_purpose = system_characteristics.get("model_purpose", "").lower()
        deployment_context = system_characteristics.get("deployment_context", "").lower()
        decision_impact = system_characteristics.get("decision_impact", "").lower()
        
        # Check for prohibited practices
        if self._is_prohibited(intended_use, model_purpose):
            classification = "prohibited"
        # Check for high-risk indicators
        elif self._is_high_risk(intended_use, data_type, model_purpose, deployment_context, decision_impact):
            classification = "high_risk"
        # Check for limited risk
        elif self._is_limited_risk(intended_use, model_purpose):
            classification = "limited_risk"
        else:
            classification = "minimal_risk"
        
        risk_info = self.risk_categories[classification]
        
        return {
            "classification": classification,
            "category_name": risk_info["name"],
            "description": risk_info["description"],
            "compliance_threshold": risk_info["compliance_threshold"],
            "requirements": risk_info["requirements"],
            "timestamp": datetime.now().isoformat(),
            "reasoning": self._get_classification_reasoning(
                classification, intended_use, data_type, model_purpose
            )
        }
    
    def _is_prohibited(self, intended_use: str, model_purpose: str) -> bool:
        """Check if system falls under prohibited practices."""
        prohibited_keywords = [
            "subliminal manipulation",
            "exploit vulnerability",
            "social scoring",
            "real-time remote biometric identification",
            "emotion recognition in workplace",
            "predictive policing"
        ]
        
        combined_text = f"{intended_use} {model_purpose}".lower()
        
        return any(keyword in combined_text for keyword in prohibited_keywords)
    
    def _is_high_risk(self, intended_use: str, data_type: str, 
                     model_purpose: str, deployment_context: str, 
                     decision_impact: str) -> bool:
        """Check if system is classified as high-risk."""
        # High-risk use cases (Annex III of EU AI Act)
        high_risk_use_cases = [
            "biometric identification",
            "critical infrastructure",
            "education",
            "employment",
            "access to essential services",
            "law enforcement",
            "migration",
            "administration of justice",
            "medical device",
            "healthcare",
            "diagnosis",
            "treatment",
            "safety component"
        ]
        
        combined_text = f"{intended_use} {data_type} {model_purpose} {deployment_context}".lower()
        
        # Check for high-risk use cases
        if any(use_case in combined_text for use_case in high_risk_use_cases):
            return True
        
        # Check for high-impact decisions
        high_impact_keywords = [
            "life-threatening",
            "significant harm",
            "fundamental rights",
            "legal consequences",
            "financial consequences"
        ]
        
        if any(keyword in decision_impact.lower() for keyword in high_impact_keywords):
            return True
        
        return False
    
    def _is_limited_risk(self, intended_use: str, model_purpose: str) -> bool:
        """Check if system has limited risk (transparency obligations)."""
        limited_risk_keywords = [
            "chatbot",
            "deepfake",
            "emotion recognition",
            "biometric categorization"
        ]
        
        combined_text = f"{intended_use} {model_purpose}".lower()
        
        return any(keyword in combined_text for keyword in limited_risk_keywords)
    
    def _get_classification_reasoning(self, classification: str, 
                                    intended_use: str, data_type: str, 
                                    model_purpose: str) -> str:
        """Generate reasoning for the classification."""
        if classification == "prohibited":
            return "System matches prohibited AI practices under EU AI Act Article 6"
        elif classification == "high_risk":
            return f"System is used in high-risk context: {intended_use or model_purpose}. Requires full compliance with high-risk AI system requirements."
        elif classification == "limited_risk":
            return "System has transparency obligations. Users must be informed they are interacting with AI."
        else:
            return "System poses minimal risk. General AI Act principles apply."
    
    def get_compliance_requirements(self, classification: str) -> List[str]:
        """Get specific compliance requirements for a risk classification."""
        requirements_map = {
            "prohibited": [
                "System must not be deployed",
                "Immediate cessation required"
            ],
            "high_risk": [
                "Risk management system",
                "Data and data governance",
                "Technical documentation",
                "Record-keeping",
                "Transparency and user information",
                "Human oversight",
                "Accuracy, robustness and cybersecurity",
                "Conformity assessment",
                "CE marking",
                "Post-market monitoring"
            ],
            "limited_risk": [
                "User notification (transparency)",
                "Inform users they are interacting with AI"
            ],
            "minimal_risk": [
                "General AI Act principles",
                "Voluntary code of conduct"
            ]
        }
        
        return requirements_map.get(classification, [])

