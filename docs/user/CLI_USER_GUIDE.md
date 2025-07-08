# ACGS-2 CLI User Guide

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

The ACGS-2 Command Line Interface provides powerful tools for interacting with the constitutional AI governance system. This guide covers all CLI tools available in the ACGS-2 ecosystem.

## Available CLI Tools

### 1. Main ACGS CLI (`acgs`)
Primary Python-based CLI for core ACGS operations

### 2. OpenCode CLI (`services/cli/opencode/`)
Modern TypeScript/Bun-based CLI with MCP integration

### 3. TUI Interface
Go-based terminal user interface for interactive operations

### 4. Blockchain CLI
Solana/Anchor CLI tools for blockchain operations

## Installation and Setup

### Prerequisites

```bash
# Ensure ACGS-2 is installed
pip install -e ".[cli,dev]"

# For OpenCode CLI (requires Bun)
curl -fsSL https://bun.sh/install | bash
cd services/cli/opencode && bun install

# For blockchain CLI (requires Anchor)
npm install -g @coral-xyz/anchor-cli
```

### Configuration

Create a CLI configuration file:

```bash
# Create CLI config directory
mkdir -p ~/.acgs

# Create configuration file
cat > ~/.acgs/config.yaml << EOF
constitutional_hash: cdd01ef066bc6cf2
default_tenant_id: your-tenant-id
api_base_url: http://localhost
services:
  constitutional_core: 8001
  integrity_service: 8002
  governance_engine: 8004
  authentication: 8016
auth:
  api_key: your-api-key
  # OR use JWT token
  jwt_token: your-jwt-token
performance:
  timeout_seconds: 30
  retries: 3
EOF
```

## Main ACGS CLI (`acgs`)

### Authentication

```bash
# Login to ACGS system
acgs auth login --tenant-id your-tenant --username your-email

# Verify authentication
acgs auth status

# Logout
acgs auth logout
```

### Constitutional Validation

```bash
# Validate a decision using CLI
acgs constitutional validate \
  --description "Deploy AI sentiment analysis model" \
  --domain "social_media" \
  --impact-level "medium" \
  --tenant-id "social-platform-001"

# Validate from JSON file
acgs constitutional validate --file decision.json

# Example decision.json:
{
  "description": "Healthcare AI diagnostic tool",
  "context": {
    "domain": "healthcare",
    "impact_level": "high",
    "regulatory_framework": "HIPAA",
    "affected_populations": ["patients", "healthcare_providers"]
  }
}
```

Example output:
```
✓ Constitutional Validation Complete
  Constitutional Hash: cdd01ef066bc6cf2
  Compliance Score: 0.94
  Status: COMPLIANT
  
  Recommendations:
  • Implement bias monitoring for demographic groups
  • Ensure model explainability for clinical decisions
  • Add patient consent verification workflow
  
  Audit ID: audit_789xyz
  Timestamp: 2025-01-08T10:30:00Z
```

### Policy Operations

```bash
# Evaluate policy compliance
acgs policy evaluate \
  --type constitutional \
  --input-file policy-input.json \
  --tenant-id healthcare-org-001

# Synthesize new policy
acgs policy synthesize \
  --domain healthcare \
  --regulations HIPAA,FDA \
  --use-case diagnostic_ai \
  --output synthesized-policy.json

# List available policies
acgs policy list --tenant-id your-tenant
```

### Audit Operations

```bash
# Query audit trail
acgs audit query \
  --tenant-id healthcare-org-001 \
  --start-date 2025-01-01 \
  --event-type constitutional_validation \
  --output audit-report.json

# Create manual audit entry
acgs audit create \
  --event-type manual_review \
  --data '{"reviewer": "admin", "decision": "approved"}' \
  --tenant-id your-tenant

# Export audit report
acgs audit export \
  --format csv \
  --tenant-id your-tenant \
  --date-range 2025-01-01:2025-01-31 \
  --output audit-january-2025.csv
```

### Service Management

```bash
# Check service health
acgs service health --all

# Detailed service status
acgs service status constitutional-core

# View service metrics
acgs service metrics --service governance-engine --format json

# Service configuration
acgs service config --service integrity-service
```

### Performance Monitoring

```bash
# Get performance report
acgs performance report --tenant-id your-tenant

# Monitor real-time metrics
acgs performance monitor --services constitutional-core,governance-engine

# Performance baseline test
acgs performance test --target-latency 5ms --target-rps 100
```

## OpenCode CLI

The modern TypeScript/Bun-based CLI with advanced features and MCP integration.

### Setup

```bash
cd services/cli/opencode
bun install

# Make CLI globally available
bun link

# Or run directly
bun run src/index.ts
```

### Constitutional Operations

```bash
# Constitutional validation with MCP integration
opencode constitutional validate \
  --decision-file decision.json \
  --tenant healthcare-org-001 \
  --mcp-enabled

# Multi-agent constitutional analysis
opencode constitutional analyze \
  --input-file complex-decision.json \
  --agents ethics,legal,operational \
  --consensus-threshold 0.8

# Constitutional compliance monitoring
opencode constitutional monitor \
  --tenant your-tenant \
  --watch \
  --alerts
```

### Agent Coordination

```bash
# Spawn constitutional analysis agents
opencode agents spawn \
  --types ethics,legal,operational \
  --decision-context healthcare \
  --tenant healthcare-org-001

# View active agents
opencode agents list --tenant your-tenant

# Agent consensus decision
opencode agents consensus \
  --agents agent1,agent2,agent3 \
  --algorithm weighted_vote \
  --decision-id decision_123
```

### Integration Features

```bash
# GitHub integration with constitutional compliance
opencode github analyze-pr \
  --repo your-org/your-repo \
  --pr-number 123 \
  --constitutional-check

# File system operations with governance
opencode fs scan \
  --directory /path/to/code \
  --constitutional-patterns \
  --output governance-scan.json

# Browser automation with compliance
opencode browser navigate \
  --url https://your-service.com \
  --constitutional-monitor \
  --compliance-check
```

## Blockchain CLI

Specialized CLI for Solana/Anchor blockchain operations with constitutional compliance.

### Setup

```bash
cd services/blockchain

# Install dependencies
bun install

# Configure Solana CLI (one-time setup)
solana config set --url devnet
solana-keygen new --outfile ~/.config/solana/id.json
```

### Constitutional Blockchain Operations

```bash
# Initialize constitutional governance on-chain
blockchain init-constitution \
  --network devnet \
  --authority ~/.config/solana/id.json \
  --constitutional-hash cdd01ef066bc6cf2

# Deploy governance programs
blockchain deploy \
  --program quantumagi-core \
  --network devnet \
  --constitutional-validation

# Constitutional transaction submission
blockchain submit-decision \
  --decision-id decision_123 \
  --compliance-score 0.94 \
  --network devnet

# Query on-chain constitutional data
blockchain query-constitution \
  --network devnet \
  --output constitutional-state.json

# Governance voting
blockchain vote \
  --proposal proposal_456 \
  --vote approve \
  --rationale "Meets constitutional requirements" \
  --network devnet
```

## TUI (Terminal User Interface)

Interactive terminal interface for ACGS operations.

### Launch TUI

```bash
# Start interactive TUI
acgs tui

# Or with specific tenant context
acgs tui --tenant healthcare-org-001
```

### TUI Features

The TUI provides interactive screens for:

1. **Dashboard**: Real-time system status and metrics
2. **Constitutional Validation**: Interactive decision validation
3. **Audit Explorer**: Browse and search audit trails
4. **Policy Manager**: Visual policy creation and editing
5. **Agent Monitor**: Real-time agent coordination status
6. **Performance Monitor**: Live performance metrics and alerts

### TUI Navigation

```
Navigation Keys:
  Tab/Shift+Tab  - Move between panels
  Enter          - Select/Activate
  Esc            - Back/Cancel
  q              - Quit
  h              - Help
  /              - Search
  F1-F5          - Quick access to main screens
```

## Advanced CLI Usage

### Batch Operations

```bash
# Batch constitutional validation
acgs constitutional validate-batch \
  --input-directory decisions/ \
  --output-format json \
  --parallel 5 \
  --tenant-id batch-tenant

# Bulk audit export
acgs audit export-bulk \
  --tenants tenant1,tenant2,tenant3 \
  --date-range 2025-01-01:2025-01-31 \
  --format csv \
  --output-directory ./exports/
```

### Scripting and Automation

```bash
#!/bin/bash
# constitutional-monitor.sh - Automated constitutional monitoring

# Set constitutional compliance monitoring
acgs constitutional monitor \
  --tenant-id production-tenant \
  --compliance-threshold 0.95 \
  --alert-webhook https://your-alerts.com/webhook \
  --daemon

# Check performance targets
PERFORMANCE_REPORT=$(acgs performance report --tenant-id production-tenant --format json)
P99_LATENCY=$(echo $PERFORMANCE_REPORT | jq '.performance_metrics.p99_latency_ms')

if (( $(echo "$P99_LATENCY > 5.0" | bc -l) )); then
  echo "WARNING: P99 latency exceeded target: ${P99_LATENCY}ms"
  acgs alerts send \
    --type performance_degradation \
    --message "P99 latency: ${P99_LATENCY}ms exceeds 5ms target" \
    --tenant-id production-tenant
fi
```

### Configuration Management

```bash
# Environment-specific configurations
acgs config set-environment production \
  --api-url https://acgs-prod.your-domain.com \
  --tenant-id prod-tenant \
  --auth-method jwt

acgs config set-environment development \
  --api-url http://localhost \
  --tenant-id dev-tenant \
  --auth-method api-key

# Switch environments
acgs config use-environment production

# Export configuration
acgs config export --output acgs-config-backup.yaml

# Import configuration
acgs config import --file acgs-config-backup.yaml
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

```bash
# Clear cached credentials
acgs auth clear

# Re-authenticate
acgs auth login --tenant your-tenant --username your-email

# Verify token validity
acgs auth verify
```

#### 2. Service Connection Issues

```bash
# Test service connectivity
acgs service ping --all

# Check service health
acgs service health --verbose

# Test specific service
curl -f http://localhost:8001/health
```

#### 3. Constitutional Hash Mismatches

```bash
# Verify constitutional hash configuration
acgs config show | grep constitutional_hash

# Update constitutional hash
acgs config set constitutional_hash cdd01ef066bc6cf2

# Validate constitutional compliance
acgs constitutional verify-compliance
```

#### 4. Performance Issues

```bash
# Performance diagnostic
acgs performance diagnose --tenant your-tenant

# Network latency test
acgs network test --services constitutional-core,governance-engine

# Cache status check
acgs cache status --tenant your-tenant
```

### Debug Mode

```bash
# Enable debug logging
export ACGS_LOG_LEVEL=DEBUG

# Run CLI with verbose output
acgs --verbose constitutional validate --file decision.json

# Trace API calls
acgs --trace-requests service health --all
```

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/constitutional-compliance.yml
name: Constitutional Compliance Check

on: [push, pull_request]

jobs:
  constitutional-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup ACGS CLI
      run: |
        pip install -e ".[cli]"
        echo "${{ secrets.ACGS_CONFIG }}" > ~/.acgs/config.yaml
    
    - name: Validate Constitutional Compliance
      run: |
        acgs constitutional validate-codebase \
          --directory . \
          --tenant-id ci-tenant \
          --fail-on-violation \
          --output compliance-report.json
    
    - name: Upload Compliance Report
      uses: actions/upload-artifact@v2
      with:
        name: constitutional-compliance-report
        path: compliance-report.json
```

### Docker Integration

```dockerfile
# Dockerfile for ACGS CLI in container
FROM python:3.11-slim

WORKDIR /app

# Install ACGS CLI
COPY . .
RUN pip install -e ".[cli]"

# Configuration
COPY config/acgs-config.yaml /root/.acgs/config.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD acgs service health --quiet || exit 1

ENTRYPOINT ["acgs"]
```

### Monitoring Integration

```bash
# Prometheus metrics export
acgs performance metrics \
  --format prometheus \
  --output /var/lib/prometheus/acgs-metrics.prom

# Grafana dashboard data
acgs performance dashboard-data \
  --tenant your-tenant \
  --time-range 24h \
  --format grafana-json > dashboard-data.json
```

## CLI Reference

### Global Options

```
--config-file PATH      Configuration file path (default: ~/.acgs/config.yaml)
--tenant-id ID          Tenant ID for operations
--verbose              Enable verbose output
--quiet                Suppress non-essential output
--format FORMAT        Output format (json, yaml, table, csv)
--output FILE          Output file path
--timeout SECONDS      Request timeout (default: 30)
--no-color             Disable colored output
--trace-requests       Trace HTTP requests
```

### Exit Codes

```
0   - Success
1   - General error
2   - Configuration error
3   - Authentication error
4   - Service unavailable
5   - Constitutional compliance violation
6   - Performance target not met
7   - Validation failed
8   - Permission denied
```

---

**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Last Updated**: 2025-01-08  
**CLI Version**: 2.0.0

For additional help with any CLI command, use the `--help` flag:
```bash
acgs --help
acgs constitutional --help
acgs constitutional validate --help
```