#!/bin/bash

# ACGS-1 Configuration Migration Script
# Migrate all vLLM configurations to Nano-vLLM equivalents

set -euo pipefail

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MIGRATION_LOG="$PROJECT_ROOT/logs/config-migration.log"
BACKUP_DIR="$PROJECT_ROOT/config_backup_$(date +%Y%m%d_%H%M%S)"

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

# Backup configurations
backup_configurations() {
    log "Backing up existing configurations..."
    
    # Backup config directories
    if [ -d "$PROJECT_ROOT/config" ]; then
        cp -r "$PROJECT_ROOT/config" "$BACKUP_DIR/"
    fi
    
    # Backup Docker configurations
    if [ -d "$PROJECT_ROOT/infrastructure/docker" ]; then
        cp -r "$PROJECT_ROOT/infrastructure/docker" "$BACKUP_DIR/"
    fi
    
    # Backup deployment scripts
    if [ -d "$PROJECT_ROOT/scripts" ]; then
        cp -r "$PROJECT_ROOT/scripts" "$BACKUP_DIR/"
    fi
    
    success "Configuration backup completed at $BACKUP_DIR"
}

# Update Docker Compose files
update_docker_compose() {
    log "Updating Docker Compose configurations..."
    
    # Find all docker-compose files
    find "$PROJECT_ROOT" -name "docker-compose*.yml" -type f | while read -r compose_file; do
        if grep -q "vllm" "$compose_file"; then
            log "Updating $compose_file"
            
            # Create backup
            cp "$compose_file" "$compose_file.backup"
            
            # Replace vLLM image references with Nano-vLLM
            sed -i 's|vllm/vllm-openai:latest|acgs-nano-vllm:latest|g' "$compose_file"
            
            # Update port mappings (if needed)
            sed -i 's|8007:8000|8000:8000|g' "$compose_file"
            sed -i 's|8008:8000|8001:8001|g' "$compose_file"
            sed -i 's|8009:8000|8002:8002|g' "$compose_file"
            
            # Add Nano-vLLM specific environment variables
            if grep -q "environment:" "$compose_file"; then
                # Add Nano-vLLM specific vars after existing environment section
                sed -i '/environment:/a\      - NANO_VLLM_MODE=enabled\n      - FALLBACK_TO_VLLM=true' "$compose_file"
            fi
            
            success "Updated $compose_file"
        fi
    done
}

# Update Kubernetes deployments
update_kubernetes_configs() {
    log "Updating Kubernetes configurations..."
    
    # Find all k8s deployment files
    find "$PROJECT_ROOT" -name "*.yaml" -path "*/k8s/*" -type f | while read -r k8s_file; do
        if grep -q "vllm\|llm" "$k8s_file"; then
            log "Updating $k8s_file"
            
            # Create backup
            cp "$k8s_file" "$k8s_file.backup"
            
            # Update image references
            sed -i 's|vllm/vllm-openai:latest|acgs-nano-vllm:latest|g' "$k8s_file"
            
            # Update resource limits (Nano-vLLM uses less resources)
            sed -i 's|memory: 32G|memory: 8G|g' "$k8s_file"
            sed -i 's|memory: 16G|memory: 4G|g' "$k8s_file"
            sed -i 's|cpu: 8000m|cpu: 2000m|g' "$k8s_file"
            sed -i 's|cpu: 4000m|cpu: 1000m|g' "$k8s_file"
            
            success "Updated $k8s_file"
        fi
    done
}

# Update environment files
update_environment_files() {
    log "Updating environment configurations..."
    
    # Find all .env files
    find "$PROJECT_ROOT" -name ".env*" -type f | while read -r env_file; do
        if grep -q "VLLM\|vllm" "$env_file"; then
            log "Updating $env_file"
            
            # Create backup
            cp "$env_file" "$env_file.backup"
            
            # Update vLLM references
            sed -i 's|VLLM_|NANO_VLLM_|g' "$env_file"
            sed -i 's|vllm_|nano_vllm_|g' "$env_file"
            
            # Add Nano-vLLM specific variables
            echo "" >> "$env_file"
            echo "# Nano-vLLM Configuration" >> "$env_file"
            echo "NANO_VLLM_ENABLED=true" >> "$env_file"
            echo "NANO_VLLM_FALLBACK=true" >> "$env_file"
            echo "NANO_VLLM_PORT=8000" >> "$env_file"
            
            success "Updated $env_file"
        fi
    done
}

# Update deployment scripts
update_deployment_scripts() {
    log "Updating deployment scripts..."
    
    # Find all deployment scripts
    find "$PROJECT_ROOT/scripts" -name "*.sh" -type f | while read -r script_file; do
        if grep -q "vllm\|VLLM" "$script_file" && [[ "$script_file" != *"migrate"* ]]; then
            log "Updating $script_file"
            
            # Create backup
            cp "$script_file" "$script_file.backup"
            
            # Update vLLM command references
            sed -i 's|vllm serve|nano-vllm-service.py|g' "$script_file"
            sed -i 's|--gpu-memory-utilization|# --gpu-memory-utilization (handled by Nano-vLLM)|g' "$script_file"
            sed -i 's|--tensor-parallel-size|# --tensor-parallel-size (handled by Nano-vLLM)|g' "$script_file"
            
            # Update port references
            sed -i 's|:8007|:8000|g' "$script_file"
            sed -i 's|:8008|:8001|g' "$script_file"
            sed -i 's|:8009|:8002|g' "$script_file"
            
            success "Updated $script_file"
        fi
    done
}

# Create Nano-vLLM specific configurations
create_nano_vllm_configs() {
    log "Creating Nano-vLLM specific configurations..."
    
    # Create main Nano-vLLM config directory
    mkdir -p "$PROJECT_ROOT/config/nano-vllm"
    
    # Create production configuration
    cat > "$PROJECT_ROOT/config/nano-vllm/production.yaml" << 'EOF'
# Nano-vLLM Production Configuration
service:
  name: "nano-vllm-reasoning"
  version: "1.0.0"
  environment: "production"

models:
  nvidia_acerreason:
    model_path: "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.9
    max_model_len: 32768
    port: 8000
    specialties: ["governance", "accountability"]
    
  microsoft_phi4:
    model_path: "microsoft/Phi-4"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.6
    max_model_len: 16384
    port: 8001
    specialties: ["ethics", "fairness"]

constitutional:
  principles_file: "/app/constitutional/principles.yaml"
  compliance_threshold: 0.85
  reasoning_depth: "deep"
  require_citations: true

performance:
  max_concurrent_requests: 20
  request_timeout: 120
  health_check_interval: 30
  
logging:
  level: "INFO"
  format: "structured"
  file: "/app/logs/nano-vllm-production.log"

monitoring:
  metrics_enabled: true
  prometheus_port: 9090
  health_endpoint: "/health"
EOF

    # Create development configuration
    cat > "$PROJECT_ROOT/config/nano-vllm/development.yaml" << 'EOF'
# Nano-vLLM Development Configuration
service:
  name: "nano-vllm-reasoning"
  version: "1.0.0"
  environment: "development"

models:
  nvidia_acerreason:
    model_path: "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.7
    max_model_len: 16384
    port: 8000
    specialties: ["governance", "accountability"]
    
  microsoft_phi4:
    model_path: "microsoft/Phi-4"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.5
    max_model_len: 8192
    port: 8001
    specialties: ["ethics", "fairness"]

constitutional:
  principles_file: "/app/constitutional/principles.yaml"
  compliance_threshold: 0.75
  reasoning_depth: "standard"
  require_citations: false

performance:
  max_concurrent_requests: 5
  request_timeout: 60
  health_check_interval: 30
  
logging:
  level: "DEBUG"
  format: "structured"
  file: "/app/logs/nano-vllm-development.log"

monitoring:
  metrics_enabled: true
  prometheus_port: 9090
  health_endpoint: "/health"
EOF

    success "Created Nano-vLLM configurations"
}

# Validate configurations
validate_configurations() {
    log "Validating migrated configurations..."
    
    local validation_errors=0
    
    # Check if required config files exist
    required_configs=(
        "$PROJECT_ROOT/config/nano-vllm/production.yaml"
        "$PROJECT_ROOT/config/nano-vllm/development.yaml"
        "$PROJECT_ROOT/config/constitutional/principles.yaml"
    )
    
    for config_file in "${required_configs[@]}"; do
        if [ ! -f "$config_file" ]; then
            error "Missing required configuration: $config_file"
            ((validation_errors++))
        else
            log "✓ Found: $config_file"
        fi
    done
    
    # Check if Docker Compose files are valid
    find "$PROJECT_ROOT" -name "docker-compose*.yml" -type f | while read -r compose_file; do
        if command -v docker-compose &> /dev/null; then
            if ! docker-compose -f "$compose_file" config &> /dev/null; then
                error "Invalid Docker Compose file: $compose_file"
                ((validation_errors++))
            else
                log "✓ Valid Docker Compose: $compose_file"
            fi
        fi
    done
    
    if [ $validation_errors -eq 0 ]; then
        success "Configuration validation passed"
        return 0
    else
        error "Configuration validation failed with $validation_errors errors"
        return 1
    fi
}

# Main migration function
main() {
    log "Starting configuration migration to Nano-vLLM"
    log "Project root: $PROJECT_ROOT"
    log "Migration log: $MIGRATION_LOG"
    log "Backup directory: $BACKUP_DIR"
    
    case "${1:-all}" in
        "backup")
            backup_configurations
            ;;
        "docker")
            update_docker_compose
            ;;
        "k8s")
            update_kubernetes_configs
            ;;
        "env")
            update_environment_files
            ;;
        "scripts")
            update_deployment_scripts
            ;;
        "configs")
            create_nano_vllm_configs
            ;;
        "validate")
            validate_configurations
            ;;
        "all")
            backup_configurations
            update_docker_compose
            update_kubernetes_configs
            update_environment_files
            update_deployment_scripts
            create_nano_vllm_configs
            validate_configurations
            ;;
        *)
            echo "Usage: $0 {backup|docker|k8s|env|scripts|configs|validate|all}"
            echo "  backup:   Backup existing configurations"
            echo "  docker:   Update Docker Compose files"
            echo "  k8s:      Update Kubernetes configurations"
            echo "  env:      Update environment files"
            echo "  scripts:  Update deployment scripts"
            echo "  configs:  Create Nano-vLLM configurations"
            echo "  validate: Validate migrated configurations"
            echo "  all:      Run all migration steps"
            exit 1
            ;;
    esac
    
    success "Configuration migration completed successfully"
}

# Run main function
main "$@"
