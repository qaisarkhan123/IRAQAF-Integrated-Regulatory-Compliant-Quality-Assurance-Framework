"""
L3 Fairness & Ethics Hub
Comprehensive fairness and ethics evaluation for AI systems.
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from datetime import datetime
from typing import Dict, List, Optional
import json
import random

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ============================================================================
# DATA MODEL & SAMPLE DATA
# ============================================================================

def generate_sample_prediction_records(count: int = 1000) -> List[Dict]:
    """Generate sample prediction records for demonstration."""
    records = []
    genders = ["M", "F", "Other"]
    age_groups = ["18-30", "31-45", "46-60", "61+"]
    
    for i in range(count):
        gender = random.choice(genders)
        age_group = random.choice(age_groups)
        
        # Simulate some bias: older age groups and certain genders have slightly different outcomes
        base_prob = 0.5
        if age_group == "61+":
            base_prob = 0.45
        if gender == "F":
            base_prob += 0.03
        
        y_prob = random.uniform(max(0.0, base_prob - 0.1), min(1.0, base_prob + 0.1))
        y_pred = 1 if y_prob > 0.5 else 0
        y_true = 1 if random.random() < 0.55 else 0  # Slight class imbalance
        
        records.append({
            "id": f"pred_{i:06d}",
            "y_true": y_true,
            "y_pred": y_pred,
            "y_prob": round(y_prob, 3),
            "protected": {
                "gender": gender,
                "age_group": age_group
            },
            "timestamp": datetime.now().isoformat()
        })
    
    return records

# Load sample data (in production, this would load from database/file)
PREDICTION_RECORDS = generate_sample_prediction_records(1000)

# ============================================================================
# FAIRNESS METRICS COMPUTATION
# ============================================================================

def compute_demographic_parity_gap(records: List[Dict], attr_name: str) -> float:
    """
    Compute Demographic Parity Gap for attribute 'attr_name'.
    Returns max difference in P(y_pred=1) between any two groups, 0-1 scale.
    """
    groups = {}
    
    for record in records:
        attr_value = record["protected"].get(attr_name)
        if attr_value is None:
            continue
        
        if attr_value not in groups:
            groups[attr_value] = {"total": 0, "positive": 0}
        
        groups[attr_value]["total"] += 1
        if record["y_pred"] == 1:
            groups[attr_value]["positive"] += 1
    
    if len(groups) < 2:
        return 0.0
    
    proportions = {}
    for group, counts in groups.items():
        if counts["total"] > 0:
            proportions[group] = counts["positive"] / counts["total"]
        else:
            proportions[group] = 0.0
    
    if len(proportions) < 2:
        return 0.0
    
    max_prop = max(proportions.values())
    min_prop = min(proportions.values())
    
    return max_prop - min_prop


def compute_equal_opportunity_gap(records: List[Dict], attr_name: str) -> float:
    """
    Compute Equal Opportunity Gap: max difference in TPR (True Positive Rate) across groups.
    TPR = P(y_pred=1 | y_true=1)
    """
    groups = {}
    
    for record in records:
        attr_value = record["protected"].get(attr_name)
        if attr_value is None or record["y_true"] != 1:
            continue
        
        if attr_value not in groups:
            groups[attr_value] = {"true_positives": 0, "actual_positives": 0}
        
        groups[attr_value]["actual_positives"] += 1
        if record["y_pred"] == 1:
            groups[attr_value]["true_positives"] += 1
    
    if len(groups) < 2:
        return 0.0
    
    tprs = {}
    for group, counts in groups.items():
        if counts["actual_positives"] > 0:
            tprs[group] = counts["true_positives"] / counts["actual_positives"]
        else:
            tprs[group] = 0.0
    
    if len(tprs) < 2:
        return 0.0
    
    max_tpr = max(tprs.values())
    min_tpr = min(tprs.values())
    
    return max_tpr - min_tpr


def compute_equalized_odds_gap(records: List[Dict], attr_name: str) -> float:
    """
    Compute Equalized Odds Gap: aggregate difference in TPR and FPR across groups.
    Returns the maximum of (TPR gap, FPR gap).
    """
    groups = {}
    
    for record in records:
        attr_value = record["protected"].get(attr_name)
        if attr_value is None:
            continue
        
        if attr_value not in groups:
            groups[attr_value] = {
                "true_positives": 0,
                "false_positives": 0,
                "actual_positives": 0,
                "actual_negatives": 0
            }
        
        if record["y_true"] == 1:
            groups[attr_value]["actual_positives"] += 1
            if record["y_pred"] == 1:
                groups[attr_value]["true_positives"] += 1
        else:
            groups[attr_value]["actual_negatives"] += 1
            if record["y_pred"] == 1:
                groups[attr_value]["false_positives"] += 1
    
    if len(groups) < 2:
        return 0.0
    
    tprs = {}
    fprs = {}
    
    for group, counts in groups.items():
        if counts["actual_positives"] > 0:
            tprs[group] = counts["true_positives"] / counts["actual_positives"]
        else:
            tprs[group] = 0.0
        
        if counts["actual_negatives"] > 0:
            fprs[group] = counts["false_positives"] / counts["actual_negatives"]
        else:
            fprs[group] = 0.0
    
    if len(tprs) < 2 or len(fprs) < 2:
        return 0.0
    
    tpr_gap = max(tprs.values()) - min(tprs.values())
    fpr_gap = max(fprs.values()) - min(fprs.values())
    
    return max(tpr_gap, fpr_gap)


def compute_subgroup_accuracy_difference(records: List[Dict], attr_name: str) -> float:
    """
    Compute Subgroup Accuracy Difference: max accuracy difference across groups.
    """
    groups = {}
    
    for record in records:
        attr_value = record["protected"].get(attr_name)
        if attr_value is None:
            continue
        
        if attr_value not in groups:
            groups[attr_value] = {"correct": 0, "total": 0}
        
        groups[attr_value]["total"] += 1
        if record["y_pred"] == record["y_true"]:
            groups[attr_value]["correct"] += 1
    
    if len(groups) < 2:
        return 0.0
    
    accuracies = {}
    for group, counts in groups.items():
        if counts["total"] > 0:
            accuracies[group] = counts["correct"] / counts["total"]
        else:
            accuracies[group] = 0.0
    
    if len(accuracies) < 2:
        return 0.0
    
    max_acc = max(accuracies.values())
    min_acc = min(accuracies.values())
    
    return max_acc - min_acc


def compute_all_attribute_metrics(records: List[Dict]) -> Dict:
    """Compute all fairness metrics for all protected attributes."""
    if not records:
        return {}
    
    # Get all protected attribute names
    protected_attrs = set()
    for record in records:
        protected_attrs.update(record["protected"].keys())
    
    all_metrics = {}
    
    for attr_name in protected_attrs:
        all_metrics[attr_name] = {
            "demographic_parity_gap": compute_demographic_parity_gap(records, attr_name),
            "equal_opportunity_gap": compute_equal_opportunity_gap(records, attr_name),
            "equalized_odds_gap": compute_equalized_odds_gap(records, attr_name),
            "subgroup_accuracy_difference": compute_subgroup_accuracy_difference(records, attr_name)
        }
    
    return all_metrics


# ============================================================================
# FAIRNESS INDEX COMPUTATION
# ============================================================================

def gap_to_score(gap: float, max_gap: float = 0.3) -> float:
    """
    Map a gap (0-1) to a 0-100 fairness score.
    If gap >= max_gap → score = 0
    If gap = 0       → score = 100
    Linear in between.
    """
    g = min(max(gap, 0.0), max_gap)
    score01 = 1.0 - (g / max_gap)
    return round(score01 * 100.0, 2)


def compute_fairness_index(all_attr_metrics: Dict) -> Dict:
    """
    Compute Fairness Index (FI) from attribute-level metrics.
    
    Returns:
      - fairness_index: Overall FI (0-100)
      - attributes: Per-attribute fairness scores
    """
    if not all_attr_metrics:
        return {
            "fairness_index": 0.0,
            "attributes": {}
        }
    
    attr_scores = {}
    
    for attr, metrics in all_attr_metrics.items():
        dpg_score = gap_to_score(metrics["demographic_parity_gap"])
        eog_score = gap_to_score(metrics["equal_opportunity_gap"])
        eod_score = gap_to_score(metrics["equalized_odds_gap"])
        sad_score = gap_to_score(metrics["subgroup_accuracy_difference"])
        
        # Equal weights for each metric
        fairness_attr_score = (dpg_score + eog_score + eod_score + sad_score) / 4.0
        
        attr_scores[attr] = {
            "fairness_score": round(fairness_attr_score, 2),
            "dpg_score": dpg_score,
            "eog_score": eog_score,
            "eod_score": eod_score,
            "sad_score": sad_score,
            "raw_metrics": metrics
        }
    
    # Overall FI is average of all attribute fairness scores
    if attr_scores:
        fi = sum(a["fairness_score"] for a in attr_scores.values()) / len(attr_scores)
    else:
        fi = 0.0
    
    return {
        "fairness_index": round(fi, 2),
        "attributes": attr_scores
    }


# ============================================================================
# ETHICAL MATURITY LEVEL (EML)
# ============================================================================

def load_ethics_checklist() -> Dict:
    """Load ethics checklist (in production, load from config/database)."""
    return {
        "ethical_policy": True,
        "bias_assessment_planned": True,
        "bias_assessment_regular": True,
        "human_oversight_documented": True,
        "incident_reporting": True,
        "fairness_monitoring": True,
        "diverse_testing_data": True,
        "explainability_requirements": True,
        "user_consent_mechanism": True,
        "audit_trail_complete": True,
        "redress_mechanism": True,
        "stakeholder_engagement": True,
        "regular_reviews": True,
        "compliance_tracking": True,
        "training_on_ethics": True
    }


def compute_ethical_maturity_level(checklist: Dict) -> Dict:
    """
    Compute Ethical Maturity Level (EML) from checklist.
    
    Returns:
      - eml_level: 1-5
      - score: 0-100
      - checklist: The checklist with pass/fail status
    """
    total = len(checklist)
    passed = sum(1 for v in checklist.values() if v)
    pct = (passed / total) * 100.0 if total > 0 else 0.0
    
    if pct < 20:
        level = 1
        label = "No formal governance"
    elif pct < 40:
        level = 2
        label = "Basic processes documented"
    elif pct < 60:
        level = 3
        label = "Partially implemented"
    elif pct < 80:
        level = 4
        label = "Fully implemented"
    else:
        level = 5
        label = "Continuous optimization"
    
    return {
        "eml_level": level,
        "eml_label": label,
        "score": round(pct, 2),
        "passed_items": passed,
        "total_items": total,
        "checklist": checklist
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_prediction_records() -> List[Dict]:
    """Load prediction records (in production, load from database/file)."""
    return PREDICTION_RECORDS


def summarize_protected_groups(records: List[Dict]) -> Dict:
    """Summarize protected attributes and their value distributions."""
    if not records:
        return {}
    
    summaries = {}
    
    # Get all protected attribute names
    protected_attrs = set()
    for record in records:
        protected_attrs.update(record["protected"].keys())
    
    for attr_name in protected_attrs:
        value_counts = {}
        for record in records:
            attr_value = record["protected"].get(attr_name, "Unknown")
            value_counts[attr_value] = value_counts.get(attr_value, 0) + 1
        
        total = sum(value_counts.values())
        distributions = {
            value: {
                "count": count,
                "percentage": round((count / total) * 100, 2) if total > 0 else 0.0
            }
            for value, count in value_counts.items()
        }
        
        summaries[attr_name] = {
            "values": distributions,
            "total": total
        }
    
    return summaries


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/", methods=["GET"])
def index():
    """Render fairness/ethics dashboard."""
    return render_template_string(get_dashboard_html())


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "L3 Fairness & Ethics Hub",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/fairness-metrics", methods=["GET"])
def get_fairness_metrics():
    """
    Returns detailed fairness metrics per protected attribute and overall FI.
    """
    try:
        records = load_prediction_records()
        attr_metrics = compute_all_attribute_metrics(records)
        fi_result = compute_fairness_index(attr_metrics)
        
        return jsonify({
            **fi_result,
            "timestamp": datetime.now().isoformat(),
            "total_records": len(records)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/fi", methods=["GET"])
def get_fairness_index():
    """
    Returns only the overall Fairness Index.
    """
    try:
        records = load_prediction_records()
        attr_metrics = compute_all_attribute_metrics(records)
        fi_result = compute_fairness_index(attr_metrics)
        
        return jsonify({
            "fairness_index": fi_result["fairness_index"],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/eml", methods=["GET"])
def get_ethical_maturity():
    """
    Returns Ethical Maturity Level (EML) and associated score.
    """
    try:
        checklist = load_ethics_checklist()
        eml = compute_ethical_maturity_level(checklist)
        
        return jsonify({
            **eml,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/groups", methods=["GET"])
def get_protected_groups():
    """
    Returns the list of protected attributes and their value distributions.
    """
    try:
        records = load_prediction_records()
        groups = summarize_protected_groups(records)
        
        return jsonify({
            "groups": groups,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Get summary for Module 5 integration."""
    try:
        records = load_prediction_records()
        attr_metrics = compute_all_attribute_metrics(records)
        fi_result = compute_fairness_index(attr_metrics)
        checklist = load_ethics_checklist()
        eml = compute_ethical_maturity_level(checklist)
        
        return jsonify({
            "fairness_index": fi_result["fairness_index"],
            "eml_level": eml["eml_level"],
            "eml_score": eml["score"],
            "total_records": len(records),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# DASHBOARD HTML TEMPLATE
# ============================================================================

def get_dashboard_html() -> str:
    """Generate the dashboard HTML template."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L3 Fairness & Ethics Hub</title>
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
            --success: #43e97b;
            --warning: #fa709a;
            --info: #4facfe;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg) 0%, #1a1f2e 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, var(--primary) 0%, #764ba2 100%);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }
        header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .kpi {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border-top: 3px solid var(--primary);
        }
        .kpi-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary);
            margin: 10px 0;
        }
        .kpi-label {
            font-size: 0.9rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 25px;
        }
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--primary);
        }
        .metric-row {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }
        .metric-row:last-child { border-bottom: none; }
        .metric-label { flex: 1; }
        .metric-value {
            font-weight: 600;
            color: var(--primary);
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚖️ L3 Fairness & Ethics Hub</h1>
            <p>Comprehensive fairness and ethics evaluation for AI systems</p>
        </header>
        
        <div class="kpi-grid">
            <div class="kpi">
                <div class="kpi-label">Fairness Index</div>
                <div class="kpi-value" id="fi">-</div>
                <div style="color: var(--muted); font-size: 0.85rem;">0-100 scale</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Ethical Maturity Level</div>
                <div class="kpi-value" id="eml-level">-</div>
                <div style="color: var(--muted); font-size: 0.85rem;" id="eml-label">-</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">EML Score</div>
                <div class="kpi-value" id="eml-score">-</div>
                <div style="color: var(--muted); font-size: 0.85rem;">0-100 scale</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Total Records</div>
                <div class="kpi-value" id="total-records">-</div>
                <div style="color: var(--muted); font-size: 0.85rem;">Analyzed</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">📊 Fairness Metrics by Attribute</div>
                <div id="fairness-details" class="loading">Loading...</div>
            </div>
            <div class="card">
                <div class="card-title">👥 Protected Groups Distribution</div>
                <div class="chart-container">
                    <canvas id="groups-chart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">📋 Ethical Maturity Checklist</div>
            <div id="checklist" class="loading">Loading...</div>
        </div>
    </div>
    
    <script>
        const api = window.location.protocol + '//' + window.location.host;
        
        function loadDashboard() {
            // Load FI
            fetch(api + '/api/fi')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('fi').textContent = data.fairness_index || '0';
                })
                .catch(e => console.error('FI error:', e));
            
            // Load EML
            fetch(api + '/api/eml')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('eml-level').textContent = data.eml_level || '-';
                    document.getElementById('eml-label').textContent = data.eml_label || '-';
                    document.getElementById('eml-score').textContent = data.score || '0';
                    
                    // Render checklist
                    const checklistHtml = Object.entries(data.checklist || {})
                        .map(([key, value]) => `
                            <div class="metric-row">
                                <div class="metric-label">${key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</div>
                                <div class="metric-value">${value ? '✓' : '✗'}</div>
                            </div>
                        `).join('');
                    document.getElementById('checklist').innerHTML = checklistHtml;
                })
                .catch(e => console.error('EML error:', e));
            
            // Load fairness metrics
            fetch(api + '/api/fairness-metrics')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-records').textContent = data.total_records || '0';
                    
                    let html = '';
                    Object.entries(data.attributes || {}).forEach(([attr, scores]) => {
                        html += `
                            <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid var(--border);">
                                <strong style="color: var(--primary); font-size: 1.1rem;">${attr}</strong>
                                <div style="margin-top: 10px;">
                                    <div class="metric-row">
                                        <div class="metric-label">Overall Fairness Score</div>
                                        <div class="metric-value">${scores.fairness_score}%</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Demographic Parity Gap</div>
                                        <div class="metric-value">${scores.raw_metrics.demographic_parity_gap.toFixed(4)}</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Equal Opportunity Gap</div>
                                        <div class="metric-value">${scores.raw_metrics.equal_opportunity_gap.toFixed(4)}</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Equalized Odds Gap</div>
                                        <div class="metric-value">${scores.raw_metrics.equalized_odds_gap.toFixed(4)}</div>
                                    </div>
                                    <div class="metric-row">
                                        <div class="metric-label">Subgroup Accuracy Difference</div>
                                        <div class="metric-value">${scores.raw_metrics.subgroup_accuracy_difference.toFixed(4)}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('fairness-details').innerHTML = html || '<div>No data available</div>';
                })
                .catch(e => console.error('Fairness metrics error:', e));
            
            // Load groups chart
            fetch(api + '/api/groups')
                .then(r => r.json())
                .then(data => {
                    const groups = data.groups || {};
                    const firstAttr = Object.keys(groups)[0];
                    if (firstAttr) {
                        const groupData = groups[firstAttr];
                        const labels = Object.keys(groupData.values);
                        const values = Object.values(groupData.values).map(v => v.count);
                        
                        new Chart(document.getElementById('groups-chart'), {
                            type: 'bar',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: 'Count',
                                    data: values,
                                    backgroundColor: '#667eea'
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: { display: false }
                                },
                                scales: {
                                    y: { ticks: { color: '#9aa3b2' }, grid: { color: '#2a2f3a' } },
                                    x: { ticks: { color: '#9aa3b2' }, grid: { color: '#2a2f3a' } }
                                }
                            }
                        });
                    }
                })
                .catch(e => console.error('Groups error:', e));
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadDashboard);
        } else {
            loadDashboard();
        }
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
    '''

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("⚖️ L3 FAIRNESS & ETHICS HUB")
    print("=" * 80)
    print("> Port: 8506")
    print("> Running on http://127.0.0.1:8506")
    print("> Features:")
    print("  - Fairness Index (FI) computation")
    print("  - Ethical Maturity Level (EML 1-5)")
    print("  - Protected group analysis")
    print("  - Comprehensive fairness metrics")
    print("> Press CTRL+C to stop")
    print()
    
    app.run(host='127.0.0.1', port=8506, debug=False, use_reloader=False, threaded=True)

