@echo off
setlocal EnableDelayedExpansion

REM --- STEP 0: SCRIPT SETUP ---
cd /d "%~dp0"
if %errorlevel% neq 0 (
    echo [FATAL ERROR] Could not change directory to script location.
    exit /b 1
)

REM --- STEP 1: HARDWARE DETECTION ---
set "PYTHON_CMD=venv\Scripts\python.exe"
"%PYTHON_CMD%" "scripts\installer\gpu_autodetect.py"
if %errorlevel% neq 0 (
    echo [FATAL ERROR] The 'gpu_autodetect.py' script failed.
    exit /b 1
)

REM --- STEP 2: ENV LOADER ---
"%PYTHON_CMD%" "scripts\installer\env_loader.py"
if %errorlevel% neq 0 (
    echo [FATAL ERROR] The 'env_loader.py' script failed.
    exit /b 1
)

REM --- STEP 3: COMPOSE GENERATOR ---
"%PYTHON_CMD%" "scripts\installer\generate_docker_compose.py"
if %errorlevel% neq 0 (
    echo [FATAL ERROR] The 'generate_docker_compose.py' script failed.
    exit /b 1
)

REM --- STEP 4: DOCKER COMPOSE UP ---
docker-compose -f docker/docker-compose.full.yml up -d --pull never
if %errorlevel% neq 0 (
    echo [FATAL ERROR] docker-compose up failed.
    exit /b 1
)

REM --- STEP 5: LIVE MONITORING ---
:monitor_loop
for /f "tokens=1,2*" %%A in ('docker ps --format "{{.Names}} {{.Status}}"') do (
    echo [MONITOR] %%A: %%B
    if /I "%%B" NEQ "Up" (
        echo [ERROR] Container %%A is not running. Investigate logs.
        docker logs %%A
    )
)
timeout /t 10 >nul
goto :monitor_loop

REM --- STEP 6: USER OVERRIDE ---
REM User can edit env files and rerun this script to reload config and restart containers

echo [SUCCESS] All scripts completed without fatal errors.
exit /b 0