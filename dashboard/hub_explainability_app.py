# -*- coding: utf-8 -*-
"""
L4 EXPLAINABILITY & TRANSPARENCY HUB
Comprehensive Assessment Tool for AI System Transparency
"""

import sys
import io
import json
import logging
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("L4 EXPLAINABILITY & TRANSPARENCY HUB - FLASK IMPLEMENTATION")
print("=" * 80)
print("> Starting Flask app on port 8503...")
print("> Running on http://127.0.0.1:8503")
print("> Press CTRL+C to stop")
print()

# Explainability Modules Definition
EXPLAINABILITY_MODULES = {
    "Explanation Methods": {
        "id": "explanation_methods",
        "description": "Verify explanation generation capability (SHAP, LIME, etc.)",
        "category": "Explanation Generation Capability (35%)",
        "weight": 0.35,
        "score": 0.92,
        "items": [
            {"name": "SHAP Implementation", "status": "", "score": 1.0},
            {"name": "Explanation Automation", "status": "", "score": 0.95},
            {"name": "Model Type Compatibility", "status": "", "score": 0.85},
            {"name": "TreeExplainer for XGBoost", "status": "", "score": 1.0},
        ],
        "color": "#667eea"
    },
    "Explanation Quality": {
        "id": "explanation_quality",
        "description": "Human-readable format, clinically meaningful explanations",
        "category": "Explanation Generation Capability (35%)",
        "weight": 0.35,
        "score": 0.88,
        "items": [
            {"name": "Human-Readable Format", "status": "", "score": 0.9},
            {"name": "Feature Importance Display", "status": "", "score": 0.85},
            {"name": "Clinical Terminology", "status": "", "score": 0.75},
            {"name": "Visual Explanations", "status": "", "score": 0.95},
        ],
        "color": "#764ba2"
    },
    "Coverage & Completeness": {
        "id": "coverage",
        "description": "Explanations available for all prediction types",
        "category": "Explanation Generation Capability (35%)",
        "weight": 0.30,
        "score": 0.85,
        "items": [
            {"name": "All Prediction Types", "status": "", "score": 0.9},
            {"name": "Edge Case Coverage", "status": "", "score": 0.85},
            {"name": "Confidence Explanation", "status": "", "score": 0.8},
            {"name": "Error Case Handling", "status": "", "score": 0.75},
        ],
        "color": "#f093fb"
    },
    "Fidelity Testing": {
        "id": "fidelity",
        "description": "Do explanations accurately reflect model behavior?",
        "category": "Explanation Reliability (30%)",
        "weight": 0.40,
        "score": 0.72,
        "items": [
            {"name": "Feature Masking Test", "status": "", "score": 0.7},
            {"name": "Importance Ranking", "status": "", "score": 0.75},
            {"name": "Prediction Change Analysis", "status": "", "score": 0.7},
            {"name": "Fidelity Threshold (>0.5)", "status": "", "score": 0.72},
        ],
        "color": "#4facfe"
    },
    "Feature Consistency": {
        "id": "consistency",
        "description": "Jaccard similarity for similar case explanations",
        "category": "Explanation Reliability (30%)",
        "weight": 0.35,
        "score": 0.68,
        "items": [
            {"name": "Similar Case Pairing", "status": "", "score": 0.7},
            {"name": "Feature Overlap", "status": "", "score": 0.65},
            {"name": "Jaccard Similarity (>0.7)", "status": "", "score": 0.68},
            {"name": "Ranking Correlation", "status": "", "score": 0.7},
        ],
        "color": "#43e97b"
    },
    "Stability Testing": {
        "id": "stability",
        "description": "Robustness to input noise and perturbations",
        "category": "Explanation Reliability (30%)",
        "weight": 0.25,
        "score": 0.85,
        "items": [
            {"name": "Noise Robustness (1%)", "status": "", "score": 0.85},
            {"name": "Spearman Correlation (>0.8)",
             "status": "", "score": 0.85},
            {"name": "Ranking Stability", "status": "", "score": 0.85},
            {"name": "Feature Persistence", "status": "", "score": 0.85},
        ],
        "color": "#fa709a"
    },
    "Prediction Logging": {
        "id": "logging",
        "description": "Comprehensive, immutable prediction logs",
        "category": "Traceability & Auditability (25%)",
        "weight": 0.35,
        "score": 1.0,
        "items": [
            {"name": "All Fields Logged", "status": "", "score": 1.0},
            {"name": "Timestamp Tracking", "status": "", "score": 1.0},
            {"name": "Immutable Records", "status": "", "score": 1.0},
            {"name": "Metadata Completeness", "status": "", "score": 1.0},
        ],
        "color": "#30cfd0"
    },
    "Model Versioning": {
        "id": "versioning",
        "description": "Model version tracking and provenance",
        "category": "Traceability & Auditability (25%)",
        "weight": 0.30,
        "score": 0.95,
        "items": [
            {"name": "Version Tracking", "status": "", "score": 1.0},
            {"name": "Training History", "status": "", "score": 0.95},
            {"name": "Hyperparameter Docs", "status": "", "score": 0.9},
            {"name": "Parent Model Tracking", "status": "", "score": 0.95},
        ],
        "color": "#330867"
    },
    "Audit Trail": {
        "id": "audit_trail",
        "description": "100% decision traceability and reconstructibility",
        "category": "Traceability & Auditability (25%)",
        "weight": 0.35,
        "score": 0.98,
        "items": [
            {"name": "Complete Traceability", "status": "", "score": 0.98},
            {"name": "Action Logging", "status": "", "score": 0.98},
            {"name": "Query-able Records", "status": "", "score": 0.98},
            {"name": "Searchability", "status": "", "score": 0.98},
        ],
        "color": "#a8edea"
    },
    "Documentation": {
        "id": "documentation",
        "description": "Architecture, training, performance, limitations",
        "category": "Documentation Transparency (10%)",
        "weight": 0.40,
        "score": 0.75,
        "items": [
            {"name": "Architecture Docs", "status": "", "score": 0.8},
            {"name": "Training Process", "status": "", "score": 0.75},
            {"name": "Performance Metrics", "status": "", "score": 0.75},
            {"name": "Limitations Statement", "status": "", "score": 0.7},
        ],
        "color": "#fed6e3"
    },
    "Intended Use": {
        "id": "intended_use",
        "description": "Target population, use cases, contraindications",
        "category": "Documentation Transparency (10%)",
        "weight": 0.30,
        "score": 0.80,
        "items": [
            {"name": "Target Population", "status": "", "score": 0.85},
            {"name": "Use Case Definition", "status": "", "score": 0.8},
            {"name": "Contraindications", "status": "", "score": 0.8},
            {"name": "Deployment Context", "status": "", "score": 0.75},
        ],
        "color": "#ffeaa7"
    },
    "Change Management": {
        "id": "change_management",
        "description": "Update policy, change log, performance tracking",
        "category": "Documentation Transparency (10%)",
        "weight": 0.30,
        "score": 0.60,
        "items": [
            {"name": "Update Policy Docs", "status": "", "score": 0.7},
            {"name": "Change Log Access", "status": "", "score": 0.6},
            {"name": "Performance Tracking", "status": "", "score": 0.5},
            {"name": "User Communication", "status": "", "score": 0.6},
        ],
        "color": "#dfe6e9"
    }
}

# Category Scores
CATEGORY_SCORES = {
    "Explanation Generation": {
        "weight": 0.35,
        "modules": ["Explanation Methods", "Explanation Quality", "Coverage & Completeness"],
        "score": 0.88,
        "description": "Ability to generate human-readable, comprehensive explanations"
    },
    "Explanation Reliability": {
        "weight": 0.30,
        "modules": ["Fidelity Testing", "Feature Consistency", "Stability Testing"],
        "score": 0.75,
        "description": "Fidelity, consistency, and stability of explanations"
    },
    "Traceability": {
        "weight": 0.25,
        "modules": ["Prediction Logging", "Model Versioning", "Audit Trail"],
        "score": 0.98,
        "description": "Complete auditability and decision traceability"
    },
    "Documentation": {
        "weight": 0.10,
        "modules": ["Documentation", "Intended Use", "Change Management"],
        "score": 0.72,
        "description": "Transparency and clarity of system documentation"
    }
}

# Calculate transparency score


def calculate_transparency_score():
    total = sum(cat["score"] * cat["weight"]
                for cat in CATEGORY_SCORES.values())
    weight_sum = sum(cat["weight"] for cat in CATEGORY_SCORES.values())
    return round(total / weight_sum, 2)


OVERALL_SCORE = calculate_transparency_score()

# Test Results
TEST_RESULTS = {
    "fidelity_test": {
        "name": "Explanation Fidelity Test",
        "description": "Masking top-3 features and measuring prediction change",
        "mean_fidelity": 0.72,
        "std_fidelity": 0.08,
        "passing": True,
        "samples_tested": 100,
        "threshold": ">0.5",
        "interpretation": "72% of prediction explained by top features "
    },
    "consistency_test": {
        "name": "Feature Consistency Test",
        "description": "Jaccard similarity for similar case pairs",
        "mean_jaccard": 0.68,
        "pairs_tested": 50,
        "threshold": ">0.7",
        "passing": False,
        "recommendation": "Improve feature selection consistency"
    },
    "stability_test": {
        "name": "Stability Test",
        "description": "Spearman correlation under 1% noise",
        "mean_correlation": 0.85,
        "std_correlation": 0.05,
        "threshold": ">0.8",
        "passing": True,
        "interpretation": "Highly stable explanations "
    },
    "audit_trail_test": {
        "name": "Audit Trail Test",
        "description": "Traceability of sampled predictions",
        "traceability_rate": 0.98,
        "fully_traceable": 98,
        "incomplete_records": 2,
        "predictions_tested": 100,
        "threshold": "0.95",
        "passing": True
    }
}

# Flask Routes


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/modules')
def get_modules():
    return jsonify(EXPLAINABILITY_MODULES)


@app.route('/api/categories')
def get_categories():
    return jsonify(CATEGORY_SCORES)


@app.route('/api/transparency-score')
def get_score():
    return jsonify({
        "transparency_score": OVERALL_SCORE,
        "category_breakdown": {k: v["score"] for k, v in CATEGORY_SCORES.items()},
        "categories": CATEGORY_SCORES
    })


@app.route('/api/tests')
def get_tests():
    return jsonify(TEST_RESULTS)


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "L4 Explainability Hub"})


# HTML Template (embedded)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L4 Explainability Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --primary: #667eea;
            --bg: #0f1116;
            --surface: #151922;
            --border: #2a2f3a;
            --text: #e6e6e6;
            --muted: #9aa3b2;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg) 0%, #1a1f2e 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, var(--primary) 0%, #764ba2 100%);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .score-card {
            background: linear-gradient(135deg, var(--primary) 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }
        .score-value { font-size: 3rem; font-weight: 700; margin: 10px 0; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        .card:hover {
            border-color: var(--primary);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }
        .card-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 15px; }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .kpi { background: var(--surface); border: 1px solid var(--border); padding: 20px; border-radius: 12px; text-align: center; }
        .kpi-value { font-size: 2rem; font-weight: 700; color: var(--primary); margin: 10px 0; }
        .kpi-label { font-size: 0.9rem; color: var(--muted); text-transform: uppercase; }
        .chart-container { position: relative; height: 400px; margin-bottom: 30px; }
        footer { text-align: center; padding: 20px; color: var(--muted); margin-top: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1> L4 Explainability & Transparency Hub</h1>
            <p>Comprehensive AI System Transparency Assessment</p>
        </header>
        <div class="score-card">
            <div>Overall Transparency Score</div>
            <div class="score-value" id="score">Loading...</div>
        </div>
        <div class="kpi-grid">
            <div class="kpi"><div class="kpi-label">Explanation Capability</div><div class="kpi-value" id="kpi1">88%</div></div>
            <div class="kpi"><div class="kpi-label">Explanation Reliability</div><div class="kpi-value" id="kpi2">75%</div></div>
            <div class="kpi"><div class="kpi-label">Traceability</div><div class="kpi-value" id="kpi3">98%</div></div>
            <div class="kpi"><div class="kpi-label">Documentation</div><div class="kpi-value" id="kpi4">72%</div></div>
        </div>
        <div class="chart-container"><canvas id="chart1"></canvas></div>
        <div class="grid" id="modules"></div>
        <footer> L4 Explainability Hub | IRAQAF Module 4</footer>
    </div>
    <script>
        async function load() {
            const score = await fetch('/api/transparency-score').then(r => r.json());
            const modules = await fetch('/api/modules').then(r => r.json());
            
            document.getElementById('score').textContent = (score.transparency_score * 100).toFixed(0) + '%';
            document.getElementById('kpi1').textContent = (score.categories['Explanation Generation'].score * 100).toFixed(0) + '%';
            document.getElementById('kpi2').textContent = (score.categories['Explanation Reliability'].score * 100).toFixed(0) + '%';
            document.getElementById('kpi3').textContent = (score.categories['Traceability'].score * 100).toFixed(0) + '%';
            document.getElementById('kpi4').textContent = (score.categories['Documentation'].score * 100).toFixed(0) + '%';
            
            const grid = document.getElementById('modules');
            grid.innerHTML = Object.entries(modules).map(([name, mod]) => 
                <div class="card">
                    <div class="card-title">+name+ - +(mod.score*100).toFixed(0)+%</div>
                    <p style="color: var(--muted); font-size: 0.9rem;">+mod.description+</p>
                </div>
            ).join('');
        }
        load();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    try:
        app.run(host='127.0.0.1', port=8503, debug=False,
                use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n L4 Hub stopped cleanly")
    except Exception as e:
        print(f" Error: {e}")
