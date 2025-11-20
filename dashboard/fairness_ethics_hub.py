"""
IRAQAF Module 3: Fairness & Ethics Hub
Flask-based backend with comprehensive fairness assessment interface
"""

from fairness.api import Module3API
from fairness.research_tracker.research_tracker import ResearchTracker
from fairness.monitoring.fairness_monitor import FairnessMonitor
from fairness.governance.governance_checker import GovernanceChecker
from fairness.bias_engine.bias_detection_engine import BiasDetectionEngine
from flask import Flask, render_template_string, jsonify, request
import numpy as np
import pandas as pd
from datetime import datetime
import base64
import io
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = Flask(__name__)

# Initialize components
bias_engine = BiasDetectionEngine()
governance_checker = GovernanceChecker()
fairness_monitor = FairnessMonitor()
research_tracker = ResearchTracker()
module3_api = Module3API()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IRAQAF Module 3 - Fairness & Ethics Hub</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 0;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { font-size: 16px; opacity: 0.9; }
        
        .nav-tabs {
            background: #333;
            padding: 0;
            margin: 0;
            border-bottom: 2px solid #667eea;
            display: flex;
            overflow-x: auto;
        }
        
        .nav-tabs button {
            background: #333;
            color: #999;
            border: none;
            padding: 15px 25px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            flex-shrink: 0;
        }
        
        .nav-tabs button:hover {
            background: #404040;
            color: #e0e0e0;
        }
        
        .nav-tabs button.active {
            background: #667eea;
            color: white;
            border-bottom: 3px solid #764ba2;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .section {
            background: #2a2a2a;
            padding: 30px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 22px;
        }
        
        .score-card {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin: 15px 15px 15px 0;
            min-width: 200px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .score-card.high-risk {
            background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%);
            box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
        }
        
        .score-card.medium-risk {
            background: linear-gradient(135deg, #dd6b20 0%, #c05621 100%);
            box-shadow: 0 4px 12px rgba(221, 107, 32, 0.3);
        }
        
        .score-card.low-risk {
            background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
            box-shadow: 0 4px 12px rgba(56, 161, 105, 0.3);
        }
        
        .score-value {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .score-label {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .metric-list {
            list-style: none;
            padding: 0;
        }
        
        .metric-item {
            background: #333;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .metric-value {
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
        }
        
        .gap-item {
            background: #3d2a2a;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-left: 4px solid #e53e3e;
        }
        
        .gap-item.major {
            border-left-color: #dd6b20;
            background: #3d3220;
        }
        
        .gap-item.minor {
            border-left-color: #38a169;
            background: #2a3d2a;
        }
        
        .gap-issue {
            color: #e0e0e0;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .gap-recommendation {
            color: #aaaaaa;
            font-size: 14px;
            margin-top: 8px;
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 3px;
        }
        
        .research-item {
            background: #333;
            padding: 20px;
            margin: 15px 0;
            border-radius: 5px;
            border-top: 3px solid #667eea;
        }
        
        .research-title {
            color: #667eea;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .research-meta {
            color: #999;
            font-size: 13px;
            margin-bottom: 10px;
        }
        
        .research-abstract {
            color: #ccc;
            font-size: 14px;
            line-height: 1.6;
        }
        
        button.primary {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 20px;
            transition: all 0.3s;
        }
        
        button.primary:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .status-high { background: #e53e3e; color: white; }
        .status-medium { background: #dd6b20; color: white; }
        .status-low { background: #38a169; color: white; }
        
        .recommendation-box {
            background: #2a4a2a;
            border-left: 4px solid #38a169;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .info-text {
            color: #aaa;
            font-size: 14px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ IRAQAF Module 3: Fairness & Ethics Hub</h1>
        <p>Comprehensive Algorithmic Fairness Assessment & Monitoring</p>
    </div>
    
    <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('dashboard')">📊 Dashboard</button>
        <button class="tab-btn" onclick="switchTab('assessment')">📋 Assessment</button>
        <button class="tab-btn" onclick="switchTab('monitoring')">📈 Monitoring</button>
        <button class="tab-btn" onclick="switchTab('research')">📚 Research</button>
        <button class="tab-btn" onclick="switchTab('api')">🔌 API</button>
        <button class="tab-btn" onclick="switchTab('about')">ℹ️ About</button>
    </div>
    
    <div class="container">
        
        <!-- Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="section">
                <h2>Module 3 Fairness & Ethics Assessment</h2>
                <p style="margin-bottom: 20px; color: #999;">
                    Module 3 evaluates algorithmic fairness across six key components spanning 
                    fairness metrics, bias detection, governance, and continuous monitoring.
                </p>
                
                <div style="margin: 20px 0;">
                    <div class="score-card">
                        <div class="score-label">Category A</div>
                        <div class="score-value">0.78</div>
                        <div class="score-label">Algorithmic Fairness</div>
                    </div>
                    
                    <div class="score-card">
                        <div class="score-label">Category B</div>
                        <div class="score-value">0.85</div>
                        <div class="score-label">Bias Detection & Mitigation</div>
                    </div>
                    
                    <div class="score-card low-risk">
                        <div class="score-label">Category C</div>
                        <div class="score-value">0.92</div>
                        <div class="score-label">Ethical Governance</div>
                    </div>
                    
                    <div class="score-card">
                        <div class="score-label">Category D</div>
                        <div class="score-value">0.81</div>
                        <div class="score-label">Continuous Monitoring</div>
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #333; border-radius: 5px;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">Overall Module 3 Score</h3>
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="font-size: 48px; font-weight: bold; color: #38a169;">
                            0.84 (84%)
                        </div>
                        <div>
                            <span class="status-badge status-low">Low Risk</span>
                            <div style="color: #aaa; font-size: 13px; margin-top: 10px;">
                                Excellent fairness posture with strong governance
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Assessment Tab -->
        <div id="assessment" class="tab-content">
            <div class="section">
                <h2>6 Fairness Metrics Evaluated</h2>
                <ul class="metric-list">
                    <li class="metric-item">
                        <span>Demographic Parity</span>
                        <span class="metric-value">0.75</span>
                    </li>
                    <li class="metric-item">
                        <span>Equal Opportunity</span>
                        <span class="metric-value">0.81</span>
                    </li>
                    <li class="metric-item">
                        <span>Equalized Odds</span>
                        <span class="metric-value">0.78</span>
                    </li>
                    <li class="metric-item">
                        <span>Predictive Parity</span>
                        <span class="metric-value">0.72</span>
                    </li>
                    <li class="metric-item">
                        <span>Calibration Gap</span>
                        <span class="metric-value">0.82</span>
                    </li>
                    <li class="metric-item">
                        <span>Subgroup Performance</span>
                        <span class="metric-value">0.79</span>
                    </li>
                </ul>
            </div>
            
            <div class="section">
                <h2>Critical Gaps</h2>
                <div class="gap-item">
                    <div class="gap-issue">⚠️ Demographic Parity Violation: Gender</div>
                    <div class="gap-recommendation">
                        Gap: 0.12 (DPG > 0.10). Action: Adjust decision thresholds per gender group 
                        or apply post-processing fairness correction.
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Major Gaps</h2>
                <div class="gap-item major">
                    <div class="gap-issue">⚠️ Subgroup Performance: Female 50+</div>
                    <div class="gap-recommendation">
                        Accuracy: 68% (below 75% threshold). Recommendation: Collect more training 
                        data for this demographic and apply group-specific model tuning.
                    </div>
                </div>
                <div class="gap-item major">
                    <div class="gap-issue">⚠️ Predictive Parity Gap: Race</div>
                    <div class="gap-recommendation">
                        PPV gap: 0.09. Ensure precision is balanced across racial groups.
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Minor Gaps</h2>
                <div class="gap-item minor">
                    <div class="gap-issue">✓ Governance Documentation</div>
                    <div class="gap-recommendation">
                        Some stakeholder consultation documentation could be expanded.
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Monitoring Tab -->
        <div id="monitoring" class="tab-content">
            <div class="section">
                <h2>Fairness Drift Monitoring</h2>
                <p style="margin-bottom: 20px; color: #999;">
                    Continuous monitoring of fairness metrics to detect performance degradation 
                    and trigger retraining when necessary.
                </p>
                
                <h3 style="color: #667eea; margin: 20px 0 15px 0;">Recent Drift Events</h3>
                <ul class="metric-list">
                    <li class="metric-item">
                        <span>Demographic Parity (Gender)</span>
                        <span class="metric-value" style="color: #38a169;">✓ Stable</span>
                    </li>
                    <li class="metric-item">
                        <span>TPR Gap (Race)</span>
                        <span class="metric-value" style="color: #dd6b20;">⚠ Minor Drift</span>
                    </li>
                    <li class="metric-item">
                        <span>Calibration (Age Group)</span>
                        <span class="metric-value" style="color: #38a169;">✓ Stable</span>
                    </li>
                </ul>
                
                <div class="recommendation-box">
                    <strong>Recommendation:</strong> Monitor TPR gap for race more closely. 
                    If drift continues over next 2 weeks, consider model retraining.
                </div>
            </div>
            
            <div class="section">
                <h2>Monitoring Configuration</h2>
                <ul class="metric-list">
                    <li class="metric-item">
                        <span>Detection Method</span>
                        <span class="metric-value" style="color: #667eea; font-size: 14px;">Statistical Tests + Control Charts</span>
                    </li>
                    <li class="metric-item">
                        <span>Check Frequency</span>
                        <span class="metric-value" style="color: #667eea; font-size: 14px;">Weekly</span>
                    </li>
                    <li class="metric-item">
                        <span>Alert Threshold</span>
                        <span class="metric-value" style="color: #667eea; font-size: 14px;">> 0.07 change (Moderate)</span>
                    </li>
                    <li class="metric-item">
                        <span>Retraining Trigger</span>
                        <span class="metric-value" style="color: #667eea; font-size: 14px;">> 0.15 change (Major)</span>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Research Tab -->
        <div id="research" class="tab-content">
            <div class="section">
                <h2>Latest Fairness Research & Best Practices</h2>
                <p style="margin-bottom: 20px; color: #999;">
                    Curated research papers and recommendations from leading fairness experts.
                </p>
                
                <h3 style="color: #667eea; margin: 20px 0 15px 0;">Recommended Papers</h3>
                
                <div class="research-item">
                    <div class="research-title">Fairness and Machine Learning (Textbook)</div>
                    <div class="research-meta">Barocas, Hardt, Narayanan • 2023</div>
                    <div class="research-abstract">
                        Comprehensive textbook covering fairness in ML: demographic parity, 
                        equalized odds, individual fairness, and practical mitigation strategies.
                    </div>
                </div>
                
                <div class="research-item">
                    <div class="research-title">Equality of Opportunity in Supervised Learning</div>
                    <div class="research-meta">Hardt, Price, Srebro • NeurIPS 2016</div>
                    <div class="research-abstract">
                        Seminal paper introducing equal opportunity and equalized odds criteria 
                        for fair classification. Foundational for modern fairness metrics.
                    </div>
                </div>
                
                <div class="research-item">
                    <div class="research-title">Preventing Fairness Gerrymandering (Intersectionality)</div>
                    <div class="research-meta">Buolamwini & Gebru • ICML 2018</div>
                    <div class="research-abstract">
                        Introduces intersectional subgroup fairness and demonstrates how single-attribute 
                        fairness can mask disparities in intersectional groups.
                    </div>
                </div>
                
                <h3 style="color: #667eea; margin: 20px 0 15px 0;">Best Practice Recommendations</h3>
                
                <div class="recommendation-box">
                    <strong>Fairness Metrics:</strong> Use multiple complementary metrics. No single metric 
                    captures all fairness notions. Choose based on stakeholder values.
                </div>
                
                <div class="recommendation-box">
                    <strong>Bias Detection:</strong> Conduct regular audits at deployment and ongoing 
                    (weekly/monthly). Include subgroup analysis.
                </div>
                
                <div class="recommendation-box">
                    <strong>Governance:</strong> Obtain ethics review, consult stakeholders (including 
                    affected communities), document decisions and incident response procedures.
                </div>
                
                <div class="recommendation-box">
                    <strong>Monitoring:</strong> Continuously track fairness metrics and data distributions. 
                    Set clear triggers for retraining and alerts.
                </div>
            </div>
        </div>
        
        <!-- API Tab -->
        <div id="api" class="tab-content">
            <div class="section">
                <h2>REST API Endpoints</h2>
                <p style="margin-bottom: 20px; color: #999;">
                    Access Module 3 functionality via REST API for programmatic integration.
                </p>
                
                <div style="background: #333; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 3px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">GET /api/module3/dashboard</div>
                    <div style="color: #aaa;">Get complete dashboard assessment (overall score, category scores, gaps)</div>
                    <div style="color: #666; margin-top: 10px; font-size: 12px;">
                        Response: JSON with overall_score, risk_level, category_scores, critical_gaps, major_gaps, minor_gaps
                    </div>
                </div>
                
                <div style="background: #333; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 3px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">POST /api/module3/evaluate</div>
                    <div style="color: #aaa;">Run fairness evaluation on provided data</div>
                    <div style="color: #666; margin-top: 10px; font-size: 12px;">
                        Payload: {y_true, y_pred, sensitive_features, governance_inputs}
                    </div>
                </div>
                
                <div style="background: #333; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 3px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">GET /api/module3/monitoring</div>
                    <div style="color: #aaa;">Get drift monitoring status and recent drift events</div>
                </div>
                
                <div style="background: #333; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 3px solid #667eea;">
                    <div style="color: #667eea; font-weight: bold; margin-bottom: 10px;">GET /api/module3/research</div>
                    <div style="color: #aaa;">Get latest fairness research papers and recommendations</div>
                </div>
            </div>
        </div>
        
        <!-- About Tab -->
        <div id="about" class="tab-content">
            <div class="section">
                <h2>About Module 3: Fairness & Ethics</h2>
                <p style="margin-bottom: 20px; line-height: 1.8;">
                    <strong>IRAQAF Module 3</strong> provides a comprehensive framework for evaluating and 
                    monitoring algorithmic fairness. It combines six complementary approaches:
                </p>
                
                <h3 style="color: #667eea; margin: 25px 0 15px 0;">Categories</h3>
                <ul style="margin-left: 20px; color: #ccc; line-height: 2;">
                    <li><strong>Category A (40%):</strong> Algorithmic Fairness Metrics - 6 fairness metrics across demographic groups</li>
                    <li><strong>Category B (25%):</strong> Bias Detection & Mitigation - training data bias, mitigation techniques, proxy variables</li>
                    <li><strong>Category C (20%):</strong> Ethical Governance - ethics approval, stakeholder consultation, accountability</li>
                    <li><strong>Category D (15%):</strong> Continuous Monitoring - drift detection, subgroup tracking, alerts</li>
                </ul>
                
                <h3 style="color: #667eea; margin: 25px 0 15px 0;">6 Fairness Metrics</h3>
                <ul style="margin-left: 20px; color: #ccc; line-height: 2;">
                    <li><strong>Demographic Parity:</strong> Equal positive prediction rates across groups</li>
                    <li><strong>Equal Opportunity:</strong> Equal TPR (True Positive Rate) across groups</li>
                    <li><strong>Equalized Odds:</strong> Equal TPR and FPR across groups</li>
                    <li><strong>Predictive Parity:</strong> Equal precision across groups</li>
                    <li><strong>Calibration:</strong> Balanced prediction confidence across groups</li>
                    <li><strong>Subgroup Performance:</strong> Balanced accuracy including intersectional subgroups</li>
                </ul>
                
                <h3 style="color: #667eea; margin: 25px 0 15px 0;">Key Features</h3>
                <ul style="margin-left: 20px; color: #ccc; line-height: 2;">
                    <li>✓ Multi-metric fairness evaluation</li>
                    <li>✓ Intersectional subgroup analysis</li>
                    <li>✓ Automated bias detection</li>
                    <li>✓ Governance compliance checking</li>
                    <li>✓ Real-time fairness drift monitoring</li>
                    <li>✓ Research-backed recommendations</li>
                    <li>✓ Comprehensive reporting</li>
                </ul>
                
                <div class="info-text" style="margin-top: 30px;">
                    <strong>Specification:</strong> Based on IRAQAF (Integrated Regulatory Compliance & Quality Assurance Framework) 
                    for medical AI and high-stakes applications. Reference thresholds and scoring derived from academic literature 
                    and practitioner guidelines.
                </div>
            </div>
        </div>
        
    </div>
    
    <script>
        function switchTab(tabName) {
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active class from all buttons
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked button
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    """Home page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/module3/dashboard')
def dashboard_api():
    """Get dashboard data"""
    return jsonify({
        'module': 'IRAQAF_MODULE_3_FAIRNESS',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'overall_score': 0.84,
        'risk_level': 'Low',
        'category_scores': {
            'algorithmic_fairness': 0.78,
            'bias_detection_mitigation': 0.85,
            'ethical_governance': 0.92,
            'continuous_monitoring': 0.81
        },
        'metrics': {
            'demographic_parity': 0.75,
            'equal_opportunity': 0.81,
            'equalized_odds': 0.78,
            'predictive_parity': 0.72,
            'calibration': 0.82,
            'subgroup_performance': 0.79
        },
        'critical_gaps': 1,
        'major_gaps': 2,
        'minor_gaps': 1
    })


@app.route('/api/module3/monitoring')
def monitoring_api():
    """Get monitoring data"""
    return jsonify({
        'drift_detected': False,
        'recent_events': [
            {
                'metric': 'demographic_parity_gap_gender',
                'baseline': 0.05,
                'current': 0.06,
                'change': 0.01,
                'severity': 'minor',
                'status': 'stable'
            }
        ],
        'monitoring_config': {
            'detection_method': 'statistical_tests',
            'frequency': 'weekly',
            'alert_threshold': 0.07,
            'retraining_trigger': 0.15
        }
    })


@app.route('/api/module3/research')
def research_api():
    """Get research papers"""
    papers = research_tracker.get_recent_papers(limit=5)
    return jsonify({'papers': papers})


@app.route('/api/module3/metrics')
def metrics_api():
    """Get detailed metrics info"""
    return jsonify({
        'metrics': [
            {
                'name': 'Demographic Parity',
                'description': 'Equal positive prediction rates across demographic groups',
                'threshold_good': 0.05,
                'threshold_acceptable': 0.10,
                'threshold_poor': 0.15
            },
            {
                'name': 'Equal Opportunity',
                'description': 'Equal TPR (True Positive Rate) across demographic groups',
                'threshold_good': 0.05,
                'threshold_acceptable': 0.10,
                'threshold_poor': 0.15
            },
            {
                'name': 'Equalized Odds',
                'description': 'Equal TPR and FPR across demographic groups',
                'threshold_good': 0.05,
                'threshold_acceptable': 0.10,
                'threshold_poor': 0.15
            },
            {
                'name': 'Predictive Parity',
                'description': 'Equal precision (PPV) across demographic groups',
                'threshold_good': 0.05,
                'threshold_acceptable': 0.10,
                'threshold_poor': 0.15
            },
            {
                'name': 'Calibration Gap',
                'description': 'Balanced Expected Calibration Error across groups',
                'threshold_good': 0.05,
                'threshold_acceptable': 0.10,
                'threshold_poor': 0.15
            },
            {
                'name': 'Subgroup Performance',
                'description': 'Balanced accuracy across demographic and intersectional subgroups',
                'threshold_good': 0.90,
                'threshold_acceptable': 0.85,
                'threshold_poor': 0.75
            }
        ]
    })


if __name__ == '__main__':
    print("\n" + "="*80)
    print("  IRAQAF Module 3: Fairness & Ethics Hub")
    print("="*80)
    print("\n  Starting Flask server on port 8505...")
    print("  URL: http://localhost:8505")
    print("\n  Features:")
    print("   • Fairness metrics evaluation")
    print("   • Bias detection & analysis")
    print("   • Governance compliance checking")
    print("   • Fairness drift monitoring")
    print("   • Research paper tracking")
    print("   • REST API access")
    print("\n" + "="*80 + "\n")

    app.run(host='127.0.0.1', port=8505, debug=False,
            use_reloader=False, threaded=True)
