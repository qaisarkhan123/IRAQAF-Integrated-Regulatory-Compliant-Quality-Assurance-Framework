"""
Privacy & Security Hub - Flask Implementation
Lightweight alternative to Streamlit for port 8502
Provides 10 security modules + L2 historical metrics
"""
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Mock data for modules
MODULES_DATA = {
    "Dashboard Overview": {
        "icon": "📊",
        "metrics": {
            "Security Score": "78/100",
            "Compliance Level": "92%",
            "Risk Level": "Low",
            "Last Audit": "2 hours ago"
        },
        "description": "Real-time security posture and compliance metrics"
    },
    "PII Detection": {
        "icon": "🔍",
        "metrics": {
            "PII Found": "0 instances",
            "Data Scanned": "1.2 GB",
            "Risk Level": "None",
            "Status": "Clean"
        },
        "description": "Detect and anonymize personally identifiable information"
    },
    "Encryption Validator": {
        "icon": "🔐",
        "metrics": {
            "Encrypted Assets": "156/156",
            "Coverage": "100%",
            "Algorithm": "AES-256",
            "Status": "All Secure"
        },
        "description": "Validate encryption status across all data assets"
    },
    "Model Integrity": {
        "icon": "🛡️",
        "metrics": {
            "Models Checked": "8/8",
            "Integrity": "100%",
            "Last Check": "1 hour ago",
            "Status": "Verified"
        },
        "description": "Verify model integrity and prevent tampering"
    },
    "Adversarial Tests": {
        "icon": "⚔️",
        "metrics": {
            "Tests Run": "45",
            "Pass Rate": "98%",
            "Vulnerabilities": "1 minor",
            "Status": "Acceptable"
        },
        "description": "Test models against adversarial attacks"
    },
    "GDPR Rights": {
        "icon": "📋",
        "metrics": {
            "Access Requests": "2 pending",
            "Deletion Requests": "0",
            "Compliance": "100%",
            "Status": "On Track"
        },
        "description": "Manage GDPR data subject rights (access, deletion, portability)"
    },
    "L2 Metrics": {
        "icon": "📈",
        "metrics": {
            "Historical Records": "24",
            "Trend": "Improving",
            "Avg Score": "82/100",
            "Period": "Last 30 days"
        },
        "description": "View L2 security metrics and historical trends"
    },
    "MFA Manager": {
        "icon": "🔑",
        "metrics": {
            "Users Protected": "156/156",
            "MFA Enabled": "100%",
            "Methods": "TOTP, SMS, Email",
            "Status": "Enforced"
        },
        "description": "Multi-factor authentication configuration and status"
    },
    "Data Retention": {
        "icon": "📦",
        "metrics": {
            "Data Stored": "8.5 TB",
            "Compliance": "On Schedule",
            "Records to Delete": "2,341",
            "Status": "Scheduled"
        },
        "description": "Data retention policy enforcement and cleanup"
    },
    "Quick Assessment": {
        "icon": "⚡",
        "metrics": {
            "Last Run": "Today 2:30 PM",
            "Scan Time": "12 minutes",
            "Issues Found": "1",
            "Status": "Complete"
        },
        "description": "Run a quick 10-minute security assessment"
    }
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy & Security Hub</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .header h1 {
            color: #2d3748;
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header p {
            color: #718096;
            font-size: 1.1em;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            padding: 10px 20px;
            background: #e2e8f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 500;
            color: #2d3748;
            transition: all 0.3s ease;
        }
        
        .tab-btn:hover {
            background: #cbd5e0;
            transform: translateY(-2px);
        }
        
        .tab-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .module-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .module-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }
        
        .module-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .module-icon {
            font-size: 2.5em;
        }
        
        .module-title {
            color: #2d3748;
            font-size: 1.3em;
            font-weight: 600;
        }
        
        .module-description {
            color: #718096;
            font-size: 0.95em;
            margin-bottom: 15px;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .metric {
            background: #f7fafc;
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        
        .metric-label {
            color: #718096;
            font-size: 0.85em;
            font-weight: 500;
        }
        
        .metric-value {
            color: #2d3748;
            font-size: 1.1em;
            font-weight: 600;
            margin-top: 5px;
        }
        
        .detail-view {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-top: 20px;
        }
        
        .detail-view h2 {
            color: #2d3748;
            margin-bottom: 25px;
            font-size: 2em;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .detail-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .detail-metric {
            background: #f7fafc;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .detail-metric-label {
            color: #718096;
            font-size: 0.9em;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .detail-metric-value {
            color: #2d3748;
            font-size: 1.8em;
            font-weight: 700;
            margin-top: 10px;
        }
        
        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            margin-top: 50px;
            padding: 20px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            background: #c6f6d5;
            color: #22543d;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .back-link {
            display: inline-block;
            color: white;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .back-link:hover {
            transform: translateX(-5px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Privacy & Security Hub</h1>
            <p>Comprehensive security assessment and compliance monitoring</p>
            <div class="nav-tabs" id="nav-tabs">
                {% for module_name in modules %}
                    <button class="tab-btn {% if loop.first %}active{% endif %}" onclick="selectModule('{{ module_name }}')">
                        {{ modules[module_name].icon }} {{ module_name }}
                    </button>
                {% endfor %}
            </div>
        </div>
        
        {% set first_module = modules | first %}
        <div id="grid-view" class="modules-grid">
            {% for module_name, data in modules.items() %}
                <div class="module-card" onclick="selectModule('{{ module_name }}')">
                    <div class="module-header">
                        <span class="module-icon">{{ data.icon }}</span>
                        <div class="module-title">{{ module_name }}</div>
                    </div>
                    <div class="module-description">{{ data.description }}</div>
                    <div class="metrics">
                        {% for metric_name, metric_value in data.metrics.items() %}
                            <div class="metric">
                                <div class="metric-label">{{ metric_name }}</div>
                                <div class="metric-value">{{ metric_value }}</div>
                            </div>
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}
        </div>
        
        <div id="detail-view" style="display: none;" class="detail-view">
            <a href="#" class="back-link" onclick="backToGrid(event)">← Back to All Modules</a>
            <h2 id="detail-title"></h2>
            <p id="detail-description" style="color: #718096; margin-bottom: 20px; font-size: 1.05em;"></p>
            <div class="detail-metrics" id="detail-metrics"></div>
        </div>
        
        <div class="footer">
            <p>Privacy & Security Hub • Running on Flask • Last updated: {{ timestamp }}</p>
            <p style="font-size: 0.9em; margin-top: 10px;">
                <a href="http://localhost:8501" style="color: rgba(255, 255, 255, 0.8); text-decoration: none;">← Back to Main Dashboard</a>
            </p>
        </div>
    </div>
    
    <script>
        const modulesData = {{ modules_json | safe }};
        
        function selectModule(moduleName) {
            const data = modulesData[moduleName];
            
            // Hide grid, show detail
            document.getElementById('grid-view').style.display = 'none';
            document.getElementById('detail-view').style.display = 'block';
            
            // Update detail view
            document.getElementById('detail-title').innerHTML = data.icon + ' ' + moduleName;
            document.getElementById('detail-description').textContent = data.description;
            
            // Update metrics
            const metricsHtml = Object.entries(data.metrics)
                .map(([label, value]) => `
                    <div class="detail-metric">
                        <div class="detail-metric-label">${label}</div>
                        <div class="detail-metric-value">${value}</div>
                    </div>
                `)
                .join('');
            document.getElementById('detail-metrics').innerHTML = metricsHtml;
            
            // Update active button
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.includes(moduleName)) {
                    btn.classList.add('active');
                }
            });
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        function backToGrid(e) {
            e.preventDefault();
            document.getElementById('grid-view').style.display = 'grid';
            document.getElementById('detail-view').style.display = 'none';
            
            // Clear active state
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.add('active', 'first'));
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main hub page with all modules"""
    return render_template_string(
        HTML_TEMPLATE,
        modules=MODULES_DATA,
        modules_json=json.dumps(MODULES_DATA),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/module/<module_name>')
def get_module(module_name):
    """API endpoint for module data"""
    if module_name in MODULES_DATA:
        return jsonify(MODULES_DATA[module_name])
    return jsonify({"error": "Module not found"}), 404

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Privacy & Security Hub",
        "port": 8502,
        "modules": len(MODULES_DATA),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    import sys
    import io
    
    # Fix emoji encoding on Windows
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n" + "="*70)
    print("PRIVACY & SECURITY HUB - FLASK IMPLEMENTATION")
    print("="*70)
    print("\n> Starting Flask app on port 8502...")
    print("> Access at: http://localhost:8502")
    print("> Modules available: 10 security modules + L2 metrics")
    print("> API health check: http://localhost:8502/health")
    print("\n" + "="*70 + "\n")
    
    # Run Flask app
    app.run(
        host='127.0.0.1',
        port=8502,
        debug=False,
        use_reloader=False,
        use_debugger=False
    )
