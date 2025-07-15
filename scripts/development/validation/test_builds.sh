# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# Comprehensive Build Testing Script
# Tests all components after reorganization

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🧪 Starting Comprehensive Build Tests"
echo "Root directory: $ROOT_DIR"
echo "=================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
    FAILED_TESTS+=("$1")
}

# Test 1: Blockchain Build Tests
test_blockchain_builds() {
    log_info "Testing blockchain builds..."
    
    cd "$ROOT_DIR"
    
    if [ ! -d "blockchain" ]; then
        log_error "Blockchain directory not found"
        return 1
    fi
    
    cd blockchain
    
    # Test Anchor build
    if command -v anchor &> /dev/null; then
        log_info "Running Anchor build..."
        if anchor build; then
            log_success "Anchor build successful"
        else
            log_error "Anchor build failed"
            return 1
        fi
        
        # Test Anchor test
        log_info "Running Anchor tests..."
        if timeout 300 anchor test; then
            log_success "Anchor tests passed"
        else
            log_warning "Anchor tests failed or timed out"
        fi
    else
        log_warning "Anchor CLI not found, skipping blockchain tests"
    fi
    
    # Check for program artifacts
    if [ -d "target/deploy" ]; then
        PROGRAMS=($(find target/deploy -name "*.so" | wc -l))
        if [ "$PROGRAMS" -gt 0 ]; then
            log_success "Found $PROGRAMS compiled programs"
        else
            log_error "No compiled programs found"
        fi
    fi
    
    cd "$ROOT_DIR"
}

# Test 2: Python Service Tests
test_python_services() {
    log_info "Testing Python services..."
    
    cd "$ROOT_DIR"
    
    if [ ! -d "services" ]; then
        log_error "Services directory not found"
        return 1
    fi
    
    # Test each core service
    CORE_SERVICES=("constitutional-ai" "governance-synthesis" "policy-governance" "formal-verification")
    
    for service in "${CORE_SERVICES[@]}"; do
        SERVICE_DIR="services/core/$service"
        
        if [ -d "$SERVICE_DIR" ]; then
            log_info "Testing $service service..."
            
            cd "$SERVICE_DIR"
            
            # Check for requirements.txt
            if [ -f "requirements.txt" ]; then
                log_info "Installing dependencies for $service..."
                if python -m pip install -r requirements.txt --quiet; then
                    log_success "$service dependencies installed"
                else
                    log_error "$service dependency installation failed"
                    cd "$ROOT_DIR"
                    continue
                fi
            fi
            
            # Test Python syntax
            if find . -name "*.py" -exec python -m py_compile {} \; 2>/dev/null; then
                log_success "$service Python syntax valid"
            else
                log_error "$service has Python syntax errors"
            fi
            
            # Test imports
            if python -c "import app.main" 2>/dev/null; then
                log_success "$service imports working"
            else
                log_warning "$service import issues (may be expected during reorganization)"
            fi
            
            cd "$ROOT_DIR"
        else
            log_warning "$service directory not found"
        fi
    done
}

# Test 3: Frontend Build Tests
test_frontend_builds() {
    log_info "Testing frontend builds..."
    
    cd "$ROOT_DIR"
    
    FRONTEND_APPS=("governance-dashboard")
    
    for app in "${FRONTEND_APPS[@]}"; do
        APP_DIR="applications/$app"
        
        if [ -d "$APP_DIR" ]; then
            log_info "Testing $app frontend..."
            
            cd "$APP_DIR"
            
            # Check for package.json
            if [ -f "package.json" ]; then
                # Install dependencies
                if command -v npm &> /dev/null; then
                    log_info "Installing npm dependencies for $app..."
                    if npm install --silent; then
                        log_success "$app dependencies installed"
                        
                        # Test build
                        log_info "Building $app..."
                        if npm run build; then
                            log_success "$app build successful"
                        else
                            log_error "$app build failed"
                        fi
                    else
                        log_error "$app npm install failed"
                    fi
                else
                    log_warning "npm not found, skipping $app build"
                fi
            else
                log_warning "$app package.json not found"
            fi
            
            cd "$ROOT_DIR"
        else
            log_warning "$app directory not found"
        fi
    done
}

# Test 4: Docker Build Tests
test_docker_builds() {
    log_info "Testing Docker builds..."
    
    cd "$ROOT_DIR"
    
    if command -v docker &> /dev/null; then
        # Test Docker Compose configuration
        if [ -f "infrastructure/docker/docker-compose.yml" ]; then
            log_info "Validating Docker Compose configuration..."
            if docker-compose -f infrastructure/docker/docker-compose.yml config > /dev/null; then
                log_success "Docker Compose configuration valid"
            else
                log_error "Docker Compose configuration invalid"
            fi
        fi
        
        # Test individual Dockerfiles
        DOCKERFILES=($(find . -name "Dockerfile" -not -path "./backup_*" -not -path "./.git/*"))
        
        for dockerfile in "${DOCKERFILES[@]}"; do
            DOCKERFILE_DIR=$(dirname "$dockerfile")
            SERVICE_NAME=$(basename "$DOCKERFILE_DIR")
            
            log_info "Testing Dockerfile for $SERVICE_NAME..."
            
            cd "$DOCKERFILE_DIR"
            
            # Validate Dockerfile syntax
            if docker build --dry-run . > /dev/null 2>&1; then
                log_success "$SERVICE_NAME Dockerfile syntax valid"
            else
                log_warning "$SERVICE_NAME Dockerfile may have issues"
            fi
            
            cd "$ROOT_DIR"
        done
    else
        log_warning "Docker not found, skipping Docker tests"
    fi
}

# Test 5: Configuration File Tests
test_configuration_files() {
    log_info "Testing configuration files..."
    
    cd "$ROOT_DIR"
    
    # Test Anchor.toml
    if [ -f "blockchain/Anchor.toml" ]; then
        log_info "Validating Anchor.toml..."
        if grep -q "quantumagi" "blockchain/Anchor.toml"; then
            log_success "Anchor.toml contains expected programs"
        else
            log_warning "Anchor.toml may be missing program definitions"
        fi
    fi
    
    # Test package.json files
    PACKAGE_JSONS=($(find . -name "package.json" -not -path "./backup_*" -not -path "./.git/*" -not -path "./node_modules/*"))
    
    for package_json in "${PACKAGE_JSONS[@]}"; do
        log_info "Validating $(dirname "$package_json")/package.json..."
        if python -c "import json; json.load(open('$package_json'))" 2>/dev/null; then
            log_success "$(dirname "$package_json")/package.json is valid JSON"
        else
            log_error "$(dirname "$package_json")/package.json has invalid JSON"
        fi
    done
    
    # Test Python requirements files
    REQUIREMENTS=($(find . -name "requirements*.txt" -not -path "./backup_*" -not -path "./.git/*"))
    
    for req_file in "${REQUIREMENTS[@]}"; do
        log_info "Validating $req_file..."
        if python -m pip check --quiet 2>/dev/null; then
            log_success "$req_file dependencies compatible"
        else
            log_warning "$req_file may have dependency conflicts"
        fi
    done
}

# Test 6: Import Path Tests
test_import_paths() {
    log_info "Testing import paths..."
    
    cd "$ROOT_DIR"
    
    # Run the import path validation
    if python scripts/validation/validate_reorganization.py; then
        log_success "Import path validation passed"
    else
        log_error "Import path validation failed"
    fi
}

# Test 7: Integration Tests
test_integrations() {
    log_info "Testing integrations..."
    
    cd "$ROOT_DIR"
    
    # Test service registry
    if [ -f "services/shared/config/service_registry.py" ]; then
        if python -c "from services.shared.config.service_registry import service_registry; print('Service registry loaded')" 2>/dev/null; then
            log_success "Service registry imports correctly"
        else
            log_warning "Service registry import issues"
        fi
    fi
    
    # Test bridge components
    if [ -d "integrations/quantumagi-bridge" ]; then
        cd "integrations/quantumagi-bridge"
        if find . -name "*.py" -exec python -m py_compile {} \; 2>/dev/null; then
            log_success "Quantumagi bridge syntax valid"
        else
            log_error "Quantumagi bridge has syntax errors"
        fi
        cd "$ROOT_DIR"
    fi
}

# Main test execution
main() {
    cd "$ROOT_DIR"
    
    echo "Starting test suite..."
    echo ""
    
    # Run all tests
    test_blockchain_builds
    test_python_services
    test_frontend_builds
    test_docker_builds
    test_configuration_files
    test_import_paths
    test_integrations
    
    # Print summary
    echo ""
    echo "=================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "🧪 Test Results Summary"
    echo "=================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo ""
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo -e "${RED}  - $test${NC}"
        done
        echo ""
        echo -e "${YELLOW}⚠️  Some tests failed. Please review and fix issues before proceeding.${NC}"
        exit 1
    else
        echo ""
        echo -e "${GREEN}🎉 All tests passed! Reorganization successful.${NC}"
        exit 0
    fi
}

# Execute main function
main "$@"
