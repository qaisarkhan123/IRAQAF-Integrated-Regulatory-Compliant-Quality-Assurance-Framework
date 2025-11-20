"""
Module 5 Hub - Enhanced Enterprise Dashboard
Continuous QA Automation & Monitoring System
Port: 8507
"""

from flask import Flask, render_template_string, jsonify
import json
import requests
from datetime import datetime
import math

app = Flask(__name__)

# Hub configuration
HUBS = {
    'l4': {'port': 5000, 'name': 'L4 Explainability', 'weight': 0.20, 'endpoint': '/api/transparency-score'},
    'l2': {'port': 8502, 'name': 'L2 Security', 'weight': 0.25, 'endpoint': '/api/sai'},
    'l1': {'port': 8504, 'name': 'L1 Regulations', 'weight': 0.25, 'endpoint': '/api/score'},
    'l3_ops': {'port': 8503, 'name': 'L3 Operations', 'weight': 0.15, 'endpoint': '/api/health'},
    'l3_fair': {'port': 8506, 'name': 'L3 Fairness', 'weight': 0.15, 'endpoint': '/api/module3/dashboard'},
}

# HTML Template with Professional UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Module 5: Continuous QA Automation & Monitoring</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        
        header {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
        }
        
        header h1 {
            font-size: 32px;
            margin-bottom: 10px;
            color: white;
        }
        
        header p {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: linear-gradient(135deg, #1a1f3a 0%, #252b48 100%);
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 48px rgba(0, 212, 255, 0.2);
        }
        
        .card h3 {
            font-size: 14px;
            color: #00d4ff;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .score-display {
            font-size: 48px;
            font-weight: bold;
            margin: 15px 0;
            padding: 20px;
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
            border: 2px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            text-align: center;
        }
        
        .score-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 20px;
        }
        
        .gauge {
            position: relative;
            width: 100%;
            height: 150px;
            margin: 20px 0;
        }
        
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status-online {
            background: rgba(0, 255, 100, 0.2);
            color: #00ff64;
            border: 1px solid #00ff64;
        }
        
        .status-offline {
            background: rgba(255, 50, 50, 0.2);
            color: #ff3232;
            border: 1px solid #ff3232;
        }
        
        .status-warning {
            background: rgba(255, 200, 0, 0.2);
            color: #ffc800;
            border: 1px solid #ffc800;
        }
        
        .chart-container {
            position: relative;
            width: 100%;
            height: 400px;
            background: linear-gradient(135deg, #1a1f3a 0%, #252b48 100%);
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }
        
        .alerts-container {
            background: linear-gradient(135deg, #1a1f3a 0%, #252b48 100%);
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }
        
        .alert-item {
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        .alert-critical {
            border-left-color: #ff3232;
            background: rgba(255, 50, 50, 0.1);
        }
        
        .alert-warning {
            border-left-color: #ffc800;
            background: rgba(255, 200, 0, 0.1);
        }
        
        .alert-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .alert-reason {
            font-size: 12px;
            color: #aaa;
            margin-top: 5px;
        }
        
        .hub-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .hub-card {
            background: linear-gradient(135deg, #1a1f3a 0%, #252b48 100%);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid rgba(0, 212, 255, 0.2);
        }
        
        .hub-name {
            font-size: 14px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .hub-score {
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
        }
        
        .score-excellent {
            color: #00ff64 !important;
        }
        
        .score-good {
            color: #ffc800 !important;
        }
        
        .score-warning {
            color: #ff9500 !important;
        }
        
        .score-critical {
            color: #ff3232 !important;
        }
        
        .hub-meta {
            font-size: 11px;
            color: #666;
            margin-top: 10px;
            line-height: 1.6;
        }
        
        .reasoning-section {
            background: linear-gradient(135deg, #1a1f3a 0%, #252b48 100%);
            padding: 25px;
            border-radius: 10px;
            border-left: 4px solid #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }
        
        .reasoning-title {
            font-size: 16px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .reasoning-item {
            padding: 15px;
            margin-bottom: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-left: 3px solid #00d4ff;
            border-radius: 4px;
        }
        
        .reasoning-item-title {
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 5px;
        }
        
        .reasoning-item-text {
            font-size: 13px;
            color: #aaa;
            line-height: 1.5;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 20px;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
        }
        
        .refresh-btn:active {
            transform: translateY(0);
        }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 40px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Module 5: Continuous QA Automation & Monitoring</h1>
            <p>Unified Quality Assurance Control Tower - Real-Time System Health Dashboard</p>
        </header>
        
        <!-- Quick Summary Cards -->
        <div style="background: rgba(0, 212, 255, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00d4ff;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; font-size: 13px;">
                <div><span style="color: #00d4ff;">🎯 CQS Target:</span> <span style="color: #00ff64; font-weight: bold;">≥ 75%</span></div>
                <div><span style="color: #00d4ff;">⚙️ Update Frequency:</span> <span style="color: #ffc800; font-weight: bold;">Every 30 seconds</span></div>
                <div><span style="color: #00d4ff;">📡 Hub Integration:</span> <span style="color: #9d4edd; font-weight: bold;">5 Active Hubs</span></div>
                <div><span style="color: #00d4ff;">🔐 Formula:</span> <span style="color: #aaa; font-weight: bold;">(L4×20% + L2×25% + L1×25% + L3-OPS×15% + L3-FAIR×15%)</span></div>
            </div>
        </div>
        
        <!-- Main CQS Score -->
        <div class="grid">
            <div class="card">
                <h3>Continuous QA Score</h3>
                <div class="score-display" id="cqs-score">0%</div>
                <div class="score-label">Master quality metric aggregating all 5 hub assessments</div>
                <div style="font-size: 12px; color: #888;">
                    Last Updated: <span id="last-update">--:--:-- --</span>
                </div>
            </div>
            
            <div class="card">
                <h3>System Status</h3>
                <div style="margin-top: 20px;">
                    <div style="margin-bottom: 15px;">
                        <div style="font-size: 12px; color: #00ff64;">Critical Issues</div>
                        <div style="font-size: 28px; color: #ff3232;" id="critical-count">0</div>
                    </div>
                    <div>
                        <div style="font-size: 12px; color: #ffc800;">Warnings</div>
                        <div style="font-size: 28px; color: #ffc800;" id="warning-count">0</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Hub Connectivity</h3>
                <div style="margin-top: 20px; font-size: 36px;">
                    <span id="online-count" style="color: #00ff64;">0</span>
                    <span style="font-size: 18px; color: #666;"> / 5 Online</span>
                </div>
                <div style="margin-top: 15px; font-size: 12px; color: #888;">
                    <div>Avg Response Time: <span id="avg-response">--ms</span></div>
                    <div>Last Sync: <span id="last-sync">--:--:-- --</span></div>
                </div>
            </div>
        </div>
        
        <!-- Hub Scores Grid -->
        <div style="margin-bottom: 30px;">
            <h2 style="color: #00d4ff; margin-bottom: 20px; font-size: 18px; text-transform: uppercase; letter-spacing: 1px;">Individual Hub Scores</h2>
            <div class="hub-grid" id="hub-scores">
                <!-- Populated by JavaScript -->
            </div>
        </div>
        
        <!-- Charts Section -->
        <div class="chart-container">
            <h3 style="color: #00d4ff; margin-bottom: 20px;">CQS Breakdown by Hub</h3>
            <canvas id="cqsChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h3 style="color: #00d4ff; margin-bottom: 20px;">Hub Contribution Analysis</h3>
            <canvas id="contributionChart"></canvas>
        </div>
        
        <!-- Active Alerts -->
        <div class="alerts-container">
            <h3 style="color: #00d4ff; margin-bottom: 20px;">⚠️ Active Alerts</h3>
            <div id="alerts-list">
                <div style="color: #666;">No alerts at this time</div>
            </div>
        </div>
        
        <!-- Reasoning Section -->
        <div class="reasoning-section">
            <div class="reasoning-title">📋 Why These Scores?</div>
            <div id="reasoning-list">
                <!-- Populated by JavaScript -->
            </div>
        </div>
        
        <!-- Hub Status Table -->
        <div class="reasoning-section">
            <div class="reasoning-title">🔄 Hub Status Overview</div>
            <div id="hub-status-table" style="overflow-x: auto;">
                <!-- Populated by JavaScript -->
            </div>
        </div>
        
        <button class="refresh-btn" onclick="fetchData()">🔄 Refresh Now</button>
        
        <div class="footer">
            <p>Module 5 Hub • Continuous QA Automation & Monitoring • Port 8507</p>
        </div>
    </div>
    
    <script>
        let cqsChart = null;
        let contributionChart = null;
        
        async function fetchData() {
            try {
                const response = await fetch('/api/overview');
                const data = await response.json();
                
                updateDashboard(data);
                updateCharts(data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        function updateDashboard(data) {
            // Update CQS Score - ensure it's properly bounded to 0-100%
            const cqsPercentage = data.cqs.overall_cqs;
            const cqsValue = Math.min(100, Math.max(0, cqsPercentage));
            document.getElementById('cqs-score').textContent = cqsValue.toFixed(1) + '%';
            
            // Update timestamps
            document.getElementById('last-update').textContent = new Date(data.timestamp).toLocaleTimeString();
            document.getElementById('last-sync').textContent = new Date(data.timestamp).toLocaleTimeString();
            
            // Count alerts
            let criticalCount = 0, warningCount = 0;
            data.alerts.forEach(alert => {
                if (alert.severity === 'CRITICAL') criticalCount++;
                else if (alert.severity === 'WARNING') warningCount++;
            });
            
            document.getElementById('critical-count').textContent = criticalCount;
            document.getElementById('warning-count').textContent = warningCount;
            
            // Count online hubs
            let onlineCount = 0;
            let totalResponse = 0;
            data.hubs.forEach(hub => {
                if (hub.is_healthy) onlineCount++;
                totalResponse += hub.response_time_ms;
            });
            
            document.getElementById('online-count').textContent = onlineCount;
            document.getElementById('avg-response').textContent = (totalResponse / data.hubs.length).toFixed(1);
            
            // Update hub scores grid
            const hubScoresHtml = data.hubs.map(hub => `
                <div class="hub-card">
                    <div class="hub-name">${hub.hub_name}</div>
                    <div class="hub-score ${getScoreClass(hub.normalized_score)}">${(hub.normalized_score * 100).toFixed(1)}%</div>
                    <div class="hub-meta">
                        <div>Status: <span class="status-badge ${hub.is_healthy ? 'status-online' : 'status-offline'}">${hub.is_healthy ? '✓ Online' : '✗ Offline'}</span></div>
                        <div>Response: ${hub.response_time_ms.toFixed(2)}ms</div>
                        <div>Weight: ${(hub.weight * 100).toFixed(0)}% of CQS</div>
                    </div>
                </div>
            `).join('');
            document.getElementById('hub-scores').innerHTML = hubScoresHtml;
            
            // Update alerts
            const alertsHtml = data.alerts.length ? data.alerts.map(alert => `
                <div class="alert-item ${alert.severity === 'CRITICAL' ? 'alert-critical' : 'alert-warning'}">
                    <div class="alert-title">${alert.severity === 'CRITICAL' ? '🔴' : '🟡'} ${alert.message}</div>
                    <div class="alert-reason">Hub: ${alert.hub_name} | Reason: ${alert.reason}</div>
                </div>
            `).join('') : '<div style="color: #666;">✓ All systems operating normally</div>';
            document.getElementById('alerts-list').innerHTML = alertsHtml;
            
            // Update reasoning
            const reasoningHtml = data.hubs.map(hub => `
                <div class="reasoning-item">
                    <div class="reasoning-item-title">${hub.hub_name}: ${(hub.normalized_score * 100).toFixed(1)}%</div>
                    <div class="reasoning-item-text">
                        ${hub.is_healthy ? '✓ Hub is responsive and healthy' : '✗ Hub is unreachable'}.
                        Weight in CQS: ${(hub.weight * 100).toFixed(0)}%.
                        Contribution: ${((hub.normalized_score * hub.weight) * 100).toFixed(2)}% of final score.
                        Response time: ${hub.response_time_ms.toFixed(2)}ms.
                    </div>
                </div>
            `).join('');
            document.getElementById('reasoning-list').innerHTML = reasoningHtml;
            
            // Update hub status table
            const tableHtml = `
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <tr style="border-bottom: 2px solid rgba(0, 212, 255, 0.3); background: rgba(0, 212, 255, 0.05);">
                        <th style="text-align: left; padding: 12px; color: #00d4ff; font-weight: bold;">Hub Name</th>
                        <th style="text-align: center; padding: 12px; color: #00d4ff; font-weight: bold;">Score</th>
                        <th style="text-align: center; padding: 12px; color: #00d4ff; font-weight: bold;">Status</th>
                        <th style="text-align: center; padding: 12px; color: #00d4ff; font-weight: bold;">Response (ms)</th>
                        <th style="text-align: center; padding: 12px; color: #00d4ff; font-weight: bold;">CQS Weight</th>
                    </tr>
                    ${data.hubs.map((hub, idx) => `
                        <tr style="border-bottom: 1px solid rgba(0, 212, 255, 0.1); background: ${idx % 2 ? 'rgba(0, 0, 0, 0.1)' : 'transparent'};">
                            <td style="padding: 10px; color: #e0e0e0;">${hub.hub_name}</td>
                            <td style="text-align: center; padding: 10px; color: ${getScoreColor(hub.normalized_score)}; font-weight: bold;">${(hub.normalized_score * 100).toFixed(1)}%</td>
                            <td style="text-align: center; padding: 10px;"><span class="status-badge ${hub.is_healthy ? 'status-online' : 'status-offline'}">${hub.is_healthy ? '✓ Online' : '✗ Offline'}</span></td>
                            <td style="text-align: center; padding: 10px; color: #aaa;">${hub.response_time_ms.toFixed(2)}</td>
                            <td style="text-align: center; padding: 10px; color: #00d4ff; font-weight: bold;">${(hub.weight * 100).toFixed(0)}%</td>
                        </tr>
                    `).join('')}
                </table>
            `;
            document.getElementById('hub-status-table').innerHTML = tableHtml;
        }
        
        function updateCharts(data) {
            const labels = data.hubs.map(h => h.hub_name);
            const scores = data.hubs.map(h => (h.normalized_score * 100));
            const colors = data.hubs.map(h => getScoreColor(h.normalized_score));
            
            // CQS Breakdown Chart
            if (cqsChart) cqsChart.destroy();
            const cqsCtx = document.getElementById('cqsChart').getContext('2d');
            cqsChart = new Chart(cqsCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Hub Score (%)',
                        data: scores,
                        backgroundColor: colors,
                        borderColor: colors,
                        borderWidth: 2,
                        borderRadius: 6,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 10,
                            titleColor: '#00d4ff',
                            bodyColor: '#e0e0e0',
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: { color: '#888' },
                            grid: { color: 'rgba(0, 212, 255, 0.1)' },
                        },
                        x: {
                            ticks: { color: '#888' },
                            grid: { display: false },
                        }
                    }
                }
            });
            
            // Contribution Chart
            if (contributionChart) contributionChart.destroy();
            const contributionCtx = document.getElementById('contributionChart').getContext('2d');
            const contributions = data.hubs.map(h => ((h.normalized_score * h.weight) * 100));
            contributionChart = new Chart(contributionCtx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: contributions,
                        backgroundColor: ['#00d4ff', '#ff3232', '#00ff64', '#ffc800', '#9d4edd'],
                        borderColor: '#1a1f3a',
                        borderWidth: 2,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#888', padding: 15 }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 10,
                            titleColor: '#00d4ff',
                            bodyColor: '#e0e0e0',
                        }
                    }
                }
            });
        }
        
        function getScoreColor(score) {
            if (score >= 0.8) return '#00ff64';
            if (score >= 0.6) return '#ffc800';
            if (score >= 0.4) return '#ff9500';
            return '#ff3232';
        }
        
        function getScoreClass(score) {
            if (score >= 0.8) return 'score-excellent';
            if (score >= 0.6) return 'score-good';
            if (score >= 0.4) return 'score-warning';
            return 'score-critical';
        }
        
        // Fetch data on load
        fetchData();
        setInterval(fetchData, 30000);
    </script>
</body>
</html>
'''


@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/overview')
def api_overview():
    """Get complete system overview with all hub data"""
    hubs_data = []
    total_response_time = 0
    timestamp = datetime.now()

    for hub_key, hub_config in HUBS.items():
        try:
            url = f"http://127.0.0.1:{hub_config['port']}{hub_config['endpoint']}"
            response = requests.get(url, timeout=2)
            response.raise_for_status()

            data = response.json()

            # Extract score based on response structure
            score = 0
            if isinstance(data, dict):
                # Try various possible field names (including L3 Fairness format)
                score = (data.get('transparency_score') or
                         data.get('sai_score') or
                         data.get('overall_score') or
                         data.get('overall_score_pct') or
                         data.get('system_health_score') or
                         data.get('overall_fairness_score') or
                         data.get('score') or
                         data.get('value') or 0)

                # Handle nested response structures
                if 'overall_cqs' in data:
                    score = data['overall_cqs']
                if 'health_score' in data:
                    score = data['health_score']
            elif isinstance(data, (int, float)):
                score = float(data)

            # Convert to 0-1 range if necessary (smart scaling)
            # If score > 1, assume it's already in 0-100% range
            if score > 1:
                score = score / 100.0
            
            # Ensure within bounds
            normalized_score = min(1.0, max(0.0, float(score)))
            response_time = response.elapsed.total_seconds() * 1000
            
            # Extract last_update timestamp with fallback
            last_update = data.get('last_update') or data.get('timestamp') or datetime.now().isoformat()
            if not last_update or last_update == 'null':
                last_update = 'No data'

            hubs_data.append({
                'hub_key': hub_key,
                'hub_name': hub_config['name'],
                'normalized_score': normalized_score,
                'response_time_ms': response_time,
                'is_healthy': True,
                'weight': hub_config['weight'],
                'error': None,
                'last_update': last_update
            })
            total_response_time += response_time
        except Exception as e:
            hubs_data.append({
                'hub_key': hub_key,
                'hub_name': hub_config['name'],
                'normalized_score': 0.0,
                'response_time_ms': 0.0,
                'is_healthy': False,
                'weight': hub_config['weight'],
                'error': str(e)
            })

    # Calculate CQS - MUST be between 0 and 1, then multiply by 100 for display
    system_cqs = sum(hub['normalized_score'] * hub['weight']
                     for hub in hubs_data)
    # Ensure CQS is within 0-1 range before converting to percentage
    system_cqs = min(1.0, max(0.0, system_cqs))

    # Generate alerts
    alerts = []
    for hub in hubs_data:
        if not hub['is_healthy']:
            alerts.append({
                'hub_name': hub['hub_name'],
                'severity': 'CRITICAL',
                'message': f"🔴 {hub['hub_name']} Hub Unreachable",
                'reason': 'Connection failed - hub may be offline'
            })
        elif hub['normalized_score'] < 0.65 and hub['is_healthy']:
            alerts.append({
                'hub_name': hub['hub_name'],
                'severity': 'WARNING',
                'message': f"🟡 {hub['hub_name']} Score Below Threshold",
                'reason': f"Score: {(hub['normalized_score'] * 100):.1f}% (threshold: 65%)"
            })

    return jsonify({
        'timestamp': timestamp.isoformat(),
        'cqs': {
            'overall_cqs': system_cqs * 100,
            'formula': '(L4×20%) + (L2×25%) + (L1×25%) + (L3-OPS×15%) + (L3-FAIR×15%)'
        },
        'hubs': hubs_data,
        'alerts': alerts,
        'system_health': {
            'online_hubs': sum(1 for h in hubs_data if h['is_healthy']),
            'total_hubs': len(hubs_data),
            'avg_response_time': total_response_time / len(hubs_data) if hubs_data else 0
        }
    })


if __name__ == '__main__':
    print('🚀 Starting Module 5 Hub - Enhanced Dashboard')
    print('📊 Access at: http://localhost:8507')
    print('⚡ Integrated hubs: L4 (5000), L2 (8502), L1 (8504), L3-Ops (8503), L3-Fair (8506)')
    app.run(host='127.0.0.1', port=8507, debug=False,
            use_reloader=False, threaded=True)
