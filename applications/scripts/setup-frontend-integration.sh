#!/bin/bash

# ACGS-PGP Frontend Integration Setup Script
# This script helps set up frontend applications for microservices integration

set -e

echo "🚀 ACGS-PGP Frontend Integration Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from a frontend application directory."
    exit 1
fi

# Determine which frontend application we're setting up
APP_NAME=""
if [ -f "src/components/GovernanceDashboard.tsx" ]; then
    APP_NAME="governance-dashboard"
elif [ -f "src/components/QuantumagiDashboard.jsx" ]; then
    APP_NAME="legacy-frontend"
else
    print_warning "Could not determine application type. Proceeding with generic setup."
    APP_NAME="unknown"
fi

print_header "Setting up $APP_NAME for ACGS-PGP microservices integration..."

# Step 1: Check for required dependencies
print_status "Checking required dependencies..."

REQUIRED_DEPS=("axios" "js-cookie")
MISSING_DEPS=()

for dep in "${REQUIRED_DEPS[@]}"; do
    if ! npm list "$dep" > /dev/null 2>&1; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_warning "Missing required dependencies: ${MISSING_DEPS[*]}"
    read -p "Install missing dependencies? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installing missing dependencies..."
        npm install "${MISSING_DEPS[@]}"
    else
        print_error "Cannot proceed without required dependencies."
        exit 1
    fi
else
    print_status "All required dependencies are installed."
fi

# Step 2: Set up environment configuration
print_status "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please review and update the .env file with your specific configuration."
    else
        print_warning ".env.example not found. Creating basic .env file..."
        cat > .env << EOF
# ACGS-PGP Microservices Configuration
REACT_APP_AC_API_URL=http://localhost:8001/api/v1
REACT_APP_GS_API_URL=http://localhost:8003/api/v1
REACT_APP_AUTH_API_URL=http://localhost:8002/auth
REACT_APP_INTEGRITY_API_URL=http://localhost:8006/api/v1
REACT_APP_PGC_API_URL=http://localhost:8004/api/v1

# Development Configuration
NODE_ENV=development
REACT_APP_DEBUG_MODE=true
REACT_APP_LOG_API_REQUESTS=true
EOF
    fi
else
    print_status ".env file already exists."
fi

# Step 3: Verify service structure
print_status "Verifying service structure..."

SERVICES_DIR="src/services"
if [ ! -d "$SERVICES_DIR" ]; then
    print_warning "Services directory not found. Creating $SERVICES_DIR..."
    mkdir -p "$SERVICES_DIR"
fi

# Check for required service files
REQUIRED_SERVICES=("api.js" "ACService.js" "GSService.js" "AuthService.js")
MISSING_SERVICES=()

for service in "${REQUIRED_SERVICES[@]}"; do
    if [ ! -f "$SERVICES_DIR/$service" ]; then
        MISSING_SERVICES+=("$service")
    fi
done

if [ ${#MISSING_SERVICES[@]} -gt 0 ]; then
    print_warning "Missing service files: ${MISSING_SERVICES[*]}"
    print_status "Please refer to the integration guide to create these files."
else
    print_status "All required service files are present."
fi

# Step 4: Check for authentication context
print_status "Checking authentication setup..."

AUTH_CONTEXT="src/contexts/AuthContext.js"
if [ ! -f "$AUTH_CONTEXT" ]; then
    print_warning "AuthContext not found at $AUTH_CONTEXT"
    print_status "Please refer to the integration guide to set up authentication context."
else
    print_status "AuthContext found."
fi

# Step 5: Verify test setup
print_status "Checking test configuration..."

if [ -f "src/setupTests.js" ]; then
    print_status "Test setup file found."
else
    print_warning "Test setup file not found. Consider adding src/setupTests.js for testing configuration."
fi

# Step 6: Health check script
print_status "Creating health check script..."

cat > scripts/health-check.js << 'EOF'
#!/usr/bin/env node

const axios = require('axios');

const services = [
    { name: 'AC Service', url: process.env.REACT_APP_AC_API_URL || 'http://localhost:8001/api/v1' },
    { name: 'GS Service', url: process.env.REACT_APP_GS_API_URL || 'http://localhost:8003/api/v1' },
    { name: 'Auth Service', url: process.env.REACT_APP_AUTH_API_URL || 'http://localhost:8002/auth' },
    { name: 'Integrity Service', url: process.env.REACT_APP_INTEGRITY_API_URL || 'http://localhost:8006/api/v1' }
];

async function checkService(service) {
    try {
        const response = await axios.get(`${service.url}/health`, { timeout: 5000 });
        return { ...service, status: 'healthy', response: response.status };
    } catch (error) {
        return { ...service, status: 'unhealthy', error: error.message };
    }
}

async function checkAllServices() {
    console.log('🏥 ACGS-PGP Services Health Check');
    console.log('==================================');
    
    const results = await Promise.all(services.map(checkService));
    
    results.forEach(result => {
        const status = result.status === 'healthy' ? '✅' : '❌';
        console.log(`${status} ${result.name}: ${result.status}`);
        if (result.error) {
            console.log(`   Error: ${result.error}`);
        }
    });
    
    const healthyCount = results.filter(r => r.status === 'healthy').length;
    console.log(`\n${healthyCount}/${results.length} services are healthy`);
}

checkAllServices().catch(console.error);
EOF

chmod +x scripts/health-check.js

# Step 7: Add npm scripts
print_status "Adding helpful npm scripts..."

# Check if jq is available for JSON manipulation
if command -v jq > /dev/null 2>&1; then
    # Add scripts using jq
    jq '.scripts["health-check"] = "node scripts/health-check.js"' package.json > package.json.tmp && mv package.json.tmp package.json
    jq '.scripts["integration-test"] = "npm run test -- --testPathPattern=integration"' package.json > package.json.tmp && mv package.json.tmp package.json
    print_status "Added health-check and integration-test scripts to package.json"
else
    print_warning "jq not found. Please manually add the following scripts to package.json:"
    echo '  "health-check": "node scripts/health-check.js",'
    echo '  "integration-test": "npm run test -- --testPathPattern=integration"'
fi

# Final summary
print_header "\n🎉 Setup Complete!"
echo "=================="
print_status "Frontend integration setup completed for $APP_NAME"
echo ""
echo "Next steps:"
echo "1. Review and update the .env file with your specific configuration"
echo "2. Ensure all microservices are running"
echo "3. Run 'npm run health-check' to verify service connectivity"
echo "4. Refer to docs/frontend-microservices-integration-guide.md for detailed integration patterns"
echo ""
print_status "Happy coding! 🚀"
