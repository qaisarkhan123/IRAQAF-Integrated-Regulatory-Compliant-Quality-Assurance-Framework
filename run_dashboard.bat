@echo off
rem === Activate venv ===
call "%~dp0venv\Scripts\activate"
rem === Env vars ===
set "PYTHONPATH=%~dp0dashboard;%C:\Users\khan\Downloads\iraqaf_starter_kit\dashboard;%PYTHONPATH%%"
set "STREAMLIT_SERVER_PORT=8501"
set "STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"
rem === Run ===
streamlit run "%~dp0dashboard\app.py"
