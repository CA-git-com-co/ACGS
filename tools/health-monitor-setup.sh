#!/bin/bash

# ACGS Health Monitor Setup Script
# Sets up comprehensive health monitoring for all 7 ACGS core services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MONITORING_DIR="$PROJECT_ROOT/infrastructure/monitoring"
HEALTH_CHECK_DIR="$PROJECT_ROOT/scripts/health-checks"

# Service configuration
declare -A SERVICES=(
    ["auth"]="8002"
    ["ac"]="8001"
    ["integrity"]="8006"
    ["fv"]="8004"
    ["gs"]="8003"
    ["pgc"]="8005"
    ["ec"]="8007"
)

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}ACGS Health Monitor Setup${NC}"
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

# Create directory structure
create_directories() {
    print_info "Creating monitoring directory structure..."
    
    local dirs=(
        "$MONITORING_DIR"
        "$MONITORING_DIR/dashboards"
        "$MONITORING_DIR/alerts"
        "$MONITORING_DIR/scripts"
        "$HEALTH_CHECK_DIR"
        "$PROJECT_ROOT/logs/health-monitoring"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Generate health check endpoints configuration
generate_health_config() {
    print_info "Generating health check configuration..."
    
    cat > "$MONITORING_DIR/health-endpoints.json" << EOF
{
  "version": "1.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "services": {
    "auth": {
      "name": "Authentication Service",
      "port": 8002,
      "baseUrl": "http://localhost:8002",
      "healthEndpoint": "/health",
      "description": "Authentication and authorization service",
      "critical": true,
      "timeout": 5000,
      "expectedResponse": {
        "status": "healthy",
        "service": "auth_service"
      }
    },
    "ac": {
      "name": "Constitutional AI Service",
      "port": 8001,
      "baseUrl": "http://localhost:8001",
      "healthEndpoint": "/health",
      "description": "Constitutional AI and compliance service",
      "critical": true,
      "timeout": 5000,
      "expectedResponse": {
        "status": "healthy",
        "service": "ac_service_production"
      }
    },
    "integrity": {
      "name": "Integrity Service",
      "port": 8006,
      "baseUrl": "http://localhost:8006",
      "healthEndpoint": "/health",
      "description": "Cryptographic integrity and verification service",
      "critical": true,
      "timeout": 5000,
      "expectedResponse": {
        "status": "healthy",
        "service": "integrity_service"
      }
    },
    "fv": {
      "name": "Formal Verification Service",
      "port": 8004,
      "baseUrl": "http://localhost:8004",
      "healthEndpoint": "/health",
      "description": "Formal verification service",
      "critical": false,
      "timeout": 10000,
      "expectedResponse": {
        "status": "healthy",
        "service": "fv_service"
      }
    },
    "gs": {
      "name": "Governance Synthesis Service",
      "port": 8003,
      "baseUrl": "http://localhost:8003",
      "healthEndpoint": "/health",
      "description": "Governance synthesis service",
      "critical": true,
      "timeout": 5000,
      "expectedResponse": {
        "status": "healthy",
        "service": "gs_service"
      }
    },
    "pgc": {
      "name": "Policy Governance Service",
      "port": 8005,
      "baseUrl": "http://localhost:8005",
      "healthEndpoint": "/health",
      "description": "Policy governance and compliance service",
      "critical": true,
      "timeout": 5000,
      "expectedResponse": {
        "status": "healthy",
        "service": "pgc_service_production"
      }
    },
    "ec": {
      "name": "Executive Council Service",
      "port": 8007,
      "baseUrl": "http://localhost:8007",
      "healthEndpoint": "/health",
      "description": "Executive council and oversight service",
      "critical": false,
      "timeout": 5000,
      "expectedResponse": {
        "status": "healthy",
        "service": "ec_service"
      }
    }
  },
  "monitoring": {
    "interval": 30000,
    "timeout": 5000,
    "retries": 3,
    "alertThresholds": {
      "responseTime": 2000,
      "errorRate": 5,
      "uptime": 99.5,
      "consecutiveFailures": 3
    }
  }
}
EOF

    print_success "Health check configuration generated"
}

# Create individual service health check scripts
create_service_health_checks() {
    print_info "Creating individual service health check scripts..."
    
    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"
        local script_file="$HEALTH_CHECK_DIR/check-${service}-service.sh"
        
        cat > "$script_file" << EOF
#!/bin/bash
# Health check script for ${service} service

SERVICE_NAME="${service}"
SERVICE_PORT="${port}"
HEALTH_URL="http://localhost:\${SERVICE_PORT}/health"
TIMEOUT=5

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if service is running
check_service() {
    local start_time=\$(date +%s%3N)
    
    if curl -s --max-time \$TIMEOUT "\$HEALTH_URL" > /dev/null 2>&1; then
        local end_time=\$(date +%s%3N)
        local response_time=\$((end_time - start_time))
        
        echo -e "\${GREEN}✓ \${SERVICE_NAME} service is healthy (Port \${SERVICE_PORT}) - \${response_time}ms\${NC}"
        return 0
    else
        echo -e "\${RED}✗ \${SERVICE_NAME} service is unhealthy (Port \${SERVICE_PORT})\${NC}"
        return 1
    fi
}

# Get detailed health information
get_health_details() {
    local response=\$(curl -s --max-time \$TIMEOUT "\$HEALTH_URL" 2>/dev/null)
    if [ \$? -eq 0 ] && [ -n "\$response" ]; then
        echo "Health Details:"
        echo "\$response" | jq '.' 2>/dev/null || echo "\$response"
    else
        echo "Unable to retrieve health details"
    fi
}

# Main execution
case "\${1:-check}" in
    "check")
        check_service
        ;;
    "details")
        check_service && get_health_details
        ;;
    "json")
        curl -s --max-time \$TIMEOUT "\$HEALTH_URL" 2>/dev/null || echo '{"status":"unhealthy","error":"connection_failed"}'
        ;;
    *)
        echo "Usage: \$0 {check|details|json}"
        exit 1
        ;;
esac
EOF

        chmod +x "$script_file"
        print_success "Created health check script for ${service} service"
    done
}

# Create comprehensive health check script
create_comprehensive_health_check() {
    print_info "Creating comprehensive health check script..."
    
    cat > "$HEALTH_CHECK_DIR/check-all-services.sh" << EOF
#!/bin/bash
# Comprehensive health check for all ACGS services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="\$SCRIPT_DIR/../logs/health-monitoring/health-check-\$(date +%Y%m%d).log"
JSON_OUTPUT=false
VERBOSE=false

# Ensure log directory exists
mkdir -p "\$(dirname "\$LOG_FILE")"

# Parse command line arguments
while [[ \$# -gt 0 ]]; do
    case \$1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --log)
            LOG_FILE="\$2"
            shift 2
            ;;
        *)
            echo "Unknown option: \$1"
            echo "Usage: \$0 [--json] [--verbose] [--log <file>]"
            exit 1
            ;;
    esac
done

# Services to check
declare -A SERVICES=(
    ["auth"]="8002"
    ["ac"]="8001"
    ["integrity"]="8006"
    ["fv"]="8004"
    ["gs"]="8003"
    ["pgc"]="8005"
    ["ec"]="8007"
)

# Results storage
declare -A RESULTS
declare -A RESPONSE_TIMES
TOTAL_SERVICES=\${#SERVICES[@]}
HEALTHY_SERVICES=0
TIMESTAMP=\$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check individual service
check_service() {
    local service="\$1"
    local port="\$2"
    local url="http://localhost:\$port/health"
    local start_time=\$(date +%s%3N)
    
    if curl -s --max-time 5 "\$url" > /dev/null 2>&1; then
        local end_time=\$(date +%s%3N)
        local response_time=\$((end_time - start_time))
        
        RESULTS["\$service"]="healthy"
        RESPONSE_TIMES["\$service"]="\$response_time"
        ((HEALTHY_SERVICES++))
        
        if [ "\$VERBOSE" = true ] && [ "\$JSON_OUTPUT" = false ]; then
            echo -e "\${GREEN}✓ \$service service (port \$port) - \${response_time}ms\${NC}"
        fi
    else
        RESULTS["\$service"]="unhealthy"
        RESPONSE_TIMES["\$service"]=0
        
        if [ "\$VERBOSE" = true ] && [ "\$JSON_OUTPUT" = false ]; then
            echo -e "\${RED}✗ \$service service (port \$port) - failed\${NC}"
        fi
    fi
}

# Main health check
main() {
    if [ "\$JSON_OUTPUT" = false ]; then
        echo -e "\${BLUE}ACGS Services Health Check\${NC}"
        echo -e "\${BLUE}========================\${NC}"
        echo "Timestamp: \$TIMESTAMP"
        echo
    fi
    
    # Check all services
    for service in "\${!SERVICES[@]}"; do
        check_service "\$service" "\${SERVICES[\$service]}"
    done
    
    # Calculate overall health
    local health_percentage=\$((HEALTHY_SERVICES * 100 / TOTAL_SERVICES))
    local overall_status="healthy"
    
    if [ \$health_percentage -lt 100 ]; then
        if [ \$health_percentage -lt 80 ]; then
            overall_status="unhealthy"
        else
            overall_status="degraded"
        fi
    fi
    
    # Output results
    if [ "\$JSON_OUTPUT" = true ]; then
        echo "{"
        echo "  \"timestamp\": \"\$TIMESTAMP\","
        echo "  \"overall_status\": \"\$overall_status\","
        echo "  \"healthy_services\": \$HEALTHY_SERVICES,"
        echo "  \"total_services\": \$TOTAL_SERVICES,"
        echo "  \"health_percentage\": \$health_percentage,"
        echo "  \"services\": {"
        
        local first=true
        for service in "\${!SERVICES[@]}"; do
            if [ "\$first" = false ]; then
                echo ","
            fi
            echo -n "    \"\$service\": {"
            echo -n "\"status\": \"\${RESULTS[\$service]}\", "
            echo -n "\"port\": \${SERVICES[\$service]}, "
            echo -n "\"response_time_ms\": \${RESPONSE_TIMES[\$service]}"
            echo -n "}"
            first=false
        done
        echo
        echo "  }"
        echo "}"
    else
        echo
        echo -e "\${BLUE}Summary:\${NC}"
        echo "Overall Status: \$overall_status"
        echo "Healthy Services: \$HEALTHY_SERVICES/\$TOTAL_SERVICES (\$health_percentage%)"
        
        if [ \$health_percentage -lt 100 ]; then
            echo
            echo -e "\${YELLOW}Unhealthy Services:\${NC}"
            for service in "\${!SERVICES[@]}"; do
                if [ "\${RESULTS[\$service]}" = "unhealthy" ]; then
                    echo "  - \$service (port \${SERVICES[\$service]})"
                fi
            done
        fi
    fi
    
    # Log results
    {
        echo "[\$TIMESTAMP] Health Check: \$overall_status (\$HEALTHY_SERVICES/\$TOTAL_SERVICES healthy)"
        for service in "\${!SERVICES[@]}"; do
            echo "[\$TIMESTAMP] \$service: \${RESULTS[\$service]} (\${RESPONSE_TIMES[\$service]}ms)"
        done
    } >> "\$LOG_FILE"
    
    # Exit with appropriate code
    if [ "\$overall_status" = "unhealthy" ]; then
        exit 2
    elif [ "\$overall_status" = "degraded" ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main
EOF

    chmod +x "$HEALTH_CHECK_DIR/check-all-services.sh"
    print_success "Created comprehensive health check script"
}

# Create monitoring dashboard configuration
create_monitoring_dashboard() {
    print_info "Creating monitoring dashboard configuration..."
    
    cat > "$MONITORING_DIR/dashboards/acgs-health-dashboard.json" << EOF
{
  "dashboard": {
    "title": "ACGS Services Health Monitor",
    "description": "Real-time health monitoring for all 7 ACGS core services",
    "version": "1.0",
    "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "panels": [
      {
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"acgs-services\"}",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Service Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "http_request_duration_seconds{job=\"acgs-services\"}",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Error Rates",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"acgs-services\",status=~\"5..\"}[5m])",
            "legendFormat": "{{service}}"
          }
        ]
      },
      {
        "title": "Service Uptime",
        "type": "table",
        "targets": [
          {
            "expr": "avg_over_time(up{job=\"acgs-services\"}[24h]) * 100",
            "legendFormat": "{{service}}"
          }
        ]
      }
    ],
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
EOF

    print_success "Created monitoring dashboard configuration"
}

# Test health monitoring setup
test_health_monitoring() {
    print_info "Testing health monitoring setup..."
    
    # Test comprehensive health check
    if [ -x "$HEALTH_CHECK_DIR/check-all-services.sh" ]; then
        print_info "Running comprehensive health check test..."
        "$HEALTH_CHECK_DIR/check-all-services.sh" --verbose
        local exit_code=$?
        
        case $exit_code in
            0)
                print_success "All services are healthy"
                ;;
            1)
                print_warning "Some services are degraded"
                ;;
            2)
                print_error "Some services are unhealthy"
                ;;
        esac
    else
        print_error "Comprehensive health check script not found"
        return 1
    fi
    
    # Test individual service checks
    print_info "Testing individual service health checks..."
    local tested_services=0
    local working_services=0
    
    for service in "${!SERVICES[@]}"; do
        local script_file="$HEALTH_CHECK_DIR/check-${service}-service.sh"
        if [ -x "$script_file" ]; then
            if "$script_file" check > /dev/null 2>&1; then
                ((working_services++))
            fi
            ((tested_services++))
        fi
    done
    
    print_info "Individual service checks: $working_services/$tested_services working"
}

# Main execution
main() {
    print_header
    
    print_info "Setting up ACGS health monitoring system..."
    
    # Create directory structure
    create_directories
    
    # Generate configurations
    generate_health_config
    
    # Create health check scripts
    create_service_health_checks
    create_comprehensive_health_check
    
    # Create monitoring dashboard
    create_monitoring_dashboard
    
    # Test the setup
    test_health_monitoring
    
    echo
    print_success "ACGS Health Monitor setup completed successfully!"
    echo
    print_info "Available commands:"
    echo "  - Check all services: $HEALTH_CHECK_DIR/check-all-services.sh"
    echo "  - Check specific service: $HEALTH_CHECK_DIR/check-<service>-service.sh"
    echo "  - View logs: tail -f $PROJECT_ROOT/logs/health-monitoring/health-check-$(date +%Y%m%d).log"
    echo
    print_info "Configuration files:"
    echo "  - Health endpoints: $MONITORING_DIR/health-endpoints.json"
    echo "  - Dashboard config: $MONITORING_DIR/dashboards/acgs-health-dashboard.json"
}

# Run main function
main "$@"
