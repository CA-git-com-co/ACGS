#!/bin/bash
# ACGS-2 Backup Validation Script
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
BACKUP_LOCATIONS=(
    "/backups/postgres"
    "/backups/kubernetes"
    "/backups/services"
    "/backups/constitutional"
)

echo "🏛️ ACGS-2 Backup Validation"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Timestamp: $(date --iso-8601=seconds)"
echo "============================="

# Initialize counters
TOTAL_BACKUPS=0
VALID_BACKUPS=0
COMPLIANT_BACKUPS=0
TOTAL_SIZE=0
FAILED_VALIDATIONS=()

# Validation functions
validate_postgres_backup() {
    local backup_file="$1"
    local is_valid=true
    
    echo "  🐘 Validating PostgreSQL backup: $(basename "$backup_file")"
    
    # Check file size
    local file_size=$(stat -c%s "$backup_file")
    if [[ $file_size -lt 1024 ]]; then
        echo "    ❌ File too small ($file_size bytes)"
        is_valid=false
    fi
    
    # Check gzip integrity
    if ! gzip -t "$backup_file" 2>/dev/null; then
        echo "    ❌ Gzip integrity check failed"
        is_valid=false
    fi
    
    # Check PostgreSQL dump format
    if ! zcat "$backup_file" | head -10 | grep -q "PostgreSQL database dump"; then
        echo "    ❌ Not a valid PostgreSQL dump"
        is_valid=false
    fi
    
    # Check constitutional hash
    if zcat "$backup_file" | grep -q "$CONSTITUTIONAL_HASH"; then
        echo "    🏛️ Constitutional hash verified"
        ((COMPLIANT_BACKUPS++))
    else
        echo "    ❌ Constitutional hash not found"
        is_valid=false
    fi
    
    if [[ "$is_valid" == "true" ]]; then
        echo "    ✅ Valid PostgreSQL backup"
        ((VALID_BACKUPS++))
    else
        FAILED_VALIDATIONS+=("$(basename "$backup_file")")
    fi
    
    TOTAL_SIZE=$((TOTAL_SIZE + file_size))
}

validate_kubernetes_backup() {
    local backup_file="$1"
    local is_valid=true
    
    echo "  ☸️ Validating Kubernetes backup: $(basename "$backup_file")"
    
    # Check file size
    local file_size=$(stat -c%s "$backup_file")
    if [[ $file_size -lt 1024 ]]; then
        echo "    ❌ File too small ($file_size bytes)"
        is_valid=false
    fi
    
    # Check tar.gz integrity
    if ! tar -tzf "$backup_file" >/dev/null 2>&1; then
        echo "    ❌ Tar archive integrity check failed"
        is_valid=false
    fi
    
    # Check for YAML content
    if ! tar -xzf "$backup_file" -O | head -50 | grep -q "apiVersion:"; then
        echo "    ❌ No valid Kubernetes YAML found"
        is_valid=false
    fi
    
    # Check constitutional hash
    if tar -xzf "$backup_file" -O | grep -q "$CONSTITUTIONAL_HASH"; then
        echo "    🏛️ Constitutional hash verified"
        ((COMPLIANT_BACKUPS++))
    else
        echo "    ❌ Constitutional hash not found"
        is_valid=false
    fi
    
    if [[ "$is_valid" == "true" ]]; then
        echo "    ✅ Valid Kubernetes backup"
        ((VALID_BACKUPS++))
    else
        FAILED_VALIDATIONS+=("$(basename "$backup_file")")
    fi
    
    TOTAL_SIZE=$((TOTAL_SIZE + file_size))
}

validate_services_backup() {
    local backup_file="$1"
    local is_valid=true
    
    echo "  🔧 Validating Services backup: $(basename "$backup_file")"
    
    # Check file size
    local file_size=$(stat -c%s "$backup_file")
    if [[ $file_size -lt 100 ]]; then
        echo "    ❌ File too small ($file_size bytes)"
        is_valid=false
    fi
    
    # Check JSON format
    if ! jq empty "$backup_file" 2>/dev/null; then
        echo "    ❌ Invalid JSON format"
        is_valid=false
    fi
    
    # Check constitutional hash
    if jq -e ".constitutional_hash == \"$CONSTITUTIONAL_HASH\"" "$backup_file" >/dev/null 2>&1; then
        echo "    🏛️ Constitutional hash verified"
        ((COMPLIANT_BACKUPS++))
    else
        echo "    ❌ Constitutional hash not found or invalid"
        is_valid=false
    fi
    
    # Check service data
    local service_count=$(jq -r '.services | length' "$backup_file" 2>/dev/null || echo "0")
    if [[ $service_count -gt 0 ]]; then
        echo "    📊 Services backed up: $service_count"
    else
        echo "    ⚠️ No services found in backup"
    fi
    
    if [[ "$is_valid" == "true" ]]; then
        echo "    ✅ Valid Services backup"
        ((VALID_BACKUPS++))
    else
        FAILED_VALIDATIONS+=("$(basename "$backup_file")")
    fi
    
    TOTAL_SIZE=$((TOTAL_SIZE + file_size))
}

validate_constitutional_backup() {
    local backup_file="$1"
    local is_valid=true
    
    echo "  🏛️ Validating Constitutional backup: $(basename "$backup_file")"
    
    # Check file size
    local file_size=$(stat -c%s "$backup_file")
    if [[ $file_size -lt 100 ]]; then
        echo "    ❌ File too small ($file_size bytes)"
        is_valid=false
    fi
    
    # Check SQL format
    if ! head -10 "$backup_file" | grep -q -E "(SELECT|INSERT|CREATE|UPDATE)"; then
        echo "    ❌ Not a valid SQL file"
        is_valid=false
    fi
    
    # Check constitutional hash
    if grep -q "$CONSTITUTIONAL_HASH" "$backup_file"; then
        echo "    🏛️ Constitutional hash verified"
        ((COMPLIANT_BACKUPS++))
    else
        echo "    ❌ Constitutional hash not found"
        is_valid=false
    fi
    
    # Count audit entries
    local audit_count=$(grep -c "audit_logs" "$backup_file" 2>/dev/null || echo "0")
    if [[ $audit_count -gt 0 ]]; then
        echo "    📊 Audit entries: $audit_count"
    else
        echo "    ⚠️ No audit entries found"
    fi
    
    if [[ "$is_valid" == "true" ]]; then
        echo "    ✅ Valid Constitutional backup"
        ((VALID_BACKUPS++))
    else
        FAILED_VALIDATIONS+=("$(basename "$backup_file")")
    fi
    
    TOTAL_SIZE=$((TOTAL_SIZE + file_size))
}

validate_metadata_file() {
    local meta_file="$1"
    local is_valid=true
    
    echo "  📄 Validating metadata: $(basename "$meta_file")"
    
    # Check JSON format
    if ! jq empty "$meta_file" 2>/dev/null; then
        echo "    ❌ Invalid JSON format"
        return 1
    fi
    
    # Check required fields
    local required_fields=("constitutional_hash" "timestamp" "backup_type" "size_bytes")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$meta_file" >/dev/null 2>&1; then
            echo "    ❌ Missing required field: $field"
            is_valid=false
        fi
    done
    
    # Check constitutional hash
    local meta_hash=$(jq -r '.constitutional_hash' "$meta_file" 2>/dev/null)
    if [[ "$meta_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        echo "    ❌ Constitutional hash mismatch in metadata"
        is_valid=false
    fi
    
    # Check retention date
    local retention_date=$(jq -r '.retention_until' "$meta_file" 2>/dev/null)
    if [[ -n "$retention_date" ]]; then
        if date -d "$retention_date" >/dev/null 2>&1; then
            echo "    📅 Retention until: $retention_date"
        else
            echo "    ⚠️ Invalid retention date format"
        fi
    fi
    
    if [[ "$is_valid" == "true" ]]; then
        echo "    ✅ Valid metadata file"
        return 0
    else
        return 1
    fi
}

# Main validation loop
for location in "${BACKUP_LOCATIONS[@]}"; do
    echo ""
    echo "📁 Validating backups in: $location"
    
    if [[ ! -d "$location" ]]; then
        echo "  ❌ Backup location does not exist"
        continue
    fi
    
    backup_count=0
    location_valid=0
    
    # Process backup files
    for backup_file in "$location"/*; do
        if [[ -f "$backup_file" ]] && [[ ! "$backup_file" =~ \.meta$ ]]; then
            ((backup_count++))
            ((TOTAL_BACKUPS++))
            
            # Validate based on location and file type
            case "$location" in
                */postgres)
                    if [[ "$backup_file" =~ \.sql\.gz$ ]]; then
                        validate_postgres_backup "$backup_file"
                    fi
                    ;;
                */kubernetes)
                    if [[ "$backup_file" =~ \.tar\.gz$ ]]; then
                        validate_kubernetes_backup "$backup_file"
                    fi
                    ;;
                */services)
                    if [[ "$backup_file" =~ \.json$ ]]; then
                        validate_services_backup "$backup_file"
                    fi
                    ;;
                */constitutional)
                    if [[ "$backup_file" =~ \.sql$ ]]; then
                        validate_constitutional_backup "$backup_file"
                    fi
                    ;;
            esac
            
            # Validate metadata file if exists
            meta_file="${backup_file}.meta"
            if [[ -f "$meta_file" ]]; then
                validate_metadata_file "$meta_file"
            else
                echo "  ⚠️ No metadata file for: $(basename "$backup_file")"
            fi
        fi
    done
    
    echo "  📊 Location summary: $backup_count backup(s) processed"
done

# Generate validation report
echo ""
echo "📊 BACKUP VALIDATION SUMMARY"
echo "============================="
echo "Validation timestamp: $(date --iso-8601=seconds)"
echo "Constitutional hash: $CONSTITUTIONAL_HASH"
echo ""
echo "Backup Statistics:"
echo "  Total backups validated: $TOTAL_BACKUPS"
echo "  Valid backups: $VALID_BACKUPS"
echo "  Constitutionally compliant: $COMPLIANT_BACKUPS"
echo "  Total backup size: $((TOTAL_SIZE / 1024 / 1024)) MB"
echo ""
echo "Validation Results:"
echo "  Validity rate: $((TOTAL_BACKUPS > 0 ? VALID_BACKUPS * 100 / TOTAL_BACKUPS : 0))%"
echo "  Compliance rate: $((TOTAL_BACKUPS > 0 ? COMPLIANT_BACKUPS * 100 / TOTAL_BACKUPS : 0))%"

# List failed validations
if [[ ${#FAILED_VALIDATIONS[@]} -gt 0 ]]; then
    echo ""
    echo "❌ Failed Validations:"
    for failed in "${FAILED_VALIDATIONS[@]}"; do
        echo "  - $failed"
    done
fi

# Health check recommendations
echo ""
echo "🩺 HEALTH CHECK RECOMMENDATIONS"
echo "==============================="

if [[ $TOTAL_BACKUPS -eq 0 ]]; then
    echo "🚨 CRITICAL: No backups found!"
    echo "   - Check backup scheduling and execution"
    echo "   - Verify backup storage locations"
    echo "   - Review backup orchestrator logs"
elif [[ $COMPLIANT_BACKUPS -lt $TOTAL_BACKUPS ]]; then
    echo "⚠️ WARNING: Constitutional compliance issues detected"
    echo "   - Some backups missing constitutional hash"
    echo "   - Review backup creation processes"
    echo "   - Verify constitutional hash propagation"
elif [[ $VALID_BACKUPS -lt $TOTAL_BACKUPS ]]; then
    echo "⚠️ WARNING: Backup integrity issues detected"
    echo "   - Some backups failed validation"
    echo "   - Check backup storage integrity"
    echo "   - Review backup creation logs"
else
    echo "✅ HEALTHY: All backups are valid and compliant"
    echo "   - Constitutional compliance: 100%"
    echo "   - Backup integrity: 100%"
    echo "   - System ready for disaster recovery"
fi

# Age analysis
echo ""
echo "📅 BACKUP AGE ANALYSIS"
echo "======================"

current_time=$(date +%s)
for location in "${BACKUP_LOCATIONS[@]}"; do
    if [[ -d "$location" ]]; then
        latest_backup=$(find "$location" -name "*.sql.gz" -o -name "*.tar.gz" -o -name "*.json" -o -name "*.sql" | xargs ls -t | head -1)
        if [[ -n "$latest_backup" ]]; then
            backup_time=$(stat -c%Y "$latest_backup")
            age_hours=$(( (current_time - backup_time) / 3600 ))
            
            echo "  $(basename "$location"): $age_hours hours ago"
            
            if [[ $age_hours -gt 24 ]]; then
                echo "    ⚠️ Backup older than 24 hours"
            elif [[ $age_hours -gt 4 ]]; then
                echo "    ⚠️ Backup older than 4 hours"
            else
                echo "    ✅ Recent backup"
            fi
        else
            echo "  $(basename "$location"): No backups found"
        fi
    fi
done

# Save validation report
REPORT_FILE="/tmp/backup_validation_report_$(date +%Y%m%d_%H%M%S).json"
cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date --iso-8601=seconds)",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "validation_results": {
    "total_backups": $TOTAL_BACKUPS,
    "valid_backups": $VALID_BACKUPS,
    "compliant_backups": $COMPLIANT_BACKUPS,
    "total_size_bytes": $TOTAL_SIZE,
    "validity_rate": $((TOTAL_BACKUPS > 0 ? VALID_BACKUPS * 100 / TOTAL_BACKUPS : 0)),
    "compliance_rate": $((TOTAL_BACKUPS > 0 ? COMPLIANT_BACKUPS * 100 / TOTAL_BACKUPS : 0))
  },
  "failed_validations": $(printf '%s\n' "${FAILED_VALIDATIONS[@]}" | jq -R . | jq -s .),
  "backup_locations": $(printf '%s\n' "${BACKUP_LOCATIONS[@]}" | jq -R . | jq -s .),
  "health_status": "$(if [[ $COMPLIANT_BACKUPS -eq $TOTAL_BACKUPS ]] && [[ $TOTAL_BACKUPS -gt 0 ]]; then echo "HEALTHY"; elif [[ $TOTAL_BACKUPS -eq 0 ]]; then echo "CRITICAL"; else echo "WARNING"; fi)"
}
EOF

echo ""
echo "📄 Detailed validation report saved to: $REPORT_FILE"

# Final exit code
if [[ $COMPLIANT_BACKUPS -eq $TOTAL_BACKUPS ]] && [[ $TOTAL_BACKUPS -gt 0 ]]; then
    echo ""
    echo "✅ ALL BACKUPS VALIDATED SUCCESSFULLY"
    echo "🏛️ Constitutional compliance: 100%"
    echo "🎉 Backup system is healthy and ready for disaster recovery"
    exit 0
elif [[ $TOTAL_BACKUPS -eq 0 ]]; then
    echo ""
    echo "🚨 CRITICAL: NO BACKUPS FOUND"
    echo "🛠️ Immediate attention required"
    exit 2
else
    echo ""
    echo "⚠️ BACKUP VALIDATION ISSUES DETECTED"
    echo "🔧 Review failed validations and take corrective action"
    echo "📊 Success rate: $((VALID_BACKUPS * 100 / TOTAL_BACKUPS))%"
    exit 1
fi