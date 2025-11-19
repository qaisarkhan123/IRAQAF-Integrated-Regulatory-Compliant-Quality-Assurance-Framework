from flask import Flask, render_template_string, jsonify
import json
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
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
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(138, 43, 226, 0.1) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #00d4ff;
            font-size: 1.1em;
            margin-top: 10px;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .nav-tabs button {
            padding: 10px 20px;
            border: 2px solid rgba(0, 212, 255, 0.3);
            background: transparent;
            color: #00d4ff;
            cursor: pointer;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        
        .nav-tabs button:hover {
            background: rgba(0, 212, 255, 0.1);
            border-color: #00d4ff;
        }
        
        .nav-tabs button.active {
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            border-color: transparent;
            color: #000;
            font-weight: bold;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .module-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(138, 43, 226, 0.05) 100%);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .module-card:hover {
            transform: translateY(-5px);
            border-color: #00d4ff;
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
        }
        
        .module-card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .score-display {
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 15px 0;
        }
        
        .score-circle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.3em;
            background: conic-gradient(#00ff88 0deg, #00ff88 var(--score-angle), rgba(0, 255, 136, 0.1) var(--score-angle), rgba(0, 255, 136, 0.1) 360deg);
            color: #00ff88;
        }
        
        .score-info h4 {
            color: #fff;
            margin-bottom: 5px;
        }
        
        .score-info p {
            color: #888;
            font-size: 0.9em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status-compliant {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid #00ff88;
        }
        
        .status-warning {
            background: rgba(255, 200, 0, 0.2);
            color: #ffc800;
            border: 1px solid #ffc800;
        }
        
        .status-alert {
            background: rgba(255, 100, 100, 0.2);
            color: #ff6464;
            border: 1px solid #ff6464;
        }
        
        .details-text {
            color: #aaa;
            font-size: 0.9em;
            line-height: 1.6;
            margin-top: 15px;
        }
        
        .overall-score {
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(138, 43, 226, 0.1) 100%);
            border: 2px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
            margin-top: 30px;
        }
        
        .overall-score h2 {
            color: #00d4ff;
            margin-bottom: 15px;
        }
        
        .overall-score-number {
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .sub-score {
            display: inline-block;
            margin: 8px 12px;
            padding: 8px 15px;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 20px;
            color: #00d4ff;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        
        .api-section {
            background: rgba(0, 212, 255, 0.05);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .api-section h4 {
            color: #00d4ff;
            margin-bottom: 10px;
        }
        
        .api-endpoint {
            background: rgba(0, 0, 0, 0.3);
            padding: 10px 15px;
            border-radius: 6px;
            color: #00ff88;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin: 8px 0;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>L1 Regulations & Governance Hub</h1>
            <p>Regulatory Compliance Management & Governance Framework</p>
        </div>
        
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('overview')">Overview</button>
            <button class="tab-btn" onclick="switchTab('compliance')">Compliance Status</button>
            <button class="tab-btn" onclick="switchTab('governance')">Governance</button>
            <button class="tab-btn" onclick="switchTab('api')">API</button>
        </div>
        
        <!-- OVERVIEW TAB -->
        <div id="overview" class="tab-content active">
            <div class="modules-grid">
                <div class="module-card">
                    <h3>GDPR Compliance</h3>
                    <div class="score-display">
                        <div class="score-circle" style="--score-angle: 330deg;">92</div>
                        <div class="score-info">
                            <h4>92/100</h4>
                            <p>Data Protection Ready</p>
                        </div>
                    </div>
                    <span class="status-badge status-compliant">Compliant</span>
                    <div class="details-text">
                        <strong>Status:</strong> All data protection requirements met<br/>
                        <strong>Last Check:</strong> Today<br/>
                        <strong>Coverage:</strong> 100% of data flows
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>EU AI Act</h3>
                    <div class="score-display">
                        <div class="score-circle" style="--score-angle: 316deg;">88</div>
                        <div class="score-info">
                            <h4>88/100</h4>
                            <p>AI Governance Aligned</p>
                        </div>
                    </div>
                    <span class="status-badge status-compliant">Aligned</span>
                    <div class="details-text">
                        <strong>Status:</strong> Risk-based AI governance compliant<br/>
                        <strong>Classification:</strong> High-Risk AI<br/>
                        <strong>Requirements:</strong> 97% met
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>ISO 13485</h3>
                    <div class="score-display">
                        <div class="score-circle" style="--score-angle: 306deg;">85</div>
                        <div class="score-info">
                            <h4>85/100</h4>
                            <p>Medical Device QMS</p>
                        </div>
                    </div>
                    <span class="status-badge status-compliant">Valid</span>
                    <div class="details-text">
                        <strong>Status:</strong> Quality Management System certified<br/>
                        <strong>Certificate:</strong> Valid until 2026<br/>
                        <strong>Scope:</strong> Full device lifecycle
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>IEC 62304</h3>
                    <div class="score-display">
                        <div class="score-circle" style="--score-angle: 324deg;">90</div>
                        <div class="score-info">
                            <h4>90/100</h4>
                            <p>Software Development</p>
                        </div>
                    </div>
                    <span class="status-badge status-compliant">Certified</span>
                    <div class="details-text">
                        <strong>Status:</strong> Software lifecycle processes defined<br/>
                        <strong>Classification:</strong> Class B/C<br/>
                        <strong>Documentation:</strong> Complete
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>FDA Guidance</h3>
                    <div class="score-display">
                        <div class="score-circle" style="--score-angle: 288deg;">80</div>
                        <div class="score-info">
                            <h4>80/100</h4>
                            <p>AI/ML Compliance</p>
                        </div>
                    </div>
                    <span class="status-badge status-warning">In Progress</span>
                    <div class="details-text">
                        <strong>Status:</strong> FDA AI/ML guidance being implemented<br/>
                        <strong>Stage:</strong> Pre-submission phase<br/>
                        <strong>Readiness:</strong> 95% complete
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>Governance Framework</h3>
                    <div class="score-display">
                        <div class="score-circle" style="--score-angle: 320deg;">89</div>
                        <div class="score-info">
                            <h4>89/100</h4>
                            <p>Overall Governance</p>
                        </div>
                    </div>
                    <span class="status-badge status-compliant">Strong</span>
                    <div class="details-text">
                        <strong>Status:</strong> Governance structures in place<br/>
                        <strong>Oversight:</strong> Executive-level review<br/>
                        <strong>Audit:</strong> Quarterly assessments
                    </div>
                </div>
            </div>
            
            <div class="overall-score">
                <h2>Overall SAI Score</h2>
                <div class="overall-score-number">87/100</div>
                <p style="margin-top: 15px; color: #aaa;">Comprehensive Regulatory Compliance Assessment</p>
                <div style="margin-top: 20px;">
                    <span class="sub-score">GDPR 92</span>
                    <span class="sub-score">EU AI 88</span>
                    <span class="sub-score">ISO 85</span>
                    <span class="sub-score">IEC 90</span>
                    <span class="sub-score">FDA 80</span>
                </div>
            </div>
        </div>
        
        <!-- COMPLIANCE STATUS TAB -->
        <div id="compliance" class="tab-content">
            <div class="modules-grid">
                <div class="module-card">
                    <h3>Data Protection</h3>
                    <div class="details-text">
                        <strong>GDPR Article 32:</strong> Security measures in place<br/>
                        <strong>Data Minimization:</strong> Implemented<br/>
                        <strong>Consent Management:</strong> Automated system<br/>
                        <strong>DPA Notification:</strong> Current<br/>
                        <span class="status-badge status-compliant" style="display: block; margin-top: 10px;">Active</span>
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>AI Risk Classification</h3>
                    <div class="details-text">
                        <strong>Prohibited Risk:</strong> None detected<br/>
                        <strong>High Risk:</strong> 3 systems identified<br/>
                        <strong>Limited Risk:</strong> 5 systems documented<br/>
                        <strong>Minimal Risk:</strong> 12 systems<br/>
                        <span class="status-badge status-compliant" style="display: block; margin-top: 10px;">Managed</span>
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>Software Lifecycle</h3>
                    <div class="details-text">
                        <strong>Planning:</strong> Complete<br/>
                        <strong>Development:</strong> IEC 62304 compliant<br/>
                        <strong>Testing:</strong> Automated CI/CD<br/>
                        <strong>Documentation:</strong> Full traceability<br/>
                        <span class="status-badge status-compliant" style="display: block; margin-top: 10px;">Certified</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- GOVERNANCE TAB -->
        <div id="governance" class="tab-content">
            <div class="modules-grid">
                <div class="module-card">
                    <h3>Executive Oversight</h3>
                    <div class="details-text">
                        <strong>Board Committee:</strong> Compliance & Risk<br/>
                        <strong>Review Frequency:</strong> Quarterly<br/>
                        <strong>Decision Authority:</strong> CRO & Legal<br/>
                        <strong>Escalation Path:</strong> CEO/Board level<br/>
                        <span class="status-badge status-compliant" style="display: block; margin-top: 10px;">Active</span>
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>Audit & Compliance</h3>
                    <div class="details-text">
                        <strong>Internal Audit:</strong> Quarterly reviews<br/>
                        <strong>External Audit:</strong> Annual assessment<br/>
                        <strong>Third-Party:</strong> Ongoing certifications<br/>
                        <strong>Gap Analysis:</strong> Continuous monitoring<br/>
                        <span class="status-badge status-compliant" style="display: block; margin-top: 10px;">Current</span>
                    </div>
                </div>
                
                <div class="module-card">
                    <h3>Change Management</h3>
                    <div class="details-text">
                        <strong>Regulatory Updates:</strong> Monitored weekly<br/>
                        <strong>Impact Assessment:</strong> Required for changes<br/>
                        <strong>Implementation:</strong> Controlled & tracked<br/>
                        <strong>Documentation:</strong> Version controlled<br/>
                        <span class="status-badge status-compliant" style="display: block; margin-top: 10px;">Established</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- API TAB -->
        <div id="api" class="tab-content">
            <div class="api-section">
                <h4>Available API Endpoints</h4>
                <p style="color: #aaa; margin-bottom: 15px;">Base URL: http://localhost:8504</p>
                
                <strong style="color: #00d4ff;">Overall Score</strong>
                <div class="api-endpoint">GET /api/score</div>
                <p style="color: #aaa; margin-bottom: 15px;">Returns overall SAI score and module breakdown</p>
                
                <strong style="color: #00d4ff;">Compliance Status</strong>
                <div class="api-endpoint">GET /api/compliance</div>
                <p style="color: #aaa; margin-bottom: 15px;">Returns detailed compliance status for all modules</p>
                
                <strong style="color: #00d4ff;">Governance Details</strong>
                <div class="api-endpoint">GET /api/governance</div>
                <p style="color: #aaa; margin-bottom: 15px;">Returns governance framework information</p>
                
                <strong style="color: #00d4ff;">Module Details</strong>
                <div class="api-endpoint">GET /api/module/{module_name}</div>
                <p style="color: #aaa; margin-bottom: 15px;">Returns details for specific module (gdpr, eu-ai-act, iso-13485, iec-62304, fda)</p>
                
                <strong style="color: #00d4ff;">System Status</strong>
                <div class="api-endpoint">GET /api/status</div>
                <p style="color: #aaa;">Returns system health and last update timestamp</p>
            </div>
        </div>
        
        <div class="footer">
            <p>L1 Regulations & Governance Hub | Last Updated: <span id="timestamp"></span></p>
            <p>Part of IRAQAF Integrated Regulatory Compliant Quality Assurance Framework</p>
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
        
        // Set timestamp
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/score')
def api_score():
    return jsonify({
        'overall_score': 87,
        'modules': {
            'gdpr': 92,
            'eu_ai_act': 88,
            'iso_13485': 85,
            'iec_62304': 90,
            'fda': 80
        },
        'status': 'compliant',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/compliance')
def api_compliance():
    return jsonify({
        'data_protection': 92,
        'ai_risk_classification': 88,
        'software_lifecycle': 90,
        'governance': 89
    })

@app.route('/api/governance')
def api_governance():
    return jsonify({
        'executive_oversight': 'Active',
        'audit_frequency': 'Quarterly',
        'external_audit': 'Annual',
        'change_management': 'Established'
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'running',
        'port': 8504,
        'framework': 'Flask',
        'last_update': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print('Starting L1 Regulations Hub on port 8504...')
    app.run(host='127.0.0.1', port=8504, debug=False, use_reloader=False, threaded=True)
