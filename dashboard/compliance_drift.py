"""
Compliance Drift Monitoring
Tracks changes in regulations, evidence, documentation, and models.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

class ComplianceDriftMonitor:
    def __init__(self, history_file: Optional[str] = None, update_service=None):
        """Initialize the compliance drift monitor."""
        if history_file is None:
            history_file = Path(__file__).parent / "evidence" / "compliance_history.json"
        
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()
        self.update_service = update_service  # RegulationUpdateService instance
    
    def _load_history(self) -> Dict:
        """Load compliance history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_history(self):
        """Save compliance history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save compliance history: {e}")
    
    def record_snapshot(self, snapshot_type: str, snapshot_data: Dict):
        """Record a compliance snapshot."""
        timestamp = datetime.now().isoformat()
        
        if snapshot_type not in self.history:
            self.history[snapshot_type] = []
        
        self.history[snapshot_type].append({
            "timestamp": timestamp,
            "data": snapshot_data
        })
        
        # Keep only last 100 snapshots per type
        if len(self.history[snapshot_type]) > 100:
            self.history[snapshot_type] = self.history[snapshot_type][-100:]
        
        self._save_history()
    
    def detect_drift(self, current_state: Dict) -> Dict:
        """
        Detect compliance drift by comparing current state with history.
        
        Args:
            current_state: Current compliance state with keys:
                - regulations: Current regulation compliance
                - evidence: Current evidence status
                - documentation: Current documentation versions
                - model_version: Current model version
                - sdlc_changes: Recent SDLC changes
        
        Returns:
            Drift detection results
        """
        drift_detected = False
        drift_areas = {}
        
        # Check regulation changes (from update service if available)
        reg_drift = self._check_regulation_changes()
        if reg_drift["drift_detected"]:
            drift_detected = True
            drift_areas["regulations"] = reg_drift
        
        # Also check regulation score drift
        reg_score_drift = self._check_regulation_drift(current_state.get("regulations", {}))
        if reg_score_drift["drift_detected"]:
            drift_detected = True
            drift_areas["regulation_scores"] = reg_score_drift
        
        # Check evidence freshness
        evidence_drift = self._check_evidence_drift(current_state.get("evidence", {}))
        if evidence_drift["drift_detected"]:
            drift_detected = True
            drift_areas["evidence"] = evidence_drift
        
        # Check documentation versions
        doc_drift = self._check_documentation_drift(current_state.get("documentation", {}))
        if doc_drift["drift_detected"]:
            drift_detected = True
            drift_areas["documentation"] = doc_drift
        
        # Check model version changes
        model_drift = self._check_model_drift(current_state.get("model_version", None))
        if model_drift["drift_detected"]:
            drift_detected = True
            drift_areas["model_version"] = model_drift
        
        # Check SDLC changes
        sdlc_drift = self._check_sdlc_drift(current_state.get("sdlc_changes", []))
        if sdlc_drift["drift_detected"]:
            drift_detected = True
            drift_areas["sdlc"] = sdlc_drift
        
        return {
            "drift_detected": drift_detected,
            "timestamp": datetime.now().isoformat(),
            "areas": drift_areas,
            "severity": self._calculate_severity(drift_areas)
        }
    
    def _check_regulation_changes(self) -> Dict:
        """Check for pending regulation changes from the update service."""
        if not self.update_service:
            return {"drift_detected": False, "message": "Update service not available"}
        
        try:
            pending_updates = self.update_service.get_pending_updates()
            
            if len(pending_updates) == 0:
                return {"drift_detected": False, "message": "No pending regulation changes"}
            
            # Group by framework
            frameworks = {}
            for update in pending_updates:
                framework = update['framework']
                if framework not in frameworks:
                    frameworks[framework] = {
                        "framework": framework,
                        "pending_changes": 0,
                        "latest_version": update.get('new_version_tag', 'unknown')
                    }
                frameworks[framework]["pending_changes"] += 1
            
            return {
                "drift_detected": True,
                "message": f"{len(pending_updates)} pending regulation change(s) requiring review",
                "pending_count": len(pending_updates),
                "frameworks": list(frameworks.values())
            }
        except Exception as e:
            return {
                "drift_detected": False,
                "message": f"Error checking regulation changes: {e}",
                "error": str(e)
            }
    
    def _check_regulation_drift(self, current_regulations: Dict) -> Dict:
        """Check for changes in regulatory requirements."""
        last_reg_snapshot = self._get_last_snapshot("regulations")
        
        if not last_reg_snapshot:
            return {"drift_detected": False, "message": "No baseline for comparison"}
        
        last_data = last_reg_snapshot.get("data", {})
        
        # Compare framework compliance scores
        changes = []
        for framework, current_score in current_regulations.items():
            last_score = last_data.get(framework, {}).get("score", 0)
            if abs(current_score - last_score) > 5:  # 5% threshold
                changes.append({
                    "framework": framework,
                    "previous_score": last_score,
                    "current_score": current_score,
                    "change": current_score - last_score
                })
        
        drift_detected = len(changes) > 0
        
        return {
            "drift_detected": drift_detected,
            "changes": changes,
            "message": f"{len(changes)} framework(s) with significant score changes" if drift_detected else "No significant regulation changes"
        }
    
    def _check_evidence_drift(self, current_evidence: Dict) -> Dict:
        """Check for stale or missing evidence."""
        last_evidence_snapshot = self._get_last_snapshot("evidence")
        
        if not last_evidence_snapshot:
            return {"drift_detected": False, "message": "No baseline for comparison"}
        
        last_data = last_evidence_snapshot.get("data", {})
        last_timestamp = datetime.fromisoformat(last_evidence_snapshot["timestamp"])
        
        # Check for stale evidence (older than 90 days)
        stale_evidence = []
        missing_evidence = []
        
        for clause_id, evidence_info in current_evidence.items():
            evidence_age = evidence_info.get("age_days", 0)
            if evidence_age > 90:
                stale_evidence.append({
                    "clause_id": clause_id,
                    "age_days": evidence_age
                })
            
            # Check if evidence was present before but is now missing
            if clause_id in last_data and clause_id not in current_evidence:
                missing_evidence.append(clause_id)
        
        drift_detected = len(stale_evidence) > 0 or len(missing_evidence) > 0
        
        return {
            "drift_detected": drift_detected,
            "stale_evidence": stale_evidence,
            "missing_evidence": missing_evidence,
            "message": f"{len(stale_evidence)} stale, {len(missing_evidence)} missing evidence items" if drift_detected else "Evidence is current"
        }
    
    def _check_documentation_drift(self, current_docs: Dict) -> Dict:
        """Check for documentation version changes."""
        last_doc_snapshot = self._get_last_snapshot("documentation")
        
        if not last_doc_snapshot:
            return {"drift_detected": False, "message": "No baseline for comparison"}
        
        last_data = last_doc_snapshot.get("data", {})
        
        version_changes = []
        for doc_name, current_version in current_docs.items():
            last_version = last_data.get(doc_name, {}).get("version", "unknown")
            if current_version != last_version:
                version_changes.append({
                    "document": doc_name,
                    "previous_version": last_version,
                    "current_version": current_version
                })
        
        drift_detected = len(version_changes) > 0
        
        return {
            "drift_detected": drift_detected,
            "version_changes": version_changes,
            "message": f"{len(version_changes)} document(s) updated" if drift_detected else "No documentation changes"
        }
    
    def _check_model_drift(self, current_model_version: Optional[str]) -> Dict:
        """Check for model version changes."""
        last_model_snapshot = self._get_last_snapshot("model_version")
        
        if not last_model_snapshot:
            return {"drift_detected": False, "message": "No baseline for comparison"}
        
        last_version = last_model_snapshot.get("data", {}).get("version", None)
        
        drift_detected = current_model_version != last_version
        
        return {
            "drift_detected": drift_detected,
            "previous_version": last_version,
            "current_version": current_model_version,
            "message": f"Model updated from {last_version} to {current_model_version}" if drift_detected else "No model version change"
        }
    
    def _check_sdlc_drift(self, sdlc_changes: List[Dict]) -> Dict:
        """Check for SDLC process changes."""
        if not sdlc_changes:
            return {"drift_detected": False, "message": "No SDLC changes"}
        
        return {
            "drift_detected": True,
            "changes": sdlc_changes,
            "message": f"{len(sdlc_changes)} SDLC change(s) detected"
        }
    
    def _get_last_snapshot(self, snapshot_type: str) -> Optional[Dict]:
        """Get the most recent snapshot of a given type."""
        snapshots = self.history.get(snapshot_type, [])
        if not snapshots:
            return None
        
        return max(snapshots, key=lambda x: x["timestamp"])
    
    def _calculate_severity(self, drift_areas: Dict) -> str:
        """Calculate overall drift severity."""
        if not drift_areas:
            return "none"
        
        critical_count = 0
        high_count = 0
        
        for area, drift_info in drift_areas.items():
            if area in ["regulations", "regulation_changes"] and drift_info.get("drift_detected"):
                critical_count += 1
            elif area == "evidence" and len(drift_info.get("missing_evidence", [])) > 0:
                critical_count += 1
            elif drift_info.get("drift_detected"):
                high_count += 1
        
        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"

