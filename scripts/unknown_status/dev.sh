#!/bin/bash

# KOS v1 - Cross-Platform Development Script
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

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please run setup script first."
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm not found. Please run setup script first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please run setup script first."
        exit 1
    fi
    
    print_success "All dependencies found"
}

# Start backend in development mode
start_backend() {
    print_status "Starting backend in development mode..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Start backend with auto-reload
    python -m uvicorn backend.main:app --host 0.0.0.0 --port "${KOS_API_INTERNAL_PORT:-8000}" --reload &
    BACKEND_PID=$!
    print_success "Backend started (PID: $BACKEND_PID)"
}

# Start frontend in development mode
start_frontend() {
    print_status "Starting frontend in development mode..."
    
    cd frontend
    
    # Start frontend with Vite
    npm run dev -- --port "${KOS_FRONTEND_INTERNAL_PORT:-5173}" &
    FRONTEND_PID=$!
    print_success "Frontend started (PID: $FRONTEND_PID)"
    
    cd ..
}

# Start with Docker
start_docker() {
    print_status "Starting with Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose up --build
    else
        print_error "Docker Compose not found"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend stopped"
    fi
    
    exit 0
}

# Trap cleanup on exit
trap cleanup SIGINT SIGTERM

# Main function
main() {
    detect_os
    check_dependencies
    
    # Parse command line arguments
    case "${1:-dev}" in
        "docker")
            start_docker
            ;;
        "backend")
            start_backend
            wait $BACKEND_PID
            ;;
        "frontend")
            start_frontend
            wait $FRONTEND_PID
            ;;
        "dev"|*)
            print_status "Starting development environment..."
            start_backend
            sleep 2
            start_frontend
            
            print_success "Development environment started!"
            print_status "Backend: http://localhost:${KOS_API_INTERNAL_PORT:-8000}"
            print_status "Frontend: http://localhost:${KOS_FRONTEND_INTERNAL_PORT:-5173}"
            print_status "Press Ctrl+C to stop"
            
            # Wait for both processes
            wait $BACKEND_PID $FRONTEND_PID
            ;;
    esac
}

# Show usage
show_usage() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes:"
    echo "  dev      - Start both backend and frontend in development mode (default)"
    echo "  docker   - Start with Docker Compose"
    echo "  backend  - Start only backend"
    echo "  frontend - Start only frontend"
    echo ""
    echo "Examples:"
    echo "  $0        # Start development environment"
    echo "  $0 docker # Start with Docker"
    echo "  $0 backend # Start only backend"
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# Run main function
main "$@" 