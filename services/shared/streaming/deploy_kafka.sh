#!/bin/bash

# Kafka Enterprise Streaming Infrastructure Deployment Script
# For ACGS (Advanced Constitutional Governance System)
# Implements the ACGE technical validation recommendations

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

# Configuration
ENVIRONMENT="${ENVIRONMENT:-development}"
KAFKA_VERSION="${KAFKA_VERSION:-7.4.0}"
COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.kafka.yml"

# Functions
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
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    # Check available disk space (minimum 10GB)
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
        log_warning "Less than 10GB disk space available. Kafka may need more space for production use."
    fi

    # Check available memory (minimum 8GB)
    available_memory=$(free -m | awk 'NR==2{print $7}')
    if [ "$available_memory" -lt 8192 ]; then  # 8GB in MB
        log_warning "Less than 8GB memory available. Kafka cluster may perform poorly."
    fi

    log_success "Prerequisites check completed"
}

create_directories() {
    log_info "Creating necessary directories..."

    # Create monitoring directory if it doesn't exist
    mkdir -p "${SCRIPT_DIR}/monitoring"

    # Create config directories
    mkdir -p "${SCRIPT_DIR}/configs/clusters"
    mkdir -p "${SCRIPT_DIR}/configs/topics"
    mkdir -p "${SCRIPT_DIR}/configs/security"

    # Create data directories (Docker will create these, but good to ensure permissions)
    mkdir -p "${SCRIPT_DIR}/data/kafka-1"
    mkdir -p "${SCRIPT_DIR}/data/kafka-2"
    mkdir -p "${SCRIPT_DIR}/data/kafka-3"
    mkdir -p "${SCRIPT_DIR}/data/zookeeper"
    mkdir -p "${SCRIPT_DIR}/data/nats"

    log_success "Directories created"
}

validate_configuration() {
    log_info "Validating configuration..."

    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi

    # Validate compose file syntax
    if ! docker-compose -f "$COMPOSE_FILE" config &> /dev/null; then
        log_error "Docker Compose file has syntax errors"
        exit 1
    fi

    # Check if JMX config exists
    if [ ! -f "${SCRIPT_DIR}/monitoring/jmx-kafka-config.yml" ]; then
        log_warning "JMX configuration file not found. Metrics collection may not work properly."
    fi

    log_success "Configuration validation completed"
}

pull_images() {
    log_info "Pulling Docker images..."

    # Pull all required images
    docker-compose -f "$COMPOSE_FILE" pull

    log_success "Docker images pulled successfully"
}

start_infrastructure() {
    log_info "Starting Kafka infrastructure..."

    # Start the services
    docker-compose -f "$COMPOSE_FILE" up -d

    log_info "Waiting for services to start..."
    sleep 30

    # Check service health
    check_service_health

    log_success "Kafka infrastructure started successfully"
}

check_service_health() {
    log_info "Checking service health..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check Zookeeper
        if docker exec acgs-zookeeper bash -c "echo ruok | nc localhost 2181" | grep -q "imok"; then
            log_success "Zookeeper is healthy"
        else
            log_warning "Zookeeper is not ready yet"
        fi

        # Check Kafka brokers
        local kafka_healthy=0
        for broker in acgs-kafka-1 acgs-kafka-2 acgs-kafka-3; do
            if docker exec "$broker" kafka-broker-api-versions --bootstrap-server localhost:9092 &> /dev/null; then
                log_success "$broker is healthy"
                ((kafka_healthy++))
            else
                log_warning "$broker is not ready yet"
            fi
        done

        # Check if majority of brokers are healthy
        if [ $kafka_healthy -ge 2 ]; then
            log_success "Kafka cluster is healthy (${kafka_healthy}/3 brokers)"
            break
        fi

        if [ $attempt -eq $max_attempts ]; then
            log_error "Services did not become healthy within expected time"
            show_service_logs
            exit 1
        fi

        sleep 10
        ((attempt++))
    done
}

show_service_logs() {
    log_info "Showing service logs for debugging..."

    echo "=== Zookeeper Logs ==="
    docker logs acgs-zookeeper --tail 20

    echo "=== Kafka-1 Logs ==="
    docker logs acgs-kafka-1 --tail 20

    echo "=== Kafka-2 Logs ==="
    docker logs acgs-kafka-2 --tail 20

    echo "=== Kafka-3 Logs ==="
    docker logs acgs-kafka-3 --tail 20
}

verify_topics() {
    log_info "Verifying Kafka topics..."

    # Wait for topics to be created
    sleep 10

    # List topics
    local topics=$(docker exec acgs-kafka-1 kafka-topics --list --bootstrap-server localhost:9092)

    log_info "Created topics:"
    echo "$topics"

    # Check for essential topics
    local essential_topics=("constitutional-decisions" "policy-synthesis" "governance-actions" "audit-events")

    for topic in "${essential_topics[@]}"; do
        if echo "$topics" | grep -q "^${topic}$"; then
            log_success "Essential topic '$topic' created successfully"
        else
            log_error "Essential topic '$topic' not found"
        fi
    done
}

show_cluster_info() {
    log_info "Cluster Information:"
    echo "===================="

    echo "Kafka Brokers:"
    echo "  - kafka-1: localhost:9092"
    echo "  - kafka-2: localhost:9093"
    echo "  - kafka-3: localhost:9094"
    echo ""

    echo "Web Interfaces:"
    echo "  - Kafka UI: http://localhost:8080"
    echo "  - Schema Registry: http://localhost:8081"
    echo "  - Kafka Connect: http://localhost:8083"
    echo "  - NATS Monitoring: http://localhost:8222"
    echo "  - JMX Metrics: http://localhost:5556/metrics"
    echo ""

    echo "Configuration:"
    echo "  - Environment: $ENVIRONMENT"
    echo "  - Kafka Version: $KAFKA_VERSION"
    echo "  - Replication Factor: 3"
    echo "  - Min In-Sync Replicas: 2"
    echo ""

    echo "Data Volumes:"
    docker volume ls | grep -E "(kafka|zookeeper|nats)"
    echo ""

    echo "Running Containers:"
    docker-compose -f "$COMPOSE_FILE" ps
}

stop_infrastructure() {
    log_info "Stopping Kafka infrastructure..."

    docker-compose -f "$COMPOSE_FILE" down

    log_success "Kafka infrastructure stopped"
}

cleanup_infrastructure() {
    log_info "Cleaning up Kafka infrastructure..."

    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans

    # Remove associated volumes
    docker volume prune -f

    # Remove network
    docker network rm acgs-streaming-network 2>/dev/null || true

    log_success "Kafka infrastructure cleaned up"
}

show_help() {
    echo "ACGS Kafka Enterprise Streaming Infrastructure Deployment"
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the Kafka infrastructure (default)"
    echo "  stop      Stop the Kafka infrastructure"
    echo "  restart   Restart the Kafka infrastructure"
    echo "  status    Show status of services"
    echo "  logs      Show logs for all services"
    echo "  cleanup   Stop and remove all containers and volumes"
    echo "  topics    List all Kafka topics"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ENVIRONMENT      Deployment environment (default: development)"
    echo "  KAFKA_VERSION    Kafka version to use (default: 7.4.0)"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  ENVIRONMENT=production $0 start"
    echo "  $0 logs kafka-1"
}

# Main script logic
main() {
    local command="${1:-start}"

    case "$command" in
        start)
            log_info "Starting ACGS Kafka Enterprise Streaming Infrastructure"
            check_prerequisites
            create_directories
            validate_configuration
            pull_images
            start_infrastructure
            verify_topics
            show_cluster_info
            ;;
        stop)
            stop_infrastructure
            ;;
        restart)
            stop_infrastructure
            sleep 5
            start_infrastructure
            verify_topics
            show_cluster_info
            ;;
        status)
            docker-compose -f "$COMPOSE_FILE" ps
            ;;
        logs)
            local service="${2:-}"
            if [ -n "$service" ]; then
                docker-compose -f "$COMPOSE_FILE" logs -f "$service"
            else
                docker-compose -f "$COMPOSE_FILE" logs -f
            fi
            ;;
        cleanup)
            cleanup_infrastructure
            ;;
        topics)
            docker exec acgs-kafka-1 kafka-topics --list --bootstrap-server localhost:9092
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
