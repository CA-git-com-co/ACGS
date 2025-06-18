#!/bin/bash

# ACGS-1 Comprehensive Security Monitoring Deployment Script
# Deploys ELK stack with security monitoring, SIEM capabilities, and automated threat detection
# Target: Real-time security monitoring, automated alerting, comprehensive audit logging

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ELK_CONFIG_DIR="$SCRIPT_DIR/elk-config"
LOG_FILE="$SCRIPT_DIR/logs/security-monitoring-deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)  echo -e "${GREEN}[INFO]${NC} $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
        DEBUG) echo -e "${BLUE}[DEBUG]${NC} $message" ;;
    esac
    
    # Also log to file
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Error handling
error_exit() {
    log ERROR "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed. Please install Docker first."
    fi
    
    if ! docker info &> /dev/null; then
        error_exit "Docker is not running. Please start Docker first."
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error_exit "Docker Compose is not available. Please install Docker Compose."
    fi
    
    # Check available disk space (need at least 10GB)
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    local required_space=10485760  # 10GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        error_exit "Insufficient disk space. Need at least 10GB available."
    fi
    
    log INFO "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log INFO "Creating necessary directories..."
    
    local dirs=(
        "$SCRIPT_DIR/logs"
        "/var/log/acgs/security"
        "/var/log/acgs/auth"
        "/var/log/acgs/audit"
        "/var/log/acgs/governance"
        "/var/log/acgs/services"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            sudo mkdir -p "$dir"
            sudo chown -R $USER:$USER "$dir" 2>/dev/null || true
            log INFO "Created directory: $dir"
        fi
    done
}

# Set up system limits for Elasticsearch
setup_system_limits() {
    log INFO "Setting up system limits for Elasticsearch..."
    
    # Increase vm.max_map_count for Elasticsearch
    local current_max_map_count=$(sysctl -n vm.max_map_count)
    local required_max_map_count=262144
    
    if [ "$current_max_map_count" -lt "$required_max_map_count" ]; then
        log INFO "Increasing vm.max_map_count to $required_max_map_count"
        sudo sysctl -w vm.max_map_count=$required_max_map_count
        
        # Make it persistent
        echo "vm.max_map_count=$required_max_map_count" | sudo tee -a /etc/sysctl.conf
    fi
    
    # Set up ulimits
    if [ -f /etc/security/limits.conf ]; then
        if ! grep -q "elasticsearch" /etc/security/limits.conf; then
            log INFO "Adding Elasticsearch ulimits"
            echo "elasticsearch soft memlock unlimited" | sudo tee -a /etc/security/limits.conf
            echo "elasticsearch hard memlock unlimited" | sudo tee -a /etc/security/limits.conf
        fi
    fi
}

# Deploy ELK stack
deploy_elk_stack() {
    log INFO "Deploying ELK stack for security monitoring..."
    
    cd "$SCRIPT_DIR"
    
    # Stop any existing containers
    log INFO "Stopping existing containers..."
    docker-compose -f docker-compose.elk-security.yml down --remove-orphans || true
    
    # Pull latest images
    log INFO "Pulling latest Docker images..."
    docker-compose -f docker-compose.elk-security.yml pull
    
    # Start the stack
    log INFO "Starting ELK security monitoring stack..."
    docker-compose -f docker-compose.elk-security.yml up -d
    
    # Wait for services to be ready
    log INFO "Waiting for services to be ready..."
    
    # Wait for Elasticsearch
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -u elastic:acgs_security_2024 "http://localhost:9201/_cluster/health" | grep -q '"status":"green\|yellow"'; then
            log INFO "Elasticsearch is ready"
            break
        fi
        
        attempt=$((attempt + 1))
        log INFO "Waiting for Elasticsearch... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error_exit "Elasticsearch failed to start within expected time"
    fi
    
    # Wait for Kibana
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "http://localhost:5601/api/status" | grep -q '"overall":{"level":"available"'; then
            log INFO "Kibana is ready"
            break
        fi
        
        attempt=$((attempt + 1))
        log INFO "Waiting for Kibana... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error_exit "Kibana failed to start within expected time"
    fi
    
    log INFO "ELK stack deployed successfully"
}

# Configure Kibana dashboards
configure_kibana_dashboards() {
    log INFO "Configuring Kibana dashboards..."
    
    # Wait a bit more for Kibana to be fully ready
    sleep 30
    
    # Import security dashboard
    local dashboard_file="$ELK_CONFIG_DIR/kibana/dashboards/security-overview.json"
    
    if [ -f "$dashboard_file" ]; then
        log INFO "Importing security overview dashboard..."
        
        curl -X POST "http://localhost:5601/api/saved_objects/_import" \
            -H "Content-Type: application/json" \
            -H "kbn-xsrf: true" \
            -u elastic:acgs_security_2024 \
            --form file=@"$dashboard_file" || log WARN "Failed to import dashboard"
    fi
    
    # Create index patterns
    log INFO "Creating index patterns..."
    
    local index_patterns=(
        "acgs-security-alerts-*"
        "acgs-auth-logs-*"
        "acgs-audit-logs-*"
        "acgs-governance-logs-*"
        "acgs-logs-*"
        "filebeat-acgs-*"
        "metricbeat-acgs-*"
    )
    
    for pattern in "${index_patterns[@]}"; do
        log INFO "Creating index pattern: $pattern"
        
        curl -X POST "http://localhost:5601/api/saved_objects/index-pattern" \
            -H "Content-Type: application/json" \
            -H "kbn-xsrf: true" \
            -u elastic:acgs_security_2024 \
            -d "{
                \"attributes\": {
                    \"title\": \"$pattern\",
                    \"timeFieldName\": \"@timestamp\"
                }
            }" || log WARN "Failed to create index pattern: $pattern"
    done
}

# Test security monitoring
test_security_monitoring() {
    log INFO "Testing security monitoring system..."
    
    # Test Elasticsearch
    log INFO "Testing Elasticsearch connection..."
    local es_health=$(curl -s -u elastic:acgs_security_2024 "http://localhost:9201/_cluster/health")
    if echo "$es_health" | grep -q '"status":"green\|yellow"'; then
        log INFO "✓ Elasticsearch is healthy"
    else
        log ERROR "✗ Elasticsearch health check failed"
        return 1
    fi
    
    # Test Kibana
    log INFO "Testing Kibana connection..."
    if curl -s "http://localhost:5601/api/status" | grep -q '"overall":{"level":"available"'; then
        log INFO "✓ Kibana is available"
    else
        log ERROR "✗ Kibana is not available"
        return 1
    fi
    
    # Test Logstash
    log INFO "Testing Logstash connection..."
    if curl -s "http://localhost:9600" | grep -q '"status":"green"'; then
        log INFO "✓ Logstash is running"
    else
        log WARN "⚠ Logstash status check failed (may still be starting)"
    fi
    
    # Test security processor
    log INFO "Testing security processor..."
    if curl -s "http://localhost:8080/health" | grep -q '"status":"healthy"'; then
        log INFO "✓ Security processor is healthy"
    else
        log WARN "⚠ Security processor health check failed (may still be starting)"
    fi
    
    # Send test security event
    log INFO "Sending test security event..."
    curl -X POST "http://localhost:8080/events" \
        -H "Content-Type: application/json" \
        -d '{
            "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
            "event_type": "test_event",
            "severity": "INFO",
            "source_ip": "127.0.0.1",
            "user_id": "test_user",
            "description": "Test security event from deployment script",
            "risk_score": 10,
            "metadata": {"test": true}
        }' || log WARN "Failed to send test event"
    
    log INFO "Security monitoring system test completed"
}

# Display deployment summary
display_summary() {
    log INFO "=== ACGS-1 Security Monitoring Deployment Summary ==="
    echo
    echo -e "${GREEN}✓ ELK Stack Security Monitoring Deployed Successfully${NC}"
    echo
    echo "Service URLs:"
    echo "  • Elasticsearch: http://localhost:9201"
    echo "  • Kibana:        http://localhost:5601"
    echo "  • Logstash:      http://localhost:9600"
    echo "  • Security Processor: http://localhost:8080"
    echo
    echo "Credentials:"
    echo "  • Elasticsearch/Kibana: elastic / acgs_security_2024"
    echo
    echo "Key Features Deployed:"
    echo "  • Real-time security event processing"
    echo "  • Threat intelligence integration"
    echo "  • Automated incident response"
    echo "  • Comprehensive audit logging"
    echo "  • Security dashboards and visualization"
    echo "  • SIEM capabilities"
    echo
    echo "Log Files:"
    echo "  • Deployment: $LOG_FILE"
    echo "  • Security Events: /var/log/acgs/security/"
    echo "  • Authentication: /var/log/acgs/auth/"
    echo "  • Audit Logs: /var/log/acgs/audit/"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Access Kibana at http://localhost:5601"
    echo "2. Configure additional security rules as needed"
    echo "3. Set up alerting webhooks in environment variables"
    echo "4. Review and customize threat detection rules"
    echo "5. Integrate with existing ACGS-1 services"
    echo
}

# Main execution
main() {
    log INFO "Starting ACGS-1 Security Monitoring Deployment"
    log INFO "Timestamp: $(date)"
    log INFO "Script: $0"
    log INFO "Working Directory: $PWD"
    
    check_prerequisites
    create_directories
    setup_system_limits
    deploy_elk_stack
    configure_kibana_dashboards
    test_security_monitoring
    display_summary
    
    log INFO "ACGS-1 Security Monitoring deployment completed successfully!"
}

# Run main function
main "$@"
