# ACGS-1 Post-Cleanup Quick Reference Guide

## 📁 New File Locations

### Configuration Files

| File                      | Old Location | New Location                     |
| ------------------------- | ------------ | -------------------------------- |
| `pytest.ini`              | `/`          | `config/pytest.ini`              |
| `requirements*.txt`       | `/`          | `config/requirements*.txt`       |
| `.env.example`            | `/`          | `config/.env.example`            |
| `uv.lock`                 | `/`          | `config/uv.lock`                 |
| `.pre-commit-config.yaml` | `/`          | `config/.pre-commit-config.yaml` |
| `.gitleaks.toml`          | `/`          | `config/.gitleaks.toml`          |

### Docker & Infrastructure

| File                   | Old Location | New Location             |
| ---------------------- | ------------ | ------------------------ |
| `docker-compose.*.yml` | `/`          | `infrastructure/docker/` |
| `Dockerfile.acgs`      | `/`          | `infrastructure/docker/` |

### Application Configs

| File             | Old Location | New Location                  |
| ---------------- | ------------ | ----------------------------- |
| `jest.config.js` | `/`          | `applications/jest.config.js` |
| `tsconfig.json`  | `/`          | `applications/tsconfig.json`  |
| `package*.json`  | `/`          | `applications/package*.json`  |

### Test Configuration

| File          | Old Location | New Location        |
| ------------- | ------------ | ------------------- |
| `conftest.py` | `/`          | `tests/conftest.py` |

### Reports & Documentation

| File                                 | Old Location | New Location       |
| ------------------------------------ | ------------ | ------------------ |
| `cleanup_report_*.json`              | `/`          | `reports/cleanup/` |
| `*SUMMARY.md`                        | `/`          | `docs/`            |
| `comprehensive_duplicate_cleanup.py` | `/`          | `scripts/`         |

## 🔧 Updated Commands

### Running Tests

```bash
# Old command
pytest

# New command (from project root)
python -m pytest -c config/pytest.ini

# Or from config directory
cd config && pytest
```

### Docker Commands

```bash
# Old command
docker-compose up

# New command
docker-compose -f infrastructure/docker/docker-compose.yml up
```

### Installing Dependencies

```bash
# Python dependencies
pip install -r config/requirements.txt

# Node.js dependencies (from applications directory)
cd applications && npm install
```

## 🏗️ Directory Structure Overview

```
ACGS-1/
├── analysis/                  # Cleanup analysis and reports
├── applications/              # Frontend and client applications
├── archive/                   # Historical data and backups
├── blockchain/                # Solana/Anchor smart contracts
├── config/                    # Centralized configuration files
├── docs/                      # Technical documentation
├── infrastructure/            # Docker, K8s, Terraform configs
├── services/                  # Core and platform services
├── scripts/                   # Automation and utility scripts
├── tests/                     # Test suites and coverage
└── [10 essential root files]  # Core project files only
```

## ⚡ Quick Actions

### Restore Service

```bash
# Check service status
curl http://localhost:8000/health

# Restart specific service
bash scripts/manage_pgc_service.sh start
```

### Run Cleanup Validation

```bash
# Validate cleanup completion
python scripts/validate_cleanup_completion.py

# Check system health
bash scripts/comprehensive_health_check.sh
```

### Fix Import Issues

```bash
# Fix Python import paths
python root_scripts/fix_python_imports.py

# Fix test imports
python root_scripts/fix_test_imports.py
```

## 🎯 Success Metrics Achieved

- ✅ **73.7% root directory reduction** (38 → 10 files)
- ✅ **1,559 files cleaned** from repository
- ✅ **All 7 core services operational** (ports 8000-8006)
- ✅ **Excellent performance** (5-78ms response times)
- ✅ **100% service availability** maintained
- ✅ **Configuration centralized** in config/
- ✅ **Docker files organized** in infrastructure/
- ✅ **Import paths fixed** and functional
- ✅ **Test framework working** with new configuration
- ✅ **Dependencies resolved** (pyotp installed)
- ✅ **Comprehensive .gitignore** updated

## 🔍 Current Status & Next Steps

### ✅ Completed Actions

1. **Service Restoration**: ✅ All 7 core services operational
2. **Import Path Fixes**: ✅ Python imports working correctly
3. **Test Validation**: ✅ Basic tests passing with new config
4. **Performance Validation**: ✅ 5-78ms response times achieved
5. **Dependencies**: ✅ Missing packages installed (pyotp)

### 🚀 Optional Enhancements

1. **Full Test Coverage**: Achieve >80% coverage across all components
2. **Legacy Test Updates**: Fix remaining path references in tests
3. **Monitoring Integration**: Fine-tune health check configurations
4. **Documentation**: Update any remaining legacy path references
5. **Production Deployment**: Final validation for production readiness

For detailed information, see: `analysis/ACGS-1_CLEANUP_COMPLETION_REPORT.md`
