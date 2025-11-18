"""
IRAQAF Dual Dashboard Launcher
Launches both Streamlit main dashboard (port 8501) and Flask security hub (port 8502)
"""
import subprocess
import time
import sys
import os
from pathlib import Path

# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"

print("\n" + "="*80)
print("🚀 IRAQAF DUAL DASHBOARD LAUNCHER")
print("="*80)
print("\n📊 Main Dashboard (Streamlit) → http://localhost:8501")
print("🔒 Security Hub (Flask) → http://localhost:8502")
print("\n🔑 Login credentials: admin / admin_default_123")
print("="*80 + "\n")

processes = []

try:
    # Kill any existing processes on ports 8501 and 8502
    print("🧹 Clearing ports 8501 and 8502...")
    os.system("taskkill /F /IM streamlit.exe /ErrorAction SilentlyContinue 2>nul")
    os.system("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq IRAQAF*\" 2>nul")
    time.sleep(2)
    
    # Launch Main Dashboard (Streamlit)
    print("▶️  Starting Main Dashboard on port 8501...")
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
        stderr=subprocess.PIPE
    )
    processes.append(("Main Dashboard (8501)", main_proc))
    
    time.sleep(3)
    
    # Launch Flask Security Hub
    print("▶️  Starting Privacy & Security Hub on port 8502...")
    hub_proc = subprocess.Popen(
        [
            str(VENV_PYTHON),
            str(PROJECT_ROOT / "dashboard" / "hub_flask_app.py")
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append(("Security Hub (8502)", hub_proc))
    
    time.sleep(2)
    
    print("\n" + "="*80)
    print("✅ BOTH DASHBOARDS LAUNCHED SUCCESSFULLY!")
    print("="*80)
    print("\n📍 Main Dashboard:    http://localhost:8501")
    print("🔒 Security Hub:      http://localhost:8502")
    print("\n🔑 Login: admin / admin_default_123")
    print("\n⚠️  Close this window to stop both applications")
    print("="*80 + "\n")
    
    # Wait for processes
    main_proc.wait()
    hub_proc.wait()
    
except KeyboardInterrupt:
    print("\n\n⏹️  Shutting down...")
    for name, proc in processes:
        if proc.poll() is None:
            print(f"   Stopping {name}...")
            proc.terminate()
            time.sleep(1)
            if proc.poll() is None:
                proc.kill()
    print("✓ All processes stopped")
    sys.exit(0)

except Exception as e:
    print(f"\n❌ Error: {e}")
    for name, proc in processes:
        if proc.poll() is None:
            proc.terminate()
    sys.exit(1)
