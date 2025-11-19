"""
PHASE 5: REQUIREMENT CHECKLISTS
Comprehensive compliance checklists for all 5 regulations (105 total requirements)

Regulations:
  - EU AI Act: 25 requirements
  - GDPR: 20 requirements
  - ISO 13485: 22 requirements
  - IEC 62304: 18 requirements
  - FDA: 20 requirements
"""

import json
from typing import Dict, List
from dataclasses import dataclass, asdict
from enum import Enum


class RequirementCategory(Enum):
    """Requirement categories"""
    GOVERNANCE = "Governance"
    DOCUMENTATION = "Documentation"
    IMPLEMENTATION = "Implementation"
    TESTING = "Testing"
    TRAINING = "Training"
    INCIDENT_RESPONSE = "Incident Response"
    MONITORING = "Monitoring"
    AUDIT = "Audit"


@dataclass
class ChecklistItem:
    """Individual checklist item"""
    req_id: str
    category: str
    description: str
    guideline: str
    verification_method: str
    evidence_type: str
    priority: str  # Critical, High, Medium, Low


class RequirementChecklists:
    """Comprehensive requirement checklists for all regulations"""

    def __init__(self):
        """Initialize checklists"""
        self.checklists = {
            "EU-AI-Act": self._get_eu_ai_act_requirements(),
            "GDPR": self._get_gdpr_requirements(),
            "ISO-13485": self._get_iso_13485_requirements(),
            "IEC-62304": self._get_iec_62304_requirements(),
            "FDA": self._get_fda_requirements()
        }

    def _get_eu_ai_act_requirements(self) -> List[ChecklistItem]:
        """EU AI Act - 25 Requirements"""
        return [
            # Risk Management (EU-AI-1 to EU-AI-8)
            ChecklistItem(
                "EU-AI-1", RequirementCategory.GOVERNANCE.value,
                "High-risk AI system classification and identification",
                "Organizations must identify and classify AI systems as high-risk per Article 6",
                "Review AI system registry and risk classification documentation",
                "System Documentation", "Critical"
            ),
            ChecklistItem(
                "EU-AI-2", RequirementCategory.GOVERNANCE.value,
                "Risk assessment before deployment",
                "Conduct formal risk assessment for high-risk AI systems",
                "Review risk assessment reports and methodology",
                "Assessment Report", "Critical"
            ),
            ChecklistItem(
                "EU-AI-3", RequirementCategory.IMPLEMENTATION.value,
                "Data quality assurance",
                "Ensure training and validation data meet quality standards",
                "Verify data quality metrics and test results",
                "Test Report", "High"
            ),
            ChecklistItem(
                "EU-AI-4", RequirementCategory.DOCUMENTATION.value,
                "Technical documentation",
                "Maintain comprehensive technical documentation of AI systems",
                "Review technical documentation completeness",
                "Documentation", "Critical"
            ),
            ChecklistItem(
                "EU-AI-5", RequirementCategory.MONITORING.value,
                "Performance monitoring system",
                "Implement monitoring for system performance and behavior",
                "Review monitoring dashboards and logs",
                "Monitoring System", "High"
            ),
            ChecklistItem(
                "EU-AI-6", RequirementCategory.TRAINING.value,
                "Staff training on AI risks",
                "Train personnel on AI system risks and safe operation",
                "Review training records and attendance",
                "Training Records", "Medium"
            ),
            ChecklistItem(
                "EU-AI-7", RequirementCategory.INCIDENT_RESPONSE.value,
                "Incident reporting mechanism",
                "Establish procedure for reporting serious incidents",
                "Review incident reporting logs and procedures",
                "Incident Procedure", "High"
            ),
            ChecklistItem(
                "EU-AI-8", RequirementCategory.AUDIT.value,
                "Internal audit of AI systems",
                "Conduct regular audits of AI system compliance",
                "Review audit reports and findings",
                "Audit Report", "Medium"
            ),
            # Transparency and Accountability (EU-AI-9 to EU-AI-15)
            ChecklistItem(
                "EU-AI-9", RequirementCategory.DOCUMENTATION.value,
                "Clear AI system information for users",
                "Provide clear information about AI system purpose and capabilities",
                "Review user-facing documentation and interfaces",
                "User Documentation", "High"
            ),
            ChecklistItem(
                "EU-AI-10", RequirementCategory.IMPLEMENTATION.value,
                "Explainability capabilities",
                "Ensure AI decisions can be explained to affected persons",
                "Test explainability features and outputs",
                "Test Results", "Critical"
            ),
            ChecklistItem(
                "EU-AI-11", RequirementCategory.GOVERNANCE.value,
                "Responsibility assignment",
                "Clearly assign responsibility for AI system outcomes",
                "Review organization chart and responsibility documentation",
                "Organization Documentation", "High"
            ),
            ChecklistItem(
                "EU-AI-12", RequirementCategory.DOCUMENTATION.value,
                "Right to explanation provision",
                "Ensure individuals can request explanations of AI decisions",
                "Review procedures and user interfaces",
                "Procedures", "High"
            ),
            ChecklistItem(
                "EU-AI-13", RequirementCategory.IMPLEMENTATION.value,
                "Human oversight mechanism",
                "Implement meaningful human oversight of AI outputs",
                "Observe operational procedures and override capabilities",
                "Observation Report", "Critical"
            ),
            ChecklistItem(
                "EU-AI-14", RequirementCategory.MONITORING.value,
                "Ongoing performance tracking",
                "Track AI system performance in production",
                "Review performance dashboards and historical data",
                "Performance Data", "High"
            ),
            ChecklistItem(
                "EU-AI-15", RequirementCategory.AUDIT.value,
                "Post-market surveillance",
                "Monitor AI system behavior after deployment",
                "Review surveillance logs and incident reports",
                "Surveillance Logs", "High"
            ),
            # Compliance and Documentation (EU-AI-16 to EU-AI-25)
            ChecklistItem(
                "EU-AI-16", RequirementCategory.DOCUMENTATION.value,
                "Compliance documentation",
                "Maintain documented evidence of compliance measures",
                "Review compliance file organization and completeness",
                "Documentation", "Critical"
            ),
            ChecklistItem(
                "EU-AI-17", RequirementCategory.GOVERNANCE.value,
                "Designated compliance officer",
                "Designate responsible person for AI compliance",
                "Verify designation and role definition",
                "Organization Documentation", "Medium"
            ),
            ChecklistItem(
                "EU-AI-18", RequirementCategory.TESTING.value,
                "Bias and discrimination testing",
                "Test AI systems for bias and discriminatory outcomes",
                "Review bias testing methodology and results",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "EU-AI-19", RequirementCategory.IMPLEMENTATION.value,
                "Robustness and accuracy",
                "Ensure AI system maintains accuracy and robustness",
                "Review accuracy metrics and robustness tests",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "EU-AI-20", RequirementCategory.MONITORING.value,
                "Security and adversarial testing",
                "Conduct security testing against adversarial inputs",
                "Review security test results and penetration tests",
                "Security Report", "High"
            ),
            ChecklistItem(
                "EU-AI-21", RequirementCategory.DOCUMENTATION.value,
                "Model card and system card",
                "Maintain model and system cards with key characteristics",
                "Review model and system card completeness",
                "Model/System Card", "High"
            ),
            ChecklistItem(
                "EU-AI-22", RequirementCategory.TRAINING.value,
                "End-user training on system limitations",
                "Train end-users on system capabilities and limitations",
                "Review training materials and records",
                "Training Materials", "Medium"
            ),
            ChecklistItem(
                "EU-AI-23", RequirementCategory.GOVERNANCE.value,
                "Supplier and third-party management",
                "Ensure compliance requirements flow to suppliers",
                "Review supplier contracts and agreements",
                "Contracts", "High"
            ),
            ChecklistItem(
                "EU-AI-24", RequirementCategory.INCIDENT_RESPONSE.value,
                "Recall and deactivation capability",
                "Maintain ability to recall or deactivate AI systems",
                "Verify recall procedures and technical capability",
                "Procedures", "High"
            ),
            ChecklistItem(
                "EU-AI-25", RequirementCategory.AUDIT.value,
                "Notified body assessment",
                "Facilitate assessment by notified body if required",
                "Review readiness for external audit",
                "Assessment Report", "Medium"
            ),
        ]

    def _get_gdpr_requirements(self) -> List[ChecklistItem]:
        """GDPR - 20 Requirements"""
        return [
            ChecklistItem(
                "GDPR-1", RequirementCategory.GOVERNANCE.value,
                "Legal basis for processing",
                "Establish valid legal basis for all personal data processing",
                "Review privacy notices and processing documentation",
                "Documentation", "Critical"
            ),
            ChecklistItem(
                "GDPR-2", RequirementCategory.DOCUMENTATION.value,
                "Data processing agreement",
                "Establish DPA with data processors",
                "Review and verify DPA contracts",
                "Contracts", "Critical"
            ),
            ChecklistItem(
                "GDPR-3", RequirementCategory.GOVERNANCE.value,
                "Data Protection Impact Assessment",
                "Conduct DPIA for high-risk processing",
                "Review DPIA documentation and findings",
                "Assessment Report", "High"
            ),
            ChecklistItem(
                "GDPR-4", RequirementCategory.GOVERNANCE.value,
                "Data protection officer",
                "Appoint DPO where required",
                "Verify DPO designation and contact",
                "Organization Documentation", "High"
            ),
            ChecklistItem(
                "GDPR-5", RequirementCategory.IMPLEMENTATION.value,
                "Data minimization",
                "Collect only necessary personal data",
                "Review data fields and retention policies",
                "Policy Documentation", "High"
            ),
            ChecklistItem(
                "GDPR-6", RequirementCategory.IMPLEMENTATION.value,
                "Storage limitation",
                "Delete or anonymize data when no longer needed",
                "Review retention schedules and deletion logs",
                "Audit Logs", "High"
            ),
            ChecklistItem(
                "GDPR-7", RequirementCategory.IMPLEMENTATION.value,
                "Encryption of personal data",
                "Encrypt personal data in transit and at rest",
                "Review encryption configurations and certificates",
                "Security Report", "Critical"
            ),
            ChecklistItem(
                "GDPR-8", RequirementCategory.IMPLEMENTATION.value,
                "Access controls",
                "Limit access to personal data to authorized personnel",
                "Review access logs and permission settings",
                "Access Audit", "Critical"
            ),
            ChecklistItem(
                "GDPR-9", RequirementCategory.INCIDENT_RESPONSE.value,
                "Breach notification",
                "Notify supervisory authority of personal data breaches",
                "Review breach notification procedures",
                "Procedures", "Critical"
            ),
            ChecklistItem(
                "GDPR-10", RequirementCategory.DOCUMENTATION.value,
                "Privacy notice",
                "Provide privacy notice to data subjects",
                "Review privacy notice completeness",
                "Privacy Notice", "High"
            ),
            ChecklistItem(
                "GDPR-11", RequirementCategory.GOVERNANCE.value,
                "Right to access",
                "Enable data subjects to access their personal data",
                "Test access request process",
                "System Test", "High"
            ),
            ChecklistItem(
                "GDPR-12", RequirementCategory.GOVERNANCE.value,
                "Right to rectification",
                "Allow data subjects to correct inaccurate data",
                "Test correction process",
                "System Test", "High"
            ),
            ChecklistItem(
                "GDPR-13", RequirementCategory.GOVERNANCE.value,
                "Right to erasure",
                "Provide capability to delete personal data",
                "Test deletion process and completeness",
                "System Test", "High"
            ),
            ChecklistItem(
                "GDPR-14", RequirementCategory.GOVERNANCE.value,
                "Right to restrict processing",
                "Allow data subjects to restrict processing",
                "Test restriction process",
                "System Test", "Medium"
            ),
            ChecklistItem(
                "GDPR-15", RequirementCategory.GOVERNANCE.value,
                "Right to data portability",
                "Enable export of personal data in structured format",
                "Test export functionality",
                "System Test", "Medium"
            ),
            ChecklistItem(
                "GDPR-16", RequirementCategory.GOVERNANCE.value,
                "Right to object",
                "Enable data subjects to object to processing",
                "Test objection process",
                "System Test", "Medium"
            ),
            ChecklistItem(
                "GDPR-17", RequirementCategory.TRAINING.value,
                "Staff training on GDPR",
                "Train staff on GDPR obligations",
                "Review training records",
                "Training Records", "Medium"
            ),
            ChecklistItem(
                "GDPR-18", RequirementCategory.AUDIT.value,
                "Privacy audit",
                "Conduct regular privacy audits",
                "Review audit reports",
                "Audit Report", "High"
            ),
            ChecklistItem(
                "GDPR-19", RequirementCategory.MONITORING.value,
                "International data transfers",
                "Ensure lawful mechanisms for international data transfers",
                "Review transfer mechanisms and SCCs",
                "Contracts", "High"
            ),
            ChecklistItem(
                "GDPR-20", RequirementCategory.GOVERNANCE.value,
                "Accountability and documentation",
                "Maintain records demonstrating GDPR compliance",
                "Review documentation and record-keeping",
                "Documentation", "Critical"
            ),
        ]

    def _get_iso_13485_requirements(self) -> List[ChecklistItem]:
        """ISO 13485 - 22 Requirements"""
        return [
            ChecklistItem(
                "ISO-13485-1", RequirementCategory.GOVERNANCE.value,
                "Quality management system scope",
                "Define scope of quality management system",
                "Review QMS documentation and scope statement",
                "Documentation", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-2", RequirementCategory.GOVERNANCE.value,
                "Quality policy",
                "Establish documented quality policy",
                "Review quality policy document",
                "Policy Document", "High"
            ),
            ChecklistItem(
                "ISO-13485-3", RequirementCategory.GOVERNANCE.value,
                "Management responsibility",
                "Define management responsibility and authority",
                "Review organization chart and responsibility matrix",
                "Documentation", "High"
            ),
            ChecklistItem(
                "ISO-13485-4", RequirementCategory.DOCUMENTATION.value,
                "Risk management",
                "Implement risk management process",
                "Review risk management reports",
                "Risk Management Report", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-5", RequirementCategory.IMPLEMENTATION.value,
                "Design and development",
                "Control design and development of medical devices",
                "Review design control documentation",
                "Design File", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-6", RequirementCategory.IMPLEMENTATION.value,
                "Supplier management",
                "Manage suppliers of materials and services",
                "Review supplier contracts and audits",
                "Supplier Assessment", "High"
            ),
            ChecklistItem(
                "ISO-13485-7", RequirementCategory.IMPLEMENTATION.value,
                "Traceability",
                "Maintain traceability of materials and components",
                "Review traceability systems",
                "Traceability Records", "High"
            ),
            ChecklistItem(
                "ISO-13485-8", RequirementCategory.TESTING.value,
                "Product validation",
                "Validate product meets intended use",
                "Review validation protocols and reports",
                "Validation Report", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-9", RequirementCategory.TESTING.value,
                "Product verification",
                "Verify product meets specifications",
                "Review verification protocols and test results",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-10", RequirementCategory.MONITORING.value,
                "Statistical analysis",
                "Use statistical methods for process control",
                "Review statistical process control data",
                "Statistical Report", "Medium"
            ),
            ChecklistItem(
                "ISO-13485-11", RequirementCategory.DOCUMENTATION.value,
                "Record control",
                "Maintain records of quality procedures",
                "Review record management system",
                "Record Management", "High"
            ),
            ChecklistItem(
                "ISO-13485-12", RequirementCategory.AUDIT.value,
                "Internal audit",
                "Conduct regular internal audits",
                "Review audit schedules and reports",
                "Audit Report", "High"
            ),
            ChecklistItem(
                "ISO-13485-13", RequirementCategory.IMPLEMENTATION.value,
                "Process validation",
                "Validate manufacturing processes",
                "Review process validation reports",
                "Validation Report", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-14", RequirementCategory.MONITORING.value,
                "Post-market surveillance",
                "Monitor product performance in market",
                "Review surveillance data and incident reports",
                "Surveillance Report", "High"
            ),
            ChecklistItem(
                "ISO-13485-15", RequirementCategory.INCIDENT_RESPONSE.value,
                "Adverse event reporting",
                "Report adverse events to authorities",
                "Review incident reporting procedures",
                "Procedures", "Critical"
            ),
            ChecklistItem(
                "ISO-13485-16", RequirementCategory.IMPLEMENTATION.value,
                "Nonconforming product",
                "Control handling of nonconforming products",
                "Review nonconformance handling procedures",
                "Procedures", "High"
            ),
            ChecklistItem(
                "ISO-13485-17", RequirementCategory.GOVERNANCE.value,
                "Corrective actions",
                "Implement corrective action procedures",
                "Review CAPA records",
                "CAPA Log", "High"
            ),
            ChecklistItem(
                "ISO-13485-18", RequirementCategory.TRAINING.value,
                "Staff training",
                "Train staff on quality procedures",
                "Review training records",
                "Training Records", "Medium"
            ),
            ChecklistItem(
                "ISO-13485-19", RequirementCategory.DOCUMENTATION.value,
                "Change management",
                "Control changes to processes and products",
                "Review change request procedures",
                "Change Log", "High"
            ),
            ChecklistItem(
                "ISO-13485-20", RequirementCategory.MONITORING.value,
                "Management review",
                "Conduct periodic management reviews",
                "Review meeting minutes and action items",
                "Meeting Minutes", "Medium"
            ),
            ChecklistItem(
                "ISO-13485-21", RequirementCategory.DOCUMENTATION.value,
                "Labeling and packaging",
                "Ensure correct labeling and packaging",
                "Review labeling procedures and samples",
                "Procedures", "High"
            ),
            ChecklistItem(
                "ISO-13485-22", RequirementCategory.IMPLEMENTATION.value,
                "Complaint handling",
                "Establish complaint handling procedures",
                "Review complaint logs and resolutions",
                "Complaint Log", "High"
            ),
        ]

    def _get_iec_62304_requirements(self) -> List[ChecklistItem]:
        """IEC 62304 - 18 Requirements"""
        return [
            ChecklistItem(
                "IEC-62304-1", RequirementCategory.GOVERNANCE.value,
                "Software lifecycle processes",
                "Define software development lifecycle processes",
                "Review software development plan",
                "Development Plan", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-2", RequirementCategory.DOCUMENTATION.value,
                "Software requirements specification",
                "Document all software requirements",
                "Review requirements specification completeness",
                "Requirements Spec", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-3", RequirementCategory.DOCUMENTATION.value,
                "Software architecture design",
                "Document software architecture and design",
                "Review design documentation",
                "Design Document", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-4", RequirementCategory.IMPLEMENTATION.value,
                "Software implementation",
                "Implement software according to specifications",
                "Review code and implementation",
                "Code Review", "High"
            ),
            ChecklistItem(
                "IEC-62304-5", RequirementCategory.TESTING.value,
                "Software unit verification",
                "Verify software units meet requirements",
                "Review unit test reports",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-6", RequirementCategory.TESTING.value,
                "Software integration testing",
                "Verify software units integrate correctly",
                "Review integration test reports",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-7", RequirementCategory.TESTING.value,
                "Software system verification",
                "Verify complete software system requirements",
                "Review system test reports",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-8", RequirementCategory.TESTING.value,
                "Software validation",
                "Validate software meets intended use",
                "Review validation test reports",
                "Validation Report", "Critical"
            ),
            ChecklistItem(
                "IEC-62304-9", RequirementCategory.DOCUMENTATION.value,
                "Software documentation",
                "Maintain complete software documentation",
                "Review documentation completeness",
                "Documentation", "High"
            ),
            ChecklistItem(
                "IEC-62304-10", RequirementCategory.GOVERNANCE.value,
                "Version control",
                "Maintain version control of software",
                "Review version control system",
                "Configuration Management", "High"
            ),
            ChecklistItem(
                "IEC-62304-11", RequirementCategory.MONITORING.value,
                "Software release and deployment",
                "Control software release and deployment",
                "Review release procedures",
                "Procedures", "High"
            ),
            ChecklistItem(
                "IEC-62304-12", RequirementCategory.MONITORING.value,
                "Traceability",
                "Maintain traceability from requirements to implementation",
                "Review traceability matrix",
                "Traceability Matrix", "High"
            ),
            ChecklistItem(
                "IEC-62304-13", RequirementCategory.GOVERNANCE.value,
                "Change management",
                "Control changes to software",
                "Review change procedures and logs",
                "Change Log", "High"
            ),
            ChecklistItem(
                "IEC-62304-14", RequirementCategory.INCIDENT_RESPONSE.value,
                "Problem reporting and resolution",
                "Report and resolve software problems",
                "Review problem reports",
                "Problem Log", "High"
            ),
            ChecklistItem(
                "IEC-62304-15", RequirementCategory.AUDIT.value,
                "Software configuration audits",
                "Conduct software configuration audits",
                "Review audit reports",
                "Audit Report", "Medium"
            ),
            ChecklistItem(
                "IEC-62304-16", RequirementCategory.TESTING.value,
                "Software testing documentation",
                "Document all software testing",
                "Review test documentation",
                "Test Documentation", "High"
            ),
            ChecklistItem(
                "IEC-62304-17", RequirementCategory.TRAINING.value,
                "Software development training",
                "Train developers on IEC 62304",
                "Review training records",
                "Training Records", "Medium"
            ),
            ChecklistItem(
                "IEC-62304-18", RequirementCategory.DOCUMENTATION.value,
                "Software maintenance records",
                "Maintain software maintenance records",
                "Review maintenance logs",
                "Maintenance Log", "Medium"
            ),
        ]

    def _get_fda_requirements(self) -> List[ChecklistItem]:
        """FDA - 20 Requirements"""
        return [
            ChecklistItem(
                "FDA-1", RequirementCategory.GOVERNANCE.value,
                "Quality management system",
                "Establish and maintain QMS per 21 CFR Part 11",
                "Review QMS documentation",
                "Documentation", "Critical"
            ),
            ChecklistItem(
                "FDA-2", RequirementCategory.DOCUMENTATION.value,
                "Electronic records",
                "Maintain electronic records per 21 CFR Part 11",
                "Review electronic record controls",
                "System Audit", "Critical"
            ),
            ChecklistItem(
                "FDA-3", RequirementCategory.DOCUMENTATION.value,
                "Electronic signatures",
                "Control electronic signatures per 21 CFR Part 11",
                "Review signature controls and audit trails",
                "System Audit", "Critical"
            ),
            ChecklistItem(
                "FDA-4", RequirementCategory.GOVERNANCE.value,
                "Predicate device comparison",
                "Document comparison to predicate devices",
                "Review 510(k) submission preparation",
                "Submission", "Critical"
            ),
            ChecklistItem(
                "FDA-5", RequirementCategory.TESTING.value,
                "Performance testing",
                "Conduct comprehensive performance testing",
                "Review performance test reports",
                "Test Report", "Critical"
            ),
            ChecklistItem(
                "FDA-6", RequirementCategory.IMPLEMENTATION.value,
                "Design controls",
                "Implement design control procedures",
                "Review design control documentation",
                "Design File", "Critical"
            ),
            ChecklistItem(
                "FDA-7", RequirementCategory.IMPLEMENTATION.value,
                "Risk analysis",
                "Conduct formal risk analysis (FMEA)",
                "Review risk analysis documentation",
                "Risk Analysis Report", "Critical"
            ),
            ChecklistItem(
                "FDA-8", RequirementCategory.TESTING.value,
                "Sterilization validation",
                "Validate sterilization if applicable",
                "Review sterilization validation reports",
                "Validation Report", "High"
            ),
            ChecklistItem(
                "FDA-9", RequirementCategory.DOCUMENTATION.value,
                "Labeling and instructions",
                "Prepare accurate labeling and instructions",
                "Review labeling and IFU completeness",
                "Labeling Documentation", "High"
            ),
            ChecklistItem(
                "FDA-10", RequirementCategory.IMPLEMENTATION.value,
                "Manufacturing controls",
                "Establish manufacturing process controls",
                "Review manufacturing procedures",
                "Procedures", "High"
            ),
            ChecklistItem(
                "FDA-11", RequirementCategory.TESTING.value,
                "Shelf life validation",
                "Validate appropriate shelf life",
                "Review stability testing data",
                "Test Report", "High"
            ),
            ChecklistItem(
                "FDA-12", RequirementCategory.MONITORING.value,
                "Post-market surveillance",
                "Maintain post-market surveillance data",
                "Review surveillance reports",
                "Surveillance Report", "High"
            ),
            ChecklistItem(
                "FDA-13", RequirementCategory.INCIDENT_RESPONSE.value,
                "Adverse event reporting",
                "Report adverse events to FDA (MedWatch)",
                "Review adverse event procedures",
                "Procedures", "Critical"
            ),
            ChecklistItem(
                "FDA-14", RequirementCategory.INCIDENT_RESPONSE.value,
                "Recalls and corrections",
                "Report recalls and corrections to FDA",
                "Review recall procedures",
                "Procedures", "Critical"
            ),
            ChecklistItem(
                "FDA-15", RequirementCategory.AUDIT.value,
                "Inspections readiness",
                "Maintain readiness for FDA inspections",
                "Review inspection readiness checklist",
                "Checklist", "Medium"
            ),
            ChecklistItem(
                "FDA-16", RequirementCategory.TRAINING.value,
                "Personnel training",
                "Train personnel on FDA requirements",
                "Review training records",
                "Training Records", "Medium"
            ),
            ChecklistItem(
                "FDA-17", RequirementCategory.DOCUMENTATION.value,
                "Change management",
                "Control changes affecting approved products",
                "Review change procedures",
                "Change Log", "High"
            ),
            ChecklistItem(
                "FDA-18", RequirementCategory.MONITORING.value,
                "Complaint handling",
                "Maintain complaint handling procedures",
                "Review complaint logs",
                "Complaint Log", "High"
            ),
            ChecklistItem(
                "FDA-19", RequirementCategory.GOVERNANCE.value,
                "Document control",
                "Maintain document control system",
                "Review document management procedures",
                "Procedures", "High"
            ),
            ChecklistItem(
                "FDA-20", RequirementCategory.DOCUMENTATION.value,
                "Regulatory submissions",
                "Prepare complete regulatory submissions",
                "Review submission completeness",
                "Submission", "High"
            ),
        ]

    def get_checklist(self, regulation: str) -> List[Dict]:
        """Get checklist for a specific regulation"""
        if regulation not in self.checklists:
            return []

        return [asdict(item) for item in self.checklists[regulation]]

    def get_all_checklists(self) -> Dict[str, List[Dict]]:
        """Get all checklists"""
        return {
            reg: [asdict(item) for item in items]
            for reg, items in self.checklists.items()
        }

    def get_summary(self) -> Dict:
        """Get checklist summary"""
        total_requirements = sum(len(items)
                                 for items in self.checklists.values())

        summary = {
            "total_requirements": total_requirements,
            "regulations": {}
        }

        for reg, items in self.checklists.items():
            summary["regulations"][reg] = {
                "count": len(items),
                "categories": self._get_category_breakdown(items)
            }

        return summary

    def _get_category_breakdown(self, items: List[ChecklistItem]) -> Dict:
        """Get category breakdown for items"""
        categories = {}
        for item in items:
            cat = item.category
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def export_checklists(self, filepath: str) -> bool:
        """Export all checklists to JSON"""
        try:
            all_checklists = self.get_all_checklists()
            summary = self.get_summary()

            export_data = {
                "summary": summary,
                "checklists": all_checklists
            }

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(
                f"Exported {sum(len(v) for v in all_checklists.values())} requirements to {filepath}")
            return True
        except Exception as e:
            print(f"Error exporting checklists: {e}")
            return False


# Example usage
if __name__ == "__main__":
    checklists = RequirementChecklists()

    # Get summary
    summary = checklists.get_summary()
    print("\n=== CHECKLIST SUMMARY ===")
    print(json.dumps(summary, indent=2))

    # Get specific regulation checklist
    eu_ai = checklists.get_checklist("EU-AI-Act")
    print(f"\n=== EU AI ACT CHECKLIST ({len(eu_ai)} items) ===")
    for item in eu_ai[:3]:  # First 3 items
        print(f"  {item['req_id']}: {item['description']}")

    # Export all
    checklists.export_checklists("compliance/checklists_export.json")
