@echo off
setlocal EnableDelayedExpansion

echo [DEBUG] kos-install.bat script started.

goto :main

:handle_error
    echo [DEBUG] Entered :handle_error label with parameter: %~1
    echo.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo [FATAL ERROR] The script failed at the step above: %~1
    echo [DEBUG] ERRORLEVEL: !errorlevel!
    echo [DEBUG] Last command attempted: !LAST_CMD!
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    pause
    exit /b 1

:main

echo [DEBUG] Before STEP 0
:: --- STEP 0: SCRIPT SETUP ---
echo [DEBUG] Starting kos-install.bat in diagnostic mode...
set "LAST_CMD=cd /d "%~dp0""
cd /d "%~dp0"
echo [DEBUG] After cd /d
if %errorlevel% neq 0 ( call :handle_error "Could not change directory to script location." )
echo [DEBUG] Current working directory set to: %cd%

echo [DEBUG] Before STEP 1
:: --- STEP 1: PYTHON CHECK AND VENV SETUP ---
echo.
echo --- STEP 1: SETTING UP PYTHON ---
set "VENV_DIR=venv"
set "PYTHON_INTERP="

set "LAST_CMD=where py"
echo [DEBUG] Before where py
where py >nul 2>nul
echo [DEBUG] After where py
if %errorlevel% equ 0 ( set "PYTHON_INTERP=py" ) else ( set "LAST_CMD=where python" & where python >nul 2>nul && (set "PYTHON_INTERP=python") )
echo [DEBUG] After where python
if not defined PYTHON_INTERP ( call :handle_error "Could not find 'py.exe' or 'python.exe' in your PATH." )
echo [DEBUG] Found Python interpreter: %PYTHON_INTERP%

if exist "%VENV_DIR%" (
    echo [DEBUG] Virtual environment '.\%VENV_DIR%' already exists. Skipping creation.
) else (
    set "LAST_CMD=%PYTHON_INTERP% -m venv %VENV_DIR%"
    echo [DEBUG] Attempting to create virtual environment...
    %PYTHON_INTERP% -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 ( call :handle_error "Command '%PYTHON_INTERP% -m venv %VENV_DIR%' failed." )
    echo [DEBUG] Virtual environment created successfully.
)

echo [DEBUG] Before setting PYTHON_CMD and PIP_CMD
set "PYTHON_CMD=%VENV_DIR%\Scripts\python.exe"
set "PIP_CMD=%VENV_DIR%\Scripts\pip.exe"
echo [DEBUG] After setting PYTHON_CMD and PIP_CMD

echo [DEBUG] Before STEP 2
:: --- STEP 2: INSTALL DEPENDENCIES ---
echo.
echo --- STEP 2: INSTALLING DEPENDENCIES ---
set "LAST_CMD=%PIP_CMD% install -r requirements.txt"
echo [DEBUG] Executing: %PIP_CMD% install -r requirements.txt
"%PIP_CMD%" install -r "requirements.txt"
echo [DEBUG] After pip install
if %errorlevel% neq 0 ( call :handle_error "Failed to install Python packages from requirements.txt" )
echo [DEBUG] Python dependencies installed successfully.

echo [DEBUG] Before STEP 3
:: --- STEP 3: RUNNING BUILD SCRIPTS ---
echo.
echo --- STEP 3: EXECUTING BUILD SCRIPTS ---
set "LAST_CMD=%PYTHON_CMD% installer\env_loader.py"
echo [DEBUG] Executing: %PYTHON_CMD% installer\env_loader.py
"%PYTHON_CMD%" "installer\env_loader.py"
echo [DEBUG] After env_loader.py
if %errorlevel% neq 0 ( call :handle_error "The 'env_loader.py' script failed." )
echo [DEBUG] 'env_loader.py' finished.

set "LAST_CMD=%PYTHON_CMD% installer\env_audit.py"
echo.
echo [DEBUG] Executing: %PYTHON_CMD% installer\env_audit.py
"%PYTHON_CMD%" "installer\env_audit.py"
echo [DEBUG] After env_audit.py
if %errorlevel% neq 0 ( call :handle_error "The 'env_audit.py' script failed." )
echo [DEBUG] 'env_audit.py' finished.

set "LAST_CMD=%PYTHON_CMD% installer\generate_docker_compose.py"
echo.
echo [DEBUG] Executing: %PYTHON_CMD% installer\generate_docker_compose.py
"%PYTHON_CMD%" "installer\generate_docker_compose.py"
echo [DEBUG] After generate_docker_compose.py
if %errorlevel% neq 0 ( call :handle_error "The 'generate_docker_compose.py' script failed." )
echo [DEBUG] 'generate_docker_compose.py' finished.

echo.
echo --------------------------------------------------------
echo [SUCCESS] All scripts completed without fatal errors.
echo --------------------------------------------------------
pause
exit /b 0