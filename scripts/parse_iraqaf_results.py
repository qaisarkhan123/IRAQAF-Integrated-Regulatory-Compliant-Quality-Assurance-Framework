#!/usr/bin/env python
"""
Parse IRAQAF compliance results and generate markdown report.
"""

import argparse
import json
import glob
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class IRQAFParser:
    """Parse IRAQAF results and extract compliance data"""
    
    def __init__(self):
        self.frameworks_map = {
            'IRAQAF': {
                'SOX': {'IR-1': 'CC1.1', 'IR-2': 'CC1.2'},
                'ISO27001': {'IR-1': 'A.5.1', 'IR-2': 'A.5.2'},
                'CIS': {'IR-1': 'CIS 1.1', 'IR-2': 'CIS 1.2'}
            }
        }
        self.traces = []
        self.evidence = []
    
    def map_framework(self, source_framework: str, target_framework: str) -> Dict:
        """Map controls from source to target framework"""
        if source_framework not in self.frameworks_map:
            return {}
        
        return self.frameworks_map[source_framework].get(target_framework, {})
    
    def bidirectional_map(self, iraqaf_control: str) -> Dict:
        """Get mappings for an IRAQAF control to all supported frameworks"""
        mapping = {'iraqaf': iraqaf_control}
        
        if 'IRAQAF' in self.frameworks_map:
            for target_fw, controls in self.frameworks_map['IRAQAF'].items():
                for irq, target_ctrl in controls.items():
                    if irq == iraqaf_control:
                        mapping[target_fw] = target_ctrl
        
        return mapping
    
    def aggregate_traces(self, traces: List[Dict]) -> List[Dict]:
        """Aggregate multiple traces into grouped results"""
        aggregated = {}
        
        for trace in traces:
            control = trace.get('control', 'unknown')
            if control not in aggregated:
                aggregated[control] = {
                    'control': control,
                    'count': 0,
                    'passed': 0,
                    'failed': 0,
                    'results': []
                }
            
            aggregated[control]['count'] += 1
            result = trace.get('result', 'UNKNOWN').upper()
            if result == 'PASS':
                aggregated[control]['passed'] += 1
            elif result == 'FAIL':
                aggregated[control]['failed'] += 1
            
            aggregated[control]['results'].append(trace)
        
        return list(aggregated.values())
    
    def aggregate_by_framework(self, traces: List[Dict]) -> Dict[str, List]:
        """Group traces by framework"""
        grouped = {}
        
        for trace in traces:
            fw = trace.get('framework', 'UNKNOWN')
            if fw not in grouped:
                grouped[fw] = []
            grouped[fw].append(trace)
        
        return grouped
    
    def deduplicate_traces(self, traces: List[Dict]) -> List[Dict]:
        """Remove duplicate traces"""
        seen = set()
        unique = []
        
        for trace in traces:
            trace_hash = trace.get('hash', str(trace))
            if trace_hash not in seen:
                seen.add(trace_hash)
                unique.append(trace)
        
        return unique
    
    def extract_evidence(self, trace: Dict) -> Dict:
        """Extract evidence from a trace"""
        evidence = trace.get('evidence', {})
        return {
            'trace_id': trace.get('id'),
            'control': trace.get('control'),
            'evidence': evidence,
            'timestamp': trace.get('timestamp')
        }
    
    def classify_evidence(self, evidence: Dict) -> str:
        """Classify evidence type"""
        evidence_type = evidence.get('type', 'unknown')
        
        valid_types = ['log_entry', 'config', 'scan', 'policy', 'audit', 'documentation']
        return evidence_type if evidence_type in valid_types else 'unknown'
    
    def sanitize_evidence(self, evidence: Dict) -> Dict:
        """Remove PII from evidence"""
        sanitized = evidence.copy()
        
        # Remove common PII patterns
        sensitive_fields = ['email', 'username', 'password', 'api_key', 'secret']
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***REDACTED***'
        
        return sanitized
    
    def validate_evidence_chain(self, chain: List[Dict]) -> bool:
        """Validate integrity of evidence chain"""
        if not chain:
            return True
        
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]
            
            expected_hash = previous.get('hash')
            actual_prev_hash = current.get('previous_hash')
            
            if expected_hash != actual_prev_hash:
                return False
        
        return True
    
    def score_evidence_relevance(self, evidence: Dict) -> float:
        """Score relevance of evidence to control (0-1)"""
        content = str(evidence.get('content', '')).lower()
        control = str(evidence.get('control', '')).lower()
        
        # Simple relevance scoring
        if control in content:
            return 1.0
        elif any(word in content for word in control.split()):
            return 0.7
        else:
            return 0.3
    
    def normalize_result(self, result: str) -> str:
        """Normalize result state"""
        result_upper = str(result).upper()
        
        if result_upper in ['PASS', 'TRUE', 'YES', '1']:
            return 'PASS'
        elif result_upper in ['FAIL', 'FALSE', 'NO', '0']:
            return 'FAIL'
        else:
            return 'INCONCLUSIVE'
    
    def normalize_severity(self, severity: str) -> str:
        """Normalize severity level"""
        sev_upper = str(severity).upper()
        
        if sev_upper in ['CRITICAL', 'CRIT']:
            return 'CRITICAL'
        elif sev_upper in ['HIGH', 'H']:
            return 'HIGH'
        elif sev_upper in ['MEDIUM', 'MED', 'M']:
            return 'MEDIUM'
        elif sev_upper in ['LOW', 'L']:
            return 'LOW'
        else:
            return 'UNKNOWN'
    
    def normalize_timestamp(self, timestamp) -> Optional[str]:
        """Normalize timestamp format"""
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp).isoformat()
            elif isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp).isoformat()
            else:
                return str(timestamp)
        except:
            return None
    
    def normalize_control_reference(self, reference: str) -> str:
        """Normalize control reference format"""
        return reference.upper().replace('_', '-').replace(' ', '')
    
    def normalize_to_schema(self, result: Dict) -> Dict:
        """Normalize to canonical result schema"""
        normalized = {
            'id': result.get('test_id', result.get('id', 'unknown')),
            'control': result.get('control', 'unknown'),
            'result': self.normalize_result(result.get('status', result.get('result'))),
            'severity': self.normalize_severity(result.get('severity', 'UNKNOWN')),
            'evidence': result.get('evidence', {}),
            'timestamp': self.normalize_timestamp(result.get('timestamp'))
        }
        
        return normalized
    
    def parse_iraqaf_xml(self, xml_data: str) -> Optional[List]:
        """Parse IRAQAF XML format"""
        try:
            root = ET.fromstring(xml_data)
            results = []
            
            for control_elem in root.findall('.//control'):
                result = {
                    'id': control_elem.get('id'),
                    'result': control_elem.findtext('result', 'UNKNOWN')
                }
                results.append(result)
            
            return results
        except:
            return None
    
    def parse_iraqaf_json(self, json_data: Dict) -> Optional[List]:
        """Parse IRAQAF JSON format"""
        try:
            return json_data.get('controls', [])
        except:
            return None
    
    def aggregate_results_by_control(self, results: List[Dict]) -> Dict:
        """Aggregate results grouped by control"""
        aggregated = {}
        
        for result in results:
            control = result.get('control', 'unknown')
            if control not in aggregated:
                aggregated[control] = {'total': 0, 'passed': 0, 'failed': 0}
            
            aggregated[control]['total'] += 1
            if result.get('result') == 'PASS':
                aggregated[control]['passed'] += 1
            else:
                aggregated[control]['failed'] += 1
        
        return aggregated
    
    def calculate_compliance_score(self, results: Dict) -> float:
        """Calculate overall compliance percentage"""
        total = results.get('total_controls', 1)
        passed = results.get('passed', 0)
        
        if total == 0:
            return 0.0
        
        return (passed / total) * 100
    
    def generate_result_summary(self, results: List[Dict]) -> str:
        """Generate summary of results"""
        passed = sum(1 for r in results if r.get('result') == 'PASS')
        failed = len(results) - passed
        
        summary = f"Results Summary: {passed} passed, {failed} failed out of {len(results)}"
        return summary
    
    def export_to_csv(self, results: List[Dict]) -> str:
        """Export results to CSV"""
        if not results:
            return ""
        
        csv_data = []
        csv_data.append("Control,Result,Severity,Timestamp\n")
        
        for result in results:
            row = f"{result.get('control', 'unknown')},{result.get('result', 'unknown')},{result.get('severity', 'unknown')},{result.get('timestamp', '')}\n"
            csv_data.append(row)
        
        return ''.join(csv_data)
    
    def export_to_json(self, results: List[Dict]) -> str:
        """Export results to JSON"""
        return json.dumps(results, indent=2)

def parse_results(compliance_json_files, threshold=75):
    """
    Parse IRAQAF JSON results and extract key information.
    
    Args:
        compliance_json_files: List of JSON file paths or glob pattern
        threshold: Minimum score threshold
        
    Returns:
        dict: Parsed results
    """
    # Handle glob pattern
    if isinstance(compliance_json_files, str) and '*' in compliance_json_files:
        files = glob.glob(compliance_json_files)
    else:
        files = compliance_json_files if isinstance(compliance_json_files, list) else [compliance_json_files]
    
    if not files:
        raise FileNotFoundError(f"No compliance reports found: {compliance_json_files}")
    
    # Use the most recent file
    latest_file = max(files, key=lambda f: Path(f).stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data, threshold

def generate_markdown_report(results, threshold, output_file):
    """
    Generate a markdown compliance report.
    
    Args:
        results: IRAQAF results dict
        threshold: Score threshold
        output_file: Output markdown file path
    """
    report = []
    report.append("# 🔍 IRAQAF Compliance Assessment Report\n")
    
    # Timestamp
    timestamp = results.get("metadata", {}).get("timestamp", datetime.utcnow().isoformat())
    report.append(f"**Generated:** {timestamp}\n")
    
    # Overall Status
    gqas = results.get("gqas", 0)
    if gqas >= threshold:
        status = "✅ **PASSED**"
        color = "green"
    elif gqas >= 50:
        status = "⚠️ **WARNING**"
        color = "orange"
    else:
        status = "❌ **FAILED**"
        color = "red"
    
    report.append(f"## Overall Status: {status}\n")
    report.append(f"**Global Quality Score:** {gqas:.1f}/100 (Threshold: {threshold})\n")
    
    # Module Breakdown
    report.append("## 📊 Module Scores\n")
    report.append("| Module | Score | Status | Issues |\n")
    report.append("|--------|-------|--------|--------|\n")
    
    modules = results.get("modules", {})
    for module_name, module_data in modules.items():
        score = module_data.get("score", 0)
        module_status = "✅ Pass" if score >= threshold else "⚠️ Warning" if score >= 50 else "❌ Fail"
        issues_count = len(module_data.get("issues", []))
        report.append(f"| {module_name} | {score:.1f} | {module_status} | {issues_count} |\n")
    
    report.append("\n")
    
    # Risk Profile
    if "risk_profile" in results:
        report.append(f"## 🎯 Risk Profile\n")
        report.append(f"**Classification:** {results['risk_profile']}\n")
        report.append(f"**Recommended Actions:** {results.get('recommended_actions', 'None')}\n\n")
    
    # Top Issues
    all_issues = []
    for module_data in modules.values():
        all_issues.extend(module_data.get("issues", []))
    
    if all_issues:
        report.append("## ⚠️ Top Issues\n")
        for i, issue in enumerate(sorted(all_issues, key=lambda x: x.get("severity", 0), reverse=True)[:10], 1):
            severity = issue.get("severity", "medium").upper()
            report.append(f"{i}. **[{severity}]** {issue.get('message', 'Unknown issue')}\n")
        report.append("\n")
    
    # Recommendations
    report.append("## 💡 Recommendations\n")
    if gqas < threshold:
        report.append(f"- Score is below threshold ({gqas:.1f} < {threshold})\n")
        for module_name, module_data in modules.items():
            if module_data.get("score", 0) < threshold:
                report.append(f"- Focus on improving **{module_name}** module\n")
    else:
        report.append("- ✅ All modules meet compliance threshold\n")
        report.append("- Continue monitoring for regressions\n")
    
    # Metadata
    report.append("\n## 📋 Metadata\n")
    metadata = results.get("metadata", {})
    report.append(f"- **Branch:** {metadata.get('branch', 'unknown')}\n")
    report.append(f"- **Commit:** {metadata.get('commit', 'unknown')[:7]}\n")
    report.append(f"- **Pipeline:** {metadata.get('pipeline', 'unknown')}\n")
    
    # Write report
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    print(f"✅ Markdown report generated: {output_path}")
    return ''.join(report)

# Module-level wrapper functions for test compatibility
_iraqaf_parser_instance = None

def parse_iraqaf_results(data: Dict) -> Dict:
    """Parse IRAQAF results from dictionary"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.normalize_to_schema(data)

def aggregate_iraqaf_traces(traces: List[Dict]) -> Dict:
    """Aggregate IRAQAF traces"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.aggregate_traces(traces)

def extract_iraqaf_evidence(trace: Dict) -> List[Dict]:
    """Extract evidence from IRAQAF trace"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.extract_evidence(trace)

def normalize_iraqaf_result(result: Dict) -> Dict:
    """Normalize IRAQAF result"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.normalize_result(result)

def map_iraqaf_framework(framework: str) -> List[str]:
    """Map IRAQAF framework to other frameworks"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.map_framework(framework)

def export_iraqaf_to_csv(results: List[Dict]) -> str:
    """Export IRAQAF results to CSV"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.export_to_csv(results)

def export_iraqaf_to_json(results: List[Dict]) -> str:
    """Export IRAQAF results to JSON"""
    global _iraqaf_parser_instance
    if _iraqaf_parser_instance is None:
        _iraqaf_parser_instance = IRQAFParser()
    return _iraqaf_parser_instance.export_to_json(results)

def main():
    parser = argparse.ArgumentParser(description="Parse IRAQAF compliance results")
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="IRAQAF JSON results file or glob pattern"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=75,
        help="Compliance score threshold"
    )
    parser.add_argument(
        "--output", "-o",
        default="compliance_report.md",
        help="Output markdown file"
    )
    
    args = parser.parse_args()
    
    # Parse results
    results, threshold = parse_results(args.input, args.threshold)
    
    # Generate report
    generate_markdown_report(results, threshold, args.output)

if __name__ == "__main__":
    main()
