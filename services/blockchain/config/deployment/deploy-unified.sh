#!/bin/bash
# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Unified Deployment Script
# Deploys both expert service and blockchain components

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Default values
ENVIRONMENT="development"
DEPLOY_BLOCKCHAIN="false"
DEPLOY_EXPERT_SERVICE="true"
USE_DOCKER="true"
SKIP_TESTS="false"
VERBOSE="false"

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

# Function to show usage
show_usage() {
    cat << EOF
ACGS-2 Unified Deployment Script

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Deployment environment (development|staging|production) [default: development]
    -b, --blockchain           Deploy blockchain programs
    -s, --expert-service       Deploy expert service (default: true)
    -d, --docker              Use Docker deployment (default: true)
    -n, --native              Use native deployment (no Docker)
    -t, --skip-tests          Skip running tests
    -v, --verbose             Enable verbose output
    -h, --help                Show this help message

Environment Variables:
    GROQ_API_KEY              Groq API key for LLM integration
    OPENAI_API_KEY            OpenAI API key for LLM integration
    SOLANA_RPC_URL            Solana RPC endpoint
    GOVERNANCE_PROGRAM_ID     Deployed governance program ID
    CONSTITUTIONAL_HASH       Constitutional compliance hash (default: cdd01ef066bc6cf2)

Examples:
    # Deploy expert service only (development)
    $0

    # Deploy both expert service and blockchain
    $0 --blockchain --environment production

    # Native deployment without Docker
    $0 --native --verbose

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -b|--blockchain)
                DEPLOY_BLOCKCHAIN="true"
                shift
                ;;
            -s|--expert-service)
                DEPLOY_EXPERT_SERVICE="true"
                shift
                ;;
            -d|--docker)
                USE_DOCKER="true"
                shift
                ;;
            -n|--native)
                USE_DOCKER="false"
                shift
                ;;
            -t|--skip-tests)
                SKIP_TESTS="true"
                shift
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Validate environment
validate_environment() {
    print_status "Validating deployment environment..."
    
    case $ENVIRONMENT in
        development|staging|production)
            print_success "Environment: $ENVIRONMENT"
            ;;
        *)
            print_error "Invalid environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    # Check constitutional hash
    if [[ "${CONSTITUTIONAL_HASH:-}" != "cdd01ef066bc6cf2" ]]; then
        print_error "Constitutional hash validation failed"
        exit 1
    fi
    
    print_success "Constitutional compliance validated: $CONSTITUTIONAL_HASH"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Rust
    if ! command -v cargo &> /dev/null; then
        print_error "Rust/Cargo not found. Please install Rust."
        exit 1
    fi
    
    # Check Docker if needed
    if [[ "$USE_DOCKER" == "true" ]]; then
        if ! command -v docker &> /dev/null; then
            print_error "Docker not found. Please install Docker or use --native flag."
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose not found. Please install Docker Compose."
            exit 1
        fi
    fi
    
    # Check Solana CLI if deploying blockchain
    if [[ "$DEPLOY_BLOCKCHAIN" == "true" ]]; then
        if ! command -v solana &> /dev/null; then
            print_error "Solana CLI not found. Please install Solana CLI."
            exit 1
        fi
        
        if ! command -v anchor &> /dev/null; then
            print_error "Anchor CLI not found. Please install Anchor."
            exit 1
        fi
    fi
    
    print_success "Prerequisites check passed"
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        print_warning "Skipping tests"
        return
    fi
    
    print_status "Running tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run Rust tests
    if [[ "$VERBOSE" == "true" ]]; then
        cargo test --verbose
    else
        cargo test
    fi
    
    print_success "All tests passed"
}

# Deploy expert service
deploy_expert_service() {
    if [[ "$DEPLOY_EXPERT_SERVICE" != "true" ]]; then
        return
    fi
    
    print_status "Deploying expert service..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$USE_DOCKER" == "true" ]]; then
        # Docker deployment
        print_status "Building Docker image..."
        docker build -t acgs-expert-service:latest -f expert-service/Dockerfile .
        
        print_status "Starting services with Docker Compose..."
        docker-compose -f docker-compose.unified.yml up -d expert-service redis prometheus
        
        # Wait for service to be ready
        print_status "Waiting for expert service to be ready..."
        for i in {1..30}; do
            if curl -f http://localhost:8002/health &> /dev/null; then
                break
            fi
            sleep 2
        done
        
    else
        # Native deployment
        print_status "Building expert service..."
        cargo build --release --bin governance_app
        
        print_status "Starting expert service..."
        # Note: In production, you'd use a process manager like systemd
        nohup ./target/release/governance_app > expert-service.log 2>&1 &
        echo $! > expert-service.pid
    fi
    
    print_success "Expert service deployed successfully"
}

# Deploy blockchain programs
deploy_blockchain() {
    if [[ "$DEPLOY_BLOCKCHAIN" != "true" ]]; then
        return
    fi
    
    print_status "Deploying blockchain programs..."
    
    cd "$PROJECT_ROOT"
    
    # Build programs
    print_status "Building Anchor programs..."
    anchor build
    
    # Deploy programs
    case $ENVIRONMENT in
        development)
            print_status "Deploying to devnet..."
            solana config set --url devnet
            anchor deploy --provider.cluster devnet
            ;;
        staging)
            print_status "Deploying to testnet..."
            solana config set --url testnet
            anchor deploy --provider.cluster testnet
            ;;
        production)
            print_status "Deploying to mainnet..."
            solana config set --url mainnet-beta
            anchor deploy --provider.cluster mainnet-beta
            ;;
    esac
    
    print_success "Blockchain programs deployed successfully"
}

# Validate deployment
validate_deployment() {
    print_status "Validating deployment..."
    
    # Check expert service health
    if [[ "$DEPLOY_EXPERT_SERVICE" == "true" ]]; then
        if curl -f http://localhost:8002/health &> /dev/null; then
            print_success "Expert service is healthy"
        else
            print_error "Expert service health check failed"
            exit 1
        fi
        
        # Check constitutional compliance
        response=$(curl -s http://localhost:8002/health)
        if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
            print_success "Constitutional compliance verified"
        else
            print_error "Constitutional compliance check failed"
            exit 1
        fi
    fi
    
    # Check blockchain deployment
    if [[ "$DEPLOY_BLOCKCHAIN" == "true" ]]; then
        # Validate program deployment
        if [[ -n "${GOVERNANCE_PROGRAM_ID:-}" ]]; then
            if solana account "$GOVERNANCE_PROGRAM_ID" &> /dev/null; then
                print_success "Blockchain programs are deployed"
            else
                print_error "Blockchain program validation failed"
                exit 1
            fi
        fi
    fi
    
    print_success "Deployment validation completed"
}

# Generate deployment report
generate_report() {
    print_status "Generating deployment report..."
    
    cat > deployment-report.md << EOF
# ACGS-2 Unified Deployment Report

**Deployment Date:** $(date)
**Environment:** $ENVIRONMENT
**Constitutional Hash:** $CONSTITUTIONAL_HASH

## Components Deployed

EOF
    
    if [[ "$DEPLOY_EXPERT_SERVICE" == "true" ]]; then
        cat >> deployment-report.md << EOF
### Expert Service ✅
- **Status:** Deployed
- **Endpoint:** http://localhost:8002
- **Health Check:** http://localhost:8002/health
- **Metrics:** http://localhost:8003/metrics
- **Deployment Method:** $(if [[ "$USE_DOCKER" == "true" ]]; then echo "Docker"; else echo "Native"; fi)

EOF
    fi
    
    if [[ "$DEPLOY_BLOCKCHAIN" == "true" ]]; then
        cat >> deployment-report.md << EOF
### Blockchain Programs ✅
- **Status:** Deployed
- **Network:** $ENVIRONMENT
- **Program ID:** ${GOVERNANCE_PROGRAM_ID:-"Not set"}

EOF
    fi
    
    cat >> deployment-report.md << EOF
## Performance Targets
- **P99 Latency:** <5ms
- **Throughput:** >100 RPS
- **Cache Hit Rate:** >85%
- **Constitutional Compliance:** 100%

## Next Steps
1. Monitor system performance
2. Validate constitutional compliance
3. Run integration tests
4. Set up alerting and monitoring

---
*Generated by ACGS-2 Unified Deployment Script*
EOF
    
    print_success "Deployment report generated: deployment-report.md"
}

# Main deployment function
main() {
    print_status "Starting ACGS-2 Unified Deployment"
    print_status "Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    parse_args "$@"
    validate_environment
    check_prerequisites
    run_tests
    deploy_expert_service
    deploy_blockchain
    validate_deployment
    generate_report
    
    print_success "🎉 ACGS-2 Unified Deployment completed successfully!"
    print_status "Check deployment-report.md for details"
}

# Run main function with all arguments
main "$@"
