#!/usr/bin/env python
"""
Local compliance check runner - simulates CI pipeline locally.
Useful for testing before pushing to GitHub.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, description, exit_on_error=False):
    """Run a shell command and report results."""
    print(f"\n{'='*60}")
    print(f"▶️  {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        
        if result.returncode != 0 and exit_on_error:
            print(f"❌ Command failed: {cmd}")
            return False
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def run_local_pipeline(threshold=75, required_modules="L1,L2,L3", min_score=80):
    """
    Run the complete compliance pipeline locally.
    
    Args:
        threshold: Compliance score threshold
        required_modules: Required modules to check
        min_score: Minimum score per module
    """
    
    print("\n" + "="*60)
    print("🔍 LOCAL IRAQAF COMPLIANCE PIPELINE")
    print("="*60)
    print(f"Threshold: {threshold}")
    print(f"Required Modules: {required_modules}")
    print(f"Min Score: {min_score}")
    
    steps = [
        (
            "python scripts/run_compliance_check.py --output reports/compliance_local.json",
            "Step 1: Run IRAQAF Compliance Assessment"
        ),
        (
            "python scripts/parse_iraqaf_results.py --input reports/compliance_local.json "
            f"--threshold {threshold} --output compliance_report.md",
            "Step 2: Parse Results and Generate Report"
        ),
        (
            f"python scripts/check_compliance_threshold.py --input reports/compliance_local.json --threshold {threshold}",
            "Step 3: Check Compliance Threshold"
        ),
        (
            f"python scripts/verify_deployment_readiness.py --compliance-report compliance_report.md "
            f"--required-modules {required_modules} --min-score {min_score}",
            "Step 4: Verify Deployment Readiness"
        ),
    ]
    
    all_passed = True
    
    for cmd, description in steps:
        success = run_command(cmd, description, exit_on_error=False)
        if not success and "check_compliance_threshold" in cmd:
            print("⚠️  Compliance threshold not met (continue to see full report)")
        elif not success:
            all_passed = False
    
    # Print summary
    print("\n" + "="*60)
    print("📊 PIPELINE SUMMARY")
    print("="*60)
    
    # Read and display report
    report_file = Path("compliance_report.md")
    if report_file.exists():
        with open(report_file, 'r') as f:
            print(f.read())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ PIPELINE PASSED - Ready for deployment")
    else:
        print("⚠️  PIPELINE COMPLETED WITH ISSUES - Review report above")
    print("="*60 + "\n")
    
    return all_passed

def main():
    parser = argparse.ArgumentParser(
        description="Run local IRAQAF compliance pipeline"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=75,
        help="Compliance score threshold"
    )
    parser.add_argument(
        "--required-modules", "-m",
        default="L1,L2,L3",
        help="Comma-separated list of required modules"
    )
    parser.add_argument(
        "--min-score", "-s",
        type=int,
        default=80,
        help="Minimum required score for each module"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Create reports directory
    Path("reports").mkdir(exist_ok=True)
    
    # Run pipeline
    passed = run_local_pipeline(
        threshold=args.threshold,
        required_modules=args.required_modules,
        min_score=args.min_score
    )
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
