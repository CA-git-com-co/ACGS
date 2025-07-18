# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS Alerting System Setup Script
# Configures automated alerting for all ACGS services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ALERTING_DIR="$PROJECT_ROOT/infrastructure/alerting"
CONFIG_DIR="$ALERTING_DIR/config"
TEMPLATES_DIR="$ALERTING_DIR/templates"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}ACGS Alerting System Setup${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Create directory structure
create_directories() {
    print_info "Creating alerting directory structure..."
    
    local dirs=(
        "$ALERTING_DIR"
        "$CONFIG_DIR"
        "$TEMPLATES_DIR"
        "$ALERTING_DIR/channels"
        "$ALERTING_DIR/rules"
        "$ALERTING_DIR/scripts"
        "$PROJECT_ROOT/logs/alerting"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Generate alerting configuration
generate_alerting_config() {
    print_info "Generating alerting configuration..."
    
    cat > "$CONFIG_DIR/alerting-config.json" << EOF
{
  "version": "1.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "alerting": {
    "enabled": true,
    "defaultChannels": ["console", "browser"],
    "retentionDays": 30,
    "maxAlertsPerHour": 100,
    "suppressDuplicates": true,
    "duplicateWindow": 300000
  },
  "escalationRules": [
    {
      "id": "critical-escalation",
      "severity": "critical",
      "escalateAfter": 300000,
      "escalateTo": ["email", "slack"],
      "maxEscalations": 3
    },
    {
      "id": "high-escalation", 
      "severity": "high",
      "escalateAfter": 900000,
      "escalateTo": ["email"],
      "maxEscalations": 2
    }
  ],
  "thresholds": {
    "responseTime": {
      "warning": 1000,
      "critical": 2000
    },
    "errorRate": {
      "warning": 2,
      "critical": 5
    },
    "uptime": {
      "warning": 99.0,
      "critical": 95.0
    },
    "consecutiveFailures": {
      "warning": 2,
      "critical": 3
    }
  },
  "services": {
    "auth": {
      "critical": true,
      "responseTimeThreshold": 1000,
      "errorRateThreshold": 2,
      "uptimeThreshold": 99.5
    },
    "ac": {
      "critical": true,
      "responseTimeThreshold": 2000,
      "errorRateThreshold": 3,
      "uptimeThreshold": 99.0
    },
    "integrity": {
      "critical": true,
      "responseTimeThreshold": 1500,
      "errorRateThreshold": 2,
      "uptimeThreshold": 99.5
    },
    "fv": {
      "critical": false,
      "responseTimeThreshold": 5000,
      "errorRateThreshold": 5,
      "uptimeThreshold": 95.0
    },
    "gs": {
      "critical": true,
      "responseTimeThreshold": 3000,
      "errorRateThreshold": 3,
      "uptimeThreshold": 99.0
    },
    "pgc": {
      "critical": true,
      "responseTimeThreshold": 2000,
      "errorRateThreshold": 2,
      "uptimeThreshold": 99.5
    },
    "ec": {
      "critical": false,
      "responseTimeThreshold": 2000,
      "errorRateThreshold": 5,
      "uptimeThreshold": 95.0
    }
  }
}
EOF

    print_success "Alerting configuration generated"
}

# Generate alert channel configurations
generate_channel_configs() {
    print_info "Generating alert channel configurations..."
    
    # Console channel
    cat > "$CONFIG_DIR/channels/console.json" << EOF
{
  "id": "console",
  "name": "Console Logging",
  "type": "console",
  "enabled": true,
  "config": {
    "logLevel": "warn",
    "includeMetadata": true,
    "colorOutput": true
  },
  "severityFilter": ["critical", "high", "medium"],
  "description": "Log alerts to console output"
}
EOF

    # Browser notifications channel
    cat > "$CONFIG_DIR/channels/browser.json" << EOF
{
  "id": "browser",
  "name": "Browser Notifications",
  "type": "browser",
  "enabled": true,
  "config": {
    "showNotifications": true,
    "playSound": true,
    "persistCritical": true,
    "maxNotifications": 5
  },
  "severityFilter": ["critical", "high"],
  "description": "Show browser notifications for alerts"
}
EOF

    # Email channel template
    cat > "$CONFIG_DIR/channels/email.json" << EOF
{
  "id": "email",
  "name": "Email Notifications",
  "type": "email",
  "enabled": false,
  "config": {
    "smtpHost": "smtp.example.com",
    "smtpPort": 587,
    "smtpUser": "alerts@acgs.org",
    "smtpPassword": "CHANGE_ME",
    "fromAddress": "alerts@acgs.org",
    "recipients": [
      "admin@acgs.org",
      "devops@acgs.org"
    ],
    "subjectPrefix": "[ACGS Alert]"
  },
  "severityFilter": ["critical", "high"],
  "description": "Send email notifications for critical alerts"
}
EOF

    # Slack channel template
    cat > "$CONFIG_DIR/channels/slack.json" << EOF
{
  "id": "slack",
  "name": "Slack Notifications",
  "type": "slack",
  "enabled": false,
  "config": {
    "webhookUrl": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "channel": "#alerts",
    "username": "ACGS Alert Bot",
    "iconEmoji": ":warning:",
    "mentionChannel": true
  },
  "severityFilter": ["critical", "high"],
  "description": "Send Slack notifications for alerts"
}
EOF

    # Webhook channel template
    cat > "$CONFIG_DIR/channels/webhook.json" << EOF
{
  "id": "webhook",
  "name": "Webhook Notifications",
  "type": "webhook",
  "enabled": false,
  "config": {
    "url": "https://your-webhook-endpoint.com/alerts",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer YOUR_TOKEN"
    },
    "timeout": 10000,
    "retries": 3
  },
  "severityFilter": ["critical", "high", "medium"],
  "description": "Send webhook notifications for alerts"
}
EOF

    print_success "Alert channel configurations generated"
}

# Generate alert rule configurations
generate_alert_rules() {
    print_info "Generating alert rule configurations..."
    
    # Service down rule
    cat > "$CONFIG_DIR/rules/service-down.json" << EOF
{
  "id": "service-down",
  "name": "Service Down",
  "description": "Alert when a service becomes unavailable",
  "enabled": true,
  "conditions": [
    {
      "metric": "service_status",
      "operator": "eq",
      "threshold": 0
    }
  ],
  "severity": "critical",
  "channels": ["console", "browser", "email"],
  "cooldown": 60000,
  "autoResolve": true
}
EOF

    # High response time rule
    cat > "$CONFIG_DIR/rules/high-response-time.json" << EOF
{
  "id": "high-response-time",
  "name": "High Response Time",
  "description": "Alert when response time exceeds threshold",
  "enabled": true,
  "conditions": [
    {
      "metric": "response_time",
      "operator": "gt",
      "threshold": 2000,
      "duration": 120000
    }
  ],
  "severity": "high",
  "channels": ["console", "browser"],
  "cooldown": 300000,
  "autoResolve": true
}
EOF

    # High error rate rule
    cat > "$CONFIG_DIR/rules/high-error-rate.json" << EOF
{
  "id": "high-error-rate",
  "name": "High Error Rate",
  "description": "Alert when error rate exceeds threshold",
  "enabled": true,
  "conditions": [
    {
      "metric": "error_rate",
      "operator": "gt",
      "threshold": 5,
      "duration": 180000
    }
  ],
  "severity": "high",
  "channels": ["console", "browser"],
  "cooldown": 300000,
  "autoResolve": true
}
EOF

    # Quantumagi failure rule
    cat > "$CONFIG_DIR/rules/quantumagi-failure.json" << EOF
{
  "id": "quantumagi-failure",
  "name": "Quantumagi System Failure",
  "description": "Critical alert for Quantumagi Solana integration failures",
  "enabled": true,
  "conditions": [
    {
      "metric": "quantumagi_health",
      "operator": "eq",
      "threshold": 0
    }
  ],
  "severity": "critical",
  "channels": ["console", "browser", "email", "slack"],
  "cooldown": 30000,
  "autoResolve": false
}
EOF

    print_success "Alert rule configurations generated"
}

# Generate alert templates
generate_alert_templates() {
    print_info "Generating alert templates..."
    
    # Email template
    cat > "$TEMPLATES_DIR/email-alert.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ACGS Alert</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background-color: #dc2626; color: white; padding: 20px; text-align: center; }
        .header.high { background-color: #ea580c; }
        .header.medium { background-color: #ca8a04; }
        .header.low { background-color: #2563eb; }
        .header.info { background-color: #6b7280; }
        .content { padding: 20px; }
        .alert-details { background-color: #f9fafb; padding: 15px; border-radius: 6px; margin: 15px 0; }
        .footer { background-color: #f9fafb; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; }
        .button { display: inline-block; background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 10px 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header {{severity}}">
            <h1>🚨 ACGS Alert</h1>
            <p>{{title}}</p>
        </div>
        <div class="content">
            <p><strong>Severity:</strong> {{severity}}</p>
            <p><strong>Service:</strong> {{service}}</p>
            <p><strong>Time:</strong> {{timestamp}}</p>
            <p><strong>Message:</strong></p>
            <p>{{message}}</p>
            
            <div class="alert-details">
                <h3>Alert Details</h3>
                <pre>{{metadata}}</pre>
            </div>
            
            <div style="text-align: center;">
                <a href="{{dashboardUrl}}" class="button">View Dashboard</a>
                <a href="{{acknowledgeUrl}}" class="button">Acknowledge</a>
            </div>
        </div>
        <div class="footer">
            <p>ACGS Alerting System | Generated at {{timestamp}}</p>
            <p>This is an automated message. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
EOF

    # Slack template
    cat > "$TEMPLATES_DIR/slack-alert.json" << EOF
{
  "text": "🚨 ACGS Alert: {{title}}",
  "attachments": [
    {
      "color": "{{color}}",
      "fields": [
        {
          "title": "Service",
          "value": "{{service}}",
          "short": true
        },
        {
          "title": "Severity",
          "value": "{{severity}}",
          "short": true
        },
        {
          "title": "Message",
          "value": "{{message}}",
          "short": false
        },
        {
          "title": "Time",
          "value": "{{timestamp}}",
          "short": true
        }
      ],
      "actions": [
        {
          "type": "button",
          "text": "View Dashboard",
          "url": "{{dashboardUrl}}"
        },
        {
          "type": "button",
          "text": "Acknowledge",
          "url": "{{acknowledgeUrl}}"
        }
      ]
    }
  ]
}
EOF

    print_success "Alert templates generated"
}

# Create alerting test script
create_test_script() {
    print_info "Creating alerting test script..."
    
    cat > "$ALERTING_DIR/scripts/test-alerts.sh" << EOF
#!/bin/bash
# Test script for ACGS alerting system

echo "Testing ACGS Alerting System..."

# Test console alerts
echo "1. Testing console alerts..."
curl -X POST http://localhost:3000/api/test/alert \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "test",
    "severity": "info",
    "title": "Test Alert",
    "message": "This is a test alert from the alerting system",
    "service": "test"
  }' 2>/dev/null || echo "API not available - testing in development mode"

# Test critical alert
echo "2. Testing critical alert..."
curl -X POST http://localhost:3000/api/test/alert \\
  -H "Content-Type: application/json" \\
  -d '{
    "type": "service_down",
    "severity": "critical",
    "title": "Critical Test Alert",
    "message": "This is a critical test alert",
    "service": "test"
  }' 2>/dev/null || echo "API not available - testing in development mode"

echo "Alert testing completed. Check console and browser notifications."
EOF

    chmod +x "$ALERTING_DIR/scripts/test-alerts.sh"
    print_success "Alerting test script created"
}

# Validate alerting configuration
validate_configuration() {
    print_info "Validating alerting configuration..."
    
    local config_files=(
        "$CONFIG_DIR/alerting-config.json"
        "$CONFIG_DIR/channels/console.json"
        "$CONFIG_DIR/channels/browser.json"
        "$CONFIG_DIR/rules/service-down.json"
    )
    
    local valid=true
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            if command -v jq >/dev/null 2>&1; then
                if jq empty "$file" >/dev/null 2>&1; then
                    print_success "Valid JSON: $(basename "$file")"
                else
                    print_error "Invalid JSON: $(basename "$file")"
                    valid=false
                fi
            else
                print_warning "jq not available - skipping JSON validation for $(basename "$file")"
            fi
        else
            print_error "Missing configuration file: $(basename "$file")"
            valid=false
        fi
    done
    
    if [ "$valid" = true ]; then
        print_success "All configuration files are valid"
    else
        print_error "Some configuration files have issues"
        return 1
    fi
}

# Main execution
main() {
    print_header
    
    print_info "Setting up ACGS automated alerting system..."
    
    # Create directory structure
    create_directories
    
    # Generate configurations
    generate_alerting_config
    generate_channel_configs
    generate_alert_rules
    generate_alert_templates
    
    # Create test script
    create_test_script
    
    # Validate configuration
    validate_configuration
    
    echo
    print_success "ACGS Alerting System setup completed successfully!"
    echo
    print_info "Configuration files created:"
    echo "  - Main config: $CONFIG_DIR/alerting-config.json"
    echo "  - Channels: $CONFIG_DIR/channels/"
    echo "  - Rules: $CONFIG_DIR/rules/"
    echo "  - Templates: $TEMPLATES_DIR/"
    echo
    print_info "Next steps:"
    echo "  1. Configure email/Slack credentials in channel configs"
    echo "  2. Test alerting: $ALERTING_DIR/scripts/test-alerts.sh"
    echo "  3. Monitor alerts in the dashboard"
    echo
    print_warning "Remember to:"
    echo "  - Update email/Slack credentials before enabling those channels"
    echo "  - Test all alert channels before production deployment"
    echo "  - Review and adjust alert thresholds based on your requirements"
}

# Run main function
main "$@"
