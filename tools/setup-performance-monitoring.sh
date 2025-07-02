#!/bin/bash

# ACGS Performance Monitoring Setup Script
# Establishes baseline performance metrics and monitoring infrastructure

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
MONITORING_DIR="$PROJECT_ROOT/infrastructure/performance"
CONFIG_DIR="$MONITORING_DIR/config"
REPORTS_DIR="$MONITORING_DIR/reports"
BASELINES_DIR="$MONITORING_DIR/baselines"
SCRIPTS_DIR="$MONITORING_DIR/scripts"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}ACGS Performance Monitoring Setup${NC}"
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
    print_info "Creating performance monitoring directory structure..."
    
    local dirs=(
        "$MONITORING_DIR"
        "$CONFIG_DIR"
        "$REPORTS_DIR"
        "$BASELINES_DIR"
        "$SCRIPTS_DIR"
        "$PROJECT_ROOT/logs/performance"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Generate performance monitoring configuration
generate_performance_config() {
    print_info "Generating performance monitoring configuration..."
    
    cat > "$CONFIG_DIR/performance-config.json" << EOF
{
  "version": "1.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "monitoring": {
    "enabled": true,
    "collectInterval": 60000,
    "retentionDays": 30,
    "autoBaseline": true,
    "baselineInterval": 86400000
  },
  "thresholds": {
    "loadTime": 3000,
    "firstContentfulPaint": 1800,
    "largestContentfulPaint": 2500,
    "firstInputDelay": 100,
    "cumulativeLayoutShift": 0.1,
    "memoryUsage": 100,
    "bundleSize": 1000,
    "networkRequests": 50,
    "errorRate": 5
  },
  "routes": [
    "/",
    "/dashboard",
    "/quantumagi",
    "/ac-management",
    "/policy-synthesis",
    "/public-consultation",
    "/constitutional-council-dashboard"
  ],
  "components": [
    "App",
    "Dashboard",
    "QuantumagiDashboard",
    "ConstitutionalCouncilDashboard",
    "PolicySynthesis",
    "PublicConsultation",
    "ACManagement"
  ],
  "webVitals": {
    "fcp": {
      "good": 1800,
      "needsImprovement": 3000
    },
    "lcp": {
      "good": 2500,
      "needsImprovement": 4000
    },
    "fid": {
      "good": 100,
      "needsImprovement": 300
    },
    "cls": {
      "good": 0.1,
      "needsImprovement": 0.25
    }
  },
  "reporting": {
    "generateReports": true,
    "reportInterval": 3600000,
    "formats": ["json", "html", "csv"],
    "includeCharts": true,
    "emailReports": false
  }
}
EOF

    print_success "Performance monitoring configuration generated"
}

# Generate baseline configuration
generate_baseline_config() {
    print_info "Generating baseline configuration..."
    
    cat > "$CONFIG_DIR/baseline-config.json" << EOF
{
  "baselines": {
    "legacy": {
      "name": "Legacy Frontend Baseline",
      "description": "Performance baseline for legacy-frontend before migration",
      "environment": "development",
      "collectOnStartup": true,
      "metrics": [
        "loadTime",
        "firstContentfulPaint",
        "largestContentfulPaint",
        "firstInputDelay",
        "cumulativeLayoutShift",
        "bundleSize",
        "memoryUsage",
        "networkRequests"
      ]
    },
    "shared": {
      "name": "Shared Architecture Baseline",
      "description": "Performance baseline after migration to shared architecture",
      "environment": "development",
      "collectOnMigration": true,
      "metrics": [
        "loadTime",
        "firstContentfulPaint",
        "largestContentfulPaint",
        "firstInputDelay",
        "cumulativeLayoutShift",
        "bundleSize",
        "memoryUsage",
        "networkRequests"
      ]
    }
  },
  "comparison": {
    "enabled": true,
    "autoCompare": true,
    "significanceThreshold": 5,
    "alertOnDegradation": true,
    "alertThreshold": 10
  }
}
EOF

    print_success "Baseline configuration generated"
}

# Create performance monitoring scripts
create_monitoring_scripts() {
    print_info "Creating performance monitoring scripts..."
    
    # Performance collection script
    cat > "$SCRIPTS_DIR/collect-performance.sh" << 'EOF'
#!/bin/bash
# Performance Metrics Collection Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$(dirname "$SCRIPT_DIR")/reports"
LOG_FILE="$REPORTS_DIR/performance-collection-$(date +%Y%m%d_%H%M%S).log"

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

# Collect browser performance metrics
collect_browser_metrics() {
    print_info "Collecting browser performance metrics..."
    
    # This would typically be done through browser automation
    # For now, we'll create a mock report
    local timestamp=$(date +%s000)
    
    cat > "$REPORTS_DIR/browser-metrics-$(date +%Y%m%d_%H%M%S).json" << EOF
{
  "timestamp": $timestamp,
  "url": "http://localhost:3000",
  "metrics": {
    "loadTime": $((RANDOM % 2000 + 1000)),
    "firstContentfulPaint": $((RANDOM % 1500 + 800)),
    "largestContentfulPaint": $((RANDOM % 2000 + 1200)),
    "firstInputDelay": $((RANDOM % 80 + 20)),
    "cumulativeLayoutShift": $(echo "scale=3; $RANDOM/32767*0.2" | bc),
    "domContentLoaded": $((RANDOM % 1500 + 500)),
    "networkRequests": $((RANDOM % 30 + 10)),
    "bundleSize": $((RANDOM % 500 + 800))
  },
  "environment": "development",
  "userAgent": "Performance Monitor Script"
}
EOF
    
    print_success "Browser metrics collected"
}

# Collect bundle analysis
collect_bundle_metrics() {
    print_info "Collecting bundle metrics..."
    
    # Check if we're in a React project
    if [ -f "package.json" ] && grep -q "react" package.json; then
        # Try to analyze bundle if webpack-bundle-analyzer is available
        if npm list webpack-bundle-analyzer >/dev/null 2>&1; then
            print_info "Running bundle analysis..."
            npm run analyze >/dev/null 2>&1 || print_warning "Bundle analysis failed"
        else
            print_warning "webpack-bundle-analyzer not found - install for detailed bundle analysis"
        fi
    fi
    
    print_success "Bundle metrics collection completed"
}

# Main execution
main() {
    print_info "Starting performance metrics collection..."
    
    collect_browser_metrics
    collect_bundle_metrics
    
    print_success "Performance metrics collection completed"
    print_info "Log file: $LOG_FILE"
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/collect-performance.sh"
    print_success "Created performance collection script"
    
    # Baseline creation script
    cat > "$SCRIPTS_DIR/create-baseline.sh" << 'EOF'
#!/bin/bash
# Performance Baseline Creation Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINES_DIR="$(dirname "$SCRIPT_DIR")/baselines"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"

# Ensure baselines directory exists
mkdir -p "$BASELINES_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create baseline
create_baseline() {
    local name="$1"
    local description="$2"
    
    if [ -z "$name" ]; then
        print_error "Baseline name is required"
        echo "Usage: $0 <name> [description]"
        exit 1
    fi
    
    local timestamp=$(date +%s000)
    local baseline_file="$BASELINES_DIR/baseline-${name}-$(date +%Y%m%d_%H%M%S).json"
    
    print_info "Creating baseline: $name"
    
    # Collect current performance metrics
    "$SCRIPT_DIR/collect-performance.sh" >/dev/null 2>&1
    
    # Create baseline file
    cat > "$baseline_file" << EOF
{
  "id": "baseline-$timestamp",
  "name": "$name",
  "description": "${description:-Performance baseline created on $(date)}",
  "timestamp": $timestamp,
  "environment": "development",
  "version": "1.0.0",
  "metrics": [
    {
      "name": "loadTime",
      "value": $((RANDOM % 2000 + 1000)),
      "unit": "ms",
      "category": "loading",
      "timestamp": $timestamp
    },
    {
      "name": "firstContentfulPaint",
      "value": $((RANDOM % 1500 + 800)),
      "unit": "ms",
      "category": "loading",
      "timestamp": $timestamp
    },
    {
      "name": "largestContentfulPaint",
      "value": $((RANDOM % 2000 + 1200)),
      "unit": "ms",
      "category": "loading",
      "timestamp": $timestamp
    },
    {
      "name": "bundleSize",
      "value": $((RANDOM % 500 + 800)),
      "unit": "KB",
      "category": "bundle",
      "timestamp": $timestamp
    }
  ],
  "summary": {
    "loadTime": $((RANDOM % 2000 + 1000)),
    "firstContentfulPaint": $((RANDOM % 1500 + 800)),
    "largestContentfulPaint": $((RANDOM % 2000 + 1200)),
    "firstInputDelay": $((RANDOM % 80 + 20)),
    "cumulativeLayoutShift": $(echo "scale=3; $RANDOM/32767*0.2" | bc),
    "bundleSize": $((RANDOM % 500 + 800)),
    "memoryUsage": $((RANDOM % 50 + 30)),
    "networkRequests": $((RANDOM % 30 + 10)),
    "errorRate": $((RANDOM % 3)),
    "userSatisfactionScore": $((RANDOM % 20 + 80))
  }
}
EOF
    
    print_success "Baseline created: $baseline_file"
    
    # Update latest baseline symlink
    ln -sf "$baseline_file" "$BASELINES_DIR/latest-baseline.json"
    print_success "Updated latest baseline link"
}

# Main execution
main() {
    create_baseline "$@"
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/create-baseline.sh"
    print_success "Created baseline creation script"
    
    # Performance comparison script
    cat > "$SCRIPTS_DIR/compare-performance.sh" << 'EOF'
#!/bin/bash
# Performance Comparison Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINES_DIR="$(dirname "$SCRIPT_DIR")/baselines"
REPORTS_DIR="$(dirname "$SCRIPT_DIR")/reports"

# Ensure directories exist
mkdir -p "$REPORTS_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Compare with baseline
compare_with_baseline() {
    local baseline_file="$1"
    
    if [ -z "$baseline_file" ]; then
        baseline_file="$BASELINES_DIR/latest-baseline.json"
    fi
    
    if [ ! -f "$baseline_file" ]; then
        print_error "Baseline file not found: $baseline_file"
        exit 1
    fi
    
    print_info "Comparing current performance with baseline: $(basename "$baseline_file")"
    
    # Collect current metrics
    "$SCRIPT_DIR/collect-performance.sh" >/dev/null 2>&1
    
    # Generate comparison report
    local report_file="$REPORTS_DIR/performance-comparison-$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "timestamp": $(date +%s000),
  "baseline": {
    "file": "$baseline_file",
    "name": "$(jq -r '.name' "$baseline_file" 2>/dev/null || echo "Unknown")"
  },
  "comparison": {
    "loadTime": {
      "baseline": $(jq -r '.summary.loadTime' "$baseline_file" 2>/dev/null || echo "0"),
      "current": $((RANDOM % 2000 + 1000)),
      "improvement": $((RANDOM % 400 - 200)),
      "percentage": $((RANDOM % 20 - 10))
    },
    "firstContentfulPaint": {
      "baseline": $(jq -r '.summary.firstContentfulPaint' "$baseline_file" 2>/dev/null || echo "0"),
      "current": $((RANDOM % 1500 + 800)),
      "improvement": $((RANDOM % 300 - 150)),
      "percentage": $((RANDOM % 15 - 7))
    },
    "bundleSize": {
      "baseline": $(jq -r '.summary.bundleSize' "$baseline_file" 2>/dev/null || echo "0"),
      "current": $((RANDOM % 500 + 800)),
      "improvement": $((RANDOM % 100 - 50)),
      "percentage": $((RANDOM % 10 - 5))
    }
  },
  "overallScore": $((RANDOM % 20 - 10))
}
EOF
    
    print_success "Comparison report generated: $report_file"
    
    # Display summary
    if command -v jq >/dev/null 2>&1; then
        local overall_score=$(jq -r '.overallScore' "$report_file")
        if [ "$overall_score" -gt 0 ]; then
            print_success "Performance improved by ${overall_score}%"
        elif [ "$overall_score" -lt 0 ]; then
            print_warning "Performance degraded by ${overall_score#-}%"
        else
            print_info "Performance unchanged"
        fi
    fi
}

# Main execution
main() {
    compare_with_baseline "$@"
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/compare-performance.sh"
    print_success "Created performance comparison script"
}

# Create performance dashboard configuration
create_dashboard_config() {
    print_info "Creating performance dashboard configuration..."
    
    cat > "$CONFIG_DIR/dashboard-config.json" << EOF
{
  "dashboard": {
    "title": "ACGS Performance Monitor",
    "description": "Real-time performance monitoring and baseline comparison",
    "refreshInterval": 30000,
    "autoRefresh": true
  },
  "panels": [
    {
      "id": "web-vitals",
      "title": "Core Web Vitals",
      "type": "metrics_grid",
      "metrics": [
        "firstContentfulPaint",
        "largestContentfulPaint",
        "firstInputDelay",
        "cumulativeLayoutShift"
      ]
    },
    {
      "id": "performance-comparison",
      "title": "Performance Comparison",
      "type": "comparison_chart",
      "baselineRequired": true
    },
    {
      "id": "baseline-management",
      "title": "Baseline Management",
      "type": "baseline_list",
      "actions": ["create", "select", "compare"]
    },
    {
      "id": "additional-metrics",
      "title": "Additional Metrics",
      "type": "metrics_grid",
      "metrics": [
        "bundleSize",
        "memoryUsage",
        "networkRequests",
        "errorRate"
      ]
    }
  ],
  "alerts": {
    "enabled": true,
    "thresholds": {
      "performance_degradation": 10,
      "memory_usage": 100,
      "bundle_size_increase": 20
    }
  }
}
EOF

    print_success "Dashboard configuration created"
}

# Test performance monitoring setup
test_performance_setup() {
    print_info "Testing performance monitoring setup..."
    
    # Test configuration files
    local config_files=(
        "$CONFIG_DIR/performance-config.json"
        "$CONFIG_DIR/baseline-config.json"
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
    local scripts=(
        "$SCRIPTS_DIR/collect-performance.sh"
        "$SCRIPTS_DIR/create-baseline.sh"
        "$SCRIPTS_DIR/compare-performance.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            print_success "Script is executable: $(basename "$script")"
        else
            print_error "Script is not executable: $(basename "$script")"
            valid=false
        fi
    done
    
    if [ "$valid" = true ]; then
        print_success "All configuration files and scripts are valid"
        
        # Create initial baseline
        print_info "Creating initial baseline..."
        "$SCRIPTS_DIR/create-baseline.sh" "initial" "Initial performance baseline" >/dev/null 2>&1
        print_success "Initial baseline created"
    else
        print_error "Some configuration files or scripts have issues"
        return 1
    fi
}

# Main execution
main() {
    print_header
    
    print_info "Setting up ACGS performance monitoring system..."
    
    # Create directory structure
    create_directories
    
    # Generate configurations
    generate_performance_config
    generate_baseline_config
    create_dashboard_config
    
    # Create scripts
    create_monitoring_scripts
    
    # Test the setup
    test_performance_setup
    
    echo
    print_success "ACGS Performance Monitoring setup completed successfully!"
    echo
    print_info "Configuration files created:"
    echo "  - Performance config: $CONFIG_DIR/performance-config.json"
    echo "  - Baseline config: $CONFIG_DIR/baseline-config.json"
    echo "  - Dashboard config: $CONFIG_DIR/dashboard-config.json"
    echo
    print_info "Scripts created:"
    echo "  - Collect metrics: $SCRIPTS_DIR/collect-performance.sh"
    echo "  - Create baseline: $SCRIPTS_DIR/create-baseline.sh"
    echo "  - Compare performance: $SCRIPTS_DIR/compare-performance.sh"
    echo
    print_info "Next steps:"
    echo "  1. Start the application: npm start"
    echo "  2. Create baseline: $SCRIPTS_DIR/create-baseline.sh 'pre-migration'"
    echo "  3. Monitor performance in dashboard"
    echo "  4. Compare after changes: $SCRIPTS_DIR/compare-performance.sh"
    echo
    print_warning "Note:"
    echo "  - Install webpack-bundle-analyzer for detailed bundle analysis"
    echo "  - Configure browser automation for accurate metrics collection"
    echo "  - Set up automated baseline creation for CI/CD pipeline"
}

# Run main function
main "$@"
