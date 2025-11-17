@echo off
setlocal
rem === change nothing below unless your paths differ ===
cd /d "C:\Users\khan\Downloads\iraqaf_starter_kit"
if not exist "logs" mkdir "logs"
"C:\Users\khan\Downloads\iraqaf_starter_kit\venv\Scripts\python.exe" -m cli.iraqaf_cli run-all --config "configs\project.example.yaml" --out "reports" >> "logs\weekly_audit.log" 2>&1
endlocal
