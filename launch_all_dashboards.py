#!/usr/bin/env python3
"""
IRAQAF Master Dashboard Launcher
Starts all 6 dashboards and 2 Flask hubs for complete system visibility

Dashboard System:
  1. Main Dashboard (8501)       - Streamlit portal with navigation
  2. L2 Privacy & Security Hub (8502)   - Flask security assessment
  3. L4 Explainability Hub (5000)       - Flask AI transparency
  4. L1 Regulations Hub (8504)          - Flask compliance checking
  5. L3 Operations Hub (8503)           - Flask system operations
  6. Fairness & Ethics Hub (8506)       - Flask fairness monitoring

Module 5 System (Continuous QA Orchestrator):
  - Module 5 Hub (8507)          - Aggregates all 5 hub scores
  - Module 5 Core (8508)         - Deep automation & drift detection

Usage:
  python launch_all_dashboards.py

All dashboards will start in parallel and open in browser automatically.
"""

import subprocess
import sys
import time
import webbrowser
import os
import signal
from pathlib import Path

# Dashboard configurations
DASHBOARDS = [
    {
        'name': 'L4 Explainability Hub',
        'port': 5000,
        'color': 'Cyan',
        'file': 'dashboard/hub_explainability_app.py',
        'type': 'python'
    },
    {
        'name': 'L2 Privacy & Security Hub',
        'port': 8502,
        'color': 'Magenta',
        'file': 'dashboard/privacy_security_hub.py',
        'type': 'python'
    },
    {
        'name': 'L1 Regulations & Governance Hub',
        'port': 8504,
        'color': 'Blue',
        'file': 'dashboard/l1_regulations_governance_hub.py',
        'type': 'python'
    },
    {
        'name': 'L3 Operations & Control Hub',
        'port': 8503,
        'color': 'Green',
        'file': 'dashboard/l3_operations_control_center.py',
        'type': 'python'
    },
    {
        'name': 'Fairness & Ethics Hub',
        'port': 8506,
        'color': 'Yellow',
        'file': 'start_fairness_hub.py',
        'type': 'python'
    },
    {
        'name': 'Module 5 Hub',
        'port': 8507,
        'color': 'White',
        'file': 'start_module5_hub.py',
        'type': 'python'
    },
    {
        'name': 'Module 5 Core',
        'port': 8508,
        'color': 'White',
        'file': 'start_module5_core.py',
        'type': 'python'
    },
    {
        'name': 'Main Dashboard',
        'port': 8501,
        'color': 'Yellow',
        'file': 'dashboard/app.py',
        'type': 'streamlit'
    }
]

# Get Python executable
if hasattr(sys, 'base_prefix'):
    venv_python = str(Path(sys.executable).parent / 'python')
else:
    venv_python = sys.executable

project_root = Path(__file__).parent.resolve()


def print_header():
    """Print launch header"""
    print("\n" + "=" * 90)
    print(" " * 20 + "IRAQAF MASTER DASHBOARD LAUNCHER")
    print(" " * 15 + "All 8 Dashboards + 2 Module 5 Components")
    print("=" * 90 + "\n")


def print_status(message: str, color: str = 'White'):
    """Print colored status message"""
    colors = {
        'Green': '\033[92m',
        'Yellow': '\033[93m',
        'Cyan': '\033[96m',
        'Magenta': '\033[95m',
        'Blue': '\033[94m',
        'Red': '\033[91m',
        'White': '\033[97m'
    }
    reset = '\033[0m'
    print(f"{colors.get(color, '')}{message}{reset}")


def launch_dashboard(dashboard: dict, delay: float = 0) -> subprocess.Popen:
    """
    Launch a single dashboard

    Args:
        dashboard: Dashboard configuration dict
        delay: Delay before launching (seconds)

    Returns:
        Popen process object
    """
    if delay > 0:
        time.sleep(delay)

    print_status(
        f"  ▶ {dashboard['name']:40s} (port {dashboard['port']:5d})",
        dashboard['color']
    )

    file_path = project_root / dashboard['file']

    if dashboard['type'] == 'streamlit':
        cmd = [
            venv_python, '-m', 'streamlit', 'run',
            str(file_path),
            '--server.port', str(dashboard['port']),
            '--logger.level=error'
        ]
    else:
        cmd = [venv_python, str(file_path)]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(project_root)
        )
        return process
    except Exception as e:
        print_status(f"    ✗ Failed to start: {e}", 'Red')
        return None


def main():
    """Launch all dashboards"""
    print_header()

    # Kill any existing Python processes running on our ports
    print_status("Cleaning up existing processes...", 'Yellow')
    os.system("Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue")
    time.sleep(2)

    # Launch dashboards with staggered delays
    print_status("Starting all dashboards in parallel...\n", 'Green')

    processes = []
    for i, dashboard in enumerate(DASHBOARDS[:-1]):  # All except Main Dashboard
        process = launch_dashboard(dashboard, delay=i * 0.5)
        if process:
            processes.append(process)

    # Give other hubs time to start, then start Main Dashboard
    time.sleep(6)
    print_status(f"  ▶ Main Dashboard (8501)  - Starts last to connect to all hubs\n", 'Yellow')
    main_process = launch_dashboard(DASHBOARDS[-1])
    if main_process:
        processes.append(main_process)

    # Print summary
    print_status("\n" + "=" * 90, 'Green')
    print_status("✓ ALL DASHBOARDS STARTED SUCCESSFULLY!", 'Green')
    print_status("=" * 90 + "\n", 'Green')

    print_status("ACCESS POINTS:", 'Cyan')
    print()
    print_status("  🎯 Main Dashboard:              http://localhost:8501", 'Yellow')
    print_status("  🔍 L4 Explainability Hub:       http://localhost:5000", 'Cyan')
    print_status("  🔐 L2 Privacy & Security Hub:   http://localhost:8502", 'Magenta')
    print_status("  📋 L1 Regulations Hub:          http://localhost:8504", 'Blue')
    print_status("  ⚙️  L3 Operations Hub:           http://localhost:8503", 'Green')
    print_status("  ⚖️  Fairness & Ethics Hub:       http://localhost:8506", 'Yellow')
    print_status("  📊 Module 5 Hub (Orchestrator): http://localhost:8507", 'Cyan')
    print_status("  🤖 Module 5 Core (AI Engine):   http://localhost:8508", 'Magenta')
    print()

    print_status("LOGIN CREDENTIALS:", 'Cyan')
    print()
    print_status("  Username: admin", 'White')
    print_status("  Password: admin_default_123", 'White')
    print()

    print_status("=" * 90, 'Green')
    print()

    # Open browser
    print_status("Opening main dashboard in browser...\n", 'Yellow')
    time.sleep(2)
    webbrowser.open('http://localhost:8501')

    # Keep running until interrupted
    try:
        print_status("Press Ctrl+C to stop all dashboards...\n", 'Yellow')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_status("\n\nShutting down all dashboards...", 'Yellow')
        for process in processes:
            try:
                process.terminate()
            except:
                pass
        time.sleep(2)
        for process in processes:
            try:
                process.kill()
            except:
                pass
        print_status("✓ All dashboards stopped", 'Green')
        sys.exit(0)


if __name__ == '__main__':
    main()
