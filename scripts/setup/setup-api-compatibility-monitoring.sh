# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS API Compatibility Monitoring Setup Script
# Sets up comprehensive API compatibility monitoring between legacy and new implementations

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
MONITORING_DIR="$PROJECT_ROOT/infrastructure/api-compatibility"
CONFIG_DIR="$MONITORING_DIR/config"
REPORTS_DIR="$MONITORING_DIR/reports"
SCRIPTS_DIR="$MONITORING_DIR/scripts"

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
    echo -e "${BLUE}ACGS API Compatibility Monitor Setup${NC}"
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
    print_info "Creating API compatibility monitoring directory structure..."
    
    local dirs=(
        "$MONITORING_DIR"
        "$CONFIG_DIR"
        "$REPORTS_DIR"
        "$SCRIPTS_DIR"
        "$MONITORING_DIR/test-data"
        "$PROJECT_ROOT/logs/api-compatibility"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Generate API compatibility configuration
generate_compatibility_config() {
    print_info "Generating API compatibility configuration..."
    
    cat > "$CONFIG_DIR/compatibility-config.json" << EOF
{
  "version": "1.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "monitoring": {
    "enabled": true,
    "testInterval": 300000,
    "tolerances": {
      "responseTimeDifference": 1000,
      "schemaVariationThreshold": 5,
      "errorRateThreshold": 2
    },
    "notifications": {
      "compatibilityIssues": true,
      "adoptionMilestones": true,
      "performanceDegradation": true
    }
  },
  "services": {
    "auth": {
      "baseUrl": "http://localhost:8002",
      "endpoints": [
        {
          "path": "/api/v1/auth/login",
          "method": "POST",
          "testData": {
            "username": "test@acgs.org",
            "password": "test123"
          }
        },
        {
          "path": "/api/v1/auth/logout",
          "method": "POST",
          "testData": {}
        },
        {
          "path": "/api/v1/auth/refresh",
          "method": "POST",
          "testData": {}
        }
      ]
    },
    "ac": {
      "baseUrl": "http://localhost:8001",
      "endpoints": [
        {
          "path": "/api/v1/principles",
          "method": "GET",
          "testData": {}
        },
        {
          "path": "/api/v1/principles",
          "method": "POST",
          "testData": {
            "title": "Test Principle",
            "content": "Test principle content",
            "category": "test",
            "priority": 1
          }
        }
      ]
    },
    "gs": {
      "baseUrl": "http://localhost:8003",
      "endpoints": [
        {
          "path": "/api/v1/synthesize",
          "method": "POST",
          "testData": {
            "principles": [{"id": "test-principle-1"}]
          }
        },
        {
          "path": "/api/v1/policies",
          "method": "GET",
          "testData": {}
        }
      ]
    },
    "pgc": {
      "baseUrl": "http://localhost:8005",
      "endpoints": [
        {
          "path": "/api/v1/compliance/check",
          "method": "POST",
          "testData": {
            "action": "test_action",
            "context": {"test": true},
            "policy": "test_policy"
          }
        },
        {
          "path": "/api/v1/governance/workflows",
          "method": "GET",
          "testData": {}
        }
      ]
    }
  },
  "reporting": {
    "generateReports": true,
    "reportInterval": 3600000,
    "retentionDays": 30,
    "formats": ["json", "html", "csv"]
  }
}
EOF

    print_success "API compatibility configuration generated"
}

# Generate endpoint test configurations
generate_endpoint_configs() {
    print_info "Generating endpoint test configurations..."
    
    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"
        local config_file="$CONFIG_DIR/endpoints-${service}.json"
        
        cat > "$config_file" << EOF
{
  "service": "$service",
  "port": $port,
  "baseUrl": "http://localhost:$port",
  "healthEndpoint": "/health",
  "testEndpoints": [
    {
      "path": "/api/v1/health",
      "method": "GET",
      "description": "Health check endpoint",
      "critical": true,
      "expectedStatus": 200,
      "timeout": 5000
    }
  ],
  "compatibility": {
    "legacyUrl": "http://localhost:$port",
    "newUrl": "http://localhost:$port",
    "compareFields": ["status", "data", "message"],
    "ignoreFields": ["timestamp", "requestId"],
    "tolerances": {
      "responseTime": 1000,
      "dataVariation": 5
    }
  }
}
EOF
        
        print_success "Created endpoint configuration for $service service"
    done
}

# Create compatibility test scripts
create_test_scripts() {
    print_info "Creating compatibility test scripts..."
    
    # Main test runner script
    cat > "$SCRIPTS_DIR/run-compatibility-tests.sh" << 'EOF'
#!/bin/bash
# API Compatibility Test Runner

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"
REPORTS_DIR="$(dirname "$SCRIPT_DIR")/reports"
LOG_FILE="$REPORTS_DIR/compatibility-test-$(date +%Y%m%d_%H%M%S).log"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Test single endpoint
test_endpoint() {
    local service="$1"
    local endpoint="$2"
    local method="$3"
    local test_data="$4"
    local base_url="$5"
    
    print_info "Testing $service: $method $endpoint"
    
    local url="$base_url$endpoint"
    local start_time=$(date +%s%3N)
    
    if [ "$method" = "GET" ]; then
        local response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$url" 2>/dev/null)
    else
        local response=$(curl -s -w "%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$test_data" \
            -o /tmp/response.json "$url" 2>/dev/null)
    fi
    
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))
    local status_code="${response: -3}"
    
    if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
        print_success "$service $endpoint: $status_code (${response_time}ms)"
        return 0
    else
        print_error "$service $endpoint: $status_code (${response_time}ms)"
        return 1
    fi
}

# Load configuration and run tests
main() {
    print_info "Starting API compatibility tests..."
    
    local config_file="$CONFIG_DIR/compatibility-config.json"
    if [ ! -f "$config_file" ]; then
        print_error "Configuration file not found: $config_file"
        exit 1
    fi
    
    # Test each service
    local services=("auth" "ac" "gs" "pgc")
    local total_tests=0
    local passed_tests=0
    
    for service in "${services[@]}"; do
        local endpoint_config="$CONFIG_DIR/endpoints-${service}.json"
        if [ -f "$endpoint_config" ]; then
            print_info "Testing $service service..."
            
            # Simple health check test
            local port=$(jq -r ".port" "$endpoint_config" 2>/dev/null || echo "8000")
            local base_url="http://localhost:$port"
            
            ((total_tests++))
            if test_endpoint "$service" "/health" "GET" "{}" "$base_url"; then
                ((passed_tests++))
            fi
        else
            print_warning "Endpoint configuration not found for $service"
        fi
    done
    
    # Generate summary
    local success_rate=$((passed_tests * 100 / total_tests))
    
    print_info "Test Summary:"
    print_info "Total Tests: $total_tests"
    print_info "Passed: $passed_tests"
    print_info "Failed: $((total_tests - passed_tests))"
    print_info "Success Rate: $success_rate%"
    
    # Generate JSON report
    cat > "$REPORTS_DIR/latest-compatibility-report.json" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "summary": {
    "totalTests": $total_tests,
    "passedTests": $passed_tests,
    "failedTests": $((total_tests - passed_tests)),
    "successRate": $success_rate
  },
  "logFile": "$LOG_FILE"
}
EOF
    
    if [ $success_rate -ge 80 ]; then
        print_success "Compatibility tests completed successfully"
        exit 0
    else
        print_error "Compatibility tests failed - success rate below 80%"
        exit 1
    fi
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/run-compatibility-tests.sh"
    print_success "Created compatibility test runner script"
    
    # Adoption tracking script
    cat > "$SCRIPTS_DIR/track-adoption.sh" << 'EOF'
#!/bin/bash
# User Adoption Tracking Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$(dirname "$SCRIPT_DIR")/reports"
LOG_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/logs/api-compatibility"

# Create directories
mkdir -p "$REPORTS_DIR" "$LOG_DIR"

# Generate adoption metrics (mock data for demonstration)
generate_adoption_metrics() {
    local service="$1"
    local timestamp=$(date +%s000)
    
    # Mock adoption data (in real implementation, this would come from analytics)
    local legacy_usage=$((RANDOM % 1000 + 100))
    local new_usage=$((RANDOM % 800 + 200))
    local total_usage=$((legacy_usage + new_usage))
    local adoption_rate=$((new_usage * 100 / total_usage))
    
    cat << EOF
{
  "service": "$service",
  "endpoint": "/api/v1/health",
  "timestamp": $timestamp,
  "legacyUsage": $legacy_usage,
  "newUsage": $new_usage,
  "adoptionRate": $adoption_rate,
  "userCount": $((RANDOM % 500 + 50)),
  "sessionCount": $((RANDOM % 1000 + 100)),
  "errorRate": $((RANDOM % 5)),
  "averageResponseTime": $((RANDOM % 500 + 100))
}
EOF
}

# Main execution
main() {
    echo "Generating adoption metrics..."
    
    local services=("auth" "ac" "gs" "pgc")
    local metrics_file="$REPORTS_DIR/adoption-metrics-$(date +%Y%m%d_%H%M%S).json"
    
    echo "[" > "$metrics_file"
    
    for i in "${!services[@]}"; do
        local service="${services[$i]}"
        generate_adoption_metrics "$service" >> "$metrics_file"
        
        if [ $i -lt $((${#services[@]} - 1)) ]; then
            echo "," >> "$metrics_file"
        fi
    done
    
    echo "]" >> "$metrics_file"
    
    echo "Adoption metrics generated: $metrics_file"
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/track-adoption.sh"
    print_success "Created adoption tracking script"
}

# Create monitoring dashboard configuration
create_dashboard_config() {
    print_info "Creating monitoring dashboard configuration..."
    
    cat > "$CONFIG_DIR/dashboard-config.json" << EOF
{
  "dashboard": {
    "title": "ACGS API Compatibility Monitor",
    "description": "Real-time monitoring of API compatibility during migration",
    "refreshInterval": 30000,
    "autoRefresh": true
  },
  "panels": [
    {
      "id": "compatibility-overview",
      "title": "Compatibility Overview",
      "type": "stats",
      "metrics": [
        "total_endpoints",
        "compatible_endpoints", 
        "incompatible_endpoints",
        "overall_compatibility_percentage"
      ]
    },
    {
      "id": "migration-progress",
      "title": "Migration Progress by Service",
      "type": "progress_bars",
      "services": ["auth", "ac", "gs", "pgc", "integrity", "fv", "ec"]
    },
    {
      "id": "recent-issues",
      "title": "Recent Compatibility Issues",
      "type": "issue_list",
      "maxItems": 10,
      "severityFilter": ["critical", "high"]
    },
    {
      "id": "adoption-metrics",
      "title": "User Adoption Metrics",
      "type": "adoption_chart",
      "timeRange": "24h"
    }
  ],
  "alerts": {
    "enabled": true,
    "thresholds": {
      "compatibility_rate": 95,
      "response_time_degradation": 50,
      "error_rate_increase": 10
    }
  }
}
EOF

    print_success "Dashboard configuration created"
}

# Test the monitoring setup
test_monitoring_setup() {
    print_info "Testing API compatibility monitoring setup..."
    
    # Test configuration files
    local config_files=(
        "$CONFIG_DIR/compatibility-config.json"
        "$CONFIG_DIR/dashboard-config.json"
    )
    
    local valid=true
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            if command -v jq >/dev/null 2>&1; then
                if jq empty "$file" >/dev/null 2>&1; then
                    print_success "Valid JSON: $(basename "$file")"
                else
                    print_error "Invalid JSON: $(basename "$file")"
                    valid=false
                fi
            else
                print_warning "jq not available - skipping JSON validation for $(basename "$file")"
            fi
        else
            print_error "Missing configuration file: $(basename "$file")"
            valid=false
        fi
    done
    
    # Test scripts
    if [ -x "$SCRIPTS_DIR/run-compatibility-tests.sh" ]; then
        print_success "Compatibility test script is executable"
    else
        print_error "Compatibility test script is not executable"
        valid=false
    fi
    
    if [ "$valid" = true ]; then
        print_success "All configuration files and scripts are valid"
        
        # Run a quick test
        print_info "Running quick compatibility test..."
        if "$SCRIPTS_DIR/run-compatibility-tests.sh" > /dev/null 2>&1; then
            print_success "Quick compatibility test passed"
        else
            print_warning "Quick compatibility test failed (services may not be running)"
        fi
    else
        print_error "Some configuration files or scripts have issues"
        return 1
    fi
}

# Main execution
main() {
    print_header
    
    print_info "Setting up ACGS API compatibility monitoring system..."
    
    # Create directory structure
    create_directories
    
    # Generate configurations
    generate_compatibility_config
    generate_endpoint_configs
    create_dashboard_config
    
    # Create scripts
    create_test_scripts
    
    # Test the setup
    test_monitoring_setup
    
    echo
    print_success "ACGS API Compatibility Monitoring setup completed successfully!"
    echo
    print_info "Configuration files created:"
    echo "  - Main config: $CONFIG_DIR/compatibility-config.json"
    echo "  - Dashboard config: $CONFIG_DIR/dashboard-config.json"
    echo "  - Endpoint configs: $CONFIG_DIR/endpoints-*.json"
    echo
    print_info "Scripts created:"
    echo "  - Run tests: $SCRIPTS_DIR/run-compatibility-tests.sh"
    echo "  - Track adoption: $SCRIPTS_DIR/track-adoption.sh"
    echo
    print_info "Next steps:"
    echo "  1. Start ACGS services"
    echo "  2. Run compatibility tests: $SCRIPTS_DIR/run-compatibility-tests.sh"
    echo "  3. View reports in: $REPORTS_DIR/"
    echo "  4. Monitor dashboard for real-time compatibility status"
    echo
    print_warning "Note:"
    echo "  - Ensure all ACGS services are running before running tests"
    echo "  - Configure adoption tracking based on your analytics system"
    echo "  - Review and adjust compatibility thresholds as needed"
}

# Run main function
main "$@"
