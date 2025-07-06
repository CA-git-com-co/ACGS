# Gemini CLI for ACGS

A powerful command-line interface that integrates Google's Gemini AI with the ACGS (AI Constitutional Governance System) for maximum capability while ensuring constitutional compliance and governance.

## Features

### 🚀 Core Capabilities
- **Full Gemini AI Integration**: Access to Gemini Pro models with enhanced tools
- **Constitutional Governance**: All operations validated against ACGS principles
- **MCP Support**: Model Context Protocol servers for extended functionality
- **Comprehensive Tool Suite**:
  - File system operations
  - Web fetching and search
  - Shell command execution
  - Persistent memory
  - Sandboxed code execution
  - Multi-file operations

### 🛡️ Security & Governance
- **Agent Identity Management**: Secure agent registration and authentication
- **Policy Verification**: Real-time policy compliance checking
- **Audit Trail**: Cryptographic audit logging with blockchain anchoring
- **Human-in-the-Loop**: Automatic escalation for high-risk operations
- **Formal Verification**: Z3-powered constitutional compliance

### 📊 Monitoring & Operations
- **Real-time Health Monitoring**: Service status and performance metrics
- **Alert Management**: Severity-based alert system
- **Performance Analytics**: Operation latency and throughput tracking
- **Comprehensive Logging**: Structured logs with telemetry support

## Installation

### Prerequisites
- Python 3.9+
- ACGS services running (see main ACGS documentation)
- Gemini API key

### Install from source
```bash
cd services/cli/gemini_cli
pip install -e .
```

### Set up configuration
```bash
# Initialize configuration
gemini-cli config init

# Set your Gemini API key
export GEMINI_API_KEY="your-api-key-here"
# Or
gemini-cli config set api_key "your-api-key-here"
```

## Quick Start

### 1. Create an Agent
```bash
# Create a new AI agent
gemini-cli agent create --name "my-assistant" --type "general" --capabilities code_generation data_analysis

# List all agents
gemini-cli agent list

# Get agent details
gemini-cli agent get <agent-id>
```

### 2. Execute Code with Governance
```bash
# Execute Python code
gemini-cli execute code --code "print('Hello ACGS!')" --language python

# Execute from file
gemini-cli execute file script.py

# Execute with Gemini assistance
gemini-cli execute assist "Write a function to analyze CSV data"
```

### 3. Verify Policies
```bash
# Check constitutional compliance
gemini-cli verify constitutional "delete_user_data" --params params.json

# Verify custom policy
gemini-cli verify policy policy.rego --context context.json

# Analyze operation risk
gemini-cli verify risk --operation operation.json --detailed
```

### 4. Monitor System
```bash
# Check system status
gemini-cli monitor status --detailed

# View real-time health
gemini-cli monitor health --continuous

# Show performance metrics
gemini-cli monitor performance --operation-type code_execution
```

### 5. Audit Trail
```bash
# List recent audit entries
gemini-cli audit list --from "2025-01-01"

# Verify audit integrity
gemini-cli audit verify --operation-id <op-id>

# Export audit trail
gemini-cli audit export audit_report.json --format json
```

## Advanced Usage

### MCP Server Configuration

The Gemini CLI automatically starts MCP servers for enhanced capabilities:

1. **Filesystem MCP**: Enhanced file operations
2. **Git MCP**: Version control integration
3. **Database MCP**: Direct database access
4. **Constitutional MCP**: Policy enforcement
5. **Docker MCP**: Container management
6. **Monitoring MCP**: Metrics and observability

Disable MCP servers:
```bash
gemini-cli --no-mcp <command>
```

### Tool Management
```bash
# List available tools
gemini-cli tools list

# Enable/disable specific tools
gemini-cli tools enable web_search
gemini-cli tools disable shell_execution
```

### Output Formats
```bash
# JSON output
gemini-cli agent list --format json

# Table format (default)
gemini-cli agent list --format table

# Plain text
gemini-cli agent list --format text
```

### Batch Operations
```bash
# Batch verify multiple policies
cat > batch.json << EOF
[
  {"type": "policy", "policy": "policy1.rego", "context": {}},
  {"type": "constitutional", "action": "data_deletion", "parameters": {}}
]
EOF

gemini-cli verify batch batch.json --parallel
```

## Configuration

### Configuration File Location
- Default: `~/.gemini_cli/config.json`
- Custom: `gemini-cli --config /path/to/config.json`

### Configuration Options
```json
{
  "api_key": "your-gemini-api-key",
  "model": "gemini-1.5-pro",
  "temperature": 0.7,
  "max_tokens": 8192,
  "acgs_coordinator_url": "http://localhost:8000",
  "auth_service_url": "http://localhost:8006",
  "tools": {
    "file_system": true,
    "web_fetch": true,
    "web_search": true,
    "shell_execution": true,
    "memory": true,
    "sandbox_execution": true
  },
  "mcp_servers": [
    {
      "name": "filesystem",
      "command": ["python", "-m", "mcp_servers.filesystem"],
      "enabled": true
    }
  ],
  "telemetry_enabled": true,
  "log_level": "INFO"
}
```

## Architecture

### Component Overview
```
┌─────────────────────────────────────────────────────────────┐
│                        Gemini CLI                            │
├─────────────────────────────────────────────────────────────┤
│  Commands Layer                                              │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌───────┐ ┌─────────┐ │
│  │  Agent  │ │ Execute │ │ Verify │ │ Audit │ │ Monitor │ │
│  └─────────┘ └─────────┘ └────────┘ └───────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Integration Layer                                           │
│  ┌──────────────┐ ┌───────────────┐ ┌──────────────────┐  │
│  │ ACGS Client  │ │ Tool Manager  │ │ MCP Servers      │  │
│  └──────────────┘ └───────────────┘ └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ACGS Services                                              │
│  ┌────────────┐ ┌─────────┐ ┌────────┐ ┌───────┐          │
│  │Coordinator │ │ Sandbox │ │ Verify │ │ Audit │          │
│  └────────────┘ └─────────┘ └────────┘ └───────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Security Model
1. **Agent Authentication**: API key-based authentication
2. **Constitutional Validation**: Every operation checked against principles
3. **Sandboxed Execution**: Isolated Docker containers
4. **Audit Logging**: Tamper-proof audit trail
5. **HITL Review**: Human oversight for high-risk operations

## Development

### Running Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Full test suite
pytest
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Service Connection Failed**
   ```bash
   # Check service health
   gemini-cli monitor health
   
   # Verify service URLs
   gemini-cli config show
   ```

2. **Authentication Error**
   ```bash
   # Check API key
   echo $GEMINI_API_KEY
   
   # Create new agent with fresh credentials
   gemini-cli agent create --name "new-agent" --type "general"
   ```

3. **MCP Server Issues**
   ```bash
   # Run without MCP
   gemini-cli --no-mcp <command>
   
   # Check MCP logs
   tail -f ~/.gemini_cli/logs/mcp-*.log
   ```

### Debug Mode
```bash
# Enable debug logging
gemini-cli --log-level DEBUG <command>

# View logs
tail -f ~/.gemini_cli/logs/gemini-cli.log
```

## License

This project is part of the ACGS system and follows the same licensing terms.

## Support

- Documentation: See main ACGS documentation
- Issues: GitHub Issues
- Community: ACGS Discord/Slack channel