# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
set -e

echo "🚀 ACGS-1 Quick Start Setup"
echo "=========================="

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r config/environments/requirements.txt

echo "✅ Python environment ready"

# Setup Node.js environment
echo "📦 Setting up Node.js environment..."
npm install
cd blockchain && npm install && cd ..

echo "✅ Node.js environment ready"

# Install Solana CLI (optional)
echo "🔗 Installing Solana CLI..."
if ! command -v solana >/dev/null 2>&1; then
    sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
fi

echo "✅ Solana CLI installed"

# Install Anchor (optional)
echo "⚓ Installing Anchor..."
if ! command -v anchor >/dev/null 2>&1; then
    cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
    avm install latest
    avm use latest
fi

echo "✅ Anchor installed"

# Run initial tests
echo "🧪 Running initial tests..."
python -m pytest tests/unit/ -v
cd blockchain && anchor test && cd ..

echo "🎉 Setup complete! You're ready to contribute to ACGS-1!"
echo ""
echo "Next steps:"
echo "1. Read the onboarding guide: docs/CONTRIBUTOR_ONBOARDING.md"
echo "2. Join our Discord: https://discord.gg/acgs"
echo "3. Pick your first issue: https://github.com/CA-git-com-co/ACGS/labels/good%20first%20issue"
