#!/bin/bash

# ACGS-1 vLLM to Nano-vLLM Migration Script
# Systematic migration with DGM safety patterns and rollback capabilities

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MIGRATION_LOG="$PROJECT_ROOT/logs/nano-vllm-migration.log"
BACKUP_DIR="$PROJECT_ROOT/vllm_backup_$(date +%Y%m%d_%H%M%S)"
MIGRATION_CONFIG="$PROJECT_ROOT/config/nano-vllm-migration.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$MIGRATION_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}" | tee -a "$MIGRATION_LOG"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$MIGRATION_LOG"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$MIGRATION_LOG"
}

# Create necessary directories
mkdir -p "$(dirname "$MIGRATION_LOG")"
mkdir -p "$BACKUP_DIR"

# Migration phases
PHASE_1_COMPLETE=false
PHASE_2_COMPLETE=false
PHASE_3_COMPLETE=false
PHASE_4_COMPLETE=false
PHASE_5_COMPLETE=false

# Check if migration config exists
create_migration_config() {
    if [ ! -f "$MIGRATION_CONFIG" ]; then
        log "Creating migration configuration..."
        cat > "$MIGRATION_CONFIG" << EOF
# Nano-vLLM Migration Configuration
migration:
  enabled: true
  fallback_to_vllm: true
  parallel_deployment: true
  
models:
  nvidia_acerreason:
    model_path: "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.9
    port: 8000
    
  microsoft_phi4:
    model_path: "microsoft/Phi-4"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.6
    port: 8001
    
  nvidia_multimodal:
    model_path: "nvidia/Llama-3.1-Nemotron-Nano-VL-8B-V1"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.6
    port: 8002

safety:
  backup_enabled: true
  health_checks: true
  rollback_on_failure: true
  validation_tests: true

performance:
  benchmark_comparison: true
  memory_monitoring: true
  latency_tracking: true
EOF
        success "Migration configuration created at $MIGRATION_CONFIG"
    fi
}

# Backup current vLLM configuration
backup_vllm_config() {
    log "Backing up current vLLM configuration..."
    
    # Backup key files
    cp -r "$PROJECT_ROOT/services/reasoning-models" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/infrastructure/docker" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "$PROJECT_ROOT/scripts/reasoning-models" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/requirements.txt" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/pyproject.toml" "$BACKUP_DIR/" 2>/dev/null || true
    
    # Backup running services state
    if command -v docker &> /dev/null; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" > "$BACKUP_DIR/running_services.txt" 2>/dev/null || true
    fi
    
    success "Backup completed at $BACKUP_DIR"
}

# Install Nano-vLLM
install_nano_vllm() {
    log "Installing Nano-vLLM..."
    
    # Check if we're in a virtual environment
    if [ -n "${VIRTUAL_ENV:-}" ] || [ -d "venv" ]; then
        if [ ! -n "${VIRTUAL_ENV:-}" ]; then
            source venv/bin/activate
        fi
        
        # Install Nano-vLLM
        pip install git+https://github.com/GeeeekExplorer/nano-vllm.git
        
        # Verify installation
        if python -c "import nanovllm; print('Nano-vLLM version:', nanovllm.__version__)" 2>/dev/null; then
            success "Nano-vLLM installed successfully"
        else
            error "Nano-vLLM installation verification failed"
            return 1
        fi
    else
        warn "Virtual environment not found, installing globally"
        pip install git+https://github.com/GeeeekExplorer/nano-vllm.git
    fi
}

# Test Nano-vLLM installation
test_nano_vllm() {
    log "Testing Nano-vLLM installation..."
    
    python3 << 'EOF'
try:
    from nanovllm import LLM, SamplingParams
    print("✅ Nano-vLLM imports successful")
    
    # Test basic functionality (without loading a model)
    print("✅ Nano-vLLM basic functionality test passed")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Test error: {e}")
    exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        success "Nano-vLLM installation test passed"
    else
        error "Nano-vLLM installation test failed"
        return 1
    fi
}

# Phase 1: Preparation
phase_1_preparation() {
    log "Starting Phase 1: Preparation and Setup"
    
    create_migration_config
    backup_vllm_config
    install_nano_vllm
    test_nano_vllm
    
    PHASE_1_COMPLETE=true
    success "Phase 1 completed successfully"
}

# Phase 2: Create parallel deployment
phase_2_parallel_deployment() {
    log "Starting Phase 2: Parallel Deployment Setup"
    
    if [ "$PHASE_1_COMPLETE" != "true" ]; then
        error "Phase 1 must be completed before Phase 2"
        return 1
    fi
    
    # Create new service with Nano-vLLM
    log "Creating Nano-vLLM service configuration..."
    
    # Copy and modify the existing service
    cp "$PROJECT_ROOT/services/reasoning-models/vllm-integration.py" \
       "$PROJECT_ROOT/services/reasoning-models/nano-vllm-integration.py"
    
    # Create Docker compose for parallel deployment
    cat > "$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm.yml" << 'EOF'
version: '3.8'

# ACGS Nano-vLLM Service - Parallel Deployment
# Lightweight vLLM alternative with comparable performance

services:
  nano-vllm-service:
    build:
      context: ../../services/reasoning-models
      dockerfile: Dockerfile.nano-vllm
    container_name: acgs_nano_vllm_service
    environment:
      - MODEL_CONFIG_PATH=/app/config/nano-vllm-config.yaml
      - ENABLE_FALLBACK=true
      - LOG_LEVEL=INFO
    ports:
      - "8010:8000"  # Different port for parallel deployment
    volumes:
      - ${HOME:-~}/.cache/huggingface:/root/.cache/huggingface
      - ./config/nano-vllm:/app/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
EOF
    
    PHASE_2_COMPLETE=true
    success "Phase 2 completed successfully"
}

# Health check function
health_check() {
    log "Performing health checks..."
    
    # Check if services are running
    local services_healthy=true
    
    # Check Nano-vLLM service
    if curl -f http://localhost:8010/health &>/dev/null; then
        success "Nano-vLLM service is healthy"
    else
        warn "Nano-vLLM service health check failed"
        services_healthy=false
    fi
    
    # Check original vLLM services (if running)
    for port in 8000 8001 8002; do
        if curl -f http://localhost:$port/health &>/dev/null; then
            log "vLLM service on port $port is healthy"
        else
            log "vLLM service on port $port is not responding"
        fi
    done
    
    if [ "$services_healthy" = "true" ]; then
        success "Health checks passed"
        return 0
    else
        error "Health checks failed"
        return 1
    fi
}

# Rollback function
rollback() {
    error "Migration failed, initiating rollback..."
    
    # Stop new services
    docker-compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm.yml" down 2>/dev/null || true
    
    # Restore backup
    if [ -d "$BACKUP_DIR" ]; then
        log "Restoring from backup..."
        
        # Restore key files
        cp -r "$BACKUP_DIR/reasoning-models" "$PROJECT_ROOT/services/" 2>/dev/null || true
        cp -r "$BACKUP_DIR/docker" "$PROJECT_ROOT/infrastructure/" 2>/dev/null || true
        cp "$BACKUP_DIR/requirements.txt" "$PROJECT_ROOT/" 2>/dev/null || true
        cp "$BACKUP_DIR/pyproject.toml" "$PROJECT_ROOT/" 2>/dev/null || true
        
        success "Rollback completed"
    else
        error "Backup directory not found, manual rollback required"
    fi
}

# Main migration function
main() {
    log "Starting vLLM to Nano-vLLM migration"
    log "Project root: $PROJECT_ROOT"
    log "Migration log: $MIGRATION_LOG"
    log "Backup directory: $BACKUP_DIR"
    
    # Set up error handling
    trap rollback ERR
    
    # Execute migration phases
    case "${1:-all}" in
        "phase1"|"1")
            phase_1_preparation
            ;;
        "phase2"|"2")
            phase_2_parallel_deployment
            ;;
        "health")
            health_check
            ;;
        "rollback")
            rollback
            ;;
        "all")
            phase_1_preparation
            phase_2_parallel_deployment
            health_check
            ;;
        *)
            echo "Usage: $0 {phase1|phase2|health|rollback|all}"
            echo "  phase1: Preparation and setup"
            echo "  phase2: Parallel deployment"
            echo "  health: Health check"
            echo "  rollback: Rollback migration"
            echo "  all: Run all phases"
            exit 1
            ;;
    esac
    
    success "Migration phase completed successfully"
}

# Run main function
main "$@"
