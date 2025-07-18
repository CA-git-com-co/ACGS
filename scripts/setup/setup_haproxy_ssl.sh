# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# ACGS-1 HAProxy SSL Certificate Setup Script
# Phase 2 - Enterprise Scalability & Performance
# Creates self-signed SSL certificates for development/testing

set -e

echo "🔧 Setting up SSL certificates for HAProxy..."

# Colors for output
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

# Configuration
PROJECT_ROOT="/home/dislove/ACGS-1"
SSL_DIR="$PROJECT_ROOT/infrastructure/load-balancer/ssl"
ERRORS_DIR="$PROJECT_ROOT/infrastructure/load-balancer/errors"

# Create directories
print_status "Creating SSL and error directories..."
mkdir -p "$SSL_DIR"
mkdir -p "$ERRORS_DIR"

# Generate self-signed SSL certificate for development
print_status "Generating self-signed SSL certificate..."

# Certificate configuration
CERT_COUNTRY="US"
CERT_STATE="California"
CERT_CITY="San Francisco"
CERT_ORG="ACGS Development"
CERT_OU="IT Department"
CERT_CN="acgs.local"
CERT_EMAIL="admin@acgs.local"

# Generate private key
openssl genrsa -out "$SSL_DIR/acgs.key" 2048

# Generate certificate signing request
openssl req -new -key "$SSL_DIR/acgs.key" -out "$SSL_DIR/acgs.csr" -subj "/C=$CERT_COUNTRY/ST=$CERT_STATE/L=$CERT_CITY/O=$CERT_ORG/OU=$CERT_OU/CN=$CERT_CN/emailAddress=$CERT_EMAIL"

# Generate self-signed certificate
openssl x509 -req -days 365 -in "$SSL_DIR/acgs.csr" -signkey "$SSL_DIR/acgs.key" -out "$SSL_DIR/acgs.crt"

# Combine certificate and key for HAProxy
cat "$SSL_DIR/acgs.crt" "$SSL_DIR/acgs.key" > "$SSL_DIR/acgs.pem"

# Set proper permissions
chmod 600 "$SSL_DIR/acgs.key"
chmod 644 "$SSL_DIR/acgs.crt"
chmod 600 "$SSL_DIR/acgs.pem"

print_success "SSL certificate generated: $SSL_DIR/acgs.pem"

# Create custom error pages
print_status "Creating custom error pages..."

# 400 Bad Request
cat > "$ERRORS_DIR/400.http" << 'EOF'
HTTP/1.1 400 Bad Request
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>400 Bad Request - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e74c3c; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #e74c3c; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">400</div>
        <h1>Bad Request</h1>
        <div class="message">
            <p>The request could not be understood by the server due to malformed syntax.</p>
            <p>Please check your request and try again.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

# 403 Forbidden
cat > "$ERRORS_DIR/403.http" << 'EOF'
HTTP/1.1 403 Forbidden
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>403 Forbidden - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e74c3c; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #e74c3c; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">403</div>
        <h1>Access Forbidden</h1>
        <div class="message">
            <p>You don't have permission to access this resource.</p>
            <p>If you believe this is an error, please contact the system administrator.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

# 408 Request Timeout
cat > "$ERRORS_DIR/408.http" << 'EOF'
HTTP/1.1 408 Request Timeout
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>408 Request Timeout - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #f39c12; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #f39c12; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">408</div>
        <h1>Request Timeout</h1>
        <div class="message">
            <p>The server timed out waiting for the request.</p>
            <p>Please try again later.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

# 500 Internal Server Error
cat > "$ERRORS_DIR/500.http" << 'EOF'
HTTP/1.1 500 Internal Server Error
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>500 Internal Server Error - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e74c3c; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #e74c3c; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">500</div>
        <h1>Internal Server Error</h1>
        <div class="message">
            <p>The server encountered an unexpected condition that prevented it from fulfilling the request.</p>
            <p>Our team has been notified and is working to resolve the issue.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

# 502 Bad Gateway
cat > "$ERRORS_DIR/502.http" << 'EOF'
HTTP/1.1 502 Bad Gateway
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>502 Bad Gateway - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e74c3c; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #e74c3c; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">502</div>
        <h1>Bad Gateway</h1>
        <div class="message">
            <p>The server received an invalid response from an upstream server.</p>
            <p>Please try again in a few moments.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

# 503 Service Unavailable
cat > "$ERRORS_DIR/503.http" << 'EOF'
HTTP/1.1 503 Service Unavailable
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>503 Service Unavailable - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #f39c12; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #f39c12; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">503</div>
        <h1>Service Unavailable</h1>
        <div class="message">
            <p>The service is temporarily unavailable due to maintenance or high load.</p>
            <p>Please try again later.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

# 504 Gateway Timeout
cat > "$ERRORS_DIR/504.http" << 'EOF'
HTTP/1.1 504 Gateway Timeout
Cache-Control: no-cache
Connection: close
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>504 Gateway Timeout - ACGS</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #f39c12; margin-bottom: 20px; }
        .error-code { font-size: 48px; font-weight: bold; color: #f39c12; margin-bottom: 10px; }
        .message { color: #666; line-height: 1.6; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">504</div>
        <h1>Gateway Timeout</h1>
        <div class="message">
            <p>The server did not receive a timely response from an upstream server.</p>
            <p>Please try again later.</p>
        </div>
        <div class="footer">
            ACGS - Autonomous Constitutional Governance System
        </div>
    </div>
</body>
</html>
EOF

print_success "Custom error pages created in $ERRORS_DIR"

# Create rsyslog configuration for HAProxy logs
print_status "Creating rsyslog configuration..."

cat > "$PROJECT_ROOT/infrastructure/load-balancer/rsyslog.conf" << 'EOF'
# ACGS-1 HAProxy Logging Configuration
# Rsyslog configuration for HAProxy log aggregation

# Global directives
$ModLoad imudp
$UDPServerRun 514
$UDPServerAddress 0.0.0.0

# HAProxy log format
$template HAProxyFormat,"%msg%\n"

# HAProxy log files
local0.*    /var/log/haproxy.log;HAProxyFormat
& stop

# General syslog
*.info;mail.none;authpriv.none;cron.none    /var/log/messages
authpriv.*                                  /var/log/secure
mail.*                                      -/var/log/maillog
cron.*                                      /var/log/cron
*.emerg                                     :omusrmsg:*
uucp,news.crit                             /var/log/spooler
local7.*                                    /var/log/boot.log
EOF

print_success "Rsyslog configuration created"

print_success "HAProxy SSL and error page setup completed!"

print_status "SSL Certificate Information:"
echo "- Certificate: $SSL_DIR/acgs.crt"
echo "- Private Key: $SSL_DIR/acgs.key"
echo "- Combined PEM: $SSL_DIR/acgs.pem"
echo "- Common Name: $CERT_CN"
echo "- Valid for: 365 days"

print_status "Error Pages:"
echo "- 400 Bad Request: $ERRORS_DIR/400.http"
echo "- 403 Forbidden: $ERRORS_DIR/403.http"
echo "- 408 Request Timeout: $ERRORS_DIR/408.http"
echo "- 500 Internal Server Error: $ERRORS_DIR/500.http"
echo "- 502 Bad Gateway: $ERRORS_DIR/502.http"
echo "- 503 Service Unavailable: $ERRORS_DIR/503.http"
echo "- 504 Gateway Timeout: $ERRORS_DIR/504.http"

print_warning "Note: This is a self-signed certificate for development use only."
print_warning "For production, use certificates from a trusted Certificate Authority."

print_status "Next steps:"
echo "1. Add 'acgs.local' to your /etc/hosts file pointing to 127.0.0.1"
echo "2. Start HAProxy with: docker-compose -f infrastructure/load-balancer/docker-compose.haproxy.yml up -d"
echo "3. Access HAProxy stats at: http://localhost:8080/stats"
echo "4. Test HTTPS access at: https://acgs.local (accept the self-signed certificate warning)"
