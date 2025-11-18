"""
IRAQAF Triple Dashboard Launcher
Launches Streamlit main dashboard (8501), Flask security hub (8502), and Flask L4 explainability hub (8503)
"""
import subprocess
import time
import sys
import os
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent.resolve()
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"

# Verify paths exist
if not VENV_PYTHON.exists():
    print(f"ERROR: Python executable not found at {VENV_PYTHON}")
    print(f"Project root: {PROJECT_ROOT}")
    sys.exit(1)

print("\n" + "="*80)
print(" IRAQAF TRIPLE DASHBOARD LAUNCHER")
print("="*80)
print("\n Main Dashboard (Streamlit)  http://localhost:8501")
print(" Security & Privacy Hub (Flask)  http://localhost:8502")
print(" L4 Explainability Hub (Flask)  http://localhost:8503")
print("\n Login credentials: admin / admin_default_123")
print("="*80 + "\n")

processes = []

try:
    # Kill any existing processes on ports 8501, 8502, and 8503
    print(" Clearing ports 8501, 8502, and 8503...")
    os.system("taskkill /F /IM streamlit.exe /ErrorAction SilentlyContinue 2>nul")
    os.system("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq IRAQAF*\" /ErrorAction SilentlyContinue 2>nul")
    time.sleep(2)

    # Launch Main Dashboard (Streamlit)
    print("  Starting Main Dashboard on port 8501...")
    main_proc = subprocess.Popen(
        [
            str(VENV_PYTHON),
            "-m",
            "streamlit",
            "run",
            str(PROJECT_ROOT / "dashboard" / "app.py"),
            "--server.port=8501",
            "--logger.level=warning"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(PROJECT_ROOT)
    )
    processes.append(("Main Dashboard", main_proc))
    print(" Main Dashboard process started")
    time.sleep(3)

    # Launch Security Hub (Flask)
    print("  Starting Security Hub on port 8502...")
    security_proc = subprocess.Popen(
        [
            str(VENV_PYTHON),
            str(PROJECT_ROOT / "dashboard" / "hub_flask_app.py")
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(PROJECT_ROOT)
    )
    processes.append(("Security Hub", security_proc))
    print(" Security Hub process started")
    time.sleep(2)

    # Launch L4 Explainability Hub (Flask)
    print("  Starting L4 Explainability Hub on port 8503...")
    l4_proc = subprocess.Popen(
        [
            str(VENV_PYTHON),
            str(PROJECT_ROOT / "dashboard" / "hub_explainability_app.py")
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(PROJECT_ROOT)
    )
    processes.append(("L4 Explainability Hub", l4_proc))
    print(" L4 Explainability Hub process started")
    time.sleep(2)

    print("\n" + "="*80)
    print(" ALL DASHBOARDS ARE RUNNING!")
    print("="*80)
    print("\n OPEN IN YOUR BROWSER:")
    print("    Main Dashboard: http://localhost:8501")
    print("    Security Hub: http://localhost:8502")
    print("    L4 Explainability Hub: http://localhost:8503")
    print("\n TIPS:")
    print("    Press CTRL+C to stop all dashboards")
    print("    Main dashboard requires authentication")
    print("    Hubs are open without authentication")
    print("\n" + "="*80 + "\n")

    # Keep processes running
    while True:
        time.sleep(1)
        # Check if any process has terminated
        for name, proc in processes:
            if proc.poll() is not None:
                print(f"  {name} process terminated with code {proc.returncode}")
                sys.exit(1)

except KeyboardInterrupt:
    print("\n\n STOPPING ALL DASHBOARDS...")
    for name, proc in processes:
        print(f"   Stopping {name}...", end="", flush=True)
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print(" ")
    print("\n All dashboards stopped cleanly")

except Exception as e:
    print(f"\n Error: {e}")
    for name, proc in processes:
        proc.kill()
    sys.exit(1)
