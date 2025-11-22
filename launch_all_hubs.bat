@echo off
echo.
echo ===============================================================================
echo 🚀 AI GOVERNANCE HUBS LAUNCHER
echo ===============================================================================
echo 🎯 Starting Comprehensive AI Quality Assurance & Governance Framework
echo.

cd /d "%~dp0"

echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

echo 📦 Installing/updating dependencies...
python -m pip install --upgrade streamlit flask pandas plotly numpy requests beautifulsoup4 scikit-learn

echo.
echo 🚀 Launching all AI Governance Hubs...
echo.

python launch_all_hubs.py

echo.
echo 👋 All hubs have been stopped. Press any key to exit...
pause >nul
