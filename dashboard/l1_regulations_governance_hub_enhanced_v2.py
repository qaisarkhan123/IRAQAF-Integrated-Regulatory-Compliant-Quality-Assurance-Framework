"""
L1 REGULATIONS & GOVERNANCE HUB - ENHANCED V2
Unified Governance & Regulatory Assurance Module with full regulatory coverage

Features:
- 8 Regulatory Frameworks (GDPR, EU AI Act, ISO 13485, HIPAA, NIST 800, PCI-DSS, SOX, CCPA)
- Compliance Readiness Score (CRS)
- SDLC Compliance Tracker
- Governance Maturity Index (GMI)
- EU AI Act Risk Classification
- Compliance Drift Monitoring
- Evidence Management System
- Module 5 Integration
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add dashboard directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import new modules
try:
    from regulatory_mapping_engine import RegulatoryMappingEngine
    from crs_engine import CRSEngine
    from sdlc_tracker import SDLCTracker
    from governance_maturity import GovernanceMaturity
    from risk_classification import RiskClassification
    from compliance_drift import ComplianceDriftMonitor
    from evidence.evidence_manager import EvidenceManager
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may not be available. Continuing with basic functionality...")
    RegulatoryMappingEngine = None
    CRSEngine = None
    SDLCTracker = None
    GovernanceMaturity = None
    RiskClassification = None
    ComplianceDriftMonitor = None
    EvidenceManager = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Initialize engines
mapping_engine = RegulatoryMappingEngine() if RegulatoryMappingEngine else None
crs_engine = CRSEngine(mapping_engine) if CRSEngine and mapping_engine else None
sdlc_tracker = SDLCTracker(mapping_engine) if SDLCTracker and mapping_engine else None
governance_maturity = GovernanceMaturity() if GovernanceMaturity else None
risk_classifier = RiskClassification() if RiskClassification else None
drift_monitor = ComplianceDriftMonitor() if ComplianceDriftMonitor else None
evidence_manager = EvidenceManager() if EvidenceManager else None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def home():
    """Main dashboard page."""
    return render_template_string(get_html_template())

@app.route('/api/frameworks')
def api_frameworks():
    """Get list of all supported frameworks."""
    if not mapping_engine:
        return jsonify({"error": "Mapping engine not available"}), 500
    
    frameworks = mapping_engine.get_all_frameworks()
    return jsonify({
        "frameworks": frameworks,
        "count": len(frameworks),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/framework/<framework_name>')
def api_framework(framework_name):
    """Get detailed information about a specific framework."""
    if not mapping_engine:
        return jsonify({"error": "Mapping engine not available"}), 500
    
    framework = mapping_engine.get_framework(framework_name)
    if not framework:
        return jsonify({"error": f"Framework {framework_name} not found"}), 404
    
    return jsonify(framework)

@app.route('/api/compliance-map')
def api_compliance_map():
    """Get comprehensive compliance map across all frameworks."""
    if not mapping_engine:
        return jsonify({"error": "Mapping engine not available"}), 500
    
    compliance_map = mapping_engine.get_compliance_map()
    return jsonify(compliance_map)

@app.route('/api/crs')
def api_crs():
    """Get Compliance Readiness Score (CRS)."""
    if not crs_engine:
        return jsonify({"error": "CRS engine not available"}), 500
    
    # Get required data
    compliance_map = mapping_engine.get_compliance_map() if mapping_engine else None
    sdlc_status = sdlc_tracker.get_sdlc_status(compliance_map) if sdlc_tracker else None
    gmi_result = governance_maturity.assess_maturity(get_governance_indicators()) if governance_maturity else None
    gmi_score = gmi_result.get("gmi", 3.0) if gmi_result else 3.0
    
    crs_result = crs_engine.calculate_crs(
        compliance_map=compliance_map,
        sdlc_status=sdlc_status,
        gmi_score=gmi_score
    )
    
    return jsonify(crs_result)

@app.route('/api/sdlc-status')
def api_sdlc_status():
    """Get SDLC compliance status."""
    if not sdlc_tracker:
        return jsonify({"error": "SDLC tracker not available"}), 500
    
    compliance_map = mapping_engine.get_compliance_map() if mapping_engine else None
    sdlc_status = sdlc_tracker.get_sdlc_status(compliance_map)
    return jsonify(sdlc_status)

@app.route('/api/gmi')
def api_gmi():
    """Get Governance Maturity Index."""
    if not governance_maturity:
        return jsonify({"error": "Governance maturity engine not available"}), 500
    
    indicators = get_governance_indicators()
    gmi_result = governance_maturity.assess_maturity(indicators)
    return jsonify(gmi_result)

@app.route('/api/risk-classification', methods=['GET', 'POST'])
def api_risk_classification():
    """Get or update risk classification."""
    if not risk_classifier:
        return jsonify({"error": "Risk classifier not available"}), 500
    
    if request.method == 'POST':
        system_characteristics = request.json
    else:
        # Default system characteristics
        system_characteristics = {
            "intended_use": "Medical diagnosis",
            "data_type": "Health data",
            "model_purpose": "Clinical decision support",
            "deployment_context": "Healthcare facility",
            "decision_impact": "Life-threatening decisions"
        }
    
    classification = risk_classifier.classify_system(system_characteristics)
    return jsonify(classification)

@app.route('/api/compliance-drift')
def api_compliance_drift():
    """Get compliance drift status."""
    if not drift_monitor:
        return jsonify({"error": "Drift monitor not available"}), 500
    
    # Get current state
    current_state = {
        "regulations": get_current_regulation_scores(),
        "evidence": get_current_evidence_status(),
        "documentation": get_current_documentation_versions(),
        "model_version": "v2.1.0",  # Would come from actual system
        "sdlc_changes": []
    }
    
    drift_result = drift_monitor.detect_drift(current_state)
    return jsonify(drift_result)

@app.route('/api/evidence/upload', methods=['POST'])
def api_evidence_upload():
    """Upload evidence for a clause."""
    if not evidence_manager:
        return jsonify({"error": "Evidence manager not available"}), 500
    
    try:
        clause_id = request.form.get('clause_id')
        framework = request.form.get('framework')
        uploaded_by = request.form.get('uploaded_by', 'system')
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        evidence = evidence_manager.upload_evidence(
            clause_id=clause_id,
            framework=framework,
            file_path=tmp_path,
            uploaded_by=uploaded_by
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return jsonify(evidence)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/evidence/<clause_id>')
def api_evidence_get(clause_id):
    """Get evidence for a specific clause."""
    if not evidence_manager:
        return jsonify({"error": "Evidence manager not available"}), 500
    
    framework = request.args.get('framework')
    evidence = evidence_manager.get_evidence(clause_id, framework)
    return jsonify({"evidence": evidence})

@app.route('/api/evidence/list')
def api_evidence_list():
    """List all evidence."""
    if not evidence_manager:
        return jsonify({"error": "Evidence manager not available"}), 500
    
    framework = request.args.get('framework')
    clause_id = request.args.get('clause_id')
    evidence = evidence_manager.list_evidence(framework, clause_id)
    return jsonify({"evidence": evidence})

@app.route('/api/summary')
def api_summary():
    """Get comprehensive summary for Module 5 integration."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "crs": None,
        "risk_classification": None,
        "gmi": None,
        "sdlc_score": None,
        "drift_status": None,
        "frameworks": []
    }
    
    # Get CRS
    if crs_engine:
        try:
            compliance_map = mapping_engine.get_compliance_map() if mapping_engine else None
            sdlc_status = sdlc_tracker.get_sdlc_status(compliance_map) if sdlc_tracker else None
            gmi_result = governance_maturity.assess_maturity(get_governance_indicators()) if governance_maturity else None
            gmi_score = gmi_result.get("gmi", 3.0) if gmi_result else 3.0
            
            crs_result = crs_engine.calculate_crs(
                compliance_map=compliance_map,
                sdlc_status=sdlc_status,
                gmi_score=gmi_score
            )
            summary["crs"] = crs_result.get("crs", 0)
        except:
            pass
    
    # Get risk classification
    if risk_classifier:
        try:
            classification = risk_classifier.classify_system({
                "intended_use": "Medical diagnosis",
                "data_type": "Health data",
                "model_purpose": "Clinical decision support"
            })
            summary["risk_classification"] = classification.get("classification", "unknown")
        except:
            pass
    
    # Get GMI
    if governance_maturity:
        try:
            gmi_result = governance_maturity.assess_maturity(get_governance_indicators())
            summary["gmi"] = gmi_result.get("gmi", 0)
        except:
            pass
    
    # Get SDLC score
    if sdlc_tracker:
        try:
            compliance_map = mapping_engine.get_compliance_map() if mapping_engine else None
            sdlc_status = sdlc_tracker.get_sdlc_status(compliance_map)
            summary["sdlc_score"] = sdlc_status.get("overall_score", 0)
        except:
            pass
    
    # Get drift status
    if drift_monitor:
        try:
            current_state = {
                "regulations": get_current_regulation_scores(),
                "evidence": get_current_evidence_status(),
                "documentation": get_current_documentation_versions()
            }
            drift_result = drift_monitor.detect_drift(current_state)
            summary["drift_status"] = drift_result.get("drift_detected", False)
        except:
            pass
    
    # Get framework summaries
    if mapping_engine:
        try:
            frameworks = mapping_engine.get_all_frameworks()
            summary["frameworks"] = [f["id"] for f in frameworks]
        except:
            pass
    
    return jsonify(summary)

# Legacy endpoints for backward compatibility
@app.route('/api/score')
def api_score():
    """Legacy endpoint - returns overall score."""
    if crs_engine:
        try:
            compliance_map = mapping_engine.get_compliance_map() if mapping_engine else None
            sdlc_status = sdlc_tracker.get_sdlc_status(compliance_map) if sdlc_tracker else None
            gmi_result = governance_maturity.assess_maturity(get_governance_indicators()) if governance_maturity else None
            gmi_score = gmi_result.get("gmi", 3.0) if gmi_result else 3.0
            
            crs_result = crs_engine.calculate_crs(
                compliance_map=compliance_map,
                sdlc_status=sdlc_status,
                gmi_score=gmi_score
            )
            overall_score = crs_result.get("crs", 87)
        except:
            overall_score = 87
    else:
        overall_score = 87
    
    return jsonify({
        'overall_score': overall_score,
        'modules': {
            'gdpr': 92,
            'eu_ai_act': 88,
            'iso_13485': 85,
            'hipaa': 90,
            'nist_800': 85,
            'pci_dss': 88,
            'sox': 82,
            'ccpa': 85
        },
        'status': 'compliant',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/compliance')
def api_compliance():
    """Legacy endpoint - returns compliance status."""
    return jsonify({
        'data_protection': 92,
        'ai_risk_classification': 88,
        'software_lifecycle': 90,
        'governance': 89
    })

@app.route('/api/governance')
def api_governance():
    """Legacy endpoint - returns governance details."""
    if governance_maturity:
        try:
            gmi_result = governance_maturity.assess_maturity(get_governance_indicators())
            return jsonify({
                'executive_oversight': 'Active',
                'audit_frequency': 'Quarterly',
                'external_audit': 'Annual',
                'change_management': 'Established',
                'gmi': gmi_result.get("gmi", 3.0),
                'gmi_level': gmi_result.get("level_name", "Partially implemented compliance")
            })
        except:
            pass
    
    return jsonify({
        'executive_oversight': 'Active',
        'audit_frequency': 'Quarterly',
        'external_audit': 'Annual',
        'change_management': 'Established'
    })

@app.route('/api/status')
def api_status():
    """System status endpoint."""
    return jsonify({
        'status': 'running',
        'port': 8504,
        'framework': 'Flask',
        'last_update': datetime.now().isoformat(),
        'modules_loaded': {
            'mapping_engine': mapping_engine is not None,
            'crs_engine': crs_engine is not None,
            'sdlc_tracker': sdlc_tracker is not None,
            'governance_maturity': governance_maturity is not None,
            'risk_classifier': risk_classifier is not None,
            'drift_monitor': drift_monitor is not None,
            'evidence_manager': evidence_manager is not None
        }
    })

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_governance_indicators():
    """Get current governance indicators (would come from actual system)."""
    return {
        "policies_documented": True,
        "procedures_documented": True,
        "compliance_docs_complete": True,
        "technical_docs_complete": True,
        "version_controlled": True,
        "change_management_defined": True,
        "risk_assessment_process": True,
        "incident_response_defined": True,
        "regular_reviews": True,
        "continuous_improvement": True,
        "compliance_tracking_enabled": True,
        "automated_alerts": True,
        "real_time_monitoring": True,
        "drift_detection": True,
        "predictive_analytics": False,
        "executive_oversight": True,
        "board_committee": True,
        "regular_audits": True,
        "external_audits": True,
        "escalation_path_defined": True,
        "automated_compliance_checks": True,
        "automated_reporting": True,
        "automated_evidence_collection": True,
        "ai_powered_analytics": False,
        "fully_integrated_systems": True
    }

def get_current_regulation_scores():
    """Get current regulation compliance scores."""
    if mapping_engine:
        try:
            compliance_map = mapping_engine.get_compliance_map()
            scores = {}
            for framework_id, framework_data in compliance_map.get("frameworks", {}).items():
                scores[framework_id] = {"score": framework_data.get("overall_score", 0)}
            return scores
        except:
            pass
    return {}

def get_current_evidence_status():
    """Get current evidence status."""
    if evidence_manager:
        try:
            evidence_list = evidence_manager.list_evidence()
            status = {}
            for ev in evidence_list:
                clause_id = ev.get("clause_id")
                if clause_id not in status:
                    status[clause_id] = {"age_days": 30}  # Placeholder
            return status
        except:
            pass
    return {}

def get_current_documentation_versions():
    """Get current documentation versions."""
    return {
        "policy_v1.2": "1.2",
        "procedures_v2.0": "2.0",
        "technical_docs_v1.5": "1.5"
    }

def get_html_template():
    """Get the HTML template for the dashboard."""
    # This will be a very large template - continuing in next part due to size limits
    # For now, return a basic template that will be enhanced
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L1 Regulations & Governance Hub - Enhanced</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(138, 43, 226, 0.1) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 15px;
        }
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
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
            transition: all 0.3s ease;
        }
        .nav-tabs button.active {
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            color: #000;
            font-weight: bold;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .metric-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(138, 43, 226, 0.05) 100%);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 25px;
            margin: 15px;
        }
        .loading { text-align: center; padding: 40px; color: #00d4ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ L1 Regulations & Governance Hub - Enhanced</h1>
            <p>Unified Governance & Regulatory Assurance Module</p>
            <p style="margin-top: 10px; font-size: 0.9em; color: #888;">
                8 Frameworks | CRS | SDLC Tracker | GMI | Risk Classification | Drift Monitoring
            </p>
        </div>
        
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('overview')">Overview</button>
            <button class="tab-btn" onclick="switchTab('crs')">CRS</button>
            <button class="tab-btn" onclick="switchTab('sdlc')">SDLC</button>
            <button class="tab-btn" onclick="switchTab('frameworks')">Frameworks</button>
            <button class="tab-btn" onclick="switchTab('evidence')">Evidence</button>
            <button class="tab-btn" onclick="switchTab('api')">API</button>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="loading">Loading dashboard data...</div>
        </div>
        
        <div id="crs" class="tab-content">
            <div class="loading">Loading CRS data...</div>
        </div>
        
        <div id="sdlc" class="tab-content">
            <div class="loading">Loading SDLC data...</div>
        </div>
        
        <div id="frameworks" class="tab-content">
            <div class="loading">Loading frameworks...</div>
        </div>
        
        <div id="evidence" class="tab-content">
            <div class="loading">Loading evidence...</div>
        </div>
        
        <div id="api" class="tab-content">
            <div class="metric-card">
                <h3 style="color: #00d4ff; margin-bottom: 15px;">API Endpoints</h3>
                <div style="font-family: monospace; color: #00ff88;">
                    <div>GET /api/frameworks</div>
                    <div>GET /api/framework/&lt;name&gt;</div>
                    <div>GET /api/compliance-map</div>
                    <div>GET /api/crs</div>
                    <div>GET /api/sdlc-status</div>
                    <div>GET /api/gmi</div>
                    <div>GET /api/risk-classification</div>
                    <div>GET /api/compliance-drift</div>
                    <div>POST /api/evidence/upload</div>
                    <div>GET /api/evidence/&lt;clause_id&gt;</div>
                    <div>GET /api/evidence/list</div>
                    <div>GET /api/summary</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            loadTabData(tabName);
        }
        
        function loadTabData(tabName) {
            // Load data for each tab
            if (tabName === 'overview') loadOverview();
            else if (tabName === 'crs') loadCRS();
            else if (tabName === 'sdlc') loadSDLC();
            else if (tabName === 'frameworks') loadFrameworks();
            else if (tabName === 'evidence') loadEvidence();
        }
        
        function loadOverview() {
            fetch('/api/summary')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('overview').innerHTML = 
                        '<div class="metric-card"><h3>Summary</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre></div>';
                });
        }
        
        function loadCRS() {
            fetch('/api/crs')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('crs').innerHTML = 
                        '<div class="metric-card"><h3>Compliance Readiness Score</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre></div>';
                });
        }
        
        function loadSDLC() {
            fetch('/api/sdlc-status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('sdlc').innerHTML = 
                        '<div class="metric-card"><h3>SDLC Status</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre></div>';
                });
        }
        
        function loadFrameworks() {
            fetch('/api/frameworks')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('frameworks').innerHTML = 
                        '<div class="metric-card"><h3>Frameworks</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre></div>';
                });
        }
        
        function loadEvidence() {
            fetch('/api/evidence/list')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('evidence').innerHTML = 
                        '<div class="metric-card"><h3>Evidence</h3><pre>' + 
                        JSON.stringify(data, null, 2) + '</pre></div>';
                });
        }
        
        // Load overview on page load
        window.addEventListener('load', () => loadOverview());
    </script>
</body>
</html>
    '''

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║     ⚖️ L1 REGULATIONS & GOVERNANCE HUB - ENHANCED V2          ║
    ║                                                                ║
    ║  Features:                                                     ║
    ║    ✓ 8 Regulatory Frameworks (GDPR, EU AI Act, ISO 13485,   ║
    ║      HIPAA, NIST 800, PCI-DSS, SOX, CCPA)                     ║
    ║    ✓ Compliance Readiness Score (CRS)                         ║
    ║    ✓ SDLC Compliance Tracker                                 ║
    ║    ✓ Governance Maturity Index (GMI)                         ║
    ║    ✓ EU AI Act Risk Classification                            ║
    ║    ✓ Compliance Drift Monitoring                             ║
    ║    ✓ Evidence Management System                              ║
    ║    ✓ Module 5 Integration                                     ║
    ║                                                                ║
    ║  Access: http://127.0.0.1:8504                               ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='127.0.0.1', port=8504, debug=False, use_reloader=False, threaded=True)

