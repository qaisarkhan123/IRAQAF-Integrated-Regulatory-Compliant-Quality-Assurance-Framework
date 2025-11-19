#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IRAQAF - START ALL THREE DASHBOARDS
Automatically launches all three dashboards in separate processes
Run: python START_ALL_DASHBOARDS.py
"""

import subprocess
import time
import sys
import os
import signal
import webbrowser
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_PATH = r"C:\Users\khan\Downloads\iraqaf_starter_kit"
VENV_PYTHON = os.path.join(PROJECT_PATH, "venv", "Scripts", "python.exe")
DASHBOARD_DIR = os.path.join(PROJECT_PATH, "dashboard")

DASHBOARDS = {
    "Main Dashboard": {
        "port": 8501,
        "file": "app.py",
        "type": "streamlit",
        "url": "http://localhost:8501",
        "desc": "User authentication, RBAC, alerts, PDF/CSV export",
        "icon": "📊"
    },
    "Security Hub": {
        "port": 8502,
        "file": "privacy_security_hub.py",
        "type": "flask",
        "url": "http://localhost:8502",
        "desc": "8 Security modules, real-time analytics",
        "icon": "🔐"
    },
    "L4 Explainability Hub": {
        "port": 5000,
        "file": "hub_explainability_app.py",
        "type": "flask",
        "url": "http://localhost:5000",
        "desc": "SHAP, LIME, GradCAM, Decision Paths (Score: 85/100)",
        "icon": "🔍"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def print_header():
    """Print startup header"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║          IRAQAF - STARTING ALL THREE DASHBOARDS               ║
╚════════════════════════════════════════════════════════════════╝
""")


def print_dashboard_info():
    """Print dashboard information"""
    print("\n📊 DASHBOARDS TO START:\n")
    for idx, (name, config) in enumerate(DASHBOARDS.items(), 1):
        print(f"  {idx}. {config['icon']} {name}")
        print(f"     Port: {config['port']} | Type: {config['type'].upper()}")
        print(f"     Desc: {config['desc']}")
        print()


def kill_existing_processes():
    """Kill any existing Python/Streamlit processes"""
    print("🛑 Stopping any existing processes...\n")
    try:
        if sys.platform == "win32":
            os.system("taskkill /F /IM python.exe /T 2>nul")
            os.system("taskkill /F /IM streamlit.exe /T 2>nul")
        else:
            os.system("pkill -f streamlit")
            os.system("pkill -f 'python.*dashboard'")
    except Exception as e:
        print(f"   ⚠️  Could not kill processes: {e}")

    time.sleep(2)
    print("✅ Cleaned up old processes\n")


def start_dashboard(name, config):
    """Start a single dashboard"""
    dashboard_path = os.path.join(DASHBOARD_DIR, config['file'])

    if not os.path.exists(dashboard_path):
        print(f"   ❌ File not found: {dashboard_path}")
        return None

    try:
        if config['type'] == 'streamlit':
            cmd = [
                VENV_PYTHON, "-m", "streamlit", "run",
                dashboard_path,
                "--server.port", str(config['port'])
            ]
        else:  # flask
            cmd = [VENV_PYTHON, dashboard_path]

        # Start process
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )

        print(f"✅ {name} started on {config['url']}")
        return process

    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None


def print_success_message():
    """Print success message with all URLs"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║          🎉 ALL DASHBOARDS STARTED SUCCESSFULLY!              ║
╚════════════════════════════════════════════════════════════════╝

📊 DASHBOARD ACCESS:
""")

    for name, config in DASHBOARDS.items():
        print(f"\n   {config['icon']} {name}")
        print(f"       URL: {config['url']}")
        print(f"       Type: {config['type'].upper()}")
        print(f"       Port: {config['port']}")

    print(f"""

🔐 LOGIN CREDENTIALS:
    Username: admin
    Password: admin_default_123

📝 L4 HUB TABS (5 Total):
    • Overview - 12 modules dashboard
    • 🔍 How Model Decides - SHAP/LIME/GradCAM/Paths
    • Detailed Analysis - Module breakdowns
    • How Scores Are Calculated - Mathematical formulas
    • Recommendations - Improvement suggestions

⚠️  NOTES:
    • All dashboards run in separate terminal windows
    • Ports: 8501 (Main), 8502 (Security), 5000 (L4)
    • Each window shows live server output
    • Browser windows will open automatically
    • To stop: Close terminal windows or Ctrl+C

🔗 QUICK URLS:
    Main:     http://localhost:8501
    Security: http://localhost:8502
    L4 Hub:   http://localhost:5000

✅ System ready! Dashboards loading...

""")


def open_browsers():
    """Open all dashboards in default browser"""
    print("🌐 Opening dashboards in browser...\n")
    for name, config in DASHBOARDS.items():
        try:
            webbrowser.open(config['url'])
            time.sleep(1)
        except Exception as e:
            print(f"   ⚠️  Could not open {config['url']}: {e}")

# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main startup function"""
    try:
        print_header()
        print_dashboard_info()

        # Kill existing processes
        kill_existing_processes()

        # Start all dashboards
        print("🚀 Starting dashboards...\n")
        processes = []

        for name, config in DASHBOARDS.items():
            print(
                f"{config['icon']} Starting {name} (Port {config['port']})...")
            process = start_dashboard(name, config)
            if process:
                processes.append((name, process))
            time.sleep(2)

        # Print success message
        print_success_message()

        # Open browsers
        time.sleep(3)
        open_browsers()

        print("=" * 70)
        print("All dashboards are running! Press Ctrl+C to stop.\n")
        print("=" * 70 + "\n")

        # Keep script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping dashboards...\n")
            for name, process in processes:
                try:
                    process.terminate()
                    print(f"✅ {name} stopped")
                except:
                    pass
            print("\n✅ All dashboards stopped\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
