@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
if %errorlevel% neq 0 (
    echo [FATAL ERROR] Could not change directory to script location.
    exit /b 1
)
set "PYTHON_CMD=venv\Scripts\python.exe"
"%PYTHON_CMD%" scripts\installer\kos_install.py
exit /b %errorlevel%