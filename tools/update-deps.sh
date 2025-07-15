# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-PGP Dependency Update Script
# Version: 3.0.0
# Last Updated: 2025-06-28

set -e

echo "🔄 ACGS-PGP Dependency Update Script v3.0.0"
echo "============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "project/package.json" ]; then
    print_error "This script must be run from the ACGS project root directory"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install Node.js first"
    exit 1
fi

# Backup current state
print_status "Creating backup of current dependency state..."
mkdir -p .backup
cp pyproject.toml .backup/pyproject.toml.backup
cp project/package.json .backup/package.json.backup
cp project/package-lock.json .backup/package-lock.json.backup 2>/dev/null || true
uv pip freeze > .backup/requirements-before.txt 2>/dev/null || true
print_success "Backup created in .backup/ directory"

# Update Python dependencies
print_status "Updating Python dependencies with uv..."

# Check for outdated packages
print_status "Checking for outdated Python packages..."
uv pip list --outdated || print_warning "Could not check outdated packages"

# Update dependencies
print_status "Updating Python dependencies..."
uv pip install --upgrade -e .[all]

# Update NeMo-Skills separately (it's a Git dependency)
print_status "Updating NeMo-Skills from GitHub..."
uv pip install --upgrade --force-reinstall git+https://github.com/NVIDIA/NeMo-Skills.git

# Generate updated requirements.txt for compatibility
print_status "Generating updated requirements.txt..."
uv pip freeze > requirements-frozen.txt

# Update JavaScript dependencies
print_status "Updating JavaScript dependencies..."
cd project

# Check for outdated packages
print_status "Checking for outdated JavaScript packages..."
npm outdated || print_warning "Some packages are outdated"

# Security audit
print_status "Running security audit..."
npm audit || print_warning "Security vulnerabilities found - consider running 'npm audit fix'"

# Update dependencies
print_status "Updating JavaScript dependencies..."
npm update

# Update dev dependencies
print_status "Updating dev dependencies..."
npm update --save-dev

cd ..

# Run tests to verify everything still works
print_status "Running tests to verify updates..."

# Test Python
print_status "Testing Python components..."
if uv run pytest tests/unit/test_simple.py tests/unit/test_auth_basic.py -v; then
    print_success "Python tests passed"
else
    print_error "Python tests failed - consider rolling back"
    exit 1
fi

# Test JavaScript
print_status "Testing JavaScript components..."
cd project
if npm test -- --testPathPattern="Button.test.tsx|provider.test.tsx" --passWithNoTests; then
    print_success "JavaScript tests passed"
else
    print_error "JavaScript tests failed - consider rolling back"
    cd ..
    exit 1
fi
cd ..

# Check for security vulnerabilities
print_status "Running security checks..."

# Python security check (if safety is installed)
if command -v safety &> /dev/null; then
    print_status "Running Python security audit..."
    safety check || print_warning "Python security issues found"
else
    print_warning "Safety not installed - skipping Python security audit"
    print_status "Install with: uv pip install safety"
fi

# JavaScript security check
print_status "Running JavaScript security audit..."
cd project
npm audit --audit-level=moderate || print_warning "JavaScript security issues found"
cd ..

# Generate update summary
print_status "Generating update summary..."
echo "# Dependency Update Summary - $(date)" > UPDATE_SUMMARY.md
echo "" >> UPDATE_SUMMARY.md
echo "## Python Dependencies" >> UPDATE_SUMMARY.md
echo "\`\`\`" >> UPDATE_SUMMARY.md
uv pip list >> UPDATE_SUMMARY.md
echo "\`\`\`" >> UPDATE_SUMMARY.md
echo "" >> UPDATE_SUMMARY.md
echo "## JavaScript Dependencies" >> UPDATE_SUMMARY.md
echo "\`\`\`" >> UPDATE_SUMMARY.md
cd project && npm list --depth=0 >> ../UPDATE_SUMMARY.md
cd ..
echo "\`\`\`" >> UPDATE_SUMMARY.md

# Cleanup
print_status "Cleaning up..."
rm -f requirements-frozen.txt

print_success "Dependency update completed successfully!"
echo ""
echo "📋 Summary:"
echo "✅ Python dependencies updated with uv"
echo "✅ JavaScript dependencies updated with npm"
echo "✅ Tests passed"
echo "✅ Security audit completed"
echo "✅ Update summary generated: UPDATE_SUMMARY.md"
echo "✅ Backup created in .backup/ directory"
echo ""
echo "🔄 Next Steps:"
echo "1. Review UPDATE_SUMMARY.md for changes"
echo "2. Test your application thoroughly"
echo "3. Commit the changes:"
echo "   git add pyproject.toml project/package.json project/package-lock.json"
echo "   git commit -m 'chore: update dependencies'"
echo "4. If issues occur, restore from backup:"
echo "   cp .backup/pyproject.toml.backup pyproject.toml"
echo "   cp .backup/package.json.backup project/package.json"
echo "   cp .backup/package-lock.json.backup project/package-lock.json"
echo ""
print_success "Update process complete! 🎉"
