#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              L3 OPERATIONS CONTROL CENTER - LAUNCHER                      ║
║                                                                            ║
║  Starts the L3 Operations Control Center on port 8503                    ║
║  Supports Windows, Mac, and Linux                                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import time
import socket
import webbrowser
import platform
from pathlib import Path


def is_port_available(port):
    """Check if port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0


def kill_process_on_port(port):
    """Kill process running on port"""
    try:
        if platform.system() == 'Windows':
            os.system(f'netsh int ipv4 set dynamicport tcp start=49152 num=16384')
            result = os.system(f'netstat -ano | findstr :{port}')
            if result == 0:
                # Extract PID and kill
                os.system(f'taskkill /F /PID {port} 2>nul')
        else:
            os.system(f'lsof -ti:{port} | xargs kill -9 2>/dev/null')
        time.sleep(1)
    except:
        pass


def get_venv_python():
    """Get path to Python in virtual environment"""
    venv_paths = [
        Path('./venv/Scripts/python.exe'),  # Windows
        Path('./venv/bin/python'),           # Mac/Linux
        Path('venv/Scripts/python.exe'),     # Windows (relative)
        Path('venv/bin/python'),             # Mac/Linux (relative)
    ]

    for path in venv_paths:
        if path.exists():
            return str(path.resolve())

    # Fallback to system python
    return 'python'


def start_l3_hub():
    """Start L3 Operations Control Center"""

    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🎛️  L3 OPERATIONS CONTROL CENTER - LAUNCHER                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    port = 8503

    print(f"\n📋 System Information:")
    print(f"   OS:       {platform.system()} {platform.release()}")
    print(f"   Python:   {sys.version.split()[0]}")
    print(f"   Port:     {port}")

    print(f"\n🔍 Pre-flight checks...")

    # Check if port is available
    if not is_port_available(port):
        print(f"   ⚠️  Port {port} is in use. Attempting to free...")
        kill_process_on_port(port)
        time.sleep(2)

        if not is_port_available(port):
            print(f"   ❌ Unable to free port {port}")
            sys.exit(1)

    print(f"   ✅ Port {port} available")

    # Verify L3 hub file exists
    l3_file = Path('./dashboard/l3_operations_control_center.py')
    if not l3_file.exists():
        print(f"   ❌ L3 hub file not found at {l3_file}")
        sys.exit(1)

    print(f"   ✅ L3 hub file found")

    # Get Python executable
    python_exe = get_venv_python()
    print(f"   ✅ Python executable: {python_exe}")

    print(f"\n🚀 Starting L3 Operations Control Center...")
    print(
        f"   Command: {python_exe} dashboard/l3_operations_control_center.py")

    try:
        # Start the server
        process = subprocess.Popen(
            [python_exe, 'dashboard/l3_operations_control_center.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )

        print(f"\n   PID: {process.pid}")
        print(f"   Status: Starting...")

        # Wait for server to start
        time.sleep(3)

        # Check if server is running
        if process.poll() is None:
            print(f"   ✅ Server started successfully")

            url = f'http://localhost:{port}'
            print(f"\n✨ L3 Operations Control Center is now running!")
            print(f"\n   🌐 Access at: {url}")
            print(f"\n   📊 Features:")
            print(f"      • All 8 phases integrated")
            print(f"      • Real-time system status")
            print(f"      • API endpoints monitoring")
            print(f"      • Test coverage tracking")
            print(f"      • Performance metrics")

            # Try to open in browser
            try:
                print(f"\n🌍 Opening in browser...")
                webbrowser.open(url)
            except:
                pass

            print(f"\n   Press Ctrl+C to stop the server")
            print(f"\n" + "="*76)

            # Keep process running
            try:
                process.wait()
            except KeyboardInterrupt:
                print(f"\n\n🛑 Shutting down L3 Operations Control Center...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                print(f"   ✅ Server stopped")
        else:
            print(f"   ❌ Server failed to start")
            stdout, stderr = process.communicate()
            print(f"\nError output:")
            print(stderr.decode())
            sys.exit(1)

    except Exception as e:
        print(f"   ❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)  # Change to project root
    start_l3_hub()
