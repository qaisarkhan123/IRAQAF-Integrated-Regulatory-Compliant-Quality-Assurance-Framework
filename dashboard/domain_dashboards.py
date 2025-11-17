"""
Domain-specific compliance dashboards for different regulatory bodies.
Provides customized visualizations and metrics for FDA, EPA, SEC, etc.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


class RegulatoryDomain:
    """Represents a regulatory domain with specific compliance rules and metrics."""
    
    DOMAINS = {
        "FDA": {
            "name": "Food and Drug Administration",
            "color": "#1f77b4",
            "icon": "🏥",
            "key_regulations": [
                "21 CFR Part 11 (Electronic Records)",
                "21 CFR Part 820 (Quality System)",
                "21 CFR Part 11 (Validation)",
                "FDASIA (Facility Inspection)",
                "Good Manufacturing Practice (GMP)"
            ],
            "metrics": [
                "inspection_readiness",
                "documentation_compliance",
                "training_completion",
                "deviation_closure_rate",
                "supplier_qualification_status"
            ]
        },
        "EPA": {
            "name": "Environmental Protection Agency",
            "color": "#2ca02c",
            "icon": "🌍",
            "key_regulations": [
                "Clean Air Act",
                "Clean Water Act",
                "Resource Conservation and Recovery Act",
                "Toxic Substances Control Act",
                "National Environmental Policy Act"
            ],
            "metrics": [
                "emission_compliance",
                "water_quality_index",
                "waste_management_score",
                "permit_renewal_status",
                "audit_findings_open"
            ]
        },
        "SEC": {
            "name": "Securities and Exchange Commission",
            "color": "#ff7f0e",
            "icon": "📈",
            "key_regulations": [
                "Dodd-Frank Act",
                "Sarbanes-Oxley (SOX)",
                "Securities Act of 1933",
                "Securities Exchange Act of 1934",
                "Regulation SHO"
            ],
            "metrics": [
                "financial_reporting_timeliness",
                "disclosure_completeness",
                "internal_control_effectiveness",
                "audit_compliance",
                "governance_score"
            ]
        },
        "ISO": {
            "name": "International Organization for Standardization",
            "color": "#d62728",
            "icon": "🔐",
            "key_regulations": [
                "ISO 9001 (Quality Management)",
                "ISO 14001 (Environmental Management)",
                "ISO 27001 (Information Security)",
                "ISO 45001 (Occupational Health and Safety)",
                "ISO 50001 (Energy Management)"
            ],
            "metrics": [
                "certification_status",
                "audit_results",
                "non_conformance_count",
                "process_effectiveness",
                "continuous_improvement_initiatives"
            ]
        },
        "GDPR": {
            "name": "General Data Protection Regulation",
            "color": "#9467bd",
            "icon": "🔒",
            "key_regulations": [
                "Right to Access",
                "Right to Erasure",
                "Right to Rectification",
                "Right to Restrict Processing",
                "Data Breach Notification"
            ],
            "metrics": [
                "dpia_completion_rate",
                "consent_tracking",
                "data_breach_response_time",
                "dsr_resolution_time",
                "privacy_training_completion"
            ]
        }
    }
    
    def __init__(self, domain_code: str):
        """Initialize domain."""
        if domain_code not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain_code}")
        self.code = domain_code
        self.config = self.DOMAINS[domain_code]
    
    def get_name(self) -> str:
        """Get domain full name."""
        return self.config["name"]
    
    def get_color(self) -> str:
        """Get domain color for visualizations."""
        return self.config["color"]
    
    def get_icon(self) -> str:
        """Get domain icon."""
        return self.config["icon"]
    
    def get_regulations(self) -> List[str]:
        """Get key regulations for this domain."""
        return self.config["key_regulations"]
    
    def get_metrics(self) -> List[str]:
        """Get key metrics for this domain."""
        return self.config["metrics"]


class DomainDashboard:
    """Creates domain-specific compliance dashboards."""
    
    def __init__(self, domain_code: str):
        """Initialize domain dashboard."""
        self.domain = RegulatoryDomain(domain_code)
        self.data_dir = Path.cwd() / "data" / "domain_dashboards"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def display_domain_overview(self) -> None:
        """Display domain overview with key information."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Domain",
                value=self.domain.get_name(),
                delta=self.domain.get_icon()
            )
        
        with col2:
            st.metric(
                label="Key Regulations",
                value=len(self.domain.get_regulations())
            )
        
        with col3:
            st.metric(
                label="Key Metrics",
                value=len(self.domain.get_metrics())
            )
    
    def display_regulations(self) -> None:
        """Display key regulations for the domain."""
        st.subheader(f"📋 Key Regulations - {self.domain.get_name()}")
        
        regulations = self.domain.get_regulations()
        for i, regulation in enumerate(regulations, 1):
            st.markdown(f"**{i}. {regulation}**")
    
    def display_metrics(self) -> None:
        """Display key metrics dashboard."""
        st.subheader(f"📊 Compliance Metrics - {self.domain.get_name()}")
        
        metrics = self.domain.get_metrics()
        cols = st.columns(2)
        
        for i, metric in enumerate(metrics):
            with cols[i % 2]:
                # Generate sample metric value (in real implementation, get from data)
                value = 85 + (hash(metric) % 15)
                delta = (hash(metric) % 10) - 5
                st.metric(
                    label=metric.replace("_", " ").title(),
                    value=f"{value}%",
                    delta=f"{delta:+d}%"
                )
    
    def display_compliance_timeline(self, days: int = 30) -> None:
        """Display compliance events timeline."""
        st.subheader(f"📅 Compliance Timeline - Last {days} Days")
        
        # Generate sample timeline data
        timeline_data = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            event_type = ["Audit", "Update", "Finding", "Training"][hash(str(date)) % 4]
            status = ["✅ Compliant", "⚠️ At Risk", "🔴 Non-Compliant"][hash(str(date)) % 3]
            
            timeline_data.append({
                "Date": date,
                "Event": event_type,
                "Status": status,
                "Details": f"{event_type} event for {self.domain.code}"
            })
        
        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    def display_audit_readiness(self) -> None:
        """Display audit readiness scorecard."""
        st.subheader(f"🎯 Audit Readiness - {self.domain.get_name()}")
        
        metrics = {
            "Documentation": 92,
            "Training Records": 88,
            "Internal Audits": 95,
            "Corrective Actions": 85,
            "System Controls": 90,
            "Risk Assessment": 87
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            for metric, score in list(metrics.items())[:3]:
                st.metric(metric, f"{score}%")
        
        with col2:
            for metric, score in list(metrics.items())[3:]:
                st.metric(metric, f"{score}%")
        
        # Overall score
        overall = sum(metrics.values()) // len(metrics)
        st.markdown("---")
        
        if overall >= 90:
            status = "🟢 Audit Ready"
        elif overall >= 80:
            status = "🟡 Minor Gaps"
        else:
            status = "🔴 Significant Gaps"
        
        st.metric("Overall Readiness", f"{overall}%", status)
    
    def display_recent_findings(self) -> None:
        """Display recent audit findings and issues."""
        st.subheader(f"🔍 Recent Findings - {self.domain.get_name()}")
        
        findings = [
            {
                "Finding ID": "F-001",
                "Date": "2024-11-15",
                "Severity": "High",
                "Description": "Missing training documentation",
                "Status": "Open",
                "Due Date": "2024-12-15"
            },
            {
                "Finding ID": "F-002",
                "Date": "2024-11-10",
                "Severity": "Medium",
                "Description": "Outdated procedure",
                "Status": "In Progress",
                "Due Date": "2024-12-01"
            },
            {
                "Finding ID": "F-003",
                "Date": "2024-11-05",
                "Severity": "Low",
                "Description": "Minor documentation error",
                "Status": "Closed",
                "Due Date": "2024-11-30"
            }
        ]
        
        df = pd.DataFrame(findings)
        
        # Color code severity
        def color_severity(val):
            if val == "High":
                return "color: red"
            elif val == "Medium":
                return "color: orange"
            else:
                return "color: green"
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    def export_domain_report(self) -> bytes:
        """Export domain compliance report."""
        from exports import ExportManager
        
        exporter = ExportManager()
        
        sections = [
            {
                "heading": "Regulatory Overview",
                "content": f"This report covers compliance for {self.domain.get_name()} "
                          f"domain. Key regulations include: {', '.join(self.domain.get_regulations()[:3])}"
            },
            {
                "heading": "Key Metrics",
                "content": f"Tracked metrics: {', '.join(self.domain.get_metrics()[:3])}"
            },
            {
                "heading": "Audit Status",
                "content": "Overall audit readiness: 89% - Minor gaps identified"
            }
        ]
        
        return exporter.generate_compliance_report_pdf(
            title=f"{self.domain.get_name()} Compliance Report",
            executive_summary=f"Compliance assessment for {self.domain.code} domain",
            sections=sections,
            metadata={"domain": self.domain.code, "generated": datetime.now().isoformat()}
        )


def render_domain_selector() -> Optional[str]:
    """Render domain selection UI and return selected domain."""
    st.sidebar.markdown("### 🌐 Regulatory Domains")
    
    domains = list(RegulatoryDomain.DOMAINS.keys())
    selected = st.sidebar.selectbox(
        "Select Domain",
        domains,
        index=0
    )
    
    return selected


def display_all_domains_overview() -> None:
    """Display overview of all regulatory domains."""
    st.subheader("📊 Regulatory Domains Overview")
    
    cols = st.columns(3)
    
    for i, (code, config) in enumerate(RegulatoryDomain.DOMAINS.items()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {config['icon']} {code}")
                st.markdown(f"*{config['name']}*")
                st.markdown(f"Regulations: {len(config['key_regulations'])}")
                st.markdown(f"Metrics: {len(config['metrics'])}")
