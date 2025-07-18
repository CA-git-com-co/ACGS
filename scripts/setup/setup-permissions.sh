# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Setup script permissions
echo "🔧 Setting up script permissions..."

chmod +x scripts/robust-github-connectivity-check.sh
chmod +x scripts/network-diagnostics.sh
chmod +x scripts/docker-connectivity-check.sh

echo "✅ All scripts are now executable"
echo "📋 Available scripts:"
echo "  - scripts/robust-github-connectivity-check.sh (main connectivity check)"
echo "  - scripts/network-diagnostics.sh (comprehensive diagnostics)"
echo "  - scripts/docker-connectivity-check.sh (Docker-based testing)"
