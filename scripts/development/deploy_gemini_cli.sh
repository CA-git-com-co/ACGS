#!/bin/bash

# Deploy Gemini CLI for ACGS
# This script sets up the Gemini CLI with full MCP support and ACGS integration

set -e

echo "==========================================="
echo "Deploying Gemini CLI for ACGS"
echo "==========================================="

# Check if running from project root
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: Please run this script from the ACGS project root directory"
    exit 1
fi

# Set up environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
GEMINI_CLI_DIR="services/cli/gemini_cli"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$GEMINI_CLI_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$GEMINI_CLI_DIR/venv"
fi

# Activate virtual environment
source "$GEMINI_CLI_DIR/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Gemini CLI
echo "Installing Gemini CLI..."
cd "$GEMINI_CLI_DIR"
pip install -e .
cd - > /dev/null

# Create configuration directory
CONFIG_DIR="$HOME/.gemini_cli"
mkdir -p "$CONFIG_DIR/logs"
mkdir -p "$CONFIG_DIR/mcp_servers"

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "WARNING: GEMINI_API_KEY environment variable not set"
    echo "Please set it with: export GEMINI_API_KEY='your-api-key'"
    echo ""
fi

# Initialize configuration if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "Initializing Gemini CLI configuration..."
    gemini-cli config init
fi

# Create systemd service for MCP servers (optional)
if command -v systemctl &> /dev/null; then
    echo "Creating systemd service for MCP servers..."
    cat > /tmp/gemini-mcp.service << EOF
[Unit]
Description=Gemini CLI MCP Servers
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
Environment="PYTHONPATH=$PWD"
Environment="CONSTITUTIONAL_HASH=cdd01ef066bc6cf2"
ExecStart=$GEMINI_CLI_DIR/venv/bin/python -m gemini_cli.mcp_servers.acgs_constitutional
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Note: Actual installation would require sudo
    echo "To install the systemd service, run:"
    echo "sudo cp /tmp/gemini-mcp.service /etc/systemd/system/"
    echo "sudo systemctl daemon-reload"
    echo "sudo systemctl enable gemini-mcp"
    echo "sudo systemctl start gemini-mcp"
fi

# Create helper scripts
echo "Creating helper scripts..."

# Create gemini-acgs wrapper
cat > "$CONFIG_DIR/gemini-acgs" << 'EOF'
#!/bin/bash
# Wrapper script for Gemini CLI with ACGS defaults

# Ensure ACGS services are running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Warning: ACGS Coordinator service not responding"
    echo "Please ensure ACGS services are running"
fi

# Set environment
export PYTHONPATH="${PYTHONPATH}:$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Run Gemini CLI
exec gemini-cli "$@"
EOF

chmod +x "$CONFIG_DIR/gemini-acgs"

# Create quick-start script
cat > "$CONFIG_DIR/quick-start.sh" << 'EOF'
#!/bin/bash
# Quick start script for Gemini CLI

echo "Gemini CLI Quick Start"
echo "====================="

# Check API key
if [ -z "$GEMINI_API_KEY" ]; then
    read -p "Enter your Gemini API key: " GEMINI_API_KEY
    export GEMINI_API_KEY
    echo "export GEMINI_API_KEY='$GEMINI_API_KEY'" >> ~/.bashrc
fi

# Create test agent
echo "Creating test agent..."
AGENT_RESULT=$(gemini-cli agent create --name "test-agent" --type "general" --capabilities code_generation data_analysis)
AGENT_ID=$(echo "$AGENT_RESULT" | grep -oP '"agent_id": "\K[^"]+')

echo "Agent created: $AGENT_ID"

# Test code execution
echo "Testing code execution..."
gemini-cli execute code --code "print('Gemini CLI with ACGS is working!')" --language python

# Check system status
echo "Checking system status..."
gemini-cli monitor status

echo ""
echo "Quick start complete! Your Gemini CLI is ready to use."
echo "Try: gemini-cli --help"
EOF

chmod +x "$CONFIG_DIR/quick-start.sh"

# Install additional MCP servers
echo "Setting up additional MCP servers..."

# Create MCP server launcher
cat > "$CONFIG_DIR/launch-mcp-servers.sh" << 'EOF'
#!/bin/bash
# Launch all MCP servers for Gemini CLI

LOG_DIR="$HOME/.gemini_cli/logs"
mkdir -p "$LOG_DIR"

echo "Launching MCP servers..."

# Kill any existing MCP processes
pkill -f "mcp_servers" || true

# Launch servers in background
servers=(
    "acgs_constitutional"
    "filesystem"
    "git"
    "database"
    "docker"
    "monitoring"
)

for server in "${servers[@]}"; do
    echo "Starting $server MCP server..."
    nohup python -m "gemini_cli.mcp_servers.$server" > "$LOG_DIR/mcp-$server.log" 2>&1 &
    echo $! > "$LOG_DIR/mcp-$server.pid"
done

echo "MCP servers launched. Check logs in $LOG_DIR"
EOF

chmod +x "$CONFIG_DIR/launch-mcp-servers.sh"

# Create stop script
cat > "$CONFIG_DIR/stop-mcp-servers.sh" << 'EOF'
#!/bin/bash
# Stop all MCP servers

LOG_DIR="$HOME/.gemini_cli/logs"

echo "Stopping MCP servers..."

for pidfile in "$LOG_DIR"/*.pid; do
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo "Stopped process $PID"
        fi
        rm "$pidfile"
    fi
done

echo "All MCP servers stopped"
EOF

chmod +x "$CONFIG_DIR/stop-mcp-servers.sh"

# Add to PATH
echo ""
echo "Adding Gemini CLI to PATH..."
if ! grep -q "gemini_cli/bin" ~/.bashrc; then
    echo "export PATH=\"\$PATH:$CONFIG_DIR\"" >> ~/.bashrc
fi

# Create command aliases
cat >> ~/.bash_aliases << 'EOF'

# Gemini CLI aliases
alias gcli='gemini-cli'
alias gcli-agent='gemini-cli agent'
alias gcli-exec='gemini-cli execute'
alias gcli-verify='gemini-cli verify'
alias gcli-audit='gemini-cli audit'
alias gcli-monitor='gemini-cli monitor'
alias gcli-mcp-start='~/.gemini_cli/launch-mcp-servers.sh'
alias gcli-mcp-stop='~/.gemini_cli/stop-mcp-servers.sh'
EOF

echo ""
echo "==========================================="
echo "Gemini CLI Deployment Complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Set your Gemini API key:"
echo "   export GEMINI_API_KEY='your-api-key'"
echo ""
echo "2. Source your shell configuration:"
echo "   source ~/.bashrc"
echo ""
echo "3. Run the quick start:"
echo "   ~/.gemini_cli/quick-start.sh"
echo ""
echo "4. Start using Gemini CLI:"
echo "   gemini-cli --help"
echo ""
echo "Optional: Launch MCP servers:"
echo "   gcli-mcp-start"
echo ""
echo "For more information, see:"
echo "   $GEMINI_CLI_DIR/README.md"
echo "==========================================="