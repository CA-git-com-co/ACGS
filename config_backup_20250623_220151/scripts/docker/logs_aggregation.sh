#!/bin/bash

# ACGS-1 Log Aggregation Script for Containerized Environment
# Collects and formats logs from all services

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOG_OUTPUT_DIR="/tmp/acgs_logs_$(date +%Y%m%d_%H%M%S)"
SERVICES=("auth_service" "ac_service" "integrity_service" "fv_service" "gs_service" "pgc_service" "ec_service")
INFRASTRUCTURE=("postgres" "redis" "haproxy")

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

# Function to collect service logs
collect_service_logs() {
    local service_name=$1
    local container_name="acgs_${service_name}"
    
    print_status "Collecting logs for $service_name..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        # Collect container logs
        docker logs "$container_name" > "$LOG_OUTPUT_DIR/${service_name}_container.log" 2>&1
        
        # Collect application logs if available
        if docker exec "$container_name" test -d /app/logs 2>/dev/null; then
            docker exec "$container_name" find /app/logs -name "*.log" -exec cat {} \; > "$LOG_OUTPUT_DIR/${service_name}_application.log" 2>/dev/null || true
        fi
        
        print_success "Logs collected for $service_name"
    else
        print_warning "$service_name container not running - skipping"
    fi
}

# Function to collect infrastructure logs
collect_infrastructure_logs() {
    local service_name=$1
    local container_name="acgs_${service_name}"
    
    print_status "Collecting infrastructure logs for $service_name..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        docker logs "$container_name" > "$LOG_OUTPUT_DIR/infra_${service_name}.log" 2>&1
        print_success "Infrastructure logs collected for $service_name"
    else
        print_warning "$service_name container not running - skipping"
    fi
}

# Function to generate log summary
generate_log_summary() {
    print_status "Generating log summary..."
    
    local summary_file="$LOG_OUTPUT_DIR/log_summary.txt"
    
    cat > "$summary_file" << EOF
ACGS-1 Log Collection Summary
============================
Collection Time: $(date)
Output Directory: $LOG_OUTPUT_DIR

Service Logs:
EOF
    
    for service in "${SERVICES[@]}"; do
        local container_log="$LOG_OUTPUT_DIR/${service}_container.log"
        local app_log="$LOG_OUTPUT_DIR/${service}_application.log"
        
        echo "  $service:" >> "$summary_file"
        
        if [ -f "$container_log" ]; then
            local container_lines=$(wc -l < "$container_log")
            echo "    Container logs: $container_lines lines" >> "$summary_file"
        fi
        
        if [ -f "$app_log" ]; then
            local app_lines=$(wc -l < "$app_log")
            echo "    Application logs: $app_lines lines" >> "$summary_file"
        fi
    done
    
    echo "" >> "$summary_file"
    echo "Infrastructure Logs:" >> "$summary_file"
    
    for infra in "${INFRASTRUCTURE[@]}"; do
        local infra_log="$LOG_OUTPUT_DIR/infra_${infra}.log"
        
        if [ -f "$infra_log" ]; then
            local infra_lines=$(wc -l < "$infra_log")
            echo "  $infra: $infra_lines lines" >> "$summary_file"
        fi
    done
    
    echo "" >> "$summary_file"
    echo "Error Analysis:" >> "$summary_file"
    
    # Search for errors across all logs
    local error_count=0
    for log_file in "$LOG_OUTPUT_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            local file_errors=$(grep -i "error\|exception\|failed\|critical" "$log_file" | wc -l)
            if [ $file_errors -gt 0 ]; then
                echo "  $(basename "$log_file"): $file_errors errors/exceptions" >> "$summary_file"
                error_count=$((error_count + file_errors))
            fi
        fi
    done
    
    echo "  Total errors found: $error_count" >> "$summary_file"
    
    print_success "Log summary generated: $summary_file"
    cat "$summary_file"
}

# Function to create compressed archive
create_log_archive() {
    print_status "Creating compressed log archive..."
    
    local archive_name="acgs_logs_$(date +%Y%m%d_%H%M%S).tar.gz"
    local archive_path="/tmp/$archive_name"
    
    tar -czf "$archive_path" -C "$(dirname "$LOG_OUTPUT_DIR")" "$(basename "$LOG_OUTPUT_DIR")"
    
    if [ -f "$archive_path" ]; then
        local archive_size=$(du -h "$archive_path" | cut -f1)
        print_success "Log archive created: $archive_path ($archive_size)"
        echo "Archive contents:"
        tar -tzf "$archive_path" | head -20
        
        if [ $(tar -tzf "$archive_path" | wc -l) -gt 20 ]; then
            echo "... and $(($(tar -tzf "$archive_path" | wc -l) - 20)) more files"
        fi
    else
        print_error "Failed to create log archive"
        return 1
    fi
}

# Main execution
main() {
    echo "📋 ACGS-1 Log Aggregation"
    echo "========================="
    echo "Date: $(date)"
    echo "Output Directory: $LOG_OUTPUT_DIR"
    echo ""
    
    # Create output directory
    mkdir -p "$LOG_OUTPUT_DIR"
    
    # Collect service logs
    print_status "Step 1: Collecting ACGS service logs"
    for service in "${SERVICES[@]}"; do
        collect_service_logs "$service"
    done
    echo ""
    
    # Collect infrastructure logs
    print_status "Step 2: Collecting infrastructure logs"
    for infra in "${INFRASTRUCTURE[@]}"; do
        collect_infrastructure_logs "$infra"
    done
    echo ""
    
    # Collect Docker Compose logs
    print_status "Step 3: Collecting Docker Compose logs"
    if command -v docker-compose > /dev/null 2>&1; then
        docker-compose -f docker-compose.acgs.yml logs --no-color > "$LOG_OUTPUT_DIR/docker_compose.log" 2>&1 || true
        print_success "Docker Compose logs collected"
    else
        print_warning "Docker Compose not available - skipping"
    fi
    echo ""
    
    # Generate summary
    print_status "Step 4: Generating log summary"
    generate_log_summary
    echo ""
    
    # Create archive
    print_status "Step 5: Creating compressed archive"
    create_log_archive
    echo ""
    
    # Final summary
    echo "📊 LOG AGGREGATION SUMMARY"
    echo "=========================="
    echo "✅ Output directory: $LOG_OUTPUT_DIR"
    echo "📁 Total files: $(find "$LOG_OUTPUT_DIR" -type f | wc -l)"
    echo "💾 Total size: $(du -sh "$LOG_OUTPUT_DIR" | cut -f1)"
    echo ""
    echo "🔍 Analysis Commands:"
    echo "   View summary: cat $LOG_OUTPUT_DIR/log_summary.txt"
    echo "   Search errors: grep -r 'ERROR' $LOG_OUTPUT_DIR/"
    echo "   Search warnings: grep -r 'WARNING' $LOG_OUTPUT_DIR/"
    echo "   View service logs: ls $LOG_OUTPUT_DIR/*_container.log"
    echo ""
    echo "📦 Archive: /tmp/acgs_logs_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    print_success "Log aggregation completed successfully!"
}

# Execute main function
main "$@"
