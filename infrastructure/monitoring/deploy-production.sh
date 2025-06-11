#!/bin/bash
# ACGS-1 Monitoring Infrastructure Production Deployment Script
# Subtask 13.8: Automated production deployment with comprehensive validation
# 
# This script automates the complete deployment of the ACGS-1 monitoring infrastructure
# for production environments with enterprise-grade security and reliability.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEPLOYMENT_LOG="/var/log/acgs/monitoring-deployment.log"
DEPLOYMENT_CONFIG="/etc/acgs/monitoring-deployment.conf"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Default configuration
ENVIRONMENT=${ENVIRONMENT:-production}
BACKUP_ENABLED=${BACKUP_ENABLED:-true}
SECURITY_HARDENING=${SECURITY_HARDENING:-true}
PERFORMANCE_VALIDATION=${PERFORMANCE_VALIDATION:-true}
MONITORING_RETENTION_DAYS=${MONITORING_RETENTION_DAYS:-15}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

info() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️ $1${NC}" | tee -a "$DEPLOYMENT_LOG"
}

# Error handling
handle_error() {
    local exit_code=$?
    error "Deployment failed at line $1 with exit code $exit_code"
    
    # Attempt rollback if deployment was in progress
    if [[ -f "/tmp/acgs-monitoring-deployment.lock" ]]; then
        warn "Attempting automatic rollback..."
        rollback_deployment
    fi
    
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# Check prerequisites
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo privileges"
        exit 1
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "curl" "jq" "openssl" "htpasswd")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command not found: $cmd"
            exit 1
        fi
    done
    
    # Check system resources
    local available_memory=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    local available_disk=$(df / | awk 'NR==2{printf "%.0f", $4/1024/1024}')
    
    if [[ $available_memory -lt 8192 ]]; then
        warn "Available memory ($available_memory MB) is below recommended 8GB"
    fi
    
    if [[ $available_disk -lt 100 ]]; then
        error "Available disk space ($available_disk GB) is below required 100GB"
        exit 1
    fi
    
    # Check network connectivity
    if ! curl -s --max-time 10 https://registry-1.docker.io/v2/ > /dev/null; then
        error "Cannot reach Docker registry. Check network connectivity."
        exit 1
    fi
    
    success "Prerequisites check completed"
}

# Initialize deployment environment
initialize_environment() {
    log "Initializing deployment environment..."
    
    # Create deployment lock
    touch "/tmp/acgs-monitoring-deployment.lock"
    
    # Create necessary directories
    mkdir -p /var/log/acgs
    mkdir -p /var/lib/acgs/monitoring
    mkdir -p /etc/acgs
    mkdir -p /etc/prometheus
    mkdir -p /etc/alertmanager
    mkdir -p /etc/grafana
    
    # Create ACGS user if not exists
    if ! id "acgs" &>/dev/null; then
        useradd -r -s /bin/false -d /var/lib/acgs acgs
        info "Created ACGS system user"
    fi
    
    # Set proper ownership
    chown -R acgs:acgs /var/log/acgs
    chown -R acgs:acgs /var/lib/acgs
    
    # Initialize deployment log
    echo "ACGS-1 Monitoring Infrastructure Deployment - $TIMESTAMP" > "$DEPLOYMENT_LOG"
    echo "Environment: $ENVIRONMENT" >> "$DEPLOYMENT_LOG"
    echo "=======================================================" >> "$DEPLOYMENT_LOG"
    
    success "Environment initialized"
}

# Generate secure configuration
generate_secure_config() {
    log "Generating secure configuration..."
    
    # Generate random passwords and keys
    local grafana_admin_password=$(openssl rand -base64 32)
    local grafana_secret_key=$(openssl rand -base64 32)
    local prometheus_password=$(openssl rand -base64 16)
    local prometheus_password_hash=$(htpasswd -nbB acgs_monitor "$prometheus_password" | cut -d: -f2)
    local backup_encryption_key=$(openssl rand -base64 32)
    
    # Create secure environment file
    cat > /etc/acgs/monitoring.env << EOF
# ACGS-1 Monitoring Infrastructure Configuration
# Generated: $TIMESTAMP
# Environment: $ENVIRONMENT

# Grafana Configuration
GRAFANA_ADMIN_USER=acgs_admin
GRAFANA_ADMIN_PASSWORD=$grafana_admin_password
GRAFANA_SECRET_KEY=$grafana_secret_key

# Prometheus Configuration
PROMETHEUS_USER=acgs_monitor
PROMETHEUS_PASSWORD=$prometheus_password
PROMETHEUS_PASSWORD_HASH=$prometheus_password_hash

# Alertmanager Configuration
SMTP_USERNAME=${SMTP_USERNAME:-acgs-alerts@acgs.ai}
SMTP_PASSWORD=${SMTP_PASSWORD:-}
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-}
PAGERDUTY_INTEGRATION_KEY=${PAGERDUTY_INTEGRATION_KEY:-}

# Security Configuration
TLS_CERT_PATH=/etc/acgs/certs
BACKUP_ENCRYPTION_KEY=$backup_encryption_key

# Performance Configuration
MONITORING_RETENTION_DAYS=$MONITORING_RETENTION_DAYS
PROMETHEUS_STORAGE_RETENTION=${MONITORING_RETENTION_DAYS}d

# Environment Settings
ENVIRONMENT=$ENVIRONMENT
DEPLOYMENT_TIMESTAMP=$TIMESTAMP
EOF
    
    # Secure the environment file
    chmod 600 /etc/acgs/monitoring.env
    chown root:root /etc/acgs/monitoring.env
    
    # Save credentials for administrator
    cat > /etc/acgs/admin-credentials.txt << EOF
ACGS-1 Monitoring Infrastructure Credentials
Generated: $TIMESTAMP

Grafana Admin Access:
  URL: http://localhost:3000
  Username: acgs_admin
  Password: $grafana_admin_password

Prometheus Access:
  URL: http://localhost:9090
  Username: acgs_monitor
  Password: $prometheus_password

Alertmanager Access:
  URL: http://localhost:9093

IMPORTANT: Store these credentials securely and delete this file after noting them.
EOF
    
    chmod 600 /etc/acgs/admin-credentials.txt
    
    success "Secure configuration generated"
    info "Admin credentials saved to /etc/acgs/admin-credentials.txt"
}

# Setup SSL/TLS certificates
setup_ssl_certificates() {
    log "Setting up SSL/TLS certificates..."
    
    mkdir -p /etc/acgs/certs
    
    # Generate self-signed certificates (replace with CA-signed in production)
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/acgs/certs/monitoring.key \
        -out /etc/acgs/certs/monitoring.crt \
        -subj "/C=US/ST=State/L=City/O=ACGS/CN=monitoring.acgs.ai" \
        -config <(
            echo '[req]'
            echo 'distinguished_name = req'
            echo '[v3_req]'
            echo 'keyUsage = keyEncipherment, dataEncipherment'
            echo 'extendedKeyUsage = serverAuth'
            echo 'subjectAltName = @alt_names'
            echo '[alt_names]'
            echo 'DNS.1 = monitoring.acgs.ai'
            echo 'DNS.2 = localhost'
            echo 'IP.1 = 127.0.0.1'
        ) \
        -extensions v3_req
    
    # Set proper permissions
    chmod 600 /etc/acgs/certs/monitoring.key
    chmod 644 /etc/acgs/certs/monitoring.crt
    chown -R root:root /etc/acgs/certs
    
    success "SSL certificates generated"
}

# Deploy monitoring configurations
deploy_configurations() {
    log "Deploying monitoring configurations..."
    
    # Source environment variables
    source /etc/acgs/monitoring.env
    
    # Deploy Prometheus configuration
    envsubst < "$SCRIPT_DIR/prometheus.yml" > /etc/prometheus/prometheus.yml
    cp -r "$SCRIPT_DIR/rules" /etc/prometheus/
    
    # Deploy Alertmanager configuration
    envsubst < "$SCRIPT_DIR/alertmanager.yml" > /etc/alertmanager/alertmanager.yml
    
    # Deploy Grafana configuration
    cp -r "$SCRIPT_DIR/grafana"/* /etc/grafana/
    
    # Set proper permissions
    chown -R prometheus:prometheus /etc/prometheus
    chown -R alertmanager:alertmanager /etc/alertmanager
    chown -R grafana:grafana /etc/grafana
    
    success "Monitoring configurations deployed"
}

# Deploy monitoring services
deploy_services() {
    log "Deploying monitoring services..."
    
    # Navigate to project directory
    cd "$PROJECT_ROOT"
    
    # Pull latest Docker images
    docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml pull
    
    # Start monitoring services
    docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d
    
    # Wait for services to be ready
    local services=("prometheus:9090" "grafana:3000" "alertmanager:9093")
    
    for service in "${services[@]}"; do
        local name=$(echo "$service" | cut -d: -f1)
        local port=$(echo "$service" | cut -d: -f2)
        
        info "Waiting for $name to be ready on port $port..."
        
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s "http://localhost:$port" > /dev/null 2>&1; then
                success "$name is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                error "$name failed to start within timeout"
                exit 1
            fi
            
            sleep 10
            ((attempt++))
        done
    done
    
    success "Monitoring services deployed successfully"
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."
    
    # Run health checks
    if ! "$SCRIPT_DIR/validate-deployment.sh"; then
        error "Deployment validation failed"
        exit 1
    fi
    
    # Run performance validation if enabled
    if [[ "$PERFORMANCE_VALIDATION" == "true" ]]; then
        info "Running performance validation..."
        if ! "$SCRIPT_DIR/run-performance-validation.sh"; then
            warn "Performance validation failed, but deployment continues"
        else
            success "Performance validation passed"
        fi
    fi
    
    success "Deployment validation completed"
}

# Setup backup procedures
setup_backup() {
    if [[ "$BACKUP_ENABLED" == "true" ]]; then
        log "Setting up backup procedures..."
        
        # Create backup script
        cp "$SCRIPT_DIR/backup-monitoring-data.sh" /usr/local/bin/
        chmod +x /usr/local/bin/backup-monitoring-data.sh
        
        # Setup cron job for daily backups
        cat > /etc/cron.d/acgs-monitoring-backup << EOF
# ACGS-1 Monitoring Backup - Daily at 2 AM
0 2 * * * root /usr/local/bin/backup-monitoring-data.sh
EOF
        
        success "Backup procedures configured"
    fi
}

# Apply security hardening
apply_security_hardening() {
    if [[ "$SECURITY_HARDENING" == "true" ]]; then
        log "Applying security hardening..."
        
        # Configure firewall rules
        ufw --force enable
        ufw default deny incoming
        ufw default allow outgoing
        
        # Allow monitoring ports
        ufw allow 9090/tcp  # Prometheus
        ufw allow 3000/tcp  # Grafana
        ufw allow 9093/tcp  # Alertmanager
        ufw allow 9101/tcp  # HAProxy Exporter
        ufw allow 9100/tcp  # Node Exporter
        
        # Allow SSH
        ufw allow ssh
        
        # Configure fail2ban for additional security
        if command -v fail2ban-server &> /dev/null; then
            systemctl enable fail2ban
            systemctl start fail2ban
        fi
        
        success "Security hardening applied"
    fi
}

# Generate deployment report
generate_deployment_report() {
    log "Generating deployment report..."
    
    local report_file="/var/log/acgs/deployment-report-$TIMESTAMP.json"
    
    cat > "$report_file" << EOF
{
  "deployment_metadata": {
    "timestamp": "$TIMESTAMP",
    "environment": "$ENVIRONMENT",
    "version": "1.0.0",
    "deployment_type": "production"
  },
  "configuration": {
    "backup_enabled": $BACKUP_ENABLED,
    "security_hardening": $SECURITY_HARDENING,
    "performance_validation": $PERFORMANCE_VALIDATION,
    "retention_days": $MONITORING_RETENTION_DAYS
  },
  "services": {
    "prometheus": {
      "port": 9090,
      "status": "$(curl -s http://localhost:9090/-/healthy > /dev/null && echo 'healthy' || echo 'unhealthy')"
    },
    "grafana": {
      "port": 3000,
      "status": "$(curl -s http://localhost:3000/api/health > /dev/null && echo 'healthy' || echo 'unhealthy')"
    },
    "alertmanager": {
      "port": 9093,
      "status": "$(curl -s http://localhost:9093/-/healthy > /dev/null && echo 'healthy' || echo 'unhealthy')"
    }
  },
  "deployment_status": "completed",
  "next_steps": [
    "Review admin credentials in /etc/acgs/admin-credentials.txt",
    "Configure external notification channels",
    "Setup monitoring for ACGS services",
    "Schedule regular maintenance procedures"
  ]
}
EOF
    
    success "Deployment report generated: $report_file"
}

# Rollback deployment
rollback_deployment() {
    warn "Rolling back deployment..."
    
    # Stop monitoring services
    cd "$PROJECT_ROOT"
    docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml down
    
    # Remove configurations
    rm -rf /etc/prometheus/*
    rm -rf /etc/alertmanager/*
    rm -rf /etc/grafana/*
    
    # Remove deployment lock
    rm -f "/tmp/acgs-monitoring-deployment.lock"
    
    warn "Deployment rolled back"
}

# Cleanup deployment
cleanup_deployment() {
    log "Cleaning up deployment..."
    
    # Remove deployment lock
    rm -f "/tmp/acgs-monitoring-deployment.lock"
    
    # Clean up temporary files
    find /tmp -name "acgs-monitoring-*" -type f -delete
    
    success "Deployment cleanup completed"
}

# Display deployment summary
display_deployment_summary() {
    echo ""
    echo "======================================================="
    echo "🎉 ACGS-1 Monitoring Infrastructure Deployment Complete"
    echo "======================================================="
    echo ""
    echo "📊 Service Endpoints:"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Grafana:      http://localhost:3000"
    echo "  Alertmanager: http://localhost:9093"
    echo ""
    echo "🔐 Admin Credentials:"
    echo "  Location: /etc/acgs/admin-credentials.txt"
    echo "  ⚠️  Please secure and delete this file after use"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Review and secure admin credentials"
    echo "  2. Configure external notification channels"
    echo "  3. Setup monitoring for ACGS services"
    echo "  4. Schedule regular maintenance procedures"
    echo ""
    echo "📖 Documentation:"
    echo "  Production Guide: infrastructure/monitoring/PRODUCTION_DEPLOYMENT_GUIDE.md"
    echo "  Operational Runbooks: infrastructure/monitoring/OPERATIONAL_RUNBOOKS.md"
    echo "  Training Guide: infrastructure/monitoring/TRAINING_GUIDE.md"
    echo ""
    echo "📞 Support:"
    echo "  Operations Team: ops@acgs.ai"
    echo "  Security Team: security@acgs.ai"
    echo ""
    echo "======================================================="
}

# Main deployment function
main() {
    log "🚀 Starting ACGS-1 Monitoring Infrastructure Production Deployment"
    log "Environment: $ENVIRONMENT"
    log "Timestamp: $TIMESTAMP"
    
    # Execute deployment steps
    check_prerequisites
    initialize_environment
    generate_secure_config
    setup_ssl_certificates
    deploy_configurations
    deploy_services
    validate_deployment
    setup_backup
    apply_security_hardening
    generate_deployment_report
    cleanup_deployment
    
    # Display summary
    display_deployment_summary
    
    success "🎉 ACGS-1 Monitoring Infrastructure deployment completed successfully!"
}

# Handle script interruption
trap 'error "Deployment interrupted"; rollback_deployment; exit 1' INT TERM

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --no-backup)
            BACKUP_ENABLED=false
            shift
            ;;
        --no-security)
            SECURITY_HARDENING=false
            shift
            ;;
        --no-validation)
            PERFORMANCE_VALIDATION=false
            shift
            ;;
        --retention-days)
            MONITORING_RETENTION_DAYS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --environment ENV     Deployment environment (default: production)"
            echo "  --no-backup          Disable backup setup"
            echo "  --no-security        Disable security hardening"
            echo "  --no-validation      Disable performance validation"
            echo "  --retention-days N   Monitoring data retention days (default: 15)"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Execute main function
main "$@"
