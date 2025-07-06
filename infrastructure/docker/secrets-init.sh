#!/bin/bash

# ACGS Production Secrets Initialization Script
# This script helps generate secure secrets for production deployment
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "===================================================================================="
echo "ACGS Production Secrets Initialization"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "===================================================================================="
echo -e "${NC}"

# Check if running as root (not recommended for production)
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}Warning: Running as root. Consider using a dedicated user for production.${NC}"
fi

# Create secrets directory
SECRETS_DIR="./secrets"
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

echo -e "${GREEN}✓ Created secrets directory with restricted permissions${NC}"

# Function to generate secure random password
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Function to generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64
}

# Function to generate database passwords
generate_db_passwords() {
    echo -e "${BLUE}Generating database passwords...${NC}"

    echo "# Database Passwords - Generated $(date)" > "$SECRETS_DIR/db_passwords.env"
    echo "POSTGRES_PASSWORD=$(generate_password 32)" >> "$SECRETS_DIR/db_passwords.env"
    echo "ACGS_AUTH_DB_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/db_passwords.env"
    echo "ACGS_CONSTITUTIONAL_DB_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/db_passwords.env"
    echo "ACGS_INTEGRITY_DB_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/db_passwords.env"
    echo "ACGS_POLICY_DB_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/db_passwords.env"
    echo "ACGS_SYNTHESIS_DB_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/db_passwords.env"

    chmod 600 "$SECRETS_DIR/db_passwords.env"
    echo -e "${GREEN}✓ Database passwords generated${NC}"
}

# Function to generate application secrets
generate_app_secrets() {
    echo -e "${BLUE}Generating application secrets...${NC}"

    echo "# Application Secrets - Generated $(date)" > "$SECRETS_DIR/app_secrets.env"
    echo "JWT_SECRET_KEY=$(generate_jwt_secret)" >> "$SECRETS_DIR/app_secrets.env"
    echo "REDIS_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/app_secrets.env"
    echo "CSRF_SECRET_KEY=$(generate_password 32)" >> "$SECRETS_DIR/app_secrets.env"
    echo "SESSION_SECRET_KEY=$(generate_password 32)" >> "$SECRETS_DIR/app_secrets.env"

    chmod 600 "$SECRETS_DIR/app_secrets.env"
    echo -e "${GREEN}✓ Application secrets generated${NC}"
}

# Function to generate TLS certificates (self-signed for development)
generate_dev_certificates() {
    echo -e "${BLUE}Generating development TLS certificates...${NC}"

    CERT_DIR="$SECRETS_DIR/certs"
    mkdir -p "$CERT_DIR"
    chmod 700 "$CERT_DIR"

    # Generate CA private key
    openssl genrsa -out "$CERT_DIR/ca.key" 4096

    # Generate CA certificate
    openssl req -new -x509 -days 365 -key "$CERT_DIR/ca.key" -out "$CERT_DIR/ca.crt" -subj "/C=US/ST=Production/L=ACGS/O=ACGS Constitutional AI/OU=Security/CN=ACGS-CA"

    # Generate server private key
    openssl genrsa -out "$CERT_DIR/acgs.key" 2048

    # Generate certificate signing request
    openssl req -new -key "$CERT_DIR/acgs.key" -out "$CERT_DIR/acgs.csr" -subj "/C=US/ST=Production/L=ACGS/O=ACGS Constitutional AI/OU=Platform/CN=acgs.local"

    # Generate server certificate
    openssl x509 -req -in "$CERT_DIR/acgs.csr" -CA "$CERT_DIR/ca.crt" -CAkey "$CERT_DIR/ca.key" -CAcreateserial -out "$CERT_DIR/acgs.crt" -days 365 -extensions v3_req -extfile <(cat << EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = acgs.local
DNS.2 = localhost
DNS.3 = acgs.example.com
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
)

    # Create certificate chain
    cat "$CERT_DIR/acgs.crt" "$CERT_DIR/ca.crt" > "$CERT_DIR/acgs-chain.crt"

    # Set appropriate permissions
    chmod 600 "$CERT_DIR"/*.key
    chmod 644 "$CERT_DIR"/*.crt "$CERT_DIR"/*.csr

    # Clean up CSR
    rm "$CERT_DIR/acgs.csr"

    echo -e "${GREEN}✓ Development TLS certificates generated${NC}"
    echo -e "${YELLOW}Note: For production, use certificates from a trusted CA${NC}"
}

# Function to generate monitoring secrets
generate_monitoring_secrets() {
    echo -e "${BLUE}Generating monitoring secrets...${NC}"

    echo "# Monitoring Secrets - Generated $(date)" > "$SECRETS_DIR/monitoring_secrets.env"
    echo "PROMETHEUS_ADMIN_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/monitoring_secrets.env"
    echo "GRAFANA_ADMIN_PASSWORD=$(generate_password 24)" >> "$SECRETS_DIR/monitoring_secrets.env"
    echo "ALERTMANAGER_SECRET=$(generate_password 32)" >> "$SECRETS_DIR/monitoring_secrets.env"

    chmod 600 "$SECRETS_DIR/monitoring_secrets.env"
    echo -e "${GREEN}✓ Monitoring secrets generated${NC}"
}

# Function to create production environment file
create_production_env() {
    echo -e "${BLUE}Creating production environment file...${NC}"

    # Copy template
    cp .env.production.template .env.production

    # Source generated secrets
    source "$SECRETS_DIR/db_passwords.env"
    source "$SECRETS_DIR/app_secrets.env"
    source "$SECRETS_DIR/monitoring_secrets.env"

    # Replace placeholders in .env.production
    sed -i "s/CHANGE_ME_STRONG_PASSWORD_HERE/$POSTGRES_PASSWORD/g" .env.production
    sed -i "s/CHANGE_ME_AUTH_PASSWORD/$ACGS_AUTH_DB_PASSWORD/g" .env.production
    sed -i "s/CHANGE_ME_CONSTITUTIONAL_PASSWORD/$ACGS_CONSTITUTIONAL_DB_PASSWORD/g" .env.production
    sed -i "s/CHANGE_ME_INTEGRITY_PASSWORD/$ACGS_INTEGRITY_DB_PASSWORD/g" .env.production
    sed -i "s/CHANGE_ME_POLICY_PASSWORD/$ACGS_POLICY_DB_PASSWORD/g" .env.production
    sed -i "s/CHANGE_ME_SYNTHESIS_PASSWORD/$ACGS_SYNTHESIS_DB_PASSWORD/g" .env.production
    sed -i "s/CHANGE_ME_REDIS_PASSWORD/$REDIS_PASSWORD/g" .env.production
    sed -i "s|CHANGE_ME_GENERATE_RANDOM_64_BYTE_KEY_HERE|$JWT_SECRET_KEY|g" .env.production

    chmod 600 .env.production
    echo -e "${GREEN}✓ Production environment file created${NC}"
}

# Function to display security checklist
display_security_checklist() {
    echo -e "${YELLOW}"
    echo "===================================================================================="
    echo "PRODUCTION SECURITY CHECKLIST"
    echo "===================================================================================="
    echo "🔒 Secrets generated and stored with restricted permissions"
    echo "🔒 Review and update CORS_ORIGINS in .env.production"
    echo "🔒 Review and update ALLOWED_HOSTS in .env.production"
    echo "🔒 Configure proper TLS certificates from trusted CA"
    echo "🔒 Configure backup destinations (S3, etc.)"
    echo "🔒 Configure monitoring alerts (Slack, PagerDuty)"
    echo "🔒 Review firewall rules and network security"
    echo "🔒 Enable audit logging and monitoring"
    echo "🔒 Test disaster recovery procedures"
    echo "🔒 Secure secrets management (consider HashiCorp Vault)"
    echo "🔒 Regular security updates and vulnerability scanning"
    echo "===================================================================================="
    echo -e "${NC}"
}

# Function to display constitutional compliance reminder
display_constitutional_compliance() {
    echo -e "${BLUE}"
    echo "===================================================================================="
    echo "CONSTITUTIONAL COMPLIANCE VERIFICATION"
    echo "===================================================================================="
    echo "Constitutional Hash: cdd01ef066bc6cf2"
    echo ""
    echo "Verify that all generated configurations maintain constitutional compliance:"
    echo "✓ Multi-tenant isolation is enforced"
    echo "✓ Audit trails are cryptographically secured"
    echo "✓ Access controls follow constitutional principles"
    echo "✓ Data protection meets constitutional requirements"
    echo "✓ Monitoring includes constitutional compliance checks"
    echo "===================================================================================="
    echo -e "${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}Starting ACGS production secrets initialization...${NC}"

    # Check dependencies
    if ! command -v openssl &> /dev/null; then
        echo -e "${RED}Error: openssl is required but not installed.${NC}"
        exit 1
    fi

    # Generate all secrets
    generate_db_passwords
    generate_app_secrets
    generate_dev_certificates
    generate_monitoring_secrets
    create_production_env

    echo -e "${GREEN}"
    echo "===================================================================================="
    echo "✅ ACGS Production Secrets Initialization Complete!"
    echo "===================================================================================="
    echo -e "${NC}"

    display_security_checklist
    display_constitutional_compliance

    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review and customize .env.production"
    echo "2. Deploy using: docker-compose -f docker-compose.production.yml up -d"
    echo "3. Verify all services are healthy"
    echo "4. Configure monitoring and alerting"
    echo "5. Perform security testing"
}

# Run main function
main "$@"
