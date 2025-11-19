@echo off
REM 🔐 PRIVACY & SECURITY HUB - ENHANCED DEPLOYMENT SCRIPT
REM Deploys upgraded hub with 3 new modules (52% → 85% SAI)
REM Port: 8502

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo 🔐 PRIVACY ^& SECURITY HUB - ENHANCED DEPLOYMENT
echo ================================================================================
echo.
echo Upgrading from 52%% SAI to 85%% SAI
echo Adding 3 critical modules:
echo   1. Anonymization ^& De-identification
echo   2. Model Security ^& Adversarial Testing
echo   3. Data Minimization ^& Retention
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

REM Navigate to dashboard directory
cd /d "C:\Users\khan\Downloads\iraqaf_starter_kit\dashboard"

if errorlevel 1 (
    echo ❌ ERROR: Dashboard directory not found
    echo Expected: C:\Users\khan\Downloads\iraqaf_starter_kit\dashboard
    pause
    exit /b 1
)

echo ✅ Dashboard directory found
echo.

REM Check for backup
if exist privacy_security_hub_backup.py (
    echo ℹ️ Backup already exists (privacy_security_hub_backup.py)
) else (
    echo 📦 Creating backup of original privacy_security_hub.py...
    copy privacy_security_hub.py privacy_security_hub_backup.py
    if errorlevel 1 (
        echo ⚠️ Warning: Could not create backup
    ) else (
        echo ✅ Backup created: privacy_security_hub_backup.py
    )
)

echo.
echo ================================================================================
echo 🚀 STARTING ENHANCED SECURITY HUB
echo ================================================================================
echo.
echo Port: 8502
echo URL: http://127.0.0.1:8502
echo.
echo API Endpoints:
echo   - GET /api/anonymization
echo   - GET /api/model-security
echo   - GET /api/data-minimization
echo   - GET /api/sai
echo   - GET /api/all-modules
echo.
echo Press CTRL+C to stop
echo.

REM Start the enhanced security hub
python privacy_security_hub_enhanced.py

pause
