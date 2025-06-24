#!/bin/bash
# ACGS-PGP v8 Vault Secret Setup Script
# Sets up secure secrets in HashiCorp Vault for production deployment

set -euo pipefail

# Configuration
VAULT_ADDR="${VAULT_ADDR:-https://vault.acgs.internal:8200}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-acgs-system}"
SECRET_PATH_PREFIX="acgs-pgp-v8"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v vault &> /dev/null; then
        log_error "Vault CLI not found. Please install HashiCorp Vault CLI."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    if ! vault status &> /dev/null; then
        log_error "Cannot connect to Vault at $VAULT_ADDR"
        log_info "Please ensure Vault is running and VAULT_ADDR is correct."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate secure random passwords
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "=+/" | cut -c1-64
}

# Setup database secrets
setup_database_secrets() {
    log_info "Setting up database secrets..."
    
    local db_password=$(generate_password 32)
    local db_host="${DB_HOST:-postgresql.acgs-system.svc.cluster.local}"
    local db_port="${DB_PORT:-5432}"
    local db_name="${DB_NAME:-acgs_db}"
    local db_username="${DB_USERNAME:-acgs_pgp_v8_user}"
    
    vault kv put secret/${SECRET_PATH_PREFIX}/database \
        username="$db_username" \
        password="$db_password" \
        host="$db_host" \
        port="$db_port" \
        database="$db_name"
    
    log_success "Database secrets configured"
    log_warning "Database password: $db_password (save this securely)"
}

# Setup Redis secrets
setup_redis_secrets() {
    log_info "Setting up Redis secrets..."
    
    local redis_password=$(generate_password 32)
    local redis_host="${REDIS_HOST:-redis.acgs-system.svc.cluster.local}"
    local redis_port="${REDIS_PORT:-6379}"
    local redis_database="${REDIS_DATABASE:-0}"
    local redis_username="${REDIS_USERNAME:-default}"
    
    vault kv put secret/${SECRET_PATH_PREFIX}/redis \
        username="$redis_username" \
        password="$redis_password" \
        host="$redis_host" \
        port="$redis_port" \
        database="$redis_database"
    
    log_success "Redis secrets configured"
    log_warning "Redis password: $redis_password (save this securely)"
}

# Setup authentication secrets
setup_auth_secrets() {
    log_info "Setting up authentication secrets..."
    
    local jwt_secret=$(generate_jwt_secret)
    local api_key=$(generate_password 48)
    local encryption_key=$(generate_password 32)
    
    vault kv put secret/${SECRET_PATH_PREFIX}/auth \
        jwt_secret_key="$jwt_secret" \
        api_key="$api_key" \
        encryption_key="$encryption_key"
    
    log_success "Authentication secrets configured"
    log_warning "JWT Secret: $jwt_secret (save this securely)"
    log_warning "API Key: $api_key (save this securely)"
}

# Setup AI/ML model API keys
setup_ai_secrets() {
    log_info "Setting up AI/ML model API keys..."
    
    # These should be provided as environment variables or prompted
    local openai_key="${OPENAI_API_KEY:-}"
    local anthropic_key="${ANTHROPIC_API_KEY:-}"
    local groq_key="${GROQ_API_KEY:-}"
    local google_key="${GOOGLE_API_KEY:-}"
    
    if [[ -z "$openai_key" ]]; then
        read -p "Enter OpenAI API Key (or press Enter to skip): " openai_key
    fi
    
    if [[ -z "$anthropic_key" ]]; then
        read -p "Enter Anthropic API Key (or press Enter to skip): " anthropic_key
    fi
    
    if [[ -z "$groq_key" ]]; then
        read -p "Enter Groq API Key (or press Enter to skip): " groq_key
    fi
    
    if [[ -z "$google_key" ]]; then
        read -p "Enter Google API Key (or press Enter to skip): " google_key
    fi
    
    vault kv put secret/${SECRET_PATH_PREFIX}/ai-models \
        openai_api_key="${openai_key:-placeholder}" \
        anthropic_api_key="${anthropic_key:-placeholder}" \
        groq_api_key="${groq_key:-placeholder}" \
        google_api_key="${google_key:-placeholder}"
    
    log_success "AI/ML model API keys configured"
}

# Setup Kubernetes authentication for Vault
setup_k8s_auth() {
    log_info "Setting up Kubernetes authentication for Vault..."
    
    # Enable Kubernetes auth method if not already enabled
    if ! vault auth list | grep -q kubernetes; then
        vault auth enable kubernetes
        log_success "Kubernetes auth method enabled"
    fi
    
    # Get Kubernetes cluster information
    local k8s_host=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.server}')
    local k8s_ca_cert=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[].cluster.certificate-authority-data}' | base64 -d)
    local jwt_token=$(kubectl get secret -n acgs-system $(kubectl get serviceaccount -n acgs-system acgs-pgp-v8-vault-auth -o jsonpath='{.secrets[0].name}') -o jsonpath='{.data.token}' | base64 -d)
    
    # Configure Kubernetes auth
    vault write auth/kubernetes/config \
        token_reviewer_jwt="$jwt_token" \
        kubernetes_host="$k8s_host" \
        kubernetes_ca_cert="$k8s_ca_cert"
    
    # Create role for ACGS-PGP v8
    vault write auth/kubernetes/role/acgs-pgp-v8 \
        bound_service_account_names=acgs-pgp-v8-vault-auth \
        bound_service_account_namespaces=acgs-system \
        policies=acgs-pgp-v8-policy \
        ttl=24h
    
    log_success "Kubernetes authentication configured"
}

# Create Vault policy for ACGS-PGP v8
create_vault_policy() {
    log_info "Creating Vault policy for ACGS-PGP v8..."
    
    cat > /tmp/acgs-pgp-v8-policy.hcl << EOF
# ACGS-PGP v8 Vault Policy
path "secret/data/${SECRET_PATH_PREFIX}/*" {
  capabilities = ["read"]
}

path "secret/metadata/${SECRET_PATH_PREFIX}/*" {
  capabilities = ["read"]
}
EOF
    
    vault policy write acgs-pgp-v8-policy /tmp/acgs-pgp-v8-policy.hcl
    rm /tmp/acgs-pgp-v8-policy.hcl
    
    log_success "Vault policy created"
}

# Verify secret setup
verify_secrets() {
    log_info "Verifying secret setup..."
    
    local paths=(
        "secret/${SECRET_PATH_PREFIX}/database"
        "secret/${SECRET_PATH_PREFIX}/redis"
        "secret/${SECRET_PATH_PREFIX}/auth"
        "secret/${SECRET_PATH_PREFIX}/ai-models"
    )
    
    for path in "${paths[@]}"; do
        if vault kv get "$path" &> /dev/null; then
            log_success "✓ $path"
        else
            log_error "✗ $path"
        fi
    done
}

# Main execution
main() {
    log_info "Starting ACGS-PGP v8 Vault secret setup..."
    log_info "Vault Address: $VAULT_ADDR"
    log_info "Namespace: $VAULT_NAMESPACE"
    
    check_prerequisites
    create_vault_policy
    setup_database_secrets
    setup_redis_secrets
    setup_auth_secrets
    setup_ai_secrets
    setup_k8s_auth
    verify_secrets
    
    log_success "ACGS-PGP v8 Vault secret setup completed successfully!"
    log_info "Next steps:"
    log_info "1. Apply the External Secrets Operator configuration: kubectl apply -f k8s/secrets-management.yaml"
    log_info "2. Deploy the updated ACGS-PGP v8: kubectl apply -f k8s/deployment.yaml"
    log_info "3. Verify secret synchronization: kubectl get externalsecrets -n acgs-system"
}

# Handle script arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "verify")
        verify_secrets
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [setup|verify|help]"
        echo "  setup  - Set up all Vault secrets (default)"
        echo "  verify - Verify existing secret setup"
        echo "  help   - Show this help message"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
