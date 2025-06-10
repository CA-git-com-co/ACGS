#!/bin/bash
# ACGS-1 Developer Onboarding Script
# Sets up development environment for new contributors

set -e

echo "🚀 Welcome to ACGS-1 Development Environment Setup!"
echo "=================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if running on supported OS
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Operating system: $OSTYPE"
else
    echo "⚠️  Warning: Untested OS. Proceed with caution."
fi

# Check Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version)"
else
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

# Check Rust
if command -v rustc &> /dev/null; then
    echo "✅ Rust: $(rustc --version)"
else
    echo "📦 Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# Check Solana CLI
if command -v solana &> /dev/null; then
    echo "✅ Solana CLI: $(solana --version)"
else
    echo "📦 Installing Solana CLI..."
    sh -c "$(curl -sSfL https://release.solana.com/v1.18.22/install)"
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
fi

# Check Anchor CLI
if command -v anchor &> /dev/null; then
    echo "✅ Anchor CLI: $(anchor --version)"
else
    echo "📦 Installing Anchor CLI..."
    cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
    avm install 0.29.0
    avm use 0.29.0
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python: $(python3 --version)"
else
    echo "❌ Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "⚠️  Docker not found. Install Docker for containerized development."
fi

echo ""
echo "🔧 Setting up development environment..."

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies for governance dashboard
echo "📦 Installing Node.js dependencies..."
cd applications/governance-dashboard
npm install
cd ../..

# Build Anchor programs
echo "🔨 Building Anchor programs..."
cd blockchain
anchor build
cd ..

# Set up Solana configuration
echo "⚙️  Configuring Solana for devnet..."
solana config set --url devnet
solana config set --keypair ~/.config/solana/id.json

# Create keypair if it doesn't exist
if [ ! -f ~/.config/solana/id.json ]; then
    echo "🔑 Creating Solana keypair..."
    solana-keygen new --outfile ~/.config/solana/id.json --no-bip39-passphrase
fi

# Request airdrop for devnet testing
echo "💰 Requesting SOL airdrop for devnet testing..."
solana airdrop 2 || echo "⚠️  Airdrop failed. You may need to request manually."

# Run basic health checks
echo "🏥 Running health checks..."
cd blockchain
anchor test --skip-deploy || echo "⚠️  Some tests failed. Check configuration."
cd ..

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Read CONTRIBUTING.md for development guidelines"
echo "2. Check docs/development/ for detailed guides"
echo "3. Run './run_tests.sh' to validate your setup"
echo "4. Start developing in your chosen area:"
echo "   - Blockchain: blockchain/programs/"
echo "   - Backend: services/core/ or services/platform/"
echo "   - Frontend: applications/"
echo "   - Integration: integrations/"
echo ""
echo "🤝 Happy coding! Welcome to the ACGS-1 team!"
