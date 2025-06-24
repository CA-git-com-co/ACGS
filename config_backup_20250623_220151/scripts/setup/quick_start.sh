#!/bin/bash
set -e

echo "🚀 ACGS-1 Quick Start Setup"
echo "=========================="

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"

# Setup Python environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install service-specific dependencies
for service_dir in services/core/*/; do
    if [ -f "${service_dir}requirements.txt" ]; then
        echo "📦 Installing dependencies for ${service_dir}..."
        pip install -r "${service_dir}requirements.txt"
    fi
done

echo "✅ Python environment ready"

# Setup environment variables
echo "🔧 Setting up environment variables..."
cp -n config/env/.env.example config/env/.env
source scripts/set_service_env.sh

echo "✅ Environment variables set"

# Start development services
echo "🚀 Starting development services..."
cd infrastructure/docker
docker-compose -f docker-compose.dev.yml up -d
cd ../..

# Run health check
echo "🔍 Running health check..."
./scripts/health_check_all_services.sh

echo "🎉 Quick start setup complete! Your development environment is ready."
echo "To activate the environment in new terminals, run: source venv/bin/activate"
