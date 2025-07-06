# ACGS-PGP Dependency Management

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->


This document outlines the dependency management strategy for ACGS-PGP using modern tools like `uv` for Python and `npm` for JavaScript/TypeScript.

## Overview

ACGS-PGP uses a hybrid dependency management approach:

- **Python**: `uv` (primary) with `pyproject.toml` as the source of truth
- **JavaScript/TypeScript**: `npm` with `package.json`
- **Legacy Support**: `requirements.txt` maintained for compatibility

## Python Dependencies (uv + pyproject.toml)

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv pip install -e .

# Install with optional dependencies
uv pip install -e .[dev,test,ml,blockchain,docs,prod,all]
```

### Core Dependencies

#### Framework & Web

- `fastapi>=0.115.6` - Modern web framework
- `uvicorn[standard]>=0.34.0` - ASGI server
- `pydantic>=2.10.5` - Data validation
- `httpx>=0.28.1` - HTTP client

#### Database & Storage

- `redis>=5.0.1` - In-memory data store
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `sqlalchemy[asyncio]>=2.0.23` - ORM
- `alembic>=1.13.0` - Database migrations

#### AI/ML & Models

- `torch>=2.0.0` - PyTorch framework
- `transformers>=4.30.0` - Hugging Face transformers
- `openai>=1.3.0` - OpenAI API client
- `anthropic>=0.3.11` - Anthropic API client
- `google-generativeai>=0.3.0` - Google Gemini API
- `nemo-skills @ git+https://github.com/NVIDIA/NeMo-Skills.git` - NVIDIA NeMo Skills

#### Security & Authentication

- `cryptography>=45.0.4` - Cryptographic recipes
- `pyjwt>=2.10.0` - JWT implementation
- `python-jose[cryptography]>=3.3.0` - JOSE implementation
- `passlib[bcrypt]>=1.7.4` - Password hashing

### Optional Dependencies

#### Development (`[dev]`)

- `pytest>=7.4.3` - Testing framework
- `black>=23.0.0` - Code formatter
- `mypy>=1.5.0` - Type checker
- `ruff>=0.1.0` - Fast linter

#### Testing (`[test]`)

- `pytest-asyncio>=0.21.1` - Async testing
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-mock>=3.14.1` - Mocking utilities

#### Machine Learning (`[ml]`)

- `scikit-learn>=1.3.0` - ML library
- `xgboost>=1.7.0` - Gradient boosting
- `optuna>=3.3.0` - Hyperparameter optimization

#### Blockchain (`[blockchain]`)

- `web3>=6.9.0` - Ethereum client
- `solana>=0.30.0` - Solana client

### Managing Dependencies

```bash
# Add a new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Add optional dependency group
uv add --optional ml package-name

# Update dependencies
uv pip install --upgrade -e .

# Generate requirements.txt (for compatibility)
uv pip freeze > requirements-frozen.txt
```

## JavaScript/TypeScript Dependencies (npm + package.json)

### Installation

```bash
cd project
npm ci  # Install exact versions from package-lock.json
npm install  # Install and update package-lock.json
```

### Core Dependencies

#### Framework & UI

- `next@13.5.1` - React framework
- `react@18.2.0` - UI library
- `typescript@5.2.2` - Type system
- `tailwindcss@3.3.3` - CSS framework

#### Blockchain & Solana

- `@solana/wallet-adapter-base@^0.9.23` - Wallet adapter base
- `@solana/wallet-adapter-react@^0.15.35` - React wallet adapter
- `@solana/wallet-adapter-wallets@^0.19.32` - Wallet implementations
- `@solana/web3.js@^1.95.2` - Solana Web3 client

#### UI Components

- `@radix-ui/react-*` - Accessible UI primitives
- `lucide-react@^0.446.0` - Icon library
- `class-variance-authority@^0.7.0` - CSS-in-JS utilities

### Development Dependencies

#### Testing

- `jest@^29.7.0` - Testing framework
- `@testing-library/react@^16.0.1` - React testing utilities
- `@playwright/test@^1.47.2` - E2E testing

#### Code Quality

- `eslint@8.49.0` - Linting
- `prettier@^3.3.3` - Code formatting
- `typescript@5.2.2` - Type checking

### Managing Dependencies

```bash
# Add dependency
npm install package-name

# Add dev dependency
npm install --save-dev package-name

# Update dependencies
npm update

# Audit security
npm audit
npm audit fix

# Check outdated packages
npm outdated
```

## Dependency Synchronization

### Keeping Dependencies in Sync

1. **Primary Source**: `pyproject.toml` for Python, `package.json` for JavaScript
2. **Generated Files**: `requirements.txt` (compatibility), `package-lock.json` (lockfile)
3. **Version Pinning**: Use `>=` for flexibility, `==` for stability

### Update Workflow

```bash
# 1. Update Python dependencies
uv pip install --upgrade -e .[all]

# 2. Update JavaScript dependencies
cd project && npm update

# 3. Test everything
uv run pytest
cd project && npm test

# 4. Update lockfiles
uv pip freeze > requirements-frozen.txt
# package-lock.json is updated automatically by npm

# 5. Commit changes
git add pyproject.toml package.json package-lock.json requirements.txt
git commit -m "chore: update dependencies"
```

## Environment Setup

### Development Environment

```bash
# 1. Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# 2. Run installation script
./install.sh

# 3. Activate environment (if using virtual env)
source .venv/bin/activate  # or uv venv && source .venv/bin/activate

# 4. Verify installation
uv run pytest tests/unit/test_simple.py
cd project && npm test
```

### Production Environment

```bash
# 1. Install production dependencies only
uv pip install -e .[prod] --no-dev

# 2. Build frontend
cd project && npm ci --production && npm run build

# 3. Set environment variables
export ENVIRONMENT=production
export DEBUG=false
export JWT_SECRET_KEY="your-secure-secret-key"
```

## Troubleshooting

### Common Issues

1. **uv not found**: Install uv using the official installer
2. **NeMo-Skills build fails**: Ensure CUDA toolkit is installed or use CPU-only PyTorch
3. **Node.js version**: Ensure Node.js >= 18.0.0
4. **Permission errors**: Use virtual environments or user installs

### Dependency Conflicts

```bash
# Check for conflicts
uv pip check

# Resolve conflicts
uv pip install --force-reinstall package-name

# Clean install
rm -rf .venv node_modules
uv venv && uv pip install -e .[all]
cd project && npm ci
```

## Security

### Vulnerability Management

```bash
# Python security audit
uv pip install safety
safety check

# JavaScript security audit
npm audit
npm audit fix

# Update security-critical packages
uv pip install --upgrade cryptography pyjwt
npm update --save
```

### Best Practices

1. **Pin security-critical dependencies** with exact versions
2. **Regular updates**: Monthly dependency updates
3. **Automated scanning**: Use GitHub Dependabot
4. **Lock files**: Always commit `package-lock.json` and consider `uv.lock`
5. **Minimal dependencies**: Only install what you need

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Setup Python with uv
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'

- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Install dependencies
  run: uv pip install -e .[test]

- name: Run tests
  run: uv run pytest
```

## Migration Guide

### From pip to uv

1. **Backup current setup**: `pip freeze > requirements-backup.txt`
2. **Install uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **Migrate dependencies**: Update `pyproject.toml` with current dependencies
4. **Test migration**: `uv pip install -e . && pytest`
5. **Update CI/CD**: Replace `pip` commands with `uv pip`

### Version Compatibility

- **Python**: 3.10+ (3.11+ recommended)
- **Node.js**: 18.0+ (20.0+ recommended)
- **uv**: Latest stable version
- **npm**: 9.0+ (comes with Node.js 18+)
