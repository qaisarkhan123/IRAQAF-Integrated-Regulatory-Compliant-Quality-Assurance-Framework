@echo off
setlocal

rem === Prefer the venv's python if available ===
set "PYTHON_EXE=python"
if exist "%~dp0venv\Scripts\python.exe" set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"

rem === Set PYTHONPATH only for this script run ===
set "PYTHONPATH=%~dp0dashboard"

echo ========================================
echo IRAQAF Dashboard Test Runner
echo ========================================
echo.

rem === Check if pytest is installed ===
"%PYTHON_EXE%" -c "import pytest" 2>nul
if errorlevel 1 (
    echo [ERROR] pytest not installed in this interpreter: %PYTHON_EXE%
    echo Install with: "%PYTHON_EXE%" -m pip install pytest pytest-cov pytest-mock
    pause
    exit /b 1
)

echo [INFO] Using Python: %PYTHON_EXE%
echo [INFO] PYTHONPATH: %PYTHONPATH%
echo.

rem === Parse command line args ===
if "%~1"==""        goto run_all
if /i "%~1"=="quick"    goto run_quick
if /i "%~1"=="coverage" goto run_coverage
if /i "%~1"=="verbose"  goto run_verbose
if /i "%~1"=="help"     goto show_help

:run_all
echo Running all tests...
"%PYTHON_EXE%" -m pytest tests/ -v
goto end

:run_quick
echo Running quick tests (skip "slow")...
"%PYTHON_EXE%" -m pytest tests/ -v -m "not slow"
goto end

:run_coverage
echo Running tests with coverage report...
"%PYTHON_EXE%" -m pytest tests/ -v ^
  --cov=app --cov-branch ^
  --cov-report=term-missing --cov-report=html
echo.
echo Coverage report saved to htmlcov\index.html
goto end

:run_verbose
echo Running tests with extra verbosity...
"%PYTHON_EXE%" -m pytest tests/ -vv -s
goto end

:show_help
echo Usage: run_tests.bat [option]
echo.
echo Options:
echo   (none)     Run all tests
echo   quick      Run quick tests only (skip slow tests)
echo   coverage   Run tests with coverage report (htmlcov)
echo   verbose    Run tests with -vv -s
echo   help       Show this help
echo.
goto end

:end
set "ecode=%errorlevel%"
endlocal & exit /b %ecode%
