@echo off
echo ========================================
echo KOS v1 Frontend - Automated Installation
echo ========================================
echo.

:: Check if Node.js is installed
echo [1/6] Checking Node.js installation...

:: Try to find Node.js in common locations
set NODE_FOUND=0
set NODE_PATH=

:: Check PATH first
node --version >nul 2>&1
if %errorlevel% equ 0 (
    set NODE_FOUND=1
    set NODE_PATH=node
    goto :node_found
)

:: Check Program Files
if exist "C:\Program Files\nodejs\node.exe" (
    set NODE_FOUND=1
    set NODE_PATH="C:\Program Files\nodejs\node.exe"
    goto :node_found
)

:: Check Program Files (x86)
if exist "C:\Program Files (x86)\nodejs\node.exe" (
    set NODE_FOUND=1
    set NODE_PATH="C:\Program Files (x86)\nodejs\node.exe"
    goto :node_found
)

:: Check user directory
if exist "%USERPROFILE%\AppData\Local\Programs\nodejs\node.exe" (
    set NODE_FOUND=1
    set NODE_PATH="%USERPROFILE%\AppData\Local\Programs\nodejs\node.exe"
    goto :node_found
)

if %NODE_FOUND% equ 0 (
    echo ERROR: Node.js not found in PATH or common locations
    echo Please install Node.js from https://nodejs.org/
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

:node_found
echo ✓ Node.js found: 
%NODE_PATH% --version

:: Check if npm is available
echo.
echo [2/6] Checking npm availability...

:: Try to find npm in common locations
set NPM_FOUND=0
set NPM_CMD=

:: Check PATH first
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    set NPM_FOUND=1
    set NPM_CMD=npm
    goto :npm_found
)

:: Check Program Files
if exist "C:\Program Files\nodejs\npm.cmd" (
    set NPM_FOUND=1
    set NPM_CMD="C:\Program Files\nodejs\npm.cmd"
    goto :npm_found
)

:: Check Program Files (x86)
if exist "C:\Program Files (x86)\nodejs\npm.cmd" (
    set NPM_FOUND=1
    set NPM_CMD="C:\Program Files (x86)\nodejs\npm.cmd"
    goto :npm_found
)

:: Check user directory
if exist "%USERPROFILE%\AppData\Local\Programs\nodejs\npm.cmd" (
    set NPM_FOUND=1
    set NPM_CMD="%USERPROFILE%\AppData\Local\Programs\nodejs\npm.cmd"
    goto :npm_found
)

if %NPM_FOUND% equ 0 (
    echo ERROR: npm not found. Please reinstall Node.js
    pause
    exit /b 1
)

:npm_found
echo ✓ npm found:
%NPM_CMD% --version

:: Clean previous installation
echo.
echo [3/6] Cleaning previous installation...
if exist node_modules (
    echo Removing existing node_modules...
    rmdir /s /q node_modules
)
if exist package-lock.json (
    echo Removing package-lock.json...
    del package-lock.json
)

:: Install dependencies
echo.
echo [4/6] Installing dependencies...
%NPM_CMD% install --no-optional --no-audit --legacy-peer-deps
if %errorlevel% neq 0 (
    echo ERROR: Installation failed
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully

:: Security audit
echo.
echo [5/6] Running security audit...
%NPM_CMD% audit --audit-level=moderate
if %errorlevel% neq 0 (
    echo WARNING: Security vulnerabilities found
    echo Attempting to fix automatically...
    %NPM_CMD% audit fix --force
)

:: Build test
echo.
echo [6/6] Testing build process...
%NPM_CMD% run build
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo ✓ Build successful

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To start development server: npm run dev
echo To build for production: npm run build
echo.
pause 