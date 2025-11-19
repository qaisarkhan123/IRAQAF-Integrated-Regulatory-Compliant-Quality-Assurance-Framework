#!/usr/bin/env python3
"""
Diagnostic script to check dashboard status and startup
"""

import subprocess
import time
import socket
import sys
from pathlib import Path


def check_port_open(port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False


def main():
    print("\n" + "="*80)
    print("IRAQAF DASHBOARD DIAGNOSTIC")
    print("="*80 + "\n")

    # Check ports
    ports = {
        8501: "Main Dashboard (Streamlit)",
        8502: "Security Hub (Flask)",
        8503: "L4 Explainability Hub (Flask)"
    }

    print("📊 PORT STATUS:")
    for port, name in ports.items():
        status = "✓ OPEN" if check_port_open(port) else "✗ CLOSED"
        print(f"  {port}: {name:<40} {status}")

    print("\n")

    # Check required files
    print("📁 REQUIRED FILES:")
    required_files = [
        "dashboard/app.py",
        "dashboard/hub_flask_app.py",
        "dashboard/hub_explainability_app.py",
        "dashboard/audit_utils.py",
        "launch_dual_dashboards.py"
    ]

    for file_path in required_files:
        p = Path(file_path)
        status = "✓" if p.exists() else "✗"
        print(f"  {status} {file_path}")

    # Test L4 Hub (simplest to start)
    print("🧪 TESTING L4 HUB (Flask on port 8503)...")
    try:
        # Kill any existing process
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq L4*'],
                       stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        time.sleep(2)

        # Start L4 hub
        print("  Starting L4 Explainability Hub...")
        proc = subprocess.Popen(
            [sys.executable, 'dashboard/hub_explainability_app.py'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        time.sleep(3)

        if check_port_open(8503):
            print("  ✓ L4 Hub started successfully!")
            print(f"     Access: http://localhost:8503")
            print(f"     PID: {proc.pid}")
        else:
            print("  ✗ L4 Hub failed to start")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\n" + "="*80)
    print("QUICK START:")
    print("="*80)
    print("""
1. L4 Explainability Hub (Flask) - Simplest to run:
   python dashboard/hub_explainability_app.py
   Access: http://localhost:8503

2. Security Hub (Flask):
   python dashboard/hub_flask_app.py
   Access: http://localhost:8502

3. Main Dashboard (Streamlit) - Requires auth:
   streamlit run dashboard/app.py --server.port 8501
   Login: admin / admin_default_123

4. All three together:
   python launch_dual_dashboards.py
""")


if __name__ == '__main__':
    main()
