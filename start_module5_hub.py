#!/usr/bin/env python3
"""
Module 5 Hub Launcher

Starts Module 5: Continuous QA Automation & Monitoring on port 8507.
This is the 6th hub that integrates all 5 existing hubs.

Usage:
    python start_module5_hub.py
"""

import sys
import os
import subprocess
import time
import platform

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Start Module 5 Hub."""

    print("\n" + "=" * 80)
    print("  Module 5: Continuous QA Automation & Monitoring - HUB LAUNCHER")
    print("=" * 80 + "\n")

    print("📊 Starting Module 5 on port 8507...\n")
    print("   Integrating 5 existing hubs:")
    print("   🔍 L4 Explainability (port 5000)")
    print("   🔐 L2 Privacy & Security (port 8502)")
    print("   ⚖️  L1 Regulations (port 8504)")
    print("   ⚙️  L3 Operations (port 8503)")
    print("   ⚖️  L3 Fairness & Ethics (port 8506)\n")

    try:
        # Try to import the hub first to check for import errors
        from module5_hub import app
        print("✓ Module 5 hub module loaded successfully\n")

        print("🌐 Open your browser:")
        print("   http://localhost:8507\n")

        print("📊 API Endpoints:")
        print("   GET /api/overview          - Complete system overview")
        print("   GET /api/cqs               - Continuous QA Score")
        print("   GET /api/hub-status        - Hub statuses")
        print("   GET /api/hub/{hub_name}    - Specific hub data\n")

        print("=" * 80)
        print("  Server starting in 3 seconds...")
        print("  Press Ctrl+C to stop")
        print("=" * 80 + "\n")

        time.sleep(3)

        # Import and run
        from module5_hub import app, polling_loop
        import threading

        # Start polling thread
        polling_thread = threading.Thread(target=polling_loop, daemon=True)
        polling_thread.start()

        # Run Flask
        app.run(host='127.0.0.1', port=8507, debug=False,
                use_reloader=False, threaded=True)

    except ImportError as e:
        print(f"❌ Import error: {e}\n")
        print("Make sure you're in the project root directory:")
        print(f"   cd {os.path.dirname(os.path.abspath(__file__))}\n")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
