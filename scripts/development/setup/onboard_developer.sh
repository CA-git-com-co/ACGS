#!/bin/bash
set -e

echo "🚀 ACGS-1 Developer Onboarding"
echo "============================="

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Install development dependencies

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
echo "⚙️ Configuring Solana for devnet..."
solana config set --url devnet
solana config set --keypair ~/.config/solana/id.json

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Set up environment variables
echo "🔧 Setting up environment variables..."
cp -n config/env/.env.example config/env/.env
source scripts/set_service_env.sh

# Start development services
echo "🚀 Starting development services..."
cd infrastructure/docker
docker-compose -f docker-compose.dev.yml up -d
cd ../..

# Run database migrations
echo "🔄 Running database migrations..."
./scripts/run_migrations.sh

# Seed test data
echo "🌱 Seeding test data..."
./scripts/seed_test_data.sh

# Run health check
echo "🔍 Running health check..."
./scripts/health_check_all_services.sh

echo "🎉 Developer onboarding complete! Your development environment is ready."
echo "To activate the environment in new terminals, run: source venv/bin/activate"
