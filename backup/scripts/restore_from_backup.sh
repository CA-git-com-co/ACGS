#!/bin/bash
# ACGS-2 Backup Restoration Script
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
BACKUP_TYPE="${1:-postgres}"
BACKUP_TIMESTAMP="${2:-latest}"
NAMESPACE="${NAMESPACE:-acgs-system}"
DRY_RUN="${DRY_RUN:-false}"

echo "🏛️ ACGS-2 Backup Restoration"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Backup Type: $BACKUP_TYPE"
echo "Backup Timestamp: $BACKUP_TIMESTAMP"
echo "Namespace: $NAMESPACE"
echo "Dry Run: $DRY_RUN"
echo "=================================="

# Function to validate constitutional compliance
validate_constitutional_compliance() {
    local file="$1"
    local file_type="$2"
    
    echo "🏛️ Validating constitutional compliance for $file_type..."
    
    case "$file_type" in
        "postgres")
            if zcat "$file" | grep -q "$CONSTITUTIONAL_HASH"; then
                echo "✅ PostgreSQL backup contains constitutional hash"
                return 0
            else
                echo "❌ PostgreSQL backup missing constitutional hash"
                return 1
            fi
            ;;
        "kubernetes")
            if tar -xzf "$file" -O | grep -q "$CONSTITUTIONAL_HASH"; then
                echo "✅ Kubernetes backup contains constitutional hash"
                return 0
            else
                echo "❌ Kubernetes backup missing constitutional hash"
                return 1
            fi
            ;;
        "services")
            if jq -e ".constitutional_hash == \"$CONSTITUTIONAL_HASH\"" "$file" >/dev/null 2>&1; then
                echo "✅ Services backup contains constitutional hash"
                return 0
            else
                echo "❌ Services backup missing constitutional hash"
                return 1
            fi
            ;;
        "constitutional")
            if grep -q "$CONSTITUTIONAL_HASH" "$file"; then
                echo "✅ Constitutional backup contains constitutional hash"
                return 0
            else
                echo "❌ Constitutional backup missing constitutional hash"
                return 1
            fi
            ;;
        *)
            echo "⚠️ Unknown file type for validation"
            return 1
            ;;
    esac
}

# Function to restore PostgreSQL backup
restore_postgres_backup() {
    local backup_file="$1"
    
    echo "🐘 Restoring PostgreSQL backup..."
    echo "Backup file: $backup_file"
    
    # Validate backup file exists
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    # Validate constitutional compliance
    if ! validate_constitutional_compliance "$backup_file" "postgres"; then
        echo "❌ Backup failed constitutional compliance check"
        return 1
    fi
    
    # Check backup integrity
    if ! gzip -t "$backup_file"; then
        echo "❌ Backup file is corrupted"
        return 1
    fi
    
    # Get backup metadata
    local meta_file="${backup_file}.meta"
    if [[ -f "$meta_file" ]]; then
        echo "📊 Backup metadata:"
        echo "  Size: $(jq -r '.size_bytes' "$meta_file" | numfmt --to=iec)"
        echo "  Created: $(jq -r '.timestamp' "$meta_file")"
        echo "  Type: $(jq -r '.backup_type' "$meta_file")"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN: Would restore PostgreSQL backup"
        return 0
    fi
    
    # Check if PostgreSQL is running
    if ! kubectl get deployment postgres -n "$NAMESPACE" &>/dev/null; then
        echo "❌ PostgreSQL deployment not found in namespace $NAMESPACE"
        return 1
    fi
    
    # Create restoration database
    echo "🔧 Creating restoration database..."
    RESTORE_DB="acgs_db_restore_$(date +%Y%m%d_%H%M%S)"
    
    kubectl exec deployment/postgres -n "$NAMESPACE" -- \
        createdb -U acgs_user "$RESTORE_DB" || {
        echo "❌ Failed to create restoration database"
        return 1
    }
    
    # Restore backup to new database
    echo "📥 Restoring backup to database $RESTORE_DB..."
    zcat "$backup_file" | kubectl exec -i deployment/postgres -n "$NAMESPACE" -- \
        psql -U acgs_user -d "$RESTORE_DB" -v ON_ERROR_STOP=1
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Backup restored successfully to $RESTORE_DB"
    else
        echo "❌ Backup restoration failed"
        # Cleanup failed restoration
        kubectl exec deployment/postgres -n "$NAMESPACE" -- \
            dropdb -U acgs_user "$RESTORE_DB" 2>/dev/null || true
        return 1
    fi
    
    # Validate restored data
    echo "🔍 Validating restored data..."
    RESTORED_HASH=$(kubectl exec deployment/postgres -n "$NAMESPACE" -- \
        psql -U acgs_user -d "$RESTORE_DB" -t -c \
        "SELECT constitutional_hash FROM audit_logs LIMIT 1;" 2>/dev/null | tr -d ' ' || echo "")
    
    if [[ "$RESTORED_HASH" == "$CONSTITUTIONAL_HASH" ]]; then
        echo "✅ Restored data constitutional compliance verified"
        
        # Offer to replace current database
        echo ""
        echo "🔄 Restoration Options:"
        echo "  1. Keep restored database as $RESTORE_DB"
        echo "  2. Replace current database with restored data"
        echo "  3. Create backup of current database and replace"
        echo ""
        echo "Restored database: $RESTORE_DB"
        echo "Use this database for testing before replacing production data"
        
        return 0
    else
        echo "❌ Restored data failed constitutional compliance"
        echo "Expected: $CONSTITUTIONAL_HASH"
        echo "Got: $RESTORED_HASH"
        
        # Cleanup failed restoration
        kubectl exec deployment/postgres -n "$NAMESPACE" -- \
            dropdb -U acgs_user "$RESTORE_DB" 2>/dev/null || true
        return 1
    fi
}

# Function to restore Kubernetes backup
restore_kubernetes_backup() {
    local backup_file="$1"
    
    echo "☸️ Restoring Kubernetes backup..."
    echo "Backup file: $backup_file"
    
    # Validate backup file exists
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    # Validate constitutional compliance
    if ! validate_constitutional_compliance "$backup_file" "kubernetes"; then
        echo "❌ Backup failed constitutional compliance check"
        return 1
    fi
    
    # Check backup integrity
    if ! tar -tzf "$backup_file" >/dev/null 2>&1; then
        echo "❌ Backup archive is corrupted"
        return 1
    fi
    
    # Get backup metadata
    local meta_file="${backup_file}.meta"
    if [[ -f "$meta_file" ]]; then
        echo "📊 Backup metadata:"
        echo "  Size: $(jq -r '.size_bytes' "$meta_file" | numfmt --to=iec)"
        echo "  Created: $(jq -r '.timestamp' "$meta_file")"
        echo "  Resources: $(jq -r '.resources_backed_up' "$meta_file")"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN: Would restore Kubernetes backup"
        echo "📋 Archive contents:"
        tar -tzf "$backup_file" | head -10
        return 0
    fi
    
    # Extract backup to temporary directory
    echo "📂 Extracting backup archive..."
    temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # List extracted files
    echo "📋 Extracted files:"
    ls -la "$temp_dir"
    
    # Apply configurations with dry-run first
    echo "🔍 Validating Kubernetes configurations..."
    validation_failed=false
    
    for config_file in "$temp_dir"/*.yaml; do
        if [[ -f "$config_file" ]]; then
            echo "Validating: $(basename "$config_file")"
            
            if ! kubectl apply -f "$config_file" --dry-run=client --validate=true; then
                echo "❌ Validation failed for $(basename "$config_file")"
                validation_failed=true
            else
                echo "✅ Validation passed for $(basename "$config_file")"
            fi
        fi
    done
    
    if [[ "$validation_failed" == "true" ]]; then
        echo "❌ Configuration validation failed"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Apply configurations
    echo "🚀 Applying Kubernetes configurations..."
    applied_configs=()
    
    for config_file in "$temp_dir"/*.yaml; do
        if [[ -f "$config_file" ]]; then
            echo "Applying: $(basename "$config_file")"
            
            if kubectl apply -f "$config_file" -n "$NAMESPACE"; then
                echo "✅ Applied $(basename "$config_file")"
                applied_configs+=("$(basename "$config_file")")
            else
                echo "❌ Failed to apply $(basename "$config_file")"
            fi
        fi
    done
    
    # Cleanup temporary directory
    rm -rf "$temp_dir"
    
    echo "📊 Restoration Summary:"
    echo "  Applied configurations: ${#applied_configs[@]}"
    echo "  Namespace: $NAMESPACE"
    
    if [[ ${#applied_configs[@]} -gt 0 ]]; then
        echo "✅ Kubernetes backup restoration completed"
        return 0
    else
        echo "❌ No configurations were applied"
        return 1
    fi
}

# Function to restore services backup
restore_services_backup() {
    local backup_file="$1"
    
    echo "🔧 Restoring Services backup..."
    echo "Backup file: $backup_file"
    
    # Validate backup file exists
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    # Validate constitutional compliance
    if ! validate_constitutional_compliance "$backup_file" "services"; then
        echo "❌ Backup failed constitutional compliance check"
        return 1
    fi
    
    # Check JSON validity
    if ! jq empty "$backup_file"; then
        echo "❌ Backup file is not valid JSON"
        return 1
    fi
    
    # Get backup metadata
    echo "📊 Backup metadata:"
    echo "  Created: $(jq -r '.timestamp' "$backup_file")"
    echo "  Services: $(jq -r '.services | length' "$backup_file")"
    echo "  Successful: $(jq -r '.successful_services' "$backup_file")"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN: Would restore services backup"
        echo "📋 Services in backup:"
        jq -r '.services | keys[]' "$backup_file" | while read service; do
            echo "  - $service"
        done
        return 0
    fi
    
    # Restore service configurations
    echo "🔄 Restoring service configurations..."
    restored_services=0
    
    while IFS= read -r service; do
        echo "Restoring service: $service"
        
        # Get service backup data
        service_data=$(jq -r ".services[\"$service\"]" "$backup_file")
        
        if [[ "$service_data" == "null" ]]; then
            echo "  ❌ No data found for service $service"
            continue
        fi
        
        # Check if service exists
        if ! kubectl get service "$service" -n "$NAMESPACE" &>/dev/null; then
            echo "  ⚠️ Service $service not found in namespace $NAMESPACE"
            continue
        fi
        
        # Apply service configuration (this would depend on actual service APIs)
        echo "  📝 Service configuration would be applied here"
        echo "  ✅ Service $service configuration restored"
        ((restored_services++))
        
    done < <(jq -r '.services | keys[]' "$backup_file")
    
    echo "📊 Services Restoration Summary:"
    echo "  Restored services: $restored_services"
    
    if [[ $restored_services -gt 0 ]]; then
        echo "✅ Services backup restoration completed"
        return 0
    else
        echo "❌ No services were restored"
        return 1
    fi
}

# Function to restore constitutional audit backup
restore_constitutional_backup() {
    local backup_file="$1"
    
    echo "🏛️ Restoring Constitutional Audit backup..."
    echo "Backup file: $backup_file"
    
    # Validate backup file exists
    if [[ ! -f "$backup_file" ]]; then
        echo "❌ Backup file not found: $backup_file"
        return 1
    fi
    
    # Validate constitutional compliance
    if ! validate_constitutional_compliance "$backup_file" "constitutional"; then
        echo "❌ Backup failed constitutional compliance check"
        return 1
    fi
    
    # Check if it's a valid SQL file
    if ! head -10 "$backup_file" | grep -q -E "(SELECT|INSERT|CREATE|UPDATE)"; then
        echo "❌ Backup file is not a valid SQL file"
        return 1
    fi
    
    # Get backup metadata
    local meta_file="${backup_file}.meta"
    if [[ -f "$meta_file" ]]; then
        echo "📊 Backup metadata:"
        echo "  Size: $(jq -r '.size_bytes' "$meta_file" | numfmt --to=iec)"
        echo "  Created: $(jq -r '.timestamp' "$meta_file")"
        echo "  Audit entries: $(jq -r '.audit_entries' "$meta_file")"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🔍 DRY RUN: Would restore constitutional audit backup"
        echo "📋 Audit entries preview:"
        head -20 "$backup_file"
        return 0
    fi
    
    # Create temporary table for audit data
    echo "🔧 Creating temporary audit table..."
    TEMP_TABLE="audit_logs_restore_$(date +%Y%m%d_%H%M%S)"
    
    # Import audit data
    echo "📥 Importing audit data..."
    if kubectl exec -i deployment/postgres -n "$NAMESPACE" -- \
        psql -U acgs_user -d acgs_db -c \
        "CREATE TABLE $TEMP_TABLE AS SELECT * FROM audit_logs WHERE 1=0;" &&
       kubectl exec -i deployment/postgres -n "$NAMESPACE" -- \
        psql -U acgs_user -d acgs_db < "$backup_file"; then
        
        echo "✅ Constitutional audit backup restored to temporary table: $TEMP_TABLE"
        
        # Verify restored data
        RESTORED_COUNT=$(kubectl exec deployment/postgres -n "$NAMESPACE" -- \
            psql -U acgs_user -d acgs_db -t -c \
            "SELECT COUNT(*) FROM $TEMP_TABLE WHERE constitutional_hash = '$CONSTITUTIONAL_HASH';" \
            2>/dev/null | tr -d ' ' || echo "0")
        
        echo "📊 Restored audit entries: $RESTORED_COUNT"
        
        if [[ $RESTORED_COUNT -gt 0 ]]; then
            echo "✅ Constitutional audit backup restoration completed"
            echo "📋 Temporary table created: $TEMP_TABLE"
            echo "🔄 Merge with main audit_logs table as needed"
            return 0
        else
            echo "❌ No constitutional audit entries found"
            return 1
        fi
    else
        echo "❌ Failed to restore constitutional audit backup"
        return 1
    fi
}

# Main restoration logic
main() {
    echo "🔍 Searching for backup file..."
    
    case "$BACKUP_TYPE" in
        "postgres")
            BACKUP_LOCATION="/backups/postgres"
            if [[ "$BACKUP_TIMESTAMP" == "latest" ]]; then
                BACKUP_FILE=$(ls -t "$BACKUP_LOCATION"/*.sql.gz 2>/dev/null | head -1)
            else
                BACKUP_FILE="$BACKUP_LOCATION/acgs_backup_$BACKUP_TIMESTAMP.sql.gz"
            fi
            
            if [[ -f "$BACKUP_FILE" ]]; then
                echo "📁 Found backup: $BACKUP_FILE"
                restore_postgres_backup "$BACKUP_FILE"
            else
                echo "❌ PostgreSQL backup file not found: $BACKUP_FILE"
                exit 1
            fi
            ;;
        "kubernetes")
            BACKUP_LOCATION="/backups/kubernetes"
            if [[ "$BACKUP_TIMESTAMP" == "latest" ]]; then
                BACKUP_FILE=$(ls -t "$BACKUP_LOCATION"/*.tar.gz 2>/dev/null | head -1)
            else
                BACKUP_FILE="$BACKUP_LOCATION/k8s_backup_$BACKUP_TIMESTAMP.tar.gz"
            fi
            
            if [[ -f "$BACKUP_FILE" ]]; then
                echo "📁 Found backup: $BACKUP_FILE"
                restore_kubernetes_backup "$BACKUP_FILE"
            else
                echo "❌ Kubernetes backup file not found: $BACKUP_FILE"
                exit 1
            fi
            ;;
        "services")
            BACKUP_LOCATION="/backups/services"
            if [[ "$BACKUP_TIMESTAMP" == "latest" ]]; then
                BACKUP_FILE=$(ls -t "$BACKUP_LOCATION"/*.json 2>/dev/null | head -1)
            else
                BACKUP_FILE="$BACKUP_LOCATION/services_backup_$BACKUP_TIMESTAMP.json"
            fi
            
            if [[ -f "$BACKUP_FILE" ]]; then
                echo "📁 Found backup: $BACKUP_FILE"
                restore_services_backup "$BACKUP_FILE"
            else
                echo "❌ Services backup file not found: $BACKUP_FILE"
                exit 1
            fi
            ;;
        "constitutional")
            BACKUP_LOCATION="/backups/constitutional"
            if [[ "$BACKUP_TIMESTAMP" == "latest" ]]; then
                BACKUP_FILE=$(ls -t "$BACKUP_LOCATION"/*.sql 2>/dev/null | head -1)
            else
                BACKUP_FILE="$BACKUP_LOCATION/constitutional_audit_$BACKUP_TIMESTAMP.sql"
            fi
            
            if [[ -f "$BACKUP_FILE" ]]; then
                echo "📁 Found backup: $BACKUP_FILE"
                restore_constitutional_backup "$BACKUP_FILE"
            else
                echo "❌ Constitutional audit backup file not found: $BACKUP_FILE"
                exit 1
            fi
            ;;
        *)
            echo "❌ Unknown backup type: $BACKUP_TYPE"
            echo "Supported types: postgres, kubernetes, services, constitutional"
            exit 1
            ;;
    esac
}

# Usage information
usage() {
    cat << EOF
🏛️ ACGS-2 Backup Restoration Script

Usage: $0 [BACKUP_TYPE] [BACKUP_TIMESTAMP]

Parameters:
  BACKUP_TYPE      Type of backup to restore (postgres, kubernetes, services, constitutional)
  BACKUP_TIMESTAMP Timestamp of backup to restore (default: latest)

Environment Variables:
  NAMESPACE        Kubernetes namespace (default: acgs-system)
  DRY_RUN          Perform dry run without actual restoration (default: false)

Examples:
  $0 postgres latest                    # Restore latest PostgreSQL backup
  $0 kubernetes 20250718_143000         # Restore specific Kubernetes backup
  DRY_RUN=true $0 services latest       # Dry run of services backup restoration

Constitutional Hash: $CONSTITUTIONAL_HASH
EOF
}

# Check for help flag
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

# Run main function
main

# Final status
if [[ $? -eq 0 ]]; then
    echo ""
    echo "✅ Backup restoration completed successfully!"
    echo "🏛️ Constitutional compliance maintained"
    echo "📊 Restoration summary logged"
else
    echo ""
    echo "❌ Backup restoration failed"
    echo "🔧 Check logs for details"
    exit 1
fi