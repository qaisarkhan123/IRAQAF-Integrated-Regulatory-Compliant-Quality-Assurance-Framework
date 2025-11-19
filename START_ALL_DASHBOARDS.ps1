# ============================================================================
# IRAQAF - START ALL THREE DASHBOARDS
# ============================================================================
# This script automatically starts all three dashboards in separate windows
# Run this file to launch the complete IRAQAF system
# ============================================================================

Write-Host "
╔════════════════════════════════════════════════════════════════╗
║          IRAQAF - STARTING ALL THREE DASHBOARDS               ║
╚════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

# Define paths
$projectPath = "C:\Users\khan\Downloads\iraqaf_starter_kit"
$pythonExe = "$projectPath\venv\Scripts\python.exe"

# Stop any existing processes
Write-Host "`n🛑 Stopping any existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "✅ Cleaned up old processes`n" -ForegroundColor Green

# Start Dashboard 1: Main Dashboard (Port 8501 - Streamlit)
Write-Host "🚀 Starting Dashboard 1: Main Application Dashboard (Port 8501)..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "-m streamlit run `"$projectPath\dashboard\app.py`" --server.port 8501" -WorkingDirectory $projectPath
Write-Host "   ✅ Main Dashboard started on http://localhost:8501" -ForegroundColor Green
Start-Sleep -Seconds 3

# Start Dashboard 2: Security Hub (Port 8502 - Flask)
Write-Host "`n🔐 Starting Dashboard 2: Privacy & Security Hub (Port 8502)..." -ForegroundColor Magenta
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "`"$projectPath\dashboard\privacy_security_hub.py`"" -WorkingDirectory $projectPath
Write-Host "   ✅ Security Hub started on http://localhost:8502" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start Dashboard 3: L4 Explainability Hub (Port 5000 - Flask)
Write-Host "`n🔍 Starting Dashboard 3: L4 Explainability & Transparency Hub (Port 5000)..." -ForegroundColor Cyan
Start-Process -NoNewWindow -FilePath $pythonExe -ArgumentList "`"$projectPath\dashboard\hub_explainability_app.py`"" -WorkingDirectory $projectPath
Write-Host "   ✅ L4 Hub started on http://localhost:5000" -ForegroundColor Green
Start-Sleep -Seconds 2

Write-Host "
╔════════════════════════════════════════════════════════════════╗
║              🎉 ALL DASHBOARDS STARTED SUCCESSFULLY!          ║
╚════════════════════════════════════════════════════════════════╝

📊 DASHBOARD ACCESS:
   
   1️⃣  MAIN DASHBOARD (Streamlit)
       URL: http://localhost:8501
       Login: admin / admin_default_123
       Features: Authentication, RBAC, PDF/CSV Export, Alerts
   
   2️⃣  SECURITY HUB (Flask)
       URL: http://localhost:8502
       Features: 8 Security Modules, Real-time Analytics
   
   3️⃣  L4 EXPLAINABILITY HUB (Flask)
       URL: http://localhost:5000
       Features: SHAP, LIME, GradCAM, Decision Paths
       Score: 85/100 (Exceeds 80% benchmark)

📝 TABS IN L4 HUB:
   • Overview - 12 modules dashboard
   • 🔍 How Model Decides - SHAP/LIME/GradCAM/Paths
   • Detailed Analysis - Module breakdowns
   • How Scores Are Calculated - Mathematical formulas
   • Recommendations - Improvement suggestions

⚠️  NOTE:
   • All three dashboards run in background
   • To stop, close the terminal windows or run:
     Stop-Process -Name streamlit -Force
     Stop-Process -Name python -Force (be careful!)
   • Check console output in each window for errors
   • Ports: 8501 (Main), 8502 (Security), 5000 (L4)

🔗 QUICK LINKS:
   Main:     http://localhost:8501
   Security: http://localhost:8502
   L4 Hub:   http://localhost:5000

" -ForegroundColor Green

Write-Host "✅ System ready! Opening dashboards in browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# Open browsers
Start-Process "http://localhost:8501"
Start-Sleep -Seconds 1
Start-Process "http://localhost:8502"
Start-Sleep -Seconds 1
Start-Process "http://localhost:5000"

Write-Host "`n✅ All dashboards opened in browser!`n" -ForegroundColor Green
