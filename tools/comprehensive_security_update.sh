#!/bin/bash

# ACGS Comprehensive Security Update Script
# Updates all dependencies to their latest secure versions

echo "🔒 ACGS Comprehensive Security Update"
echo "===================================="
echo ""

# Update pip and essential tools
echo "📦 Updating pip and essential tools..."
python -m pip install --upgrade pip setuptools wheel pip-tools

# Update all Python dependencies to latest secure versions
echo "📦 Updating all Python dependencies..."

# Core dependencies with known vulnerabilities
pip install --upgrade \
    "fastapi>=0.115.6" \
    "uvicorn[standard]>=0.34.0" \
    "pydantic>=2.10.5" \
    "httpx>=0.28.1" \
    "cryptography>=45.0.4" \
    "pyjwt>=2.10.0" \
    "python-jose[cryptography]>=3.3.0" \
    "passlib[bcrypt]>=1.7.4" \
    "python-multipart>=0.0.10" \
    "sqlalchemy>=2.0.36" \
    "alembic>=1.16.0" \
    "redis>=5.2.1" \
    "asyncpg>=0.30.0" \
    "psycopg2-binary>=2.9.10" \
    "prometheus-client>=0.21.1" \
    "opentelemetry-api>=1.29.0" \
    "opentelemetry-sdk>=1.29.0" \
    "pyyaml>=6.0.2" \
    "click>=8.1.8" \
    "rich>=13.10.0" \
    "pytest>=8.3.4" \
    "pytest-asyncio>=0.25.0" \
    "pytest-cov>=6.0.0"

# Update requirements files in all services
echo "📝 Updating requirements files..."

# Function to update a requirements file
update_requirements() {
    local req_file=$1
    if [ -f "$req_file" ]; then
        echo "  Updating $req_file..."
        # Create backup
        cp "$req_file" "${req_file}.backup"
        
        # Generate updated requirements
        pip freeze > "$req_file.tmp"
        
        # Keep comments and structure
        grep "^#" "$req_file" > "$req_file.new" || true
        echo "" >> "$req_file.new"
        grep -v "^#" "$req_file.tmp" >> "$req_file.new"
        
        # Replace original
        mv "$req_file.new" "$req_file"
        rm -f "$req_file.tmp"
    fi
}

# Update main requirements
update_requirements "requirements.txt"
update_requirements "requirements-test.txt"

# Update service requirements
find services -name "requirements*.txt" | while read req_file; do
    update_requirements "$req_file"
done

# Run security audit
echo ""
echo "🔍 Running security audit..."
pip install pip-audit
pip-audit --fix --dry-run || true

echo ""
echo "✅ Security update completed!"
echo ""
echo "Next steps:"
echo "1. Review the changes"
echo "2. Run tests to ensure compatibility"
echo "3. Commit and push the updates"