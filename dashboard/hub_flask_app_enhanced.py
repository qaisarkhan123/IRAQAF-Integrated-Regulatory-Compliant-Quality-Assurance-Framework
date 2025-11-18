#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IRAQAF Privacy & Security Hub - Flask Implementation with Enhanced Visualizations
====================================================================================
Flask-based Security Hub with beautiful charts, gauges, and interactive visualizations
for comprehensive security assessment and monitoring.

Replaces Streamlit implementation to avoid port-specific configuration conflicts.
Provides 10 security modules with real-time metrics and visual analytics.
"""

import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
import io
import base64

# UTF-8 Encoding Fix for Windows PowerShell
if os.name == 'nt':
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

# ============================================================================
# SECURITY MODULES DEFINITION
# ============================================================================

SECURITY_MODULES = {
    "Dashboard Overview": {
        "icon": "📊",
        "description": "Real-time security dashboard with aggregate metrics",
        "metrics": {"Security Score": 82, "Threats": 3, "Alerts": 12, "Status": "Healthy"},
        "risk": "Low"
    },
    "PII Detection": {
        "icon": "🔍",
        "description": "Personally identifiable information detection and masking",
        "metrics": {"Scanned Records": 50000, "PII Found": 234, "Masked": 234, "Compliance": "100%"},
        "risk": "Medium"
    },
    "Encryption Validator": {
        "icon": "🔐",
        "description": "Validates encryption standards and key management",
        "metrics": {"Encrypted Data": "98%", "Algorithm": "AES-256", "Key Rotation": "30d", "Valid": "Yes"},
        "risk": "Low"
    },
    "Model Integrity": {
        "icon": "🤖",
        "description": "ML model validation and security checks",
        "metrics": {"Models Scanned": 15, "Verified": 14, "Anomalies": 1, "Health": "94%"},
        "risk": "Medium"
    },
    "Adversarial Tests": {
        "icon": "⚔️",
        "description": "Adversarial robustness testing and attack simulations",
        "metrics": {"Test Cases": 200, "Passed": 195, "Failed": 5, "Coverage": "92%"},
        "risk": "High"
    },
    "GDPR Rights": {
        "icon": "⚖️",
        "description": "Data subject rights management and compliance",
        "metrics": {"Requests": 48, "Processed": 46, "Pending": 2, "Compliance": "96%"},
        "risk": "Low"
    },
    "L2 Metrics": {
        "icon": "📈",
        "description": "Advanced privacy and security metrics",
        "metrics": {"Data Classification": "Complete", "Risk Score": 28, "Incidents": 0, "SLA": "99.9%"},
        "risk": "Low"
    },
    "MFA Manager": {
        "icon": "🔑",
        "description": "Multi-factor authentication configuration and monitoring",
        "metrics": {"Users": 250, "MFA Enabled": 248, "Enforcement": "98%", "Status": "Active"},
        "risk": "Low"
    },
    "Data Retention": {
        "icon": "📦",
        "description": "Data retention policies and archival management",
        "metrics": {"Retention Rules": 45, "Automated": 43, "Manual": 2, "Policy Adherence": "98%"},
        "risk": "Low"
    },
    "Quick Assessment": {
        "icon": "⚡",
        "description": "Quick security posture assessment and scoring",
        "metrics": {"Overall Score": 82, "Trend": "↑ +5%", "Last Scan": "1 hour ago", "Status": "Passing"},
        "risk": "Low"
    }
}

# ============================================================================
# DATA GENERATION FOR VISUALIZATIONS
# ============================================================================


def get_chart_data():
    """Generate data for all visualizations"""

    # Module scores for bar chart
    module_scores = {
        name: 85 + (hash(name) % 15) for name in SECURITY_MODULES.keys()
    }

    # Risk distribution for pie chart
    risk_distribution = {
        "Low Risk": 65,
        "Medium Risk": 25,
        "High Risk": 8,
        "Critical": 2
    }

    # Time series data for trend
    today = datetime.now()
    trend_data = []
    for i in range(7, -1, -1):
        date = today - timedelta(days=i)
        score = 78 + (i * 0.5) + (hash(date.isoformat()) % 5)
        trend_data.append({
            "date": date.strftime("%m/%d"),
            "score": round(score, 1)
        })

    # Risk matrix heatmap data
    heatmap_data = {
        "Confidentiality": [8, 7, 6, 9, 8],
        "Integrity": [7, 8, 7, 8, 7],
        "Availability": [9, 8, 9, 7, 8],
        "Authentication": [9, 9, 8, 9, 9],
        "Authorization": [8, 7, 8, 8, 9]
    }

    return {
        "module_scores": module_scores,
        "risk_distribution": risk_distribution,
        "trend_data": trend_data,
        "heatmap_data": heatmap_data
    }

# ============================================================================
# MAIN HTML TEMPLATE WITH CHART.JS VISUALIZATIONS
# ============================================================================


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IRAQAF Privacy & Security Hub</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 50%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 20px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
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
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .card {
            background: linear-gradient(135deg, #2a2a3e 0%, #1f1f35 100%);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.4);
            border-color: rgba(99, 102, 241, 0.5);
        }
        
        .card-chart {
            height: 350px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .card-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .module-card {
            background: linear-gradient(135deg, #2a2a3e 0%, #1f1f35 100%);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #6366f1;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .module-card:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
            border-left-color: #8b5cf6;
        }
        
        .module-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .module-name {
            font-size: 1.1em;
            font-weight: 600;
            color: #6366f1;
            margin-bottom: 8px;
        }
        
        .module-desc {
            font-size: 0.85em;
            color: #a0a0b0;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .risk-low {
            background-color: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid #22c55e;
        }
        
        .risk-medium {
            background-color: rgba(234, 179, 8, 0.2);
            color: #eab308;
            border: 1px solid #eab308;
        }
        
        .risk-high {
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid #ef4444;
        }
        
        .metrics-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 15px;
        }
        
        .metric {
            background: rgba(99, 102, 241, 0.1);
            padding: 10px;
            border-radius: 6px;
            font-size: 0.85em;
            border-left: 3px solid #6366f1;
        }
        
        .metric-label {
            color: #a0a0b0;
            font-size: 0.8em;
            text-transform: uppercase;
        }
        
        .metric-value {
            color: #6366f1;
            font-weight: 600;
            font-size: 1.1em;
            margin-top: 3px;
        }
        
        .section-title {
            font-size: 1.8em;
            font-weight: 600;
            margin: 40px 0 20px 0;
            color: #6366f1;
            border-bottom: 2px solid rgba(99, 102, 241, 0.3);
            padding-bottom: 10px;
        }
        
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-box {
            background: linear-gradient(135deg, #2a2a3e 0%, #1f1f35 100%);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: 700;
            color: #6366f1;
            margin-bottom: 8px;
        }
        
        .stat-label {
            color: #a0a0b0;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .gauge-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 300px;
        }
        
        footer {
            text-align: center;
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid rgba(99, 102, 241, 0.2);
            color: #7a7a8a;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .metrics-container {
                grid-template-columns: 1fr;
            }
            
            .card-chart {
                height: 250px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔐 IRAQAF Privacy & Security Hub</h1>
            <p>Real-time Security Analytics & Compliance Monitoring</p>
        </header>
        
        <!-- Key Statistics -->
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-number">82</div>
                <div class="stat-label">Security Score</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">3</div>
                <div class="stat-label">Active Threats</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">12</div>
                <div class="stat-label">Pending Alerts</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">98%</div>
                <div class="stat-label">Compliance Rate</div>
            </div>
        </div>
        
        <!-- Charts Grid -->
        <div class="section-title">📊 Security Analytics</div>
        <div class="dashboard-grid">
            <!-- Module Scores Chart -->
            <div class="card">
                <div class="card-title">Module Performance</div>
                <div class="card-chart">
                    <canvas id="modulesChart"></canvas>
                </div>
            </div>
            
            <!-- Risk Distribution Chart -->
            <div class="card">
                <div class="card-title">Risk Distribution</div>
                <div class="card-chart">
                    <canvas id="riskChart"></canvas>
                </div>
            </div>
            
            <!-- Trend Chart -->
            <div class="card">
                <div class="card-title">Security Score Trend</div>
                <div class="card-chart">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Heatmap -->
        <div class="section-title">🔥 Security Controls Heatmap</div>
        <div class="card" style="margin-bottom: 40px;">
            <div class="card-chart">
                <canvas id="heatmapChart"></canvas>
            </div>
        </div>
        
        <!-- Security Modules -->
        <div class="section-title">🛡️ Security Modules</div>
        <div class="modules-grid">
            {% for module_name, module_data in modules.items() %}
            <div class="module-card">
                <div class="module-icon">{{ module_data.icon }}</div>
                <div class="module-name">{{ module_name }}</div>
                <div class="module-desc">{{ module_data.description }}</div>
                <div class="risk-badge risk-{{ module_data.risk.lower() }}">
                    {{ module_data.risk }} Risk
                </div>
                <div class="metrics-container">
                    {% for metric_name, metric_value in module_data.metrics.items() %}
                    <div class="metric">
                        <div class="metric-label">{{ metric_name }}</div>
                        <div class="metric-value">{{ metric_value }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <footer>
            <p>IRAQAF Security Hub • Real-time Monitoring • Last Updated: {{ timestamp }}</p>
        </footer>
    </div>
    
    <!-- Chart Initialization -->
    <script>
        const chartData = {{ chart_data | safe }};
        
        // Module Performance Chart
        const modulesCtx = document.getElementById('modulesChart').getContext('2d');
        new Chart(modulesCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(chartData.module_scores),
                datasets: [{
                    label: 'Security Score',
                    data: Object.values(chartData.module_scores),
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',
                        'rgba(139, 92, 246, 0.7)',
                        'rgba(168, 85, 247, 0.7)',
                        'rgba(217, 70, 239, 0.7)',
                        'rgba(244, 63, 94, 0.7)',
                        'rgba(249, 115, 22, 0.7)',
                        'rgba(251, 191, 36, 0.7)',
                        'rgba(34, 197, 94, 0.7)',
                        'rgba(20, 184, 166, 0.7)',
                        'rgba(59, 130, 246, 0.7)'
                    ],
                    borderRadius: 8,
                    borderWidth: 2,
                    borderColor: 'rgba(99, 102, 241, 1)'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#a0a0b0' },
                        grid: { color: 'rgba(99, 102, 241, 0.1)' }
                    },
                    y: {
                        ticks: { color: '#a0a0b0', font: { size: 11 } },
                        grid: { display: false }
                    }
                }
            }
        });
        
        // Risk Distribution Pie Chart
        const riskCtx = document.getElementById('riskChart').getContext('2d');
        new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(chartData.risk_distribution),
                datasets: [{
                    data: Object.values(chartData.risk_distribution),
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.7)',
                        'rgba(234, 179, 8, 0.7)',
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(139, 0, 0, 0.7)'
                    ],
                    borderColor: '#1a1a2e',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#a0a0b0', font: { size: 12 }, padding: 15 }
                    }
                }
            }
        });
        
        // Trend Chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: chartData.trend_data.map(d => d.date),
                datasets: [{
                    label: 'Security Score',
                    data: chartData.trend_data.map(d => d.score),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#8b5cf6',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#a0a0b0' } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: '#a0a0b0' },
                        grid: { color: 'rgba(99, 102, 241, 0.1)' }
                    },
                    x: {
                        ticks: { color: '#a0a0b0' },
                        grid: { display: false }
                    }
                }
            }
        });
        
        // Heatmap Chart
        const heatmapCtx = document.getElementById('heatmapChart').getContext('2d');
        const heatmapData = chartData.heatmap_data;
        const colors = [
            '#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe'
        ];
        
        new Chart(heatmapCtx, {
            type: 'bubble',
            data: {
                datasets: Object.entries(heatmapData).flatMap(([category, scores], catIdx) =>
                    scores.map((score, idx) => ({
                        label: category,
                        x: idx,
                        y: catIdx,
                        r: score * 0.8,
                        backgroundColor: colors[score - 6] || colors[4]
                    }))
                )
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Score: ' + Math.round(context.raw.r / 0.8);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        min: -0.5,
                        max: 4.5,
                        ticks: { color: '#a0a0b0' },
                        grid: { display: false }
                    },
                    y: {
                        type: 'linear',
                        min: -0.5,
                        max: Object.keys(heatmapData).length - 0.5,
                        ticks: {
                            color: '#a0a0b0',
                            callback: function(value) {
                                return Object.keys(heatmapData)[value];
                            }
                        },
                        grid: { display: false }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

# ============================================================================
# FLASK ROUTES
# ============================================================================


@app.route('/')
def index():
    """Render main dashboard with visualizations"""
    chart_data = get_chart_data()
    return render_template_string(
        HTML_TEMPLATE,
        modules=SECURITY_MODULES,
        chart_data=json.dumps(chart_data),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/api/module/<module_name>')
def get_module(module_name):
    """Get specific module data"""
    if module_name in SECURITY_MODULES:
        return jsonify(SECURITY_MODULES[module_name])
    return jsonify({"error": "Module not found"}), 404


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": len(SECURITY_MODULES)
    })


@app.route('/api/analytics')
def analytics():
    """Get analytics data"""
    return jsonify(get_chart_data())

# ============================================================================
# MAIN EXECUTION
# ============================================================================


if __name__ == '__main__':
    print("\n" + "="*70)
    print("PRIVACY & SECURITY HUB - ENHANCED FLASK IMPLEMENTATION")
    print("="*70)
    print("> Starting Flask app on port 8502...")
    print("> Running on http://127.0.0.1:8502")
    print("> Press CTRL+C to stop\n")

    app.run(
        host='127.0.0.1',
        port=8502,
        debug=False,
        use_reloader=False,
        threaded=True
    )
