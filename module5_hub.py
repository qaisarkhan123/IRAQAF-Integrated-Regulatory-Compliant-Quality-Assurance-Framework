"""
Module 5: Continuous QA Automation & Monitoring - Flask Hub

Serves Module 5 as the 6th hub in the IRAQAF system (port 8507).
Integrates and orchestrates all 5 existing hubs to produce unified QA monitoring.

PORT: 8507
URL: http://localhost:8507
"""

from flask import Flask, render_template_string, jsonify
import logging
import threading
from datetime import datetime, timezone

from module5.orchestrator import Module5Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize orchestrator
orchestrator = Module5Orchestrator(polling_interval_seconds=30)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module 5: Continuous QA Automation & Monitoring</title>
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
            background: linear-gradient(90deg, #00d4ff, #0084ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
            <h1>📊 Module 5: Continuous QA Automation & Monitoring</h1>
            <p>Unified Quality Assurance Control Tower - Integrating All 5 IRAQAF Hubs</p>
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
                    <div class="info-label">L3 Operations</div>
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
        </div>

        <footer>
            <p>Module 5 v1.0 | Continuous QA Automation & Monitoring</p>
            <p>Integrating: L4 Explainability • L2 Security • L1 Compliance • L3 Operations • L3 Fairness</p>
            <p>Port 8507 | <span id="status-indicator">●</span> Live</p>
        </footer>
    </div>

    <script>
        async function refreshData() {
            try {
                const response = await fetch('/api/overview');
                const data = await response.json();
                updateUI(data);
            } catch (error) {
                console.error('Error refreshing:', error);
            }
        }

        function updateUI(data) {
            if (!data.cqs) {
                document.getElementById('hubGrid').innerHTML = '<p style="color: #ff6b6b;">No data available. Starting orchestration...</p>';
                return;
            }

            const cqs = data.cqs;
            const percent = (cqs.overall_cqs * 100).toFixed(1);
            document.getElementById('cqsScore').textContent = percent + '%';
            
            const time = new Date(cqs.timestamp).toLocaleTimeString();
            document.getElementById('lastUpdate').textContent = time;
            document.getElementById('criticalCount').textContent = cqs.critical_issues;
            document.getElementById('warningCount').textContent = cqs.warnings;

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

        // Refresh every 30 seconds
        refreshData();
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve Module 5 dashboard."""
    return render_template_string(HTML_TEMPLATE)


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


if __name__ == '__main__':
    # Start background polling thread
    polling_thread = threading.Thread(target=polling_loop, daemon=True)
    polling_thread.start()

    logger.info("=" * 80)
    logger.info(" Module 5: Continuous QA Automation & Monitoring")
    logger.info("=" * 80)
    logger.info("")
    logger.info("  Server: http://127.0.0.1:8507")
    logger.info("  Status: Starting...")
    logger.info("")
    logger.info("  Integrated Hubs:")
    logger.info("    • L4 Explainability (port 5000)")
    logger.info("    • L2 Privacy & Security (port 8502)")
    logger.info("    • L1 Regulations (port 8504)")
    logger.info("    • L3 Operations (port 8503)")
    logger.info("    • L3 Fairness & Ethics (port 8506)")
    logger.info("")
    logger.info("  API Endpoints:")
    logger.info("    • GET /api/overview - Complete system overview")
    logger.info("    • GET /api/cqs - Current Continuous QA Score")
    logger.info("    • GET /api/hub-status - All hub statuses")
    logger.info("    • GET /api/hub/{hub_name} - Specific hub data")
    logger.info("")
    logger.info("=" * 80)

    app.run(host='127.0.0.1', port=8507, debug=False,
            use_reloader=False, threaded=True)
