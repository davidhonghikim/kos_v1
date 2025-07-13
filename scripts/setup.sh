#!/bin/bash

# KOS v1 - Cross-Platform Setup Script
# Supports Linux, macOS, and Windows (WSL)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if grep -q Microsoft /proc/version 2>/dev/null; then
            OS="wsl"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_status "Detected OS: $OS"
}

# Install Node.js and npm
install_nodejs() {
    print_status "Installing Node.js and npm..."
    
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        print_success "Node.js and npm already installed"
        node --version
        npm --version
        return 0
    fi
    
    case $OS in
        "linux"|"wsl")
            # Install NVM for Linux/WSL
            if ! command -v nvm &> /dev/null; then
                print_status "Installing NVM..."
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            fi
            nvm install 18
            nvm use 18
            nvm alias default 18
            ;;
        "macos")
            # Install NVM for macOS
            if ! command -v nvm &> /dev/null; then
                print_status "Installing NVM..."
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            fi
            nvm install 18
            nvm use 18
            nvm alias default 18
            ;;
        "windows")
            print_warning "Please install Node.js manually from https://nodejs.org/"
            return 1
            ;;
        *)
            print_error "Unsupported OS: $OS"
            return 1
            ;;
    esac
    
    print_success "Node.js and npm installed successfully"
}

# Install Python dependencies
install_python() {
    print_status "Setting up Python environment..."
    
    if command -v python3 &> /dev/null; then
        print_success "Python 3 found"
        python3 --version
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        return 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Install frontend dependencies
install_frontend() {
    print_status "Installing frontend dependencies..."
    
    cd frontend
    
    # Install npm dependencies
    if [ -f "package.json" ]; then
        npm install
        print_success "Frontend dependencies installed"
    else
        print_error "package.json not found in frontend directory"
        return 1
    fi
    
    cd ..
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p vault dicom models plugins logs
    mkdir -p nginx/ssl
    mkdir -p monitoring
    
    print_success "Directories created"
}

# Setup Docker (if available)
setup_docker() {
    print_status "Checking Docker availability..."
    
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        print_success "Docker and Docker Compose found"
        docker --version
        docker-compose --version
    else
        print_warning "Docker not found. Please install Docker and Docker Compose"
        print_warning "Visit: https://docs.docker.com/get-docker/"
    fi
}

# Main setup function
main() {
    print_status "Starting KOS v1 setup..."
    
    detect_os
    create_directories
    install_nodejs
    install_python
    install_frontend
    setup_docker
    
    print_success "Setup completed successfully!"
    print_status "Next steps:"
    echo "  1. Run 'docker-compose up' to start the application"
    echo "  2. Or run 'npm run dev' in the frontend directory for development"
    echo "  3. Or run 'python -m uvicorn backend.main:app --reload' for backend development"
}

# Run main function
main "$@" 