@echo off
echo Starting IRAQAF Platform Hubs...
echo ================================

echo Starting L2 Privacy & Security Hub (Port 8502)...
start "L2 Privacy Security" cmd /k "cd dashboard && python privacy_security_hub.py"
timeout /t 2 /nobreak >nul

echo Starting L3 Fairness & Ethics Hub (Port 8506)...
start "L3 Fairness Ethics" cmd /k "cd dashboard && python l3_fairness_ethics_hub.py"
timeout /t 2 /nobreak >nul

echo Starting L4 Explainability Hub (Port 5000)...
start "L4 Explainability" cmd /k "cd dashboard && python hub_explainability_app.py"
timeout /t 2 /nobreak >nul

echo Starting SOQM Operations Hub (Port 8503)...
start "SOQM Operations" cmd /k "cd dashboard && python l3_operations_control_center.py"
timeout /t 2 /nobreak >nul

echo Starting CAE Core (Port 8508)...
start "CAE Core" cmd /k "python module5_core.py"
timeout /t 2 /nobreak >nul

echo All hubs started! Waiting 10 seconds for initialization...
timeout /t 10 /nobreak >nul

echo Checking hub status...
curl -s http://localhost:8502/health >nul 2>&1 && echo L2 Privacy Security: ONLINE || echo L2 Privacy Security: OFFLINE
curl -s http://localhost:8506/health >nul 2>&1 && echo L3 Fairness Ethics: ONLINE || echo L3 Fairness Ethics: OFFLINE  
curl -s http://localhost:5000/health >nul 2>&1 && echo L4 Explainability: ONLINE || echo L4 Explainability: OFFLINE
curl -s http://localhost:8503/health >nul 2>&1 && echo SOQM Operations: ONLINE || echo SOQM Operations: OFFLINE
curl -s http://localhost:8508/health >nul 2>&1 && echo CAE Core: ONLINE || echo CAE Core: OFFLINE

echo ================================
echo IRAQAF Platform startup complete!
pause
