#!/bin/bash

# ACGS-1 Enterprise Artifact Management and Retention Policy Validator
# Validates artifact upload/download patterns, retention policies, naming, and organization
# requires: Proper artifact naming, 14-30 day retention, enterprise reporting artifacts
# ensures: Comprehensive artifact management, proper retention policies, organized storage
# sha256: c9f6e3a2b8d5f1e7c4a9b6f3e8c5a2d9f6e3c7a4b1d8f5e2c9b6a3f7e4c1a8b5

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ARTIFACT_LOG="/tmp/acgs-artifact-management.log"
RESULTS_FILE="/tmp/artifact-management-results.json"

# Enterprise artifact management targets
MIN_RETENTION_DAYS=14
MAX_RETENTION_DAYS=30
REQUIRED_ARTIFACT_TYPES=("security" "performance" "compliance" "build")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log_artifact() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[ARTIFACT-INFO]${NC} $message" | tee -a "$ARTIFACT_LOG"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[ARTIFACT-SUCCESS]${NC} $message" | tee -a "$ARTIFACT_LOG"
            ;;
        "WARNING")
            echo -e "${YELLOW}[ARTIFACT-WARNING]${NC} $message" | tee -a "$ARTIFACT_LOG"
            ;;
        "ERROR")
            echo -e "${RED}[ARTIFACT-ERROR]${NC} $message" | tee -a "$ARTIFACT_LOG"
            ;;
        "METRIC")
            echo -e "${PURPLE}[ARTIFACT-METRIC]${NC} $message" | tee -a "$ARTIFACT_LOG"
            ;;
    esac
    echo "[$timestamp] [$level] $message" >> "$ARTIFACT_LOG"
}

# Initialize artifact management validation
initialize_artifact_validation() {
    local start_time=$(date +%s)
    local validation_id="artifact-mgmt-$(date +%s)"
    
    log_artifact "INFO" "📦 ACGS-1 Enterprise Artifact Management Validation Started"
    log_artifact "INFO" "Validation ID: $validation_id"
    log_artifact "INFO" "Retention Policy: $MIN_RETENTION_DAYS-$MAX_RETENTION_DAYS days"
    log_artifact "INFO" "Required Types: ${REQUIRED_ARTIFACT_TYPES[*]}"
    
    # Create initial results structure
    cat > "$RESULTS_FILE" << EOF
{
  "validation_id": "$validation_id",
  "start_time": $start_time,
  "start_time_iso": "$(date -u -d @$start_time +%Y-%m-%dT%H:%M:%SZ)",
  "retention_policy": {
    "min_retention_days": $MIN_RETENTION_DAYS,
    "max_retention_days": $MAX_RETENTION_DAYS,
    "required_artifact_types": $(printf '%s\n' "${REQUIRED_ARTIFACT_TYPES[@]}" | jq -R . | jq -s .)
  },
  "upload_patterns": {},
  "download_patterns": {},
  "retention_compliance": {},
  "naming_organization": {},
  "enterprise_artifacts": {},
  "summary": {
    "total_validations": 0,
    "passed_validations": 0,
    "failed_validations": 0,
    "artifact_score": 0
  },
  "validation_status": "in_progress"
}
EOF
    
    log_artifact "SUCCESS" "✅ Artifact management validation initialized"
}

# Validate artifact upload patterns
validate_upload_patterns() {
    log_artifact "INFO" "🔍 Validating artifact upload patterns..."
    
    local upload_actions_count=0
    local upload_pattern_quality="unknown"
    local path_organization="unknown"
    local upload_score=0
    
    # Count upload actions
    if [ -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        upload_actions_count=$(grep -c "upload-artifact@v4" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" || echo "0")
        
        if [ $upload_actions_count -ge 5 ]; then
            upload_pattern_quality="comprehensive"
            upload_score=$((upload_score + 40))
            log_artifact "SUCCESS" "✅ Comprehensive upload patterns ($upload_actions_count uploads)"
        elif [ $upload_actions_count -ge 3 ]; then
            upload_pattern_quality="adequate"
            upload_score=$((upload_score + 25))
            log_artifact "WARNING" "⚠️ Adequate upload patterns ($upload_actions_count uploads)"
        else
            upload_pattern_quality="insufficient"
            log_artifact "ERROR" "❌ Insufficient upload patterns ($upload_actions_count uploads)"
        fi
        
        # Check path organization
        if grep -q "path:.*|" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" && \
           grep -q "/tmp/.*\.json" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
            path_organization="organized"
            upload_score=$((upload_score + 30))
            log_artifact "SUCCESS" "✅ Well-organized artifact paths"
        else
            path_organization="basic"
            upload_score=$((upload_score + 15))
            log_artifact "WARNING" "⚠️ Basic path organization"
        fi
        
        # Check for conditional uploads
        if grep -q "if:.*always()" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
            upload_score=$((upload_score + 30))
            log_artifact "SUCCESS" "✅ Conditional upload patterns implemented"
        else
            log_artifact "WARNING" "⚠️ No conditional upload patterns found"
        fi
    else
        log_artifact "ERROR" "❌ Enterprise CI workflow not found"
    fi
    
    log_artifact "METRIC" "Upload patterns score: $upload_score/100"
    
    # Update results
    local temp_file=$(mktemp)
    jq --arg count "$upload_actions_count" --arg quality "$upload_pattern_quality" \
       --arg organization "$path_organization" --arg score "$upload_score" \
       '.upload_patterns = {
          "upload_actions_count": ($count | tonumber),
          "pattern_quality": $quality,
          "path_organization": $organization,
          "upload_score": ($score | tonumber),
          "validated": true
        }' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
}

# Validate artifact download patterns
validate_download_patterns() {
    log_artifact "INFO" "🔍 Validating artifact download patterns..."
    
    local download_actions_count=0
    local download_strategy="unknown"
    local download_score=0
    
    # Count download actions
    if [ -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        download_actions_count=$(grep -c "download-artifact@v4" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" || echo "0")
        
        if [ $download_actions_count -ge 1 ]; then
            download_score=$((download_score + 50))
            log_artifact "SUCCESS" "✅ Artifact download patterns implemented ($download_actions_count downloads)"
            
            # Check download strategy
            if grep -q "Download all artifacts" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
                download_strategy="comprehensive"
                download_score=$((download_score + 50))
                log_artifact "SUCCESS" "✅ Comprehensive download strategy"
            else
                download_strategy="selective"
                download_score=$((download_score + 30))
                log_artifact "WARNING" "⚠️ Selective download strategy"
            fi
        else
            download_strategy="missing"
            log_artifact "WARNING" "⚠️ No artifact download patterns found"
        fi
    else
        log_artifact "ERROR" "❌ Enterprise CI workflow not found"
    fi
    
    log_artifact "METRIC" "Download patterns score: $download_score/100"
    
    # Update results
    local temp_file=$(mktemp)
    jq --arg count "$download_actions_count" --arg strategy "$download_strategy" --arg score "$download_score" \
       '.download_patterns = {
          "download_actions_count": ($count | tonumber),
          "download_strategy": $strategy,
          "download_score": ($score | tonumber),
          "validated": true
        }' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
}

# Validate retention policy compliance
validate_retention_compliance() {
    log_artifact "INFO" "🔍 Validating retention policy compliance..."
    
    local retention_policies_count=0
    local compliant_policies=0
    local retention_compliance_score=0
    
    # Analyze retention policies
    if [ -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        retention_policies_count=$(grep -c "retention-days:" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" || echo "0")
        
        if [ $retention_policies_count -gt 0 ]; then
            log_artifact "SUCCESS" "✅ Retention policies found ($retention_policies_count policies)"
            
            # Check compliance with 14-30 day requirement
            local retention_values=$(grep "retention-days:" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" | awk '{print $2}' | sort -u)
            
            for retention_value in $retention_values; do
                if [ "$retention_value" -ge $MIN_RETENTION_DAYS ] && [ "$retention_value" -le $MAX_RETENTION_DAYS ]; then
                    compliant_policies=$((compliant_policies + 1))
                    log_artifact "SUCCESS" "✅ Compliant retention policy: $retention_value days"
                else
                    log_artifact "WARNING" "⚠️ Non-compliant retention policy: $retention_value days"
                fi
            done
            
            # Calculate compliance score
            if [ $compliant_policies -eq $retention_policies_count ]; then
                retention_compliance_score=100
                log_artifact "SUCCESS" "✅ All retention policies compliant"
            elif [ $compliant_policies -gt 0 ]; then
                retention_compliance_score=$(echo "scale=0; $compliant_policies * 100 / $retention_policies_count" | bc)
                log_artifact "WARNING" "⚠️ Partial retention compliance: $compliant_policies/$retention_policies_count"
            else
                retention_compliance_score=0
                log_artifact "ERROR" "❌ No compliant retention policies"
            fi
        else
            log_artifact "ERROR" "❌ No retention policies found"
        fi
    else
        log_artifact "ERROR" "❌ Enterprise CI workflow not found"
    fi
    
    log_artifact "METRIC" "Retention compliance score: $retention_compliance_score/100"
    
    # Update results
    local temp_file=$(mktemp)
    jq --arg total "$retention_policies_count" --arg compliant "$compliant_policies" --arg score "$retention_compliance_score" \
       '.retention_compliance = {
          "total_policies": ($total | tonumber),
          "compliant_policies": ($compliant | tonumber),
          "compliance_score": ($score | tonumber),
          "validated": true
        }' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
}

# Validate naming and organization
validate_naming_organization() {
    log_artifact "INFO" "🔍 Validating artifact naming and organization..."
    
    local naming_convention_score=0
    local organization_quality="unknown"
    local enterprise_naming="unknown"
    
    # Check naming conventions
    if [ -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        # Check for enterprise-prefixed artifacts
        if grep -q "enterprise-.*-" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
            enterprise_naming="consistent"
            naming_convention_score=$((naming_convention_score + 40))
            log_artifact "SUCCESS" "✅ Enterprise naming conventions used"
        else
            enterprise_naming="inconsistent"
            log_artifact "WARNING" "⚠️ Inconsistent enterprise naming"
        fi
        
        # Check for descriptive names
        if grep -q "security-.*results" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" && \
           grep -q "performance.*metrics" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
            organization_quality="descriptive"
            naming_convention_score=$((naming_convention_score + 35))
            log_artifact "SUCCESS" "✅ Descriptive artifact names used"
        else
            organization_quality="basic"
            naming_convention_score=$((naming_convention_score + 20))
            log_artifact "WARNING" "⚠️ Basic artifact naming"
        fi
        
        # Check for categorization
        if grep -q "build.*artifacts" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" && \
           grep -q "compliance.*dashboard" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
            naming_convention_score=$((naming_convention_score + 25))
            log_artifact "SUCCESS" "✅ Categorized artifact naming"
        else
            log_artifact "WARNING" "⚠️ Limited artifact categorization"
        fi
    else
        log_artifact "ERROR" "❌ Enterprise CI workflow not found"
    fi
    
    log_artifact "METRIC" "Naming and organization score: $naming_convention_score/100"
    
    # Update results
    local temp_file=$(mktemp)
    jq --arg quality "$organization_quality" --arg enterprise "$enterprise_naming" --arg score "$naming_convention_score" \
       '.naming_organization = {
          "organization_quality": $quality,
          "enterprise_naming": $enterprise,
          "naming_score": ($score | tonumber),
          "validated": true
        }' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
}

# Validate enterprise reporting artifacts
validate_enterprise_artifacts() {
    log_artifact "INFO" "🔍 Validating enterprise reporting artifacts..."
    
    local enterprise_artifacts_count=0
    local required_types_found=0
    local enterprise_artifacts_score=0
    
    # Check for required artifact types
    if [ -f "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" ]; then
        for artifact_type in "${REQUIRED_ARTIFACT_TYPES[@]}"; do
            if grep -q "$artifact_type.*artifacts\|$artifact_type.*results\|$artifact_type.*reports" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml"; then
                required_types_found=$((required_types_found + 1))
                log_artifact "SUCCESS" "✅ $artifact_type artifacts found"
            else
                log_artifact "WARNING" "⚠️ $artifact_type artifacts missing"
            fi
        done
        
        # Count enterprise-specific artifacts
        enterprise_artifacts_count=$(grep -c "enterprise-.*-.*" "$PROJECT_ROOT/.github/workflows/enterprise-ci.yml" || echo "0")
        
        # Calculate score
        local type_coverage_score=$(echo "scale=0; $required_types_found * 60 / ${#REQUIRED_ARTIFACT_TYPES[@]}" | bc)
        local enterprise_count_score=0
        
        if [ $enterprise_artifacts_count -ge 3 ]; then
            enterprise_count_score=40
        elif [ $enterprise_artifacts_count -ge 2 ]; then
            enterprise_count_score=25
        elif [ $enterprise_artifacts_count -ge 1 ]; then
            enterprise_count_score=15
        fi
        
        enterprise_artifacts_score=$((type_coverage_score + enterprise_count_score))
        
        log_artifact "METRIC" "Required types coverage: $required_types_found/${#REQUIRED_ARTIFACT_TYPES[@]}"
        log_artifact "METRIC" "Enterprise artifacts count: $enterprise_artifacts_count"
    else
        log_artifact "ERROR" "❌ Enterprise CI workflow not found"
    fi
    
    log_artifact "METRIC" "Enterprise artifacts score: $enterprise_artifacts_score/100"
    
    # Update results
    local temp_file=$(mktemp)
    jq --arg count "$enterprise_artifacts_count" --arg types_found "$required_types_found" \
       --arg total_types "${#REQUIRED_ARTIFACT_TYPES[@]}" --arg score "$enterprise_artifacts_score" \
       '.enterprise_artifacts = {
          "enterprise_artifacts_count": ($count | tonumber),
          "required_types_found": ($types_found | tonumber),
          "total_required_types": ($total_types | tonumber),
          "enterprise_score": ($score | tonumber),
          "validated": true
        }' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
}

# Calculate overall artifact management score
calculate_artifact_score() {
    log_artifact "INFO" "📊 Calculating overall artifact management score..."
    
    local total_score=0
    local max_score=100
    
    # Upload patterns (20 points)
    local upload_score=$(jq -r '.upload_patterns.upload_score' "$RESULTS_FILE")
    local upload_points=$(echo "scale=0; $upload_score * 20 / 100" | bc)
    total_score=$((total_score + upload_points))
    
    # Download patterns (15 points)
    local download_score=$(jq -r '.download_patterns.download_score' "$RESULTS_FILE")
    local download_points=$(echo "scale=0; $download_score * 15 / 100" | bc)
    total_score=$((total_score + download_points))
    
    # Retention compliance (25 points)
    local retention_score=$(jq -r '.retention_compliance.compliance_score' "$RESULTS_FILE")
    local retention_points=$(echo "scale=0; $retention_score * 25 / 100" | bc)
    total_score=$((total_score + retention_points))
    
    # Naming and organization (20 points)
    local naming_score=$(jq -r '.naming_organization.naming_score' "$RESULTS_FILE")
    local naming_points=$(echo "scale=0; $naming_score * 20 / 100" | bc)
    total_score=$((total_score + naming_points))
    
    # Enterprise artifacts (20 points)
    local enterprise_score=$(jq -r '.enterprise_artifacts.enterprise_score' "$RESULTS_FILE")
    local enterprise_points=$(echo "scale=0; $enterprise_score * 20 / 100" | bc)
    total_score=$((total_score + enterprise_points))
    
    # Determine artifact management grade
    local artifact_grade="F"
    local artifact_status="poor"
    
    if [ $total_score -ge 90 ]; then
        artifact_grade="A"
        artifact_status="excellent"
    elif [ $total_score -ge 80 ]; then
        artifact_grade="B"
        artifact_status="good"
    elif [ $total_score -ge 70 ]; then
        artifact_grade="C"
        artifact_status="adequate"
    elif [ $total_score -ge 60 ]; then
        artifact_grade="D"
        artifact_status="poor"
    fi
    
    log_artifact "METRIC" "Artifact management score: $total_score/$max_score (Grade: $artifact_grade)"
    
    # Update results with final score
    local temp_file=$(mktemp)
    jq --arg score "$total_score" --arg max_score "$max_score" --arg grade "$artifact_grade" --arg status "$artifact_status" \
       '.summary.artifact_score = ($score | tonumber) |
        .summary.max_score = ($max_score | tonumber) |
        .summary.artifact_grade = $grade |
        .validation_status = $status' \
       "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
    
    return $total_score
}

# Main validation function
main() {
    case "${1:-validate}" in
        "validate")
            initialize_artifact_validation
            validate_upload_patterns
            validate_download_patterns
            validate_retention_compliance
            validate_naming_organization
            validate_enterprise_artifacts
            
            if calculate_artifact_score; then
                local final_score=$(jq -r '.summary.artifact_score' "$RESULTS_FILE")
                if [ $final_score -ge 80 ]; then
                    log_artifact "SUCCESS" "🎉 Artifact management validation PASSED (Score: $final_score/100)"
                    exit 0
                else
                    log_artifact "ERROR" "❌ Artifact management validation FAILED (Score: $final_score/100)"
                    exit 1
                fi
            fi
            ;;
        "help"|*)
            echo "ACGS-1 Enterprise Artifact Management Validator"
            echo "Usage: $0 {validate|help}"
            echo ""
            echo "Commands:"
            echo "  validate    Run artifact management validation"
            echo "  help        Show this help message"
            ;;
    esac
}

# Execute main function
main "$@"
