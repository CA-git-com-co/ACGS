#!/bin/bash
# ACGS-PGP Installation Script
# Version: 3.0.0
# Last Updated: 2025-06-28

set -e

echo "🚀 ACGS-PGP Installation Script v3.0.0"
echo "========================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version is compatible (>= $required_version)"
else
    echo "❌ Python $python_version is not compatible. Please install Python >= $required_version"
    exit 1
fi

# Install Python dependencies with uv
echo "📦 Installing Python dependencies with uv..."
uv pip install -e . --index-strategy unsafe-best-match

# Install development dependencies
echo "🛠️ Installing development dependencies..."
uv pip install -e .[dev,test] --index-strategy unsafe-best-match

# Install NeMo-Skills separately (due to complex dependencies)
echo "🧠 Installing NeMo-Skills (optional)..."
uv pip install git+https://github.com/NVIDIA/NeMo-Skills.git --index-strategy unsafe-best-match || echo "⚠️ NeMo-Skills installation failed - continuing without it"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js >= 18.0.0"
    echo "Visit: https://nodejs.org/"
    exit 1
else
    node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -ge 18 ]; then
        echo "✅ Node.js $(node --version) is compatible"
    else
        echo "❌ Node.js $(node --version) is not compatible. Please install Node.js >= 18.0.0"
        exit 1
    fi
fi

# Install JavaScript dependencies
echo "📦 Installing JavaScript dependencies..."
cd project
npm ci
cd ..

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || echo "# ACGS-PGP Environment Variables" > .env
    echo "JWT_SECRET_KEY=test-jwt-secret-key-32-characters-minimum-length-required-for-validation" >> .env
    echo "DATABASE_URL=postgresql+asyncpg://acgs_user:strong_password_here@localhost:5432/acgs_pgp_db" >> .env
    echo "REDIS_URL=redis://localhost:6379/0" >> .env
    echo "ENVIRONMENT=development" >> .env
    echo "DEBUG=true" >> .env
    echo "✅ Created .env file with default values"
else
    echo "✅ .env file already exists"
fi

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
echo "Running Python tests..."
python3 -m pytest tests/unit/test_simple.py -v

echo "Running JavaScript tests..."
cd project
npm test -- --testPathPattern="Button.test.tsx" --passWithNoTests
cd ..

echo ""
echo "🎉 ACGS-PGP Installation Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo "1. Review and update .env file with your configuration"
echo "2. Start the development server:"
echo "   Backend:  uv run uvicorn services.main:app --reload"
echo "   Frontend: cd project && npm run dev"
echo "3. Run tests: uv run pytest"
echo "4. View documentation: open README.md"
echo ""
echo "🔗 Useful Commands:"
echo "   uv pip list                    # List installed packages"
echo "   uv pip install -e .[all]      # Install all optional dependencies"
echo "   uv run pytest --cov           # Run tests with coverage"
echo "   cd project && npm run build   # Build frontend for production"
echo ""
echo "📚 Documentation: https://github.com/CA-git-com-co/ACGS"
echo "🐛 Issues: https://github.com/CA-git-com-co/ACGS/issues"
