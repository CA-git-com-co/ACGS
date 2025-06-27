#!/bin/bash

# ACGS-PGP Backup and Restore Operations
# Handles database backups, configuration backups, and disaster recovery

set -e

NAMESPACE="acgs-system"
BACKUP_DIR="/var/backups/acgs-pgp"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_backup() { echo -e "${BLUE}[BACKUP]${NC} $1"; }

# Create backup directory structure
setup_backup_dirs() {
    log_info "Setting up backup directories..."
    mkdir -p "$BACKUP_DIR"/{database,configs,secrets,monitoring}
    log_info "Backup directories created at: $BACKUP_DIR"
}

# Backup CockroachDB database
backup_database() {
    log_backup "Starting CockroachDB backup..."
    
    local backup_file="$BACKUP_DIR/database/cockroachdb_backup_$TIMESTAMP.sql"
    
    # Get CockroachDB pod
    local db_pod=$(kubectl get pods -n $NAMESPACE -l app=cockroachdb -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -z "$db_pod" ]]; then
        log_error "CockroachDB pod not found"
        return 1
    fi
    
    # Create database backup
    kubectl exec -n $NAMESPACE $db_pod -- cockroach dump acgs_db --insecure > "$backup_file"
    
    # Compress backup
    gzip "$backup_file"
    
    log_backup "Database backup completed: ${backup_file}.gz"
    return 0
}

# Backup Kubernetes configurations
backup_configurations() {
    log_backup "Starting configuration backup..."
    
    local config_backup_dir="$BACKUP_DIR/configs/$TIMESTAMP"
    mkdir -p "$config_backup_dir"
    
    # Backup all deployments
    kubectl get deployments -n $NAMESPACE -o yaml > "$config_backup_dir/deployments.yaml"
    
    # Backup all services
    kubectl get services -n $NAMESPACE -o yaml > "$config_backup_dir/services.yaml"
    
    # Backup all configmaps
    kubectl get configmaps -n $NAMESPACE -o yaml > "$config_backup_dir/configmaps.yaml"
    
    # Backup persistent volumes
    kubectl get pv -o yaml > "$config_backup_dir/persistent-volumes.yaml"
    
    # Backup persistent volume claims
    kubectl get pvc -n $NAMESPACE -o yaml > "$config_backup_dir/persistent-volume-claims.yaml"
    
    # Create archive
    tar -czf "$BACKUP_DIR/configs/acgs_configs_$TIMESTAMP.tar.gz" -C "$config_backup_dir" .
    rm -rf "$config_backup_dir"
    
    log_backup "Configuration backup completed: acgs_configs_$TIMESTAMP.tar.gz"
    return 0
}

# Backup secrets (encrypted)
backup_secrets() {
    log_backup "Starting secrets backup..."
    
    local secrets_file="$BACKUP_DIR/secrets/secrets_$TIMESTAMP.yaml"
    
    # Backup secrets
    kubectl get secrets -n $NAMESPACE -o yaml > "$secrets_file"
    
    # Encrypt secrets file
    if command -v gpg &> /dev/null; then
        gpg --symmetric --cipher-algo AES256 "$secrets_file"
        rm "$secrets_file"
        log_backup "Secrets backup completed (encrypted): secrets_$TIMESTAMP.yaml.gpg"
    else
        log_warn "GPG not available - secrets backup not encrypted"
        log_backup "Secrets backup completed: secrets_$TIMESTAMP.yaml"
    fi
    
    return 0
}

# Backup monitoring data
backup_monitoring() {
    log_backup "Starting monitoring backup..."
    
    local monitoring_dir="$BACKUP_DIR/monitoring/$TIMESTAMP"
    mkdir -p "$monitoring_dir"
    
    # Backup Prometheus configuration
    kubectl get configmap prometheus-config -n $NAMESPACE -o yaml > "$monitoring_dir/prometheus-config.yaml" 2>/dev/null || true
    
    # Backup Grafana dashboards
    kubectl get configmap grafana-dashboards -n $NAMESPACE -o yaml > "$monitoring_dir/grafana-dashboards.yaml" 2>/dev/null || true
    
    # Backup alerting rules
    kubectl get prometheusrule -n $NAMESPACE -o yaml > "$monitoring_dir/prometheus-rules.yaml" 2>/dev/null || true
    
    # Create archive
    tar -czf "$BACKUP_DIR/monitoring/monitoring_$TIMESTAMP.tar.gz" -C "$monitoring_dir" .
    rm -rf "$monitoring_dir"
    
    log_backup "Monitoring backup completed: monitoring_$TIMESTAMP.tar.gz"
    return 0
}

# Restore database from backup
restore_database() {
    local backup_file=$1
    
    if [[ -z "$backup_file" ]]; then
        log_error "Backup file not specified"
        return 1
    fi
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_backup "Starting database restore from: $backup_file"
    
    # Get CockroachDB pod
    local db_pod=$(kubectl get pods -n $NAMESPACE -l app=cockroachdb -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -z "$db_pod" ]]; then
        log_error "CockroachDB pod not found"
        return 1
    fi
    
    # Decompress if needed
    local restore_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        restore_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$restore_file"
    fi
    
    # Restore database
    kubectl exec -i -n $NAMESPACE $db_pod -- cockroach sql --insecure < "$restore_file"
    
    # Clean up temporary file
    if [[ "$backup_file" == *.gz ]]; then
        rm "$restore_file"
    fi
    
    log_backup "Database restore completed"
    return 0
}

# Restore configurations
restore_configurations() {
    local config_archive=$1
    
    if [[ -z "$config_archive" ]]; then
        log_error "Configuration archive not specified"
        return 1
    fi
    
    if [[ ! -f "$config_archive" ]]; then
        log_error "Configuration archive not found: $config_archive"
        return 1
    fi
    
    log_backup "Starting configuration restore from: $config_archive"
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    
    # Extract archive
    tar -xzf "$config_archive" -C "$temp_dir"
    
    # Apply configurations
    kubectl apply -f "$temp_dir/deployments.yaml"
    kubectl apply -f "$temp_dir/services.yaml"
    kubectl apply -f "$temp_dir/configmaps.yaml"
    
    # Clean up
    rm -rf "$temp_dir"
    
    log_backup "Configuration restore completed"
    return 0
}

# Validate backup integrity
validate_backup() {
    local backup_date=${1:-$TIMESTAMP}
    
    log_backup "Validating backup integrity for: $backup_date"
    
    local validation_errors=0
    
    # Check database backup
    if [[ -f "$BACKUP_DIR/database/cockroachdb_backup_${backup_date}.sql.gz" ]]; then
        if gzip -t "$BACKUP_DIR/database/cockroachdb_backup_${backup_date}.sql.gz"; then
            log_info "✓ Database backup integrity verified"
        else
            log_error "✗ Database backup corrupted"
            ((validation_errors++))
        fi
    else
        log_warn "⚠ Database backup not found"
    fi
    
    # Check configuration backup
    if [[ -f "$BACKUP_DIR/configs/acgs_configs_${backup_date}.tar.gz" ]]; then
        if tar -tzf "$BACKUP_DIR/configs/acgs_configs_${backup_date}.tar.gz" >/dev/null; then
            log_info "✓ Configuration backup integrity verified"
        else
            log_error "✗ Configuration backup corrupted"
            ((validation_errors++))
        fi
    else
        log_warn "⚠ Configuration backup not found"
    fi
    
    # Check monitoring backup
    if [[ -f "$BACKUP_DIR/monitoring/monitoring_${backup_date}.tar.gz" ]]; then
        if tar -tzf "$BACKUP_DIR/monitoring/monitoring_${backup_date}.tar.gz" >/dev/null; then
            log_info "✓ Monitoring backup integrity verified"
        else
            log_error "✗ Monitoring backup corrupted"
            ((validation_errors++))
        fi
    else
        log_warn "⚠ Monitoring backup not found"
    fi
    
    if [[ $validation_errors -eq 0 ]]; then
        log_backup "Backup validation completed successfully"
        return 0
    else
        log_error "Backup validation failed with $validation_errors errors"
        return 1
    fi
}

# Emergency backup (quick backup for emergency situations)
emergency_backup() {
    log_backup "Starting emergency backup..."
    
    local emergency_dir="$BACKUP_DIR/emergency/emergency_$TIMESTAMP"
    mkdir -p "$emergency_dir"
    
    # Quick configuration backup
    kubectl get all -n $NAMESPACE -o yaml > "$emergency_dir/all-resources.yaml"
    
    # Constitutional hash verification
    echo "$CONSTITUTIONAL_HASH" > "$emergency_dir/constitutional_hash.txt"
    
    # Current system state
    kubectl get pods -n $NAMESPACE -o wide > "$emergency_dir/pod-status.txt"
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' > "$emergency_dir/events.txt"
    
    # Create emergency archive
    tar -czf "$BACKUP_DIR/emergency/emergency_$TIMESTAMP.tar.gz" -C "$emergency_dir" .
    rm -rf "$emergency_dir"
    
    log_backup "Emergency backup completed: emergency_$TIMESTAMP.tar.gz"
    return 0
}

# Main function
main() {
    local action=${1:-"backup"}
    
    case $action in
        "backup")
            log_info "Starting full ACGS-PGP backup..."
            setup_backup_dirs
            backup_database
            backup_configurations
            backup_secrets
            backup_monitoring
            validate_backup
            log_info "Full backup completed successfully"
            ;;
        "restore-db")
            restore_database "$2"
            ;;
        "restore-config")
            restore_configurations "$2"
            ;;
        "validate")
            validate_backup "$2"
            ;;
        "emergency")
            emergency_backup
            ;;
        *)
            echo "Usage: $0 {backup|restore-db|restore-config|validate|emergency} [file]"
            echo "  backup          - Full system backup"
            echo "  restore-db      - Restore database from backup file"
            echo "  restore-config  - Restore configurations from archive"
            echo "  validate        - Validate backup integrity"
            echo "  emergency       - Quick emergency backup"
            exit 1
            ;;
    esac
}

main "$@"
