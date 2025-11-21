#!/usr/bin/env python3
"""Test hub imports to identify startup issues"""

import sys
import os
sys.path.append('dashboard')

def test_import(module_name, description):
    try:
        __import__(module_name)
        print(f"✓ {description} imports successfully")
        return True
    except Exception as e:
        print(f"✗ {description} import error: {e}")
        return False

if __name__ == "__main__":
    print("Testing IRAQAF Hub Imports...")
    print("=" * 40)
    
    success_count = 0
    
    if test_import('l3_fairness_ethics_hub', 'L3 Fairness & Ethics Hub'):
        success_count += 1
    
    if test_import('privacy_security_hub', 'L2 Privacy & Security Hub'):
        success_count += 1
    
    if test_import('hub_explainability_app', 'L4 Explainability Hub'):
        success_count += 1
    
    if test_import('l3_operations_control_center', 'SOQM Operations Hub'):
        success_count += 1
    
    # Test module5_core from root directory
    sys.path.append('.')
    if test_import('module5_core', 'CAE Core'):
        success_count += 1
    
    print("=" * 40)
    print(f"Import Test Results: {success_count}/5 hubs can be imported")
    
    if success_count == 5:
        print("✓ All hubs can be imported successfully!")
    else:
        print("✗ Some hubs have import issues that need to be resolved.")
