@echo off
setlocal enabledelayedexpansion

REM Change to the project root (parent of this script)
cd /d %~dp0..

REM KOS v1 Automated Deployment Script for Windows
REM Zero-interaction installation with auto-detection and feature flag management

echo [INFO] Starting KOS v1 automated deployment...
echo [INFO] This will install and configure KOS v1 with zero user interaction
echo.

REM Function to print colored output (Windows-compatible)
:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Function to pause and wait for user input (for debugging)
:pause
echo.
echo Press Enter to continue...
pause >nul
goto :eof

REM Function to check if command exists
:command_exists
where %~1 >nul 2>&1
if %errorlevel% equ 0 (
    goto :eof
) else (
    exit /b 1
)

REM Function to install Python dependencies
:install_python_deps
call :print_status "Installing Python dependencies..."

REM Check if Python is available
echo [DEBUG] Checking if %PYTHON_CMD% exists...
call :command_exists %PYTHON_CMD%
if %errorlevel% neq 0 (
    call :print_error "Python not found. Please install Python 3.8+"
    echo [DEBUG] Python command '%PYTHON_CMD%' not found in PATH
    exit /b 1
)

REM Install psutil for system detection
call :print_status "Installing psutil for system detection..."
echo [DEBUG] Running: %PIP_CMD% install psutil
%PIP_CMD% install psutil
if %errorlevel% neq 0 (
    call :print_error "Failed to install psutil"
    echo [DEBUG] pip install psutil failed with exit code %errorlevel%
    exit /b 1
)

call :print_success "Python dependencies installed"
goto :eof

REM Function to generate environment files
:generate_environment
call :print_status "Generating environment configuration..."

REM Run the environment loader
echo [DEBUG] Running: %PYTHON_CMD% scripts\env_loader.py
%PYTHON_CMD% scripts\env_loader.py
if %errorlevel% neq 0 (
    call :print_error "Failed to generate environment configuration"
    echo [DEBUG] env_loader.py failed with exit code %errorlevel%
    exit /b 1
)

call :print_success "Environment configuration generated"
goto :eof

REM Function to create necessary directories
:create_directories
call :print_status "Creating necessary directories..."

echo [DEBUG] Creating directories...
if not exist "vault" mkdir vault
if not exist "dicom" mkdir dicom
if not exist "models" mkdir models
if not exist "plugins" mkdir plugins
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "tmp" mkdir tmp
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "monitoring" mkdir monitoring

call :print_success "Directories created"
goto :eof

REM Function to check Docker installation
:check_docker
call :print_status "Checking Docker installation..."

echo [DEBUG] Checking if docker exists...
call :command_exists docker
if %errorlevel% neq 0 (
    call :print_warning "Docker not found. Please install Docker Desktop for Windows from https://www.docker.com/products/docker-desktop"
    call :print_warning "After installation, restart this script"
    exit /b 1
)

echo [DEBUG] Checking if docker-compose exists...
call :command_exists docker-compose
if %errorlevel% neq 0 (
    call :print_warning "Docker Compose not found. Please install Docker Desktop for Windows from https://www.docker.com/products/docker-desktop"
    call :print_warning "After installation, restart this script"
    exit /b 1
)

echo [DEBUG] Running: docker --version
docker --version
echo [DEBUG] Running: docker-compose --version
docker-compose --version
call :print_success "Docker and Docker Compose found"
goto :eof

REM Function to start KOS v1
:start_kos
call :print_status "Starting KOS v1..."

REM Load environment variables if .env exists
if exist ".env" (
    echo [DEBUG] Loading .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
) else (
    echo [DEBUG] No .env file found
)

REM Start with docker-compose
echo [DEBUG] Running: docker-compose up -d
docker-compose up -d
if %errorlevel% neq 0 (
    call :print_error "Failed to start KOS v1"
    echo [DEBUG] docker-compose up -d failed with exit code %errorlevel%
    exit /b 1
)

call :print_success "KOS v1 started successfully!"
goto :eof

REM Function to check service health
:check_health
call :print_status "Checking service health..."

REM Wait for services to be ready
echo [DEBUG] Waiting 10 seconds for services to start...
timeout /t 10 /nobreak >nul

REM Check API health (using PowerShell for better HTTP handling)
echo [DEBUG] Checking API health...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:%KOS_API_EXTERNAL_PORT%/health' -UseBasicParsing | Out-Null; Write-Host 'API service is healthy' } catch { Write-Host 'API service health check failed' }"
if %errorlevel% equ 0 (
    call :print_success "API service is healthy"
) else (
    call :print_warning "API service health check failed"
    echo [DEBUG] API health check failed for port %KOS_API_EXTERNAL_PORT%
)

REM Check frontend
echo [DEBUG] Checking frontend health...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:%KOS_FRONTEND_EXTERNAL_PORT%' -UseBasicParsing | Out-Null; Write-Host 'Frontend service is healthy' } catch { Write-Host 'Frontend service health check failed' }"
if %errorlevel% equ 0 (
    call :print_success "Frontend service is healthy"
) else (
    call :print_warning "Frontend service health check failed"
    echo [DEBUG] Frontend health check failed for port %KOS_FRONTEND_EXTERNAL_PORT%
)

goto :eof

REM Function to display access information
:display_access_info
call :print_success "KOS v1 deployment completed!"
echo.
echo Access Information:
echo ==================
echo Web Dashboard: http://localhost:%KOS_FRONTEND_EXTERNAL_PORT%
echo API Documentation: http://localhost:%KOS_API_EXTERNAL_PORT%/docs
echo API Health Check: http://localhost:%KOS_API_EXTERNAL_PORT%/health
echo Container Monitoring: http://localhost:%KOS_CADVISOR_EXTERNAL_PORT%
echo.
echo Database Access:
echo PostgreSQL: localhost:%KOS_POSTGRES_EXTERNAL_PORT%
echo Redis: localhost:%KOS_REDIS_EXTERNAL_PORT%
echo Weaviate: http://localhost:%KOS_WEAVIATE_EXTERNAL_PORT%
echo MinIO Console: http://localhost:%KOS_MINIO_CONSOLE_EXTERNAL_PORT%
echo.
echo Default Credentials:
echo Admin User: %KOS_ADMIN_USER%
echo Admin Password: %KOS_ADMIN_PASSWORD%
echo.
echo Useful Commands:
echo View logs: docker-compose logs -f
echo Stop services: docker-compose down
echo Restart services: docker-compose restart
echo Update services: docker-compose pull ^&^& docker-compose up -d
echo.
goto :eof

REM Error handler
:error
call :print_error "Deployment failed. Check the logs above for more information."
echo.
echo [DEBUG] Error occurred in command: %CMDCMDLINE%
echo [DEBUG] Exit code: %errorlevel%
echo.
echo Press Enter to exit...
pause >nul
exit /b 1

REM === MAIN SEQUENCE ===

REM Detect Python and pip
echo [DEBUG] Detecting Python and pip...
set PYTHON_CMD=python
set PIP_CMD=pip
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
    set PIP_CMD=venv\Scripts\pip.exe
    echo [INFO] Using venv Python: %PYTHON_CMD%
) else (
    echo [INFO] Using system Python: %PYTHON_CMD%
)

call :print_status "Starting KOS v1 automated deployment..."
call :print_status "This will install and configure KOS v1 with zero user interaction"
echo.

echo [DEBUG] Step 1: Create directories
call :create_directories
if %errorlevel% neq 0 goto :error

echo [DEBUG] Step 2: Install Python dependencies
call :install_python_deps
if %errorlevel% neq 0 goto :error

echo [DEBUG] Step 3: Check Docker installation
call :check_docker
if %errorlevel% neq 0 goto :error

echo [DEBUG] Step 4: Generate environment configuration
call :generate_environment
if %errorlevel% neq 0 goto :error

echo [DEBUG] Step 5: Start KOS v1
call :start_kos
if %errorlevel% neq 0 goto :error

echo [DEBUG] Step 6: Check health
call :check_health

echo [DEBUG] Step 7: Display access information
call :display_access_info

call :print_success "KOS v1 deployment completed successfully!"
echo.
echo Press Enter to exit...
pause >nul
exit /b 0 