#!/bin/bash

# ACGS-1 Complete Service Startup Script
# Starts all 7 core services for Phase 3 completion

set -e

echo "🚀 ACGS-1 Complete Service Startup"
echo "=================================="
echo "Date: $(date)"
echo "Starting all 7 core services (ports 8000-8006)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Project root directory (current directory)
PROJECT_ROOT="/home/dislove/ACGS-2"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Service configuration with correct paths
declare -A SERVICES=(
    ["auth_service"]="8000:services/platform_services/authentication/auth_service"
    ["ac_service"]="8001:services/core/constitutional-ai/ac_service"
    ["integrity_service"]="8002:services/platform_services/integrity/integrity_service"
    ["fv_service"]="8003:services/core/formal-verification/fv_service"
    ["gs_service"]="8004:services/core/governance-synthesis/gs_service"
    ["pgc_service"]="8005:services/core/policy-governance/pgc_service"
    ["ec_service"]="8006:services/core/evolutionary-computation"
)

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2

    if curl -f -s --connect-timeout 5 --max-time 10 "http://localhost:$port/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to validate constitutional compliance
check_constitutional_compliance() {
    local service_name=$1
    local port=$2
    local compliance_threshold=0.95

    print_status "Validating constitutional compliance for $service_name..."

    # Check if service has constitutional compliance endpoint
    local compliance_response=$(curl -s --connect-timeout 5 --max-time 10 "http://localhost:$port/constitutional/compliance" 2>/dev/null || echo "")

    if [ -n "$compliance_response" ]; then
        # Extract compliance score (assuming JSON response with "compliance_score" field)
        local compliance_score=$(echo "$compliance_response" | grep -o '"compliance_score":[0-9.]*' | cut -d: -f2 | tr -d ' ')

        if [ -n "$compliance_score" ]; then
            # Compare compliance score with threshold using awk for floating point comparison
            local meets_threshold=$(awk -v score="$compliance_score" -v threshold="$compliance_threshold" 'BEGIN { print (score >= threshold) ? "1" : "0" }')

            if [ "$meets_threshold" = "1" ]; then
                print_success "$service_name constitutional compliance: $compliance_score (>= $compliance_threshold) ✓"
                return 0
            else
                print_error "$service_name constitutional compliance: $compliance_score (< $compliance_threshold) ✗"
                return 1
            fi
        else
            print_warning "$service_name constitutional compliance endpoint returned invalid score"
            return 1
        fi
    else
        print_warning "$service_name does not have constitutional compliance endpoint"
        return 1
    fi
}

# Function to validate DGM safety patterns
check_dgm_safety() {
    local service_name=$1
    local port=$2

    print_status "Validating DGM safety patterns for $service_name..."

    # Check sandbox status
    local sandbox_response=$(curl -s --connect-timeout 5 --max-time 10 "http://localhost:$port/dgm/sandbox/status" 2>/dev/null || echo "")
    if [[ "$sandbox_response" == *"active"* ]]; then
        print_success "$service_name DGM sandbox: ACTIVE ✓"
    else
        print_warning "$service_name DGM sandbox: INACTIVE"
        return 1
    fi

    # Check human review capability
    local review_response=$(curl -s --connect-timeout 5 --max-time 10 "http://localhost:$port/dgm/review/status" 2>/dev/null || echo "")
    if [[ "$review_response" == *"enabled"* ]]; then
        print_success "$service_name DGM human review: ENABLED ✓"
    else
        print_warning "$service_name DGM human review: DISABLED"
        return 1
    fi

    # Check rollback capability
    local rollback_response=$(curl -s --connect-timeout 5 --max-time 10 "http://localhost:$port/dgm/rollback/status" 2>/dev/null || echo "")
    if [[ "$rollback_response" == *"ready"* ]]; then
        print_success "$service_name DGM rollback: READY ✓"
        return 0
    else
        print_warning "$service_name DGM rollback: NOT READY"
        return 1
    fi
}

# Function to test emergency shutdown capability (<30min RTO)
test_emergency_shutdown() {
    local service_name=$1
    local port=$2

    print_status "Testing emergency shutdown capability for $service_name..."

    local start_time=$(date +%s)

    # Trigger emergency shutdown
    local shutdown_response=$(curl -s -X POST --connect-timeout 5 --max-time 10 "http://localhost:$port/emergency/shutdown" 2>/dev/null || echo "")

    if [[ "$shutdown_response" == *"initiated"* ]]; then
        # Wait for service to become unavailable
        local attempts=0
        while [ $attempts -lt 180 ]; do  # 30 minutes = 1800 seconds, check every 10 seconds
            if ! check_service "$service_name" "$port"; then
                local end_time=$(date +%s)
                local shutdown_time=$((end_time - start_time))
                local shutdown_minutes=$((shutdown_time / 60))

                if [ $shutdown_time -le 1800 ]; then  # 30 minutes = 1800 seconds
                    print_success "$service_name emergency shutdown: ${shutdown_minutes}m ${shutdown_time}s (<30min RTO) ✓"
                    return 0
                else
                    print_error "$service_name emergency shutdown: ${shutdown_minutes}m ${shutdown_time}s (>30min RTO) ✗"
                    return 1
                fi
            fi
            sleep 10
            attempts=$((attempts + 1))
        done

        print_error "$service_name emergency shutdown: TIMEOUT (>30min RTO) ✗"
        return 1
    else
        print_warning "$service_name does not support emergency shutdown endpoint"
        return 1
    fi
}

# Function to validate performance targets
check_performance_targets() {
    local service_name=$1
    local port=$2

    print_status "Validating performance targets for $service_name..."

    # Test response time (≤2s target)
    local start_time=$(date +%s%3N)  # milliseconds
    local health_response=$(curl -s --connect-timeout 5 --max-time 3 "http://localhost:$port/health" 2>/dev/null || echo "")
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))

    if [ $response_time -le 2000 ]; then  # 2000ms = 2s
        print_success "$service_name response time: ${response_time}ms (≤2s) ✓"
    else
        print_error "$service_name response time: ${response_time}ms (>2s) ✗"
        return 1
    fi

    # Test throughput capability (basic check)
    local throughput_response=$(curl -s --connect-timeout 5 --max-time 10 "http://localhost:$port/metrics/throughput" 2>/dev/null || echo "")
    if [[ "$throughput_response" == *"rps"* ]]; then
        print_success "$service_name throughput metrics: AVAILABLE ✓"
    else
        print_warning "$service_name throughput metrics: NOT AVAILABLE"
    fi

    return 0
}

# Function to stop existing service
stop_service() {
    local service_name=$1
    local port=$2
    local pid_file="$PID_DIR/${service_name}.pid"

    print_status "Stopping existing $service_name processes..."

    # Kill by PID file if exists
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_success "Stopped $service_name (PID: $pid)"
        fi
        rm -f "$pid_file"
    fi

    # Kill any uvicorn processes on the port
    pkill -f "uvicorn.*:$port" || true
    pkill -f "$service_name" || true

    # Wait for process to stop
    sleep 2
}

# Function to start a service
start_service() {
    local service_name=$1
    local config=${SERVICES[$service_name]}
    local port=$(echo $config | cut -d: -f1)
    local service_path=$(echo $config | cut -d: -f2)
    local service_dir="$PROJECT_ROOT/$service_path"
    local log_file="$LOG_DIR/${service_name}.log"
    local pid_file="$PID_DIR/${service_name}.pid"
    
    print_status "Starting $service_name on port $port..."
    
    # Check if service directory exists
    if [ ! -d "$service_dir" ]; then
        print_error "Service directory not found: $service_dir"
        return 1
    fi
    
    # Determine the correct main module path based on service structure
    local main_module=""
    local working_dir=""
    
    case $service_name in
        "auth_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "Auth service main.py not found"
                return 1
            fi
            ;;
        "ac_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "AC service main.py not found"
                return 1
            fi
            ;;
        "integrity_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "Integrity service main.py not found"
                return 1
            fi
            ;;
        "fv_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/main.py" ]; then
                main_module="main:app"
            else
                print_error "FV service main.py not found"
                return 1
            fi
            ;;
        "gs_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "GS service main.py not found"
                return 1
            fi
            ;;
        "pgc_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "PGC service main.py not found"
                return 1
            fi
            ;;
        "ec_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "EC service main.py not found"
                return 1
            fi
            ;;
    esac
    
    # Stop any existing service
    stop_service "$service_name" "$port"
    
    # Set common environment variables
    export DATABASE_URL=os.environ.get("DATABASE_URL")
    export REDIS_URL="redis://localhost:6379/0"
    export LOG_LEVEL="INFO"
    export SERVICE_PORT="$port"
    export SECRET_KEY="acgs-development-secret-key-2024-phase3-completion-testing-$(date +%s)"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    export CSRF_SECRET_KEY="acgs-development-csrf-secret-key-2024-phase3-completion"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/services:$PYTHONPATH"

    # Constitutional governance configuration
    export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
    export OPA_SERVER_URL="http://localhost:8181"
    export CONSTITUTIONAL_COMPLIANCE_THRESHOLD="0.95"
    export GOVERNANCE_VALIDATION_ENABLED="true"

    # Real AI Model Integrations
    export GOOGLE_GEMINI_ENABLED="true"
    export DEEPSEEK_R1_ENABLED="true"
    export NVIDIA_QWEN_ENABLED="true"
    export NANO_VLLM_ENABLED="true"

    # DGM Safety Patterns
    export DGM_SANDBOX_ENABLED="true"
    export DGM_HUMAN_REVIEW_ENABLED="true"
    export DGM_ROLLBACK_ENABLED="true"
    export EMERGENCY_SHUTDOWN_RTO_MINUTES="30"
    
    # Service-specific environment variables
    case $service_name in
        "auth_service")
            export AUTH_SERVICE_PORT="$port"
            ;;
        "ac_service")
            export AC_SERVICE_PORT="$port"
            ;;
        "integrity_service")
            export INTEGRITY_SERVICE_PORT="$port"
            ;;
        "fv_service")
            export FV_SERVICE_PORT="$port"
            ;;
        "gs_service")
            export GS_SERVICE_PORT="$port"
            export AC_SERVICE_URL="http://localhost:8001"
            export INTEGRITY_SERVICE_URL="http://localhost:8002"
            export FV_SERVICE_URL="http://localhost:8003"
            export PGC_SERVICE_URL="http://localhost:8005"
            export EC_SERVICE_URL="http://localhost:8006"
            export AUTH_SERVICE_URL="http://localhost:8000"
            ;;
        "pgc_service")
            export PGC_SERVICE_PORT="$port"
            ;;
        "ec_service")
            export EC_SERVICE_PORT="$port"
            ;;
    esac
    
    # Change to service directory
    cd "$working_dir"
    
    # Start the service in background with virtual environment and correct PYTHONPATH
    print_status "Executing: uvicorn $main_module --host 0.0.0.0 --port $port"
    nohup env PYTHONPATH="$PROJECT_ROOT" "$PROJECT_ROOT/.venv/bin/python" -m uvicorn "$main_module" --host 0.0.0.0 --port "$port" > "$log_file" 2>&1 &
    local service_pid=$!
    
    # Save PID
    echo "$service_pid" > "$pid_file"
    
    # Wait and check if service started
    sleep 5
    if kill -0 "$service_pid" 2>/dev/null; then
        print_success "$service_name started successfully (PID: $service_pid)"
        
        # Test health endpoint
        local attempts=0
        while [ $attempts -lt 6 ]; do
            if check_service "$service_name" "$port"; then
                print_success "$service_name health check passed"
                return 0
            fi
            print_status "Waiting for $service_name to be ready... (attempt $((attempts+1))/6)"
            sleep 5
            attempts=$((attempts+1))
        done
        
        print_warning "$service_name started but health check failed"
        return 1
    else
        print_error "$service_name failed to start. Check log: $log_file"
        return 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if PostgreSQL is running (optional for testing)
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_warning "PostgreSQL not running - services will use fallback configuration"
    else
        print_success "PostgreSQL is running"
    fi

    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        print_warning "Redis not running - services will use fallback configuration"
    else
        print_success "Redis is running"
    fi

    return 0
}

# Main execution
main() {
    print_status "Step 1: Checking prerequisites"
    if ! check_prerequisites; then
        print_error "Prerequisites check failed"
        exit 1
    fi
    
    print_status "Step 2: Starting all ACGS services"
    
    # Service startup order (dependency-aware)
    local service_order=("auth_service" "ac_service" "integrity_service" "fv_service" "gs_service" "pgc_service" "ec_service")
    local started_services=0
    local total_services=${#service_order[@]}
    
    for service_name in "${service_order[@]}"; do
        if start_service "$service_name"; then
            started_services=$((started_services + 1))
        fi
        sleep 3  # Wait between service starts
    done
    
    print_status "Step 3: Comprehensive validation"
    sleep 10  # Wait for all services to stabilize

    echo ""
    print_success "🎉 Service Startup Completed!"
    echo "================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "✅ Total services started: $started_services/$total_services"
    echo ""

    # Comprehensive validation for all services
    print_status "Step 3.1: Basic health check for all services:"
    local healthy_services=0
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)

        if check_service "$service_name" "$port"; then
            print_success "✅ $service_name (port $port): OPERATIONAL"
            healthy_services=$((healthy_services + 1))
        else
            print_error "❌ $service_name (port $port): FAILED"
        fi
    done

    print_status "Step 3.2: Constitutional compliance validation:"
    local compliant_services=0
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)

        if check_service "$service_name" "$port"; then
            if check_constitutional_compliance "$service_name" "$port"; then
                compliant_services=$((compliant_services + 1))
            fi
        fi
    done

    print_status "Step 3.3: DGM safety pattern validation:"
    local dgm_safe_services=0
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)

        if check_service "$service_name" "$port"; then
            if check_dgm_safety "$service_name" "$port"; then
                dgm_safe_services=$((dgm_safe_services + 1))
            fi
        fi
    done

    print_status "Step 3.4: Performance target validation:"
    local performant_services=0
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)

        if check_service "$service_name" "$port"; then
            if check_performance_targets "$service_name" "$port"; then
                performant_services=$((performant_services + 1))
            fi
        fi
    done
    
    echo ""
    echo "📊 ACGS-PGP System Validation Summary"
    echo "================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "✅ Services Started: $started_services/$total_services"
    echo "✅ Health Checks: $healthy_services/$total_services"
    echo "✅ Constitutional Compliance: $compliant_services/$total_services"
    echo "✅ DGM Safety Patterns: $dgm_safe_services/$total_services"
    echo "✅ Performance Targets: $performant_services/$total_services"
    echo ""

    # Calculate overall compliance percentage
    local total_checks=$((total_services * 4))  # 4 checks per service
    local passed_checks=$((healthy_services + compliant_services + dgm_safe_services + performant_services))
    local compliance_percentage=$((passed_checks * 100 / total_checks))

    echo "🎯 Overall System Compliance: $compliance_percentage%"

    if [ $compliance_percentage -ge 95 ]; then
        print_success "🎉 ACGS-PGP SYSTEM READY FOR PRODUCTION (≥95% compliance)"
    elif [ $compliance_percentage -ge 80 ]; then
        print_warning "⚠️ ACGS-PGP SYSTEM READY FOR STAGING ($compliance_percentage% compliance)"
    else
        print_error "❌ ACGS-PGP SYSTEM REQUIRES REMEDIATION (<80% compliance)"
    fi

    echo ""
    echo "📄 Logs directory: $LOG_DIR"
    echo "📄 PID files: $PID_DIR"
    echo ""
    echo "🔧 Service Management Commands:"
    echo "   Stop all services: pkill -f 'uvicorn.*:800[0-6]'"
    echo "   Check logs: tail -f $LOG_DIR/<service_name>.log"
    echo ""
    echo "🔍 Validation Commands:"
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)
        echo "   $service_name health: curl -s http://localhost:$port/health"
        echo "   $service_name compliance: curl -s http://localhost:$port/constitutional/compliance"
        echo "   $service_name DGM: curl -s http://localhost:$port/dgm/sandbox/status"
    done

    echo ""
    echo "🚨 Emergency Shutdown Command:"
    echo "   Emergency shutdown: curl -X POST http://localhost:<port>/emergency/shutdown"
    echo "   Target RTO: <30 minutes"

    if [ $started_services -eq $total_services ] && [ $compliance_percentage -ge 95 ]; then
        print_success "🎯 ACGS-PGP PRODUCTION DEPLOYMENT READY!"
        return 0
    elif [ $started_services -eq $total_services ] && [ $compliance_percentage -ge 80 ]; then
        print_warning "⚠️ ACGS-PGP STAGING DEPLOYMENT READY - Production requires ≥95% compliance"
        return 0
    else
        print_error "❌ ACGS-PGP SYSTEM VALIDATION FAILED - Check logs and remediate issues"
        return 1
    fi
}

# Run main function
main "$@"
