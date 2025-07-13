@echo off
REM KOS v1 - Windows Setup Script
REM Supports Windows and Windows Subsystem for Linux (WSL)

setlocal enabledelayedexpansion

echo [INFO] Starting KOS v1 setup for Windows...

REM Check if running in WSL
wsl.exe -e uname -a >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] WSL detected, running Linux setup script...
    wsl.exe bash scripts/setup.sh
    exit /b %errorlevel%
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Node.js not found. Please install Node.js from https://nodejs.org/
    echo [WARNING] Recommended version: 18.x or later
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python not found. Please install Python 3.8+ from https://python.org/
    pause
    exit /b 1
)

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker not found. Please install Docker Desktop from https://docs.docker.com/get-docker/
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "vault" mkdir vault
if not exist "dicom" mkdir dicom
if not exist "models" mkdir models
if not exist "plugins" mkdir plugins
if not exist "logs" mkdir logs
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "monitoring" mkdir monitoring

REM Install frontend dependencies
echo [INFO] Installing frontend dependencies...
cd frontend
if exist "package.json" (
    npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Frontend dependencies installed
) else (
    echo [ERROR] package.json not found in frontend directory
    pause
    exit /b 1
)
cd ..

REM Install Python dependencies
echo [INFO] Setting up Python environment...
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo [INFO] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo [SUCCESS] Setup completed successfully!
echo [INFO] Next steps:
echo   1. Run 'docker-compose up' to start the application
echo   2. Or run 'npm run dev' in the frontend directory for development
echo   3. Or run 'python -m uvicorn backend.main:app --reload' for backend development

pause 