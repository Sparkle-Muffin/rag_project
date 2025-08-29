#!/bin/bash

# RAG Project Helper Script
# A user-friendly wrapper for the Makefile commands

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to show help
show_help() {
    cat << EOF
🚀 RAG Project Helper Script

Usage: ./rag.sh [COMMAND]

Available Commands:
  setup           - Complete project setup (environment + Docker)
  start           - Start all services (Docker containers)
  stop            - Stop all services
  restart         - Restart all services
  status          - Check project status
  pipeline        - Run document processing pipeline
  test            - Run system tests
  app             - Launch Streamlit application
  clean           - Clean up generated files
  backup          - Create project backup
  install-bielik  - Install Bielik model in Ollama
  dev             - Run development workflow (format + lint + test)
  logs            - Show container logs
  help            - Show this help message

Examples:
  ./rag.sh setup      # First-time setup
  ./rag.sh start      # Start services
  ./rag.sh pipeline   # Process documents
  ./rag.sh app        # Launch app

For more detailed commands, use: make help
EOF
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if conda is available
check_conda() {
    if ! command -v conda >/dev/null 2>&1; then
        print_error "Conda is not installed or not in PATH."
        print_error "Please install Miniconda first: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
}

# Main command processing
case "${1:-help}" in
    "setup")
        print_header "Setting up RAG Project"
        check_conda
        check_docker
        print_status "Running complete setup..."
        make setup
        print_status "Setup complete! Next steps:"
        echo "  1. conda activate myenv"
        echo "  2. ./rag.sh pipeline"
        echo "  3. ./rag.sh app"
        ;;
    
    "start")
        print_header "Starting Services"
        check_docker
        make docker-start
        print_status "Services started successfully!"
        ;;
    
    "stop")
        print_header "Stopping Services"
        check_docker
        make docker-stop
        print_status "Services stopped successfully!"
        ;;
    
    "restart")
        print_header "Restarting Services"
        check_docker
        make docker-restart
        print_status "Services restarted successfully!"
        ;;
    
    "status")
        print_header "Project Status"
        make status
        ;;
    
    "pipeline")
        print_header "Running Document Pipeline"
        make run-pipeline
        print_status "Pipeline completed successfully!"
        ;;
    
    "test")
        print_header "Running Tests"
        make run-tests
        print_status "Tests completed! Check TEST_REPORT.md for results."
        ;;
    
    "app")
        print_header "Launching Application"
        make run-app
        ;;
    
    "clean")
        print_header "Cleaning Project"
        print_warning "This will remove all generated files and caches."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            make clean
            print_status "Cleanup completed!"
        else
            print_status "Cleanup cancelled."
        fi
        ;;
    
    "backup")
        print_header "Creating Backup"
        make backup
        ;;
    
    "install-bielik")
        print_header "Installing Bielik Model"
        check_docker
        make install-bielik
        ;;
    
    "dev")
        print_header "Development Workflow"
        make dev
        ;;
    
    "logs")
        print_header "Container Logs"
        check_docker
        make docker-logs
        ;;
    
    "help"|*)
        show_help
        ;;
esac 