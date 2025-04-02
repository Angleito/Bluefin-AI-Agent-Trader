#!/usr/bin/env bash

set -euo pipefail

# Deployment script for Bluefin AI Agent Trader
# Supports different deployment environments

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENVIRONMENT="${1:-production}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="${PROJECT_ROOT}/logs"
DEPLOY_LOG="${LOG_DIR}/deploy_${ENVIRONMENT}_${TIMESTAMP}.log"

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${DEPLOY_LOG}"
}

# Function to handle errors
handle_error() {
    log "ERROR: $*"
    exit 1
}

# Validate environment
validate_environment() {
    case "${ENVIRONMENT}" in
        production|staging|development)
            log "Deploying to ${ENVIRONMENT} environment"
            ;;
        *)
            handle_error "Invalid environment. Use production, staging, or development."
            ;;
    esac
}

# Prepare deployment
prepare_deployment() {
    log "Preparing deployment..."
    
    # Check for required tools
    command -v nix >/dev/null 2>&1 || handle_error "Nix is not installed"
    command -v docker >/dev/null 2>&1 || handle_error "Docker is not installed"
    
    # Update Nix channels
    nix-channel --update
}

# Build Nix packages
build_packages() {
    log "Building Nix packages..."
    nix build ".#bluefin-trader" || handle_error "Nix build failed"
}

# Build Docker image
build_docker_image() {
    log "Building Docker image..."
    docker build -f "${PROJECT_ROOT}/docker/Dockerfile.nix" -t bluefin-ai-agent-trader:"${ENVIRONMENT}" "${PROJECT_ROOT}" || handle_error "Docker build failed"
}

# Deploy application
deploy_application() {
    log "Deploying application..."
    
    case "${ENVIRONMENT}" in
        production)
            docker-compose -f "${PROJECT_ROOT}/docker/docker-compose.nix.yml" up -d || handle_error "Docker Compose deployment failed"
            ;;
        staging)
            docker-compose -f "${PROJECT_ROOT}/docker/docker-compose.nix.yml" up || handle_error "Docker Compose deployment failed"
            ;;
        development)
            nix develop || handle_error "Nix development environment setup failed"
            ;;
    esac
}

# Main deployment workflow
main() {
    log "Starting Bluefin AI Agent Trader deployment"
    
    validate_environment
    prepare_deployment
    build_packages
    build_docker_image
    deploy_application
    
    log "Deployment completed successfully"
}

# Run main function with error handling
main "$@" 2>&1 | tee -a "${DEPLOY_LOG}"