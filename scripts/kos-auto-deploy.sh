#!/bin/bash

# Change to the project root (parent of this script)
cd "$(dirname "$0")/.." || exit 1

# KOS v1 Automated Deployment Script
# Zero-interaction installation with auto-detection and feature flag management

# set -e  # Commented out for debugging - prevents script from exiting on any error

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

# Function to pause and wait for user input (for debugging)
pause() {
    echo ""
    echo "Press Enter to continue..."
    read -r
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    echo "[DEBUG] Detecting OS..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if grep -q Microsoft /proc/version 2>/dev/null; then
            OS="wsl"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "msys"* ]]; then
        OS="windows"
    elif [[ "$OS" == "Windows_NT" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        # Fallback detection for Windows
        if [[ -n "$WINDIR" ]] || [[ -n "$windir" ]] || [[ -n "$COMSPEC" ]]; then
            OS="windows"
        else
            OS="unknown"
        fi
    fi
    print_status "Detected OS: $OS"
    echo "[DEBUG] OSTYPE: $OSTYPE"
    echo "[DEBUG] OS: $OS"
}

# Function to install Docker
install_docker() {
    print_status "Checking Docker installation..."
    
    if command_exists docker && command_exists docker-compose; then
        print_success "Docker and Docker Compose already installed"
        docker --version
        docker-compose --version
        return 0
    fi
    
    print_status "Installing Docker..."
    
    case $OS in
        "linux"|"wsl")
            # Install Docker on Linux
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            sudo usermod -aG docker $USER
            rm get-docker.sh
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "macos")
            print_warning "Please install Docker Desktop for macOS from https://www.docker.com/products/docker-desktop"
            return 1
            ;;
        "windows")
            print_warning "Please install Docker Desktop for Windows from https://www.docker.com/products/docker-desktop"
            return 1
            ;;
        *)
            print_error "Unsupported OS: $OS"
            return 1
            ;;
    esac
    
    print_success "Docker installed successfully"
}

# Function to detect Python and pip based on OS
detect_python() {
    echo "[DEBUG] Detecting Python and pip..."
    if [ -f "venv/bin/python" ]; then
        PYTHON_CMD="venv/bin/python"
        PIP_CMD="venv/bin/pip"
        echo "[INFO] Using venv Python: $PYTHON_CMD"
    else
        # On Windows/MSYS, try python first, then python3
        if [[ "$OS" == "windows" ]]; then
            if command -v python >/dev/null 2>&1; then
                PYTHON_CMD="python"
                PIP_CMD="pip"
                echo "[INFO] Using Windows Python: $PYTHON_CMD"
            elif command -v python3 >/dev/null 2>&1; then
                PYTHON_CMD="python3"
                PIP_CMD="pip3"
                echo "[INFO] Using Windows Python3: $PYTHON_CMD"
            else
                PYTHON_CMD="python"
                PIP_CMD="pip"
                echo "[INFO] Defaulting to Windows Python: $PYTHON_CMD"
            fi
        else
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
            echo "[INFO] Using system Python: $PYTHON_CMD"
        fi
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if Python is available
    echo "[DEBUG] Checking if $PYTHON_CMD exists..."
    if ! command_exists $PYTHON_CMD; then
        print_error "Python not found. Please install Python 3.8+"
        echo "[DEBUG] Python command '$PYTHON_CMD' not found in PATH"
        return 1
    fi
    
    # Install psutil for system detection
    print_status "Installing psutil for system detection..."
    echo "[DEBUG] Running: $PIP_CMD install psutil"
    $PIP_CMD install psutil
    if [ $? -ne 0 ]; then
        print_error "Failed to install psutil"
        echo "[DEBUG] pip install psutil failed with exit code $?"
        return 1
    fi
    
    print_success "Python dependencies installed"
}

# Function to generate environment files
generate_environment() {
    print_status "Generating environment configuration..."
    
    # Run the environment loader
    echo "[DEBUG] Running: $PYTHON_CMD scripts/env_loader.py"
    $PYTHON_CMD scripts/env_loader.py
    if [ $? -ne 0 ]; then
        print_error "Failed to generate environment configuration"
        echo "[DEBUG] env_loader.py failed with exit code $?"
        return 1
    fi
    
    print_success "Environment configuration generated"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    echo "[DEBUG] Creating directories..."
    mkdir -p vault dicom models plugins logs data tmp
    mkdir -p nginx/ssl
    mkdir -p monitoring
    
    print_success "Directories created"
}

# Function to start KOS v1
start_kos() {
    print_status "Starting KOS v1..."
    
    # Load environment variables
    if [ -f ".env" ]; then
        echo "[DEBUG] Loading .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "[DEBUG] No .env file found"
    fi
    
    # Start with docker-compose
    echo "[DEBUG] Running: docker-compose up -d"
    docker-compose up -d
    if [ $? -ne 0 ]; then
        print_error "Failed to start KOS v1"
        echo "[DEBUG] docker-compose up -d failed with exit code $?"
        return 1
    fi
    
    print_success "KOS v1 started successfully!"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to be ready
    echo "[DEBUG] Waiting 10 seconds for services to start..."
    sleep 10
    
    # Check API health
    echo "[DEBUG] Checking API health..."
    if curl -f http://localhost:${KOS_API_EXTERNAL_PORT:-8000}/health >/dev/null 2>&1; then
        print_success "API service is healthy"
    else
        print_warning "API service health check failed"
        echo "[DEBUG] API health check failed for port ${KOS_API_EXTERNAL_PORT:-8000}"
    fi
    
    # Check frontend
    echo "[DEBUG] Checking frontend health..."
    if curl -f http://localhost:${KOS_FRONTEND_EXTERNAL_PORT:-3000} >/dev/null 2>&1; then
        print_success "Frontend service is healthy"
    else
        print_warning "Frontend service health check failed"
        echo "[DEBUG] Frontend health check failed for port ${KOS_FRONTEND_EXTERNAL_PORT:-3000}"
    fi
}

# Function to display access information
display_access_info() {
    print_success "KOS v1 deployment completed!"
    echo ""
    echo "Access Information:"
    echo "=================="
    echo "Web Dashboard: http://localhost:${KOS_FRONTEND_EXTERNAL_PORT:-3000}"
    echo "API Documentation: http://localhost:${KOS_API_EXTERNAL_PORT:-8000}/docs"
    echo "API Health Check: http://localhost:${KOS_API_EXTERNAL_PORT:-8000}/health"
    echo "Container Monitoring: http://localhost:${KOS_CADVISOR_EXTERNAL_PORT:-8081}"
    echo "PostgreSQL: localhost:${KOS_POSTGRES_EXTERNAL_PORT:-5432}"
    echo "Redis: localhost:${KOS_REDIS_EXTERNAL_PORT:-6379}"
    echo "Weaviate: http://localhost:${KOS_WEAVIATE_EXTERNAL_PORT:-8082}"
    echo "MinIO Console: http://localhost:${KOS_MINIO_CONSOLE_EXTERNAL_PORT:-9001}"
    echo "Admin User: ${KOS_ADMIN_USER:-kos-admin}"
    echo "Admin Password: ${KOS_ADMIN_PASSWORD:-kos-30437}"
    echo ""
    echo "Useful Commands:"
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    echo "Restart services: docker-compose restart"
    echo "Update services: docker-compose pull && docker-compose up -d"
}

# Function to handle errors
handle_error() {
    print_error "Deployment failed at step: $1"
    print_error "Check the logs above for more information"
    echo ""
    echo "[DEBUG] Error occurred in command: $BASH_COMMAND"
    echo "[DEBUG] Exit code: $?"
    echo ""
    echo "Press Enter to exit..."
    read -r
    exit 1
}

# Main deployment function
main() {
    print_status "Starting KOS v1 automated deployment..."
    print_status "This will install and configure KOS v1 with zero user interaction"
    echo ""
    
    # Set error handling
    trap 'handle_error "$BASH_COMMAND"' ERR
    
    # Step 1: Detect OS
    detect_os
    
    # Step 2: Detect Python and pip
    detect_python
    
    echo "[DEBUG] Step 1: Create directories"
    create_directories
    
    echo "[DEBUG] Step 2: Install Python dependencies"
    install_python_deps
    if [ $? -ne 0 ]; then
        print_error "Python dependencies installation failed"
        pause
        return 1
    fi
    
    echo "[DEBUG] Step 3: Install Docker/check Docker installation"
    install_docker
    if [ $? -ne 0 ]; then
        print_error "Docker installation/check failed"
        pause
        return 1
    fi
    
    echo "[DEBUG] Step 4: Generate environment configuration"
    generate_environment
    if [ $? -ne 0 ]; then
        print_error "Environment configuration generation failed"
        pause
        return 1
    fi
    
    echo "[DEBUG] Step 5: Start KOS v1"
    start_kos
    if [ $? -ne 0 ]; then
        print_error "KOS v1 startup failed"
        pause
        return 1
    fi
    
    echo "[DEBUG] Step 6: Check health"
    check_health
    
    echo "[DEBUG] Step 7: Display access information"
    display_access_info
    
    print_success "KOS v1 deployment completed successfully!"
    echo ""
    echo "Press Enter to exit..."
    read -r
}

# Run main function
main "$@" 