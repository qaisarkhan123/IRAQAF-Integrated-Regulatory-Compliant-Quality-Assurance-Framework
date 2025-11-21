#!/usr/bin/env python3
import sys
import os
sys.path.append('dashboard')

try:
    print("Testing L3 Fairness & Ethics Hub import...")
    import l3_fairness_ethics_hub
    print("✓ L3 hub imports successfully")
    
    # Test if the app is created
    if hasattr(l3_fairness_ethics_hub, 'app'):
        print("✓ Flask app found")
        
        # Try to start the app
        print("Starting L3 hub on port 8506...")
        l3_fairness_ethics_hub.app.run(host='127.0.0.1', port=8506, debug=False)
    else:
        print("❌ No Flask app found in module")
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
