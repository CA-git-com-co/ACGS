#!/bin/bash

# ACGS-PGP Legacy Frontend Migration Control Script
# This script helps manage the migration phases and feature flag configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
PHASES=("phase1" "phase2" "phase3")
CURRENT_ENV_FILE="$PROJECT_DIR/.env"
BACKUP_DIR="$PROJECT_DIR/.env.backups"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}ACGS-PGP Migration Control${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_success "Created backup directory: $BACKUP_DIR"
    fi
}

# Backup current .env file
backup_current_env() {
    if [ -f "$CURRENT_ENV_FILE" ]; then
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="$BACKUP_DIR/.env.backup.$timestamp"
        cp "$CURRENT_ENV_FILE" "$backup_file"
        print_success "Backed up current .env to: $backup_file"
    fi
}

# Get current phase
get_current_phase() {
    if [ -f "$CURRENT_ENV_FILE" ]; then
        grep "REACT_APP_MIGRATION_PHASE=" "$CURRENT_ENV_FILE" | cut -d'=' -f2 | tr -d '"' || echo "unknown"
    else
        echo "none"
    fi
}

# Validate phase
validate_phase() {
    local phase=$1
    for valid_phase in "${PHASES[@]}"; do
        if [ "$phase" = "$valid_phase" ]; then
            return 0
        fi
    done
    return 1
}

# Set migration phase
set_phase() {
    local phase=$1
    
    if ! validate_phase "$phase"; then
        print_error "Invalid phase: $phase"
        print_info "Valid phases: ${PHASES[*]}"
        exit 1
    fi
    
    local phase_file="$PROJECT_DIR/.env.migration.$phase"
    
    if [ ! -f "$phase_file" ]; then
        print_error "Phase configuration file not found: $phase_file"
        exit 1
    fi
    
    print_info "Setting migration phase to: $phase"
    
    # Create backup
    create_backup_dir
    backup_current_env
    
    # Copy phase configuration
    cp "$phase_file" "$CURRENT_ENV_FILE"
    print_success "Applied $phase configuration"
    
    # Validate configuration
    validate_configuration
}

# Validate configuration
validate_configuration() {
    print_info "Validating configuration..."
    
    # Check required environment variables
    local required_vars=(
        "REACT_APP_MIGRATION_PHASE"
        "REACT_APP_AUTH_API_URL"
        "REACT_APP_AC_API_URL"
        "REACT_APP_GS_API_URL"
        "REACT_APP_SOLANA_NETWORK"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$CURRENT_ENV_FILE"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_success "Configuration validation passed"
    else
        print_error "Missing required variables: ${missing_vars[*]}"
        exit 1
    fi
}

# Emergency rollback
emergency_rollback() {
    print_warning "EMERGENCY ROLLBACK INITIATED"
    
    # Set all feature flags to false
    local emergency_env="$PROJECT_DIR/.env.emergency"
    
    cat > "$emergency_env" << EOF
# EMERGENCY ROLLBACK CONFIGURATION
REACT_APP_MIGRATION_PHASE=emergency
REACT_APP_EMERGENCY_ROLLBACK=true
REACT_APP_LEGACY_MODE=true

# Disable all shared components
REACT_APP_USE_SHARED_THEME=false
REACT_APP_USE_SHARED_AUTH=false
REACT_APP_USE_SHARED_LAYOUT=false
REACT_APP_USE_SHARED_ERROR_HANDLING=false
REACT_APP_USE_SHARED_DASHBOARD=false
REACT_APP_USE_SHARED_QUANTUMAGI=false
REACT_APP_USE_SHARED_MONITORING=false
REACT_APP_USE_SHARED_CONSULTATION=false
REACT_APP_USE_SHARED_AMENDMENT=false
REACT_APP_USE_SHARED_PAGES=false
REACT_APP_USE_SHARED_ROUTING=false

# ACGS Service URLs
REACT_APP_AUTH_API_URL=http://localhost:8002/api/v1
REACT_APP_AC_API_URL=http://localhost:8001/api/v1
REACT_APP_INTEGRITY_API_URL=http://localhost:8006/api/v1
REACT_APP_FV_API_URL=http://localhost:8004/api/v1
REACT_APP_GS_API_URL=http://localhost:8003/api/v1
REACT_APP_PGC_API_URL=http://localhost:8005/api/v1
REACT_APP_EC_API_URL=http://localhost:8007/api/v1

# Solana Configuration
REACT_APP_SOLANA_NETWORK=devnet
REACT_APP_SOLANA_RPC_URL=https://api.devnet.solana.com
EOF
    
    # Backup current and apply emergency config
    create_backup_dir
    backup_current_env
    cp "$emergency_env" "$CURRENT_ENV_FILE"
    
    print_success "Emergency rollback configuration applied"
    print_warning "All shared components disabled - system running in pure legacy mode"
}

# Show current status
show_status() {
    local current_phase=$(get_current_phase)
    
    echo "Current Migration Status:"
    echo "========================"
    echo "Phase: $current_phase"
    
    if [ -f "$CURRENT_ENV_FILE" ]; then
        echo
        echo "Feature Flags:"
        grep "REACT_APP_USE_SHARED" "$CURRENT_ENV_FILE" | while read -r line; do
            local flag=$(echo "$line" | cut -d'=' -f1 | sed 's/REACT_APP_USE_SHARED_//')
            local value=$(echo "$line" | cut -d'=' -f2)
            if [ "$value" = "true" ]; then
                echo -e "  ${GREEN}✓${NC} $flag"
            else
                echo -e "  ${RED}✗${NC} $flag"
            fi
        done
        
        echo
        echo "Emergency Controls:"
        local emergency=$(grep "REACT_APP_EMERGENCY_ROLLBACK=" "$CURRENT_ENV_FILE" | cut -d'=' -f2)
        local maintenance=$(grep "REACT_APP_MAINTENANCE_MODE=" "$CURRENT_ENV_FILE" | cut -d'=' -f2)
        
        if [ "$emergency" = "true" ]; then
            echo -e "  ${RED}⚠ EMERGENCY ROLLBACK ACTIVE${NC}"
        fi
        
        if [ "$maintenance" = "true" ]; then
            echo -e "  ${YELLOW}⚠ MAINTENANCE MODE ACTIVE${NC}"
        fi
    else
        print_warning "No .env file found"
    fi
}

# Test configuration
test_configuration() {
    print_info "Testing configuration..."
    
    # Test ACGS services
    local services=(
        "AUTH:$REACT_APP_AUTH_API_URL"
        "AC:$REACT_APP_AC_API_URL"
        "GS:$REACT_APP_GS_API_URL"
    )
    
    for service in "${services[@]}"; do
        local name=$(echo "$service" | cut -d':' -f1)
        local url=$(echo "$service" | cut -d':' -f2)
        
        if curl -s --max-time 5 "$url/health" > /dev/null 2>&1; then
            print_success "$name service: OK"
        else
            print_warning "$name service: Not responding"
        fi
    done
    
    # Test Solana connectivity
    if curl -s --max-time 5 "https://api.devnet.solana.com" > /dev/null 2>&1; then
        print_success "Solana devnet: OK"
    else
        print_warning "Solana devnet: Not responding"
    fi
}

# Main script logic
main() {
    print_header
    
    case "${1:-}" in
        "set")
            if [ -z "${2:-}" ]; then
                print_error "Usage: $0 set <phase>"
                print_info "Available phases: ${PHASES[*]}"
                exit 1
            fi
            set_phase "$2"
            ;;
        "status")
            show_status
            ;;
        "test")
            test_configuration
            ;;
        "rollback")
            emergency_rollback
            ;;
        "help"|"--help"|"-h")
            echo "Usage: $0 <command> [options]"
            echo
            echo "Commands:"
            echo "  set <phase>    Set migration phase (${PHASES[*]})"
            echo "  status         Show current migration status"
            echo "  test           Test service connectivity"
            echo "  rollback       Emergency rollback to legacy mode"
            echo "  help           Show this help message"
            echo
            ;;
        *)
            print_error "Unknown command: ${1:-}"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
