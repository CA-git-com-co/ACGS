#!/bin/bash

# ACGS Performance Testing Suite Deployment Script
# Deploys comprehensive performance testing infrastructure

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
TESTING_DIR="$PROJECT_ROOT/infrastructure/performance-testing"
CONFIG_DIR="$TESTING_DIR/config"
REPORTS_DIR="$TESTING_DIR/reports"
SCRIPTS_DIR="$TESTING_DIR/scripts"
TOOLS_DIR="$TESTING_DIR/tools"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}ACGS Performance Testing Deployment${NC}"
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
    print_info "Creating performance testing directory structure..."
    
    local dirs=(
        "$TESTING_DIR"
        "$CONFIG_DIR"
        "$REPORTS_DIR"
        "$SCRIPTS_DIR"
        "$TOOLS_DIR"
        "$TESTING_DIR/fixtures"
        "$TESTING_DIR/screenshots"
        "$PROJECT_ROOT/logs/performance-testing"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Install performance testing dependencies
install_dependencies() {
    print_info "Installing performance testing dependencies..."
    
    # Check if we're in a Node.js project
    if [ -f "$PROJECT_ROOT/package.json" ]; then
        cd "$PROJECT_ROOT"
        
        # Install Playwright for browser automation
        if ! npm list playwright >/dev/null 2>&1; then
            print_info "Installing Playwright..."
            npm install --save-dev playwright
            npx playwright install
            print_success "Playwright installed"
        else
            print_success "Playwright already installed"
        fi
        
        # Install Lighthouse for performance auditing
        if ! npm list lighthouse >/dev/null 2>&1; then
            print_info "Installing Lighthouse..."
            npm install --save-dev lighthouse
            print_success "Lighthouse installed"
        else
            print_success "Lighthouse already installed"
        fi
        
        # Install webpack-bundle-analyzer for bundle analysis
        if ! npm list webpack-bundle-analyzer >/dev/null 2>&1; then
            print_info "Installing webpack-bundle-analyzer..."
            npm install --save-dev webpack-bundle-analyzer
            print_success "webpack-bundle-analyzer installed"
        else
            print_success "webpack-bundle-analyzer already installed"
        fi
        
        # Install additional testing utilities
        local test_deps=("puppeteer" "jest" "@types/jest")
        for dep in "${test_deps[@]}"; do
            if ! npm list "$dep" >/dev/null 2>&1; then
                print_info "Installing $dep..."
                npm install --save-dev "$dep"
            fi
        done
        
        print_success "All dependencies installed"
    else
        print_warning "No package.json found - skipping Node.js dependencies"
    fi
}

# Generate performance testing configuration
generate_testing_config() {
    print_info "Generating performance testing configuration..."
    
    cat > "$CONFIG_DIR/performance-testing-config.json" << EOF
{
  "version": "1.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "testing": {
    "enabled": true,
    "environment": "development",
    "baseUrl": "http://localhost:3000",
    "timeout": 30000,
    "retries": 2,
    "parallel": false,
    "headless": true,
    "slowMo": 0
  },
  "thresholds": {
    "performance": {
      "loadTime": 3000,
      "firstContentfulPaint": 1800,
      "largestContentfulPaint": 2500,
      "firstInputDelay": 100,
      "cumulativeLayoutShift": 0.1,
      "speedIndex": 3000
    },
    "resources": {
      "bundleSize": 1000,
      "memoryUsage": 100,
      "networkRequests": 50,
      "totalTransferSize": 2000
    },
    "lighthouse": {
      "performance": 90,
      "accessibility": 95,
      "bestPractices": 90,
      "seo": 90
    }
  },
  "testSuites": [
    {
      "name": "Core Application Tests",
      "description": "Test core application performance",
      "tests": [
        {
          "name": "Homepage Load Test",
          "url": "/",
          "iterations": 5,
          "warmup": 2
        },
        {
          "name": "Dashboard Load Test",
          "url": "/dashboard",
          "iterations": 5,
          "warmup": 2
        }
      ]
    },
    {
      "name": "ACGS Specific Tests",
      "description": "Test ACGS-specific components",
      "tests": [
        {
          "name": "Quantumagi Dashboard Test",
          "url": "/quantumagi",
          "iterations": 3,
          "warmup": 1,
          "thresholds": {
            "loadTime": 4000,
            "memoryUsage": 120
          }
        },
        {
          "name": "Constitutional Council Test",
          "url": "/constitutional-council-dashboard",
          "iterations": 3,
          "warmup": 1
        },
        {
          "name": "Policy Synthesis Test",
          "url": "/policy-synthesis",
          "iterations": 3,
          "warmup": 1
        }
      ]
    }
  ],
  "reporting": {
    "formats": ["json", "html", "junit"],
    "outputDir": "./reports",
    "includeScreenshots": true,
    "includeTraces": false,
    "generateCharts": true
  }
}
EOF

    print_success "Performance testing configuration generated"
}

# Create Playwright test configuration
create_playwright_config() {
    print_info "Creating Playwright configuration..."
    
    cat > "$PROJECT_ROOT/playwright.config.ts" << 'EOF'
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './infrastructure/performance-testing/tests',
  fullyParallel: false,
  forbidOnly: !!processconfig/environments/development.env.CI,
  retries: processconfig/environments/development.env.CI ? 2 : 0,
  workers: processconfig/environments/development.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: './infrastructure/performance-testing/reports/playwright' }],
    ['json', { outputFile: './infrastructure/performance-testing/reports/results.json' }],
    ['junit', { outputFile: './infrastructure/performance-testing/reports/results.xml' }]
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !processconfig/environments/development.env.CI,
    timeout: 120 * 1000,
  },
});
EOF

    print_success "Playwright configuration created"
}

# Create performance test scripts
create_test_scripts() {
    print_info "Creating performance test scripts..."
    
    # Main performance test runner
    cat > "$SCRIPTS_DIR/run-performance-tests.sh" << 'EOF'
#!/bin/bash
# Performance Test Runner Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
REPORTS_DIR="$(dirname "$SCRIPT_DIR")/reports"
CONFIG_FILE="$(dirname "$SCRIPT_DIR")/config/performance-testing-config.json"

# Ensure reports directory exists
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

# Check if application is running
check_application() {
    print_info "Checking if application is running..."
    
    local base_url=$(jq -r '.testing.baseUrl' "$CONFIG_FILE" 2>/dev/null || echo "http://localhost:3000")
    
    if curl -s "$base_url" >/dev/null 2>&1; then
        print_success "Application is running at $base_url"
        return 0
    else
        print_error "Application is not running at $base_url"
        print_info "Please start the application with: npm start"
        return 1
    fi
}

# Run Playwright tests
run_playwright_tests() {
    print_info "Running Playwright performance tests..."
    
    cd "$PROJECT_ROOT"
    
    if command -v npx >/dev/null 2>&1 && [ -f "playwright.config.ts" ]; then
        npx playwright test --reporter=html,json,junit
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            print_success "Playwright tests completed successfully"
        else
            print_error "Playwright tests failed with exit code $exit_code"
        fi
        
        return $exit_code
    else
        print_warning "Playwright not available - skipping Playwright tests"
        return 0
    fi
}

# Run Lighthouse audits
run_lighthouse_audits() {
    print_info "Running Lighthouse performance audits..."
    
    local base_url=$(jq -r '.testing.baseUrl' "$CONFIG_FILE" 2>/dev/null || echo "http://localhost:3000")
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    if command -v npx >/dev/null 2>&1; then
        # Test key pages
        local pages=("/" "/dashboard" "/quantumagi")
        
        for page in "${pages[@]}"; do
            local page_name=$(echo "$page" | sed 's/\//_/g' | sed 's/^_//')
            [ -z "$page_name" ] && page_name="homepage"
            
            print_info "Auditing page: $page"
            
            npx lighthouse "$base_url$page" \
                --output=json,html \
                --output-path="$REPORTS_DIR/lighthouse-${page_name}-${timestamp}" \
                --chrome-flags="--headless --no-sandbox" \
                --quiet || print_warning "Lighthouse audit failed for $page"
        done
        
        print_success "Lighthouse audits completed"
    else
        print_warning "Lighthouse not available - skipping Lighthouse audits"
    fi
}

# Run bundle analysis
run_bundle_analysis() {
    print_info "Running bundle analysis..."
    
    cd "$PROJECT_ROOT"
    
    if command -v npx >/dev/null 2>&1 && npm list webpack-bundle-analyzer >/dev/null 2>&1; then
        # Generate bundle analysis report
        if [ -f "package.json" ] && grep -q "\"build\"" package.json; then
            npm run build >/dev/null 2>&1 || print_warning "Build failed"
            
            # Analyze bundle if build directory exists
            if [ -d "build" ]; then
                npx webpack-bundle-analyzer build/static/js/*.js \
                    --report "$REPORTS_DIR/bundle-analysis-$(date +%Y%m%d_%H%M%S).html" \
                    --mode static --no-open || print_warning "Bundle analysis failed"
                
                print_success "Bundle analysis completed"
            else
                print_warning "Build directory not found - skipping bundle analysis"
            fi
        else
            print_warning "No build script found - skipping bundle analysis"
        fi
    else
        print_warning "webpack-bundle-analyzer not available - skipping bundle analysis"
    fi
}

# Generate performance report
generate_report() {
    print_info "Generating performance report..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="$REPORTS_DIR/performance-report-${timestamp}.json"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "testRun": {
    "id": "perf-test-${timestamp}",
    "environment": "development",
    "baseUrl": "$(jq -r '.testing.baseUrl' "$CONFIG_FILE" 2>/dev/null || echo "http://localhost:3000")"
  },
  "summary": {
    "playwrightTests": "$([ -f "$REPORTS_DIR/results.json" ] && echo "completed" || echo "skipped")",
    "lighthouseAudits": "$(ls "$REPORTS_DIR"/lighthouse-*.json 2>/dev/null | wc -l) audits",
    "bundleAnalysis": "$([ -f "$REPORTS_DIR"/bundle-analysis-*.html ] && echo "completed" || echo "skipped")"
  },
  "files": {
    "playwrightResults": "results.json",
    "lighthouseReports": "lighthouse-*.json",
    "bundleAnalysis": "bundle-analysis-*.html"
  }
}
EOF
    
    print_success "Performance report generated: $report_file"
}

# Main execution
main() {
    print_info "Starting ACGS performance test suite..."
    
    # Check prerequisites
    if ! check_application; then
        exit 1
    fi
    
    # Run tests
    run_playwright_tests
    run_lighthouse_audits
    run_bundle_analysis
    
    # Generate report
    generate_report
    
    print_success "Performance testing completed!"
    print_info "Reports available in: $REPORTS_DIR"
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/run-performance-tests.sh"
    print_success "Created performance test runner script"
    
    # Bundle size monitoring script
    cat > "$SCRIPTS_DIR/monitor-bundle-size.sh" << 'EOF'
#!/bin/bash
# Bundle Size Monitoring Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
REPORTS_DIR="$(dirname "$SCRIPT_DIR")/reports"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "[INFO] $1"
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

# Analyze bundle size
analyze_bundle_size() {
    cd "$PROJECT_ROOT"
    
    if [ ! -d "build" ]; then
        print_info "Building application..."
        npm run build >/dev/null 2>&1 || {
            print_error "Build failed"
            return 1
        }
    fi
    
    print_info "Analyzing bundle size..."
    
    # Calculate total bundle size
    local total_size=0
    local js_files=()
    
    if [ -d "build/static/js" ]; then
        while IFS= read -r -d '' file; do
            js_files+=("$file")
            local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
            total_size=$((total_size + size))
        done < <(find build/static/js -name "*.js" -print0)
    fi
    
    # Convert to KB
    local total_kb=$((total_size / 1024))
    
    # Generate report
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="$REPORTS_DIR/bundle-size-${timestamp}.json"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "bundleSize": {
    "totalBytes": $total_size,
    "totalKB": $total_kb,
    "files": [
EOF
    
    # Add file details
    local first=true
    for file in "${js_files[@]}"; do
        if [ "$first" = false ]; then
            echo "," >> "$report_file"
        fi
        local filename=$(basename "$file")
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        local size_kb=$((size / 1024))
        
        cat >> "$report_file" << EOF
      {
        "name": "$filename",
        "bytes": $size,
        "kb": $size_kb
      }
EOF
        first=false
    done
    
    cat >> "$report_file" << EOF
    ]
  },
  "thresholds": {
    "warning": 800,
    "error": 1000
  },
  "status": "$([ $total_kb -gt 1000 ] && echo "error" || [ $total_kb -gt 800 ] && echo "warning" || echo "ok")"
}
EOF
    
    # Print results
    print_info "Bundle size analysis completed"
    print_info "Total bundle size: ${total_kb}KB"
    
    if [ $total_kb -gt 1000 ]; then
        print_error "Bundle size exceeds 1MB threshold!"
    elif [ $total_kb -gt 800 ]; then
        print_warning "Bundle size exceeds 800KB warning threshold"
    else
        print_success "Bundle size is within acceptable limits"
    fi
    
    print_info "Report saved: $report_file"
}

# Main execution
main() {
    analyze_bundle_size
}

main "$@"
EOF

    chmod +x "$SCRIPTS_DIR/monitor-bundle-size.sh"
    print_success "Created bundle size monitoring script"
}

# Create sample Playwright tests
create_sample_tests() {
    print_info "Creating sample Playwright tests..."
    
    local test_dir="$TESTING_DIR/tests"
    mkdir -p "$test_dir"
    
    cat > "$test_dir/performance.spec.ts" << 'EOF'
import { test, expect } from '@playwright/test';

test.describe('ACGS Performance Tests', () => {
  test('Homepage loads within performance thresholds', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Assert load time is under 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    // Check that main content is visible
    await expect(page.locator('main, #root, .App')).toBeVisible();
  });

  test('Dashboard loads and renders correctly', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Assert load time
    expect(loadTime).toBeLessThan(3000);
    
    // Check for dashboard-specific elements
    const dashboardElements = [
      'h1, h2, .dashboard-title',
      '.dashboard-content, .dashboard-main',
    ];
    
    for (const selector of dashboardElements) {
      const element = page.locator(selector).first();
      if (await element.count() > 0) {
        await expect(element).toBeVisible();
        break;
      }
    }
  });

  test('Quantumagi dashboard loads with Solana integration', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/quantumagi');
    
    // Wait longer for Solana connection
    await page.waitForTimeout(3000);
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Higher threshold for Quantumagi due to Solana integration
    expect(loadTime).toBeLessThan(5000);
    
    // Check for Quantumagi-specific elements
    const quantumagiElements = [
      '.quantumagi, .solana-dashboard',
      'h1, h2',
    ];
    
    for (const selector of quantumagiElements) {
      const element = page.locator(selector).first();
      if (await element.count() > 0) {
        await expect(element).toBeVisible();
        break;
      }
    }
  });

  test('Bundle size is within limits', async ({ page }) => {
    await page.goto('/');
    
    // Get all JavaScript resources
    const jsResources = await page.evaluate(() => {
      return performance.getEntriesByType('resource')
        .filter(entry => entry.name.includes('.js'))
        .map(entry => ({
          name: entry.name,
          size: entry.transferSize || 0
        }));
    });
    
    const totalSize = jsResources.reduce((sum, resource) => sum + resource.size, 0);
    const totalSizeKB = totalSize / 1024;
    
    console.log(`Total JS bundle size: ${totalSizeKB.toFixed(2)}KB`);
    
    // Assert bundle size is under 1MB
    expect(totalSizeKB).toBeLessThan(1000);
  });

  test('Memory usage is within limits', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Get memory usage
    const memoryUsage = await page.evaluate(() => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        return {
          used: memory.usedJSHeapSize / 1024 / 1024, // MB
          total: memory.totalJSHeapSize / 1024 / 1024, // MB
        };
      }
      return null;
    });
    
    if (memoryUsage) {
      console.log(`Memory usage: ${memoryUsage.used.toFixed(2)}MB`);
      
      // Assert memory usage is under 100MB
      expect(memoryUsage.used).toBeLessThan(100);
    }
  });
});
EOF

    print_success "Created sample Playwright tests"
}

# Test the deployment
test_deployment() {
    print_info "Testing performance testing deployment..."
    
    # Check configuration files
    local config_files=(
        "$CONFIG_DIR/performance-testing-config.json"
        "$PROJECT_ROOT/playwright.config.ts"
    )
    
    local valid=true
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Configuration file exists: $(basename "$file")"
        else
            print_error "Missing configuration file: $(basename "$file")"
            valid=false
        fi
    done
    
    # Check scripts
    local scripts=(
        "$SCRIPTS_DIR/run-performance-tests.sh"
        "$SCRIPTS_DIR/monitor-bundle-size.sh"
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
        
        # Test bundle size monitoring
        print_info "Testing bundle size monitoring..."
        if "$SCRIPTS_DIR/monitor-bundle-size.sh" >/dev/null 2>&1; then
            print_success "Bundle size monitoring test passed"
        else
            print_warning "Bundle size monitoring test failed (application may not be built)"
        fi
    else
        print_error "Some configuration files or scripts have issues"
        return 1
    fi
}

# Main execution
main() {
    print_header
    
    print_info "Deploying ACGS performance testing suite..."
    
    # Create directory structure
    create_directories
    
    # Install dependencies
    install_dependencies
    
    # Generate configurations
    generate_testing_config
    create_playwright_config
    
    # Create scripts and tests
    create_test_scripts
    create_sample_tests
    
    # Test the deployment
    test_deployment
    
    echo
    print_success "ACGS Performance Testing Suite deployed successfully!"
    echo
    print_info "Configuration files created:"
    echo "  - Testing config: $CONFIG_DIR/performance-testing-config.json"
    echo "  - Playwright config: $PROJECT_ROOT/playwright.config.ts"
    echo
    print_info "Scripts created:"
    echo "  - Run tests: $SCRIPTS_DIR/run-performance-tests.sh"
    echo "  - Monitor bundle: $SCRIPTS_DIR/monitor-bundle-size.sh"
    echo
    print_info "Sample tests created:"
    echo "  - Playwright tests: $TESTING_DIR/tests/performance.spec.ts"
    echo
    print_info "Next steps:"
    echo "  1. Start the application: npm start"
    echo "  2. Run performance tests: $SCRIPTS_DIR/run-performance-tests.sh"
    echo "  3. Monitor bundle size: $SCRIPTS_DIR/monitor-bundle-size.sh"
    echo "  4. View reports in: $REPORTS_DIR/"
    echo
    print_warning "Note:"
    echo "  - Ensure application is running before executing tests"
    echo "  - Install additional browsers: npx playwright install"
    echo "  - Configure CI/CD integration for automated testing"
}

# Run main function
main "$@"
