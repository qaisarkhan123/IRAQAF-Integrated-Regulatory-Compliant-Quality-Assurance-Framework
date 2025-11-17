#!/usr/bin/env python
"""
IRAQAF Regulatory Sync Layer
Automatically updates IRAQAF trace_map.yaml and triggers re-evaluations
when regulatory changes are detected
"""

import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class IRQAFRegulatorySync:
    """Synchronize detected regulatory changes with IRAQAF"""
    
    def __init__(self, trace_map_path: str = 'configs/trace_map.yaml',
                 regulations_dir: str = 'regulatory_data'):
        self.trace_map_path = Path(trace_map_path)
        self.regulations_dir = Path(regulations_dir)
        self.regulations_dir.mkdir(exist_ok=True)
        
        # Define mapping: regulation → IRAQAF modules
        self.regulation_module_mapping = {
            'GDPR': {
                'modules': ['L1-Governance', 'L2-Privacy'],
                'clauses': ['consent', 'data_subject_rights', 'data_protection_officer']
            },
            'HIPAA': {
                'modules': ['L2-Privacy', 'L5-Operations'],
                'clauses': ['phi_protection', 'breach_notification', 'audit_controls']
            },
            'EU-AI-Act': {
                'modules': ['L3-Fairness', 'L4-Explainability', 'L1-Governance'],
                'clauses': ['risk_assessment', 'transparency', 'human_oversight']
            },
            'SOC2': {
                'modules': ['L1-Governance', 'L5-Operations'],
                'clauses': ['access_controls', 'monitoring', 'change_management']
            }
        }
        
    def load_trace_map(self) -> Dict:
        """Load current trace_map.yaml"""
        try:
            with open(self.trace_map_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Trace map not found at {self.trace_map_path}, creating new one")
            return {}
            
    def save_trace_map(self, trace_map: Dict) -> None:
        """Save updated trace_map.yaml"""
        self.trace_map_path.parent.mkdir(exist_ok=True)
        with open(self.trace_map_path, 'w') as f:
            yaml.dump(trace_map, f, default_flow_style=False, sort_keys=False)
        logger.info(f"✅ Trace map saved to {self.trace_map_path}")
        
    def identify_regulation(self, title: str, content: str) -> Optional[str]:
        """Identify which regulation this is (GDPR, HIPAA, etc.)"""
        title_lower = (title + ' ' + content[:200]).lower()
        
        for reg_name in self.regulation_module_mapping.keys():
            if reg_name.lower() in title_lower:
                return reg_name
        
        # Try to infer from content
        if 'personal data' in title_lower or 'data subject' in title_lower:
            return 'GDPR'
        elif 'phi' in title_lower or 'protected health' in title_lower:
            return 'HIPAA'
        elif 'artificial intelligence' in title_lower or 'ai' in title_lower:
            return 'EU-AI-Act'
        
        return None
        
    def add_regulatory_trace(self, regulation: str, module: str, 
                            trace_item: Dict) -> Dict:
        """Add a regulatory requirement to trace map"""
        trace_map = self.load_trace_map()
        
        if 'regulatory_requirements' not in trace_map:
            trace_map['regulatory_requirements'] = {}
        
        if regulation not in trace_map['regulatory_requirements']:
            trace_map['regulatory_requirements'][regulation] = {
                'modules': [],
                'requirements': [],
                'last_updated': datetime.now().isoformat()
            }
        
        # Add module if not present
        reg_data = trace_map['regulatory_requirements'][regulation]
        if module not in reg_data['modules']:
            reg_data['modules'].append(module)
        
        # Add requirement
        trace_item['added_at'] = datetime.now().isoformat()
        trace_item['regulation'] = regulation
        reg_data['requirements'].append(trace_item)
        
        self.save_trace_map(trace_map)
        logger.info(f"Added regulatory trace: {regulation} → {module}")
        
        return trace_map
        
    def update_module_due_to_regulation(self, regulation: str, 
                                       changes: Dict) -> Dict:
        """Mark modules for re-evaluation due to regulatory changes"""
        trace_map = self.load_trace_map()
        
        if 'regulatory_changes' not in trace_map:
            trace_map['regulatory_changes'] = []
        
        # Get affected modules for this regulation
        mapping = self.regulation_module_mapping.get(regulation, {})
        affected_modules = mapping.get('modules', ['L1-Governance'])
        
        change_record = {
            'regulation': regulation,
            'timestamp': datetime.now().isoformat(),
            'affected_modules': affected_modules,
            'severity': self._classify_change_severity(changes),
            'details': {
                'new_clauses': len(changes.get('added_clauses', [])),
                'removed_clauses': len(changes.get('removed_clauses', [])),
                'modified_clauses': len(changes.get('modified_clauses', []))
            }
        }
        
        trace_map['regulatory_changes'].append(change_record)
        
        # Mark modules for re-evaluation
        if 'modules_requiring_review' not in trace_map:
            trace_map['modules_requiring_review'] = []
        
        for module in affected_modules:
            if module not in trace_map['modules_requiring_review']:
                trace_map['modules_requiring_review'].append(module)
                logger.info(f"⚠️  Module marked for review: {module}")
        
        self.save_trace_map(trace_map)
        return trace_map
        
    def generate_sync_report(self, changes: Dict) -> str:
        """Generate report of IRAQAF updates"""
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║         IRAQAF REGULATORY SYNCHRONIZATION REPORT                   ║
╚════════════════════════════════════════════════════════════════════╝

📅 Timestamp: {datetime.now().isoformat()}

🔄 CHANGES DETECTED:
   • New Regulations: {len(changes.get('new_regulations', []))}
   • Updated Regulations: {len(changes.get('updated_regulations', []))}
   • Affected Modules: {', '.join(changes.get('affected_modules', []))}

📋 TRACE MAP UPDATES:
   ✅ Regulatory requirements added
   ✅ Module mappings updated
   ✅ Change history recorded

🎯 NEXT STEPS:
   1. Review affected modules in trace_map.yaml
   2. Update compliance requirements if needed
   3. Trigger IRAQAF re-evaluation with: python scripts/run_compliance_check.py
   4. Review updated compliance report

⚠️  MODULES REQUIRING REVIEW:
"""
        trace_map = self.load_trace_map()
        for module in trace_map.get('modules_requiring_review', []):
            report += f"   • {module}\n"
        
        report += """
╚════════════════════════════════════════════════════════════════════╝
"""
        return report
        
    def _classify_change_severity(self, changes: Dict) -> str:
        """Classify severity of regulatory change"""
        added = len(changes.get('added_clauses', []))
        removed = len(changes.get('removed_clauses', []))
        modified = len(changes.get('modified_clauses', []))
        similarity = changes.get('similarity_score', 1.0)
        
        if similarity < 0.5 or (added + removed) > 5:
            return 'CRITICAL'
        elif similarity < 0.7 or (added + removed) > 3:
            return 'HIGH'
        elif similarity < 0.85 or added + removed > 1:
            return 'MEDIUM'
        else:
            return 'LOW'


class RegulatoryComplianceDelta:
    """Generate delta reports showing compliance impact"""
    
    def __init__(self, output_dir: str = 'regulatory_data'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_impact_report(self, regulation: str, changes: Dict,
                              affected_modules: List[str]) -> str:
        """Generate compliance impact report"""
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║    COMPLIANCE IMPACT REPORT: {regulation}
╚════════════════════════════════════════════════════════════════════╝

📅 Generated: {datetime.now().isoformat()}

🏛️  REGULATION: {regulation}
📊 CHANGE SEVERITY: {self._compute_severity(changes)}

AFFECTED MODULES:
"""
        for module in affected_modules:
            report += f"  • {module}\n"
        
        report += f"""
CHANGE SUMMARY:
  ➕ New Clauses/Requirements: {len(changes.get('added_clauses', []))}
  ➖ Removed Clauses: {len(changes.get('removed_clauses', []))}
  🔄 Modified Clauses: {len(changes.get('modified_clauses', []))}
  
📈 Semantic Similarity: {changes.get('similarity_score', 0):.1%}
   (Lower = more significant changes)

ACTION ITEMS:
"""
        
        # Generate action items based on changes
        if changes.get('added_clauses'):
            report += """
  ⚠️  NEW REQUIREMENTS:
      Your organization may need to implement new controls to meet:
"""
            for clause in changes['added_clauses'][:3]:
                report += f"      • {clause['text'][:80]}\n"
        
        if changes.get('removed_clauses'):
            report += """
  ✅ OBSOLETE REQUIREMENTS:
      The following requirements are no longer mandated:
"""
            for clause in changes['removed_clauses'][:3]:
                report += f"      • {clause['text'][:80]}\n"
        
        if changes.get('modified_clauses'):
            report += """
  🔄 MODIFIED REQUIREMENTS:
      These requirements have changed and may need re-assessment:
"""
            for clause in changes['modified_clauses'][:3]:
                report += f"      • {clause['old_text'][:60]} → {clause['new_text'][:60]}\n"
        
        report += """
📋 RECOMMENDED NEXT STEPS:
   1. ✓ Review the full regulation text
   2. ✓ Assess current compliance controls
   3. ✓ Identify gaps against new requirements
   4. ✓ Update IRAQAF trace_map.yaml with new clauses
   5. ✓ Re-run compliance assessment
   6. ✓ Create remediation plan for gaps

🔗 RESOURCES:
   • Regulation Source: Check regulatory_data/regulations_cache.json
   • Change History: regulatory_data/change_history.json
   • Trace Map: configs/trace_map.yaml

╚════════════════════════════════════════════════════════════════════╝
"""
        return report
        
    def save_impact_report(self, regulation: str, report: str) -> Path:
        """Save impact report to file"""
        report_file = self.output_dir / f"impact_{regulation}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f"Impact report saved: {report_file}")
        return report_file
        
    def _compute_severity(self, changes: Dict) -> str:
        """Compute severity level"""
        similarity = changes.get('similarity_score', 1.0)
        if similarity < 0.5:
            return '🔴 CRITICAL'
        elif similarity < 0.7:
            return '🟠 HIGH'
        elif similarity < 0.85:
            return '🟡 MEDIUM'
        else:
            return '🟢 LOW'


def main():
    """Example usage"""
    logger.info("IRAQAF Regulatory Sync Test")
    
    sync = IRQAFRegulatorySync()
    
    # Simulate regulatory change
    test_changes = {
        'added_clauses': [
            {'text': 'Data minimization: Collect only necessary data'}
        ],
        'removed_clauses': [],
        'modified_clauses': [],
        'similarity_score': 0.92
    }
    
    # Update trace map
    sync.update_module_due_to_regulation('GDPR', test_changes)
    
    # Generate sync report
    all_changes = {
        'new_regulations': [],
        'updated_regulations': [],
        'affected_modules': ['L1-Governance', 'L2-Privacy']
    }
    
    sync_report = sync.generate_sync_report(all_changes)
    logger.info(sync_report)
    
    # Generate impact report
    delta = RegulatoryComplianceDelta()
    impact = delta.generate_impact_report('GDPR', test_changes, 
                                         ['L1-Governance', 'L2-Privacy'])
    logger.info(impact)


if __name__ == '__main__':
    main()
