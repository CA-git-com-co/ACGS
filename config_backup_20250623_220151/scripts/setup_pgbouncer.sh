#!/bin/bash
# ACGS-1 PgBouncer Setup Script
# Phase 2 - Enterprise Scalability & Performance
# Configure PgBouncer for >1000 concurrent users

set -e

echo "🔧 Setting up PgBouncer for ACGS-1 Enterprise Production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration paths
PGBOUNCER_CONFIG_DIR="/etc/pgbouncer"
PGBOUNCER_LOG_DIR="/var/log/pgbouncer"
PGBOUNCER_RUN_DIR="/var/run/pgbouncer"
PROJECT_ROOT="/home/dislove/ACGS-1"

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

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. This is acceptable for system configuration."
elif sudo -n true 2>/dev/null; then
    print_status "Sudo access available."
else
    print_error "This script requires sudo access for system configuration."
    exit 1
fi

# Create necessary directories
print_status "Creating PgBouncer directories..."
sudo mkdir -p "$PGBOUNCER_CONFIG_DIR"
sudo mkdir -p "$PGBOUNCER_LOG_DIR"
sudo mkdir -p "$PGBOUNCER_RUN_DIR"

# Set proper ownership
sudo chown postgres:postgres "$PGBOUNCER_CONFIG_DIR"
sudo chown postgres:postgres "$PGBOUNCER_LOG_DIR"
sudo chown postgres:postgres "$PGBOUNCER_RUN_DIR"

# Copy configuration files
print_status "Installing PgBouncer configuration..."
sudo cp "$PROJECT_ROOT/infrastructure/database/pgbouncer.ini" "$PGBOUNCER_CONFIG_DIR/"
sudo cp "$PROJECT_ROOT/infrastructure/database/userlist.txt" "$PGBOUNCER_CONFIG_DIR/"

# Set proper permissions
sudo chmod 640 "$PGBOUNCER_CONFIG_DIR/pgbouncer.ini"
sudo chmod 640 "$PGBOUNCER_CONFIG_DIR/userlist.txt"
sudo chown postgres:postgres "$PGBOUNCER_CONFIG_DIR/pgbouncer.ini"
sudo chown postgres:postgres "$PGBOUNCER_CONFIG_DIR/userlist.txt"

# Generate proper password hashes for userlist.txt
print_status "Generating password hashes..."
ACGS_PASSWORD="acgs_password"
POSTGRES_PASSWORD="postgres"

# Generate MD5 hashes (format: md5 + md5(password + username))
ACGS_HASH="md5$(echo -n "${ACGS_PASSWORD}acgs_user" | md5sum | cut -d' ' -f1)"
POSTGRES_HASH="md5$(echo -n "${POSTGRES_PASSWORD}postgres" | md5sum | cut -d' ' -f1)"

# Update userlist.txt with proper hashes
sudo tee "$PGBOUNCER_CONFIG_DIR/userlist.txt" > /dev/null << EOF
# PgBouncer User Authentication File
# Generated automatically by setup_pgbouncer.sh

"acgs_user" "$ACGS_HASH"
"postgres" "$POSTGRES_HASH"
EOF

sudo chmod 640 "$PGBOUNCER_CONFIG_DIR/userlist.txt"
sudo chown postgres:postgres "$PGBOUNCER_CONFIG_DIR/userlist.txt"

# Test configuration
print_status "Testing PgBouncer configuration..."
if sudo -u postgres pgbouncer -t "$PGBOUNCER_CONFIG_DIR/pgbouncer.ini"; then
    print_success "PgBouncer configuration is valid"
else
    print_error "PgBouncer configuration test failed"
    exit 1
fi

# Stop existing PgBouncer if running
print_status "Stopping existing PgBouncer service..."
sudo systemctl stop pgbouncer || true

# Start PgBouncer with new configuration
print_status "Starting PgBouncer with new configuration..."
sudo systemctl start pgbouncer

# Enable PgBouncer to start on boot
sudo systemctl enable pgbouncer

# Wait for service to start
sleep 5

# Check service status
if sudo systemctl is-active --quiet pgbouncer; then
    print_success "PgBouncer is running successfully"
else
    print_error "Failed to start PgBouncer"
    sudo systemctl status pgbouncer
    exit 1
fi

# Test connection through PgBouncer
print_status "Testing connection through PgBouncer..."
if PGPASSWORD="$ACGS_PASSWORD" psql -h localhost -p 6432 -U acgs_user -d acgs_db -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "PgBouncer connection test successful"
else
    print_warning "PgBouncer connection test failed - this may be normal if database doesn't exist yet"
fi

# Display status
print_status "PgBouncer Status:"
sudo systemctl status pgbouncer --no-pager -l

print_success "PgBouncer setup completed successfully!"
print_status "Configuration file: $PGBOUNCER_CONFIG_DIR/pgbouncer.ini"
print_status "Log file: $PGBOUNCER_LOG_DIR/pgbouncer.log"
print_status "PgBouncer is listening on port 6432"
print_status "Use connection string: postgresql://acgs_user:acgs_password@localhost:6432/acgs_db"

echo ""
print_status "Next steps:"
echo "1. Update application connection strings to use port 6432"
echo "2. Configure connection pools for each service"
echo "3. Implement retry mechanisms and circuit breakers"
echo "4. Set up read replica routing"
echo "5. Configure monitoring and performance tuning"
