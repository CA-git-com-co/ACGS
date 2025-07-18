#!/bin/bash
set -euo pipefail

# ACGS Docker-in-Docker Setup Script
# Sets up Docker-in-Docker environment for ACGS services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIND_DIR="$PROJECT_ROOT/infrastructure/docker/dind"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites for Docker-in-Docker setup..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if running as root or in docker group
    if [[ $EUID -ne 0 ]] && ! groups | grep -q docker; then
        log_error "Please run as root or add your user to the docker group."
        exit 1
    fi
    
    # Check available disk space (minimum 20GB)
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 20971520 ]]; then # 20GB in KB
        log_warning "Less than 20GB available disk space. DinD may require more space."
    fi
    
    log_success "Prerequisites check completed"
}

create_dind_directories() {
    log_info "Creating Docker-in-Docker directories..."
    
    mkdir -p "$DIND_DIR/dind-config"
    mkdir -p "$DIND_DIR/certs"
    mkdir -p "$PROJECT_ROOT/logs/docker"
    mkdir -p "$PROJECT_ROOT/reports/dind"
    
    log_success "DinD directories created"
}

generate_tls_certificates() {
    log_info "Generating TLS certificates for Docker daemon..."
    
    CERT_DIR="$DIND_DIR/certs"
    
    # Generate CA private key
    openssl genrsa -out "$CERT_DIR/ca-key.pem" 4096
    
    # Generate CA certificate
    openssl req -new -x509 -days 365 -key "$CERT_DIR/ca-key.pem" -sha256 -out "$CERT_DIR/ca.pem" -subj "/C=US/ST=CA/L=San Francisco/O=ACGS/OU=Docker/CN=acgs-docker-ca"
    
    # Generate server private key
    openssl genrsa -out "$CERT_DIR/server-key.pem" 4096
    
    # Generate server certificate signing request
    openssl req -subj "/C=US/ST=CA/L=San Francisco/O=ACGS/OU=Docker/CN=docker-dind" -sha256 -new -key "$CERT_DIR/server-key.pem" -out "$CERT_DIR/server.csr"
    
    # Generate server certificate
    echo "subjectAltName = DNS:docker-dind,DNS:localhost,IP:127.0.0.1,IP:172.20.0.2" > "$CERT_DIR/extfile.cnf"
    echo "extendedKeyUsage = serverAuth" >> "$CERT_DIR/extfile.cnf"
    
    openssl x509 -req -days 365 -sha256 -in "$CERT_DIR/server.csr" -CA "$CERT_DIR/ca.pem" -CAkey "$CERT_DIR/ca-key.pem" -out "$CERT_DIR/server-cert.pem" -extfile "$CERT_DIR/extfile.cnf" -CAcreateserial
    
    # Generate client private key
    openssl genrsa -out "$CERT_DIR/client-key.pem" 4096
    
    # Generate client certificate signing request
    openssl req -subj "/C=US/ST=CA/L=San Francisco/O=ACGS/OU=Docker/CN=client" -new -key "$CERT_DIR/client-key.pem" -out "$CERT_DIR/client.csr"
    
    # Generate client certificate
    echo "extendedKeyUsage = clientAuth" > "$CERT_DIR/extfile-client.cnf"
    openssl x509 -req -days 365 -sha256 -in "$CERT_DIR/client.csr" -CA "$CERT_DIR/ca.pem" -CAkey "$CERT_DIR/ca-key.pem" -out "$CERT_DIR/client-cert.pem" -extfile "$CERT_DIR/extfile-client.cnf" -CAcreateserial
    
    # Set appropriate permissions
    chmod 400 "$CERT_DIR/ca-key.pem" "$CERT_DIR/server-key.pem" "$CERT_DIR/client-key.pem"
    chmod 444 "$CERT_DIR/ca.pem" "$CERT_DIR/server-cert.pem" "$CERT_DIR/client-cert.pem"
    
    # Clean up
    rm "$CERT_DIR/server.csr" "$CERT_DIR/client.csr" "$CERT_DIR/extfile.cnf" "$CERT_DIR/extfile-client.cnf"
    
    log_success "TLS certificates generated"
}

create_dockerfiles() {
    log_info "Creating Dockerfiles for ACGS services..."
    
    # Create base Dockerfile for ACGS services
    cat > "$PROJECT_ROOT/services/Dockerfile.base" << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for DinD support
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian bullseye stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY config/environments/requirements.txt .
RUN pip install --no-cache-dir -r config/environments/requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 acgs && chown -R acgs:acgs /app
USER acgs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT}/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${SERVICE_PORT}"]
EOF

    # Create test runner Dockerfile
    cat > "$PROJECT_ROOT/tests/Dockerfile.dind" << 'EOF'
FROM python:3.11-slim

# Install system dependencies including Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && echo "deb [arch=amd64] https://download.docker.com/linux/debian bullseye stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python testing dependencies
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy test files
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Default command
CMD ["pytest", "/app/tests", "--verbose", "--tb=short", "--junitxml=/app/reports/test-results.xml"]
EOF

    # Create test requirements
    cat > "$PROJECT_ROOT/tests/requirements-test.txt" << 'EOF'
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-xdist==3.3.1
aiohttp==3.9.1
docker==6.1.3
requests==2.31.0
pydantic==2.5.0
prometheus-client==0.19.0
nats-py==2.6.0
psycopg2-binary==2.9.9
redis==5.0.1
EOF

    log_success "Dockerfiles created"
}

setup_environment_files() {
    log_info "Setting up environment files..."
    
    # Create config/environments/development.env file for DinD
    cat > "$DIND_DIR/config/environments/development.env" << EOF
# ACGS Docker-in-Docker Environment Configuration
COMPOSE_PROJECT_NAME=acgs-dind
CONSTITUTIONAL_HASH=$CONSTITUTIONAL_HASH

# Database Configuration
POSTGRES_DB=acgs
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=os.environ.get("PASSWORD")

# Redis Configuration
REDIS_PASSWORD=os.environ.get("PASSWORD")

# Grafana Configuration
GF_SECURITY_ADMIN_PASSWORD=os.environ.get("PASSWORD")

# Docker Configuration
DOCKER_TLS_VERIFY=1
DOCKER_CERT_PATH=/certs/client
DOCKER_HOST=tcp://docker-dind:2376

# Service Ports
AUTH_SERVICE_PORT=8000
AC_SERVICE_PORT=8001
INTEGRITY_SERVICE_PORT=8002
FV_SERVICE_PORT=8003
GS_SERVICE_PORT=8004
PGC_SERVICE_PORT=8005
EC_SERVICE_PORT=8006
EOF

    log_success "Environment files created"
}

start_dind_services() {
    log_info "Starting Docker-in-Docker services..."
    
    cd "$DIND_DIR"
    
    # Pull required images
    docker-compose pull
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Docker-in-Docker services started"
}

check_service_health() {
    log_info "Checking service health..."
    
    local services=(
        "docker-dind:2376"
        "acgs-postgres-dind:5432"
        "acgs-redis-dind:6379"
        "acgs-nats-dind:4222"
    )
    
    for service in "${services[@]}"; do
        local container_name="${service%:*}"
        local port="${service#*:}"
        
        if docker ps --filter "name=$container_name" --filter "status=running" | grep -q "$container_name"; then
            log_success "$container_name is running"
        else
            log_error "$container_name is not running"
        fi
    done
}

run_integration_tests() {
    log_info "Running integration tests in DinD environment..."
    
    cd "$DIND_DIR"
    
    # Run test suite
    docker-compose --profile testing run --rm acgs-test-runner
    
    # Copy test results
    docker cp acgs-test-runner-dind:/app/reports "$PROJECT_ROOT/reports/dind-tests" 2>/dev/null || true
    
    log_success "Integration tests completed"
}

cleanup_dind() {
    log_info "Cleaning up Docker-in-Docker environment..."
    
    cd "$DIND_DIR"
    
    # Stop and remove containers
    docker-compose down -v
    
    # Remove unused images
    docker image prune -f
    
    log_success "DinD environment cleaned up"
}

show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     - Set up Docker-in-Docker environment"
    echo "  start     - Start DinD services"
    echo "  stop      - Stop DinD services"
    echo "  restart   - Restart DinD services"
    echo "  test      - Run integration tests"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  cleanup   - Clean up DinD environment"
    echo "  help      - Show this help message"
}

main() {
    case "${1:-help}" in
        setup)
            check_prerequisites
            create_dind_directories
            generate_tls_certificates
            create_dockerfiles
            setup_environment_files
            start_dind_services
            ;;
        start)
            cd "$DIND_DIR"
            docker-compose up -d
            check_service_health
            ;;
        stop)
            cd "$DIND_DIR"
            docker-compose down
            ;;
        restart)
            cd "$DIND_DIR"
            docker-compose restart
            check_service_health
            ;;
        test)
            run_integration_tests
            ;;
        status)
            cd "$DIND_DIR"
            docker-compose ps
            ;;
        logs)
            cd "$DIND_DIR"
            docker-compose logs -f "${2:-}"
            ;;
        cleanup)
            cleanup_dind
            ;;
        help|*)
            show_usage
            ;;
    esac
}

main "$@"
