#!/usr/bin/env python
"""
Run IRAQAF quality assessment on the codebase.
Generates compliance report for CI/CD pipeline integration.
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

def run_iraqaf_assessment(framework_patterns=None):
    """
    Run IRAQAF assessment on the codebase.
    
    Args:
        framework_patterns: Dict of framework names to file patterns
        
    Returns:
        dict: IRAQAF assessment results
    """
    # Import IRAQAF if available
    try:
        from core.engine import IRAQAF
    except ImportError:
        print("⚠️  IRAQAF not installed. Installing from local core...")
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.engine import IRAQAF
    
    # Default patterns if not provided
    if not framework_patterns:
        framework_patterns = {
            "L1_Governance": ["*.py", "*.yml", "*.yaml"],
            "L2_Privacy": ["**/*.py"],
            "L3_Fairness": ["**/*.py"],
            "L4_Explainability": ["**/*.py"],
            "L5_Operations": ["**/*.py", "*.txt", "*.md"]
        }
    
    print("🔍 Starting IRAQAF Compliance Assessment...")
    
    try:
        iraqaf = IRAQAF()
        results = iraqaf.assess()
        
        # Add metadata
        results["metadata"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline": "github-actions",
            "branch": os.getenv("GITHUB_REF", "unknown"),
            "commit": os.getenv("GITHUB_SHA", "unknown"),
            "actor": os.getenv("GITHUB_ACTOR", "unknown")
        }
        
        return results
    except Exception as e:
        print(f"❌ Error running IRAQAF: {e}")
        return {
            "status": "error",
            "error": str(e),
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline": "github-actions"
            }
        }

def save_results(results, output_path):
    """Save IRAQAF results to file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ Results saved to {output_path}")

def generate_summary(results):
    """Generate and print summary of results."""
    print("\n" + "="*60)
    print("IRAQAF COMPLIANCE ASSESSMENT SUMMARY")
    print("="*60)
    
    if "error" in results:
        print(f"❌ Assessment failed: {results['error']}")
        return False
    
    # Print module scores
    if "modules" in results:
        print("\n📊 Module Scores:")
        for module_name, module_data in results["modules"].items():
            score = module_data.get("score", 0)
            status = "✅" if score >= 75 else "⚠️ " if score >= 50 else "❌"
            print(f"  {status} {module_name}: {score:.1f}/100")
    
    # Print overall score
    if "gqas" in results:
        gqas = results["gqas"]
        status = "✅" if gqas >= 75 else "⚠️ " if gqas >= 50 else "❌"
        print(f"\n📈 Global Quality Score: {status} {gqas:.1f}/100")
    
    # Print issues
    if "issues" in results and results["issues"]:
        print(f"\n⚠️  Issues Found: {len(results['issues'])}")
        for issue in results["issues"][:5]:  # Show first 5
            print(f"   - {issue.get('type', 'Unknown')}: {issue.get('message', '')}")
    
    print("="*60 + "\n")
    
    return results.get("gqas", 0) >= 50

def main():
    parser = argparse.ArgumentParser(
        description="Run IRAQAF compliance assessment"
    )
    parser.add_argument(
        "--output", "-o",
        default="reports/compliance_assessment.json",
        help="Output file for IRAQAF results"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "yaml"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Run assessment
    results = run_iraqaf_assessment()
    
    # Save results
    save_results(results, args.output)
    
    # Generate summary
    success = generate_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
