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
    from regulation_update_service import RegulationUpdateService
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
    RegulationUpdateService = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Initialize engines
mapping_engine = RegulatoryMappingEngine() if RegulatoryMappingEngine else None
crs_engine = CRSEngine(mapping_engine) if CRSEngine and mapping_engine else None
sdlc_tracker = SDLCTracker(mapping_engine) if SDLCTracker and mapping_engine else None
governance_maturity = GovernanceMaturity() if GovernanceMaturity else None
risk_classifier = RiskClassification() if RiskClassification else None
update_service = RegulationUpdateService() if RegulationUpdateService else None
drift_monitor = ComplianceDriftMonitor(update_service=update_service) if ComplianceDriftMonitor else None
evidence_manager = EvidenceManager() if EvidenceManager else None

# Start update service scheduler if available
if update_service:
    try:
        update_service.start_scheduler()
        print("✓ Regulation update scheduler started")
    except Exception as e:
        print(f"Warning: Could not start update scheduler: {e}")

# Configuration flag for auto-apply
AUTO_APPLY_REGULATION_UPDATES = False

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

@app.route('/api/regulations/drift')
def api_regulations_drift():
    """Get regulatory drift status with pending changes."""
    if not update_service:
        return jsonify({"error": "Update service not available"}), 500
    
    try:
        pending_updates = update_service.get_pending_updates()
        
        if len(pending_updates) == 0:
            return jsonify({
                "drift_detected": False,
                "message": "No pending regulation changes",
                "frameworks": []
            })
        
        # Group by framework
        frameworks = {}
        for update in pending_updates:
            framework = update['framework']
            if framework not in frameworks:
                frameworks[framework] = {
                    "framework": framework,
                    "pending_changes": 0,
                    "latest_version": update.get('new_version_tag', 'unknown'),
                    "old_version": update.get('old_version_tag', 'unknown')
                }
            frameworks[framework]["pending_changes"] += 1
        
        return jsonify({
            "drift_detected": True,
            "message": f"{len(pending_updates)} pending regulation change(s) requiring review",
            "pending_count": len(pending_updates),
            "frameworks": list(frameworks.values()),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regulations/updates')
def api_regulations_updates():
    """List all pending regulation updates."""
    if not update_service:
        return jsonify({"error": "Update service not available"}), 500
    
    try:
        pending_updates = update_service.get_pending_updates()
        
        return jsonify({
            "updates": pending_updates,
            "count": len(pending_updates),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regulations/approve/<int:change_id>', methods=['POST'])
def api_approve_regulation(change_id):
    """Approve a regulation change and activate the new version."""
    if not update_service:
        return jsonify({"error": "Update service not available"}), 500
    
    try:
        reviewed_by = request.json.get('reviewed_by', 'admin') if request.json else 'admin'
        success = update_service.approve_change(change_id, reviewed_by)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Change {change_id} approved and version activated",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Change not found or already processed"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regulations/reject/<int:change_id>', methods=['POST'])
def api_reject_regulation(change_id):
    """Reject a regulation change."""
    if not update_service:
        return jsonify({"error": "Update service not available"}), 500
    
    try:
        reviewed_by = request.json.get('reviewed_by', 'admin') if request.json else 'admin'
        success = update_service.reject_change(change_id, reviewed_by)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Change {change_id} rejected",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Change not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/regulations/check-updates', methods=['POST'])
def api_check_updates():
    """Manually trigger a check for regulation updates."""
    if not update_service:
        return jsonify({"error": "Update service not available"}), 500
    
    try:
        changes = update_service.check_for_updates()
        return jsonify({
            "success": True,
            "changes_detected": changes,
            "count": len(changes),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            
            # Apply penalty for pending regulation changes if not auto-apply enabled
            if not AUTO_APPLY_REGULATION_UPDATES and update_service:
                try:
                    pending_updates = update_service.get_pending_updates()
                    if len(pending_updates) > 0:
                        # Apply 5% penalty per pending update (max 20% penalty)
                        penalty_factor = max(0.8, 1.0 - (len(pending_updates) * 0.05))
                        original_crs = crs_result.get("crs", 0)
                        crs_result["crs"] = original_crs * penalty_factor
                        crs_result["regulatory_drift_penalty"] = {
                            "pending_updates": len(pending_updates),
                            "penalty_percentage": (1 - penalty_factor) * 100,
                            "original_crs": original_crs,
                            "adjusted_crs": crs_result["crs"]
                        }
                except:
                    pass
            
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
    pending_updates_count = 0
    if update_service:
        try:
            pending_updates = update_service.get_pending_updates()
            pending_updates_count = len(pending_updates)
        except:
            pass
    
    return jsonify({
        'status': 'running',
        'port': 8504,
        'framework': 'Flask',
        'last_update': datetime.now().isoformat(),
        'pending_regulation_updates': pending_updates_count,
        'modules_loaded': {
            'mapping_engine': mapping_engine is not None,
            'crs_engine': crs_engine is not None,
            'sdlc_tracker': sdlc_tracker is not None,
            'governance_maturity': governance_maturity is not None,
            'risk_classifier': risk_classifier is not None,
            'drift_monitor': drift_monitor is not None,
            'evidence_manager': evidence_manager is not None,
            'update_service': update_service is not None
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
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L1 Regulations & Governance Hub - Enhanced</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a1e 0%, #1a1a3e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 35px;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%);
            border: 2px solid rgba(0, 212, 255, 0.4);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .header h1 {
            font-size: 3em;
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        }
        .header p {
            color: #00d4ff;
            font-size: 1.2em;
            margin-top: 8px;
        }
        .subtitle {
            margin-top: 10px;
            font-size: 0.95em;
            color: #888;
        }
        .nav-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
            padding: 0 10px;
        }
        .nav-tabs button {
            padding: 12px 24px;
            border: 2px solid rgba(0, 212, 255, 0.4);
            background: rgba(0, 212, 255, 0.05);
            color: #00d4ff;
            cursor: pointer;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .nav-tabs button:hover {
            background: rgba(0, 212, 255, 0.15);
            border-color: #00d4ff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
        }
        .nav-tabs button.active {
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            border-color: transparent;
            color: #000;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
        }
        .tab-content { display: none; animation: fadeIn 0.4s ease; }
        .tab-content.active { display: block; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(138, 43, 226, 0.08) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #00d4ff;
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
        }
        .metric-card h3 {
            color: #00d4ff;
            font-size: 1.1em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .score-gauge {
            position: relative;
            width: 200px;
            height: 200px;
            margin: 20px auto;
        }
        .score-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .score-label {
            text-align: center;
            margin-top: 10px;
            color: #888;
            font-size: 0.9em;
        }
        .component-bar {
            margin: 12px 0;
            padding: 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
        }
        .component-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        .component-name {
            color: #00d4ff;
            font-weight: 500;
        }
        .component-value {
            color: #00ff88;
            font-weight: bold;
        }
        .progress-bar {
            height: 8px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff 0%, #8a2be2 100%);
            border-radius: 4px;
            transition: width 0.8s ease;
        }
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 5px;
        }
        .badge-success { background: rgba(0, 255, 136, 0.2); color: #00ff88; border: 1px solid #00ff88; }
        .badge-warning { background: rgba(255, 200, 0, 0.2); color: #ffc800; border: 1px solid #ffc800; }
        .badge-danger { background: rgba(255, 100, 100, 0.2); color: #ff6464; border: 1px solid #ff6464; }
        .badge-info { background: rgba(0, 212, 255, 0.2); color: #00d4ff; border: 1px solid #00d4ff; }
        .framework-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .framework-item {
            background: rgba(0, 212, 255, 0.05);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            color: #00d4ff;
            font-weight: 500;
        }
        .loading {
            text-align: center;
            padding: 60px 20px;
            color: #00d4ff;
            font-size: 1.1em;
        }
        .spinner {
            border: 3px solid rgba(0, 212, 255, 0.1);
            border-top: 3px solid #00d4ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin: 20px 0;
        }
        .crs-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        @media (max-width: 768px) {
            .crs-details { grid-template-columns: 1fr; }
            .metrics-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚖️ L1 Regulations & Governance Hub</h1>
            <p>Unified Governance & Regulatory Assurance Module</p>
            <p class="subtitle">8 Frameworks | CRS | SDLC Tracker | GMI | Risk Classification | Drift Monitoring</p>
        </div>
        
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('overview')">📊 Overview</button>
            <button class="tab-btn" onclick="switchTab('crs')">🎯 CRS</button>
            <button class="tab-btn" onclick="switchTab('sdlc')">🔄 SDLC</button>
            <button class="tab-btn" onclick="switchTab('updates')">🔄 Updates</button>
            <button class="tab-btn" onclick="switchTab('frameworks')">📋 Frameworks</button>
            <button class="tab-btn" onclick="switchTab('evidence')">📁 Evidence</button>
            <button class="tab-btn" onclick="switchTab('api')">🔌 API</button>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="loading">
                <div class="spinner"></div>
                Loading dashboard data...
            </div>
        </div>
        
        <div id="crs" class="tab-content">
            <div class="loading">
                <div class="spinner"></div>
                Loading CRS data...
            </div>
        </div>
        
        <div id="sdlc" class="tab-content">
            <div class="loading">
                <div class="spinner"></div>
                Loading SDLC data...
            </div>
        </div>
        
        <div id="updates" class="tab-content">
            <div class="loading">
                <div class="spinner"></div>
                Loading regulation updates...
            </div>
        </div>
        
        <div id="frameworks" class="tab-content">
            <div class="loading">
                <div class="spinner"></div>
                Loading frameworks...
            </div>
        </div>
        
        <div id="evidence" class="tab-content">
            <div class="loading">
                <div class="spinner"></div>
                Loading evidence...
            </div>
        </div>
        
        <div id="api" class="tab-content">
            <div class="metric-card">
                <h3>🔌 API Endpoints</h3>
                <div style="font-family: 'Courier New', monospace; color: #00ff88; line-height: 2;">
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
        let crsChart = null;
        
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            loadTabData(tabName);
        }
        
        function loadTabData(tabName) {
            if (tabName === 'overview') loadOverview();
            else if (tabName === 'crs') loadCRS();
            else if (tabName === 'sdlc') loadSDLC();
            else if (tabName === 'updates') loadUpdates();
            else if (tabName === 'frameworks') loadFrameworks();
            else if (tabName === 'evidence') loadEvidence();
        }
        
        function loadOverview() {
            Promise.all([
                fetch('/api/summary').then(r => r.json()),
                fetch('/api/crs').then(r => r.json()),
                fetch('/api/regulations/updates').then(r => r.json()).catch(() => ({updates: [], count: 0}))
            ]).then(([summary, crs, updates]) => {
                renderOverview(summary, crs, updates);
            }).catch(err => {
                document.getElementById('overview').innerHTML = 
                    '<div class="loading">Error loading data: ' + err.message + '</div>';
            });
        }
        
        function renderOverview(summary, crs, updates) {
            const crsValue = summary.crs || 0;
            const riskClass = summary.risk_classification || 'unknown';
            const gmiValue = summary.gmi || 0;
            const driftStatus = summary.drift_status;
            const frameworks = summary.frameworks || [];
            const pendingUpdates = updates.updates || [];
            
            const riskBadgeClass = riskClass === 'high_risk' ? 'badge-danger' : 
                                  riskClass === 'prohibited' ? 'badge-danger' : 'badge-warning';
            
            // Banner for pending regulation updates
            const updatesBanner = pendingUpdates.length > 0 ? `
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(255, 200, 0, 0.15) 0%, rgba(255, 100, 100, 0.15) 100%); border-color: #ffc800; margin-bottom: 30px;">
                    <h3 style="color: #ffc800; margin-bottom: 15px;">⚠️ New Regulatory Updates Detected</h3>
                    <p style="color: #fff; margin-bottom: 15px;">
                        <strong>${pendingUpdates.length}</strong> pending regulation change${pendingUpdates.length !== 1 ? 's' : ''} requiring review
                    </p>
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${pendingUpdates.map(update => `
                            <div class="component-bar" style="margin-bottom: 15px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                <div class="component-label" style="margin-bottom: 10px;">
                                    <span class="component-name" style="font-weight: bold; font-size: 1.1em;">${update.framework || 'Unknown'}</span>
                                    <span class="component-value">${update.new_version_tag || 'New Version'}</span>
                                </div>
                                <div style="font-size: 0.9em; color: #aaa; margin-bottom: 10px;">
                                    <div>Old Version: ${update.old_version_tag || 'N/A'}</div>
                                    <div style="margin-top: 5px;">${update.diff_summary || 'Changes detected'}</div>
                                    <div style="margin-top: 5px; font-size: 0.85em; color: #888;">
                                        Created: ${new Date(update.created_at).toLocaleString()}
                                    </div>
                                </div>
                                <div style="display: flex; gap: 10px; margin-top: 10px;">
                                    <button onclick="approveUpdate(${update.id})" style="padding: 8px 16px; background: #00ff88; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                                        ✓ Approve
                                    </button>
                                    <button onclick="rejectUpdate(${update.id})" style="padding: 8px 16px; background: #ff6464; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                                        ✗ Reject
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div style="margin-top: 15px; text-align: center;">
                        <button onclick="switchTab('frameworks'); loadFrameworks()" style="padding: 10px 20px; background: #00d4ff; color: #000; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                            View All Updates
                        </button>
                    </div>
                </div>
            ` : '';
            
            const html = `
                ${updatesBanner}
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>🎯 Compliance Readiness Score</h3>
                        <div class="score-gauge">
                            <canvas id="crsGauge"></canvas>
                        </div>
                        <div class="score-label">${crsValue.toFixed(2)}% Compliance Ready</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>⚠️ Risk Classification</h3>
                        <div style="text-align: center; padding: 30px 0;">
                            <div class="badge ${riskBadgeClass}" style="font-size: 1.2em; padding: 12px 24px;">
                                ${riskClass.toUpperCase().replace('_', ' ')}
                            </div>
                            <div style="margin-top: 20px; color: #888; font-size: 0.9em;">
                                ${riskClass === 'high_risk' ? 'High-risk AI system detected' : 
                                  riskClass === 'prohibited' ? 'Prohibited practices detected' : 
                                  'Limited risk system'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>📈 Governance Maturity Index</h3>
                        <div style="text-align: center; padding: 30px 0;">
                            <div style="font-size: 3em; font-weight: bold; background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                                ${gmiValue.toFixed(1)}/5.0
                            </div>
                            <div style="margin-top: 15px; color: #00ff88; font-weight: 500;">
                                ${gmiValue >= 4.5 ? 'Continuous Optimization' : 
                                  gmiValue >= 3.5 ? 'Fully Implemented' : 
                                  gmiValue >= 2.5 ? 'Partially Implemented' : 'Basic Processes'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>🔄 Compliance Drift Status</h3>
                        <div style="text-align: center; padding: 30px 0;">
                            <div class="badge ${driftStatus ? 'badge-warning' : 'badge-success'}" style="font-size: 1.2em; padding: 12px 24px;">
                                ${driftStatus ? 'DRIFT DETECTED' : 'NO DRIFT'}
                            </div>
                            <div style="margin-top: 20px; color: #888; font-size: 0.9em;">
                                ${driftStatus ? 'Compliance changes detected' : 'System is stable'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>📋 Regulatory Frameworks</h3>
                        <div class="framework-grid">
                            ${frameworks.map(f => `<div class="framework-item">${f}</div>`).join('')}
                        </div>
                        <div style="margin-top: 15px; text-align: center; color: #00ff88; font-weight: 500;">
                            ${frameworks.length} Framework${frameworks.length !== 1 ? 's' : ''} Active
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>📊 CRS Components Breakdown</h3>
                        ${Object.entries(crs.components || {}).map(([key, value]) => `
                            <div class="component-bar">
                                <div class="component-label">
                                    <span class="component-name">${formatComponentName(key)}</span>
                                    <span class="component-value">${value.toFixed(1)}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${value}%"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            document.getElementById('overview').innerHTML = html;
            
            // Render gauge chart
            setTimeout(() => renderCRSGauge(crsValue), 100);
        }
        
        function renderCRSGauge(value) {
            const canvas = document.getElementById('crsGauge');
            if (!canvas) return;
            
            if (crsChart) {
                crsChart.destroy();
            }
            
            const ctx = canvas.getContext('2d');
            crsChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [value, 100 - value],
                        backgroundColor: [
                            value >= 70 ? '#00ff88' : value >= 40 ? '#00d4ff' : '#ff6464',
                            'rgba(255, 255, 255, 0.1)'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    cutout: '75%',
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: false }
                    },
                    responsive: true,
                    maintainAspectRatio: true
                }
            });
        }
        
        function formatComponentName(name) {
            return name.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
        }
        
        function loadCRS() {
            fetch('/api/crs')
                .then(r => r.json())
                .then(data => {
                    const html = `
                        <div class="metric-card">
                            <h3>🎯 Compliance Readiness Score</h3>
                            <div class="score-gauge">
                                <canvas id="crsDetailGauge"></canvas>
                            </div>
                            <div class="score-label">${data.crs.toFixed(2)}% Overall CRS</div>
                        </div>
                        
                        <div class="crs-details">
                            <div class="metric-card">
                                <h3>📊 Component Scores</h3>
                                ${Object.entries(data.components || {}).map(([key, value]) => `
                                    <div class="component-bar">
                                        <div class="component-label">
                                            <span class="component-name">${formatComponentName(key)}</span>
                                            <span class="component-value">${value.toFixed(1)}%</span>
                                        </div>
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: ${value}%"></div>
                                        </div>
                                        <div style="margin-top: 5px; font-size: 0.8em; color: #888;">
                                            Weight: ${((data.weights || {})[key] * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                            
                            <div class="metric-card">
                                <h3>⚖️ Calculation Formula</h3>
                                <div style="line-height: 2; color: #aaa; margin-top: 20px;">
                                    <div>CRS = 0.30 × Regulatory Alignment</div>
                                    <div>+ 0.25 × Evidence Completeness</div>
                                    <div>+ 0.20 × SDLC Alignment</div>
                                    <div>+ 0.15 × Governance Maturity</div>
                                    <div>+ 0.10 × Post-Market Monitoring</div>
                                    <hr style="border-color: rgba(0, 212, 255, 0.3); margin: 15px 0;">
                                    <div style="font-weight: bold; color: #00d4ff; font-size: 1.2em;">
                                        = ${data.crs.toFixed(2)}%
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    document.getElementById('crs').innerHTML = html;
                    setTimeout(() => {
                        const canvas = document.getElementById('crsDetailGauge');
                        if (canvas) {
                            const ctx = canvas.getContext('2d');
                            new Chart(ctx, {
                                type: 'doughnut',
                                data: {
                                    datasets: [{
                                        data: [data.crs, 100 - data.crs],
                                        backgroundColor: [
                                            data.crs >= 70 ? '#00ff88' : data.crs >= 40 ? '#00d4ff' : '#ff6464',
                                            'rgba(255, 255, 255, 0.1)'
                                        ],
                                        borderWidth: 0
                                    }]
                                },
                                options: {
                                    cutout: '75%',
                                    plugins: {
                                        legend: { display: false },
                                        tooltip: { enabled: false }
                                    }
                                }
                            });
                        }
                    }, 100);
                }).catch(err => {
                    document.getElementById('crs').innerHTML = 
                        '<div class="loading">Error loading CRS data: ' + err.message + '</div>';
                });
        }
        
        function loadSDLC() {
            fetch('/api/sdlc-status')
                .then(r => r.json())
                .then(data => {
                    const phases = Object.entries(data.phases || {});
                    const html = `
                        <div class="metric-card">
                            <h3>🔄 SDLC Compliance Overview</h3>
                            <div style="text-align: center; padding: 20px 0;">
                                <div style="font-size: 2.5em; font-weight: bold; background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                                    ${(data.overall_score || 0).toFixed(1)}%
                                </div>
                                <div style="color: #888; margin-top: 10px;">Overall SDLC Coverage</div>
                            </div>
                        </div>
                        
                        <div class="metrics-grid">
                            ${phases.map(([phase, phaseData]) => `
                                <div class="metric-card">
                                    <h3>${phase}</h3>
                                    <div style="margin: 15px 0;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                            <span style="color: #888;">Coverage</span>
                                            <span style="color: #00ff88; font-weight: bold;">${phaseData.clause_coverage.toFixed(1)}%</span>
                                        </div>
                                        <div class="progress-bar">
                                            <div class="progress-fill" style="width: ${phaseData.clause_coverage}%"></div>
                                        </div>
                                        <div style="margin-top: 10px; font-size: 0.85em; color: #888;">
                                            ${phaseData.compliant_clauses || 0} / ${phaseData.total_clauses || 0} clauses compliant
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    `;
                    document.getElementById('sdlc').innerHTML = html;
                }).catch(err => {
                    document.getElementById('sdlc').innerHTML = 
                        '<div class="loading">Error loading SDLC data: ' + err.message + '</div>';
                });
        }
        
        function loadFrameworks() {
            fetch('/api/frameworks')
                .then(r => r.json())
                .then(data => {
                    const html = `
                        <div class="metric-card">
                            <h3>📋 Regulatory Frameworks</h3>
                            <div style="text-align: center; padding: 20px 0; margin-bottom: 20px;">
                                <div style="font-size: 2em; color: #00ff88; font-weight: bold;">
                                    ${data.count || 0}
                                </div>
                                <div style="color: #888;">Total Frameworks</div>
                            </div>
                            <div class="framework-grid">
                                ${(data.frameworks || []).map(f => `
                                    <div class="framework-item" style="cursor: pointer;" onclick="viewFramework('${f.id}')">
                                        <div style="font-size: 1.2em; margin-bottom: 5px;">${f.name}</div>
                                        <div style="font-size: 0.85em; color: #888;">${f.version}</div>
                                        <div style="font-size: 0.8em; color: #00d4ff; margin-top: 5px;">${f.clause_count} clauses</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                    document.getElementById('frameworks').innerHTML = html;
                }).catch(err => {
                    document.getElementById('frameworks').innerHTML = 
                        '<div class="loading">Error loading frameworks: ' + err.message + '</div>';
                });
        }
        
        function loadUpdates() {
            Promise.all([
                fetch('/api/regulations/updates').then(r => r.json()).catch(() => ({updates: [], count: 0})),
                fetch('/api/regulations/drift').then(r => r.json()).catch(() => ({drift_detected: false, frameworks: []}))
            ]).then(([updates, drift]) => {
                const pendingUpdates = updates.updates || [];
                const driftInfo = drift.frameworks || [];
                
                const html = `
                    <div class="metric-card">
                        <h3>🔄 Regulation Update Status</h3>
                        <div style="text-align: center; padding: 20px 0; margin-bottom: 20px;">
                            <div style="font-size: 2em; color: ${pendingUpdates.length > 0 ? '#ffc800' : '#00ff88'}; font-weight: bold;">
                                ${pendingUpdates.length}
                            </div>
                            <div style="color: #888;">Pending Update${pendingUpdates.length !== 1 ? 's' : ''}</div>
                        </div>
                        
                        <div style="margin-bottom: 20px; text-align: center;">
                            <button onclick="checkUpdates()" style="padding: 10px 20px; background: #00d4ff; color: #000; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-right: 10px;">
                                🔄 Check for Updates Now
                            </button>
                        </div>
                        
                        ${pendingUpdates.length === 0 ? 
                            '<div style="text-align: center; padding: 40px; color: #888;">No pending regulation updates. All regulations are up to date!</div>' :
                            pendingUpdates.map(update => `
                                <div class="component-bar" style="margin-bottom: 15px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 8px;">
                                    <div class="component-label" style="margin-bottom: 10px;">
                                        <span class="component-name" style="font-weight: bold; font-size: 1.1em;">${update.framework || 'Unknown'}</span>
                                        <span class="component-value">${update.new_version_tag || 'New Version'}</span>
                                    </div>
                                    <div style="font-size: 0.9em; color: #aaa; margin-bottom: 10px;">
                                        <div><strong>Old Version:</strong> ${update.old_version_tag || 'N/A'}</div>
                                        <div style="margin-top: 5px;"><strong>New Version:</strong> ${update.new_version_tag || 'N/A'}</div>
                                        <div style="margin-top: 5px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                                            ${update.diff_summary || 'Changes detected'}
                                        </div>
                                        <div style="margin-top: 10px; font-size: 0.85em; color: #888;">
                                            Created: ${new Date(update.created_at).toLocaleString()}
                                            ${update.reviewed_by ? `\\nReviewed by: ${update.reviewed_by} on ${new Date(update.reviewed_at).toLocaleString()}` : ''}
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                                        <button onclick="approveUpdate(${update.id})" style="flex: 1; padding: 10px 16px; background: #00ff88; color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.95em;">
                                            ✓ Approve & Activate
                                        </button>
                                        <button onclick="rejectUpdate(${update.id})" style="flex: 1; padding: 10px 16px; background: #ff6464; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.95em;">
                                            ✗ Reject
                                        </button>
                                    </div>
                                </div>
                            `).join('')
                        }
                    </div>
                    
                    ${driftInfo.length > 0 ? `
                        <div class="metric-card">
                            <h3>📊 Drift Summary by Framework</h3>
                            ${driftInfo.map(fw => `
                                <div class="component-bar">
                                    <div class="component-label">
                                        <span class="component-name">${fw.framework}</span>
                                        <span class="component-value">${fw.pending_changes} pending</span>
                                    </div>
                                    <div style="font-size: 0.85em; color: #888; margin-top: 5px;">
                                        Latest Version: ${fw.latest_version || 'Unknown'}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                `;
                document.getElementById('updates').innerHTML = html;
            }).catch(err => {
                document.getElementById('updates').innerHTML = 
                    '<div class="loading">Error loading updates: ' + err.message + '</div>';
            });
        }
        
        function checkUpdates() {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = 'Checking...';
            
            fetch('/api/regulations/check-updates', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert(`Update check complete!\\nFound ${data.count} new change(s).`);
                        loadUpdates(); // Reload updates
                    } else {
                        alert('Error: ' + (data.error || 'Failed to check for updates'));
                    }
                })
                .catch(err => {
                    alert('Error checking updates: ' + err.message);
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.textContent = '🔄 Check for Updates Now';
                });
        }
        
        function loadEvidence() {
            fetch('/api/evidence/list')
                .then(r => r.json())
                .then(data => {
                    const evidence = data.evidence || [];
                    const html = `
                        <div class="metric-card">
                            <h3>📁 Evidence Management</h3>
                            <div style="text-align: center; padding: 20px 0; margin-bottom: 20px;">
                                <div style="font-size: 2em; color: #00ff88; font-weight: bold;">
                                    ${evidence.length}
                                </div>
                                <div style="color: #888;">Total Evidence Files</div>
                            </div>
                            ${evidence.length === 0 ? 
                                '<div style="text-align: center; padding: 40px; color: #888;">No evidence files uploaded yet</div>' :
                                evidence.map(ev => `
                                    <div class="component-bar" style="cursor: pointer;">
                                        <div class="component-label">
                                            <span class="component-name">${ev.file_name || 'Unknown'}</span>
                                            <span class="component-value">${ev.framework}</span>
                                        </div>
                                        <div style="font-size: 0.85em; color: #888; margin-top: 5px;">
                                            Clause: ${ev.clause_id} | Uploaded: ${new Date(ev.timestamp).toLocaleDateString()}
                                        </div>
                                    </div>
                                `).join('')
                            }
                        </div>
                    `;
                    document.getElementById('evidence').innerHTML = html;
                }).catch(err => {
                    document.getElementById('evidence').innerHTML = 
                        '<div class="loading">Error loading evidence: ' + err.message + '</div>';
                });
        }
        
        function viewFramework(frameworkId) {
            fetch('/api/framework/' + frameworkId)
                .then(r => r.json())
                .then(data => {
                    alert('Framework: ' + data.name + '\\nVersion: ' + data.version + '\\nClauses: ' + data.clauses.length);
                });
        }
        
        function approveUpdate(changeId) {
            if (!confirm('Are you sure you want to approve this regulation update? This will activate the new version.')) {
                return;
            }
            
            fetch('/api/regulations/approve/' + changeId, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reviewed_by: 'admin'})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('Update approved successfully! The new version has been activated.');
                    loadOverview(); // Reload overview
                } else {
                    alert('Error: ' + (data.error || 'Failed to approve update'));
                }
            })
            .catch(err => {
                alert('Error approving update: ' + err.message);
            });
        }
        
        function rejectUpdate(changeId) {
            if (!confirm('Are you sure you want to reject this regulation update?')) {
                return;
            }
            
            fetch('/api/regulations/reject/' + changeId, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reviewed_by: 'admin'})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('Update rejected successfully.');
                    loadOverview(); // Reload overview
                } else {
                    alert('Error: ' + (data.error || 'Failed to reject update'));
                }
            })
            .catch(err => {
                alert('Error rejecting update: ' + err.message);
            });
        }
        
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
