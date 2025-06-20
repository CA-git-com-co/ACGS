# ACGS Dependency Management Guide

This document outlines the unified dependency management strategy for the ACGS project using UV, TOML configuration, and proper .gitignore patterns.

## 🎯 Overview

The ACGS project now uses a unified approach to dependency management:

- **Python**: UV with pyproject.toml and workspace configuration
- **Node.js**: npm workspaces with package.json
- **Rust**: Cargo workspaces with Cargo.toml
- **All dependencies**: Excluded from Git tracking via comprehensive .gitignore

## 🚀 Quick Start

### Initial Setup
```bash
# Run the comprehensive setup script
./setup_dependencies.sh
```

### Daily Development

#### Python Dependencies
```bash
# Add a dependency
uv add fastapi

# Add a dev dependency
uv add --dev pytest

# Install all dependencies
uv sync

# Run with UV
uv run python your_script.py

# Activate virtual environment
source .venv/bin/activate
```

#### Node.js Dependencies
```bash
# Install all workspace dependencies
npm install

# Add dependency to specific workspace
npm install axios --workspace=applications/app

# Run scripts across workspaces
npm run build --workspaces

# Test all workspaces
npm test --workspaces
```

#### Rust Dependencies
```bash
# Add a dependency
cargo add serde

# Build all workspace members
cargo build --workspace

# Test all workspace members
cargo test --workspace
```

## 📁 Project Structure

```
ACGS/
├── pyproject.toml              # Python workspace root
├── uv.toml                     # UV configuration
├── package.json                # Node.js workspace root
├── Cargo.toml                  # Rust workspace root
├── .gitignore                  # Comprehensive dependency exclusions
├── services/
│   ├── core/
│   │   ├── constitutional-ai/
│   │   │   └── pyproject.toml  # Service-specific Python config
│   │   └── ...
│   └── platform/
├── applications/
│   ├── app/
│   │   └── package.json        # App-specific Node.js config
│   └── ...
├── blockchain/
│   ├── package.json            # Blockchain Node.js dependencies
│   ├── Cargo.toml              # Blockchain Rust workspace
│   └── programs/
│       └── */Cargo.toml        # Individual program dependencies
└── tools/
    └── */pyproject.toml        # Tool-specific configurations
```

## 🔧 Configuration Files

### UV Configuration (uv.toml)
- Global Python settings
- Workspace member definitions
- Dependency resolution strategies
- Environment-specific configurations

### Python Workspace (pyproject.toml)
- Root workspace configuration
- Shared dependencies
- Development tools
- Build system configuration

### Node.js Workspace (package.json)
- npm workspace definitions
- Shared scripts and tools
- Development dependencies
- Linting and formatting configuration

### Rust Workspace (Cargo.toml)
- Cargo workspace members
- Shared dependencies
- Build profiles
- Security patches

## 🚫 What's Excluded from Git

The comprehensive .gitignore excludes:

### Dependency Directories
- `node_modules/` - Node.js packages
- `target/` - Rust build artifacts
- `venv/`, `.venv/` - Python virtual environments
- `__pycache__/` - Python bytecode cache
- `dist/`, `build/` - Build outputs
- `.next/`, `.nuxt/` - Framework build caches

### Lock Files
- `package-lock.json` - npm lock file
- `yarn.lock` - Yarn lock file
- `Cargo.lock` - Rust lock file (workspace level)
- `poetry.lock` - Poetry lock file

### Cache Directories
- `.mypy_cache/` - MyPy type checker cache
- `.pytest_cache/` - Pytest cache
- `.ruff_cache/` - Ruff linter cache
- `.cache/` - General cache directories

### Build Artifacts
- `*.pyc`, `*.pyo` - Python compiled files
- `*.so`, `*.dll` - Compiled libraries
- `*.egg-info/` - Python package metadata

## 🛠️ Common Tasks

### Adding Dependencies

#### Python Service
```bash
# Navigate to service directory
cd services/core/constitutional-ai

# Add dependency to service
uv add requests

# Add dev dependency
uv add --dev pytest-mock

# Sync workspace
cd ../../..
uv sync
```

#### Node.js Application
```bash
# Add to specific application
npm install react --workspace=applications/app

# Add dev dependency
npm install --save-dev typescript --workspace=applications/app
```

#### Rust Program
```bash
# Navigate to program directory
cd blockchain/programs/quantumagi-core

# Add dependency
cargo add serde

# Build workspace
cd ../../..
cargo build --workspace
```

### Updating Dependencies

#### Python
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add "fastapi>=0.105.0"
```

#### Node.js
```bash
# Update all workspaces
npm update --workspaces

# Update specific workspace
npm update --workspace=applications/app
```

#### Rust
```bash
# Update all dependencies
cargo update --workspace
```

### Cleaning Dependencies

#### Complete Cleanup
```bash
# Run comprehensive cleanup
python scripts/cleanup_dependencies.py

# Or use the setup script
./setup_dependencies.sh
```

#### Manual Cleanup
```bash
# Remove Node.js dependencies
find . -name "node_modules" -type d -prune -exec rm -rf {} +

# Remove Python caches
find . -name "__pycache__" -type d -prune -exec rm -rf {} +

# Remove build artifacts
find . -name "dist" -type d -prune -exec rm -rf {} +
find . -name "build" -type d -prune -exec rm -rf {} +
```

## 🔍 Troubleshooting

### UV Issues
```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clear UV cache
uv cache clean

# Recreate virtual environment
rm -rf .venv
uv sync
```

### npm Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Cargo Issues
```bash
# Clean build artifacts
cargo clean --workspace

# Update Rust toolchain
rustup update

# Rebuild
cargo build --workspace
```

## 📊 Benefits

### Space Savings
- **Before**: ~10GB of dependency artifacts tracked in Git
- **After**: <100MB of configuration files tracked in Git
- **Savings**: >99% reduction in repository size

### Development Experience
- **Unified**: Single command setup across all languages
- **Fast**: Parallel dependency resolution with UV
- **Reliable**: Reproducible builds with lock files
- **Clean**: No dependency artifacts in Git history

### Maintenance
- **Centralized**: All dependency configuration in TOML files
- **Automated**: Scripts for setup, cleanup, and updates
- **Documented**: Clear patterns and conventions
- **Scalable**: Easy to add new services and applications

## 🔗 Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [npm Workspaces](https://docs.npmjs.com/cli/v7/using-npm/workspaces)
- [Cargo Workspaces](https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html)
- [Python Packaging](https://packaging.python.org/en/latest/)
- [TOML Specification](https://toml.io/en/)
