#!/bin/bash
"""
ACGS HashiCorp Vault Deployment Script
Deploys and configures HashiCorp Vault for ACGS secrets management.
"""

set -euo pipefail

# Configuration
VAULT_VERSION="1.15.2"
VAULT_PORT="8200"
VAULT_DATA_DIR="/opt/vault/data"
VAULT_CONFIG_DIR="/opt/vault/config"
VAULT_LOG_DIR="/opt/vault/logs"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        error "curl is required but not installed"
        exit 1
    fi
    
    # Check if unzip is installed
    if ! command -v unzip &> /dev/null; then
        error "unzip is required but not installed"
        exit 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        warn "jq is not installed - some features may not work properly"
    fi
    
    log "Prerequisites check completed"
}

# Download and install Vault
install_vault() {
    log "Installing HashiCorp Vault ${VAULT_VERSION}..."
    
    # Create vault user if it doesn't exist
    if ! id "vault" &>/dev/null; then
        sudo useradd --system --home /opt/vault --shell /bin/false vault
        log "Created vault user"
    fi
    
    # Create directories
    sudo mkdir -p ${VAULT_DATA_DIR} ${VAULT_CONFIG_DIR} ${VAULT_LOG_DIR}
    sudo mkdir -p /usr/local/bin
    
    # Download Vault
    VAULT_ZIP="vault_${VAULT_VERSION}_linux_amd64.zip"
    VAULT_URL="https://releases.hashicorp.com/vault/${VAULT_VERSION}/${VAULT_ZIP}"
    
    cd /tmp
    curl -O ${VAULT_URL}
    
    # Verify download (optional - add checksum verification here)
    if [[ ! -f ${VAULT_ZIP} ]]; then
        error "Failed to download Vault"
        exit 1
    fi
    
    # Extract and install
    unzip -o ${VAULT_ZIP}
    sudo mv vault /usr/local/bin/
    sudo chmod +x /usr/local/bin/vault
    
    # Set ownership
    sudo chown -R vault:vault /opt/vault
    
    # Clean up
    rm -f ${VAULT_ZIP}
    
    log "Vault ${VAULT_VERSION} installed successfully"
}

# Create Vault configuration
create_vault_config() {
    log "Creating Vault configuration..."
    
    # Create main configuration file
    sudo tee ${VAULT_CONFIG_DIR}/vault.hcl > /dev/null <<EOF
# ACGS Vault Configuration
# Constitutional Hash: ${CONSTITUTIONAL_HASH}

storage "file" {
  path = "${VAULT_DATA_DIR}"
}

listener "tcp" {
  address     = "0.0.0.0:${VAULT_PORT}"
  tls_disable = 1
  # Note: In production, enable TLS
  # tls_cert_file = "/opt/vault/tls/vault.crt"
  # tls_key_file  = "/opt/vault/tls/vault.key"
}

api_addr = "http://127.0.0.1:${VAULT_PORT}"
cluster_addr = "https://127.0.0.1:8201"
ui = true

# Disable mlock for development (enable in production)
disable_mlock = true

# Logging
log_level = "INFO"
log_file = "${VAULT_LOG_DIR}/vault.log"
log_rotate_duration = "24h"
log_rotate_max_files = 30

# Telemetry for monitoring
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}

# ACGS-specific configuration
default_lease_ttl = "768h"  # 32 days
max_lease_ttl = "8760h"     # 1 year

# Plugin directory
plugin_directory = "/opt/vault/plugins"
EOF

    # Set proper permissions
    sudo chown vault:vault ${VAULT_CONFIG_DIR}/vault.hcl
    sudo chmod 640 ${VAULT_CONFIG_DIR}/vault.hcl
    
    log "Vault configuration created"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    sudo tee /etc/systemd/system/vault.service > /dev/null <<EOF
[Unit]
Description=HashiCorp Vault - ACGS Secrets Management
Documentation=https://www.vaultproject.io/docs/
Requires=network-online.target
After=network-online.target
ConditionFileNotEmpty=${VAULT_CONFIG_DIR}/vault.hcl
StartLimitIntervalSec=60
StartLimitBurst=3

[Service]
Type=notify
User=vault
Group=vault
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
SecureBits=keep-caps
AmbientCapabilities=CAP_IPC_LOCK
CapabilityBoundingSet=CAP_SYSLOG CAP_IPC_LOCK
NoNewPrivileges=yes
ExecStart=/usr/local/bin/vault server -config=${VAULT_CONFIG_DIR}/vault.hcl
ExecReload=/bin/kill --signal HUP \$MAINPID
KillMode=process
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
StartLimitInterval=60
StartLimitBurst=3
LimitNOFILE=65536
LimitMEMLOCK=infinity

# Environment
Environment=VAULT_ADDR=http://127.0.0.1:${VAULT_PORT}
Environment=VAULT_API_ADDR=http://127.0.0.1:${VAULT_PORT}
Environment=ACGS_CONSTITUTIONAL_HASH=${CONSTITUTIONAL_HASH}

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable vault
    
    log "Systemd service created and enabled"
}

# Start Vault service
start_vault() {
    log "Starting Vault service..."
    
    sudo systemctl start vault
    
    # Wait for Vault to start
    sleep 5
    
    # Check if Vault is running
    if sudo systemctl is-active --quiet vault; then
        log "Vault service started successfully"
    else
        error "Failed to start Vault service"
        sudo systemctl status vault
        exit 1
    fi
}

# Initialize Vault
initialize_vault() {
    log "Initializing Vault..."
    
    # Set Vault address
    export VAULT_ADDR="http://127.0.0.1:${VAULT_PORT}"
    
    # Check if Vault is already initialized
    if vault status 2>/dev/null | grep -q "Initialized.*true"; then
        warn "Vault is already initialized"
        return 0
    fi
    
    # Initialize Vault
    INIT_OUTPUT=$(vault operator init -key-shares=5 -key-threshold=3 -format=json)
    
    if [[ $? -ne 0 ]]; then
        error "Failed to initialize Vault"
        exit 1
    fi
    
    # Save keys and root token securely
    KEYS_FILE="/opt/vault/vault-keys.json"
    echo "${INIT_OUTPUT}" | sudo tee ${KEYS_FILE} > /dev/null
    sudo chown vault:vault ${KEYS_FILE}
    sudo chmod 600 ${KEYS_FILE}
    
    # Extract unseal keys and root token
    UNSEAL_KEY_1=$(echo "${INIT_OUTPUT}" | jq -r '.unseal_keys_b64[0]')
    UNSEAL_KEY_2=$(echo "${INIT_OUTPUT}" | jq -r '.unseal_keys_b64[1]')
    UNSEAL_KEY_3=$(echo "${INIT_OUTPUT}" | jq -r '.unseal_keys_b64[2]')
    ROOT_TOKEN=$(echo "${INIT_OUTPUT}" | jq -r '.root_token')
    
    # Unseal Vault
    vault operator unseal ${UNSEAL_KEY_1}
    vault operator unseal ${UNSEAL_KEY_2}
    vault operator unseal ${UNSEAL_KEY_3}
    
    # Authenticate with root token
    vault auth ${ROOT_TOKEN}
    
    log "Vault initialized and unsealed successfully"
    info "Root token and unseal keys saved to ${KEYS_FILE}"
    warn "IMPORTANT: Securely backup the keys file and remove it from the server"
}

# Configure ACGS-specific Vault setup
configure_acgs_vault() {
    log "Configuring ACGS-specific Vault setup..."
    
    # Set Vault address
    export VAULT_ADDR="http://127.0.0.1:${VAULT_PORT}"
    
    # Get root token from keys file
    ROOT_TOKEN=$(sudo cat /opt/vault/vault-keys.json | jq -r '.root_token')
    vault auth ${ROOT_TOKEN}
    
    # Enable secret engines
    log "Enabling secret engines..."
    
    # KV v2 for static secrets
    vault secrets enable -path=acgs-secrets kv-v2
    
    # Database secrets engine
    vault secrets enable -path=acgs-database database
    
    # PKI secrets engine
    vault secrets enable -path=acgs-pki pki
    
    # Configure PKI
    log "Configuring PKI..."
    vault secrets tune -max-lease-ttl=8760h acgs-pki
    
    # Generate root CA
    vault write acgs-pki/root/generate/internal \
        common_name="ACGS Root CA" \
        ttl=8760h
    
    # Configure PKI URLs
    vault write acgs-pki/config/urls \
        issuing_certificates="http://127.0.0.1:${VAULT_PORT}/v1/acgs-pki/ca" \
        crl_distribution_points="http://127.0.0.1:${VAULT_PORT}/v1/acgs-pki/crl"
    
    # Create constitutional compliance secrets
    log "Creating constitutional compliance secrets..."
    
    vault kv put acgs-secrets/constitutional/hash \
        value="${CONSTITUTIONAL_HASH}" \
        description="ACGS constitutional compliance hash" \
        created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    vault kv put acgs-secrets/constitutional/validation_key \
        value="acgs_constitutional_validation_key_2024" \
        description="Key for constitutional validation operations" \
        created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    log "ACGS Vault configuration completed"
}

# Create Vault policies for ACGS services
create_acgs_policies() {
    log "Creating ACGS service policies..."
    
    # Auth Service Policy
    vault policy write acgs-auth-policy - <<EOF
# Auth Service Policy
path "acgs-secrets/data/auth/*" {
  capabilities = ["read", "create", "update"]
}

path "acgs-secrets/data/constitutional/hash" {
  capabilities = ["read"]
}

path "acgs-database/creds/auth-role" {
  capabilities = ["read"]
}

path "acgs-pki/issue/auth-cert" {
  capabilities = ["create", "update"]
}
EOF

    # AC Service Policy
    vault policy write acgs-ac-policy - <<EOF
# Algorithmic Constitution Service Policy
path "acgs-secrets/data/ac/*" {
  capabilities = ["read", "create", "update"]
}

path "acgs-secrets/data/constitutional/*" {
  capabilities = ["read", "create", "update"]
}

path "acgs-database/creds/ac-role" {
  capabilities = ["read"]
}
EOF

    # EC Service Policy (most permissive for evolution operations)
    vault policy write acgs-ec-policy - <<EOF
# Evolutionary Computation Service Policy
path "acgs-secrets/data/ec/*" {
  capabilities = ["read", "create", "update", "delete"]
}

path "acgs-secrets/data/constitutional/*" {
  capabilities = ["read", "create", "update"]
}

path "acgs-database/creds/ec-role" {
  capabilities = ["read"]
}

path "acgs-pki/issue/ec-cert" {
  capabilities = ["create", "update"]
}
EOF

    # Create policies for other services
    for service in integrity fv gs pgc; do
        vault policy write acgs-${service}-policy - <<EOF
# ${service} Service Policy
path "acgs-secrets/data/${service}/*" {
  capabilities = ["read"]
}

path "acgs-secrets/data/constitutional/hash" {
  capabilities = ["read"]
}

path "acgs-database/creds/${service}-role" {
  capabilities = ["read"]
}
EOF
    done
    
    log "ACGS service policies created"
}

# Setup AppRole authentication
setup_approle_auth() {
    log "Setting up AppRole authentication..."
    
    # Enable AppRole auth method
    vault auth enable approle
    
    # Create AppRoles for each service
    for service in auth ac integrity fv gs pgc ec; do
        vault write auth/approle/role/${service}-service \
            token_policies="acgs-${service}-policy" \
            token_ttl=1h \
            token_max_ttl=4h \
            bind_secret_id=true
        
        # Get role ID
        ROLE_ID=$(vault read -field=role_id auth/approle/role/${service}-service/role-id)
        
        # Generate secret ID
        SECRET_ID=$(vault write -field=secret_id auth/approle/role/${service}-service/secret-id)
        
        # Save credentials
        echo "Service: ${service}-service" >> /tmp/acgs-vault-credentials.txt
        echo "Role ID: ${ROLE_ID}" >> /tmp/acgs-vault-credentials.txt
        echo "Secret ID: ${SECRET_ID}" >> /tmp/acgs-vault-credentials.txt
        echo "---" >> /tmp/acgs-vault-credentials.txt
    done
    
    log "AppRole authentication configured"
    info "Service credentials saved to /tmp/acgs-vault-credentials.txt"
}

# Health check
health_check() {
    log "Performing health check..."
    
    export VAULT_ADDR="http://127.0.0.1:${VAULT_PORT}"
    
    # Check Vault status
    if vault status; then
        log "Vault is healthy and unsealed"
    else
        error "Vault health check failed"
        return 1
    fi
    
    # Test constitutional compliance secret
    if vault kv get acgs-secrets/constitutional/hash >/dev/null 2>&1; then
        log "Constitutional compliance secret accessible"
    else
        error "Constitutional compliance secret not accessible"
        return 1
    fi
    
    log "Health check completed successfully"
}

# Main deployment function
deploy_vault() {
    log "Starting ACGS Vault deployment..."
    
    check_root
    check_prerequisites
    install_vault
    create_vault_config
    create_systemd_service
    start_vault
    initialize_vault
    configure_acgs_vault
    create_acgs_policies
    setup_approle_auth
    health_check
    
    log "ACGS Vault deployment completed successfully!"
    info "Vault UI available at: http://localhost:${VAULT_PORT}/ui"
    info "Constitutional Hash: ${CONSTITUTIONAL_HASH}"
    warn "Remember to securely backup and remove /opt/vault/vault-keys.json"
    warn "Service credentials are in /tmp/acgs-vault-credentials.txt"
}

# Script usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy and configure Vault"
    echo "  start     Start Vault service"
    echo "  stop      Stop Vault service"
    echo "  status    Check Vault status"
    echo "  unseal    Unseal Vault"
    echo "  health    Perform health check"
    echo "  help      Show this help message"
    echo ""
    echo "Constitutional Hash: ${CONSTITUTIONAL_HASH}"
}

# Command handling
case "${1:-deploy}" in
    deploy)
        deploy_vault
        ;;
    start)
        sudo systemctl start vault
        log "Vault service started"
        ;;
    stop)
        sudo systemctl stop vault
        log "Vault service stopped"
        ;;
    status)
        sudo systemctl status vault
        ;;
    unseal)
        export VAULT_ADDR="http://127.0.0.1:${VAULT_PORT}"
        if [[ -f /opt/vault/vault-keys.json ]]; then
            UNSEAL_KEY_1=$(sudo cat /opt/vault/vault-keys.json | jq -r '.unseal_keys_b64[0]')
            UNSEAL_KEY_2=$(sudo cat /opt/vault/vault-keys.json | jq -r '.unseal_keys_b64[1]')
            UNSEAL_KEY_3=$(sudo cat /opt/vault/vault-keys.json | jq -r '.unseal_keys_b64[2]')
            
            vault operator unseal ${UNSEAL_KEY_1}
            vault operator unseal ${UNSEAL_KEY_2}
            vault operator unseal ${UNSEAL_KEY_3}
            
            log "Vault unsealed"
        else
            error "Vault keys file not found"
            exit 1
        fi
        ;;
    health)
        health_check
        ;;
    help)
        usage
        ;;
    *)
        error "Unknown command: $1"
        usage
        exit 1
        ;;
esac
