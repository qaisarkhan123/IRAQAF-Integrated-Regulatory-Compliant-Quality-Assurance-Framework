@echo off
REM ════════════════════════════════════════════════════════════════════════════
REM  IRAQAF COMPLETE SYSTEM LAUNCHER - ALL 4 DASHBOARDS
REM ════════════════════════════════════════════════════════════════════════════
REM
REM This script starts all four dashboards:
REM  • L0 Main Dashboard (Port 8501 - Streamlit)
REM  • L1 Regulations Hub (Port 8504 - Flask)
REM  • L2 Privacy & Security Hub (Port 8502 - Flask)
REM  • L4 Explainability Hub (Port 5000 - Flask)
REM

setlocal enabledelayedexpansion

cd C:\Users\khan\Downloads\iraqaf_starter_kit

echo.
echo ════════════════════════════════════════════════════════════════════════════
echo  IRAQAF COMPLETE SYSTEM - STARTING ALL 4 DASHBOARDS
echo ════════════════════════════════════════════════════════════════════════════
echo.
echo  Cleaning up old processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq*flask*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq*streamlit*" >nul 2>&1
ping 127.0.0.1 -n 3 >nul 2>&1

echo  ✓ Old processes stopped
echo.
echo  Starting dashboards...
echo.

REM Terminal 1: L1 Regulations Hub (Flask)
echo  [1/4] L1 Regulations & Governance Hub (Port 8504)...
start "L1_HUB" cmd /k "cd C:\Users\khan\Downloads\iraqaf_starter_kit && .\venv\Scripts\python.exe dashboard\l1_regulations_governance_hub.py"
ping 127.0.0.1 -n 3 >nul 2>&1

REM Terminal 2: L2 Privacy & Security Hub (Flask)
echo  [2/4] L2 Privacy & Security Hub (Port 8502)...
start "L2_HUB" cmd /k "cd C:\Users\khan\Downloads\iraqaf_starter_kit && .\venv\Scripts\python.exe dashboard\privacy_security_hub.py"
ping 127.0.0.1 -n 3 >nul 2>&1

REM Terminal 3: L4 Explainability Hub (Flask)
echo  [3/4] L4 Explainability Hub (Port 5000)...
start "L4_HUB" cmd /k "cd C:\Users\khan\Downloads\iraqaf_starter_kit && .\venv\Scripts\python.exe dashboard\hub_explainability_app.py"
ping 127.0.0.1 -n 3 >nul 2>&1

REM Terminal 4: L0 Main Dashboard (Streamlit)
echo  [4/4] L0 Main Dashboard (Port 8501)...
start "L0_MAIN" cmd /k "cd C:\Users\khan\Downloads\iraqaf_starter_kit && .\venv\Scripts\streamlit.exe run dashboard\app.py --server.port 8501 --logger.level=off"

echo.
echo ════════════════════════════════════════════════════════════════════════════
echo  ✅ ALL DASHBOARDS LAUNCHED!
echo ════════════════════════════════════════════════════════════════════════════
echo.
echo  Waiting for services to be ready (10 seconds)...
ping 127.0.0.1 -n 11 >nul 2>&1
echo.
echo  🌐 ACCESS YOUR DASHBOARDS:
echo.
echo     L0 Main Dashboard:          http://localhost:8501
echo     L1 Regulations Hub:          http://localhost:8504        [NEW!]
echo     L2 Privacy & Security Hub:   http://localhost:8502
echo     L4 Explainability Hub:       http://localhost:5000
echo.
echo  📝 LOGIN CREDENTIALS:
echo.
echo     Username: admin
echo     Password: admin_default_123
echo.
echo  ⏹️  To stop: Close terminal windows or press CTRL+C in each
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo.

pause
