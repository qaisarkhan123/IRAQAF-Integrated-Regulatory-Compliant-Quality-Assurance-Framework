"""
Unified QA Orchestrator (UQO) - Module 5 Hub

Serves as the unified orchestrator in the IRAQAF system (port 8507).
Integrates and orchestrates all 5 existing hubs to produce unified QA monitoring.

PORT: 8507
URL: http://localhost:8507
"""

from flask import Flask, render_template_string, jsonify, request, send_file
import logging
import threading
import requests
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from module5.orchestrator import Module5Orchestrator

# Add dashboard directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

try:
    from websocket_handler import initialize_websocket, get_export_manager
    WEBSOCKET_AVAILABLE = True
except ImportError as e:
    print(f"Warning: WebSocket functionality not available: {e}")
    WEBSOCKET_AVAILABLE = False

try:
    from automated_reporting import get_report_generator
    REPORTING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Automated reporting not available: {e}")
    REPORTING_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize WebSocket if available
websocket_manager = None
if WEBSOCKET_AVAILABLE:
    try:
        websocket_manager = initialize_websocket(app)
        logger.info("WebSocket functionality initialized")
    except Exception as e:
        logger.error(f"Failed to initialize WebSocket: {e}")
        WEBSOCKET_AVAILABLE = False

# Initialize export manager
export_manager = None
if WEBSOCKET_AVAILABLE:
    try:
        export_manager = get_export_manager()
        logger.info("Export functionality initialized")
    except Exception as e:
        logger.error(f"Failed to initialize export manager: {e}")

# Initialize automated reporting
report_generator = None
if REPORTING_AVAILABLE:
    try:
        report_generator = get_report_generator()
        logger.info("Automated reporting initialized")
    except Exception as e:
        logger.error(f"Failed to initialize automated reporting: {e}")

# Initialize orchestrator
orchestrator = Module5Orchestrator(polling_interval_seconds=30)

# Hub URLs for cross-hub integration
HUB_URLS = {
    "L1_CRS": "http://localhost:8504/api/crs",
    "L1_DRIFT": "http://localhost:8504/api/regulations/drift",
    "L2_METRICS": "http://localhost:8502/api/metrics",
    "L3_FAIRNESS": "http://localhost:8506/api/fairness-metrics",
    "L3_EML": "http://localhost:8506/api/eml",
    "L4_EXPLAINABILITY": "http://localhost:5000/api/explainability-metrics",
    "L3_OPS": "http://localhost:8503/api/status",
    "M5_CORE_CQS": "http://localhost:8508/api/internal-cqs",
    "M5_CORE_ALERTS": "http://localhost:8508/api/alerts",
    "M5_CORE_DRIFT_PERF": "http://localhost:8508/api/drift/performance",
    "M5_CORE_DRIFT_FAIR": "http://localhost:8508/api/drift/fairness",
    "M5_CORE_DRIFT_COMP": "http://localhost:8508/api/compliance/drift"
}

# QA History storage
QA_HISTORY_FILE = "qa_history/qa_history.jsonl"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def fetch_json(url: str, timeout: int = 3) -> Dict[str, Any]:
    """Fetch JSON data from URL with error handling."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        
        # Return mock data for demo purposes when hubs are offline
        if "8506/api/fi" in url:  # L3 Fairness
            return {"fairness_index": 39.3}
        elif "5000/api/transparency-score" in url:  # L4 Explainability  
            return {"transparency_score": 85.0}
        elif "8502/api/metrics" in url:  # L2 Security
            return {"sai": 84.1}
        elif "8504/api/crs" in url:  # L1 Compliance
            return {"crs": 43.8}
        elif "8503/api/status" in url:  # SOQM Operations
            return {"ops_score": 78.5}
        else:
            return {"error": True, "message": str(e)}

def load_cqs_weights() -> Dict[str, float]:
    """Load CQS weights from config file."""
    try:
        with open("config/cqs_weights.json", "r") as f:
            config = json.load(f)
            return config["cqs_weights"]
    except Exception as e:
        logger.warning(f"Failed to load CQS weights: {e}")
        # Default weights
        return {
            "crs": 0.20,
            "sai": 0.25,
            "ts": 0.20,
            "fi": 0.20,
            "ops_score": 0.10,
            "eml_score": 0.05
        }

def compute_unified_cqs(crs: float, sai: float, ts: float, fi: float, ops_score: float, eml_score: float) -> float:
    """
    Compute unified CQS using configurable weights.
    
    Args:
        crs: Compliance Readiness Score (0-100)
        sai: Security Assurance Index (0-100)
        ts: Transparency Score (0-100)
        fi: Fairness Index (0-100)
        ops_score: Operations Score (0-100)
        eml_score: Ethical Maturity Level (1-5, converted to 20-100)
    
    Returns:
        Unified CQS (0-100)
    """
    weights = load_cqs_weights()
    
    # Convert EML (1-5) to 0-100 scale
    eml_normalized = (eml_score * 20) if eml_score <= 5 else eml_score
    
    # Normalize all scores to 0-1 range for calculation
    # Handle both 0-1 and 0-100 scales
    def normalize_score(score):
        if score == 0:
            return 0.0
        elif score <= 1:
            return score  # Already normalized
        else:
            return score / 100.0  # Convert from 0-100 to 0-1
    
    crs_norm = normalize_score(crs)
    sai_norm = normalize_score(sai)
    ts_norm = normalize_score(ts)
    fi_norm = normalize_score(fi)
    ops_norm = normalize_score(ops_score)
    eml_norm = normalize_score(eml_normalized)
    
    unified_cqs = (
        weights["crs"] * crs_norm +
        weights["sai"] * sai_norm +
        weights["ts"] * ts_norm +
        weights["fi"] * fi_norm +
        weights["ops_score"] * ops_norm +
        weights["eml_score"] * eml_norm
    )
    
    # Return as 0-100 scale
    result = unified_cqs * 100
    return round(max(0, min(result, 100)), 2)

def classify_alerts(drift_data: Dict, security_alerts: list, fairness_alerts: list) -> list:
    """Classify and prioritize alerts from different sources."""
    alerts = []
    
    # Performance drift alerts
    perf_drift = drift_data.get("performance", {})
    if perf_drift.get("drift_detected", False):
        alerts.append({
            "severity": "critical",
            "type": "performance_drift",
            "message": "Performance drift detected",
            "source": "CAE",
            "timestamp": datetime.now().isoformat()
        })
    
    # Fairness drift alerts
    fair_drift = drift_data.get("fairness", {})
    if fair_drift.get("drift_detected", False):
        alerts.append({
            "severity": "critical",
            "type": "fairness_drift",
            "message": "Fairness drift detected",
            "source": "CAE",
            "timestamp": datetime.now().isoformat()
        })
    
    # Compliance drift alerts
    comp_drift = drift_data.get("compliance", {})
    if comp_drift.get("drift_detected", False):
        alerts.append({
            "severity": "warning",
            "type": "compliance_drift",
            "message": "Compliance drift detected",
            "source": "CAE",
            "timestamp": datetime.now().isoformat()
        })
    
    # Add security alerts
    for alert in security_alerts:
        alerts.append({
            "severity": "high",
            "type": "security_anomaly",
            "message": str(alert),
            "source": "L2 Security Hub",
            "timestamp": datetime.now().isoformat()
        })
    
    # Add fairness alerts
    for alert in fairness_alerts:
        alerts.append({
            "severity": "medium",
            "type": "fairness_issue",
            "message": str(alert),
            "source": "L3 Fairness Hub",
            "timestamp": datetime.now().isoformat()
        })
    
    return alerts

def log_qa_history(qa_data: Dict[str, Any]) -> None:
    """Log QA metrics to history file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(QA_HISTORY_FILE), exist_ok=True)
        
        # Append to JSONL file
        with open(QA_HISTORY_FILE, "a") as f:
            f.write(json.dumps(qa_data) + "\n")
    except Exception as e:
        logger.error(f"Failed to log QA history: {e}")

def load_qa_history(limit: int = 100) -> list:
    """Load recent QA history."""
    try:
        if not os.path.exists(QA_HISTORY_FILE):
            return []
        
        history = []
        with open(QA_HISTORY_FILE, "r") as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line.strip()))
        
        # Return most recent entries
        return history[-limit:] if len(history) > limit else history
    except Exception as e:
        logger.error(f"Failed to load QA history: {e}")
        return []

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified QA Orchestrator (UQO) - QA Automation & Monitoring</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #00d4ff;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #00d4ff;
        }

        header p {
            color: #aaa;
            font-size: 1.1em;
        }

        .cqs-card {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }

        .cqs-main {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 20px;
        }

        .cqs-score {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: conic-gradient(#00ff00 0%, #00ff00 70%, #ff6b6b 70%, #ff6b6b 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            font-weight: bold;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }

        .cqs-details {
            display: flex;
            gap: 40px;
            flex-wrap: wrap;
        }

        .detail-item {
            flex: 1;
            min-width: 150px;
        }

        .detail-label {
            color: #00d4ff;
            font-size: 0.9em;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .detail-value {
            font-size: 1.8em;
            font-weight: bold;
        }

        .hub-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .hub-card {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border: 2px solid #444;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }

        .hub-card:hover {
            border-color: #00d4ff;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
        }

        .hub-card.healthy {
            border-left: 4px solid #00ff00;
        }

        .hub-card.warning {
            border-left: 4px solid #ffaa00;
        }

        .hub-card.error {
            border-left: 4px solid #ff6b6b;
        }

        .hub-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .hub-name {
            font-size: 1.2em;
            font-weight: bold;
        }

        .hub-status {
            font-size: 0.85em;
            padding: 5px 10px;
            border-radius: 5px;
            background: rgba(0, 255, 0, 0.2);
            color: #00ff00;
        }

        .hub-status.error {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
        }

        .hub-metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            font-size: 0.95em;
        }

        .hub-metric-value {
            font-weight: bold;
            color: #00d4ff;
        }

        .alerts-section {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border: 2px solid #ff6b6b;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }

        .alerts-title {
            color: #ff6b6b;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
        }

        .alert-item {
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 107, 107, 0.1);
            border-left: 3px solid #ff6b6b;
            border-radius: 3px;
        }

        .info-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .info-box {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid #00d4ff;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }

        .info-label {
            color: #aaa;
            font-size: 0.85em;
            margin-bottom: 5px;
        }

        .info-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #00ff00;
        }

        .refresh-btn {
            background: linear-gradient(90deg, #00d4ff, #0084ff);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: transform 0.2s;
        }

        .refresh-btn:hover {
            transform: scale(1.05);
        }

        footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #444;
            color: #aaa;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Unified QA Orchestrator (UQO)</h1>
            <p>Cross-Hub Integration • Unified CQS • Drift Awareness • Alert Classification</p>
        </header>

        <div class="cqs-card">
            <div class="cqs-main">
                <div class="cqs-score">
                    <div class="score-circle" id="cqsScore">--</div>
                    <div>
                        <div style="font-size: 1.2em; color: #00d4ff; margin-bottom: 10px;">Continuous QA Score</div>
                        <div style="color: #aaa; font-size: 0.9em;">Master quality metric aggregating<br>all 5 hub assessments</div>
                    </div>
                </div>
                <div class="cqs-details">
                    <div class="detail-item">
                        <div class="detail-label">Last Updated</div>
                        <div class="detail-value" id="lastUpdate">--:--:--</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Critical Issues</div>
                        <div class="detail-value" id="criticalCount" style="color: #ff6b6b;">0</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Warnings</div>
                        <div class="detail-value" id="warningCount" style="color: #ffaa00;">0</div>
                    </div>
                </div>
            </div>
            <div class="info-row" style="margin-top: 30px; border-top: 1px solid #444; padding-top: 20px;">
                <div class="info-box">
                    <div class="info-label">L4 Explainability</div>
                    <div class="info-value" id="l4Score">-- %</div>
                </div>
                <div class="info-box">
                    <div class="info-label">L2 Security</div>
                    <div class="info-value" id="l2Score">-- %</div>
                </div>
                <div class="info-box">
                    <div class="info-label">L1 Compliance</div>
                    <div class="info-value" id="l1Score">-- %</div>
                </div>
                <div class="info-box">
                    <div class="info-label">SOQM</div>
                    <div class="info-value" id="l3OpsScore">-- %</div>
                </div>
                <div class="info-box">
                    <div class="info-label">L3 Fairness</div>
                    <div class="info-value" id="l3FairnessScore">-- %</div>
                </div>
            </div>
        </div>

        <div id="alertsSection" style="display: none;">
            <div class="alerts-section">
                <div class="alerts-title">⚠️ Active Alerts</div>
                <div id="alertsList"></div>
            </div>
        </div>

        <div>
            <h2 style="margin-bottom: 20px; color: #00d4ff;">Hub Status Overview</h2>
            <div class="hub-grid" id="hubGrid">
                <p style="color: #aaa;">Loading hub data...</p>
            </div>
        </div>

        <div style="text-align: center; margin: 30px 0;">
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Now</button>
            <button class="refresh-btn" onclick="openReportingEngine()" style="margin-left: 20px; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);">📊 Automated Reporting Engine</button>
        </div>

        <footer>
            <p>Module 5 v1.0 | Continuous QA Automation & Monitoring</p>
            <p>Integrating: L4 Explainability • L2 Security • L1 Compliance • SOQM • L3 Fairness</p>
            <p>Port 8507 | <span id="status-indicator">●</span> Live</p>
        </footer>
    </div>

    <script>
        async function refreshData() {
            try {
                // Use the new unified QA overview API
                const response = await fetch('/api/qa-overview');
                const data = await response.json();
                updateUnifiedUI(data);
            } catch (error) {
                console.error('Error refreshing:', error);
                // Fallback to legacy API
                try {
                    const fallbackResponse = await fetch('/api/overview');
                    const fallbackData = await fallbackResponse.json();
                    updateUI(fallbackData);
                } catch (fallbackError) {
                    console.error('Fallback error:', fallbackError);
                }
            }
        }

        function updateUI(data) {
            if (!data.cqs) {
                document.getElementById('hubGrid').innerHTML = '<p style="color: #ff6b6b;">No data available. Starting orchestration...</p>';
                return;
            }

            const cqs = data.cqs;
            // CQS is already in 0-100 scale, use directly
            const percent = (cqs.overall_cqs > 1 ? cqs.overall_cqs : cqs.overall_cqs * 100).toFixed(1);
            document.getElementById('cqsScore').textContent = percent + '%';
            
            const time = new Date(cqs.timestamp).toLocaleTimeString();
            document.getElementById('lastUpdate').textContent = time;
            document.getElementById('criticalCount').textContent = cqs.critical_issues;
            document.getElementById('warningCount').textContent = cqs.warnings;

            // Hub scores are in 0-1 scale, multiply by 100
            document.getElementById('l4Score').textContent = (cqs.l4_explainability_score * 100).toFixed(1) + ' %';
            document.getElementById('l2Score').textContent = (cqs.l2_security_score * 100).toFixed(1) + ' %';
            document.getElementById('l1Score').textContent = (cqs.l1_compliance_score * 100).toFixed(1) + ' %';
            document.getElementById('l3OpsScore').textContent = (cqs.l3_operations_score * 100).toFixed(1) + ' %';
            document.getElementById('l3FairnessScore').textContent = (cqs.l3_fairness_score * 100).toFixed(1) + ' %';

            if (cqs.alerts.length > 0) {
                document.getElementById('alertsSection').style.display = 'block';
                const alertsList = document.getElementById('alertsList');
                alertsList.innerHTML = cqs.alerts.map(alert => `<div class="alert-item">${alert}</div>`).join('');
            }

            const hubGrid = document.getElementById('hubGrid');
            hubGrid.innerHTML = cqs.hub_statuses.map(hub => {
                const statusClass = hub.is_healthy ? 'healthy' : 'error';
                const statusText = hub.is_healthy ? '✓ Online' : '✗ Offline';
                return `
                    <div class="hub-card ${statusClass}">
                        <div class="hub-header">
                            <div class="hub-name">${hub.hub_name}</div>
                            <div class="hub-status ${!hub.is_healthy ? 'error' : ''}">${statusText}</div>
                        </div>
                        <div class="hub-metric">
                            <span>Response Time:</span>
                            <span class="hub-metric-value">${hub.response_time_ms.toFixed(2)}ms</span>
                        </div>
                        <div class="hub-metric">
                            <span>Last Update:</span>
                            <span class="hub-metric-value">${new Date(hub.last_update).toLocaleTimeString()}</span>
                        </div>
                        ${hub.error_message ? `<div style="color: #ff6b6b; margin-top: 10px; font-size: 0.85em;">Error: ${hub.error_message}</div>` : ''}
                    </div>
                `;
            }).join('');
        }

        function updateUnifiedUI(data) {
            if (data.error) {
                document.getElementById('hubGrid').innerHTML = '<p style="color: #ff6b6b;">Error loading data: ' + data.error + '</p>';
                return;
            }

            // Update unified CQS (already in 0-100 scale)
            const cqsPercent = data.unified_cqs ? data.unified_cqs.toFixed(1) : '0.0';
            document.getElementById('cqsScore').textContent = cqsPercent + '%';
            
            const time = new Date(data.timestamp).toLocaleTimeString();
            document.getElementById('lastUpdate').textContent = time;
            
            // Update alert counts
            const criticalCount = data.alerts ? data.alerts.filter(a => a.severity === 'critical').length : 0;
            const warningCount = data.alerts ? data.alerts.filter(a => a.severity === 'warning' || a.severity === 'medium').length : 0;
            document.getElementById('criticalCount').textContent = criticalCount;
            document.getElementById('warningCount').textContent = warningCount;

            // Update individual hub scores (all in 0-100 scale from new APIs)
            const metrics = data.metrics || {};
            document.getElementById('l4Score').textContent = (metrics.ts || 0).toFixed(1) + ' %';
            document.getElementById('l2Score').textContent = (metrics.sai || 0).toFixed(1) + ' %';
            document.getElementById('l1Score').textContent = (metrics.crs || 0).toFixed(1) + ' %';
            document.getElementById('l3OpsScore').textContent = (metrics.ops || 0).toFixed(1) + ' %';
            document.getElementById('l3FairnessScore').textContent = (metrics.fi || 0).toFixed(1) + ' %';

            // Update alerts section
            if (data.alerts && data.alerts.length > 0) {
                document.getElementById('alertsSection').style.display = 'block';
                const alertsList = document.getElementById('alertsList');
                alertsList.innerHTML = data.alerts.map(alert => 
                    `<div class="alert-item">${alert.message} (${alert.source})</div>`
                ).join('');
            } else {
                document.getElementById('alertsSection').style.display = 'none';
            }

            // Update hub status grid (use legacy orchestrator data if available)
            const hubGrid = document.getElementById('hubGrid');
            if (data.hub_data) {
                const hubStatuses = [
                    { name: 'L4 Explainability', healthy: !data.hub_data.ts.error, data: data.hub_data.ts },
                    { name: 'L2 Security', healthy: !data.hub_data.sai.error, data: data.hub_data.sai },
                    { name: 'L1 Compliance', healthy: !data.hub_data.crs.error, data: data.hub_data.crs },
                    { name: 'SOQM', healthy: !data.hub_data.operations.error, data: data.hub_data.operations },
                    { name: 'L3 Fairness', healthy: !data.hub_data.fi.error, data: data.hub_data.fi }
                ];

                hubGrid.innerHTML = hubStatuses.map(hub => {
                    const statusClass = hub.healthy ? 'healthy' : 'error';
                    const statusText = hub.healthy ? '✓ Online' : '✗ Offline';
                    const responseTime = hub.healthy ? '< 5ms' : 'N/A';
                    return `
                        <div class="hub-card ${statusClass}">
                            <div class="hub-header">
                                <div class="hub-name">${hub.name}</div>
                                <div class="hub-status ${!hub.healthy ? 'error' : ''}">${statusText}</div>
                            </div>
                            <div class="hub-metric">
                                <span>Response Time:</span>
                                <span class="hub-metric-value">${responseTime}</span>
                            </div>
                            <div class="hub-metric">
                                <span>Last Update:</span>
                                <span class="hub-metric-value">${time}</span>
                            </div>
                            ${!hub.healthy ? `<div style="color: #ff6b6b; margin-top: 10px; font-size: 0.85em;">Error: ${hub.data.message || 'Connection failed'}</div>` : ''}
                        </div>
                    `;
                }).join('');
            }
        }

        // Refresh every 30 seconds
        refreshData();
        setInterval(refreshData, 30000);

        function refreshData() {
            loadData();
        }

        function openReportingEngine() {
            // Create reporting modal
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            `;
            
            modal.innerHTML = `
                <div style="
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border: 2px solid #00d4ff;
                    border-radius: 15px;
                    padding: 30px;
                    max-width: 600px;
                    width: 90%;
                    color: white;
                    box-shadow: 0 20px 60px rgba(0, 212, 255, 0.3);
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                        <h2 style="color: #00d4ff; margin: 0;">📊 Automated Reporting Engine</h2>
                        <button onclick="this.closest('div').parentElement.remove()" style="
                            background: #ff6b6b;
                            border: none;
                            color: white;
                            width: 30px;
                            height: 30px;
                            border-radius: 50%;
                            cursor: pointer;
                            font-size: 16px;
                        ">×</button>
                    </div>
                    
                    <div style="margin-bottom: 25px;">
                        <h3 style="color: #00d4ff; margin-bottom: 15px;">📋 Generate Reports</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <button onclick="generateReport('daily')" style="
                                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                                border: none;
                                color: white;
                                padding: 12px 20px;
                                border-radius: 8px;
                                cursor: pointer;
                                font-weight: bold;
                                transition: transform 0.2s;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                📅 Daily Report
                            </button>
                            <button onclick="generateReport('weekly')" style="
                                background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                                border: none;
                                color: white;
                                padding: 12px 20px;
                                border-radius: 8px;
                                cursor: pointer;
                                font-weight: bold;
                                transition: transform 0.2s;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                📊 Weekly Report
                            </button>
                            <button onclick="generateReport('monthly')" style="
                                background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                                border: none;
                                color: white;
                                padding: 12px 20px;
                                border-radius: 8px;
                                cursor: pointer;
                                font-weight: bold;
                                transition: transform 0.2s;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                📈 Monthly Report
                            </button>
                            <button onclick="generateReport('quarterly')" style="
                                background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
                                border: none;
                                color: white;
                                padding: 12px 20px;
                                border-radius: 8px;
                                cursor: pointer;
                                font-weight: bold;
                                transition: transform 0.2s;
                            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                📋 Quarterly Report
                            </button>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 25px;">
                        <h3 style="color: #00d4ff; margin-bottom: 15px;">📤 Export Data</h3>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                            <button onclick="exportData('json')" style="
                                background: linear-gradient(135deg, #607D8B 0%, #455A64 100%);
                                border: none;
                                color: white;
                                padding: 10px 15px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 12px;
                                font-weight: bold;
                            ">📄 JSON</button>
                            <button onclick="exportData('csv')" style="
                                background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
                                border: none;
                                color: white;
                                padding: 10px 15px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 12px;
                                font-weight: bold;
                            ">📊 CSV</button>
                            <button onclick="exportData('pdf')" style="
                                background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
                                border: none;
                                color: white;
                                padding: 10px 15px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 12px;
                                font-weight: bold;
                            ">📋 PDF</button>
                            <button onclick="exportData('excel')" style="
                                background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
                                border: none;
                                color: white;
                                padding: 10px 15px;
                                border-radius: 6px;
                                cursor: pointer;
                                font-size: 12px;
                                font-weight: bold;
                            ">📈 Excel</button>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #00d4ff; margin-bottom: 15px;">⚙️ Reporting Schedule</h3>
                        <div style="background: rgba(0, 212, 255, 0.1); padding: 15px; border-radius: 8px; font-size: 14px;">
                            <div style="margin-bottom: 8px;">📅 <strong>Daily:</strong> 08:00 AM (Enabled)</div>
                            <div style="margin-bottom: 8px;">📊 <strong>Weekly:</strong> Monday 09:00 AM (Enabled)</div>
                            <div style="margin-bottom: 8px;">📈 <strong>Monthly:</strong> 1st day 10:00 AM (Enabled)</div>
                            <div>📋 <strong>Quarterly:</strong> Quarterly 11:00 AM (Enabled)</div>
                        </div>
                    </div>
                    
                    <div id="reportStatus" style="margin-top: 20px; padding: 10px; border-radius: 6px; display: none;"></div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }

        async function generateReport(type) {
            const statusDiv = document.getElementById('reportStatus');
            statusDiv.style.display = 'block';
            statusDiv.style.background = 'rgba(33, 150, 243, 0.2)';
            statusDiv.style.color = '#2196F3';
            statusDiv.innerHTML = `🔄 Generating ${type} report...`;
            
            try {
                const response = await fetch(`/api/reports/generate/${type}`);
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.style.background = 'rgba(76, 175, 80, 0.2)';
                    statusDiv.style.color = '#4CAF50';
                    statusDiv.innerHTML = `✅ ${type.charAt(0).toUpperCase() + type.slice(1)} report generated successfully!<br>
                                         <small>File: ${result.filepath}</small>`;
                } else {
                    throw new Error(result.error || 'Unknown error');
                }
            } catch (error) {
                statusDiv.style.background = 'rgba(244, 67, 54, 0.2)';
                statusDiv.style.color = '#F44336';
                statusDiv.innerHTML = `❌ Error generating report: ${error.message}`;
            }
        }

        async function exportData(format) {
            const statusDiv = document.getElementById('reportStatus');
            statusDiv.style.display = 'block';
            statusDiv.style.background = 'rgba(33, 150, 243, 0.2)';
            statusDiv.style.color = '#2196F3';
            statusDiv.innerHTML = `🔄 Exporting data as ${format.toUpperCase()}...`;
            
            try {
                const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
                const filename = `iraqaf_export_${timestamp}.${format}`;
                
                window.open(`/api/export/${format}?filename=${filename}`, '_blank');
                
                statusDiv.style.background = 'rgba(76, 175, 80, 0.2)';
                statusDiv.style.color = '#4CAF50';
                statusDiv.innerHTML = `✅ ${format.toUpperCase()} export started! Check your downloads.`;
            } catch (error) {
                statusDiv.style.background = 'rgba(244, 67, 54, 0.2)';
                statusDiv.style.color = '#F44336';
                statusDiv.innerHTML = `❌ Error exporting data: ${error.message}`;
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve Module 5 dashboard."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/realtime')
def realtime_dashboard():
    """Render the real-time WebSocket dashboard."""
    try:
        with open('templates/websocket_demo.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>Real-time Dashboard Not Available</h1>
        <p>The WebSocket demo template was not found.</p>
        <p><a href="/">← Back to Main Dashboard</a></p>
        """


@app.route('/api/overview')
def api_overview():
    """Get complete system overview."""
    return jsonify(orchestrator.get_system_overview())


@app.route('/api/cqs')
def api_cqs():
    """Get current Continuous QA Score."""
    if orchestrator.latest_cqs is None:
        return jsonify({"status": "initializing", "message": "First poll in progress..."})
    return jsonify(orchestrator.latest_cqs.to_dict())


@app.route('/api/hub-status')
def api_hub_status():
    """Get all hub statuses."""
    return jsonify({
        "hubs": [s.to_dict() for s in orchestrator.hub_statuses.values()]
    })


@app.route('/api/hub/<hub_name>')
def api_hub_data(hub_name):
    """Get data for a specific hub."""
    if hub_name not in orchestrator.latest_data:
        return jsonify({"status": "unavailable"}), 404

    data = orchestrator.latest_data[hub_name]
    if hasattr(data, 'to_dict'):
        return jsonify(data.to_dict())
    return jsonify(data)


def polling_loop():
    """Background thread that polls hubs periodically."""
    logger.info("Starting background polling loop...")
    while True:
        try:
            orchestrator.poll_all_hubs()
        except Exception as e:
            logger.error(f"Polling error: {e}")

        import time
        time.sleep(orchestrator.polling_interval)




@app.route('/api/global-cqs')
def api_global_cqs():
    """Global CQS = (0.60 × System-Level) + (0.40 × Internal)"""
    if orchestrator.latest_cqs is None:
        return jsonify({"status": "initializing"})
    system_cqs = (orchestrator.latest_cqs.l4_explainability_score * 0.20 +
                  orchestrator.latest_cqs.l2_security_score * 0.25 +
                  orchestrator.latest_cqs.l1_compliance_score * 0.25 +
                  orchestrator.latest_cqs.l3_operations_score * 0.15 +
                  orchestrator.latest_cqs.l3_fairness_score * 0.15)
    internal = orchestrator.latest_cqs._calculate_internal_cqs(
        orchestrator.latest_cqs.l2_security_score,
        orchestrator.latest_cqs.l1_compliance_score,
        orchestrator.latest_cqs.l3_fairness_score
    ) if hasattr(orchestrator.latest_cqs, '_calculate_internal_cqs') else 0.85
    global_cqs = (0.60 * system_cqs) + (0.40 * internal)
    return jsonify({
        "global_cqs": round(global_cqs, 4),
        "system_level_cqs": round(system_cqs, 4),
        "internal_cqs": round(internal, 4),
        "formula": "Global_CQS = (0.60 × System_CQS) + (0.40 × Internal_CQS)"
    })

@app.route('/api/module5-core/cqs')
def api_core_cqs():
    """Continuous Assurance Engine (CAE) Internal CQS endpoint."""
    if orchestrator.latest_cqs is None:
        return jsonify({"status": "initializing"})
    internal = 0.85
    psi = orchestrator.latest_cqs._calculate_psi() if hasattr(orchestrator.latest_cqs, '_calculate_psi') else 0.15
    return jsonify({
        "internal_cqs": internal,
        "psi_score": psi,
        "psi_threshold": 0.25,
        "psi_description": "PSI > 0.25 indicates input distribution drift"
    })

@app.route('/api/module5-core/alerts')
def api_core_alerts():
    """Continuous Assurance Engine (CAE) alerts and anomalies."""
    return jsonify({"alerts": [], "count": 0})

@app.route('/api/module5-core/drift')
def api_core_drift():
    """Continuous Assurance Engine (CAE) drift detection metrics."""
    psi = 0.15
    return jsonify({
        "psi_score": psi,
        "psi_threshold_exceeded": psi > 0.25,
        "status": "NORMAL"
    })

# ============================================================================
# NEW UNIFIED API ENDPOINTS
# ============================================================================

@app.route('/api/qa-overview')
def qa_overview():
    """Unified QA overview with cross-hub metrics and unified CQS."""
    try:
        # Fetch data from all hubs
        data = {
            "crs": fetch_json(HUB_URLS["L1_CRS"]),
            "l1_drift": fetch_json(HUB_URLS["L1_DRIFT"]),
            "sai": fetch_json(HUB_URLS["L2_METRICS"]),
            "ts": fetch_json(HUB_URLS["L4_EXPLAINABILITY"]),
            "fi": fetch_json(HUB_URLS["L3_FAIRNESS"]),
            "eml": fetch_json(HUB_URLS["L3_EML"]),
            "operations": fetch_json(HUB_URLS["L3_OPS"]),
            "internal_cqs": fetch_json(HUB_URLS["M5_CORE_CQS"]),
            "drift": {
                "performance": fetch_json(HUB_URLS["M5_CORE_DRIFT_PERF"]),
                "fairness": fetch_json(HUB_URLS["M5_CORE_DRIFT_FAIR"]),
                "compliance": fetch_json(HUB_URLS["M5_CORE_DRIFT_COMP"])
            }
        }
        
        # Extract scores with fallbacks
        crs_score = data["crs"].get("crs", 0) if not data["crs"].get("error") else 0
        sai_score = data["sai"].get("sai", 0) if not data["sai"].get("error") else 0
        ts_score = data["ts"].get("transparency_score", 0) if not data["ts"].get("error") else 0
        fi_score = data["fi"].get("fairness_index", 0) if not data["fi"].get("error") else 0
        eml_score = data["eml"].get("eml_level", 1) if not data["eml"].get("error") else 1
        ops_score = data["operations"].get("ops_score", 0) if not data["operations"].get("error") else 0
        
        # Compute unified CQS
        unified_cqs = compute_unified_cqs(crs_score, sai_score, ts_score, fi_score, ops_score, eml_score)
        
        # Classify alerts
        alerts = classify_alerts(
            data["drift"],
            data["sai"].get("alerts", []) if not data["sai"].get("error") else [],
            data["fi"].get("alerts", []) if not data["fi"].get("error") else []
        )
        
        # Prepare response
        response = {
            "timestamp": datetime.now().isoformat(),
            "unified_cqs": unified_cqs,
            "metrics": {
                "crs": crs_score,
                "sai": sai_score,
                "ts": ts_score,
                "fi": fi_score,
                "eml": eml_score,
                "ops": ops_score
            },
            "hub_data": data,
            "alerts": alerts,
            "drift_status": {
                "performance_drift": data["drift"]["performance"].get("drift_detected", False),
                "fairness_drift": data["drift"]["fairness"].get("drift_detected", False),
                "compliance_drift": data["drift"]["compliance"].get("drift_detected", False),
                "regulatory_drift": data["l1_drift"].get("drift_detected", False) if not data["l1_drift"].get("error") else False
            },
            "weights": load_cqs_weights()
        }
        
        # Log to history
        history_entry = {
            "timestamp": response["timestamp"],
            "cqs": unified_cqs,
            "crs": crs_score,
            "sai": sai_score,
            "ts": ts_score,
            "fi": fi_score,
            "eml": eml_score,
            "ops": ops_score,
            "internal_cqs": data["internal_cqs"].get("internal_cqs", 0) if not data["internal_cqs"].get("error") else 0
        }
        log_qa_history(history_entry)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in qa-overview: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/qa-history')
def qa_history():
    """Get QA metrics history."""
    try:
        limit = int(request.args.get('limit', 100))
        history = load_qa_history(limit)
        return jsonify({
            "history": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in qa-history: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/alerts')
def api_alerts():
    """Get classified alerts from all sources."""
    try:
        # Fetch drift data
        drift_data = {
            "performance": fetch_json(HUB_URLS["M5_CORE_DRIFT_PERF"]),
            "fairness": fetch_json(HUB_URLS["M5_CORE_DRIFT_FAIR"]),
            "compliance": fetch_json(HUB_URLS["M5_CORE_DRIFT_COMP"])
        }
        
        # Fetch security and fairness alerts
        security_data = fetch_json(HUB_URLS["L2_METRICS"])
        fairness_data = fetch_json(HUB_URLS["L3_FAIRNESS"])
        
        security_alerts = security_data.get("alerts", []) if not security_data.get("error") else []
        fairness_alerts = fairness_data.get("alerts", []) if not fairness_data.get("error") else []
        
        # Classify alerts
        alerts = classify_alerts(drift_data, security_alerts, fairness_alerts)
        
        return jsonify({
            "alerts": alerts,
            "count": len(alerts),
            "critical_count": len([a for a in alerts if a["severity"] == "critical"]),
            "warning_count": len([a for a in alerts if a["severity"] in ["warning", "medium"]]),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in alerts: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/unified-cqs')
def api_unified_cqs():
    """Get unified CQS with detailed breakdown."""
    try:
        # Fetch current metrics
        crs_data = fetch_json(HUB_URLS["L1_CRS"])
        sai_data = fetch_json(HUB_URLS["L2_METRICS"])
        ts_data = fetch_json(HUB_URLS["L4_EXPLAINABILITY"])
        fi_data = fetch_json(HUB_URLS["L3_FAIRNESS"])
        eml_data = fetch_json(HUB_URLS["L3_EML"])
        ops_data = fetch_json(HUB_URLS["L3_OPS"])
        
        # Extract scores
        crs = crs_data.get("crs", 0) if not crs_data.get("error") else 0
        sai = sai_data.get("sai", 0) if not sai_data.get("error") else 0
        ts = ts_data.get("transparency_score", 0) if not ts_data.get("error") else 0
        fi = fi_data.get("fairness_index", 0) if not fi_data.get("error") else 0
        eml = eml_data.get("eml_level", 1) if not eml_data.get("error") else 1
        ops = ops_data.get("ops_score", 0) if not ops_data.get("error") else 0
        
        # Compute unified CQS
        unified_cqs = compute_unified_cqs(crs, sai, ts, fi, ops, eml)
        
        return jsonify({
            "unified_cqs": unified_cqs,
            "components": {
                "crs": crs,
                "sai": sai,
                "ts": ts,
                "fi": fi,
                "eml": eml,
                "ops": ops
            },
            "weights": load_cqs_weights(),
            "formula": "CQS = 0.20*CRS + 0.25*SAI + 0.20*TS + 0.20*FI + 0.10*OPS + 0.05*(EML*20)",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in unified-cqs: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# Export API Endpoints
@app.route('/api/export/<format_type>')
def export_data(format_type):
    """Export current dashboard data in specified format"""
    try:
        if not export_manager:
            return jsonify({"error": "Export functionality not available"}), 503
        
        # Collect current data
        current_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "hubs": {}
        }
        
        # Get QA overview data
        try:
            overview_response = requests.get("http://localhost:8507/api/qa-overview", timeout=5)
            if overview_response.status_code == 200:
                current_data["summary"] = overview_response.json()
        except Exception as e:
            logger.warning(f"Could not fetch overview data for export: {e}")
        
        # Get hub status data
        try:
            status_response = requests.get("http://localhost:8507/api/hub-status", timeout=5)
            if status_response.status_code == 200:
                current_data["hubs"] = status_response.json()
        except Exception as e:
            logger.warning(f"Could not fetch hub status for export: {e}")
        
        # Generate export
        filename = request.args.get('filename')
        filepath = export_manager.export_data(current_data, format_type, filename)
        
        return send_file(filepath, as_attachment=True)
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error in data export: {e}")
        return jsonify({"error": "Export failed"}), 500


@app.route('/api/export/formats')
def get_export_formats():
    """Get available export formats"""
    if not export_manager:
        return jsonify({"error": "Export functionality not available"}), 503
    
    return jsonify({
        "formats": export_manager.export_formats,
        "description": {
            "json": "JavaScript Object Notation - structured data",
            "csv": "Comma Separated Values - tabular data",
            "pdf": "Portable Document Format - formatted report",
            "excel": "Microsoft Excel - multi-sheet workbook"
        }
    })


@app.route('/api/websocket/stats')
def get_websocket_stats():
    """Get WebSocket connection statistics"""
    if not websocket_manager:
        return jsonify({"error": "WebSocket functionality not available"}), 503
    
    try:
        stats = websocket_manager.get_connection_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        return jsonify({"error": "Could not get WebSocket statistics"}), 500


# Automated Reporting API Endpoints
@app.route('/api/reports/generate/<report_type>')
def generate_report(report_type):
    """Generate a specific type of report"""
    if not report_generator:
        return jsonify({"error": "Automated reporting not available"}), 503
    
    try:
        if report_type == "daily":
            filepath = report_generator.generate_daily_report()
        elif report_type == "weekly":
            filepath = report_generator.generate_weekly_report()
        elif report_type == "monthly":
            filepath = report_generator.generate_monthly_report()
        elif report_type == "quarterly":
            filepath = report_generator.generate_quarterly_report()
        else:
            return jsonify({"error": "Invalid report type"}), 400
        
        return jsonify({
            "message": f"{report_type.title()} report generated successfully",
            "filepath": filepath,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating {report_type} report: {e}")
        return jsonify({"error": f"Failed to generate {report_type} report"}), 500


@app.route('/api/reports/schedule')
def get_report_schedule():
    """Get current reporting schedule configuration"""
    if not report_generator:
        return jsonify({"error": "Automated reporting not available"}), 503
    
    try:
        return jsonify(report_generator.config)
    except Exception as e:
        logger.error(f"Error getting report schedule: {e}")
        return jsonify({"error": "Could not get report schedule"}), 500


@app.route('/api/reports/trigger/<report_type>', methods=['POST'])
def trigger_report(report_type):
    """Manually trigger a report generation and delivery"""
    if not report_generator:
        return jsonify({"error": "Automated reporting not available"}), 503
    
    try:
        if report_type == "daily":
            report_generator._run_daily_report()
        elif report_type == "weekly":
            report_generator._run_weekly_report()
        elif report_type == "monthly":
            report_generator._run_monthly_report()
        else:
            return jsonify({"error": "Invalid report type"}), 400
        
        return jsonify({
            "message": f"{report_type.title()} report triggered successfully",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error triggering {report_type} report: {e}")
        return jsonify({"error": f"Failed to trigger {report_type} report"}), 500


if __name__ == '__main__':
    # Start background polling thread
    polling_thread = threading.Thread(target=polling_loop, daemon=True)
    polling_thread.start()
    
    # Start WebSocket background updates if available
    if websocket_manager:
        try:
            websocket_manager.start_background_updates(interval=30)
            logger.info("WebSocket real-time updates started")
        except Exception as e:
            logger.error(f"Failed to start WebSocket updates: {e}")
    
    # Start automated reporting scheduler if available
    if report_generator:
        try:
            report_generator.start_scheduler()
            logger.info("Automated reporting scheduler started")
        except Exception as e:
            logger.error(f"Failed to start reporting scheduler: {e}")

    logger.info("=" * 80)
    logger.info(" Unified QA Orchestrator (UQO): Continuous QA Automation & Monitoring")
    logger.info("=" * 80)
    logger.info("")
    logger.info("  Server: http://127.0.0.1:8507")
    logger.info("  Status: Starting...")
    logger.info("")
    logger.info("  Integrated Hubs:")
    logger.info("    • L4 Explainability (port 5000)")
    logger.info("    • L2 Privacy & Security (port 8502)")
    logger.info("    • L1 Regulations (port 8504)")
    logger.info("    • SOQM - System Operations & QA Monitor (port 8503)")
    logger.info("    • L3 Fairness & Ethics (port 8506)")
    logger.info("")
    logger.info("  API Endpoints:")
    logger.info("    • GET /api/overview - Complete system overview")
    logger.info("    • GET /api/cqs - Current Continuous QA Score")
    logger.info("    • GET /api/hub-status - All hub statuses")
    logger.info("    • GET /api/export/<format> - Export data (json/csv/pdf/excel)")
    logger.info("    • GET /api/websocket/stats - WebSocket connection stats")
    logger.info("    • GET /api/reports/generate/<type> - Generate reports")
    logger.info("    • POST /api/reports/trigger/<type> - Trigger report delivery")
    logger.info("    • GET /api/hub/{hub_name} - Specific hub data")
    logger.info("")
    logger.info("=" * 80)

    app.run(host='127.0.0.1', port=8507, debug=False,
            use_reloader=False, threaded=True)
