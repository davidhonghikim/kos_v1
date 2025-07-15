#!/bin/bash

echo "========================================"
echo "KOS v1 Frontend - Automated Installation"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if Node.js is installed
echo "[1/6] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_error "Node.js not found"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
print_status "Node.js found: $(node --version)"

# Check if npm is available
echo
echo "[2/6] Checking npm availability..."
if ! command -v npm &> /dev/null; then
    print_error "npm not found"
    echo "Please reinstall Node.js"
    exit 1
fi
print_status "npm found: $(npm --version)"

# Clean previous installation
echo
echo "[3/6] Cleaning previous installation..."
if [ -d "node_modules" ]; then
    echo "Removing existing node_modules..."
    rm -rf node_modules
fi
if [ -f "package-lock.json" ]; then
    echo "Removing package-lock.json..."
    rm package-lock.json
fi

# Install dependencies
echo
echo "[4/6] Installing dependencies..."
if npm install --no-optional --no-audit --legacy-peer-deps; then
    print_status "Dependencies installed successfully"
else
    print_error "Installation failed"
    exit 1
fi

# Security audit
echo
echo "[5/6] Running security audit..."
if npm audit --audit-level=moderate; then
    print_status "No security vulnerabilities found"
else
    print_warning "Security vulnerabilities found"
    echo "Attempting to fix automatically..."
    npm audit fix --force
fi

# Build test
echo
echo "[6/6] Testing build process..."
if npm run build; then
    print_status "Build successful"
else
    print_error "Build failed"
    exit 1
fi

echo
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo
echo "To start development server: npm run dev"
echo "To build for production: npm run build"
echo 