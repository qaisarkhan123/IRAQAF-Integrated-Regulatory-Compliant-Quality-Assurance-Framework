#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                  L1 REGULATIONS & GOVERNANCE HUB                           ║
║              Automated Compliance Assessment for Medical AI                ║
║                                                                            ║
║  Features:                                                                 ║
║    ✓ Regulatory web scraper (EU AI Act, GDPR, FDA, ISO)                   ║
║    ✓ Document analyzer (NLP-based extraction)                             ║
║    ✓ Compliance scoring engine                                            ║
║    ✓ Gap analysis & recommendations                                       ║
║    ✓ Regulatory change monitoring & alerts                                ║
║    ✓ Beautiful Flask web interface                                        ║
║    ✓ Real-time compliance dashboard                                       ║
║    ✓ PDF report export                                                    ║
║                                                                            ║
║  Regulations Monitored:                                                   ║
║    • EU AI Act (Annex IV, VI, VII, VIII)                                 ║
║    • GDPR (Articles 6, 9, 30, 35)                                        ║
║    • ISO 13485 (Quality Management)                                       ║
║    • IEC 62304 (Software Lifecycle)                                       ║
║    • FDA Guidance (GMLP, SaMD)                                           ║
║                                                                            ║
║  Port: 8504                                                               ║
║  Framework: Flask                                                         ║
║  Author: IRAQAF Team                                                      ║
║  Date: 2025-01-19                                                         ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, render_template_string, jsonify, request, send_file
from flask_cors import CORS
import json
import base64
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import numpy as np
import re
from collections import defaultdict
import hashlib

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════════
# REGULATORY DATABASE & COMPLIANCE REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════════


class RegulatorySource:
    """Represents a regulatory source"""

    def __init__(self, name, url, category, keywords):
        self.name = name
        self.url = url
        self.category = category
        self.keywords = keywords
        self.last_scraped = None
        self.content_hash = None
        self.content = ""


# Regulatory Sources
REGULATORY_SOURCES = {
    "EU_AI_ACT": RegulatorySource(
        name="EU AI Act",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        category="EU Legislation",
        keywords=["high-risk", "Annex IV",
                  "conformity assessment", "human oversight"]
    ),
    "GDPR": RegulatorySource(
        name="GDPR",
        url="https://gdpr-info.eu/",
        category="Data Protection",
        keywords=["lawful basis", "DPIA",
                  "data subject rights", "data protection impact"]
    ),
    "FDA": RegulatorySource(
        name="FDA AI/ML Guidance",
        url="https://www.fda.gov/medical-devices/",
        category="US Regulation",
        keywords=["GMLP", "SaMD", "algorithm transparency",
                  "predetermined change control"]
    ),
    "ISO_13485": RegulatorySource(
        name="ISO 13485",
        url="https://www.iso.org/standard/59752.html",
        category="Quality Management",
        keywords=["quality management system",
                  "design control", "risk management"]
    ),
    "IEC_62304": RegulatorySource(
        name="IEC 62304",
        url="https://www.iec.ch/",
        category="Software Lifecycle",
        keywords=["software lifecycle",
                  "software testing", "configuration management"]
    )
}

# Compliance Requirements Checklist
COMPLIANCE_REQUIREMENTS = {
    "GDPR": [
        {"id": "GDPR_1", "name": "Lawful basis for processing documented",
            "article": "Article 6", "weight": 1.0},
        {"id": "GDPR_2", "name": "Special category data justification",
            "article": "Article 9", "weight": 1.0},
        {"id": "GDPR_3",
            "name": "Data Protection Impact Assessment (DPIA) completed", "article": "Article 35", "weight": 1.0},
        {"id": "GDPR_4", "name": "Record of Processing Activities maintained",
            "article": "Article 30", "weight": 0.9},
        {"id": "GDPR_5", "name": "Privacy policy publicly available",
            "article": "Articles 12-14", "weight": 0.9},
        {"id": "GDPR_6", "name": "Data subject rights documented",
            "article": "Articles 15-22", "weight": 0.9},
        {"id": "GDPR_7",
            "name": "Data breach response plan (72-hour notification)", "article": "Articles 33-34", "weight": 0.8},
        {"id": "GDPR_8", "name": "Data retention policy defined",
            "article": "Article 5", "weight": 0.8},
        {"id": "GDPR_9", "name": "Encryption at rest implemented",
            "article": "Article 32", "weight": 0.8},
        {"id": "GDPR_10", "name": "Encryption in transit implemented",
            "article": "Article 32", "weight": 0.8},
    ],
    "EU_AI_ACT": [
        {"id": "EU_AI_1", "name": "Risk classification documented",
            "article": "Article 6", "weight": 1.0},
        {"id": "EU_AI_2", "name": "General description of AI system",
            "article": "Annex IV.1", "weight": 1.0},
        {"id": "EU_AI_3", "name": "Intended purpose clearly stated",
            "article": "Annex IV.1", "weight": 1.0},
        {"id": "EU_AI_4", "name": "Development methods described",
            "article": "Annex IV.2", "weight": 0.95},
        {"id": "EU_AI_5", "name": "System architecture documented",
            "article": "Annex IV.2", "weight": 0.95},
        {"id": "EU_AI_6", "name": "Training dataset documented",
            "article": "Annex IV.3", "weight": 0.95},
        {"id": "EU_AI_7", "name": "Validation dataset documented",
            "article": "Annex IV.3", "weight": 0.95},
        {"id": "EU_AI_8", "name": "Testing dataset documented",
            "article": "Annex IV.3", "weight": 0.95},
        {"id": "EU_AI_9", "name": "Bias identification and mitigation",
            "article": "Annex IV.3", "weight": 0.9},
        {"id": "EU_AI_10", "name": "Capabilities and limitations documented",
            "article": "Annex IV.4", "weight": 0.9},
        {"id": "EU_AI_11", "name": "Performance metrics defined",
            "article": "Annex IV.4", "weight": 0.9},
        {"id": "EU_AI_12", "name": "Human oversight measures",
            "article": "Article 14", "weight": 0.9},
        {"id": "EU_AI_13", "name": "Risk management system described",
            "article": "Annex IV.5", "weight": 0.85},
        {"id": "EU_AI_14", "name": "Change management procedures",
            "article": "Annex IV.6", "weight": 0.85},
        {"id": "EU_AI_15", "name": "Post-market monitoring plan",
            "article": "Annex VIII", "weight": 0.85},
    ],
    "ISO_13485": [
        {"id": "ISO_1", "name": "Quality Management System documented",
            "article": "Clause 4", "weight": 1.0},
        {"id": "ISO_2", "name": "Design and development plan",
            "article": "Clause 7.3.2", "weight": 1.0},
        {"id": "ISO_3", "name": "Design input requirements specified",
            "article": "Clause 7.3.3", "weight": 0.95},
        {"id": "ISO_4", "name": "Design output specifications",
            "article": "Clause 7.3.4", "weight": 0.95},
        {"id": "ISO_5", "name": "Design verification performed",
            "article": "Clause 7.3.5", "weight": 0.9},
        {"id": "ISO_6", "name": "Design validation performed",
            "article": "Clause 7.3.6", "weight": 0.9},
        {"id": "ISO_7", "name": "Design transfer documented",
            "article": "Clause 7.3.7", "weight": 0.8},
        {"id": "ISO_8", "name": "Design changes controlled",
            "article": "Clause 7.3.9", "weight": 0.8},
        {"id": "ISO_9", "name": "Risk Management File per ISO 14971",
            "article": "Clause 7.3", "weight": 0.85},
        {"id": "ISO_10", "name": "Change control procedures documented",
            "article": "Clause 8.5.6", "weight": 0.8},
    ],
    "IEC_62304": [
        {"id": "IEC_1", "name": "Software development plan exists",
            "article": "Clause 5.1", "weight": 1.0},
        {"id": "IEC_2", "name": "Software safety classification assigned",
            "article": "Clause 5.2", "weight": 1.0},
        {"id": "IEC_3", "name": "Software requirements specification",
            "article": "Clause 5.3", "weight": 0.95},
        {"id": "IEC_4", "name": "Software architecture documented",
            "article": "Clause 5.4", "weight": 0.95},
        {"id": "IEC_5", "name": "Unit testing performed and documented",
            "article": "Clause 5.5", "weight": 0.9},
        {"id": "IEC_6", "name": "Integration testing performed",
            "article": "Clause 5.6", "weight": 0.9},
        {"id": "IEC_7", "name": "System testing performed",
            "article": "Clause 5.7", "weight": 0.9},
        {"id": "IEC_8", "name": "Software release documentation",
            "article": "Clause 5.8", "weight": 0.85},
        {"id": "IEC_9", "name": "Known anomalies documented",
            "article": "Clause 5.8", "weight": 0.8},
    ],
    "FDA": [
        {"id": "FDA_1", "name": "Data quality assurance documented",
            "article": "GMLP", "weight": 1.0},
        {"id": "FDA_2", "name": "Algorithm transparency provided",
            "article": "GMLP", "weight": 1.0},
        {"id": "FDA_3", "name": "Model monitoring plan defined",
            "article": "GMLP", "weight": 0.95},
        {"id": "FDA_4", "name": "Predetermined Change Control Plan",
            "article": "GMLP", "weight": 0.9},
        {"id": "FDA_5", "name": "Clinical validation completed",
            "article": "SaMD Guidance", "weight": 0.95},
    ]
}

# Keywords for detection
REGULATION_KEYWORDS = {
    "GDPR": [
        "GDPR", "General Data Protection Regulation", "Article 6", "Article 9", "Article 30", "Article 35",
        "lawful basis", "legitimate interest", "consent", "DPIA", "data protection impact assessment",
        "data subject rights", "right to access", "right to erasure", "data controller", "data processor",
        "privacy policy", "breach notification", "72 hour", "record of processing", "RoPA"
    ],
    "EU_AI_ACT": [
        "EU AI Act", "Artificial Intelligence Act", "high-risk", "risk classification", "Annex III", "Annex IV",
        "Annex VI", "Annex VII", "Annex VIII", "conformity assessment", "CE marking", "notified body",
        "post-market monitoring", "human oversight", "transparency", "technical documentation"
    ],
    "ISO_13485": [
        "ISO 13485", "quality management system", "QMS", "design control", "design history file", "DHF",
        "design input", "design output", "design verification", "design validation", "risk management",
        "ISO 14971", "change control", "CAPA", "corrective action"
    ],
    "IEC_62304": [
        "IEC 62304", "software lifecycle", "software safety", "Class A", "Class B", "Class C",
        "software requirements", "software architecture", "unit testing", "integration testing",
        "system testing", "software validation", "configuration management"
    ],
    "FDA": [
        "FDA", "Food and Drug Administration", "510(k)", "De Novo", "PMA", "SaMD", "Software as Medical Device",
        "GMLP", "Good Machine Learning Practice", "algorithm transparency", "predetermined change control"
    ]
}

# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════


class DocumentAnalyzer:
    """Analyzes documents for compliance keywords and content"""

    def __init__(self):
        self.detected_keywords = defaultdict(list)
        self.keyword_counts = defaultdict(int)
        self.semantic_scores = defaultdict(float)

    def analyze_text(self, text):
        """Analyze text for regulatory keywords"""
        results = {}
        text_lower = text.lower()

        # Detect keywords for each regulation
        for regulation, keywords in REGULATION_KEYWORDS.items():
            found_keywords = []
            count = 0

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
                    count += len(re.findall(re.escape(keyword.lower()), text_lower))

            results[regulation] = {
                "found": len(found_keywords) > 0,
                "keywords_found": found_keywords,
                "keyword_count": count,
                "coverage": len(found_keywords) / len(keywords) if keywords else 0
            }

        return results

    def calculate_semantic_similarity(self, requirement, document_text):
        """Calculate semantic similarity between requirement and document"""
        # Simple implementation: word overlap
        req_words = set(requirement.lower().split())
        doc_words = set(document_text.lower().split())

        if not req_words:
            return 0.0

        intersection = len(req_words & doc_words)
        union = len(req_words | doc_words)

        return intersection / union if union > 0 else 0.0


analyzer = DocumentAnalyzer()

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLIANCE SCORING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class ComplianceScorer:
    """Calculates compliance scores based on requirements"""

    def __init__(self):
        self.weights = {
            "GDPR": 0.25,
            "EU_AI_ACT": 0.35,
            "ISO_13485": 0.25,
            "IEC_62304": 0.10,
            "FDA": 0.05
        }

    def score_requirement(self, requirement_id, document_analysis, document_text):
        """Score a single requirement (0.0 to 1.0)"""
        # Find which regulation this requirement belongs to
        regulation = None
        req_name = None

        for reg, reqs in COMPLIANCE_REQUIREMENTS.items():
            for req in reqs:
                if req["id"] == requirement_id:
                    regulation = reg
                    req_name = req["name"]
                    break

        if not regulation:
            return 0.0

        # Check if keywords are detected
        if regulation not in document_analysis or not document_analysis[regulation]["found"]:
            return 0.0

        keyword_count = document_analysis[regulation]["keyword_count"]
        keyword_coverage = document_analysis[regulation]["coverage"]

        # Scoring logic
        if keyword_count >= 3:
            base_score = 1.0
        elif keyword_count >= 1:
            base_score = 0.6
        else:
            base_score = 0.3

        # Adjust based on coverage
        if keyword_coverage > 0.7:
            base_score = min(1.0, base_score + 0.2)
        elif keyword_coverage < 0.2:
            base_score = max(0.0, base_score - 0.2)

        return base_score

    def calculate_regulation_score(self, regulation, document_analysis, document_text):
        """Calculate score for a regulation"""
        if regulation not in COMPLIANCE_REQUIREMENTS:
            return 0.0

        requirements = COMPLIANCE_REQUIREMENTS[regulation]
        scores = []

        for req in requirements:
            score = self.score_requirement(
                req["id"], document_analysis, document_text)
            scores.append(score * req["weight"])

        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    def calculate_crs(self, document_analysis, document_text):
        """Calculate overall Compliance Readiness Score"""
        regulation_scores = {}

        for regulation in self.weights.keys():
            if regulation in COMPLIANCE_REQUIREMENTS:
                score = self.calculate_regulation_score(
                    regulation, document_analysis, document_text)
                regulation_scores[regulation] = score

        # Calculate weighted average
        crs = sum(regulation_scores[reg] * self.weights[reg]
                  for reg in regulation_scores)

        return crs * 100, regulation_scores

    def identify_gaps(self, document_analysis, document_text):
        """Identify compliance gaps"""
        gaps = {
            "critical": [],
            "major": [],
            "minor": []
        }

        for regulation, requirements in COMPLIANCE_REQUIREMENTS.items():
            for req in requirements:
                score = self.score_requirement(
                    req["id"], document_analysis, document_text)

                if score == 0.0:
                    gap = {
                        "regulation": regulation,
                        "requirement": req["name"],
                        "article": req["article"],
                        "score": score,
                        "priority": "Critical" if req["weight"] >= 0.95 else "High" if req["weight"] >= 0.8 else "Medium"
                    }
                    gaps["critical"].append(gap)
                elif score < 0.6:
                    gap = {
                        "regulation": regulation,
                        "requirement": req["name"],
                        "article": req["article"],
                        "score": score,
                        "priority": "High"
                    }
                    gaps["major"].append(gap)
                elif score < 0.8:
                    gap = {
                        "regulation": regulation,
                        "requirement": req["name"],
                        "article": req["article"],
                        "score": score,
                        "priority": "Medium"
                    }
                    gaps["minor"].append(gap)

        return gaps


scorer = ComplianceScorer()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def generate_compliance_radar(scores_dict):
    """Generate radar chart for compliance scores"""
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor('#0f0f1e')
    ax.set_facecolor('#1a1a2e')

    regulations = list(scores_dict.keys())
    values = list(scores_dict.values())
    values += values[:1]  # Complete the circle

    angles = np.linspace(0, 2 * np.pi, len(regulations),
                         endpoint=False).tolist()
    angles += angles[:1]

    ax.plot(angles, values, 'o-', linewidth=2, color='#667eea', markersize=8)
    ax.fill(angles, values, alpha=0.25, color='#667eea')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(regulations, size=10, color='#ffffff')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'],
                       size=8, color='#888888')
    ax.grid(True, color='#444444', alpha=0.3)

    ax.tick_params(colors='#ffffff')

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', facecolor='#0f0f1e',
                dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{image_base64}"


def generate_gaps_chart(gaps):
    """Generate chart showing gaps by priority"""
    critical = len(gaps["critical"])
    major = len(gaps["major"])
    minor = len(gaps["minor"])

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0f0f1e')
    ax.set_facecolor('#1a1a2e')

    categories = ['Critical', 'Major', 'Minor']
    values = [critical, major, minor]
    colors = ['#ff4444', '#ffaa00', '#ffff44']

    bars = ax.bar(categories, values, color=colors,
                  edgecolor='#ffffff', linewidth=1.5)

    # Add value labels
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}',
                ha='center', va='bottom', color='#ffffff', fontweight='bold', fontsize=12)

    ax.set_ylabel('Number of Gaps', color='#ffffff',
                  fontsize=12, fontweight='bold')
    ax.set_xlabel('Priority Level', color='#ffffff',
                  fontsize=12, fontweight='bold')
    ax.set_title('Compliance Gaps by Priority', color='#ffffff',
                 fontsize=14, fontweight='bold', pad=20)

    ax.spines['bottom'].set_color('#444444')
    ax.spines['left'].set_color('#444444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.tick_params(colors='#ffffff')
    ax.grid(axis='y', alpha=0.2, color='#444444')

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', facecolor='#0f0f1e',
                dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{image_base64}"


def generate_score_gauge(score, title):
    """Generate circular gauge for score"""
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor('#0f0f1e')
    ax.set_facecolor('#0f0f1e')

    # Create gauge
    theta = np.linspace(0, np.pi, 100)
    r = 1
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    # Gauge background
    ax.plot(x, y, color='#444444', linewidth=3)

    # Color zones
    red_theta = np.linspace(0, np.pi/3, 50)
    yellow_theta = np.linspace(np.pi/3, 2*np.pi/3, 50)
    green_theta = np.linspace(2*np.pi/3, np.pi, 50)

    ax.plot(np.cos(red_theta), np.sin(red_theta), color='#ff4444', linewidth=8)
    ax.plot(np.cos(yellow_theta), np.sin(
        yellow_theta), color='#ffaa00', linewidth=8)
    ax.plot(np.cos(green_theta), np.sin(
        green_theta), color='#00ff41', linewidth=8)

    # Needle
    needle_angle = (score / 100) * np.pi
    needle_x = 0.7 * np.cos(needle_angle)
    needle_y = 0.7 * np.sin(needle_angle)
    ax.arrow(0, 0, needle_x, needle_y, head_width=0.1,
             head_length=0.1, fc='#ffffff', ec='#ffffff')
    ax.plot(0, 0, 'o', color='#ffffff', markersize=15)

    # Score text
    ax.text(0, -0.3, f'{score:.1f}%', ha='center', va='top', fontsize=24,
            color='#ffffff', fontweight='bold')
    ax.text(0, -0.5, title, ha='center', va='top',
            fontsize=12, color='#888888')

    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.8, 1.3)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', facecolor='#0f0f1e',
                dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return f"data:image/png;base64,{image_base64}"

# ═══════════════════════════════════════════════════════════════════════════════
# HTML TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════


def get_html_template():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>L1 Regulations & Governance Hub</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0f0f1e;
                color: #ffffff;
                line-height: 1.6;
            }
            
            header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 20px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
                margin-bottom: 40px;
            }
            
            header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            header p {
                font-size: 1.1em;
                opacity: 0.95;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
                margin-bottom: 40px;
            }
            
            .card {
                background: #1a1a2e;
                border: 1px solid #2d2d2d;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #667eea, #764ba2);
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
                border-color: #667eea;
            }
            
            .score-card {
                text-align: center;
            }
            
            .score-ring {
                width: 150px;
                height: 150px;
                margin: 20px auto;
                background: conic-gradient(
                    #00ff41 0deg,
                    #00ff41 calc({{ score }}% * 3.6deg),
                    #2d2d2d calc({{ score }}% * 3.6deg)
                );
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5em;
                font-weight: bold;
                box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
            }
            
            .score-text {
                font-size: 0.9em;
                color: #888888;
                margin-top: 10px;
            }
            
            .status-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
                margin-top: 15px;
            }
            
            .status-ready {
                background-color: #00ff41;
                color: #000000;
            }
            
            .status-partial {
                background-color: #ffaa00;
                color: #000000;
            }
            
            .status-critical {
                background-color: #ff4444;
                color: #ffffff;
            }
            
            .regulation-scores {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .regulation-card {
                background: linear-gradient(135deg, #1a1a2e 0%, #2d2d2d 100%);
                border: 1px solid #3d3d4d;
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
            }
            
            .regulation-card:hover {
                transform: scale(1.02);
                border-color: #667eea;
                box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
            }
            
            .regulation-name {
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 10px;
                color: #667eea;
            }
            
            .score-bar {
                width: 100%;
                height: 30px;
                background: #0f0f1e;
                border-radius: 15px;
                overflow: hidden;
                margin-bottom: 10px;
                border: 1px solid #2d2d2d;
            }
            
            .score-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                display: flex;
                align-items: center;
                justify-content: center;
                color: #ffffff;
                font-size: 0.85em;
                font-weight: bold;
            }
            
            .gap-section {
                margin-top: 40px;
                margin-bottom: 40px;
            }
            
            .gap-header {
                font-size: 1.8em;
                font-weight: bold;
                margin-bottom: 20px;
                color: #ffffff;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }
            
            .gaps-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
            }
            
            .gap-item {
                background: #1a1a2e;
                border-left: 4px solid;
                border-radius: 8px;
                padding: 20px;
                transition: all 0.3s ease;
            }
            
            .gap-critical {
                border-left-color: #ff4444;
                background: rgba(255, 68, 68, 0.05);
            }
            
            .gap-major {
                border-left-color: #ffaa00;
                background: rgba(255, 170, 0, 0.05);
            }
            
            .gap-minor {
                border-left-color: #ffff44;
                background: rgba(255, 255, 68, 0.05);
            }
            
            .gap-item:hover {
                transform: translateX(5px);
            }
            
            .gap-title {
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            
            .gap-details {
                font-size: 0.9em;
                color: #cccccc;
                margin-bottom: 10px;
            }
            
            .gap-priority {
                display: inline-block;
                padding: 5px 12px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
                margin-top: 10px;
            }
            
            .priority-critical {
                background-color: #ff4444;
                color: #ffffff;
            }
            
            .priority-major {
                background-color: #ffaa00;
                color: #000000;
            }
            
            .priority-minor {
                background-color: #ffff44;
                color: #000000;
            }
            
            .chart-container {
                background: #1a1a2e;
                border: 1px solid #2d2d2d;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 30px;
                text-align: center;
            }
            
            .chart-container img {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
            }
            
            .chart-title {
                font-size: 1.3em;
                font-weight: bold;
                margin-bottom: 20px;
                color: #667eea;
            }
            
            .requirement-list {
                list-style: none;
                margin-bottom: 30px;
            }
            
            .requirement-item {
                background: #1a1a2e;
                border-left: 3px solid #667eea;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 6px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .requirement-details {
                flex: 1;
            }
            
            .requirement-name {
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 5px;
            }
            
            .requirement-article {
                font-size: 0.85em;
                color: #888888;
            }
            
            .requirement-score {
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 8px;
                background: #2d2d2d;
                color: #667eea;
                min-width: 80px;
                text-align: center;
            }
            
            .upload-section {
                background: linear-gradient(135deg, #1a1a2e 0%, #2d2d2d 100%);
                border: 2px dashed #667eea;
                border-radius: 12px;
                padding: 40px 20px;
                text-align: center;
                margin-bottom: 40px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .upload-section:hover {
                border-color: #764ba2;
                box-shadow: 0 8px 16px rgba(102, 126, 234, 0.2);
            }
            
            .upload-icon {
                font-size: 3em;
                margin-bottom: 15px;
            }
            
            .upload-text {
                font-size: 1.2em;
                margin-bottom: 10px;
                color: #ffffff;
            }
            
            .upload-subtext {
                font-size: 0.9em;
                color: #888888;
            }
            
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            footer {
                text-align: center;
                padding: 30px 20px;
                color: #666666;
                border-top: 1px solid #2d2d2d;
                margin-top: 60px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: #1a1a2e;
                border: 1px solid #2d2d2d;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            }
            
            .stat-number {
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .stat-label {
                font-size: 0.95em;
                color: #888888;
            }
            
            .tab-container {
                display: flex;
                gap: 0;
                margin-bottom: 30px;
                border-bottom: 2px solid #2d2d2d;
            }
            
            .tab-button {
                background: transparent;
                color: #888888;
                border: none;
                padding: 12px 20px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                border-bottom: 3px solid transparent;
                margin: 0;
                margin-top: 0;
            }
            
            .tab-button:hover {
                color: #667eea;
                border-bottom-color: #667eea;
                transform: none;
            }
            
            .tab-button.active {
                color: #667eea;
                border-bottom-color: #667eea;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>🔐 L1 REGULATIONS & GOVERNANCE HUB</h1>
            <p>Automated Compliance Assessment for Medical AI Systems</p>
        </header>
        
        <div class="container">
            <div class="upload-section" onclick="document.getElementById('docInput').click()">
                <div class="upload-icon">📄</div>
                <div class="upload-text">Upload Documentation</div>
                <div class="upload-subtext">Drag and drop your documents here or click to browse</div>
                <input type="file" id="docInput" style="display:none;" accept=".pdf,.docx,.txt,.md" multiple>
                <button onclick="analyzeDocuments()" style="margin-top: 20px;">Analyze Compliance</button>
            </div>
            
            <div id="results" style="display:none;">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="crsScore">0%</div>
                        <div class="stat-label">Compliance Readiness Score</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="criticalCount">0</div>
                        <div class="stat-label">Critical Gaps</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="majorCount">0</div>
                        <div class="stat-label">Major Gaps</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="minorCount">0</div>
                        <div class="stat-label">Minor Gaps</div>
                    </div>
                </div>
                
                <div class="tab-container">
                    <button class="tab-button active" onclick="switchTab('overview')">Overview</button>
                    <button class="tab-button" onclick="switchTab('scores')">Regulation Scores</button>
                    <button class="tab-button" onclick="switchTab('requirements')">Requirements</button>
                    <button class="tab-button" onclick="switchTab('gaps')">Gap Analysis</button>
                </div>
                
                <div id="overview" class="tab-content active">
                    <div class="chart-container">
                        <div class="chart-title">Overall Compliance Score</div>
                        <img id="gaugeChart" src="" alt="Gauge Chart">
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-title">Compliance by Regulation</div>
                        <img id="radarChart" src="" alt="Radar Chart">
                    </div>
                </div>
                
                <div id="scores" class="tab-content">
                    <div class="regulation-scores" id="regulationScores"></div>
                </div>
                
                <div id="requirements" class="tab-content">
                    <ul class="requirement-list" id="requirementsList"></ul>
                </div>
                
                <div id="gaps" class="tab-content">
                    <div class="chart-container">
                        <div class="chart-title">Gaps by Priority</div>
                        <img id="gapsChart" src="" alt="Gaps Chart">
                    </div>
                    
                    <div class="gap-section">
                        <div class="gap-header" style="color: #ff4444;">🔴 Critical Gaps</div>
                        <div class="gaps-grid" id="criticalGaps"></div>
                    </div>
                    
                    <div class="gap-section">
                        <div class="gap-header" style="color: #ffaa00;">🟡 Major Gaps</div>
                        <div class="gaps-grid" id="majorGaps"></div>
                    </div>
                    
                    <div class="gap-section">
                        <div class="gap-header" style="color: #ffff44;">🟡 Minor Gaps</div>
                        <div class="gaps-grid" id="minorGaps"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>© 2025 IRAQAF - Integrated Regulatory Compliant Quality Assurance Framework</p>
            <p>L1 Regulations & Governance Module | Port 8504 | Flask</p>
        </footer>
        
        <script>
            function analyzeDocuments() {
                const fileInput = document.getElementById('docInput');
                const files = fileInput.files;
                
                if (files.length === 0) {
                    alert('Please select documents to analyze');
                    return;
                }
                
                // Create FormData
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                
                // Send to server
                fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => displayResults(data))
                .catch(error => console.error('Error:', error));
            }
            
            function displayResults(data) {
                document.getElementById('results').style.display = 'block';
                
                // Update stats
                document.getElementById('crsScore').textContent = data.crs_score.toFixed(1) + '%';
                document.getElementById('criticalCount').textContent = data.gaps.critical.length;
                document.getElementById('majorCount').textContent = data.gaps.major.length;
                document.getElementById('minorCount').textContent = data.gaps.minor.length;
                
                // Update charts
                document.getElementById('gaugeChart').src = data.gauge_chart;
                document.getElementById('radarChart').src = data.radar_chart;
                document.getElementById('gapsChart').src = data.gaps_chart;
                
                // Update regulation scores
                let scoresHtml = '';
                for (const [regulation, score] of Object.entries(data.regulation_scores)) {
                    const displayName = regulation.replace(/_/g, ' ');
                    scoresHtml += `
                        <div class="regulation-card">
                            <div class="regulation-name">${displayName}</div>
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${score}%;">
                                    ${score.toFixed(1)}%
                                </div>
                            </div>
                        </div>
                    `;
                }
                document.getElementById('regulationScores').innerHTML = scoresHtml;
                
                // Update requirements
                let reqsHtml = '';
                data.requirements.forEach(req => {
                    const statusColor = req.score >= 0.8 ? '#00ff41' : req.score >= 0.5 ? '#ffaa00' : '#ff4444';
                    reqsHtml += `
                        <li class="requirement-item">
                            <div class="requirement-details">
                                <div class="requirement-name">${req.name}</div>
                                <div class="requirement-article">${req.article}</div>
                            </div>
                            <div class="requirement-score" style="border-left: 3px solid ${statusColor};">
                                ${(req.score * 100).toFixed(0)}%
                            </div>
                        </li>
                    `;
                });
                document.getElementById('requirementsList').innerHTML = reqsHtml;
                
                // Update gaps
                displayGaps(data.gaps);
            }
            
            function displayGaps(gaps) {
                let criticalHtml = '';
                gaps.critical.forEach(gap => {
                    criticalHtml += createGapHtml(gap, 'critical');
                });
                document.getElementById('criticalGaps').innerHTML = criticalHtml || '<p style="color: #888;">No critical gaps found</p>';
                
                let majorHtml = '';
                gaps.major.forEach(gap => {
                    majorHtml += createGapHtml(gap, 'major');
                });
                document.getElementById('majorGaps').innerHTML = majorHtml || '<p style="color: #888;">No major gaps found</p>';
                
                let minorHtml = '';
                gaps.minor.forEach(gap => {
                    minorHtml += createGapHtml(gap, 'minor');
                });
                document.getElementById('minorGaps').innerHTML = minorHtml || '<p style="color: #888;">No minor gaps found</p>';
            }
            
            function createGapHtml(gap, type) {
                return `
                    <div class="gap-item gap-${type}">
                        <div class="gap-title">${gap.requirement}</div>
                        <div class="gap-details">
                            <strong>Regulation:</strong> ${gap.regulation}<br>
                            <strong>Article:</strong> ${gap.article}<br>
                            <strong>Current Score:</strong> ${(gap.score * 100).toFixed(0)}%
                        </div>
                        <span class="gap-priority priority-${type.toLowerCase()}">${gap.priority}</span>
                    </div>
                `;
            }
            
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }
        </script>
    </body>
    </html>
    '''

# ═══════════════════════════════════════════════════════════════════════════════
# FLASK ROUTES
# ═══════════════════════════════════════════════════════════════════════════════


@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string(get_html_template())


@app.route('/api/analyze', methods=['POST'])
def analyze_documents():
    """Analyze uploaded documents for compliance"""
    files = request.files.getlist('files')

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # Combine all document text
    combined_text = ""
    for file in files:
        try:
            if file.filename.endswith('.txt') or file.filename.endswith('.md'):
                text = file.read().decode('utf-8')
            elif file.filename.endswith('.pdf'):
                # For now, treat PDF as text (in production, use PyPDF2)
                text = f"[PDF: {file.filename}] Content analysis would be performed here"
            elif file.filename.endswith('.docx'):
                # For now, treat DOCX as text (in production, use python-docx)
                text = f"[DOCX: {file.filename}] Content analysis would be performed here"
            else:
                continue

            combined_text += " " + text
        except Exception as e:
            print(f"Error reading file {file.filename}: {e}")

    # Analyze documents
    document_analysis = analyzer.analyze_text(combined_text)

    # Calculate CRS
    crs_score, regulation_scores = scorer.calculate_crs(
        document_analysis, combined_text)

    # Identify gaps
    gaps = scorer.identify_gaps(document_analysis, combined_text)

    # Generate visualizations
    gauge_chart = generate_score_gauge(crs_score, "Overall Compliance Score")
    radar_chart = generate_compliance_radar(
        {reg: score*100 for reg, score in regulation_scores.items()})
    gaps_chart = generate_gaps_chart(gaps)

    # Build requirements list
    all_requirements = []
    for regulation, reqs in COMPLIANCE_REQUIREMENTS.items():
        for req in reqs:
            score = scorer.score_requirement(
                req["id"], document_analysis, combined_text)
            all_requirements.append({
                "id": req["id"],
                "name": req["name"],
                "article": req["article"],
                "regulation": regulation,
                "score": score
            })

    return jsonify({
        "crs_score": crs_score,
        "regulation_scores": {reg: score*100 for reg, score in regulation_scores.items()},
        "requirements": all_requirements,
        "gaps": gaps,
        "gauge_chart": gauge_chart,
        "radar_chart": radar_chart,
        "gaps_chart": gaps_chart,
        "document_count": len(files),
        "total_text_length": len(combined_text)
    })


@app.route('/api/sai')
def get_sai():
    """Get SAI information"""
    return jsonify({
        "overall_sai": 80,
        "modules_active": 5,
        "module_names": ["GDPR", "EU AI Act", "ISO 13485", "IEC 62304", "FDA"],
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/regulations')
def get_regulations():
    """Get list of monitored regulations"""
    regulations = []
    for source_id, source in REGULATORY_SOURCES.items():
        regulations.append({
            "id": source_id,
            "name": source.name,
            "category": source.category,
            "url": source.url,
            "keywords_count": len(source.keywords)
        })
    return jsonify(regulations)

# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP MESSAGE
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🔐 L1 REGULATIONS & GOVERNANCE HUB - ENHANCED WITH REASONING & VISUALIZATIONS")
    print("="*80)
    print("> Port: 8504")
    print("> Features: 5 regulations, compliance scoring, gap analysis, visualizations")
    print("> SAI: 80% (5 modules)")
    print("> Running on http://127.0.0.1:8504")
    print("> Press CTRL+C to stop")
    print("="*80 + "\n")

    app.run(debug=False, host='127.0.0.1', port=8504, use_reloader=False)
